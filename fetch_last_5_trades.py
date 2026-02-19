#!/usr/bin/env python3
"""
Script to fetch and display the last 5 completed trades from IBIS database.
"""

import sys
import sqlite3
from typing import List, Dict
from datetime import datetime

# Database path from ibis/database/db.py
DB_PATH = "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_v8.db"


def fetch_last_5_trades() -> List[Dict]:
    """Fetch the last 5 completed trades from the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row

        # Fetch last 5 trades ordered by timestamp descending
        cursor = conn.execute("SELECT * FROM trades ORDER BY timestamp DESC LIMIT 5")

        trades = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return trades
    except Exception as e:
        print(f"Error fetching trades: {e}")
        return []


def format_trade(trade: Dict) -> Dict:
    """Format trade data for display"""
    # Convert timestamp to readable format
    if trade.get("timestamp"):
        try:
            # Handle both datetime objects and string timestamps
            if isinstance(trade["timestamp"], str):
                dt = datetime.fromisoformat(trade["timestamp"])
            else:
                dt = trade["timestamp"]
            trade["timestamp"] = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass

    # Ensure side is lowercase (buy/sell)
    if trade.get("side"):
        trade["side"] = trade["side"].lower()

    # Format numbers for better readability
    if trade.get("price") is not None:
        trade["price"] = f"{trade['price']:.8f}"
    if trade.get("fees") is not None:
        trade["fees"] = f"{trade['fees']:.8f}"
    if trade.get("pnl") is not None:
        trade["pnl"] = f"{trade['pnl']:.8f}"
    if trade.get("pnl_pct") is not None:
        trade["pnl_pct"] = f"{trade['pnl_pct']:.4%}"

    return trade


def display_trades(trades: List[Dict]):
    """Display trades in a readable format"""
    if not trades:
        print("No completed trades found in the database.")
        return

    print("=" * 100)
    print(
        f"{'Trade ID':<10} {'Symbol':<15} {'Side':<8} {'Quantity':<10} {'Price':<15} {'Fees':<10} {'Timestamp':<20} {'PnL':<12} {'Reason':<20}"
    )
    print("-" * 100)

    for trade in trades:
        formatted_trade = format_trade(trade)

        print(
            f"{formatted_trade['id']:<10} "
            f"{formatted_trade['symbol']:<15} "
            f"{formatted_trade['side']:<8} "
            f"{formatted_trade['quantity']:<10.4f} "
            f"{formatted_trade['price']:<15} "
            f"{formatted_trade['fees']:<10} "
            f"{formatted_trade['timestamp']:<20} "
            f"{formatted_trade['pnl']:<12} "
            f"{formatted_trade['reason']:<20}"
        )

    print("=" * 100)
    print(f"Total trades: {len(trades)}")


def main():
    """Main function"""
    print("Fetching last 5 completed trades from IBIS database...\n")

    trades = fetch_last_5_trades()
    display_trades(trades)


if __name__ == "__main__":
    main()
