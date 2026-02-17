"""
PnL Tracker - Trade-based PnL Calculation from KuCoin
====================================================
Tracks actual PnL from KuCoin trade history with FIFO matching.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
import logging

logger = logging.getLogger("IBIS")


@dataclass
class Trade:
    """Represents a single trade from KuCoin"""

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

    @classmethod
    def from_kucoin_order(cls, order: Dict) -> "Trade":
        """Create Trade from KuCoin order response"""
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

        return cls(
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


@dataclass
class MatchedTrade:
    """A completed round-trip trade (buy + sell)"""

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
            logger.error(f"Could not save trade history: {e}")

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

                except Exception as e:
                    logger.error(f"Error processing order {order.get('orderId', 'unknown')}: {e}")
                    continue

            if new_trades:
                logger.info(f"Synced {len(new_trades)} new trades from KuCoin")
                self._save_trade_history()

            return self._trades

        except Exception as e:
            logger.error(f"Error syncing trades from KuCoin: {e}")
            return self._trades

    def match_trades_fifo(self, symbol: str = None) -> List[MatchedTrade]:
        """Match buy and sell trades using FIFO method - interleaved by timestamp"""
        # Filter trades by symbol if provided
        if symbol:
            trades = [t for t in self._trades if t.symbol == symbol]
        else:
            trades = self._trades

        # Sort ALL trades by timestamp (interleaved buys and sells)
        all_trades = sorted(trades, key=lambda t: t.timestamp)

        matched = []
        buy_queue = []

        for trade in all_trades:
            if trade.side == "buy":
                # Add buy to queue
                buy_queue.append(trade)
            elif trade.side == "sell":
                # Match sell with oldest buy in queue
                remaining_sell_qty = trade.size

                while remaining_sell_qty > 0.00000001 and buy_queue:
                    buy = buy_queue[0]

                    # Match the minimum quantity
                    matched_qty = min(buy.size, remaining_sell_qty)

                    # Calculate PnL
                    gross_pnl = (trade.price - buy.price) * matched_qty
                    fees = buy.fee + trade.fee
                    net_pnl = gross_pnl - fees

                    # Calculate duration
                    duration_sec = (trade.timestamp - buy.timestamp) / 1000

                    matched_trade = MatchedTrade(
                        buy_trade=buy,
                        sell_trade=trade,
                        quantity=matched_qty,
                        entry_price=buy.price,
                        exit_price=trade.price,
                        gross_pnl=gross_pnl,
                        fees=fees,
                        net_pnl=net_pnl,
                        pnl_pct=((trade.price - buy.price) / buy.price * 100)
                        if buy.price > 0
                        else 0,
                        duration_seconds=duration_sec,
                        opened_at=buy.executed_at,
                        closed_at=trade.executed_at,
                    )
                    matched.append(matched_trade)

                    # Update quantities
                    buy.size -= matched_qty
                    remaining_sell_qty -= matched_qty

                    # Remove fully matched buys
                    if buy.size <= 0.00000001:
                        buy_queue.pop(0)

        self._matched_trades = matched
        self._save_trade_history()

        return matched

    def get_weekly_pnl(self, symbol: str = None) -> Dict:
        """Calculate weekly PnL from matched trades"""
        now = datetime.now()
        week_ago = now - timedelta(days=7)

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

        weekly_trades = [
            t for t in trades if t.closed_at and parse_timestamp(t.closed_at) >= week_ago
        ]

        total_pnl = sum(t.net_pnl for t in weekly_trades)
        wins = sum(1 for t in weekly_trades if t.net_pnl > 0)
        losses = sum(1 for t in weekly_trades if t.net_pnl <= 0)

        return {
            "pnl": total_pnl,
            "trades": len(weekly_trades),
            "wins": wins,
            "losses": losses,
            "win_rate": wins / len(weekly_trades) * 100 if weekly_trades else 0,
            "avg_win": sum(t.net_pnl for t in weekly_trades if t.net_pnl > 0) / wins
            if wins > 0
            else 0,
            "avg_loss": sum(t.net_pnl for t in weekly_trades if t.net_pnl <= 0) / losses
            if losses > 0
            else 0,
            "best_trade": max((t.net_pnl for t in weekly_trades), default=0),
            "worst_trade": min((t.net_pnl for t in weekly_trades), default=0),
            "trades_detail": [t.to_dict() for t in weekly_trades],
        }

    def get_monthly_pnl(self, symbol: str = None) -> Dict:
        """Calculate monthly PnL from matched trades"""
        now = datetime.now()
        month_ago = now - timedelta(days=30)

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

        monthly_trades = [
            t for t in trades if t.closed_at and parse_timestamp(t.closed_at) >= month_ago
        ]

        total_pnl = sum(t.net_pnl for t in monthly_trades)
        wins = sum(1 for t in monthly_trades if t.net_pnl > 0)
        losses = sum(1 for t in monthly_trades if t.net_pnl <= 0)

        return {
            "pnl": total_pnl,
            "trades": len(monthly_trades),
            "wins": wins,
            "losses": losses,
            "win_rate": wins / len(monthly_trades) * 100 if monthly_trades else 0,
            "avg_win": sum(t.net_pnl for t in monthly_trades if t.net_pnl > 0) / wins
            if wins > 0
            else 0,
            "avg_loss": sum(t.net_pnl for t in monthly_trades if t.net_pnl <= 0) / losses
            if losses > 0
            else 0,
            "best_trade": max((t.net_pnl for t in monthly_trades), default=0),
            "worst_trade": min((t.net_pnl for t in monthly_trades), default=0),
            "trades_detail": [t.to_dict() for t in monthly_trades],
        }

    def get_all_time_pnl(self, symbol: str = None) -> Dict:
        """Calculate all-time PnL from matched trades"""
        if symbol:
            trades = [t for t in self._matched_trades if t.buy_trade.symbol == symbol]
        else:
            trades = self._matched_trades

        total_pnl = sum(t.net_pnl for t in trades)
        wins = sum(1 for t in trades if t.net_pnl > 0)
        losses = sum(1 for t in trades if t.net_pnl <= 0)

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
            "trades_detail": [t.to_dict() for t in trades],
        }

    def get_open_positions(self) -> List[Dict]:
        """Get current open positions (unmatched buys)"""
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
                open_positions.append(
                    {
                        "symbol": symbol,
                        "quantity": remaining_qty,
                        "avg_entry_price": avg_buy_price,
                        "total_cost": total_cost,
                    }
                )

        return open_positions

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


async def calculate_realized_pnl_from_fills(fills: List[Dict]) -> Dict:
    """Calculate realized PnL from a list of KuCoin fills"""
    trades = [Trade.from_kucoin_order(f) for f in fills]

    tracker = PnLTracker()
    tracker._trades = trades
    tracker.match_trades_fifo()

    return tracker.get_all_time_pnl()
