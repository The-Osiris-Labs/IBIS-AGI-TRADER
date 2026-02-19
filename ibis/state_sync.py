"""
IBIS State Synchronization Module
================================
Keeps ibis_true_state.json in sync with the SQLite database.
This ensures real-time updates for monitoring tools.
"""

import asyncio
import json
import os
import fcntl
from datetime import datetime
from typing import Dict

from ibis.database.db import IbisDB
from ibis.exchange.kucoin_client import get_kucoin_client
from ibis.core.trading_constants import TRADING

from ibis.core.logging_config import get_logger
logger = get_logger(__name__)


class StateSynchronizer:
    """Synchronizes state between DB and JSON for real-time monitoring."""

    def __init__(
        self,
        state_file: str = "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_true_state.json",
    ):
        self.state_file = state_file
        self.state_lock_file = (
            "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_state.lock"
        )
        self.db = IbisDB()
        self.client = get_kucoin_client()
        self.running = False

    async def reconcile_positions(self):
        """Reconcile local positions with KuCoin's actual positions"""
        try:
            # Get positions from exchange
            exchange_account = await self.client._request_with_retry("GET", "/api/v1/accounts")
            exchange_positions = {}

            if exchange_account:
                for account in exchange_account:
                    if account.get("type") == "trade" and float(account.get("balance", 0)) > 0:
                        currency = account.get("currency", "")
                        if currency != "USDT":  # Skip USDT
                            # Find corresponding trading pair
                            symbol = f"{currency}-USDT"
                            exchange_positions[symbol] = {
                                "quantity": float(account.get("balance", 0)),
                                "available": float(account.get("available", 0)),
                                "hold": float(account.get("hold", 0)),
                            }

            # Get local positions
            local_positions = self.db.get_open_positions()
            local_symbols = {pos.get("symbol", "") for pos in local_positions}
            exchange_symbols = set(exchange_positions.keys())

            # Reconcile discrepancies
            # 1. Positions in exchange but not in local DB
            for symbol in exchange_symbols - local_symbols:
                if symbol.endswith("-USDT") and exchange_positions[symbol]["quantity"] > 0.0001:
                    logger.warning(f"Found new position on exchange not in DB: {symbol}")
                    # TODO: Add logic to adopt this position

            # 2. Positions in local DB but not in exchange
            for symbol in local_symbols - exchange_symbols:
                logger.warning(f"Position in DB not found on exchange: {symbol}")
                # TODO: Add logic to remove this position

            # 3. Verify quantities match
            for symbol in local_symbols & exchange_symbols:
                local_qty = next(
                    pos.get("quantity", 0) for pos in local_positions if pos.get("symbol") == symbol
                )
                exchange_qty = exchange_positions[symbol]["quantity"]

                if abs(local_qty - exchange_qty) > 0.0001:
                    logger.warning(
                        f"Quantity mismatch for {symbol}: DB={local_qty:.8f}, Exchange={exchange_qty:.8f}"
                    )

            return True

        except Exception as e:
            logger.error(f"Position reconciliation error: {e}", exc_info=True)
            return False

    async def verify_balance(self):
        """Verify balance consistency with open orders"""
        try:
            balances = await self.client.get_all_balances()
            usdt_available = float(balances.get("USDT", {}).get("available", 0))
            usdt_locked = float(balances.get("USDT", {}).get("hold", 0))

            # Verify with open orders
            open_orders = await self.client.get_open_orders()
            expected_locked = 0.0

            for order in open_orders:
                if order.get("side") == "buy":
                    # For buy orders, locked funds should match order size
                    if order.get("type") == "limit":
                        expected_locked += float(order.get("price", 0)) * float(
                            order.get("size", 0)
                        )
                    else:  # market
                        expected_locked += float(order.get("funds", 0))

            if abs(usdt_locked - expected_locked) > 0.01:
                logger.warning(
                    f"Balance discrepancy: locked funds mismatch (API: {usdt_locked:.2f}, Calculated: {expected_locked:.2f})"
                )

            return True

        except Exception as e:
            logger.error(f"Balance verification error: {e}", exc_info=True)
            return False

    async def sync_to_json(self):
        """Sync database state to JSON file with reconciliation"""
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            os.makedirs(os.path.dirname(self.state_lock_file), exist_ok=True)

            # Perform position reconciliation
            await self.reconcile_positions()

            # Verify balance consistency
            await self.verify_balance()

            positions = self.db.get_open_positions()

            # Get current prices for all positions
            positions_with_prices = {}
            for pos in positions:
                symbol = pos.get("symbol", "")
                try:
                    ticker = await self.client.get_ticker(symbol)
                    if ticker:
                        current_price = float(ticker.price)
                        entry_price = float(pos.get("entry_price", current_price))
                        quantity = float(pos.get("quantity", 0))

                        pnl_pct = (current_price / entry_price - 1) * 100 if entry_price > 0 else 0

                        positions_with_prices[symbol.replace("-USDT", "")] = {
                            "symbol": symbol.replace("-USDT", ""),
                            "quantity": quantity,
                            "buy_price": entry_price,
                            "current_price": current_price,
                            "mode": pos.get("mode", "EXISTING"),
                            "regime": pos.get("regime", "unknown"),
                            "opened": pos.get("opened_at", datetime.now().isoformat()),
                            "opportunity_score": pos.get("agi_score", 50),
                            "tp": entry_price * (1 + TRADING.RISK.TAKE_PROFIT_PCT),
                            "sl": entry_price * (1 - TRADING.RISK.STOP_LOSS_PCT),
                            "unrealized_pnl": (current_price - entry_price) * quantity,
                            "unrealized_pnl_pct": pnl_pct,
                        }
                except Exception as e:
                    logger.error(f"Error getting price for {symbol}: {e}", exc_info=True)
                    continue

            # Get daily stats from trades
            trades = self.db.get_trades(limit=100)
            wins = sum(1 for t in trades if t.get("pnl", 0) > 0)
            losses = sum(1 for t in trades if t.get("pnl", 0) <= 0)
            pnl = sum(t.get("pnl", 0) for t in trades)

            # Get USDT balance
            balances = await self.client.get_all_balances()
            usdt_available = float(balances.get("USDT", {}).get("available", 0))

            # Merge into existing state (avoid clobbering unrelated fields like capital_awareness).
            with open(self.state_lock_file, "w") as lock_f:
                fcntl.flock(lock_f, fcntl.LOCK_EX)
                existing_state = {}
                if os.path.exists(self.state_file):
                    try:
                        with open(self.state_file, "r") as f:
                            existing_state = json.load(f)

                        # Filter out any fields with empty string values
                        def filter_empty(obj):
                            if isinstance(obj, dict):
                                return {
                                    k: filter_empty(v)
                                    for k, v in obj.items()
                                    if v not in ["", None]
                                }
                            elif isinstance(obj, list):
                                return [filter_empty(x) for x in obj if x not in ["", None]]
                            else:
                                return obj

                        existing_state = filter_empty(existing_state)

                    except Exception:
                        existing_state = {}

                daily_existing = existing_state.get("daily", {})
                daily_merged = {
                    **daily_existing,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "trades": len(trades),
                    "wins": wins,
                    "losses": losses,
                    "pnl": pnl,
                }
                if "start_balance" not in daily_merged:
                    daily_merged["start_balance"] = 0.0
                if "regimes_experienced" not in daily_merged:
                    daily_merged["regimes_experienced"] = {}
                if "strategies_tried" not in daily_merged:
                    daily_merged["strategies_tried"] = {}

                # Update capital awareness - explicitly set all fields to ensure no empty values
                capital_awareness = existing_state.get("capital_awareness", {})

                # Remove any existing fields with empty string values
                keys_to_remove = [
                    key for key, value in capital_awareness.items() if value == "" or value is None
                ]
                for key in keys_to_remove:
                    del capital_awareness[key]

                # Force update all capital awareness fields
                capital_awareness["usdt_available"] = usdt_available

                # Calculate total assets
                holdings_value = sum(
                    pos["current_price"] * pos["quantity"] for pos in positions_with_prices.values()
                )
                locked_buy = sum(
                    order["funds"] for order in capital_awareness.get("buy_orders", {}).values()
                )
                capital_awareness["holdings_value"] = holdings_value
                capital_awareness["total_assets"] = usdt_available + holdings_value + locked_buy
                capital_awareness["usdt_total"] = usdt_available + locked_buy
                capital_awareness["usdt_locked_buy"] = locked_buy

                # Keep existing fields that are not related to core capital calculation
                for key in [
                    "total_fees",
                    "fees_today",
                    "real_trading_capital",
                    "open_orders_count",
                    "buy_orders",
                    "sell_orders",
                ]:
                    if key not in capital_awareness and key in existing_state.get(
                        "capital_awareness", {}
                    ):
                        capital_awareness[key] = existing_state["capital_awareness"][key]

                state = {
                    **existing_state,
                    "positions": positions_with_prices,
                    "daily": daily_merged,
                    "updated": datetime.now().isoformat(),
                    "usdt_available": usdt_available,
                    "total_positions": len(positions),
                    "capital_awareness": capital_awareness,
                }

                if "market_regime" not in state:
                    state["market_regime"] = "unknown"
                if "agent_mode" not in state:
                    state["agent_mode"] = "ROTATING"

                # Debug: Print capital awareness before saving
                logger.debug("Debug - Capital awareness before saving:", capital_awareness)

                tmp_path = f"{self.state_file}.tmp"
                with open(tmp_path, "w") as f:
                    json.dump(state, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp_path, self.state_file)
                fcntl.flock(lock_f, fcntl.LOCK_UN)

            return True

        except Exception as e:
            logger.error(f"State sync error: {e}", exc_info=True)
            return False

    async def run_sync_loop(self, interval: int = 30):
        """Run continuous sync loop."""
        self.running = True
        logger.info(f"🔄 State synchronizer started (interval: {interval}s)")

        while self.running:
            try:
                await self.sync_to_json()
            except Exception as e:
                logger.error(f"Sync error: {e}", exc_info=True)
            await asyncio.sleep(interval)

    def stop(self):
        """Stop the sync loop."""
        self.running = False


async def run_single_sync():
    """Run a single sync and exit."""
    syncer = StateSynchronizer()
    success = await syncer.sync_to_json()
    if success:
        logger.info("✅ State synchronized successfully")
    else:
        logger.error("❌ State sync failed")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="IBIS State Synchronizer")
    parser.add_argument("--loop", action="store_true", help="Run continuous loop")
    parser.add_argument("--interval", type=int, default=30, help="Sync interval in seconds")
    args = parser.parse_args()

    if args.loop:
        syncer = StateSynchronizer()
        asyncio.run(syncer.run_sync_loop(args.interval))
    else:
        asyncio.run(run_single_sync())
