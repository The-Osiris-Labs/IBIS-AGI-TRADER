"""
KuCoin API Client for IBIS
Real-time market data and trading capabilities
"""

import asyncio
import hashlib
import hmac
import json
import time
import websockets
import os
import base64
from pathlib import Path
from typing import Optional, Dict, List, Callable, Any
from dataclasses import dataclass
from enum import Enum
import aiohttp
import socket
from aiohttp.resolver import DefaultResolver
from aiohttp.abc import AbstractResolver

try:
    from dotenv import load_dotenv

    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


def load_env():
    """Load environment variables from keys.env or .env"""
    env_path = Path(__file__).parent.parent / "keys.env"

    if env_path.exists():
        if DOTENV_AVAILABLE:
            load_dotenv(env_path, override=True)
            print(f"Loaded env from: {env_path}")
        else:
            with open(env_path) as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, val = line.strip().split("=", 1)
                        os.environ[key] = val


load_env()

_KUCOIN_API_KEY = os.environ.get("KUCOIN_API_KEY", "")
_KUCOIN_API_SECRET = os.environ.get("KUCOIN_API_SECRET", "")
_KUCOIN_API_PASSPHRASE = os.environ.get("KUCOIN_API_PASSPHRASE", "")
_KUCOIN_IS_SANDBOX = os.environ.get("KUCOIN_IS_SANDBOX", "false").lower() == "true"
_PAPER_TRADING = os.environ.get("PAPER_TRADING", "false").lower() == "true"
_KUCOIN_DNS = os.environ.get("KUCOIN_DNS", "").strip()
_KUCOIN_API_HOST = os.environ.get("KUCOIN_API_HOST", "api.kucoin.com").strip()
_KUCOIN_API_IP = os.environ.get("KUCOIN_API_IP", "").strip()


class EnvConfig:
    KUCOIN_API_KEY = _KUCOIN_API_KEY
    KUCOIN_API_SECRET = _KUCOIN_API_SECRET
    KUCOIN_API_PASSPHRASE = _KUCOIN_API_PASSPHRASE
    KUCOIN_IS_SANDBOX = _KUCOIN_IS_SANDBOX
    PAPER_TRADING = _PAPER_TRADING
    KUCOIN_DNS = _KUCOIN_DNS
    KUCOIN_API_HOST = _KUCOIN_API_HOST
    KUCOIN_API_IP = _KUCOIN_API_IP


class StaticResolver(AbstractResolver):
    """Resolver that maps specific hosts to fixed IPs."""

    def __init__(self, mapping: Dict[str, str]):
        self.mapping = mapping
        self._fallback = DefaultResolver()

    async def resolve(self, host: str, port: int = 0, family: int = socket.AF_INET):
        ip = self.mapping.get(host)
        if ip:
            return [
                {
                    "hostname": host,
                    "host": ip,
                    "port": port,
                    "family": family,
                    "proto": 0,
                    "flags": 0,
                }
            ]
        return await self._fallback.resolve(host, port=port, family=family)

    async def close(self):
        await self._fallback.close()


DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=30, connect=10, sock_read=15, sock_connect=15)
MAX_RETRIES = 3
RETRY_DELAY = 1.0


@dataclass
class Ticker:
    symbol: str = ""
    price: float = 0.0
    change_24h: float = 0.0
    change_percent_24h: float = 0.0
    volume_24h: float = 0.0
    high_24h: float = 0.0
    low_24h: float = 0.0
    buy: float = 0.0  # Bid
    sell: float = 0.0  # Ask
    timestamp: int = 0

    @classmethod
    def from_response(cls, data: Dict, symbol: str) -> "Ticker":
        ticker = data.get("ticker", {})

        def _f(val):
            try:
                return float(val)
            except Exception:
                return 0.0

        price = _f(ticker.get("last", ticker.get("price", 0)))
        return cls(
            symbol=symbol,
            price=price,
            change_24h=_f(ticker.get("changeRate", 0)) * 100,
            change_percent_24h=_f(ticker.get("changePrice", 0)),
            volume_24h=_f(ticker.get("vol", 0)),
            high_24h=_f(ticker.get("high", 0)),
            low_24h=_f(ticker.get("low", 0)),
            buy=_f(ticker.get("buy", ticker.get("bestBid", 0))),
            sell=_f(ticker.get("sell", ticker.get("bestAsk", 0))),
            timestamp=int(ticker.get("time", 0) or 0),
        )


