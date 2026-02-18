"""
KuCoin WebSocket Client
Real-time market data streaming for IBIS AGI Trader
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Callable
import websockets
from datetime import datetime

from .kucoin_client import KuCoinClient, Ticker, OrderBook, TradeOrder

# Configure logger
logger = logging.getLogger(__name__)


class KuCoinWebSocket:
    """KuCoin WebSocket client for real-time market data streaming"""

    TICKER_CHANNEL = "/market/ticker:{}"
    ORDERBOOK_CHANNEL = "/market/level2_20:{}"
    TRADE_CHANNEL = "/market/match:{}"

    def __init__(self, client: KuCoinClient):
        self.client = client
        self.running = False
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.subscriptions: Dict[str, List[Callable]] = {}
        self.price_cache: Dict[str, float] = {}
        self.orderbook_cache: Dict[str, OrderBook] = {}
        self.trade_cache: Dict[str, List[dict]] = {}
        self._connect_lock = asyncio.Lock()
        self.PUBLIC_WS_URL = (
            self.client.WS_URL_SANDBOX if self.client.sandbox else self.client.WS_URL_PROD
        )

    async def connect(self) -> bool:
        """Establish WebSocket connection with retry logic"""
        async with self._connect_lock:
            if self.running and self.websocket:
                return True

            max_retries = 3
            retry_delay = 2

            for attempt in range(max_retries):
                try:
                    logger.info("🔌 Establishing WebSocket connection...")
                    self.websocket = await websockets.connect(self.PUBLIC_WS_URL)
                    self.running = True
                    logger.info("✅ WebSocket connection established")

                    # Start listener task
                    asyncio.create_task(self._listen_loop())
                    return True

                except Exception as e:
                    logger.warning(f"❌ WebSocket connection attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        logger.info(f"⏳ Retrying in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        logger.warning("⚠️ WebSocket unavailable, will use REST API fallback")
                        return False

    async def _listen_loop(self):
        """Main WebSocket listening loop"""
        while self.running and self.websocket:
            try:
                message = await self.websocket.recv()
                await self._process_message(message)

            except websockets.exceptions.ConnectionClosed:
                logger.warning("🔌 WebSocket connection closed")
                self.running = False
                await self._reconnect()

            except Exception as e:
                logger.error(f"❌ WebSocket listen error: {e}")
                await asyncio.sleep(1)

    async def _reconnect(self):
        """Reconnect to WebSocket with backoff"""
        logger.info("🔄 Attempting to reconnect WebSocket...")
        await asyncio.sleep(5)

        success = await self.connect()
        if success:
            logger.info("✅ WebSocket reconnected successfully")
            # Re-subscribe to all channels
            await self._resubscribe()
        else:
            logger.error("❌ WebSocket reconnection failed")

    async def _resubscribe(self):
        """Re-subscribe to all previously subscribed channels"""
        for topic in list(self.subscriptions.keys()):
            try:
                await self._send_subscription(topic, True)
            except Exception as e:
                logger.error(f"❌ Failed to resubscribe to {topic}: {e}")

    async def subscribe(self, symbol: str, callback: Callable) -> bool:
        """Subscribe to ticker and orderbook channels for a symbol"""
        if not self.running:
            success = await self.connect()
            if not success:
                return False

        # Subscribe to ticker channel
        ticker_topic = self.TICKER_CHANNEL.format(symbol)
        if ticker_topic not in self.subscriptions:
            self.subscriptions[ticker_topic] = []
        if callback not in self.subscriptions[ticker_topic]:
            self.subscriptions[ticker_topic].append(callback)

        # Subscribe to orderbook channel
        orderbook_topic = self.ORDERBOOK_CHANNEL.format(symbol)
        if orderbook_topic not in self.subscriptions:
            self.subscriptions[orderbook_topic] = []
        if callback not in self.subscriptions[orderbook_topic]:
            self.subscriptions[orderbook_topic].append(callback)

        # Send subscription messages
        await self._send_subscription(ticker_topic)
        await self._send_subscription(orderbook_topic)

        logger.debug(f"✅ Subscribed to channels for {symbol}")
        return True

    async def unsubscribe(self, symbol: str, callback: Callable = None) -> bool:
        """Unsubscribe from channels for a symbol"""
        ticker_topic = self.TICKER_CHANNEL.format(symbol)
        orderbook_topic = self.ORDERBOOK_CHANNEL.format(symbol)

        for topic in [ticker_topic, orderbook_topic]:
            if topic in self.subscriptions:
                if callback:
                    if callback in self.subscriptions[topic]:
                        self.subscriptions[topic].remove(callback)
                    if not self.subscriptions[topic]:
                        await self._send_subscription(topic, is_unsubscribe=True)
                        del self.subscriptions[topic]
                else:
                    await self._send_subscription(topic, is_unsubscribe=True)
                    del self.subscriptions[topic]

        return True

    async def _send_subscription(self, topic: str, is_unsubscribe: bool = False):
        """Send subscription/unsubscription message"""
        if not self.running or not self.websocket:
            return

        try:
            message = {
                "id": f"{topic}_{int(time.time() * 1000)}",
                "type": "unsubscribe" if is_unsubscribe else "subscribe",
                "topic": topic,
                "privateChannel": False,
                "response": True,
            }

            await self.websocket.send(json.dumps(message))
            logger.debug(f"{'Un' if is_unsubscribe else ''}subscribed to {topic}")

        except Exception as e:
            logger.error(f"❌ Failed to {'un' if is_unsubscribe else ''}subscribe to {topic}: {e}")

    async def _process_message(self, raw_message: str):
        """Process incoming WebSocket messages"""
        try:
            data = json.loads(raw_message)

            if "topic" not in data:
                return

            topic = data["topic"]

            # Handle ticker updates
            if "/market/ticker" in topic:
                await self._process_ticker_update(topic, data)

            # Handle orderbook updates
            elif "/market/level2_20" in topic:
                await self._process_orderbook_update(topic, data)

            # Handle trade updates
            elif "/market/match" in topic:
                await self._process_trade_update(topic, data)

        except Exception as e:
            logger.error(f"❌ Error processing WebSocket message: {e}")

    async def _process_ticker_update(self, topic: str, data: dict):
        """Process ticker channel updates"""
        try:
            symbol = topic.split(":")[-1]
            ticker_data = data.get("data", {})

            # Update price cache
            price = float(ticker_data.get("price", 0))
            self.price_cache[symbol] = price

            # Call registered callbacks
            if topic in self.subscriptions:
                for callback in self.subscriptions[topic]:
                    try:
                        await callback("ticker", symbol, price)
                    except Exception as e:
                        logger.error(f"❌ Callback error for {topic}: {e}")

        except Exception as e:
            logger.error(f"❌ Error processing ticker update: {e}")

    async def _process_orderbook_update(self, topic: str, data: dict):
        """Process orderbook channel updates"""
        try:
            symbol = topic.split(":")[-1]
            orderbook_data = data.get("data", {})

            # Create OrderBook object from WebSocket data
            orderbook = OrderBook(
                symbol=symbol,
                bids=[[float(b[0]), float(b[1])] for b in orderbook_data.get("bids", [])],
                asks=[[float(a[0]), float(a[1])] for a in orderbook_data.get("asks", [])],
                timestamp=int(time.time() * 1000),
            )

            self.orderbook_cache[symbol] = orderbook

            # Call registered callbacks
            if topic in self.subscriptions:
                for callback in self.subscriptions[topic]:
                    try:
                        await callback("orderbook", symbol, orderbook)
                    except Exception as e:
                        logger.error(f"❌ Callback error for {topic}: {e}")

        except Exception as e:
            logger.error(f"❌ Error processing orderbook update: {e}")

    async def _process_trade_update(self, topic: str, data: dict):
        """Process trade channel updates"""
        try:
            symbol = topic.split(":")[-1]
            trade_data = data.get("data", {})

            if symbol not in self.trade_cache:
                self.trade_cache[symbol] = []

            self.trade_cache[symbol].append(
                {
                    "price": float(trade_data.get("price", 0)),
                    "size": float(trade_data.get("size", 0)),
                    "side": trade_data.get("side", ""),
                    "timestamp": int(time.time() * 1000),
                }
            )

            # Keep only last 100 trades
            if len(self.trade_cache[symbol]) > 100:
                self.trade_cache[symbol] = self.trade_cache[symbol][-100:]

            # Call registered callbacks
            if topic in self.subscriptions:
                for callback in self.subscriptions[topic]:
                    try:
                        await callback("trade", symbol, self.trade_cache[symbol][-1])
                    except Exception as e:
                        logger.error(f"❌ Callback error for {topic}: {e}")

        except Exception as e:
            logger.error(f"❌ Error processing trade update: {e}")

    def get_latest_price(self, symbol: str) -> float:
        """Get latest price from cache"""
        return self.price_cache.get(symbol, 0.0)

    def get_orderbook(self, symbol: str) -> Optional[OrderBook]:
        """Get latest orderbook from cache"""
        return self.orderbook_cache.get(symbol)

    def get_recent_trades(self, symbol: str, limit: int = 20) -> List[dict]:
        """Get recent trades from cache"""
        if symbol not in self.trade_cache:
            return []
        return self.trade_cache[symbol][-limit:]

    async def close(self):
        """Close WebSocket connection"""
        self.running = False
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception:
                pass
        logger.info("🔌 WebSocket connection closed")


class WebSocketDataFeed:
    """Data feed manager that uses WebSocket for real-time updates"""

    def __init__(self, client: KuCoinClient, update_interval: float = 1.0):
        self.client = client
        self.update_interval = update_interval
        self.ws = KuCoinWebSocket(client)
        self.running = False
        self._update_task: Optional[asyncio.Task] = None
        self._fallback_task: Optional[asyncio.Task] = None
        self._symbols: List[str] = []

        # Callbacks for data updates
        self._ticker_callback = lambda *args: asyncio.create_task(self._on_ticker_update(*args))
        self._orderbook_callback = lambda *args: asyncio.create_task(
            self._on_orderbook_update(*args)
        )

    async def start(self, symbols: List[str]):
        """Start data feed for specified symbols"""
        self.running = True
        self._symbols = symbols.copy()

        # Try to use WebSocket
        success = await self.ws.connect()
        if success:
            # Subscribe to each symbol
            for symbol in symbols:
                await self.ws.subscribe(symbol, self._ticker_callback)
                await self.ws.subscribe(symbol, self._orderbook_callback)
            logger.info(f"✅ WebSocket data feed started for {len(symbols)} symbols")
        else:
            logger.warning("⚠️ WebSocket unavailable, using REST API fallback")
            self._fallback_task = asyncio.create_task(self._rest_api_fallback_loop())

    async def _rest_api_fallback_loop(self):
        """Fallback to REST API polling if WebSocket fails"""
        while self.running:
            for symbol in self._symbols:
                try:
                    # Get ticker
                    ticker = await self.client.get_ticker(symbol)
                    self.ws.price_cache[symbol] = ticker.price

                    # Get orderbook
                    orderbook = await self.client.get_orderbook(symbol)
                    self.ws.orderbook_cache[symbol] = orderbook

                except Exception as e:
                    logger.error(f"❌ REST API fallback error for {symbol}: {e}")

            await asyncio.sleep(self.update_interval)

    async def stop(self):
        """Stop data feed"""
        self.running = False
        await self.ws.close()
        if self._fallback_task:
            self._fallback_task.cancel()
            try:
                await self._fallback_task
            except asyncio.CancelledError:
                pass
        logger.info("✅ WebSocket data feed stopped")

    async def _on_ticker_update(self, data_type: str, symbol: str, price: float):
        """Handle ticker updates"""
        logger.debug(f"Ticker update - {symbol}: ${price:.6f}")

    async def _on_orderbook_update(self, data_type: str, symbol: str, orderbook: OrderBook):
        """Handle orderbook updates"""
        logger.debug(
            f"Orderbook update - {symbol}: {len(orderbook.bids)} bids, {len(orderbook.asks)} asks"
        )

    async def get_latest_price(self, symbol: str) -> float:
        """Get latest price from WebSocket or fallback to REST API"""
        price = self.ws.get_latest_price(symbol)
        if price > 0:
            return price

        logger.warning(f"No WebSocket price for {symbol}, falling back to REST API")
        ticker = await self.client.get_ticker(symbol)
        return ticker.price

    async def get_orderbook(self, symbol: str) -> Optional[OrderBook]:
        """Get orderbook from WebSocket or fallback to REST API"""
        orderbook = self.ws.get_orderbook(symbol)
        if orderbook:
            return orderbook

        logger.warning(f"No WebSocket orderbook for {symbol}, falling back to REST API")
        return await self.client.get_orderbook(symbol)

    async def get_recent_trades(self, symbol: str, limit: int = 20) -> List[dict]:
        """Get recent trades from WebSocket"""
        return self.ws.get_recent_trades(symbol, limit)


# Global instance
_websocket_instance: Optional[KuCoinWebSocket] = None


def get_kucoin_websocket(client: KuCoinClient) -> KuCoinWebSocket:
    """Get or create WebSocket instance"""
    global _websocket_instance
    if _websocket_instance is None:
        _websocket_instance = KuCoinWebSocket(client)
    return _websocket_instance
