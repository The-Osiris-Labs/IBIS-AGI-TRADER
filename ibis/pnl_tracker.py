from ibis.core.logging_config import get_logger

"""
PnL Tracker - Trade-based PnL Calculation from KuCoin
====================================================
Tracks actual PnL from KuCoin trade history with FIFO matching.

Key Features:
- FIFO (First-In-First-Out) trade matching
- Comprehensive validation checks for trade data
- Detailed error handling and debugging capabilities
- Fee calculation and tracking
- Realized and unrealized PnL reporting
- Open positions tracking

Validation Rules:
- All trade prices and quantities must be positive
- Fees must be non-negative
- Timestamps must be valid unix timestamps
- Symbol format must be valid (without quote currency suffix)
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path

logger = get_logger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors"""

    def __init__(self, message: str, errors: List[str] = None):
        self.message = message
        self.errors = errors or []
        super().__init__(self.message)


class CalculationError(Exception):
    """Custom exception for calculation errors"""

    def __init__(self, message: str, trade_data: Dict = None):
        self.message = message
        self.trade_data = trade_data or {}
        super().__init__(self.message)


@dataclass
class Trade:
    """Represents a single trade from KuCoin

    Attributes:
        order_id: Unique identifier for the order
        symbol: Trading pair symbol (without quote currency)
        side: Trade side - "buy" or "sell"
        price: Execution price in quote currency
        size: Quantity traded
        funds: Total value of the trade in quote currency
        fee: Fee paid for the trade
        fee_currency: Currency the fee was paid in
        timestamp: Unix timestamp in milliseconds
        executed_at: ISO format timestamp
    """

    order_id: str
    symbol: str
    side: str  # "buy" or "sell"
    price: float
    size: float
    funds: float
    fee: float
    fee_currency: str
    timestamp: int  # Unix timestamp in milliseconds
    executed_at: str  # ISO format

    def validate(self) -> List[str]:
        """Validate trade data against business rules"""
        errors = []

        # Validate order ID
        if not self.order_id or len(self.order_id.strip()) == 0:
            errors.append("Order ID cannot be empty")

        # Validate symbol
        if not self.symbol or len(self.symbol.strip()) == 0:
            errors.append("Symbol cannot be empty")
        if len(self.symbol) > 20:
            errors.append(f"Symbol '{self.symbol}' is too long (max 20 characters)")

        # Validate side
        if self.side not in ["buy", "sell"]:
            errors.append(f"Invalid side '{self.side}' - must be 'buy' or 'sell'")

        # Validate price
        if self.price <= 0:
            errors.append(f"Invalid price: {self.price} - must be positive")
        if self.price > 1e10:
            errors.append(f"Price {self.price} exceeds reasonable limit (1e10)")

        # Validate size
        if self.size <= 0:
            errors.append(f"Invalid size: {self.size} - must be positive")
        if self.size > 1e6:
            errors.append(f"Size {self.size} exceeds reasonable limit (1e6)")

        # Validate funds
        if self.funds < 0:
            errors.append(f"Invalid funds: {self.funds} - cannot be negative")

        # Validate fee
        if self.fee < 0:
            errors.append(f"Invalid fee: {self.fee} - cannot be negative")
        if self.fee > self.funds:
            errors.append(f"Fee {self.fee} exceeds trade value {self.funds}")

        # Validate timestamp
        if self.timestamp <= 0:
            errors.append(f"Invalid timestamp: {self.timestamp} - must be positive")
        try:
            datetime.fromtimestamp(self.timestamp / 1000)
        except Exception as e:
            errors.append(f"Invalid timestamp: {self.timestamp} - {e}")

        return errors

    @classmethod
    def from_kucoin_order(cls, order: Dict) -> "Trade":
        """Create Trade from KuCoin order response

        Args:
            order: KuCoin API order response

        Returns:
            Trade object

        Raises:
            ValidationError: If order data is invalid
        """
        try:
            # Extract price - calculate from dealSize/dealFunds if price is 0
            price_str = order.get("price", "0")
            if price_str in ["0", "0.0", "", None]:
                deal_size = float(order.get("dealSize", 0) or 0)
                deal_funds = float(order.get("dealFunds", 0) or 0)
                if deal_size > 0 and deal_funds > 0:
                    price = deal_funds / deal_size
                else:
                    price = 0.0
            else:
                price = float(price_str)

            trade = cls(
                order_id=order.get("id", "") or order.get("orderId", ""),
                symbol=order.get("symbol", "").replace("-USDT", ""),
                side=order.get("side", "").lower(),
                price=price,
                size=float(order.get("dealSize", 0) or 0),
                funds=float(order.get("dealFunds", 0) or 0),
                fee=float(order.get("fee", 0) or 0),
                fee_currency=order.get("feeCurrency", "USDT"),
                timestamp=int(order.get("createdAt", 0)),
                executed_at=str(order.get("createdAt", "")),
            )

            # Validate the trade
            errors = trade.validate()
            if errors:
                raise ValidationError(
                    f"Invalid trade data from KuCoin order {trade.order_id}", errors
                )

            return trade

        except Exception as e:
            raise ValidationError(f"Failed to parse KuCoin order: {str(e)}", [str(e)])