@dataclass
class Candle:
    symbol: str
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    turnover: float

    @classmethod
    def from_kline(cls, kline: List, symbol: str) -> "Candle":
        return cls(
            symbol=symbol,
            timestamp=int(kline[0]),
            open=float(kline[1]),
            high=float(kline[2]),
            low=float(kline[3]),
            close=float(kline[4]),
            volume=float(kline[5]),
            turnover=float(kline[7]) if len(kline) > 7 else 0,
        )


@dataclass
class OrderBook:
    symbol: str
    bids: List[tuple]
    asks: List[tuple]
    timestamp: int

    @classmethod
    def from_response(cls, data: Dict, symbol: str) -> "OrderBook":
        return cls(
            symbol=symbol,
            bids=[[float(b[0]), float(b[1])] for b in data.get("bids", [])],
            asks=[[float(a[0]), float(a[1])] for a in data.get("asks", [])],
            timestamp=int(data.get("time", 0)),
        )


@dataclass
class TradeOrder:
    order_id: str
    symbol: str
    side: str
    type: str
    price: float
    size: float
    status: str
    filled_size: float
    avg_price: float
    created_at: int
    fee: float = 0.0  # Actual fee from KuCoin (in quote currency)
    fee_currency: str = "USDT"  # Fee currency (usually quote currency)

    @classmethod
    def from_response(cls, data: Dict, symbol: str) -> "TradeOrder":
        raw_fee = data.get("fee", "0")
        if isinstance(raw_fee, str):
            try:
                fee = abs(float(raw_fee))
            except (ValueError, TypeError):
                fee = 0.0
        else:
            fee = abs(float(raw_fee)) if raw_fee else 0.0

        filled_size_str = data.get("filledSize", "0")
        if isinstance(filled_size_str, str):
            try:
                filled_size = float(filled_size_str)
            except (ValueError, TypeError):
                filled_size = 0.0
        else:
            filled_size = float(filled_size_str) if filled_size_str else 0.0

        deal_size_str = data.get("dealSize", "0")
        if isinstance(deal_size_str, str):
            try:
                deal_size = float(deal_size_str)
            except (ValueError, TypeError):
                deal_size = 0.0
        else:
            deal_size = float(deal_size_str) if deal_size_str else 0.0

        avg_price = deal_size / max(filled_size, 0.001) if filled_size > 0 else 0.0

        return cls(
            order_id=data.get("orderId", ""),
            symbol=symbol,
            side=data.get("side", ""),
            type=data.get("type", ""),
            price=float(data.get("price", 0)) if data.get("price") else 0.0,
            size=float(data.get("size", 0)) if data.get("size") else 0.0,
            status=data.get("status", ""),
            filled_size=filled_size,
            avg_price=avg_price,
            created_at=int(data.get("createdAt", 0)),
            fee=fee,
            fee_currency=data.get("feeCurrency", "USDT"),
        )


