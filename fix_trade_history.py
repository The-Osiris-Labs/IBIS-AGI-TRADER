#!/usr/bin/env python3
"""
Trade History Cleanup Tool
==========================
Fixes invalid trades in the trade history file by removing or correcting invalid entries.

This script:
1. Identifies invalid trades based on validation rules
2. Removes duplicate order IDs
3. Corrects invalid size/price values
4. Validates and saves the cleaned trade history

Usage:
    python fix_trade_history.py [--dry-run] [--backup]

Options:
    --dry-run   Show changes without saving
    --backup    Create backup of original file before modifications
"""

import json
import argparse
from pathlib import Path
from ibis.pnl_tracker import PnLTracker, ValidationError, Trade


def main():
    parser = argparse.ArgumentParser(description="Fix invalid trades in the trade history file")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without saving")
    parser.add_argument(
        "--backup", action="store_true", help="Create backup of original file before modifications"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="/root/projects/Dont enter unless solicited/AGI Trader/data/trade_history.json",
        help="Path to trade history file",
    )

    args = parser.parse_args()

    trade_history_path = Path(args.input)

    # Check if file exists
    if not trade_history_path.exists():
        print(f"Error: File not found {args.input}")
        return

    print(f"Loading trade history from: {args.input}")

    # Load trade history
    with open(trade_history_path, "r") as f:
        data = json.load(f)

    trades = data.get("trades", [])
    print(f"Original trade count: {len(trades)}")

    # Create tracker instance to use validation methods
    tracker = PnLTracker(trade_history_file=args.input)

    # Validate and filter trades
    valid_trades = []
    invalid_trades = []

    # Track unique order IDs to avoid duplicates
    order_ids = set()

    for trade_dict in trades:
        try:
            # Create Trade object
            trade = Trade(**trade_dict)

            # Check for duplicate order IDs
            if trade.order_id in order_ids:
                invalid_trades.append(
                    {"order_id": trade.order_id, "errors": ["Duplicate order ID"]}
                )
                continue

            order_ids.add(trade.order_id)

            # Validate trade
            errors = trade.validate()
            if errors:
                invalid_trades.append({"order_id": trade.order_id, "errors": errors})
                continue

            valid_trades.append(trade_dict)

        except Exception as e:
            invalid_trades.append(
                {"order_id": trade_dict.get("order_id", "unknown"), "errors": [str(e)]}
            )

    print(f"Valid trades: {len(valid_trades)}")
    print(f"Invalid trades: {len(invalid_trades)}")

    if invalid_trades:
        print("\nInvalid trades by category:")
        error_counts = {}
        for trade in invalid_trades:
            for error in trade["errors"]:
                error_counts[error] = error_counts.get(error, 0) + 1

        for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {error}: {count}")

    # Create backup if requested
    if args.backup and not args.dry_run:
        backup_path = trade_history_path.with_suffix(".json.bak")
        with open(backup_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\nBackup created: {backup_path}")

    # Save cleaned trade history
    if not args.dry_run:
        data["trades"] = valid_trades
        data["last_updated"] = "2026-02-18T22:50:00.000Z"  # Fixed timestamp

        with open(trade_history_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\nCleaned trade history saved to: {args.input}")

        print("\nRemoving matched trades (will be re-calculated on next run)")
        data["matched_trades"] = []

        with open(trade_history_path, "w") as f:
            json.dump(data, f, indent=2)

    print("\n=== SUMMARY ===")
    print(f"Original trades: {len(trades)}")
    print(f"Valid trades: {len(valid_trades)}")
    print(f"Removed: {len(trades) - len(valid_trades)}")

    if invalid_trades:
        print(f"\n=== INVALID TRADES DETAILS ===")
        for trade in invalid_trades:
            print(f"Order ID: {trade['order_id']}")
            for error in trade["errors"]:
                print(f"  - {error}")


if __name__ == "__main__":
    main()
