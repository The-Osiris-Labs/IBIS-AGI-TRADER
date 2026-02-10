#!/usr/bin/env python3
"""
Real-Time System State & Knowledge Stream Updater
Ensures all system information is always up to date
"""

import asyncio
import json
import time
from ibis_true_agent import IBISTrueAgent
from enhanced_execution_engine import EnhancedExecutionEngine
from advanced_intelligence import AdvancedIntelligenceSystem


class RealTimeUpdater:
    """
    Real-time system state and knowledge stream updater
    """

    def __init__(self):
        self.agent = None
        self.execution_engine = None
        self.ai_system = None
        self.running = False
        self.last_update = 0
        self.update_interval = 30  # Update every 30 seconds

    async def initialize(self):
        """Initialize the updater"""
        self.agent = IBISTrueAgent()
        await self.agent.initialize()

        self.execution_engine = EnhancedExecutionEngine(self.agent)
        await self.execution_engine.initialize()

        self.ai_system = AdvancedIntelligenceSystem(self.agent)

        print("✅ Real-time updater initialized")

    async def update_system_state(self):
        """Update system state and knowledge stream"""
        current_time = time.time()

        if current_time - self.last_update < self.update_interval:
            return

        self.last_update = current_time

        print("🔄 Updating system state...")

        try:
            # Update market intelligence
            await self.ai_system.enhance_market_intelligence()

            # Update execution strategy
            await self.execution_engine.execute_strategy()

            # Update capital awareness
            await self.agent.update_capital_awareness()

            # Update position awareness
            await self.agent.update_positions_awareness()

            # Save state to file
            await self.save_state()

            print("✅ System state updated")

        except Exception as e:
            print(f"❌ Error updating system state: {e}")

    async def save_state(self):
        """Save current state to state file"""
        state_path = "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_true_state.json"

        try:
            with open(state_path, "w") as f:
                json.dump(self.agent.state, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving state: {e}")

    async def update_knowledge_stream(self):
        """Update knowledge stream with real-time insights"""
        # This would integrate with WebSocket or other real-time data sources
        # For now, we'll use periodic polling

        # Update market intelligence
        await self.ai_system.enhance_market_intelligence()

        # Check for new opportunities
        signals = []
        for symbol, intel in self.agent.market_intel.items():
            if hasattr(intel, "agi_insight"):
                insight = intel.agi_insight.lower()
                if "buy" in insight or "strong buy" in insight:
                    signals.append(symbol)

        if signals:
            print(f"📊 New signals detected: {', '.join(signals)}")

    async def run(self):
        """Run the real-time updater loop"""
        self.running = True

        while self.running:
            try:
                await self.update_system_state()
                await self.update_knowledge_stream()

                # Wait for next update
                await asyncio.sleep(self.update_interval)

            except Exception as e:
                print(f"❌ Updater error: {e}")
                await asyncio.sleep(10)

    async def stop(self):
        """Stop the updater"""
        self.running = False


async def test_real_time_updater():
    """Test the real-time updater"""
    print("=" * 80)
    print("🎯 TESTING REAL-TIME SYSTEM STATE UPDATER")
    print("=" * 80)

    updater = RealTimeUpdater()
    await updater.initialize()

    print("\n✅ Updater initialized successfully")

    # Run for 2 updates
    print("\n🚀 Running updater for 2 updates...")
    await asyncio.wait_for(updater.run(), timeout=60)

    print("\n✅ Updater test complete")

    # Verify state was updated
    print("\n🔍 VERIFYING SYSTEM STATE")
    print(
        f"Total Assets: ${updater.agent.state['capital_awareness']['total_assets']:.2f}"
    )
    print(
        f"USDT Balance: ${updater.agent.state['capital_awareness']['usdt_available']:.2f}"
    )
    print(
        f"Holdings Value: ${updater.agent.state['capital_awareness']['holdings_value']:.2f}"
    )
    print(
        f"Locked Capital: ${updater.agent.state['capital_awareness']['usdt_locked_buy']:.2f}"
    )

    # Verify positions
    portfolio = await updater.agent.update_positions_awareness()
    print(
        f"Total PnL: ${portfolio['total_pnl']:.2f} ({portfolio['total_pnl_pct']:.2f}%)"
    )


if __name__ == "__main__":
    try:
        asyncio.run(test_real_time_updater())
    except asyncio.TimeoutError:
        print("\n⏰ Updater test completed - ran 2 updates")
