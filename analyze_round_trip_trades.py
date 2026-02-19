#!/usr/bin/env python3
"""
Fetch detailed spot trade history with complete round-trip trades, PnL calculation,
fee breakdown, and position duration for the IBIS system.
"""

import sqlite3
from datetime import datetime
from ibis.database.db import IbisDB
from ibis.pnl_tracker import ValidationError, CalculationError
from typing import List, Dict, Tuple, Optional
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)


class TradeAnalyzer:
    def __init__(self):
        self.db = IbisDB()

    def get_trades_by_symbol(self) -> Dict[str, List[Dict]]:
        """Get all trades grouped by symbol"""
        with self.db.get_conn() as conn:
            cursor = conn.execute("SELECT * FROM trades ORDER BY symbol, timestamp")
            trades = [dict(row) for row in cursor.fetchall()]

        symbol_trades = {}
        for trade in trades:
            symbol = trade["symbol"]
            if symbol not in symbol_trades:
                symbol_trades[symbol] = []
            symbol_trades[symbol].append(trade)

        return symbol_trades

    def get_fee_history(self) -> Dict[str, List[Dict]]:
        """Get fee history grouped by order ID"""
        with self.db.get_conn() as conn:
            cursor = conn.execute("SELECT * FROM fee_history")
            fees = [dict(row) for row in cursor.fetchall()]

        order_fees = {}
        for fee in fees:
            order_id = fee["order_id"]
            if order_id not in order_fees:
                order_fees[order_id] = []
            order_fees[order_id].append(fee)

        return order_fees

    def match_round_trip_trades(self, trades: List[Dict]) -> List[Dict]:
        """
        Match buy and sell trades to form complete round-trip positions
        and calculate detailed metrics

        Args:
            trades: List of trades to match

        Returns:
            List of matched round-trip trades

        Raises:
            ValidationError: If trade data is invalid
            CalculationError: If matching fails
        """
        round_trips = []
        open_positions = []

        # Validate input
        if not isinstance(trades, list):
            raise ValidationError("Trades must be a list")

        for trade in trades:
            if not isinstance(trade, dict):
                raise ValidationError("Each trade must be a dictionary")

            required_fields = ["id", "symbol", "side", "price", "quantity", "timestamp", "fees"]
            for field in required_fields:
                if field not in trade:
                    raise ValidationError(f"Trade missing required field: {field}")

            if trade["price"] <= 0 or trade["quantity"] <= 0:
                raise ValidationError(
                    f"Invalid trade values: price={trade['price']}, quantity={trade['quantity']}"
                )

        try:
            for trade in sorted(trades, key=lambda x: x["timestamp"]):
                if trade["side"] == "BUY":
                    open_positions.append(trade)
                elif trade["side"] == "SELL" and open_positions:
                    # Match the most recent buy with this sell
                    buy_trade = open_positions.pop()
                    round_trip = self.calculate_round_trip_metrics(buy_trade, trade)
                    round_trips.append(round_trip)

            logger.info(f"Successfully matched {len(round_trips)} round-trip trades")
            return round_trips

        except Exception as e:
            raise CalculationError(
                f"Failed to match round-trip trades: {str(e)}", {"trades": trades}
            )

    def calculate_round_trip_metrics(self, buy_trade: Dict, sell_trade: Dict) -> Dict:
        """Calculate detailed metrics for a round-trip trade"""
        # Calculate gross P&L (without fees)
        buy_value = buy_trade["quantity"] * buy_trade["price"]
        sell_value = sell_trade["quantity"] * sell_trade["price"]
        gross_pnl = sell_value - buy_value

        # Calculate net P&L (with fees)
        total_fees = buy_trade["fees"] + sell_trade["fees"]
        net_pnl = gross_pnl - total_fees

        # Calculate P&L percentage
        gross_pnl_pct = (gross_pnl / buy_value) * 100
        net_pnl_pct = (net_pnl / buy_value) * 100

        # Calculate position duration
        buy_time = datetime.fromisoformat(buy_trade["timestamp"])
        sell_time = datetime.fromisoformat(sell_trade["timestamp"])
        duration = sell_time - buy_time

        # Get fee details
        buy_fee = buy_trade["fees"]
        sell_fee = sell_trade["fees"]

        return {
            "symbol": buy_trade["symbol"],
            "buy_timestamp": buy_trade["timestamp"],
            "sell_timestamp": sell_trade["timestamp"],
            "duration": str(duration),
            "duration_seconds": duration.total_seconds(),
            "quantity": buy_trade["quantity"],
            "entry_price": buy_trade["price"],
            "exit_price": sell_trade["price"],
            "entry_value": buy_value,
            "exit_value": sell_value,
            "gross_pnl": gross_pnl,
            "gross_pnl_pct": gross_pnl_pct,
            "net_pnl": net_pnl,
            "net_pnl_pct": net_pnl_pct,
            "buy_fee": buy_fee,
            "sell_fee": sell_fee,
            "total_fees": total_fees,
            "buy_order_id": buy_trade["order_id"],
            "sell_order_id": sell_trade["order_id"],
            "buy_reason": buy_trade["reason"],
            "sell_reason": sell_trade["reason"],
        }

    def analyze_all_round_trips(self) -> List[Dict]:
        """Analyze all trades and find complete round-trips"""
        symbol_trades = self.get_trades_by_symbol()
        all_round_trips = []

        for symbol, trades in symbol_trades.items():
            round_trips = self.match_round_trip_trades(trades)
            all_round_trips.extend(round_trips)

        # Sort by timestamp
        all_round_trips.sort(key=lambda x: x["buy_timestamp"])

        return all_round_trips

    def print_summary_statistics(self, round_trips: List[Dict]):
        """Print summary statistics of round-trip trades"""
        if not round_trips:
            print("No complete round-trip trades found")
            return

        df = pd.DataFrame(round_trips)

        print("=== Round-Trip Trade Statistics ===")
        print(f"Total complete round-trips: {len(round_trips)}")
        print(f"Total symbols with round-trips: {df['symbol'].nunique()}")
        print()

        profitable = len(df[df["net_pnl"] > 0])
        losing = len(df[df["net_pnl"] < 0])
        breakeven = len(df[df["net_pnl"] == 0])

        print("Profitability Analysis:")
        print(f"  Profitable trades: {profitable} ({profitable / len(round_trips) * 100:.1f}%)")
        print(f"  Losing trades: {losing} ({losing / len(round_trips) * 100:.1f}%)")
        print(f"  Breakeven trades: {breakeven} ({breakeven / len(round_trips) * 100:.1f}%)")
        print()

        print("P&L Summary:")
        print(f"  Total gross P&L: ${df['gross_pnl'].sum():,.2f}")
        print(f"  Total net P&L: ${df['net_pnl'].sum():,.2f}")
        print(f"  Total fees paid: ${df['total_fees'].sum():,.2f}")
        print(f"  Average net P&L per trade: ${df['net_pnl'].mean():,.2f}")
        print(f"  Average net P&L % per trade: {df['net_pnl_pct'].mean():.2f}%")
        print()

        print("Duration Analysis:")
        avg_duration = df["duration_seconds"].mean()
        avg_hours = avg_duration / 3600
        print(f"  Average position duration: {avg_hours:.2f} hours")
        print()

        print("Top 5 Most Profitable Trades:")
        top_profitable = df.sort_values("net_pnl", ascending=False).head()
        for _, row in top_profitable.iterrows():
            print(f"  {row['symbol']}: ${row['net_pnl']:.2f} ({row['net_pnl_pct']:.2f}%)")

        print()

        print("Bottom 5 Most Losing Trades:")
        top_losing = df.sort_values("net_pnl").head()
        for _, row in top_losing.iterrows():
            print(f"  {row['symbol']}: ${row['net_pnl']:.2f} ({row['net_pnl_pct']:.2f}%)")

    def print_detailed_report(self, round_trips: List[Dict], limit: int = 50):
        """Print detailed report of round-trip trades"""
        if not round_trips:
            print("No complete round-trip trades found")
            return

        print("\n" + "=" * 100)
        print("Detailed Round-Trip Trade Report")
        print("=" * 100)

        # Print table header
        header = ("{:<12} {:<20} {:<12} {:<10} {:<12} {:<12} {:<10} {:<10} {:<12}").format(
            "Symbol",
            "Entry Time",
            "Exit Time",
            "Duration",
            "Quantity",
            "Entry Price",
            "Exit Price",
            "Net P&L",
            "Net P&L %",
        )
        print(header)
        print("-" * 100)

        # Print trades
        for trip in round_trips[-limit:]:
            entry_time = trip["buy_timestamp"].split(" ")[1]
            exit_time = trip["sell_timestamp"].split(" ")[1]

            print(
                "{:<12} {:<20} {:<12} {:<10} {:<12,.2f} {:<12,.4f} {:<12,.4f} {:<10,.2f} {:<10,.2f}%".format(
                    trip["symbol"],
                    entry_time,
                    exit_time,
                    str(trip["duration"]).split(".")[0],  # Remove microseconds
                    trip["quantity"],
                    trip["entry_price"],
                    trip["exit_price"],
                    trip["net_pnl"],
                    trip["net_pnl_pct"],
                )
            )

        print("-" * 100)
        print(f"Showing {min(limit, len(round_trips))} of {len(round_trips)} trades\n")

    def export_to_excel(self, round_trips: List[Dict], filename: str = "round_trip_trades.xlsx"):
        """Export round-trip trades to Excel with detailed breakdown"""
        df = pd.DataFrame(round_trips)

        # Reorder columns for better readability
        columns = [
            "symbol",
            "buy_timestamp",
            "sell_timestamp",
            "duration",
            "duration_seconds",
            "quantity",
            "entry_price",
            "exit_price",
            "entry_value",
            "exit_value",
            "gross_pnl",
            "gross_pnl_pct",
            "net_pnl",
            "net_pnl_pct",
            "buy_fee",
            "sell_fee",
            "total_fees",
            "buy_order_id",
            "sell_order_id",
            "buy_reason",
            "sell_reason",
        ]

        df = df[columns]

        # Save to Excel
        df.to_excel(filename, index=False, sheet_name="Round Trip Trades")
        print(f"\nDetailed report exported to {filename}")


def main():
    try:
        analyzer = TradeAnalyzer()

        print("Analyzing IBIS system spot trade history...")

        # Analyze all round-trip trades
        round_trips = analyzer.analyze_all_round_trips()

        # Print summary
        analyzer.print_summary_statistics(round_trips)

        # Print detailed report of recent trades
        analyzer.print_detailed_report(round_trips, limit=20)

        # Export to Excel
        analyzer.export_to_excel(round_trips)

    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        if e.errors:
            for error in e.errors:
                logger.error(f"  - {error}")
        sys.exit(1)
    except CalculationError as e:
        logger.error(f"Calculation failed: {e}")
        if e.trade_data:
            logger.debug(f"Trade data: {json.dumps(e.trade_data, indent=2, default=str)}")
        sys.exit(2)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        import traceback

        logger.debug(f"Stack trace: {traceback.format_exc()}")
        sys.exit(3)


if __name__ == "__main__":
    import sys
    import json

    main()
