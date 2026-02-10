#!/usr/bin/env python3
"""
Enhanced execution engine with price increment validation and improved error handling
"""

import asyncio
import json
import os
from ibis_true_agent import IBISTrueAgent


class EnhancedExecutionEngine:
    """
    Enhanced execution engine with dynamic pricing and increment validation
    """

    def __init__(self, agent):
        self.agent = agent
        self.price_increments = {}
        self.size_increments = {}

    async def initialize(self):
        """Initialize execution engine"""
        await self.load_symbol_info()
        print("✅ Enhanced execution engine initialized")

    async def load_symbol_info(self):
        """Load symbol information including price increments"""
        symbols = ["ADI", "AIO", "AERGO", "ALEPH"]

        for symbol in symbols:
            try:
                symbol_info = await self.agent.client.get_symbol(f"{symbol}-USDT")
                self.price_increments[symbol] = float(symbol_info["priceIncrement"])
                self.size_increments[symbol] = float(symbol_info["baseIncrement"])
            except Exception as e:
                print(f"⚠️ Error loading info for {symbol}: {e}")
                # Default values
                self.price_increments[symbol] = 0.0001
                self.size_increments[symbol] = 0.01

    async def validate_order_params(self, symbol, price, size):
        """Validate order parameters against exchange rules"""
        if symbol not in self.price_increments or symbol not in self.size_increments:
            await self.load_symbol_info()

        price_increment = self.price_increments.get(symbol, 0.0001)
        size_increment = self.size_increments.get(symbol, 0.01)

        # Validate price - always round to valid decimal places for the increment
        decimal_places = (
            len(str(price_increment).split(".")[-1])
            if "." in str(price_increment)
            else 0
        )
        price = round(price, decimal_places)

        # Validate size
        size_decimal_places = (
            len(str(size_increment).split(".")[-1]) if "." in str(size_increment) else 0
        )
        size = round(size, size_decimal_places)

        return price, size

    async def optimize_adi_order(self):
        """Optimize ADI order with valid price and size increments"""
        open_orders = await self.agent.client.get_open_orders()
        adi_order = None

        for order in open_orders:
            if order.get("symbol") == "ADI-USDT":
                adi_order = order
                break

        if adi_order:
            try:
                adi_ticker = await self.agent.client.get_ticker("ADI-USDT")
                current_price = adi_ticker.price

                # Calculate optimal price based on 0.5% discount (moderate volatility)
                optimal_price = current_price * 0.995
                optimal_price, _ = await self.validate_order_params(
                    "ADI", optimal_price, 0
                )

                current_limit = float(adi_order.get("price"))
                distance = abs((optimal_price - current_limit) / current_limit)

                if distance > 0.0005:  # More than 0.05% difference
                    print(
                        f"🔄 Optimizing ADI order: ${current_limit:.6f} → ${optimal_price:.6f}"
                    )

                    # Cancel existing order with retry logic
                    for attempt in range(3):
                        try:
                            await self.agent.client.cancel_order(
                                adi_order.get("orderId")
                            )
                            break
                        except Exception as e:
                            print(f"⚠️ Cancel attempt {attempt + 1} failed: {e}")
                            await asyncio.sleep(1)

                await asyncio.sleep(2)

                order_size = float(adi_order.get("size"))
                order_size, _ = await self.validate_order_params("ADI", 0, order_size)

                new_order = await self.agent.client.create_limit_order(
                    symbol="ADI-USDT", side="buy", price=optimal_price, size=order_size
                )

                print(
                    f"✅ ADI order optimized: {new_order.get('size')} @ ${new_order.get('price'):.6f}"
                )

                # Update capital awareness
                await self.agent.update_capital_awareness()

            except Exception as e:
                print(f"⚠️ Error optimizing ADI order: {e}")

    async def execute_strategy(self):
        """Execute enhanced trading strategy"""
        print("🚀 Executing enhanced strategy...")

        await self.agent.analyze_market_intelligence()

        # Get all STRONG_BUY and BUY signals
        signals = []
        for symbol, intel in self.agent.market_intel.items():
            if hasattr(intel, "agi_insight"):
                insight = intel.agi_insight.lower()
                if "buy" in insight or "strong buy" in insight:
                    signals.append(symbol)

        print(f"📊 Trading signals: {signals}")

        capital = self.agent.state["capital_awareness"]
        available = capital["usdt_available"]

        if available < 10:
            print("⚠️ Insufficient capital for trading")
            return

        # Check if we need to optimize existing orders or place new ones
        for symbol in signals:
            if symbol in self.agent.state["positions"]:
                print(f"ℹ️ {symbol} already in portfolio")
                continue

            print(f"🎯 Opening position in {symbol}")

            await self.open_position(symbol)

    async def open_position(self, symbol):
        """Open new position with validated parameters"""
        capital = self.agent.state["capital_awareness"]
        available = capital["usdt_available"]

        position_size = min(available * 0.25, 30)

        try:
            ticker = await self.agent.client.get_ticker(f"{symbol}-USDT")
            price = ticker.price

            # Calculate optimal entry price based on volatility
            await self.agent.analyze_market_intelligence()
            intel = self.agent.market_intel.get(symbol, {})
            volatility = intel.get("volatility_1m", 0.0)

            if volatility > 1.0:
                discount = 0.002  # 0.2% discount
            elif volatility > 0.5:
                discount = 0.005  # 0.5% discount
            else:
                discount = 0.010  # 1.0% discount

            optimal_price = price * (1 - discount)
            optimal_price, _ = await self.validate_order_params(
                symbol, optimal_price, 0
            )

            order_size = position_size / optimal_price
            order_size, _ = await self.validate_order_params(symbol, 0, order_size)

            order = await self.agent.client.create_limit_order(
                symbol=f"{symbol}-USDT",
                side="buy",
                price=optimal_price,
                size=order_size,
            )

            print(
                f"✅ Position opened: {symbol} - {order.get('size')} @ ${order.get('price'):.6f}"
            )

            # Update capital awareness
            await self.agent.update_capital_awareness()

        except Exception as e:
            print(f"⚠️ Error opening position in {symbol}: {e}")


async def test_enhanced_engine():
    """Test enhanced execution engine"""
    agent = IBISTrueAgent()
    await agent.initialize()

    engine = EnhancedExecutionEngine(agent)
    await engine.initialize()

    print("=" * 60)
    print("🎯 TESTING ENHANCED EXECUTION ENGINE")
    print("=" * 60)

    # Test parameter validation
    test_price, test_size = await engine.validate_order_params("ADI", 2.607660, 5.67)
    print(f"Validated ADI: Price=${test_price:.6f}, Size={test_size:.6f}")

    # Check if we should optimize ADI order
    await engine.optimize_adi_order()

    # Execute strategy
    await engine.execute_strategy()

    print("\n✅ Enhanced execution engine test complete")


if __name__ == "__main__":
    asyncio.run(test_enhanced_engine())
