"""
IBIS Trade Executor
Order management and trade execution
"""

import asyncio
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from ..exchange.kucoin_client import KuCoinClient, TradeOrder


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class TradeRequest:
    symbol: str
    side: OrderSide
    type: OrderType
    size: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    leverage: int = 1
    reduce_only: bool = False
    post_only: bool = False
    client_oid: Optional[str] = None
    callback: Optional[Callable] = None

    def validate(self) -> bool:
        if self.type in [OrderType.LIMIT, OrderType.STOP_LIMIT] and self.price is None:
            return False
        if (
            self.type in [OrderType.STOP, OrderType.STOP_LIMIT]
            and self.stop_price is None
        ):
            return False
        if self.size <= 0:
            return False
        if self.symbol.endswith("USDT") and self.side == OrderSide.SELL:
            return False
        return True


@dataclass
class TradeResult:
    order_id: str
    symbol: str
    side: str
    status: OrderStatus
    filled_size: float
    avg_price: float
    total_value: float
    commission: float
    timestamp: int
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "order_id": self.order_id,
            "symbol": self.symbol,
            "side": self.side,
            "status": self.status.value,
            "filled_size": self.filled_size,
            "avg_price": self.avg_price,
            "total_value": self.total_value,
            "commission": self.commission,
            "timestamp": self.timestamp,
            "error": self.error,
        }


@dataclass
class Position:
    symbol: str
    side: str
    size: float
    entry_price: float
    mark_price: float
    unrealized_pnl: float
    realized_pnl: float
    leverage: int
    timestamp: int

    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "side": self.side,
            "size": self.size,
            "entry_price": self.entry_price,
            "mark_price": self.mark_price,
            "unrealized_pnl": self.unrealized_pnl,
            "realized_pnl": self.realized_pnl,
            "leverage": self.leverage,
            "timestamp": self.timestamp,
        }


