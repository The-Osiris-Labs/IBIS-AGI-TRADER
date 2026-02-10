#!/usr/bin/env python3
import asyncio
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

    # Update both capital and positions
    await agent.update_capital_awareness()
    capital = agent.state["capital_awareness"]
    print(f"   USDT Total: ${capital['usdt_total']:.2f}")
    print(f"   USDT Available: ${capital['usdt_available']:.2f}")
    print(f"   Holdings Value: ${capital['holdings_value']:.2f}")
    print(f"   Total Assets: ${capital['total_assets']:.2f}")
    print(f"   Real Trading Capital: ${capital['real_trading_capital']:.2f}")

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

    scores = []
    for symbol, intel in agent.market_intel.items():
        score = intel.get("score", 0)
        if score > 0:
            scores.append((symbol, score))

    scores.sort(key=lambda x: x[1], reverse=True)

    print(f"   Valid scores found: {len(scores)}")
    high_score_count = sum(1 for s in scores if s[1] >= 90)
    print(f"   High-quality opportunities (≥90 score): {high_score_count}")

    if scores:
        print("   Top scores:")
        for sym, score in scores[:10]:
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
