#!/usr/bin/env python3
import asyncio
from ibis.exchange.kucoin_client import get_kucoin_client
from ibis_true_agent import IBISTrueAgent


async def analyze_system():
    print("🎯 Running comprehensive IBIS system analysis...")

    # Initialize agent
    agent = IBISTrueAgent()
    await agent.initialize()

    print("\n📊 SYSTEM STATUS:")
    print(f"   Market Regime: {agent.state['market_regime']}")
    print(f"   Agent Mode: {agent.state['agent_mode']}")
    print(f"   Positions: {len(agent.state['positions'])}")
    print(
        f"   Available Capital: ${agent.state['capital_awareness']['real_trading_capital']:.2f}"
    )
    print(
        f"   Holdings Value: ${agent.state['capital_awareness']['holdings_value']:.2f}"
    )
    print(f"   Total Assets: ${agent.state['capital_awareness']['total_assets']:.2f}")

    # Check open orders
    print("\n📝 OPEN ORDERS:")
    open_orders = await agent.client.get_open_orders()
    print(f"   Total open orders: {len(open_orders)}")

    if open_orders:
        for order in open_orders:
            symbol = (
                order.symbol.replace("-USDT", "")
                if hasattr(order, "symbol")
                else order.get("symbol", "N/A")
            )
            side = order.side if hasattr(order, "side") else order.get("side", "N/A")
            size = order.size if hasattr(order, "size") else order.get("size", "N/A")
            price = (
                order.price if hasattr(order, "price") else order.get("price", "N/A")
            )
            print(f"   • {symbol} {side}: {size} @ ${price}")

    # Analyze current positions
    print("\n📈 POSITION PERFORMANCE:")
    portfolio = await agent.update_positions_awareness()

    for sym, pos in portfolio["positions"].items():
        status = "📈" if pos["pnl_pct"] > 0 else "📉" if pos["pnl_pct"] < 0 else "➡️"
        print(
            f"   {status} {sym}: ${pos['value']:.2f} | {pos['pnl_pct']:+.2f}% | {pos['hold_time']}"
        )

    # Run market intelligence analysis
    print("\n🔍 MARKET INTELLIGENCE:")
    await agent.analyze_market_intelligence()

    high_score_count = 0
    high_opportunities = []

    for symbol, intel in agent.market_intel.items():
        score = intel.get("score", 0)
        if score >= 90:
            high_score_count += 1
            high_opportunities.append((symbol, score))

    high_opportunities.sort(key=lambda x: x[1], reverse=True)

    print(f"   High-quality opportunities (≥90 score): {high_score_count}")
    if high_opportunities:
        print("   Top opportunities:")
        for sym, score in high_opportunities[:5]:
            print(f"      • {sym}: {score:.1f}")

    # Check if we should adjust strategy
    print("\n🎯 STRATEGY ASSESSMENT:")
    regime = agent.state["market_regime"]
    if regime == "VOLATILE" and high_score_count > 3:
        print(
            "   ✅ Volatile regime + multiple high-score opportunities - strategy optimal"
        )
        print("   🚀 Consider scaling: High-quality opportunities available")
    elif regime == "VOLATILE" and high_score_count <= 3:
        print(
            "   ⚠️ Volatile regime but limited high-quality opportunities - monitor closely"
        )
    else:
        print(f"   📊 {regime} regime - strategy appropriate")

    # Evaluate AGI effectiveness
    print("\n🧠 AGI EFFECTIVENESS:")
    agi_decisions = 0
    agi_buy_signals = 0
    agi_sell_signals = 0

    for symbol, intel in agent.market_intel.items():
        if "agi_insight" in intel:
            agi_decisions += 1
            if "BUY" in intel.get("agi_insight", "") or "BULLISH" in intel.get(
                "agi_insight", ""
            ):
                agi_buy_signals += 1
            elif "SELL" in intel.get("agi_insight", "") or "BEARISH" in intel.get(
                "agi_insight", ""
            ):
                agi_sell_signals += 1

    if agi_decisions > 0:
        print(f"   AGI decisions made: {agi_decisions}")
        print(f"   Buy signals: {agi_buy_signals} | Sell signals: {agi_sell_signals}")
        if agi_buy_signals > agi_sell_signals and regime == "VOLATILE":
            print(
                "   ✅ AGI bullish signals align with extreme fear contrarian strategy"
            )

    print("\n✅ Analysis complete!")


asyncio.run(analyze_system())