class KuCoinClient:
    BASE_URL_SANDBOX = "https://api-sandbox.kucoin.com"
    BASE_URL_PROD = "https://api.kucoin.com"
    WS_URL_SANDBOX = "wss://ws-sandbox.kucoin.com"
    WS_URL_PROD = "wss://ws.kucoin.com"

    def __init__(
        self,
        api_key: str = "",
        api_secret: str = "",
        api_passphrase: str = "",
        sandbox: bool = False,
        paper_trading: bool = False,
    ):
        self.api_key = api_key or EnvConfig.KUCOIN_API_KEY
        self.api_secret = api_secret or EnvConfig.KUCOIN_API_SECRET
        self.api_passphrase = api_passphrase or EnvConfig.KUCOIN_API_PASSPHRASE
        self.sandbox = sandbox or EnvConfig.KUCOIN_IS_SANDBOX
        self.paper_trading = paper_trading or EnvConfig.PAPER_TRADING
        self.dns_servers = []
        if EnvConfig.KUCOIN_DNS:
            self.dns_servers = [s.strip() for s in EnvConfig.KUCOIN_DNS.split(",") if s.strip()]
        self.api_host = EnvConfig.KUCOIN_API_HOST or "api.kucoin.com"
        self.api_ip = EnvConfig.KUCOIN_API_IP

        self.base_url = self.BASE_URL_SANDBOX if self.sandbox else self.BASE_URL_PROD
        self.ws_url = self.WS_URL_SANDBOX if self.sandbox else self.WS_URL_PROD

        self._session: Optional[aiohttp.ClientSession] = None
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._subscriptions: Dict[str, Callable] = {}
        self._running = False

        self._tickers: Dict[str, Ticker] = {}
        self._orderbooks: Dict[str, OrderBook] = {}
        self._candles: Dict[str, List[Candle]] = {}

        # Always initialize paper trading attributes
        self._paper_orders: Dict[str, TradeOrder] = {}
        self._paper_balance: Dict[str, float] = {"USDT": 10000, "BTC": 0, "ETH": 0}

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            resolver = None
            if self.api_ip:
                resolver = StaticResolver({self.api_host: self.api_ip})
            elif self.dns_servers:
                # Prefer custom DNS via system resolver fallback if available
                resolver = StaticResolver({})
            if resolver:
                connector = aiohttp.TCPConnector(resolver=resolver, family=socket.AF_INET)
                self._session = aiohttp.ClientSession(timeout=DEFAULT_TIMEOUT, connector=connector)
            else:
                self._session = aiohttp.ClientSession(timeout=DEFAULT_TIMEOUT)
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    def _sign(self, method: str, path: str, query: str = "", body: str = "") -> Dict[str, str]:
        timestamp = str(int(time.time() * 1000))

        if "?" in path:
            endpoint, existing_query = path.split("?", 1)
            if query:
                request_path = f"{endpoint}?{query}"
            else:
                request_path = path
        else:
            endpoint = path
            request_path = endpoint + (f"?{query}" if query else "")

        if method == "GET":
            message = f"{timestamp}{method}{request_path}{body}"
        else:
            message = f"{timestamp}{method}{request_path}{body}"

        signature = base64.b64encode(
            hmac.new(
                self.api_secret.encode("utf-8"),
                message.encode("utf-8"),
                hashlib.sha256,
            ).digest()
        ).decode("utf-8")

        passphrase = base64.b64encode(
            hmac.new(
                self.api_secret.encode("utf-8"),
                self.api_passphrase.encode("utf-8"),
                hashlib.sha256,
            ).digest()
        ).decode("utf-8")

        return {
            "KC-API-SIGN": signature,
            "KC-API-TIMESTAMP": timestamp,
            "KC-API-KEY": self.api_key,
            "KC-API-PASSPHRASE": passphrase,
            "KC-API-KEY-VERSION": "2",
            "Content-Type": "application/json",
        }

    async def _request_with_retry(
        self, method: str, path: str, query: str = "", body: str = ""
    ) -> Dict:
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                return await self._request(method, path, query, body)
            except asyncio.TimeoutError as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_DELAY * (2**attempt)
                    print(f"Timeout on attempt {attempt + 1}, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
            except Exception as e:
                last_error = e
                error_str = str(e)
                # If it's an auth error, don't retry - credentials are wrong
                if "400005" in error_str or "Invalid" in error_str:
                    print(f"⚠️ Authentication error - check API credentials: {e}")
                    # Return empty data instead of crashing
                    if "orders" in path:
                        return {"items": []}
                    return {}
                if attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_DELAY * (2**attempt)
                    if attempt == 0:
                        print(f"⚠️ Rate limit, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
        raise Exception(f"Max retries exceeded: {last_error}")

    async def _request(self, method: str, path: str, query: str = "", body: str = "") -> Dict:
        session = await self._get_session()
        headers = {}

        if self.api_key and self.api_secret:
            if "?" in path:
                endpoint, path_query = path.split("?", 1)
                if query:
                    full_query = f"{path_query}&{query}"
                else:
                    full_query = path_query
            else:
                endpoint = path
                full_query = query
            headers = self._sign(method, endpoint, full_query, body)

        url = f"{self.base_url}{path}"
        if query:
            url += f"?{query}"

        async with session.request(
            method, url, headers=headers, data=body.encode() if body else None
        ) as resp:
            data = await resp.json()
            if data.get("code") != "200000":
                raise Exception(f"KuCoin API Error: {data}")
            return data.get("data", {})

    async def get_symbols(self) -> List[Dict]:
        return await self._request_with_retry("GET", "/api/v2/symbols")

    async def get_symbol(self, symbol: str) -> Optional[Dict]:
        return await self._request_with_retry("GET", f"/api/v2/symbols/{symbol}")

    async def get_accounts(self) -> List[Dict]:
        return await self._request_with_retry("GET", "/api/v1/accounts")

    async def get_account(self, currency: str) -> Optional[Dict]:
        accounts = await self._request_with_retry("GET", f"/api/v1/accounts?currency={currency}")
        return accounts[0] if accounts else None

    async def get_balance(self, currency: str) -> float:
        account = await self.get_account(currency)
        if account:
            return float(account.get("available", 0))
        return 0.0

    async def get_all_balances(
        self, account_type_filter="trade", min_value_usd=0.10
    ) -> Dict[str, Dict[str, float]]:
        """Get balances, optionally filtered by account type and minimum USD value.

        Args:
            account_type_filter: 'trade' for Trading Account (Spot), 'main' for Main Account,
                               None for all accounts
            min_value_usd: Minimum USD value to include (default $0.10 to filter dust)
        """
        balances = {}
        accounts = await self.get_accounts()

        # Optimization: Fetch all tickers once if filtering by USD value
        tickers_map = {}
        if min_value_usd > 0:
            all_tickers = await self.get_tickers()
            tickers_map = {t.symbol: t.price for t in all_tickers}

        for acc in accounts:
            currency = acc.get("currency", "")
            acc_type = acc.get("type", "")
            available = float(acc.get("available", 0))
            balance = float(acc.get("balance", 0))

            # Filter by account type if specified
            if account_type_filter and acc_type != account_type_filter:
                continue

            if available > 0 or balance > 0:
                # Calculate USD value for dust filtering (except USDT which is always included)
                if currency != "USDT" and min_value_usd > 0:
                    symbol = f"{currency}-USDT"
                    price = tickers_map.get(symbol, 0)

                    # Skip if we have no price or below minimum value (dust)
                    if price <= 0 or (balance * price) < min_value_usd:
                        continue

                if currency not in balances:
                    balances[currency] = {
                        "available": available,
                        "balance": balance,
                        "type": acc_type,
                    }
                else:
                    # If currency already exists, sum balances from both accounts
                    existing = balances[currency]
                    existing["available"] += available
                    existing["balance"] += balance
                    # Keep track of both account types
                    if acc_type != existing["type"]:
                        existing["type"] = "both"

        return balances

    async def get_basic_orders(self, symbol: str = "", status: str = "active") -> List[Dict]:
        """Get basic spot orders (limit, market)"""
        params = []
        if symbol:
            params.append(f"symbol={symbol}")
        if status:
            params.append(f"status={status}")

        query = "&".join(params)

        try:
            data = await self._request_with_retry("GET", "/api/v1/orders", query)
            orders = data.get("items", []) if data else []

            # For active status, we get only active orders from API
            if status == "active":
                return orders

            return orders

        except Exception as e:
            print(f"Warning: Could not fetch basic orders: {e}")
            return []

    async def get_advanced_orders(self, symbol: str = "") -> List[Dict]:
        """Get advanced orders (stop limit, take profit, trailing stop)"""
        try:
            data = await self._request_with_retry("GET", "/api/v1/stop-order")
            return data.get("items", []) if data else []
        except Exception as e:
            print(f"Warning: Could not fetch advanced orders: {e}")
            return []

    async def get_twap_orders(self, symbol: str = "") -> List[Dict]:
        """Get TWAP (time-weighted average price) orders"""
        return []  # TWAP endpoint returns 404 on KuCoin

    async def get_all_orders(self, symbol: str = "") -> Dict[str, List[Dict]]:
        """Get all order types in a structured format"""
        [basic, advanced, twap] = await asyncio.gather(
            self.get_basic_orders(symbol),
            self.get_advanced_orders(symbol),
            self.get_twap_orders(symbol),
        )

        return {"basic": basic, "advanced": advanced, "twap": twap}

    async def get_open_orders(
        self, symbol: str = "", trade_type: str = "TRADE", status: str = "active"
    ) -> List[Dict]:
        """
        Get open orders for spot trading (compatibility method)

        Parameters:
            symbol: Specific symbol to filter (e.g., "BTC-USDT")
            trade_type: Trading type - TRADE (spot), MARGIN_TRADE (margin), etc.
            status: Order status filter - 'active' for currently active orders
        Returns:
            List of open orders with detailed information
        """
        return await self.get_basic_orders(symbol, status)

    async def get_recent_fills(self, limit: int = 50) -> List[Dict]:
        try:
            data = await self._request("GET", "/api/v1/orders")
            items = data.get("items", []) if data else []
            filled_orders = [
                o for o in items if o.get("isActive") == False and o.get("dealSize", "0") != "0"
            ]

            # Enhanced order details with price and fee information
            enhanced_orders = []
            for order in filled_orders:
                enhanced_order = order.copy()
                try:
                    # Extract price from order
                    if "price" in order and order["price"] and order["price"] != "0":
                        # Handle string prices that need conversion
                        if isinstance(order["price"], str):
                            enhanced_order["price"] = float(order["price"])
                        else:
                            enhanced_order["price"] = order["price"]
                    else:
                        # Fallback to calculating from dealSize and dealFunds
                        deal_size = float(order.get("dealSize", 0))
                        deal_funds = float(order.get("dealFunds", 0))
                        if deal_size > 0:
                            enhanced_order["price"] = deal_funds / deal_size
                        else:
                            enhanced_order["price"] = 0.0

                    # Extract and validate actual fee from KuCoin response
                    # KuCoin returns fee in the 'fee' field (e.g., "0.0015" or "0.000001")
                    raw_fee = order.get("fee", "0")
                    deal_funds = float(order.get("dealFunds", 0))
                    deal_size_val = float(order.get("dealSize", 0))

                    # Calculate trade value for validation
                    trade_value = (
                        deal_funds if deal_funds > 0 else enhanced_order["price"] * deal_size_val
                    )

                    # Parse fee - handle string or numeric values
                    if isinstance(raw_fee, str):
                        try:
                            actual_fee = abs(float(raw_fee))
                        except (ValueError, TypeError):
                            actual_fee = 0.0
                    else:
                        actual_fee = abs(float(raw_fee)) if raw_fee else 0.0

                    # Validate fee - KuCoin typically charges 0.1% (0.001) for makers and 0.1% for takers
                    # Acceptable range: 0.05% to 0.5% of trade value
                    max_acceptable_fee = trade_value * 0.005  # 0.5% max
                    min_acceptable_fee = trade_value * 0.0005  # 0.05% min

                    if actual_fee > max_acceptable_fee and trade_value > 0:
                        # Fee is suspiciously high - flag as anomaly
                        print(
                            f"⚠️ FEE ANOMALY DETECTED: {actual_fee:.6f} USDT on trade value {trade_value:.2f} USDT ({actual_fee / trade_value * 100:.2f}%)"
                        )
                        print(f"   Order ID: {order.get('orderId', 'unknown')}")
                        # Cap fee at reasonable maximum for calculation purposes
                        enhanced_order["fee"] = max_acceptable_fee
                        enhanced_order["fee_anomaly"] = True
                    elif actual_fee < min_acceptable_fee and actual_fee > 0 and trade_value > 0:
                        # Fee is suspiciously low
                        enhanced_order["fee"] = actual_fee
                        enhanced_order["fee_anomaly"] = False
                    else:
                        enhanced_order["fee"] = actual_fee
                        enhanced_order["fee_anomaly"] = False

                    # Store calculated fee rate for reference
                    if trade_value > 0:
                        enhanced_order["fee_rate"] = enhanced_order["fee"] / trade_value
                    else:
                        enhanced_order["fee_rate"] = 0.001  # Default 0.1%

                except Exception as e:
                    print(f"Error processing order {order.get('orderId', 'unknown')}: {e}")
                    enhanced_order["price"] = 0.0
                    enhanced_order["fee"] = 0.0
                    enhanced_order["fee_anomaly"] = False
                    enhanced_order["fee_rate"] = 0.001

                enhanced_orders.append(enhanced_order)

            return enhanced_orders[:limit]

        except Exception as e:
            print(f"Warning: Could not fetch fills: {e}")
            return []

    async def get_order_details(self, order_id: str) -> Optional[Dict]:
        return await self._request_with_retry("GET", f"/api/v1/orders/{order_id}")

    async def get_ticker(self, symbol: str) -> Ticker:
        data = await self._request_with_retry(
            "GET", f"/api/v1/market/orderbook/level1?symbol={symbol}"
        )
        ticker_data = {"ticker": data} if "price" in data else data
        ticker = Ticker.from_response(ticker_data, symbol)
        self._tickers[symbol] = ticker
        return ticker

    async def get_tickers(self) -> List[Ticker]:
        data = await self._request_with_retry("GET", "/api/v1/market/allTickers")
        tickers = []
        for t in data.get("ticker", []):
            symbol = t.get("symbol", "")
            if symbol.endswith("USDT"):
                ticker = Ticker.from_response({"ticker": t}, symbol)
                tickers.append(ticker)
                self._tickers[symbol] = ticker
        return tickers

    async def get_24h_stats(self, symbol: str) -> Dict:
        """Get 24h stats for a symbol."""
        return await self._request_with_retry("GET", f"/api/v1/market/stats?symbol={symbol}")

    async def get_candles(
        self,
        symbol: str,
        candle_type: str = "1min",
        limit: int = None,
        start: int = None,
        end: int = None,
    ) -> List[Candle]:
        params = f"symbol={symbol}&type={candle_type}"
        if start:
            params += f"&startAt={start}"
        if end:
            params += f"&endAt={end}"

        data = await self._request_with_retry("GET", f"/api/v1/market/candles?{params}")
        candles = [Candle.from_kline(k, symbol) for k in data]
        candles.reverse()
        if limit and len(candles) > limit:
            candles = candles[-limit:]
        self._candles[symbol] = candles
        return candles

    async def get_orderbook(self, symbol: str, limit: int = 20) -> OrderBook:
        # Map limit to KuCoin's available levels: 20, 50, 100
        depth = 20
        if limit >= 100:
            depth = 100
        elif limit >= 50:
            depth = 50

        data = await self._request_with_retry(
            "GET", f"/api/v1/market/orderbook/level2_{depth}?symbol={symbol}"
        )
        orderbook = OrderBook.from_response(data, symbol)
        self._orderbooks[symbol] = orderbook
        return orderbook

    async def create_order(
        self,
        symbol: str,
        side: str,
        type: str,
        price: float,
        size: float,
    ) -> TradeOrder:
        order_data = {
            "clientOid": f"ibis_{int(time.time() * 1000)}",
            "symbol": symbol,
            "side": side,
            "type": type,
        }

        # Market Buy orders on KuCoin use 'funds' (USD value)
        # Market Sell orders use 'size' (Base quantity)
        if type.lower() == "market":
            if side.lower() == "buy":
                order_data["funds"] = str(size)
            else:
                order_data["size"] = str(size)
        else:
            order_data["size"] = str(size)
            if type.lower() == "limit":
                order_data["price"] = str(price)

        if self.paper_trading:
            return await self._paper_create_order(order_data)
        else:
            return await self._live_create_order(order_data)

    async def create_market_order(self, symbol: str, side: str, size: float) -> TradeOrder:
        """Alias for engine compatibility."""
        return await self.create_order(symbol, side, "market", 0, size)

    async def create_limit_order(
        self, symbol: str, side: str, price: float, size: float
    ) -> TradeOrder:
        """Alias for engine compatibility."""
        return await self.create_order(symbol, side, "limit", price, size)

    async def place_market_order(self, symbol: str, side: str, size: float) -> TradeOrder:
        """Place a market order."""
        return await self.create_order(symbol, side, "market", 0, size)

    async def place_limit_order(
        self, symbol: str, side: str, price: float, size: float
    ) -> TradeOrder:
        """Place a limit order."""
        return await self.create_order(symbol, side, "limit", price, size)

    async def _paper_create_order(self, order_data: Dict) -> TradeOrder:
        order_id = f"paper_{int(time.time() * 1000)}"
        symbol = order_data["symbol"]
        side = order_data["side"]

        # Handle market order parameters (KuCoin uses 'funds' for buy market orders)
        if order_data.get("type") == "market":
            if side == "buy":
                funds = float(order_data.get("funds", 0))
                ticker = self._tickers.get(symbol)
                current_price = float(ticker.price) if ticker and ticker.price else 0.001
                size = funds / current_price if current_price > 0 else 0
                price = current_price
            else:
                size = float(order_data.get("size", 0))
                ticker = self._tickers.get(symbol)
                price = float(ticker.price) if ticker and ticker.price else 0.001
        else:
            price = float(order_data["price"])
            size = float(order_data["size"])

        ticker = self._tickers.get(symbol)
        current_price = price if ticker is None else ticker.price

        order = TradeOrder(
            order_id=order_id,
            symbol=symbol,
            side=side,
            type=order_data["type"],
            price=price,
            size=size,
            status="ACTIVE",
            filled_size=0,
            avg_price=0,
            created_at=int(time.time() * 1000),
        )

        self._paper_orders[order_id] = order

        execution_price = current_price
        execution_size = size

        base, quote = symbol.replace("-", "").split("USDT")
        base = base.upper()
        quote = "USDT"

        if quote in self._paper_balance:
            if side == "buy":
                cost = execution_price * execution_size
                if self._paper_balance[quote] >= cost:
                    self._paper_balance[quote] -= cost
                    self._paper_balance[base] = self._paper_balance.get(base, 0) + execution_size
            else:
                if self._paper_balance.get(base, 0) >= execution_size:
                    self._paper_balance[base] -= execution_size
                    self._paper_balance[quote] += execution_price * execution_size

        order.filled_size = execution_size
        order.avg_price = execution_price
        order.status = "DONE"
        order.fee = execution_size * execution_price * 0.001  # 0.1% fee
        order.fee_currency = quote

        self._paper_orders[order_id] = order
        return order

    async def _live_create_order(self, order_data: Dict) -> TradeOrder:
        body = json.dumps(order_data)
        data = await self._request("POST", "/api/v1/orders", body=body)
        return TradeOrder.from_response(data, order_data["symbol"])

    async def cancel_order(self, order_id: str) -> bool:
        if self.paper_trading:
            if order_id in self._paper_orders:
                self._paper_orders[order_id].status = "CANCELLED"
                return True
            return False
        else:
            await self._request_with_retry("DELETE", f"/api/v1/orders/{order_id}")
            return True

    async def get_order(self, order_id: str, symbol: str = "") -> Optional[TradeOrder]:
        if self.paper_trading:
            return self._paper_orders.get(order_id)
        else:
            data = await self._request_with_retry("GET", f"/api/v1/orders/{order_id}")
            return TradeOrder.from_response(data, symbol)

    def get_paper_balance(self) -> Dict[str, float]:
        return self._paper_balance.copy()

    async def get_funding_rate(self, symbol: str) -> Dict:
        try:
            data = await self._request_with_retry("GET", f"/api/v1/funding-rate/{symbol}")
            return {
                "symbol": symbol,
                "funding_rate": float(data.get("fundingRate", 0)),
                "time": data.get("time", 0),
            }
        except Exception:
            return {"symbol": symbol, "funding_rate": 0, "time": 0}

    async def get_open_interest(self, symbol: str) -> Dict:
        try:
            data = await self._request_with_retry("GET", f"/api/v1/openInterest/{symbol}")
            return {
                "symbol": symbol,
                "open_interest": float(data.get("openInterest", 0)),
                "timestamp": data.get("time", 0),
            }
        except Exception:
            return {"symbol": symbol, "open_interest": 0, "timestamp": 0}

    async def get_derivatives_metrics(self, symbol: str) -> Dict:
        funding = await self.get_funding_rate(symbol)
        oi = await self.get_open_interest(symbol)
        return {
            "funding_rate": funding.get("funding_rate", 0),
            "funding_time": funding.get("time", 0),
            "open_interest": oi.get("open_interest", 0),
            "oi_timestamp": oi.get("timestamp", 0),
        }

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
        if self._ws:
            await self._ws.close()

    def __repr__(self):
        return f"KuCoinClient(sandbox={self.sandbox}, paper={self.paper_trading})"


class MarketData:
    def __init__(self, client: KuCoinClient):
        self.client = client

    async def get_price(self, symbol: str) -> float:
        ticker = await self.client.get_ticker(symbol)
        return ticker.price

    async def get_order_flow(self, symbol: str) -> Dict:
        orderbook = await self.client.get_orderbook(symbol)
        bids = orderbook.bids
        asks = orderbook.asks

        bid_volume = sum(b[1] for b in bids[:5])
        ask_volume = sum(a[1] for a in asks[:5])

        return {
            "bid_volume": bid_volume,
            "ask_volume": ask_volume,
            "imbalance": (bid_volume - ask_volume) / (bid_volume + ask_volume + 0.001),
            "pressure": "BUY" if bid_volume > ask_volume else "SELL",
        }

    async def get_volume_profile(self, symbol: str, granularity: str = "1min") -> Dict:
        """
        Get volume profile for a symbol.

        Args:
            symbol: Trading symbol (e.g., "BTC-USDT")
            granularity: Candle type (KuCoin format: 1min, 5min, 15min, 1h, 4h, 1d)

        Returns:
            Volume profile data including VWAP and point of control
        """
        # Map granularity to KuCoin candle type format
        candle_type = granularity
        if isinstance(granularity, int):
            # Convert seconds to KuCoin format
            if granularity == 60:
                candle_type = "1min"
            elif granularity == 300:
                candle_type = "5min"
            elif granularity == 900:
                candle_type = "15min"
            elif granularity == 3600:
                candle_type = "1h"
            elif granularity == 14400:
                candle_type = "4h"
            elif granularity == 86400:
                candle_type = "1d"
            else:
                candle_type = "1min"  # Default

        candles = await self.client.get_candles(symbol, candle_type)

        prices = []
        volumes = []
        for c in candles:
            avg_price = (c.high + c.low + c.close) / 3
            prices.append(avg_price)
            volumes.append(c.volume)

        total_volume = sum(volumes)
        vwap = sum(p * v for p, v in zip(prices, volumes)) / total_volume if total_volume > 0 else 0

        volume_by_price = {}
        for p, v in zip(prices, volumes):
            bucket = int(p / 10) * 10
            volume_by_price[bucket] = volume_by_price.get(bucket, 0) + v

        poc = max(volume_by_price, key=volume_by_price.get)

        return {
            "vwap": vwap,
            "poc": poc,
            "total_volume": total_volume,
        }


class TradingClient:
    def __init__(self, client: KuCoinClient):
        self.client = client

    async def place_market_order(self, symbol: str, side: str, size: float) -> TradeOrder:
        return await self.client.create_order(symbol, side, "market", 0, size)

    async def place_limit_order(
        self, symbol: str, side: str, price: float, size: float
    ) -> TradeOrder:
        return await self.client.create_order(symbol, side, "limit", price, size)

    async def place_stop_order(
        self, symbol: str, side: str, price: float, size: float, stop_price: float
    ) -> TradeOrder:
        order_data = {
            "clientOid": f"ibis_{int(time.time() * 1000)}",
            "symbol": symbol,
            "side": side,
            "type": "limit",
            "price": str(price),
            "size": str(size),
            "stop": "price",
            "stopPrice": str(stop_price),
        }

        if self.client.paper_trading:
            return await self.client._paper_create_order(order_data)
        else:
            body = json.dumps(order_data)
            data = await self.client._request("POST", "/api/v1/orders", body=body)
            return TradeOrder.from_response(data, symbol)

    async def get_open_orders(self, symbol: str = "") -> List[TradeOrder]:
        if self.client.paper_trading:
            orders = [o for o in self.client._paper_orders.values() if o.status == "ACTIVE"]
            if symbol:
                orders = [o for o in orders if o.symbol == symbol]
            return orders
        else:
            query = f"symbol={symbol}" if symbol else ""
            data = await self.client._request(
                "GET", f"/api/v1/orders?status=ACTIVE{'&' + query if query else ''}"
            )
            return [TradeOrder.from_response(o, symbol) for o in data.get("items", [])]

    async def cancel_all_orders(self, symbol: str = ""):
        if self.client.paper_trading:
            for order_id in list(self.client._paper_orders.keys()):
                if self.client._paper_orders[order_id].status == "ACTIVE":
                    if not symbol or self.client._paper_orders[order_id].symbol == symbol:
                        await self.client.cancel_order(order_id)
        else:
            await self.client._request_with_retry(
                "DELETE", f"/api/v1/orders{'?symbol=' + symbol if symbol else ''}"
            )


_KUCOIN_CLIENT_INSTANCE: Optional[KuCoinClient] = None


def get_kucoin_client(
    api_key: str = "",
    api_secret: str = "",
    api_passphrase: str = "",
    sandbox: Optional[bool] = None,
    paper_trading: Optional[bool] = None,
) -> KuCoinClient:
    global _KUCOIN_CLIENT_INSTANCE
    if _KUCOIN_CLIENT_INSTANCE is None:
        # Use defaults from env if not provided
        k = api_key or EnvConfig.KUCOIN_API_KEY
        s = api_secret or EnvConfig.KUCOIN_API_SECRET
        p = api_passphrase or EnvConfig.KUCOIN_API_PASSPHRASE
        sb = sandbox if sandbox is not None else EnvConfig.KUCOIN_IS_SANDBOX
        pt = paper_trading if paper_trading is not None else EnvConfig.PAPER_TRADING

        _KUCOIN_CLIENT_INSTANCE = KuCoinClient(k, s, p, sb, pt)
    return _KUCOIN_CLIENT_INSTANCE


def clear_kucoin_client_instance():
    global _KUCOIN_CLIENT_INSTANCE
    _KUCOIN_CLIENT_INSTANCE = None
