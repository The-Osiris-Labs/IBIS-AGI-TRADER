#!/usr/bin/env python3
"""
Comprehensive IBIS System Logic Analysis
"""

import sys

sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader")

from ibis_true_agent import IBISTrueAgent
from ibis_enhanced_integration import IBISEnhancedIntegration
from ibis.core.trading_constants import TRADING
import asyncio


async def analyze_system_logic():
    print("🧠 COMPREHENSIVE IBIS SYSTEM LOGIC ANALYSIS")
    print("=" * 70)

    # Initialize agent
    agent = IBISTrueAgent()
    await agent.initialize()

    print(f"✅ Agent initialized successfully")
    print(f"   Version: IBIS TRUE TRADER v3.1")
    print(f"   Paper Trading: {agent.paper_trading}")

    # Enhanced integration
    enhanced = IBISEnhancedIntegration(agent)

    # Market intelligence
    print(f"\n📊 MARKET INTELLIGENCE:")
    print(f"   Symbols discovered: {len(agent.symbols_cache)}")
    print(f"   Rules loaded: {len(agent.symbol_rules)}")

    # Analyze opportunities
    await agent.analyze_market_intelligence()
    print(f"   Opportunities analyzed: {len(agent.market_intel)}")

    best_opp = None
    for sym, intel in agent.market_intel.items():
        if not best_opp or intel["score"] > best_opp["score"]:
            best_opp = {"symbol": sym, "score": intel["score"]}

    print(f"   Best opportunity: {best_opp}")

    # Enhanced analysis for best opportunity
    if best_opp:
        sym = best_opp["symbol"]
        intel = agent.market_intel[sym]
        print(f"\n🔍 ENHANCED ANALYSIS FOR {sym}:")

        enhanced_signal = await enhanced.get_comprehensive_analysis(sym, intel)
        print(f"   Enhanced score: {enhanced_signal.get('enhanced_score', 0):.1f}")
        print(
            f"   AGI action: {enhanced_signal.get('agi_analysis', {}).get('agi_action', 'HOLD')}"
        )
        print(
            f"   MTF alignment: {enhanced_signal.get('mtf_analysis', {}).get('alignment_score', 0):.1f}%"
        )
        print(
            f"   Risk/reward: {enhanced_signal.get('stops', {}).get('risk_reward', 0):.2f}R"
        )

        sizing = enhanced_signal.get("position_sizing", {})
        print(f"   Position size: ${sizing.get('size_usdt', 0):.2f}")

        rec = enhanced_signal.get("recommendation", {})
        print(f"   Recommendation: {rec.get('action', 'HOLD')}")

    # Trading constants
    print(f"\n🎯 TRADING CONSTANTS:")
    print(f"   Min score threshold: {TRADING.SCORE.MIN_THRESHOLD}")
    print(
        f"   Position limits: {TRADING.POSITION.MAX_TOTAL_POSITIONS} max, ${TRADING.POSITION.MIN_CAPITAL_PER_TRADE:.0f} min"
    )
    print(f"   Risk per trade: {TRADING.RISK.BASE_RISK_PER_TRADE:.1%}")

    # Portfolio status
    print(f"\n💰 PORTFOLIO STATUS:")
    capital = agent.state["capital_awareness"]
    positions = agent.state["positions"]

    print(f"   Total assets: ${capital.get('total_assets', 0):.2f}")
    print(f"   Available: ${capital.get('usdt_available', 0):.2f}")
    print(f"   Holdings value: ${capital.get('holdings_value', 0):.2f}")
    print(f"   Positions: {len(positions)}")

    if positions:
        print(f"\n📈 POSITION DETAILS:")
        for sym, pos in positions.items():
            print(f"   {sym}:")
            print(f"      Size: {pos.get('size', 0):.4f}")
            print(f"      Entry: ${pos.get('entry_price', 0):.4f}")
            print(f"      Current: ${pos.get('current_price', 0):.4f}")
            pnl = pos.get("pnl", 0)
            print(
                f"      PnL: ${pnl:.2f} ({pnl / pos.get('entry_price', 1) * 100:.1f}%)"
            )

    print(f"\n✅ SYSTEM LOGIC ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(analyze_system_logic())