@dataclass
class MatchedTrade:
    """A completed round-trip trade (buy + sell)

    Attributes:
        buy_trade: The buy trade that opened the position
        sell_trade: The sell trade that closed the position
        quantity: Quantity matched in this round-trip
        entry_price: Average entry price
        exit_price: Average exit price
        gross_pnl: Gross profit/loss before fees
        fees: Total fees paid for both trades
        net_pnl: Net profit/loss after fees
        pnl_pct: Percentage profit/loss
        duration_seconds: Time held in seconds
        opened_at: ISO timestamp when position was opened
        closed_at: ISO timestamp when position was closed
    """

    buy_trade: Trade
    sell_trade: Trade
    quantity: float
    entry_price: float
    exit_price: float
    gross_pnl: float
    fees: float
    net_pnl: float
    pnl_pct: float
    duration_seconds: float
    opened_at: str
    closed_at: str

    def validate(self) -> List[str]:
        """Validate matched trade data"""
        errors = []

        # Validate symbols match
        if self.buy_trade.symbol != self.sell_trade.symbol:
            errors.append(
                f"Symbol mismatch: buy={self.buy_trade.symbol}, sell={self.sell_trade.symbol}"
            )

        # Validate buy then sell order
        if self.buy_trade.timestamp > self.sell_trade.timestamp:
            errors.append(
                f"Invalid trade order: buy timestamp {self.buy_trade.timestamp} "
                f"> sell timestamp {self.sell_trade.timestamp}"
            )

        # Validate quantity
        if self.quantity <= 0:
            errors.append(f"Invalid quantity: {self.quantity} - must be positive")
        if self.quantity > self.buy_trade.size or self.quantity > self.sell_trade.size:
            errors.append(
                f"Matched quantity {self.quantity} exceeds trade sizes "
                f"(buy: {self.buy_trade.size}, sell: {self.sell_trade.size})"
            )

        # Validate prices
        if self.entry_price <= 0 or self.exit_price <= 0:
            errors.append(
                f"Invalid prices: entry={self.entry_price}, exit={self.exit_price} - must be positive"
            )

        # Validate fees
        if self.fees < 0:
            errors.append(f"Invalid fees: {self.fees} - cannot be negative")

        # Validate duration
        if self.duration_seconds < 0:
            errors.append(f"Invalid duration: {self.duration_seconds} - cannot be negative")

        return errors

    def to_dict(self) -> Dict:
        return {
            "symbol": self.buy_trade.symbol,
            "order_id_buy": self.buy_trade.order_id,
            "order_id_sell": self.sell_trade.order_id,
            "quantity": self.quantity,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "gross_pnl": self.gross_pnl,
            "fees": self.fees,
            "net_pnl": self.net_pnl,
            "pnl_pct": self.pnl_pct,
            "duration_seconds": self.duration_seconds,
            "opened_at": self.opened_at,
            "closed_at": self.closed_at,
        }


