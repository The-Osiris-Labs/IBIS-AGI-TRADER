#!/usr/bin/env python3
"""
Enhanced execution strategy with dynamic limit pricing
Based on real-time volatility and order book analysis
"""

import asyncio
import json
import os
from ibis_true_agent import IBISTrueAgent
from advanced_intelligence import AdvancedIntelligenceSystem


class EnhancedExecutionSystem:
    """
    Enhanced execution system with dynamic limit pricing
    """

    def __init__(self, agent):
        self.agent = agent
        self.ai_system = AdvancedIntelligenceSystem(agent)

    async def enhance_execution_strategy(self):
        """Enhance standard execution with dynamic pricing"""
        print("🚀 ENHANCING EXECUTION STRATEGY...")

        # Enhance market intelligence
        await self.ai_system.enhance_market_intelligence()

        # Analyze current positions and orders
        await self.analyze_current_state()

        # Adjust execution strategy based on advanced analytics
        await self.adjust_execution_strategy()

        print("✅ EXECUTION STRATEGY ENHANCED")

    async def analyze_current_state(self):
        """Analyze current positions and orders"""
        capital = self.agent.state["capital_awareness"]
        portfolio = await self.agent.update_positions_awareness()

        print("\n📊 CURRENT STATE ANALYSIS")
        print("=" * 60)

        print(
            f"Capital: ${capital['total_assets']:.2f} | Available: ${capital['usdt_available']:.2f}"
        )
        print(
            f"Holdings Value: ${capital['holdings_value']:.2f} | Locked: ${capital['usdt_locked_buy']:.2f}"
        )

        print("\nPositions:")
        for sym, pos in portfolio["positions"].items():
            status = "📈" if pos["pnl_pct"] > 0 else "📉" if pos["pnl_pct"] < 0 else "➡️"
            print(f"{status} {sym}: ${pos['value']:.2f} ({pos['pnl_pct']:+.2f}%)")

        open_orders = await self.agent.client.get_open_orders()
        print(f"\nOpen Orders: {len(open_orders)}")
        for order in open_orders:
            print(
                f"  {order.get('symbol')}: {order.get('size')} @ {order.get('price')}"
            )

    async def adjust_execution_strategy(self):
        """Adjust execution strategy based on advanced analytics"""
        # Process ADI - currently has limit order
        await self.process_adi_order()

        # Check for new opportunities based on enhanced intelligence
        await self.check_new_opportunities()

    async def process_adi_order(self):
        """Process ADI order with dynamic pricing"""
        open_orders = await self.agent.client.get_open_orders()
        adi_order = None

        for order in open_orders:
            if order.get("symbol") == "ADI-USDT":
                adi_order = order
                break

        adi_signal = self.ai_system.real_time_signals.get("ADI", {})

        if adi_order and adi_signal.get("signal") in ["BUY", "STRONG_BUY"]:
            await self.optimize_adi_order(adi_order, adi_signal)

    async def optimize_adi_order(self, current_order, signal):
        """Optimize ADI order based on real-time signals"""
        try:
            adi_ticker = await self.agent.client.get_ticker("ADI-USDT")
            current_price = adi_ticker.price
            order_book = await self.agent.client.get_orderbook("ADI-USDT", 20)

            # Calculate dynamic discount based on volatility and signal
            volatility = signal.get("volatility", 0.0)

            if volatility > 1.0:
                discount = 0.002  # 0.2% discount - aggressive
            elif volatility > 0.5:
                discount = 0.005  # 0.5% discount - balanced
            else:
                discount = 0.010  # 1.0% discount - patient

            optimal_price = current_price * (1 - discount)
            current_limit = float(current_order.get("price"))

            distance = abs((optimal_price - current_limit) / current_limit)

            if distance > 0.0005:  # More than 0.05% difference
                print(
                    f"\n🔄 Optimizing ADI order: ${current_limit:.6f} → ${optimal_price:.6f}"
                )

                # Cancel and re-place order
                await self.agent.client.cancel_order(current_order.get("orderId"))
                await asyncio.sleep(1)

                order_size = float(current_order.get("size"))
                new_order = await self.agent.client.create_limit_order(
                    symbol="ADI-USDT", side="buy", price=optimal_price, size=order_size
                )

                print(
                    f"✅ ADI order optimized: {new_order.get('size')} @ ${new_order.get('price'):.6f}"
                )

                # Update capital awareness
                await self.agent.update_capital_awareness()
            else:
                print("\n✅ ADI order already optimal")

        except Exception as e:
            print(f"⚠️ Error optimizing ADI order: {e}")

    async def check_new_opportunities(self):
        """Check for new opportunities based on enhanced intelligence"""
        capital = self.agent.state["capital_awareness"]
        available = capital["usdt_available"]

        if available < 10:
            print("\n⚠️ Insufficient capital for new opportunities")
            return

        # Check for strong buy signals
        strong_buys = [
            (symbol, signal)
            for symbol, signal in self.ai_system.real_time_signals.items()
            if signal["signal"] == "STRONG_BUY"
            and symbol not in self.agent.state["positions"]
        ]

        for symbol, signal in strong_buys:
            if available < 10:
                break

            print(f"\n🎯 New opportunity: {symbol} (STRONG_BUY)")

            # Calculate position size based on signal strength
            position_size = min(available * (signal["confidence"] * 0.25), 30)

            try:
                ticker = await self.agent.client.get_ticker(f"{symbol}-USDT")
                optimal_price = ticker.price * (1 - (0.005 * signal["confidence"]))

                order = await self.agent.client.create_limit_order(
                    symbol=f"{symbol}-USDT",
                    side="buy",
                    price=optimal_price,
                    size=position_size / optimal_price,
                )

                print(
                    f"✅ Order placed: {symbol} - {order.get('size')} @ ${order.get('price'):.6f}"
                )

                available -= position_size

            except Exception as e:
                print(f"⚠️ Error placing order for {symbol}: {e}")


async def test_enhanced_execution():
    """Test the enhanced execution system"""
    agent = IBISTrueAgent()
    await agent.initialize()

    execution_system = EnhancedExecutionSystem(agent)
    await execution_system.enhance_execution_strategy()

    return execution_system


if __name__ == "__main__":
    asyncio.run(test_enhanced_execution())
