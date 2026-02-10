"""
IBIS State Synchronization Module
================================
Keeps ibis_true_state.json in sync with the SQLite database.
This ensures real-time updates for monitoring tools.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict

from ibis.database.db import IbisDB
from ibis.exchange.kucoin_client import get_kucoin_client


class StateSynchronizer:
    """Synchronizes state between DB and JSON for real-time monitoring."""

    def __init__(
        self,
        state_file: str = "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_true_state.json",
    ):
        self.state_file = state_file
        self.db = IbisDB()
        self.client = get_kucoin_client()
        self.running = False

    async def sync_to_json(self):
        """Sync database state to JSON file."""
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)

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

                        pnl_pct = (
                            (current_price / entry_price - 1) * 100
                            if entry_price > 0
                            else 0
                        )

                        positions_with_prices[symbol.replace("-USDT", "")] = {
                            "symbol": symbol.replace("-USDT", ""),
                            "quantity": quantity,
                            "buy_price": entry_price,
                            "current_price": current_price,
                            "mode": pos.get("mode", "EXISTING"),
                            "regime": pos.get("regime", "unknown"),
                            "opened": pos.get("opened_at", datetime.now().isoformat()),
                            "opportunity_score": pos.get("agi_score", 50),
                            "tp": pos.get("take_profit", entry_price * 1.01),
                            "sl": pos.get("stop_loss", entry_price * 0.95),
                            "unrealized_pnl": (current_price - entry_price) * quantity,
                            "unrealized_pnl_pct": pnl_pct,
                        }
                except:
                    continue

            # Get daily stats from trades
            trades = self.db.get_trades(limit=100)
            wins = sum(1 for t in trades if t.get("pnl", 0) > 0)
            losses = sum(1 for t in trades if t.get("pnl", 0) <= 0)
            pnl = sum(t.get("pnl", 0) for t in trades)

            # Get USDT balance
            balances = await self.client.get_all_balances()
            usdt_available = float(balances.get("USDT", {}).get("available", 0))

            # Build state
            state = {
                "positions": positions_with_prices,
                "daily": {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "trades": len(trades),
                    "wins": wins,
                    "losses": losses,
                    "pnl": pnl,
                    "start_balance": 0.0,
                    "regimes_experienced": {},
                    "strategies_tried": {},
                },
                "market_regime": "unknown",
                "agent_mode": "ROTATING",
                "updated": datetime.now().isoformat(),
                "usdt_available": usdt_available,
                "total_positions": len(positions),
            }

            # Write to file
            with open(self.state_file, "w") as f:
                json.dump(state, f, indent=2)

            return True

        except Exception as e:
            print(f"State sync error: {e}")
            return False

    async def run_sync_loop(self, interval: int = 30):
        """Run continuous sync loop."""
        self.running = True
        print(f"🔄 State synchronizer started (interval: {interval}s)")

        while self.running:
            try:
                await self.sync_to_json()
            except Exception as e:
                print(f"Sync error: {e}")
            await asyncio.sleep(interval)

    def stop(self):
        """Stop the sync loop."""
        self.running = False


async def run_single_sync():
    """Run a single sync and exit."""
    syncer = StateSynchronizer()
    success = await syncer.sync_to_json()
    if success:
        print("✅ State synchronized successfully")
    else:
        print("❌ State sync failed")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="IBIS State Synchronizer")
    parser.add_argument("--loop", action="store_true", help="Run continuous loop")
    parser.add_argument(
        "--interval", type=int, default=30, help="Sync interval in seconds"
    )
    args = parser.parse_args()

    if args.loop:
        syncer = StateSynchronizer()
        asyncio.run(syncer.run_sync_loop(args.interval))
    else:
        asyncio.run(run_single_sync())