class PnLTracker:
    """Track PnL from actual KuCoin trade history"""

    def __init__(self, trade_history_file: str = None):
        self.trade_history_file = (
            trade_history_file
            or "/root/projects/Dont enter unless solicited/AGI Trader/data/trade_history.json"
        )
        self.trade_history_path = Path(self.trade_history_file)
        self._trades: List[Trade] = []
        self._matched_trades: List[MatchedTrade] = []
        self._load_trade_history()

    def _load_trade_history(self):
        """Load existing trade history from file"""
        try:
            if self.trade_history_path.exists():
                with open(self.trade_history_path, "r") as f:
                    data = json.load(f)
                    self._trades = [Trade(**t) for t in data.get("trades", [])]
                    # Load matched trades as dicts for reference, not as MatchedTrade objects
                    # since MatchedTrade expects Trade objects
                    logger.info(f"Loaded {len(self._trades)} trades from history")
        except Exception as e:
            logger.warning(f"Could not load trade history: {e}")
            self._trades = []

        # Always start with fresh matching from KuCoin
        self._matched_trades = []

    def _save_trade_history(self):
        """Save trade history to file"""
        try:
            data = {
                "trades": [asdict(t) for t in self._trades],
                "matched_trades": [t.to_dict() for t in self._matched_trades],
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.trade_history_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save trade history: {e}", exc_info=True)

    async def sync_trades_from_kucoin(self, client) -> List[Trade]:
        """Fetch all trades from KuCoin and sync with local history"""
        try:
            # Use retry logic for reliability
            data = await client._request_with_retry("GET", "/api/v1/orders")
            items = data.get("items", []) if data else []

            # Filter to filled orders
            filled_orders = [
                o
                for o in items
                if o.get("isActive") == False and o.get("dealSize", "0") not in ["", "0", "0.0", 0]
            ]

            # Convert to Trade objects with validation
            new_trades = []
            from ibis.database.db import IbisDB

            db = IbisDB()

            for order in filled_orders:
                try:
                    trade = Trade.from_kucoin_order(order)

                    # Validate trade data
                    if trade.price <= 0 or trade.size <= 0:
                        logger.warning(f"Invalid trade data: {order.get('orderId', 'unknown')}")
                        continue

                    # Check if we already have this trade
                    existing_ids = {t.order_id for t in self._trades}
                    if trade.order_id not in existing_ids:
                        self._trades.append(trade)
                        new_trades.append(trade)

                    # Record fee information in fee_history table
                    if trade.fee > 0:
                        db.update_fee_tracking(
                            symbol=trade.symbol,
                            fees=trade.fee,
                            trade_value=trade.funds,
                            side=trade.side.upper(),
                            order_id=trade.order_id,
                        )

                except Exception as e:
                    logger.error(
                        f"Error processing order {order.get('orderId', 'unknown')}: {e}",
                        exc_info=True,
                    )
                    continue

            if new_trades:
                logger.info(f"Synced {len(new_trades)} new trades from KuCoin")
                self._save_trade_history()

            return self._trades

        except Exception as e:
            logger.error(f"Error syncing trades from KuCoin: {e}", exc_info=True)
            return self._trades

    def match_trades_fifo(self, symbol: str = None, validate: bool = True) -> List[MatchedTrade]:
        """Match buy and sell trades using FIFO method - interleaved by timestamp

        Args:
            symbol: Optional symbol to filter trades
            validate: Whether to validate matched trades

        Returns:
            List of matched round-trip trades

        Raises:
            ValidationError: If any trade or matched trade fails validation
        """
        # Validate input
        if symbol and not isinstance(symbol, str):
            raise ValidationError("Symbol must be a string")
        if symbol and len(symbol.strip()) == 0:
            raise ValidationError("Symbol cannot be empty")

        # Filter trades by symbol if provided
        if symbol:
            trades = [t for t in self._trades if t.symbol == symbol]
        else:
            trades = self._trades

        logger.debug(f"Matching {len(trades)} trades for symbol: {symbol or 'all'}")

        # Validate all trades before matching
        invalid_trades = []
        for trade in trades:
            errors = trade.validate()
            if errors:
                invalid_trades.append(
                    {"order_id": trade.order_id, "symbol": trade.symbol, "errors": errors}
                )
                logger.warning(f"Invalid trade {trade.order_id}: {', '.join(errors)}")

        if invalid_trades:
            raise ValidationError(
                f"Found {len(invalid_trades)} invalid trades",
                [f"{t['order_id']}: {', '.join(t['errors'])}" for t in invalid_trades],
            )

        # Group trades by symbol first for proper matching
        trades_by_symbol = {}
        for trade in trades:
            if trade.symbol not in trades_by_symbol:
                trades_by_symbol[trade.symbol] = {"buy": [], "sell": []}
            if trade.side == "buy":
                # Create copy to avoid modifying original trade objects
                trades_by_symbol[trade.symbol]["buy"].append(
                    Trade(
                        order_id=trade.order_id,
                        symbol=trade.symbol,
                        side=trade.side,
                        price=trade.price,
                        size=trade.size,
                        funds=trade.funds,
                        fee=trade.fee,
                        fee_currency=trade.fee_currency,
                        timestamp=trade.timestamp,
                        executed_at=trade.executed_at,
                    )
                )
            elif trade.side == "sell":
                trades_by_symbol[trade.symbol]["sell"].append(
                    Trade(
                        order_id=trade.order_id,
                        symbol=trade.symbol,
                        side=trade.side,
                        price=trade.price,
                        size=trade.size,
                        funds=trade.funds,
                        fee=trade.fee,
                        fee_currency=trade.fee_currency,
                        timestamp=trade.timestamp,
                        executed_at=trade.executed_at,
                    )
                )

        # Sort each symbol's trades by timestamp
        for symbol in trades_by_symbol:
            trades_by_symbol[symbol]["buy"].sort(key=lambda x: x.timestamp)
            trades_by_symbol[symbol]["sell"].sort(key=lambda x: x.timestamp)

        matched = []

        # Process each symbol separately
        for symbol, sides in trades_by_symbol.items():
            buy_queue = sides["buy"].copy()
            sells = sides["sell"].copy()
            buy_index = 0
            sell_index = 0

            logger.debug(f"Processing symbol {symbol}: {len(buy_queue)} buys, {len(sells)} sells")

            while buy_index < len(buy_queue) and sell_index < len(sells):
                buy = buy_queue[buy_index]
                sell = sells[sell_index]

                remaining_sell_qty = sell.size

                while remaining_sell_qty > 0.00000001 and buy_index < len(buy_queue):
                    buy = buy_queue[buy_index]

                    if buy.size <= 0.00000001:
                        buy_index += 1
                        continue

                    # Match the minimum quantity
                    matched_qty = min(buy.size, remaining_sell_qty)

                    try:
                        # Calculate P&L
                        gross_pnl = (sell.price - buy.price) * matched_qty
                        fees = (buy.fee * (matched_qty / buy.size)) + (
                            sell.fee * (matched_qty / sell.size)
                        )
                        net_pnl = gross_pnl - fees

                        # Calculate duration
                        duration_sec = (sell.timestamp - buy.timestamp) / 1000

                        matched_trade = MatchedTrade(
                            buy_trade=buy,
                            sell_trade=sell,
                            quantity=matched_qty,
                            entry_price=buy.price,
                            exit_price=sell.price,
                            gross_pnl=gross_pnl,
                            fees=fees,
                            net_pnl=net_pnl,
                            pnl_pct=((sell.price - buy.price) / buy.price * 100)
                            if buy.price > 0
                            else 0,
                            duration_seconds=duration_sec,
                            opened_at=buy.executed_at,
                            closed_at=sell.executed_at,
                        )

                        # Validate the matched trade
                        if validate:
                            errors = matched_trade.validate()
                            if errors:
                                raise ValidationError(
                                    f"Invalid matched trade: buy={buy.order_id}, sell={sell.order_id}",
                                    errors,
                                )

                        matched.append(matched_trade)
                        logger.debug(
                            f"Matched trade {symbol}: buy={buy.order_id}, sell={sell.order_id}, "
                            f"qty={matched_qty:.8f}, net_pnl={net_pnl:.4f}"
                        )

                        # Update quantities
                        buy.size -= matched_qty
                        remaining_sell_qty -= matched_qty

                        # Move to next buy if fully matched
                        if buy.size <= 0.00000001:
                            buy_index += 1

                    except Exception as e:
                        raise CalculationError(
                            f"Failed to match trade {symbol}: buy={buy.order_id}, sell={sell.order_id} - {str(e)}",
                            {
                                "buy_trade": buy.to_dict() if hasattr(buy, "to_dict") else str(buy),
                                "sell_trade": sell.to_dict()
                                if hasattr(sell, "to_dict")
                                else str(sell),
                            },
                        )

                # Move to next sell if fully matched
                if remaining_sell_qty <= 0.00000001:
                    sell_index += 1

        self._matched_trades = matched
        self._save_trade_history()

        logger.debug(f"Successfully matched {len(matched)} round-trip trades")

        return matched

    def get_weekly_pnl(self, symbol: str = None) -> Dict:
        """Calculate weekly PnL from matched trades

        Args:
            symbol: Optional symbol to filter trades

        Returns:
            PnL summary including total P&L, win rate, average trade size, etc.
        """
        return self._get_period_pnl(symbol, days=7)

    def get_monthly_pnl(self, symbol: str = None) -> Dict:
        """Calculate monthly PnL from matched trades

        Args:
            symbol: Optional symbol to filter trades

        Returns:
            PnL summary including total P&L, win rate, average trade size, etc.
        """
        return self._get_period_pnl(symbol, days=30)

    def get_all_time_pnl(self, symbol: str = None) -> Dict:
        """Calculate all-time PnL from matched trades

        Args:
            symbol: Optional symbol to filter trades

        Returns:
            PnL summary including total P&L, win rate, average trade size, etc.
        """
        if symbol and not isinstance(symbol, str):
            raise ValidationError("Symbol must be a string")

        if symbol:
            trades = [t for t in self._matched_trades if t.buy_trade.symbol == symbol]
        else:
            trades = self._matched_trades

        return self._calculate_pnl_summary(trades)

    def _get_period_pnl(self, symbol: str, days: int) -> Dict:
        """Internal method to calculate PnL for a specific time period

        Args:
            symbol: Optional symbol to filter trades
            days: Number of days in the period

        Returns:
            PnL summary
        """
        if symbol and not isinstance(symbol, str):
            raise ValidationError("Symbol must be a string")
        if days <= 0:
            raise ValidationError("Days must be a positive integer")

        now = datetime.now()
        period_start = now - timedelta(days=days)

        if symbol:
            trades = [t for t in self._matched_trades if t.buy_trade.symbol == symbol]
        else:
            trades = self._matched_trades

        def parse_timestamp(ts):
            """Parse timestamp (ms) to datetime"""
            if isinstance(ts, (int, float)):
                return datetime.fromtimestamp(ts / 1000)
            elif isinstance(ts, str) and ts.isdigit():
                return datetime.fromtimestamp(int(ts) / 1000)
            elif isinstance(ts, str):
                return datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return now

        period_trades = [
            t for t in trades if t.closed_at and parse_timestamp(t.closed_at) >= period_start
        ]

        return self._calculate_pnl_summary(period_trades)

    def _calculate_pnl_summary(self, trades: List[MatchedTrade]) -> Dict:
        """Internal method to calculate PnL summary from matched trades

        Args:
            trades: List of matched trades to summarize

        Returns:
            PnL summary dictionary
        """
        if not isinstance(trades, list):
            raise ValidationError("Trades must be a list")

        for trade in trades:
            if not isinstance(trade, MatchedTrade):
                raise ValidationError("All items must be MatchedTrade instances")

        total_pnl = sum(t.net_pnl for t in trades)
        wins = sum(1 for t in trades if t.net_pnl > 0)
        losses = sum(1 for t in trades if t.net_pnl <= 0)
        total_fees = sum(t.fees for t in trades)
        total_quantity = sum(t.quantity for t in trades)
        total_duration = sum(t.duration_seconds for t in trades)

        avg_trade_size = total_quantity / len(trades) if trades else 0
        avg_duration = total_duration / len(trades) if trades else 0
        avg_fees_per_trade = total_fees / len(trades) if trades else 0

        return {
            "pnl": total_pnl,
            "trades": len(trades),
            "wins": wins,
            "losses": losses,
            "win_rate": wins / len(trades) * 100 if trades else 0,
            "avg_win": sum(t.net_pnl for t in trades if t.net_pnl > 0) / wins if wins > 0 else 0,
            "avg_loss": sum(t.net_pnl for t in trades if t.net_pnl <= 0) / losses
            if losses > 0
            else 0,
            "best_trade": max((t.net_pnl for t in trades), default=0),
            "worst_trade": min((t.net_pnl for t in trades), default=0),
            "total_fees": total_fees,
            "avg_fees_per_trade": avg_fees_per_trade,
            "avg_trade_size": avg_trade_size,
            "avg_duration": avg_duration,
            "trades_detail": [t.to_dict() for t in trades],
        }

    def get_open_positions(self) -> List[Dict]:
        """Get current open positions (unmatched buys)

        Returns:
            List of open positions with symbol, quantity, average entry price, and total cost
        """
        trades_by_symbol = {}
        for t in self._trades:
            if t.symbol not in trades_by_symbol:
                trades_by_symbol[t.symbol] = {"buy": [], "sell": []}
            trades_by_symbol[t.symbol][t.side].append(t)

        open_positions = []
        for symbol, sides in trades_by_symbol.items():
            buys = sorted(sides["buy"], key=lambda t: t.timestamp)
            sells = sorted(sides["sell"], key=lambda t: t.timestamp)

            # FIFO matching to find remaining quantity
            remaining_qty = 0
            total_cost = 0
            for buy in buys:
                remaining_qty += buy.size
                total_cost += buy.price * buy.size

            buy_sizes = sum(b.size for b in buys)
            avg_cost = total_cost / buy_sizes if buy_sizes > 0 else 0

            for sell in sells:
                sell_qty = min(sell.size, remaining_qty)
                remaining_qty -= sell_qty
                total_cost -= avg_cost * sell_qty

            if remaining_qty > 0.00000001:
                avg_buy_price = total_cost / remaining_qty if remaining_qty > 0 else 0
                position = {
                    "symbol": symbol,
                    "quantity": remaining_qty,
                    "avg_entry_price": avg_buy_price,
                    "total_cost": total_cost,
                }
                open_positions.append(position)
                logger.debug(f"Open position: {symbol} - {remaining_qty:.8f} @ {avg_buy_price:.4f}")

        logger.debug(f"Total open positions: {len(open_positions)}")
        return open_positions

    def validate_trade_history(self) -> Dict:
        """Validate entire trade history for consistency and errors

        Returns:
            Validation report with errors and warnings
        """
        report = {
            "total_trades": len(self._trades),
            "valid_trades": 0,
            "invalid_trades": 0,
            "errors": [],
            "warnings": [],
            "duplicate_order_ids": [],
        }

        # Check for duplicates
        order_ids = set()
        for trade in self._trades:
            if trade.order_id in order_ids:
                report["duplicate_order_ids"].append(trade.order_id)
                report["warnings"].append(f"Duplicate order ID: {trade.order_id}")
            order_ids.add(trade.order_id)

        # Validate each trade
        for i, trade in enumerate(self._trades):
            try:
                errors = trade.validate()
                if errors:
                    report["invalid_trades"] += 1
                    report["errors"].append(
                        {
                            "trade_index": i,
                            "order_id": trade.order_id,
                            "symbol": trade.symbol,
                            "errors": errors,
                        }
                    )
                else:
                    report["valid_trades"] += 1
            except Exception as e:
                report["invalid_trades"] += 1
                report["errors"].append(
                    {
                        "trade_index": i,
                        "order_id": getattr(trade, "order_id", "unknown"),
                        "symbol": getattr(trade, "symbol", "unknown"),
                        "errors": [str(e)],
                    }
                )

        # Check for symbol consistency
        symbols = set()
        for trade in self._trades:
            symbols.add(trade.symbol)

        # Check for trade pairs consistency
        for symbol in symbols:
            symbol_trades = [t for t in self._trades if t.symbol == symbol]
            buy_count = sum(1 for t in symbol_trades if t.side == "buy")
            sell_count = sum(1 for t in symbol_trades if t.side == "sell")

            if buy_count == 0 or sell_count == 0:
                report["warnings"].append(
                    f"Symbol {symbol} has only {buy_count} buy and {sell_count} sell trades"
                )

        logger.debug(f"Validation report: {json.dumps(report, indent=2)}")

        return report

    def debug_calculation(self, symbol: str = None, detailed: bool = False) -> Dict:
        """Debug P&L calculation with detailed information

        Args:
            symbol: Optional symbol to debug
            detailed: Whether to include detailed trade information

        Returns:
            Debug information about the calculation
        """
        debug_info = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "total_trades": len(self._trades),
            "matched_trades": len(self._matched_trades),
        }

        if symbol:
            symbol_trades = [t for t in self._trades if t.symbol == symbol]
            symbol_matched = [t for t in self._matched_trades if t.buy_trade.symbol == symbol]
        else:
            symbol_trades = self._trades
            symbol_matched = self._matched_trades

        debug_info["symbol_trades"] = len(symbol_trades)
        debug_info["symbol_matched"] = len(symbol_matched)

        if detailed:
            debug_info["trades"] = []
            for trade in symbol_trades:
                debug_info["trades"].append(
                    {
                        "order_id": trade.order_id,
                        "side": trade.side,
                        "price": trade.price,
                        "size": trade.size,
                        "timestamp": trade.timestamp,
                        "fee": trade.fee,
                    }
                )

            debug_info["matched_trades_detail"] = []
            for mt in symbol_matched:
                debug_info["matched_trades_detail"].append(
                    {
                        "buy_order": mt.buy_trade.order_id,
                        "sell_order": mt.sell_trade.order_id,
                        "quantity": mt.quantity,
                        "entry_price": mt.entry_price,
                        "exit_price": mt.exit_price,
                        "gross_pnl": mt.gross_pnl,
                        "fees": mt.fees,
                        "net_pnl": mt.net_pnl,
                        "pnl_pct": mt.pnl_pct,
                    }
                )

        return debug_info

    def get_trade_history(self, symbol: str = None, limit: int = 50) -> List[Dict]:
        """Get recent trade history"""
        if symbol:
            trades = [t for t in self._matched_trades if t.buy_trade.symbol == symbol]
        else:
            trades = self._matched_trades

        return [
            t.to_dict()
            for t in sorted(trades, key=lambda t: t.sell_trade.timestamp, reverse=True)[:limit]
        ]

    def calculate_average_fees_per_symbol(self) -> Dict[str, Dict[str, float]]:
        """Calculate average maker/taker fees per symbol from historical trades"""
        symbol_fees = {}

        # Group trades by symbol and side
        trades_by_symbol = {}
        for trade in self._trades:
            if trade.symbol not in trades_by_symbol:
                trades_by_symbol[trade.symbol] = {"buy": [], "sell": []}
            trades_by_symbol[trade.symbol][trade.side].append(trade)

        # Calculate average fees per symbol
        for symbol, sides in trades_by_symbol.items():
            # Calculate fee rates (fee / funds) for each trade
            maker_fees = []
            taker_fees = []

            for trade in sides["buy"] + sides["sell"]:
                if trade.funds > 0:
                    fee_rate = trade.fee / trade.funds
                    # For now, assume all trades are taker (we can add order type detection later)
                    # In future, we could analyze order types from KuCoin data
                    taker_fees.append(fee_rate)
                    # For maker fees, we can use the same rate if we don't have order type info
                    maker_fees.append(fee_rate)

            if maker_fees and taker_fees:
                symbol_fees[symbol] = {
                    "maker": sum(maker_fees) / len(maker_fees),
                    "taker": sum(taker_fees) / len(taker_fees),
                    "count": len(maker_fees),
                }

        return symbol_fees

    def update_trading_constants_fees(self):
        """Update trading constants with dynamic fee rates from historical data"""
        from ibis.core.trading_constants import TRADING

        symbol_fees = self.calculate_average_fees_per_symbol()

        for symbol, fees in symbol_fees.items():
            TRADING.EXCHANGE.update_symbol_fees(symbol, fees["maker"], fees["taker"])

        logger.info(f"Updated dynamic fees for {len(symbol_fees)} symbols from PnL tracker")

    def get_average_fee_rate(self, symbol: str = None) -> Dict[str, float]:
        """Get average fee rates for a specific symbol or overall"""
        all_symbol_fees = self.calculate_average_fees_per_symbol()

        if symbol and symbol in all_symbol_fees:
            return {
                "maker": all_symbol_fees[symbol]["maker"],
                "taker": all_symbol_fees[symbol]["taker"],
                "count": all_symbol_fees[symbol]["count"],
            }

        # Calculate overall average if symbol not specified or no data
        total_maker = 0
        total_taker = 0
        total_count = 0

        for fees in all_symbol_fees.values():
            total_maker += fees["maker"] * fees["count"]
            total_taker += fees["taker"] * fees["count"]
            total_count += fees["count"]

        if total_count > 0:
            return {
                "maker": total_maker / total_count,
                "taker": total_taker / total_count,
                "count": total_count,
            }

        # Default fallback rates
        return {
            "maker": 0.0010,  # 0.10%
            "taker": 0.0010,  # 0.10%
            "count": 0,
        }

    def get_fee_analysis(self, symbol: str = None) -> Dict:
        """Get comprehensive fee analysis using advanced intelligence"""
        from ibis.advanced_intelligence import FeeAnalyzer

        analyzer = FeeAnalyzer(self)
        matched_trades = self._matched_trades

        if symbol:
            matched_trades = [t for t in self._matched_trades if t.buy_trade.symbol == symbol]

        fee_result = analyzer.analyze_fee_impact(matched_trades, symbol)
        recommendations = analyzer.get_fee_optimization_recommendations(symbol)

        return {"analysis": fee_result.__dict__, "recommendations": recommendations}


async def calculate_realized_pnl_from_fills(fills: List[Dict]) -> Dict:
    """Calculate realized PnL from a list of KuCoin fills"""
    trades = [Trade.from_kucoin_order(f) for f in fills]

    tracker = PnLTracker()
    tracker._trades = trades
    tracker.match_trades_fifo()

    return tracker.get_all_time_pnl()
