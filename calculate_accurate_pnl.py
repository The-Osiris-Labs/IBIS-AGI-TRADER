import sys
import json
import sqlite3
import pandas as pd
from collections import defaultdict
import logging
from ibis.pnl_tracker import ValidationError, CalculationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

try:
    # Connect to database
    conn = sqlite3.connect("/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_v8.db")
    cursor = conn.cursor()

    # Fetch all trades
    logger.info("=== Fetching all trades from database ===")
    trades_df = pd.read_sql_query("SELECT * FROM trades", conn)
    logger.info(f"Total trades found: {len(trades_df)}")

    # Validate trade data
    if trades_df.empty:
        raise ValidationError("No trades found in the database")

    # Check for invalid data
    invalid_rows = []
    for index, row in trades_df.iterrows():
        errors = []
        if row['price'] <= 0:
            errors.append(f"Invalid price: {row['price']}")
        if row['quantity'] <= 0:
            errors.append(f"Invalid quantity: {row['quantity']}")
        if row['fees'] < 0:
            errors.append(f"Invalid fees: {row['fees']}")
        if row['side'] not in ['BUY', 'SELL']:
            errors.append(f"Invalid side: {row['side']}")
        if errors:
            invalid_rows.append((index, errors))

    if invalid_rows:
        logger.warning(f"Found {len(invalid_rows)} invalid trades:")
        for index, errors in invalid_rows:
            logger.warning(f"  Row {index}: {', '.join(errors)}")

    # Check if we have fee_history table
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fee_history';")
        fee_table = cursor.fetchone()
        if fee_table:
            logger.info("\n=== Fee History Table ===")
            fee_df = pd.read_sql_query("SELECT * FROM fee_history", conn)
            logger.info(f"Fee history records: {len(fee_df)}")
            logger.debug(fee_df.to_string(index=False))
        else:
            logger.warning("\n=== Fee History Table Not Found ===")
    except Exception as e:
        logger.error(f"\nError checking fee_history table: {e}")


def calculate_fifo_pnl(trades):
    """Calculate P&L using FIFO accounting
    
    Args:
        trades: DataFrame of trades with validation
    
    Returns:
        (total_pnl, total_fees, symbol_summary)
        
    Raises:
        CalculationError: If calculation fails
    """
    try:
        # Group trades by symbol
        symbol_trades = defaultdict(list)
        for _, trade in trades.iterrows():
            symbol_trades[trade["symbol"]].append(trade)

        total_pnl = 0.0
        total_fees = 0.0
        symbol_summary = {}

        for symbol, symbol_trade_list in symbol_trades.items():
            logger.debug(f"Processing symbol: {symbol}")
            
            # Separate buys and sells
            buys = []
            sells = []

            for trade in symbol_trade_list:
                if trade["side"] == "BUY":
                    buys.append(
                        {
                            "id": trade["id"],
                            "price": trade["price"],
                            "size": trade["quantity"],
                            "time": trade["timestamp"],
                            "fees": trade["fees"] if pd.notna(trade["fees"]) else 0.0,
                        }
                    )
                elif trade["side"] == "SELL":
                    sells.append(
                        {
                            "id": trade["id"],
                            "price": trade["price"],
                            "size": trade["quantity"],
                            "time": trade["timestamp"],
                            "fees": trade["fees"] if pd.notna(trade["fees"]) else 0.0,
                        }
                    )

            # Sort by time
            buys.sort(key=lambda x: x["time"])
            sells.sort(key=lambda x: x["time"])

            logger.debug(f"Found {len(buys)} buy and {len(sells)} sell trades for {symbol}")

            # Process FIFO
            buy_index = 0
            sell_index = 0
            symbol_pnl = 0.0
            symbol_fees = 0.0

            while buy_index < len(buys) and sell_index < len(sells):
                buy = buys[buy_index]
                sell = sells[sell_index]

                # Determine how much we can match
                match_size = min(buy["size"], sell["size"])

                # Calculate P&L for this match
                profit = match_size * (sell["price"] - buy["price"])

                # Calculate fees - use actual fees from database if available, otherwise 0.05% per trade
                if buy["fees"] > 0 and sell["fees"] > 0:
                    fee_buy = (buy["fees"] / buy["size"]) * match_size
                    fee_sell = (sell["fees"] / sell["size"]) * match_size
                else:
                    fee_buy = match_size * buy["price"] * 0.0005
                    fee_sell = match_size * sell["price"] * 0.0005

                total_fees_match = fee_buy + fee_sell

                # Add to totals
                symbol_pnl += profit - total_fees_match
                symbol_fees += total_fees_match

                # Update sizes
                buy["size"] -= match_size
                sell["size"] -= match_size

                # Move to next trade if size is zero
                if buy["size"] == 0:
                    buy_index += 1
                if sell["size"] == 0:
                    sell_index += 1

            total_pnl += symbol_pnl
            total_fees += symbol_fees

            # Track open positions
            open_buy_size = 0.0
            if buy_index < len(buys):
                open_buy_size = sum(b["size"] for b in buys[buy_index:])

            symbol_summary[symbol] = {
                "pnl": symbol_pnl,
                "fees": symbol_fees,
                "open_position": open_buy_size,
            }

        # Print detailed breakdown per symbol
        print("\n=== Detailed P&L Breakdown by Symbol ===")
        print(f"{'Symbol':<12} {'P&L ($)':<15} {'Fees ($)':<15} {'Open Position':<15}")
        print("-" * 60)
        for symbol, data in sorted(symbol_summary.items()):
            print(
                f"{symbol:<12} {data['pnl']:,.2f} {' ':<6} {data['fees']:,.2f} {' ':<6} {data['open_position']:,.4f}"
            )

        print("\n=== FINAL CALCULATION ===")
        print(f"Total P&L: ${total_pnl:,.2f}")
        print(f"Total Fees: ${total_fees:,.2f}")

        return total_pnl, total_fees, symbol_summary

    except Exception as e:
        raise CalculationError(f"FIFO P&L calculation failed: {str(e)}", {"trades": trades.to_dict()})


# Calculate P&L
final_pnl, final_fees, symbol_summary = calculate_fifo_pnl(trades_df)

except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    if hasattr(e, 'errors') and e.errors:
        for error in e.errors:
            logger.error(f"  - {error}")
    sys.exit(1)
except CalculationError as e:
    logger.error(f"Calculation failed: {e}")
    if hasattr(e, 'trade_data') and e.trade_data:
        logger.debug(f"Trade data: {json.dumps(e.trade_data, indent=2, default=str)}")
    sys.exit(2)
except Exception as e:
    logger.error(f"Error: {e}")
    import traceback
    logger.debug(f"Stack trace: {traceback.format_exc()}")
    sys.exit(3)
finally:
    if 'conn' in locals():
        conn.close()
