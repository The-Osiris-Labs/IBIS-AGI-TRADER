"""
IBIS CCXT Integration
Unified access to 100+ cryptocurrency exchanges
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from ibis.core.logging_config import get_logger

logger = get_logger(__name__)

try:
    import ccxt

    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False


@dataclass
class OHLCV:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class Ticker:
    symbol: str
    price: float
    change_24h: float
    volume_24h: float
    high_24h: float
    low_24h: float
    bid: float
    ask: float
    timestamp: int


class CCXTClient:
    """Unified exchange client using CCXT."""

    SUPPORTED_EXCHANGES = [
        "binance",
        "kucoin",
        "kraken",
        "okx",
        "bybit",
        "huobi",
        "gate",
        "mexc",
        "bitget",
        "coinbase",
    ]

    def __init__(
        self,
        exchange: str = "binance",
        api_key: str = "",
        api_secret: str = "",
        password: str = "",
        sandbox: bool = True,
        paper_trading: bool = True,
    ):
        self.exchange_name = exchange.lower()
        self.paper_trading = paper_trading
        self._exchange = None
        self._session = None

        if not CCXT_AVAILABLE:
            logger.warning("CCXT not installed. Install with: pip install ccxt")
            return

        if self.exchange_name not in self.SUPPORTED_EXCHANGES:
            logger.warning(f"Warning: {exchange} may not be fully tested")

        try:
            exchange_class = getattr(ccxt, self.exchange_name)

            config = {
                "enableRateLimit": True,
                "timeout": 30000,
            }

            if api_key and api_secret:
                config["apiKey"] = api_key
                config["secret"] = api_secret
                if password:
                    config["password"] = password

            self._exchange = exchange_class(config)

            if sandbox or paper_trading:
                if hasattr(self._exchange, "set_sandbox_mode"):
                    self._exchange.set_sandbox_mode(True)
        except Exception as e:
            logger.error(f"Failed to initialize {exchange}: {e}", exc_info=True)

    async def fetch_tickers(self, symbols: List[str] = None) -> Dict[str, Ticker]:
        """Fetch current market tickers."""
        if not CCXT_AVAILABLE or not self._exchange:
            return {}

        try:
            if hasattr(self._exchange, "fetch_tickers"):
                # Filter symbols to only those available on the exchange to avoid CCXT errors
                valid_symbols = symbols
                if symbols and hasattr(self._exchange, "load_markets"):
                    markets = await asyncio.to_thread(self._exchange.load_markets)
                    valid_symbols = [s for s in symbols if s in markets]

                if not valid_symbols and symbols:
                    return {}

                data = await asyncio.to_thread(self._exchange.fetch_tickers, valid_symbols)
                tickers = {}
                for symbol, ticker in data.items():
                    tickers[symbol] = Ticker(
                        symbol=symbol,
                        price=ticker.get("last", 0),
                        change_24h=ticker.get("percentage", 0),
                        volume_24h=ticker.get("quoteVolume", 0),
                        high_24h=ticker.get("high", 0),
                        low_24h=ticker.get("low", 0),
                        bid=ticker.get("bid", 0),
                        ask=ticker.get("ask", 0),
                        timestamp=int(ticker.get("timestamp", 0)),
                    )
                return tickers
        except Exception as e:
            logger.error(f"Error fetching tickers: {e}", exc_info=True)
        return {}

    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        since: int = None,
        limit: int = 500,
    ) -> List[OHLCV]:
        """Fetch OHLCV candles."""
        if not CCXT_AVAILABLE or not self._exchange:
            return []

        try:
            data = await asyncio.to_thread(
                self._exchange.fetch_ohlcv, symbol, timeframe, since, limit
            )
            return [
                OHLCV(
                    timestamp=c[0],
                    open=float(c[1]),
                    high=float(c[2]),
                    low=float(c[3]),
                    close=float(c[4]),
                    volume=float(c[5]),
                )
                for c in data
            ]
        except Exception as e:
            logger.error(f"Error fetching OHLCV: {e}", exc_info=True)
        return []

    async def fetch_orderbook(self, symbol: str, limit: int = 20) -> Dict:
        """Fetch order book."""
        if not CCXT_AVAILABLE or not self._exchange:
            return {}

        try:
            return await asyncio.to_thread(self._exchange.fetch_order_book, symbol, limit)
        except Exception as e:
            logger.error(f"Error fetching orderbook: {e}", exc_info=True)
        return {}

    async def fetch_balance(self) -> Dict:
        """Fetch account balance."""
        if not CCXT_AVAILABLE or not self._exchange:
            return {}

        try:
            return await asyncio.to_thread(self._exchange.fetch_balance)
        except Exception as e:
            logger.error(f"Error fetching balance: {e}", exc_info=True)
        return {}

    async def create_order(
        self,
        symbol: str,
        type: str,
        side: str,
        amount: float,
        price: float = None,
    ) -> Dict:
        """Create a trade order."""
        if not CCXT_AVAILABLE or not self._exchange:
            return {}

        try:
            order = {
                "symbol": symbol,
                "type": type,
                "side": side,
                "amount": amount,
            }
            if price:
                order["price"] = price

            return await asyncio.to_thread(self._exchange.create_order, **order)
        except Exception as e:
            logger.error(f"Error creating order: {e}", exc_info=True)
        return {}

    def get_exchange_name(self) -> str:
        return self.exchange_name

    def is_available(self) -> bool:
        return CCXT_AVAILABLE and self._exchange is not None

    def close(self):
        if self._exchange:
            try:
                self._exchange.close()
            except:
                pass


def get_ccxt_client(
    exchange: str = "binance",
    api_key: str = "",
    api_secret: str = "",
    sandbox: bool = True,
    paper_trading: bool = True,
) -> CCXTClient:
    """Factory function for CCXT client."""
    return CCXTClient(
        exchange=exchange,
        api_key=api_key,
        api_secret=api_secret,
        sandbox=sandbox,
        paper_trading=paper_trading,
    )
