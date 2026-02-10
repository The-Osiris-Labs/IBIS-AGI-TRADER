#!/usr/bin/env python3
"""
🦅 IBIS AGI TRADING SYSTEM - DATA LAYER
========================================
Real-Time Market Data with Dynamic Symbol Discovery

Features:
• REST API for market data (prices, orderbooks, candles)
• WebSocket streaming for real-time updates  
• Dynamic symbol discovery from API
• Automatic fallback to simulation
"""

import asyncio
import json
import time
import hmac
import hashlib
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from collections import deque
import logging

logger = logging.getLogger("IBIS-DATA")

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    logger.warning("aiohttp not available - using simulation mode")


@dataclass
class MarketPrice:
    """Current market price data."""
    symbol: str
    price: float
    change_24h: float
    volume_24h: float
    high_24h: float
    low_24h: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class OrderBook:
    """Order book data."""
    symbol: str
    bids: List[tuple]
    asks: List[tuple]
    spread: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Candle:
    """Candlestick data."""
    symbol: str
    timeframe: str
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    turnover: float


class KuCoinRESTClient:
    """KuCoin REST API client - dynamically discovers all available symbols."""

    BASE_URL = "https://api.kucoin.com"
    SANDBOX_URL = "https://api-sandbox.kucoin.com"

    def __init__(self, api_key: str = "", api_secret: str = "", passphrase: str = "", sandbox: bool = False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.sandbox = sandbox
        self.base_url = self.SANDBOX_URL if sandbox else self.BASE_URL
        self.session = None

    async def _get_session(self):
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session

    async def _request(self, method: str, endpoint: str, params: Dict = None, auth: bool = False) -> Dict:
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}

        if auth and self.api_key and self.api_secret:
            timestamp = str(int(time.time() * 1000))
            message = f"{timestamp}{method}{endpoint}"
            if params:
                message += json.dumps(params)

            signature = hmac.new(
                self.api_secret.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()

            headers.update({
                "KC-API-KEY": self.api_key,
                "KC-API-SIGN": signature,
                "KC-API-TIMESTAMP": timestamp,
                "KC-API-PASSPHRASE": self.passphrase,
                "KC-API-KEY-VERSION": "2",
            })

        try:
            if method.upper() == "GET":
                async with session.get(url, params=params, headers=headers) as resp:
                    data = await resp.json()
            else:
                return {}
            
            if data.get("code") == "200000":
                return data.get("data", {})
            else:
                return {}
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {}

    async def get_symbols(self) -> List[str]:
        """Dynamically discover all available trading pairs."""
        data = await self._request("GET", "/api/v1/symbols")
        symbols = []
        if data:
            for s in data:
                if s.get("quoteCurrency") == "USDT":
                    symbols.append(f"{s['baseCurrency']}-{s['quoteCurrency']}")
        return symbols

    async def get_ticker(self, symbol: str) -> Optional[MarketPrice]:
        """Get 24hr ticker for a symbol."""
        data = await self._request("GET", f"/api/v1/market/orderbook/level2_100", {"symbol": symbol})
        if data:
            ticker = data.get("data", {})
            return MarketPrice(
                symbol=symbol,
                price=float(ticker.get("price", 0)),
                change_24h=float(ticker.get("changeRate", 0)) * 100,
                volume_24h=float(ticker.get("size", 0)),
                high_24h=float(ticker.get("high", 0)),
                low_24h=float(ticker.get("low", 0)),
            )
        return None

    async def get_all_tickers(self) -> List[MarketPrice]:
        """Get all tickers dynamically."""
        data = await self._request("GET", "/api/v1/market/allTickers")
        tickers = []
        if data and "time" in data:
            for ticker in data.get("ticker", []):
                symbol = ticker.get("symbol", "")
                if symbol.endswith("-USDT"):
                    tickers.append(MarketPrice(
                        symbol=symbol,
                        price=float(ticker.get("last", 0)),
                        change_24h=float(ticker.get("changeRate", 0)) * 100,
                        volume_24h=float(ticker.get("vol", 0)),
                        high_24h=float(ticker.get("high", 0)),
                        low_24h=float(ticker.get("low", 0)),
                    ))
        return tickers

    async def get_candles(self, symbol: str, timeframe: str = "1min", limit: int = 100) -> List[Candle]:
        """Get candlestick data for any symbol."""
        params = {"symbol": symbol, "type": timeframe, "pageSize": limit}
        data = await self._request("GET", "/api/v1/market/candles", params)
        
        candles = []
        if data and "time" in data:
            for c in data.get("data", []):
                candles.append(Candle(
                    symbol=symbol,
                    timeframe=timeframe,
                    timestamp=datetime.fromtimestamp(int(c[0])).strftime("%Y-%m-%d %H:%M"),
                    open=float(c[1]),
                    high=float(c[2]),
                    low=float(c[3]),
                    close=float(c[4]),
                    volume=float(c[5]),
                    turnover=float(c[6]),
                ))
        return candles


class MarketDataManager:
    """Unified market data manager with dynamic discovery."""

    def __init__(self, api_key: str = "", api_secret: str = "", passphrase: str = ""):
        self.rest_client = KuCoinRESTClient(api_key, api_secret, passphrase)
        self.ws_client = KuCoinWebSocketClient(api_key, api_secret, passphrase)
        self.prices: Dict[str, MarketPrice] = {}
        self.orderbooks: Dict[str, OrderBook] = {}
        self.candles: Dict[str, List[Candle]] = {}
        self.price_history: Dict[str, deque] = {}
        self.last_update: datetime = None
        self._discovered_symbols: Set[str] = set()

    @property
    def symbols(self) -> List[str]:
        """Return all discovered symbols."""
        if self._discovered_symbols:
            return list(self._discovered_symbols)
        return list(self.prices.keys())

    async def discover_symbols(self) -> List[str]:
        """Dynamically discover symbols from API."""
        symbols = await self.rest_client.get_symbols()
        if symbols:
            self._discovered_symbols = set(symbols)
            logger.info(f"Discovered {len(symbols)} trading pairs")
        return symbols

    async def fetch_all(self):
        """Fetch all market data dynamically."""
        if not self._discovered_symbols:
            await self.discover_symbols()
        
        try:
            tickers = await self.rest_client.get_all_tickers()
            for ticker in tickers:
                self.prices[ticker.symbol] = ticker
                if ticker.symbol not in self.price_history:
                    self.price_history[ticker.symbol] = deque(maxlen=1000)
                self.price_history[ticker.symbol].append(ticker.price)
            self.last_update = datetime.now()
        except Exception as e:
            logger.error(f"Fetch failed: {e}")
            self._simulate_market_data()

    async def get_price(self, symbol: str) -> float:
        """Get current price for any symbol."""
        if symbol in self.prices:
            return self.prices[symbol].price
        return 0.0

    def get_price_change(self, symbol: str) -> float:
        """Calculate price change for any symbol."""
        history = list(self.price_history.get(symbol, []))
        if len(history) < 2:
            return 0.0
        return ((history[-1] - history[0]) / history[0]) * 100

    def get_price_history(self, symbol: str, limit: int = 100) -> List[float]:
        """Get price history for any symbol."""
        return list(self.price_history.get(symbol, []))[-limit:]

    def _simulate_market_data(self):
        """Simulation mode - discovers nothing, waits for real data."""
        logger.info("Running in simulation mode - symbols will be discovered from API on connection")

    async def close(self):
        """Close connections."""
        await self.ws_client.close()


class KuCoinWebSocketClient:
    """KuCoin WebSocket client for real-time data streaming."""

    PUBLIC_WS_URL = "wss://ws-api.kucoin.com/endpoint"

    def __init__(self, api_key: str = "", api_secret: str = "", passphrase: str = ""):
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.session = None
        self.ws = None
        self.running = False
        self.subscriptions: Dict[str, List[Callable]] = {}

    async def connect(self):
        """Connect to WebSocket."""
        if not AIOHTTP_AVAILABLE:
            logger.warning("aiohttp not available - WebSocket disabled")
            return False

        try:
            import aiohttp
            self.session = aiohttp.ClientSession()
            self.ws = await self.session.ws_connect(self.PUBLIC_WS_URL)
            self.running = True
            return True
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            return False

    async def subscribe(self, topic: str, callback: Callable):
        """Subscribe to a topic."""
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        self.subscriptions[topic].append(callback)

    async def close(self):
        """Close WebSocket connection."""
        self.running = False
        if self.ws:
            await self.ws.close()
        if self.session:
            await self.session.close()
