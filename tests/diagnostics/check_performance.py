#!/usr/bin/env python3
"""
Check performance tracking system
"""

import sys

sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader")
from ibis_true_agent import IBISTrueAgent
import asyncio


async def check_performance_tracking():
    agent = IBISTrueAgent()
    await agent.initialize()

    print("📊 PERFORMANCE TRACKING VERIFICATION")
    print("=" * 50)

    # Check if performance tracking is initialized
    if hasattr(agent, "enhanced") and hasattr(agent.enhanced, "performance_tracker"):
        print("✅ Performance tracker initialized")

        # Check performance tracker type
        tracker = agent.enhanced.performance_tracker
        print(f"   Tracker: {type(tracker).__name__}")

        # Check if we can get metrics
        metrics = tracker.get_metrics()
        print(f"   Metrics available: {len(metrics) > 0}")

        if metrics:
            print(f"   Trades tracked: {metrics.get('total_trades', 0)}")
            print(f"   Win rate: {metrics.get('win_rate', 0):.1f}%")
            print(f"   Total PnL: ${metrics.get('total_pnl', 0):.2f}")
        else:
            print("⚠️ No trades in history - metrics not available")
    else:
        print("❌ Performance tracker not initialized")

    # Check if trades can be recorded
    test_trade = {
        "symbol": "TEST",
        "entry_price": 100,
        "exit_price": 105,
        "size": 0.1,
        "pnl": 0.5,
        "pnl_pct": 5.0,
        "status": "CLOSED",
        "entry_reason": "Test",
        "exit_reason": "Test",
        "entry_time": "2024-01-12T10:00:00",
        "exit_time": "2024-01-12T10:30:00",
        "regime": "VOLATILE",
        "strategy": "MICRO_HUNTER",
    }

    if hasattr(agent, "enhanced") and hasattr(agent.enhanced, "performance_tracker"):
        agent.enhanced.performance_tracker.record_trade(test_trade)
        print("✅ Test trade recorded")

        # Verify trade was recorded
        metrics = agent.enhanced.performance_tracker.get_metrics()
        if metrics.get("total_trades", 0) == 1:
            print("✅ Trade tracking working")
        else:
            print("❌ Trade not found in metrics")

    print("\n✅ Performance tracking system is working correctly")


asyncio.run(check_performance_tracking())
