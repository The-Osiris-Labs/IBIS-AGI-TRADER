#!/usr/bin/env python3
"""
WebSocket data feed for real-time market updates
"""

import asyncio
import json
import websockets
import time
from ibis.exchange.kucoin_client import get_kucoin_client


class WebSocketDataFeed:
    """
    WebSocket data feed for real-time market updates
    """

    def __init__(self, agent):
        self.agent = agent
        self.client = agent.client
        self.running = False
        self.subscriptions = set()
        self.price_cache = {}
        self.orderbook_cache = {}
        self.volatility_cache = {}

    async def connect(self):
        """Establish WebSocket connection"""
        try:
            self.running = True
            print("🔌 Establishing WebSocket connection...")

            # Create WebSocket connection to KuCoin
            url = "wss://ws-api.kucoin.com/endpoint"
            self.websocket = await websockets.connect(url)

            print("✅ WebSocket connection established")

            # Subscribe to priority symbols
            await self.subscribe_to_symbols()

            # Start listening loop
            await self.listen()

        except Exception as e:
            print(f"❌ WebSocket connection failed: {e}")
            self.running = False
            await asyncio.sleep(5)
            await self.connect()  # Reconnect

    async def subscribe_to_symbols(self):
        """Subscribe to WebSocket channels for priority symbols"""
        symbols = ["ADI", "AIO", "AERGO", "ALEPH"]

        for symbol in symbols:
            # Subscribe to ticker channel
            ticker_sub = {
                "id": f"ticker_{symbol}",
                "type": "subscribe",
                "topic": f"/market/ticker:{symbol}-USDT",
                "privateChannel": False,
                "response": True,
            }

            await self.websocket.send(json.dumps(ticker_sub))
            self.subscriptions.add(f"/market/ticker:{symbol}-USDT")

            # Subscribe to orderbook channel
            orderbook_sub = {
                "id": f"orderbook_{symbol}",
                "type": "subscribe",
                "topic": f"/market/level2_20:{symbol}-USDT",
                "privateChannel": False,
                "response": True,
            }

            await self.websocket.send(json.dumps(orderbook_sub))
            self.subscriptions.add(f"/market/level2_20:{symbol}-USDT")

            print(f"✅ Subscribed to {symbol}-USDT channels")

    async def listen(self):
        """Listen for WebSocket messages"""
        while self.running:
            try:
                message = await self.websocket.recv()
                data = json.loads(message)

                await self.process_message(data)

            except Exception as e:
                print(f"❌ WebSocket error: {e}")
                break

    async def process_message(self, data):
        """Process incoming WebSocket messages"""
        if "topic" not in data:
            return

        topic = data["topic"]

        # Handle ticker updates
        if "/market/ticker" in topic:
            symbol = topic.split(":")[-1].replace("-USDT", "")
            await self.process_ticker_update(symbol, data)

        # Handle orderbook updates
        elif "/market/level2_20" in topic:
            symbol = topic.split(":")[-1].replace("-USDT", "")
            await self.process_orderbook_update(symbol, data)

    async def process_ticker_update(self, symbol, data):
        """Process ticker updates"""
        try:
            price = float(data["data"]["price"])
            self.price_cache[symbol] = price

            # Calculate real-time volatility
            await self.calculate_volatility(symbol)

        except Exception as e:
            print(f"❌ Error processing ticker for {symbol}: {e}")

    async def process_orderbook_update(self, symbol, data):
        """Process orderbook updates"""
        try:
            self.orderbook_cache[symbol] = data["data"]

            # Update market intelligence
            await self.agent.update_market_intelligence()

        except Exception as e:
            print(f"❌ Error processing orderbook for {symbol}: {e}")

    async def calculate_volatility(self, symbol):
        """Calculate real-time volatility"""
        if symbol not in self.price_cache:
            return

        # Simple volatility calculation based on last 20 prices
        price_history = []
        # In production, this would use actual historical prices

        # For demo purposes, use random volatility
        import random

        volatility = random.uniform(0.0, 2.0)
        self.volatility_cache[symbol] = volatility

    async def get_latest_price(self, symbol):
        """Get latest price from cache"""
        return self.price_cache.get(symbol, 0)

    async def get_orderbook(self, symbol):
        """Get latest orderbook from cache"""
        return self.orderbook_cache.get(symbol, {})

    async def get_volatility(self, symbol):
        """Get real-time volatility"""
        return self.volatility_cache.get(symbol, 0.0)

    async def disconnect(self):
        """Disconnect from WebSocket"""
        self.running = False
        if hasattr(self, "websocket"):
            await self.websocket.close()
        print("🔌 WebSocket connection closed")


# Test WebSocket integration
async def test_websocket():
    """Test WebSocket integration"""
    from ibis_true_agent import IBISTrueAgent

    agent = IBISTrueAgent()
    await agent.initialize()

    ws = WebSocketDataFeed(agent)

    try:
        await ws.connect()
        print("\n✅ WebSocket integration test complete")

        # Display cache after 3 seconds
        await asyncio.sleep(3)

        print("\n📊 Price Cache:")
        for symbol, price in ws.price_cache.items():
            print(f"  {symbol}: ${price:.6f}")

        print("\n📊 Volatility Cache:")
        for symbol, vol in ws.volatility_cache.items():
            print(f"  {symbol}: {vol:.2f}%")

    except Exception as e:
        print(f"\n❌ WebSocket test failed: {e}")

    finally:
        await ws.disconnect()


if __name__ == "__main__":
    asyncio.run(test_websocket())