class TradeExecutor:
    def __init__(
        self,
        client: KuCoinClient,
        max_position_size: float = 0.1,
        max_order_size: float = 0.05,
        default_leverage: int = 1,
        commission_rate: float = 0.001,
    ):
        self.client = client
        self.max_position_size = max_position_size
        self.max_order_size = max_order_size
        self.default_leverage = default_leverage
        self.commission_rate = commission_rate

        self.active_orders: Dict[str, TradeRequest] = {}
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[TradeResult] = []
        self.order_callbacks: Dict[str, Callable] = {}

    async def execute(self, request: TradeRequest) -> TradeResult:
        if not request.validate():
            return TradeResult(
                order_id="",
                symbol=request.symbol,
                side=request.side.value,
                status=OrderStatus.REJECTED,
                filled_size=0,
                avg_price=0,
                total_value=0,
                commission=0,
                timestamp=int(time.time() * 1000),
                error="Invalid request parameters",
            )

        try:
            if request.type == OrderType.MARKET:
                return await self._execute_market(request)
            elif request.type == OrderType.LIMIT:
                return await self._execute_limit(request)
            elif request.type in [OrderType.STOP, OrderType.STOP_LIMIT]:
                return await self._execute_stop(request)
            else:
                return TradeResult(
                    order_id="",
                    symbol=request.symbol,
                    side=request.side.value,
                    status=OrderStatus.REJECTED,
                    filled_size=0,
                    avg_price=0,
                    total_value=0,
                    commission=0,
                    timestamp=int(time.time() * 1000),
                    error=f"Unsupported order type: {request.type}",
                )
        except Exception as e:
            return TradeResult(
                order_id="",
                symbol=request.symbol,
                side=request.side.value,
                status=OrderStatus.REJECTED,
                filled_size=0,
                avg_price=0,
                total_value=0,
                commission=0,
                timestamp=int(time.time() * 1000),
                error=str(e),
            )

    async def _execute_market(self, request: TradeRequest) -> TradeResult:
        ticker = await self.client.get_ticker(request.symbol)
        execution_price = ticker.price

        filled_size = min(request.size, self.max_order_size)

        if request.side == OrderSide.BUY:
            value = filled_size * execution_price
            commission = value * self.commission_rate
        else:
            value = filled_size * execution_price
            commission = value * self.commission_rate

        order_id = f"market_{int(time.time() * 1000)}"

        if request.client_oid:
            order_id = request.client_oid

        result = TradeResult(
            order_id=order_id,
            symbol=request.symbol,
            side=request.side.value,
            status=OrderStatus.FILLED,
            filled_size=filled_size,
            avg_price=execution_price,
            total_value=value,
            commission=commission,
            timestamp=int(time.time() * 1000),
        )

        self.trade_history.append(result)
        await self._update_position(request, result)

        if request.callback:
            asyncio.create_task(request.callback(result))

        return result

    async def _execute_limit(self, request: TradeRequest) -> TradeResult:
        price = request.price or 0

        if request.side == OrderSide.BUY and price > 0:
            value = request.size * price
            commission = value * self.commission_rate
        elif request.side == OrderSide.SELL and price > 0:
            value = request.size * price
            commission = value * self.commission_rate
        else:
            value = 0
            commission = 0

        order_id = f"limit_{int(time.time() * 1000)}"

        if request.client_oid:
            order_id = request.client_oid

        self.active_orders[order_id] = request

        partial_fill = request.size * 0.2
        filled_size = partial_fill
        filled_value = partial_fill * price
        commission = filled_value * self.commission_rate

        result = TradeResult(
            order_id=order_id,
            symbol=request.symbol,
            side=request.side.value,
            status=OrderStatus.PARTIAL
            if partial_fill < request.size
            else OrderStatus.FILLED,
            filled_size=filled_size,
            avg_price=price,
            total_value=filled_value,
            commission=commission,
            timestamp=int(time.time() * 1000),
        )

        if result.status == OrderStatus.FILLED:
            if order_id in self.active_orders:
                del self.active_orders[order_id]
            self.trade_history.append(result)
            await self._update_position(request, result)
        else:
            self.trade_history.append(result)

        if request.callback:
            asyncio.create_task(request.callback(result))

        return result

    async def _execute_stop(self, request: TradeRequest) -> TradeResult:
        stop_price = request.stop_price or request.price or 0

        order_id = f"stop_{int(time.time() * 1000)}"

        if request.client_oid:
            order_id = request.client_oid

        self.active_orders[order_id] = request

        result = TradeResult(
            order_id=order_id,
            symbol=request.symbol,
            side=request.side.value,
            status=OrderStatus.ACTIVE,
            filled_size=0,
            avg_price=0,
            total_value=0,
            commission=0,
            timestamp=int(time.time() * 1000),
        )

        self.trade_history.append(result)

        if request.callback:
            asyncio.create_task(request.callback(result))

        return result

    async def _update_position(self, request: TradeRequest, result: TradeResult):
        symbol = request.symbol
        base = symbol.replace("-USDT", "")

        if request.side == OrderSide.BUY:
            if symbol not in self.positions:
                self.positions[symbol] = Position(
                    symbol=symbol,
                    side="long",
                    size=result.filled_size,
                    entry_price=result.avg_price,
                    mark_price=result.avg_price,
                    unrealized_pnl=0,
                    realized_pnl=0,
                    leverage=request.leverage,
                    timestamp=result.timestamp,
                )
            else:
                pos = self.positions[symbol]
                total_size = pos.size + result.filled_size
                new_entry = (
                    pos.size * pos.entry_price + result.filled_size * result.avg_price
                ) / total_size
                pos.size = total_size
                pos.entry_price = new_entry
                pos.timestamp = result.timestamp
        else:
            if symbol in self.positions and self.positions[symbol].size > 0:
                pos = self.positions[symbol]
                pnl = (
                    (result.avg_price - pos.entry_price)
                    * result.filled_size
                    * pos.leverage
                )
                pos.realized_pnl += pnl
                pos.size -= result.filled_size
                pos.timestamp = result.timestamp

                if pos.size <= 0:
                    del self.positions[symbol]

    async def cancel_order(self, order_id: str) -> bool:
        if order_id in self.active_orders:
            del self.active_orders[order_id]
            return True
        return await self.client.cancel_order(order_id)

    async def cancel_all_orders(self, symbol: str = ""):
        for order_id in list(self.active_orders.keys()):
            if not symbol or self.active_orders[order_id].symbol == symbol:
                del self.active_orders[order_id]
        await self.client.cancel_all_orders(symbol)

    async def get_order_status(self, order_id: str) -> Optional[TradeResult]:
        for result in reversed(self.trade_history):
            if result.order_id == order_id:
                return result
        return None

    def get_positions(self) -> List[Position]:
        return list(self.positions.values())

    def get_trade_history(self, n: int = 50) -> List[TradeResult]:
        return self.trade_history[-n:]

    def get_pnl_summary(self) -> Dict:
        total_realized = sum(p.realized_pnl for p in self.positions.values())
        total_unrealized = sum(p.unrealized_pnl for p in self.positions.values())
        total_trades = len(self.trade_history)
        winning_trades = len(
            [t for t in self.trade_history if t.filled_size > 0 and t.avg_price > 0]
        )

        return {
            "total_realized_pnl": total_realized,
            "total_unrealized_pnl": total_unrealized,
            "total_pnl": total_realized + total_unrealized,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "win_rate": winning_trades / max(total_trades, 1),
        }


def get_trade_executor(
    client: KuCoinClient,
    max_position_size: float = 0.1,
    max_order_size: float = 0.05,
    default_leverage: int = 1,
    commission_rate: float = 0.001,
) -> TradeExecutor:
    return TradeExecutor(
        client,
        max_position_size,
        max_order_size,
        default_leverage,
        commission_rate,
    )
