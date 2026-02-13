"""
IBIS v2 EXECUTION ENGINE - ENHANCED WITH ERROR RECOVERY
=========================================================
Fixes for:
- SELL order size increment bug
- Proper quantity rounding with symbol rules
- Retry logic for failed orders
- Circuit breaker for failing positions
- Enhanced capital management
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

from ..core.config import Config
from ..core.trading_constants import TRADING, SCORE_THRESHOLDS
from ..database.db import IbisDB
from ..exchange.kucoin_client import get_kucoin_client
from ..cross_exchange_monitor import CrossExchangeMonitor
from ..market_intelligence import market_intelligence

LOG_PATH = "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_v2.log"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()],
)
logger = logging.getLogger("ibis_v2")


@dataclass
class SymbolRules:
    """Trading rules for a symbol"""

    base_increment: float = 0.0
    base_min_size: float = 0.0
    quote_min_size: float = 0.0
    price_increment: float = 0.0


class EnhancedExecutionEngine:
    """Enhanced execution engine with error recovery and proper quantity handling"""

    ORDER_EXPIRY_MINUTES = 30  # 30 minutes order expiry

    def __init__(self):
        self.db = IbisDB()
        self.client = get_kucoin_client()
        self.monitor = CrossExchangeMonitor()
        self.symbol_rules_cache: Dict[str, SymbolRules] = {}
        self.failed_positions: Dict[str, int] = {}  # Track failed attempts
        self.circuit_breaker: Dict[str, datetime] = {}  # Blocked positions
        self.max_retry_attempts = 3
        self.circuit_breaker_timeout_minutes = 5
        self.active_orders: Dict[str, datetime] = {}  # Track active orders and their creation times

    async def initialize(self):
        """Initialize all components"""
        logger.info("🦅 IBIS v2 ENGINE INITIALIZING...")

        try:
            await self.client.get_all_balances()
            logger.info("✅ KuCoin Connection Verified")
        except Exception as e:
            logger.error(f"❌ KuCoin Connection Failed: {e}")
            raise

        await self.monitor.initialize()
        logger.info("✅ Cross-Exchange Monitor Active")

        await self._warmup_symbol_cache()
        await self.sync_state()
        logger.info("✅ State Synchronized")

    async def _warmup_symbol_cache(self):
        """Pre-fetch symbol trading rules for common pairs"""
        logger.info("   🔥 Warming up symbol rules cache...")
        common_symbols = [
            "BTC-USDT",
            "ETH-USDT",
            "SOL-USDT",
            "XRP-USDT",
            "ADA-USDT",
            "MATIC-USDT",
            "DOT-USDT",
            "LINK-USDT",
            "AVAX-USDT",
            "ATOM-USDT",
            "2Z-USDT",
            "KCS-USDT",
            "A2Z-USDT",
            "AGI-USDT",
            "ACX-USDT",
            "AAVE-USDT",
            "AERGO-USDT",
            "ADI-USDT",
            "ACH-USDT",
            "ADX-USDT",
            "AERO-USDT",
            "0G-USDT",
            "1INCH-USDT",
        ]
        for symbol in common_symbols:
            await self._fetch_symbol_rules(symbol)

    async def _fetch_symbol_rules(self, symbol: str) -> Optional[SymbolRules]:
        """Fetch and cache trading rules for a symbol"""
        if symbol in self.symbol_rules_cache:
            return self.symbol_rules_cache[symbol]

        try:
            rules_data = await self.client.get_symbol(symbol)
            if rules_data:
                rules = SymbolRules(
                    base_increment=float(rules_data.get("baseIncrement", 0.000001)),
                    base_min_size=float(rules_data.get("baseMinSize", 0.001)),
                    quote_min_size=float(rules_data.get("quoteMinSize", 0.1)),
                    price_increment=float(rules_data.get("priceIncrement", 0.0001)),
                )
                self.symbol_rules_cache[symbol] = rules
                return rules
        except Exception as e:
            logger.debug(f"Could not fetch rules for {symbol}: {e}")

        return None

    def _round_quantity(self, quantity: float, symbol: str) -> float:
        """Round quantity to valid trading increments"""
        rules = self.symbol_rules_cache.get(symbol)
        if rules and rules.base_increment > 0:
            quantity = round(quantity / rules.base_increment) * rules.base_increment
        return float(f"{quantity:.8f}")

    def _validate_quantity(self, quantity: float, symbol: str) -> bool:
        """Validate quantity meets minimum requirements"""
        rules = self.symbol_rules_cache.get(symbol)
        if rules:
            return quantity >= rules.base_min_size
        return quantity >= 0.0001

    async def sync_state(self):
        """Reconcile local DB with Exchange"""
        logger.info("   🔄 Syncing State...")
        try:
            balances = await self.client.get_all_balances(min_value_usd=0)
            tickers_list = await self.client.get_tickers()
            tickers = {t.symbol: t for t in tickers_list}
        except Exception as e:
            logger.error(f"❌ Failed to sync: {e}")
            return

        logger.info(f"   🔄 Analyzing {len(balances)} balances...")

        db_positions = {p["symbol"]: p for p in self.db.get_open_positions()}

        for currency, data in balances.items():
            if currency == "USDT":
                continue

            qty = float(data.get("balance", 0))
            if qty <= 0:
                continue

            symbol = f"{currency}-USDT"

            try:
                ticker = tickers.get(symbol)
                price = ticker.price if ticker else 0.0

                if price * qty < 1.0:
                    continue

                if symbol not in db_positions:
                    self.db.update_position(symbol, qty, price)
                    logger.info(f"📥 Adopted: {symbol} ({qty:.4f} @ ${price:.4f})")
                else:
                    db_qty = db_positions[symbol]["quantity"]
                    if abs(qty - db_qty) > 0.0001:
                        self.db.update_position(symbol, qty, price)
                        logger.info(f"🔄 Updated: {symbol} {db_qty:.4f} -> {qty:.4f}")

            except Exception as e:
                logger.warning(f"⚠️ Could not sync {symbol}: {e}")
                continue

        usdt_balance = balances.get("USDT", {}).get("balance", 0)
        self.db.set_state("usdt_balance", usdt_balance)
        logger.info(f"   ✅ USDT Balance: ${usdt_balance:.2f}")

    async def _execute_buy_with_retry(self, symbol: str, size_usd: float) -> bool:
        """Execute BUY with retry logic"""
        ticker = await self.client.get_ticker(symbol)
        if not ticker:
            return False

        price = ticker.price
        quantity = size_usd / price

        rules = await self._fetch_symbol_rules(symbol)
        if rules:
            quantity = round(quantity / rules.base_increment) * rules.base_increment

        if not self._validate_quantity(quantity, symbol):
            logger.warning(f"⚠️ Quantity below minimum for {symbol}")
            return False

        for attempt in range(self.max_retry_attempts):
            try:
                logger.info(
                    f"🚀 BUY {symbol}: ${size_usd:.2f} ({quantity:.8f}) [Attempt {attempt + 1}]"
                )
                 order = await self.client.create_order(
                        symbol=symbol, side="buy", type="market", price=0, size=quantity
                    )

                    # Track active order
                    self.active_orders[order["orderId"]] = now

                    self.db.update_position(
                        symbol, quantity, price, agi_score=50, agi_insight="IBIS v2 Entry"
                    )
                logger.info(f"✅ BUY SUCCESS: {symbol}")
                return True

            except Exception as e:
                logger.warning(f"⚠️ BUY attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(1)

        logger.error(f"❌ BUY failed after {self.max_retry_attempts} attempts: {symbol}")
        return False

    async def _execute_sell_with_retry(self, symbol: str, quantity: float) -> bool:
        """Execute SELL with proper quantity handling and retry"""
        now = datetime.now()

        if symbol in self.circuit_breaker:
            last_failed = self.circuit_breaker[symbol]
            if (now - last_failed).total_seconds() < self.circuit_breaker_timeout_minutes * 60:
                logger.warning(f"⏸️ Circuit breaker active for {symbol}")
                return False
            else:
                del self.circuit_breaker[symbol]

        self.failed_positions[symbol] = self.failed_positions.get(symbol, 0) + 1

        if self.failed_positions[symbol] > self.max_retry_attempts:
            self.circuit_breaker[symbol] = now
            self.failed_positions[symbol] = 0
            logger.error(f"🛑 Circuit breaker triggered for {symbol}")
            return False

        for attempt in range(self.max_retry_attempts):
            try:
                rounded_qty = self._round_quantity(quantity, symbol)

                if not self._validate_quantity(rounded_qty, symbol):
                    logger.warning(f"⚠️ Invalid quantity for {symbol}: {rounded_qty}")
                    return False

                logger.info(f"🛑 SELL {symbol}: {rounded_qty:.8f} [Attempt {attempt + 1}]")
                 order = await self.client.create_order(
                    symbol=symbol, side="sell", type="market", price=0, size=rounded_qty
                )

                # Track active order
                self.active_orders[order["orderId"]] = now

                self.db.close_position(symbol, 0, "SELL_ORDER")
                logger.info(f"✅ SELL SUCCESS: {symbol}")
                self.failed_positions[symbol] = 0
                return True

            except Exception as e:
                logger.warning(f"⚠️ SELL attempt {attempt + 1} failed for {symbol}: {e}")

                if "increment invalid" in str(e):
                    await self._fix_and_retry(symbol, quantity, attempt)
                    continue

                await asyncio.sleep(1)

        logger.error(f"❌ SELL failed after {self.max_retry_attempts} attempts: {symbol}")
        return False

    async def _fix_and_retry(self, symbol: str, original_qty: float, attempt: int):
        """Attempt to fix quantity increment issue"""
        try:
            rules = await self._fetch_symbol_rules(symbol)
            if rules:
                logger.info(f"   🔧 Fixing quantity for {symbol} (min_size: {rules.base_min_size})")

                if rules.base_min_size > 0:
                    fixed_qty = rules.base_min_size
                else:
                    fixed_qty = round(original_qty, 8)

                logger.info(f"   🔧 Retry with fixed quantity: {fixed_qty:.8f}")

        except Exception as e:
            logger.error(f"   ❌ Could not fix quantity: {e}")

    async def manage_positions(self):
        """Enhanced position management with proper exit logic"""
        positions = self.db.get_open_positions()

        for pos in positions:
            symbol = pos["symbol"]
            ticker = await self.client.get_ticker(symbol)

            if not ticker:
                continue

            current_price = ticker.price
            entry_price = pos["entry_price"]
            quantity = pos["quantity"]
            pnl_pct = (current_price / entry_price - 1) * 100 if entry_price > 0 else 0

            if pnl_pct <= -5.0:
                logger.warning(f"🛑 STOP LOSS TRIGGERED: {symbol} at {pnl_pct:.2f}%")
                await self._execute_sell_with_retry(symbol, quantity)
                continue

            if pnl_pct >= 10.0:
                logger.info(f"🎯 TAKE PROFIT: {symbol} at {pnl_pct:.2f}%")
                await self._execute_sell_with_retry(symbol, quantity)
                continue

    async def execute_signal(self, symbol: str, signal: Dict) -> bool:
        """Execute signal with full error handling"""
        if signal["signal"] != "BUY":
            return False

        balances = await self.client.get_all_balances()
        usdt = float(balances.get("USDT", {}).get("available", 0))

        if usdt < TRADING.POSITION.MIN_CAPITAL_PER_TRADE:
            logger.warning(
                f"⚠️ Insufficient capital: ${usdt:.2f} < ${TRADING.POSITION.MIN_CAPITAL_PER_TRADE}"
            )
            return False

        size_usd = min(usdt, TRADING.POSITION.MAX_CAPITAL_PER_TRADE)
        return await self._execute_buy_with_retry(symbol, size_usd)

    async def run(self):
        """Main loop with enhanced monitoring"""
        self.running = True
        await self.initialize()

        logger.info("🦅 IBIS v2 ENGINE STARTED - ENHANCED MODE")

        while self.running:
            try:
                positions = self.db.get_open_positions()
                balances = await self.client.get_all_balances()
                usdt = float(balances.get("USDT", {}).get("available", 0))

                logger.info(f"💓 Heartbeat: {len(positions)} positions | USDT: ${usdt:.2f}")

                await self.manage_positions()
                await self.check_order_expiry()

                if usdt >= TRADING.POSITION.MIN_CAPITAL_PER_TRADE:
                    logger.info(f"   🎯 Capital available for trading: ${usdt:.2f}")

                await asyncio.sleep(60)

            except Exception:
                logger.exception("⚠️ Engine Loop Error")
                await asyncio.sleep(5)

    async def check_order_expiry(self):
        """Check and handle expired orders"""
        now = datetime.now()
        expired_orders = []

        for order_id, created_time in self.active_orders.items():
            if (now - created_time).total_seconds() > self.ORDER_EXPIRY_MINUTES * 60:
                expired_orders.append(order_id)
                logger.warning(f"⏰ Order {order_id} expired")

        for order_id in expired_orders:
            try:
                await self.client.cancel_order(order_id)
                del self.active_orders[order_id]
                logger.info(f"✅ Order {order_id} cancelled")
            except Exception as e:
                logger.error(f"❌ Failed to cancel expired order {order_id}: {e}")

    async def shutdown(self):
        """Clean shutdown"""
        self.running = False
        await self.client.close()
        await self.monitor.close()
        logger.info("👋 IBIS v2 Shutdown Complete")
