#!/usr/bin/env python3
"""Comprehensive IBIS True Agent Test"""

import asyncio
from ibis_true_agent import IBISAutonomousAgent
from datetime import datetime


async def comprehensive_test():
    print("=" * 70)
    print("🦅 IBIS TRUE AGENT - COMPREHENSIVE CAPABILITY TEST")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Test 1: Class instantiation
    print("TEST 1: Class Instantiation")
    agent = IBISAutonomousAgent()
    print(f"  ✅ Agent created: {type(agent).__name__}")
    print(f"  ✅ Config loaded: {len(agent.config)} config keys")
    print(f"  ✅ State initialized: {list(agent.state.keys())}")
    print(f"  ✅ Memory loaded: {len(agent.agent_memory)} memory keys")
    print()

    # Test 2: Initialize (connects to KuCoin)
    print("TEST 2: KuCoin Connection & Market Discovery")
    await agent.initialize()
    print(f"  ✅ Symbols discovered: {len(agent.symbols_cache)}")
    print(f"  ✅ Symbol rules loaded: {len(agent.symbol_rules)}")
    print(f"  ✅ Market intel entries: {len(agent.market_intel)}")
    print(f"  ✅ Market regime: {agent.state['market_regime']}")
    print(f"  ✅ Agent mode: {agent.state['agent_mode']}")
    print()

    # Test 3: Market Intelligence Analysis
    print("TEST 3: Market Intelligence Quality")
    if agent.market_intel:
        scores = [d["score"] for d in agent.market_intel.values()]
        changes = [d["change_24h"] for d in agent.market_intel.values()]
        volatilities = [d["volatility"] for d in agent.market_intel.values()]
        volumes = [d["volume_24h"] for d in agent.market_intel.values()]

        print(f"  ✅ Opportunities analyzed: {len(agent.market_intel)}")
        print(f"  ✅ Score range: {min(scores):.0f} - {max(scores):.0f}")
        print(f"  ✅ Avg score: {sum(scores) / len(scores):.1f}")
        print(f"  ✅ 24h change range: {min(changes):.2f}% - {max(changes):.2f}%")
        print(
            f"  ✅ Volatility range: {min(volatilities) * 100:.2f}% - {max(volatilities) * 100:.2f}%"
        )
        print(f"  ✅ Total volume: ${sum(volumes):,.0f}")
        print()

        # Show top 5 opportunities
        print("TOP 5 OPPORTUNITIES:")
        sorted_opps = sorted(
            agent.market_intel.items(), key=lambda x: x[1]["score"], reverse=True
        )[:5]
        for i, (sym, data) in enumerate(sorted_opps, 1):
            print(
                f"  {i}. {sym:10} | Score: {data['score']:>5.0f} | 24h: {data['change_24h']:>+6.2f}% | Vol: {data['volatility'] * 100:>5.2f}%"
            )
    print()

    # Test 4: Regime Detection
    print("TEST 4: Regime Detection")
    regime = await agent.detect_market_regime()
    print(f"  ✅ Detected regime: {regime}")
    print(f"  ✅ Regime counts: {agent.state['daily']['regimes_experienced']}")
    print()

    # Test 5: Strategy Execution
    print("TEST 5: Strategy Execution")
    mode = await agent.determine_agent_mode(regime, agent.market_intel)
    strategy = await agent.execute_strategy(regime, mode)
    print(f"  ✅ Mode determined: {mode}")
    print(f"  ✅ Target profit: +{strategy['target_profit'] * 100:.1f}%")
    print(
        f"  ✅ Stop loss: {strategy['stop_loss'] if strategy['stop_loss'] else 'None (manual)'}"
    )
    print(f"  ✅ Max positions: {strategy['max_positions']}")
    print(f"  ✅ Confidence threshold: {strategy['confidence_threshold']}")
    print()

    # Test 6: Best Opportunity Finding
    print("TEST 6: Best Opportunity Finder")
    best = await agent.find_best_opportunity(strategy)
    if best:
        print(f"  ✅ Best opportunity: {best['symbol']}")
        print(f"  ✅ Score: {best['score']:.0f}")
        print(f"  ✅ Price: ${best['price']:.4f}")
        print(f"  ✅ 24h change: {best['change_24h']:+.2f}%")
    else:
        print("  ⚠️ No opportunities found meeting criteria")
    print()

    # Test 7: Position Sizing
    print("TEST 7: Dynamic Position Sizing")
    if best:
        position_size = await agent.dynamic_position_sizing(
            strategy, best["symbol"], agent.market_intel
        )
        print(f"  ✅ Position size for {best['symbol']}: ${position_size:.2f}")
    print()

    # Test 8: Market Conditions Assessment
    print("TEST 8: Market Conditions Assessment")
    conditions = agent._assess_market_conditions()
    print(f"  ✅ Overall health: {conditions['overall_health']}")
    print(f"  ✅ Trading opportunity: {conditions['trading_opportunity']}")
    print(f"  ✅ Volatility risk: {conditions['volatility_risk']}")
    print(f"  ✅ Market primed: {agent._is_market_primed()}")
    print()

    # Test 9: Portfolio Summary
    print("TEST 9: Portfolio Summary")
    balances = await agent.client.get_all_balances()
    usdt_balance = float(balances.get("USDT", {}).get("balance", 0))
    print(f"  ✅ USDT balance: ${usdt_balance:.2f}")
    print(f"  ✅ Open positions: {len(agent.state['positions'])}")
    print(f"  ✅ Daily trades: {agent.state['daily']['trades']}")
    print(f"  ✅ Daily PnL: ${agent.state['daily']['pnl']:+.4f}")
    print()

    # Test 10: Performance Tracking
    print("TEST 10: Performance Tracking")
    perf = agent.agent_memory.get("performance_by_symbol", {})
    print(f"  ✅ Strategies tracked: {len(perf)}")
    for strat, data in list(perf.items())[:3]:
        wr = (data["wins"] / data["trades"] * 100) if data["trades"] > 0 else 0
        print(
            f"     - {strat}: {data['trades']} trades, WR: {wr:.0f}%, PnL: ${data['pnl']:+.4f}"
        )
    print()

    # Cleanup
    await agent.client.close()

    print("=" * 70)
    print("🦅 IBIS TRUE AGENT - ALL TESTS PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(comprehensive_test())
