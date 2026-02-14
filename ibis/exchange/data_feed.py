"""
IBIS Data Feed Manager
Real-time market data streaming and buffering
"""

import asyncio
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
from ..exchange.kucoin_client import KuCoinClient, Ticker, Candle, OrderBook


@dataclass
class MarketSnapshot:
    symbol: str
    timestamp: int
    price: float
    price_change: float
    volume: float
    volatility: float
    bid_ask_spread: float
    bid_volume: float
    ask_volume: float
    order_imbalance: float
    vwap: float

    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "price": self.price,
            "price_change": self.price_change,
            "volume": self.volume,
            "volatility": self.volatility,
            "bid_ask_spread": self.bid_ask_spread,
            "bid_volume": self.bid_volume,
            "ask_volume": self.ask_volume,
            "order_imbalance": self.order_imbalance,
            "vwap": self.vwap,
        }


@dataclass
class DataBuffer:
    symbol: str
    max_size: int = 100
    tickers: deque = field(default_factory=deque)
    candles: deque = field(default_factory=deque)
    orderbooks: deque = field(default_factory=deque)

    def add_ticker(self, ticker: Ticker):
        while len(self.tickers) >= self.max_size:
            self.tickers.popleft()
        self.tickers.append(ticker)

    def add_candle(self, candle: Candle):
        while len(self.candles) >= self.max_size:
            self.candles.popleft()
        self.candles.append(candle)

    def add_orderbook(self, orderbook: OrderBook):
        while len(self.orderbooks) >= self.max_size:
            self.orderbooks.popleft()
        self.orderbooks.append(orderbook)

    def get_recent_tickers(self, n: int = 10) -> List[Ticker]:
        return list(self.tickers)[-n:]

    def get_recent_candles(self, n: int = 50) -> List[Candle]:
        return list(self.candles)[-n:]

    def calculate_trend(self, n: int = 10) -> float:
        tickers = list(self.tickers)[-n:]
        if len(tickers) < 2:
            return 0
        prices = [t.price for t in tickers]
        return (prices[-1] - prices[0]) / prices[0] * 100

    def calculate_volatility(self, n: int = 10) -> float:
        tickers = list(self.tickers)[-n:]
        if len(tickers) < 2:
            return 0
        prices = [t.price for t in tickers]
        returns = [(prices[i] - prices[i - 1]) / prices[i - 1] for i in range(1, len(prices))]
        return sum(abs(r) for r in returns) / len(returns) * 100


class DataFeed:
    def __init__(
        self,
        client: KuCoinClient,
        symbols: List[str] = None,
        update_interval: float = 1.0,
    ):
        self.client = client
        self.symbols = symbols or []
        self.update_interval = update_interval
        self.buffers: Dict[str, DataBuffer] = {}
        self.running = False
        self._tasks: List[asyncio.Task] = []

        for symbol in self.symbols:
            self.buffers[symbol] = DataBuffer(symbol)

    async def start(self):
        self.running = True
        for symbol in self.symbols:
            task = asyncio.create_task(self._update_loop(symbol))
            self._tasks.append(task)

    async def stop(self):
        self.running = False
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()

    async def _update_loop(self, symbol: str):
        while self.running:
            try:
                ticker = await self.client.get_ticker(symbol)
                orderbook = await self.client.get_orderbook(symbol)

                self.buffers[symbol].add_ticker(ticker)
                self.buffers[symbol].add_orderbook(orderbook)

                await asyncio.sleep(self.update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Data feed error for {symbol}: {e}")
                await asyncio.sleep(1)

    async def get_snapshot(self, symbol: str) -> Optional[MarketSnapshot]:
        if symbol not in self.buffers:
            return None

        buffer = self.buffers[symbol]
        tickers = list(buffer.tickers)

        if not tickers:
            return None

        latest = tickers[-1]
        orderbook = buffer.orderbooks[-1] if buffer.orderbooks else None

        bid_volume = sum(b[1] for b in (orderbook.bids if orderbook else [])[:5])
        ask_volume = sum(a[1] for a in (orderbook.asks if orderbook else [])[:5])
        spread = 0
        if orderbook and orderbook.bids and orderbook.asks:
            spread = float(orderbook.asks[0][0]) - float(orderbook.bids[0][0])

        return MarketSnapshot(
            symbol=symbol,
            timestamp=latest.timestamp,
            price=latest.price,
            price_change=latest.change_24h,
            volume=latest.volume_24h,
            volatility=buffer.calculate_volatility(10),
            bid_ask_spread=spread,
            bid_volume=bid_volume,
            ask_volume=ask_volume,
            order_imbalance=(bid_volume - ask_volume) / (bid_volume + ask_volume + 0.001),
            vwap=latest.price * 1.001,
        )

    def get_ohlcv(self, symbol: str, n: int = 50) -> List[Dict]:
        if symbol not in self.buffers:
            return []

        candles = list(self.buffers[symbol].candles)[-n:]
        return [
            {
                "timestamp": c.timestamp,
                "open": c.open,
                "high": c.high,
                "low": c.low,
                "close": c.close,
                "volume": c.volume,
            }
            for c in candles
        ]

    async def wait_for_candles(self, symbol: str, count: int = 10, timeout: float = 30.0) -> bool:
        start_time = time.time()
        while len(self.buffers[symbol].candles) < count:
            if time.time() - start_time > timeout:
                return False
            await asyncio.sleep(0.5)
        return True


def get_data_feed(
    client: KuCoinClient,
    symbols: List[str] = None,
    update_interval: float = 1.0,
) -> DataFeed:
    return DataFeed(client, symbols, update_interval)
