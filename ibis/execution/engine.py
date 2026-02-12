"""
IBIS v8 EXECUTION ENGINE
Orchestrates the trading lifecycle: Data -> Strategy -> Execution -> Database.
"""

import os
import asyncio
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional

from ibis.core.config import Config
from ibis.database.db import IbisDB
from ibis.strategies.swing_native import NativeLimitlessSwing
from ibis.exchange.kucoin_client import get_kucoin_client
from ibis.cross_exchange_monitor import CrossExchangeMonitor
from ibis.market_funnel import MarketFunnel
from ibis.market_intelligence import market_intelligence
from ibis.position_rotation import PositionRotationManager
from ibis.state_sync import StateSynchronizer
from ibis.core.trading_constants import TRADING

# Configure logging
LOG_PATH = "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_v8.log"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()],
)
logger = logging.getLogger("ibis_v8")


class ExecutionEngine:
    def __init__(self):
        self.db = IbisDB()
        self.client = get_kucoin_client()
        self.monitor = CrossExchangeMonitor()
        self.strategy = NativeLimitlessSwing({})
        self.funnel = MarketFunnel(self.client)  # Legacy funnel for initial screening
        self.running = False

    async def initialize(self):
        """Initialize all components."""
        logger.info("🦅 IBIS v8 ENGINE INITIALIZING...")

        # Verify Exchange Connection
        try:
            # Check balance (basic connectivity test)
            await self.client.get_all_balances()
            logger.info("✅ KuCoin Connection Verified")
        except Exception as e:
            logger.error(f"❌ KuCoin Connection Failed: {e}")
            raise

        # Initialize Monitors
        await self.monitor.initialize()
        logger.info("✅ Cross-Exchange Monitor Active")

        # Sync State
        await self.sync_state()
        logger.info("✅ State Synchronized with Database")

    async def sync_state(self):
        """Reconcile local DB with Exchange."""
        logger.info("   🔄 Syncing State (Fetching Balances)...")
        # Get actual balances (Raw)
        try:
            # We use the raw SDK call if possible, or just the client one without min_value_usd to avoid internal ticker fetches if possible?
            # Actually, let's just use the client one but with min_value_usd=0 to skip the slow USD calc inside the client if possible?
            # Looking at client code, if min_value_usd > 0 it fetches ticker.
            # So we pass min_value_usd=0 to skip that logic in client.
            balances = await self.client.get_all_balances(min_value_usd=0)
            tickers_list = await self.client.get_tickers()
            tickers = {t.symbol: t for t in tickers_list}
        except Exception as e:
            logger.error(f"❌ Failed to sync hardware state: {e}")
            return

        logger.info(f"   🔄 Analyzing {len(balances)} non-zero balances...")

        # Get recorded positions
        db_positions = {p["symbol"]: p for p in self.db.get_open_positions()}

        # Reconcile
        for currency, data in balances.items():
            if currency == "USDT":
                continue

            qty = float(data.get("balance", 0))
            if qty <= 0:
                continue

            # Filter dust here manually with logging
            try:
                symbol = f"{currency}-USDT"
                ticker = tickers.get(symbol)
                price = ticker.price if ticker else 0.0

                if price * qty < 1.0:  # Ignore dust < $1
                    continue

                if symbol not in db_positions:
                    # Found new position (adopt it)
                    self.db.update_position(symbol, qty, price)
                    logger.info(f"📥 Adopted Position: {symbol} ({qty} @ ${price})")
                else:
                    # Update quantity if changed
                    db_qty = db_positions[symbol]["quantity"]
                    if abs(qty - db_qty) > 0.0001:
                        self.db.update_position(symbol, qty, price)
                        logger.info(f"🔄 Updated Position: {symbol} {db_qty} -> {qty}")

            except Exception as e:
                logger.warning(f"⚠️ Could not sync {currency}: {e}")
                continue

        # Save USDT liquid balance for monitor
        usdt_balance = balances.get("USDT", {}).get("balance", 0)
        self.db.set_state("usdt_balance", usdt_balance)

        # Check for ghosts (in DB but not in balances)
        # Note: This is simplified; assumes all db positions are spot assets

    async def fetch_market_data(self, symbol: str) -> Dict:
        """Fetch all data required for strategy analysis."""
        # 1. Get 15m Candles (Limit 50 for indicators)
        # Note: KuCoin client needs fetch_ohlcv method.
        # Using existing get_kline_data from legacy if available, or fetch_ohlcv from ccxt if integrated.
        # Fallback to pure ticker for now if OHLCV missing, but Strategy needs closes.

        # We need to implement a clean fetch_ohlcv wrapper in the engine
        # leveraging the existing client or direct API calls.

    async def fetch_market_data(self, symbol: str, intelligence_batch: Dict = None) -> Dict:
        """Fetch all data needed for strategy analysis for a symbol."""
        # 1. Get 15m Candles
        ohlcv = await self.client.get_candles(symbol, "15min", limit=100)
        closes = [c.close for c in ohlcv] if ohlcv else []

        # 2. Get Ticker
        ticker = await self.client.get_ticker(symbol)

        # 3. Get Cross-Exchange Signal
        lead = await self.monitor.get_price_lead_signal(symbol, ticker.price)

        # 4. Get AGI Intelligence Score
        if intelligence_batch and symbol in intelligence_batch:
            intel = intelligence_batch[symbol]
        else:
            intel = await market_intelligence.get_combined_intelligence([symbol])

        agi_score = market_intelligence.calculate_intelligence_score(symbol, intel)

        return {
            "symbol": symbol,
            "current_price": ticker.price,
            "closes_15m": closes,
            "lead_signal": lead,
            "agi_score": agi_score,
        }

    async def execute_signal(self, symbol: str, signal: Dict):
        """🚀 SMART PASSIVE TRADING

        IBIS philosophy:
        - Trade when intelligence says trade
        - Position size scales with capital (15% of available)
        - +0.6% limit sell, -1.0% hard stop
        - Walk away and let orders fill
        """
        if signal["signal"] == "BUY":
            # Check capital
            balances = await self.client.get_all_balances()
            usdt = float(balances.get("USDT", {}).get("available", 0))
            min_trade = TRADING.POSITION.MIN_CAPITAL_PER_TRADE  # $5

            if usdt < min_trade:
                logger.info(f"💤 No capital for {symbol} (${usdt:.2f} < ${min_trade})")
                return

            # Smart position sizing: 15% of available capital
            size_usd = TRADING.get_standard_position_size(usdt)
            size_usd = min(size_usd, usdt * 0.99)  # Keep 1% for fees

            try:
                logger.info(
                    f"🚀 SMART BUY: {symbol} ${size_usd:.2f} | Score: {signal.get('score', 50)}"
                )

                # Execute market buy
                order = await self.client.create_market_order(symbol, "buy", size_usd)
                entry_price = signal.get(
                    "price", order.avg_price if hasattr(order, "avg_price") else 0
                )

                if entry_price <= 0:
                    ticker = await self.client.get_ticker(symbol)
                    entry_price = ticker.price

                quantity = size_usd / entry_price

                logger.info(f"   📊 Bought: {quantity:.8f} {symbol} @ ${entry_price:.6f}")

                # Calculate +3.0% limit sell price
                take_profit_price = entry_price * (1 + TRADING.RISK.TAKE_PROFIT_PCT)
                expected_profit = (take_profit_price - entry_price) * quantity
                entry_fee = size_usd * TRADING.PROFIT.ENTRY_FEE_PCT
                total_fees = entry_fee + (
                    expected_profit * TRADING.PROFIT.EXIT_FEE_PCT / TRADING.PROFIT.TAKE_PROFIT_PCT
                )
                net_profit = expected_profit - total_fees

                logger.info(
                    f"   🎯 TP: ${take_profit_price:.6f} (+{TRADING.RISK.TAKE_PROFIT_PCT * 100:.1f}%)"
                )
                logger.info(
                    f"   💰 Gross: +${expected_profit:.4f} | Fees: -${total_fees:.4f} | Net: +${net_profit:.4f}"
                )

                # Place passive limit sell
                limit_order = await self._place_passive_limit_sell(
                    symbol,
                    quantity,
                    entry_price,
                    take_profit_pct=TRADING.RISK.TAKE_PROFIT_PCT,
                )

                # Update DB
                self.db.update_position(
                    symbol,
                    quantity,
                    entry_price,
                    agi_score=signal.get("score", 0.0),
                    agi_insight=signal.get("insight"),
                    entry_fee=entry_fee,
                    limit_sell_order_id=limit_order.order_id if limit_order else None,
                    limit_sell_price=take_profit_price,
                )

                logger.info(f"✅ POSITION OPEN: {symbol} | Net: +${net_profit:.4f}")

            except Exception as e:
                logger.error(f"❌ BUY FAILED {symbol}: {e}")

        elif signal["signal"] == "SELL":
            pass

    async def _get_symbol_rules(self, symbol: str) -> Dict:
        """Fetch trading rules for a symbol"""
        try:
            rules = await self.client.get_symbol(symbol)
            return rules if rules else {}
        except:
            return {}

    def _round_quantity(self, quantity: float, rules: Dict) -> float:
        """Round quantity to valid increments"""
        if rules:
            base_increment = float(rules.get("baseIncrement", 0.000001))
            if base_increment > 0:
                quantity = round(quantity / base_increment) * base_increment
        return float(f"{quantity:.8f}")

    async def manage_positions(self):
        """Check exit conditions for all open positions with proper error handling."""
        positions = self.db.get_open_positions()

        for pos in positions:
            symbol = pos["symbol"]
            ticker = await self.client.get_ticker(symbol)
            if not ticker:
                continue

            current_price = ticker.price
            highest = max(pos.get("current_price", 0), current_price)

            intel = await market_intelligence.get_combined_intelligence([symbol])
            agi_score = market_intelligence.calculate_intelligence_score(symbol, intel)
            insights = await market_intelligence.generate_insights(intel)
            insight_str = insights.get(symbol, ["--"])[0] if insights.get(symbol) else "--"

            if abs(current_price - pos.get("current_price", 0)) > (
                current_price * 0.001
            ) or agi_score != pos.get("agi_score"):
                self.db.update_position(
                    symbol,
                    pos["quantity"],
                    current_price,
                    agi_score=agi_score,
                    agi_insight=insight_str,
                )

            should_exit, reason = self.strategy.should_exit(
                symbol,
                entry_price=pos["entry_price"],
                current_price=current_price,
                highest_price=highest,
            )

            if should_exit:
                await self._execute_safe_sell(symbol, pos["quantity"], current_price, reason)

    async def _execute_safe_sell(
        self, symbol: str, quantity: float, current_price: float, reason: str
    ):
        """Execute SELL with proper quantity handling"""
        try:
            entry_price = 0
            positions = self.db.get_open_positions()
            for pos in positions:
                if pos.get("symbol") == symbol:
                    entry_price = float(pos.get("entry_price", current_price))
                    break

            pnl = (current_price - entry_price) * quantity
            pnl_pct = ((current_price / entry_price - 1) * 100) if entry_price > 0 else 0

            logger.info(
                f"🛑 SELLING: {symbol} | Qty: {quantity:.8f} | PnL: ${pnl:+.2f} ({pnl_pct:+.2f}%)"
            )

            rules = await self._get_symbol_rules(symbol)
            sell_qty = self._round_quantity(quantity, rules)

            if sell_qty < float(rules.get("baseMinSize", 0.001)):
                logger.warning(f"⚠️ Quantity below minimum for {symbol}, using min size")
                sell_qty = float(rules.get("baseMinSize", 0.001))

            logger.info(f"   📊 Rounded sell quantity: {sell_qty:.8f}")

            order = await self.client.create_market_order(symbol, "sell", sell_qty)
            self.db.close_position(symbol, current_price, reason)
            logger.info(f"✅ SELL SUCCESS: {symbol}")

        except Exception as e:
            logger.error(f"❌ SELL FAILED {symbol}: {e}")
            if "increment invalid" in str(e):
                logger.warning(f"   🔧 Attempting quantity fix...")
                try:
                    min_size = float(rules.get("baseMinSize", 0.001)) if rules else 0.001
                    fixed_qty = round(min_size / 0.00000001) * 0.00000001
                    logger.info(f"   🔧 Retry with fixed qty: {fixed_qty}")
                    order = await self.client.create_market_order(symbol, "sell", fixed_qty)
                    self.db.close_position(symbol, current_price, reason)
                    logger.info(f"✅ SELL SUCCESS after fix: {symbol}")
                except Exception as e2:
                    logger.error(f"   ❌ Fix failed: {e2}")

    async def _place_passive_limit_sell(
        self,
        symbol: str,
        quantity: float,
        entry_price: float,
        take_profit_pct: float = None,
    ):
        """🚀 PASSIVE LIMIT SELL

        Places limit sell at +0.6% (from TRADING config)
        IBIS sets it and forgets it.
        """
        if take_profit_pct is None:
            take_profit_pct = TRADING.RISK.TAKE_PROFIT_PCT

        try:
            limit_price = entry_price * (1 + take_profit_pct)
            rules = await self._get_symbol_rules(symbol)
            sell_qty = self._round_quantity(quantity, rules)

            if sell_qty < float(rules.get("baseMinSize", 0.001)):
                logger.warning(f"⚠️ Quantity below minimum for {symbol}")
                return None

            logger.info(
                f"🎯 LIMIT SELL: {symbol} | Qty: {sell_qty:.8f} | "
                f"Entry: ${entry_price:.6f} | Limit: ${limit_price:.6f} (+{take_profit_pct * 100:.1f}%)"
            )

            order = await self.client.place_limit_order(
                symbol=symbol, side="sell", price=limit_price, size=sell_qty
            )

            logger.info(f"✅ LIMIT SET: {symbol} @ ${limit_price:.6f}")
            logger.info(f"   📊 Order: {order.order_id}")
            logger.info(f"   💰 Gross profit: ${(limit_price - entry_price) * sell_qty:.4f}")

            return order

        except Exception as e:
            logger.error(f"❌ LIMIT FAILED {symbol}: {e}")
            return None

    async def run(self):
        """Main Loop with Continuous Rotation and State Sync."""
        self.running = True
        await self.initialize()

        # Initialize rotation manager and state synchronizer
        rotation_mgr = PositionRotationManager()
        state_sync = StateSynchronizer()

        logger.info("🦅 IBIS v8 ENGINE STARTED - CONTINUOUS ROTATION MODE")

        while self.running:
            try:
                # 1. POSITION ROTATION - Sell winners, cut losers, free capital
                logger.info("🔄 Running Position Rotation...")
                rotation_results = await rotation_mgr.execute_rotation()
                rotation_mgr = PositionRotationManager()

                # 2. Sync state to JSON for monitoring
                await state_sync.sync_to_json()

                # 3. Get updated balances after rotation
                balances = await self.client.get_all_balances()
                usdt = float(balances.get("USDT", {}).get("available", 0))

                # 4. Scan for Opportunities with fresh capital
                logger.info(f"   💰 Available Capital: ${usdt:.2f}")

                if usdt >= Config.MIN_CAPITAL_PER_TRADE:
                    logger.info("🎯 Scanning for new opportunities...")
                    candidates = await self.funnel.rank(limit=30)
                    top_symbols = [c.symbol for c in candidates[:5]]

                    intel_batch = await market_intelligence.get_combined_intelligence(top_symbols)

                    for symbol in top_symbols:
                        data = await self.fetch_market_data(symbol, intelligence_batch=intel_batch)
                        signal = self.strategy.analyze(data)

                        if signal["signal"] == "BUY":
                            await self.execute_signal(symbol, signal)

                        await asyncio.sleep(0.5)
                else:
                    logger.info(f"   🛑 Insufficient capital (${usdt:.2f}) - Rotating only")

                # 5. Meta-Reflection
                positions = self.db.get_open_positions()

                global_thought = f"Rotated {rotation_results['trades_executed']} | PnL: ${rotation_results['total_realized_pnl']:+.2f} | {len(positions)} positions"

                self.db.set_state("agent_thought", global_thought)

                logger.info(
                    f"💓 Heartbeat: {len(positions)} positions | USDT: ${usdt:.2f} | Rotations: {rotation_results['trades_executed']} | PnL: ${rotation_results['total_realized_pnl']:+.2f}"
                )

                await asyncio.sleep(30)

            except Exception:
                logger.exception("⚠️ Engine Loop Error")
                await asyncio.sleep(5)

    async def shutdown(self):
        """Cleanup."""
        self.running = False
        await self.client.close()
        await market_intelligence.close()
        await self.monitor.close()
        logger.info("👋 Engine shutdown complete")
