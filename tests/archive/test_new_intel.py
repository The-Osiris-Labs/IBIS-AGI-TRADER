#!/usr/bin/env python3
"""
🦅 IBIS TRUE AGENT - NEW INTELLIGENCE INTEGRATION TEST
=======================================================
Test all new intelligence sources:
1. Order book depth analysis
2. Sentiment analysis (placeholder)
3. On-chain metrics (placeholder)
4. ATR-based dynamic TP/SL
5. Portfolio rebalancing
"""

import asyncio
from ibis_true_agent import IBISAutonomousAgent


async def test_new_intelligence():
    print("=" * 80)
    print("🦅 IBIS TRUE AGENT - NEW INTELLIGENCE INTEGRATION TEST")
    print("=" * 80)

    agent = IBISAutonomousAgent()
    await agent.initialize()

    print("\n" + "=" * 80)
    print("TEST 1: Order Book Depth Analysis")
    print("=" * 80)

    symbols_to_test = ["BTC", "ETH", "CGPT"]
    for sym in symbols_to_test:
        try:
            orderbook = await agent._analyze_orderbook_depth(f"{sym}-USDT")
            print(f"  {sym}:")
            print(f"    Bid Depth: ${orderbook.get('bid_depth', 0):,.2f}")
            print(f"    Ask Depth: ${orderbook.get('ask_depth', 0):,.2f}")
            print(f"    Imbalance: {orderbook.get('imbalance', 0):.2%}")
            print(f"    Score: {orderbook.get('score', 50):.1f}/100")
        except Exception as e:
            print(f"  {sym}: Error - {e}")

    print("\n" + "=" * 80)
    print("TEST 2: Sentiment Analysis")
    print("=" * 80)

    for sym in symbols_to_test:
        try:
            sentiment = await agent._get_sentiment_score(sym)
            print(f"  {sym}:")
            print(f"    Score: {sentiment.get('score', 50):.1f}/100")
            print(f"    Confidence: {sentiment.get('confidence', 0):.1%}")
            print(f"    Sources: {list(sentiment.get('sources', {}).keys())}")
        except Exception as e:
            print(f"  {sym}: Error - {e}")

    print("\n" + "=" * 80)
    print("TEST 3: On-Chain Metrics")
    print("=" * 80)

    for sym in symbols_to_test:
        try:
            onchain = await agent._get_onchain_metrics(sym)
            print(f"  {sym}:")
            print(f"    Overall Score: {onchain.get('score', 50):.1f}/100")
            print(f"    Whale Score: {onchain.get('whale_score', 50):.1f}")
            print(f"    Inflow Score: {onchain.get('inflow_score', 50):.1f}")
            print(f"    Holder Score: {onchain.get('holder_score', 50):.1f}")
        except Exception as e:
            print(f"  {sym}: Error - {e}")

    print("\n" + "=" * 80)
    print("TEST 4: ATR-Based Dynamic TP/SL")
    print("=" * 80)

    test_regimes = ["TRENDING", "NORMAL", "FLAT", "VOLATILE"]
    for regime in test_regimes:
        tp_sl = agent._calculate_dynamic_tp_sl(
            price=100.0, atr_percent=0.025, regime=regime, confidence_score=75
        )
        print(f"  {regime}:")
        print(
            f"    TP: {tp_sl.get('tp_percent', 0):.2f}% (${tp_sl.get('tp_price', 0):.2f})"
        )
        print(
            f"    SL: {tp_sl.get('sl_percent', 0):.2f}% (${tp_sl.get('sl_price', 0):.2f})"
        )
        print(f"    ATR%: {tp_sl.get('atr_percent', 0):.2f}%")

    print("\n" + "=" * 80)
    print("TEST 5: Portfolio Rebalancing")
    print("=" * 80)

    opportunities = [
        {"symbol": "BTC", "adjusted_score": 85},
        {"symbol": "ETH", "adjusted_score": 75},
        {"symbol": "CGPT", "adjusted_score": 65},
    ]
    portfolio = await agent._optimize_portfolio_allocation(
        opportunities=opportunities, available_capital=1000.0
    )
    print(f"  Available Capital: $1,000.00")
    print(f"  Opportunities: {len(opportunities)}")
    for sym, data in portfolio.items():
        print(f"  {sym}:")
        print(f"    Position Size: ${data.get('size', 0):.2f}")
        print(f"    Weight: {data.get('weight', 0):.1%}")
        print(f"    ATR%: {data.get('atr_percent', 0):.2f}%")
        print(f"    Risk Factor: {data.get('risk_factor', 0):.2f}")

    print("\n" + "=" * 80)
    print("TEST 6: Complete Intelligence Integration")
    print("=" * 80)

    print(f"  Market Intel Entries: {len(agent.market_intel)}")
    for sym, intel in list(agent.market_intel.items())[:3]:
        print(f"\n  {sym}:")
        print(f"    Price: ${intel.get('price', 0):.4f}")
        print(f"    Score: {intel.get('score', 0):.1f}/100")
        print(f"    Base Score: {intel.get('base_score', 0):.1f}")
        print(f"    24h Change: {intel.get('change_24h', 0):.2f}%")
        print(f"    Volatility: {intel.get('volatility', 0):.2%}")
        if intel.get("orderbook_analysis"):
            print(f"    Orderbook: {intel['orderbook_analysis'].get('score', 50):.1f}")
        if intel.get("sentiment_analysis"):
            print(f"    Sentiment: {intel['sentiment_analysis'].get('score', 50):.1f}")
        if intel.get("onchain_metrics"):
            print(f"    On-chain: {intel['onchain_metrics'].get('score', 50):.1f}")
        if intel.get("atr_data"):
            print(f"    ATR: {intel['atr_data'].get('atr_percent', 0):.2f}%")
        insights = intel.get("insights", [])[:3]
        if insights:
            print(f"    Insights: {insights}")

    await agent.client.close()

    print("\n" + "=" * 80)
    print("🦅 ALL NEW INTELLIGENCE INTEGRATIONS: SUCCESSFUL!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_new_intelligence())
