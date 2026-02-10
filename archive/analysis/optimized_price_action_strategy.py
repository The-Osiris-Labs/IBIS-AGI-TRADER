#!/usr/bin/env python3
"""
Optimized Price Action Strategy for IBIS
Capitalizes on momentum pushes, pullbacks, and dynamic limit pricing
"""

import asyncio
import json
import os
from ibis_true_agent import IBISTrueAgent


async def analyze_current_strategy():
    """Analyze current strategy and suggest improvements"""
    agent = IBISTrueAgent()
    await agent.initialize()

    print("=" * 80)
    print("🎯 IBIS CURRENT STRATEGY ANALYSIS")
    print("=" * 80)

    # Check current positions and orders
    capital = agent.state["capital_awareness"]
    portfolio = await agent.update_positions_awareness()

    print("\n📊 CURRENT STATE:")
    print(f"   Regime: {agent.state['market_regime']}")
    print(f"   Mode: {agent.state['agent_mode']}")
    print(f"   Total Assets: ${capital['total_assets']:.2f}")
    print(f"   USDT Available: ${capital['usdt_available']:.2f}")
    print(f"   Holdings Value: ${capital['holdings_value']:.2f}")
    print(f"   Open Orders: {capital['open_orders_count']}")

    print("\n📈 PORTFOLIO:")
    for sym, pos in portfolio["positions"].items():
        print(f"   • {sym}: ${pos['value']:.2f} ({pos['pnl_pct']:+.2f}%)")

    print("\n📝 OPEN ORDERS:")
    open_orders = await agent.client.get_open_orders()
    for order in open_orders:
        print(f"   • {order.get('symbol')}: {order.get('size')} @ {order.get('price')}")

    # Analyze ADI price action
    print("\n🔍 ADI PRICE ACTION ANALYSIS:")
    adi_ticker = await agent.client.get_ticker("ADI-USDT")
    print(f"   Current Price: ${adi_ticker.price:.6f}")
    order_book = await agent.client.get_orderbook("ADI-USDT", 20)

    # Calculate spread and depth
    best_bid = float(order_book.bids[0][0])
    best_ask = float(order_book.asks[0][0])
    spread_pct = ((best_ask - best_bid) / ((best_ask + best_bid) / 2)) * 100

    bid_depth = sum(float(bid[1]) for bid in order_book.bids)
    ask_depth = sum(float(ask[1]) for ask in order_book.asks)
    imbalance = (bid_depth - ask_depth) / (bid_depth + ask_depth)

    print(f"   Spread: {spread_pct:.3f}%")
    print(f"   Bid Depth: {bid_depth:.0f} ADI")
    print(f"   Ask Depth: {ask_depth:.0f} ADI")
    print(f"   Imbalance: {imbalance:.2f}")

    # Check ADI market intel
    await agent.analyze_market_intelligence()
    adi_intel = agent.market_intel.get("ADI", {})
    print(f"   Score: {adi_intel.get('score', 0):.1f}")
    print(f"   AGI Action: {adi_intel.get('agi_insight', '')}")

    # Calculate if current limit order will capture momentum
    limit_price = 2.6186
    current_price = adi_ticker.price

    distance_pct = ((current_price - limit_price) / current_price) * 100
    print(f"   Limit Order Distance: {distance_pct:.2f}% below market")

    print("\n=" * 80)
    print("🎯 PRICE ACTION STRATEGY IMPROVEMENTS")
    print("=" * 80)

    print("\n1️⃣ DYNAMIC LIMIT PRICING")
    print("   Current: Static 0.5% discount")
    print("   Improve: Dynamic discount based on volatility and order book strength")
    print("   • High volatility: 0.2% discount (capture momentum)")
    print("   • Moderate volatility: 0.5% discount (balanced)")
    print("   • Low volatility: 1.0% discount (wait for better price)")

    print("\n2️⃣ SCALED ENTRY STRATEGY")
    print("   Current: Single limit order")
    print("   Improve: Scale into positions with multiple limit orders")
    print("   • 60% at current price -0.3% (quick fill)")
    print("   • 30% at current price -0.8% (better price)")
    print("   • 10% at current price -1.5% (deep pullback)")

    print("\n3️⃣ MOMENTUM-BASED ENTRY TIMING")
    print("   Current: Based on spread and volatility")
    print("   Improve: Add momentum detection")
    print(
        "   • Strong upward momentum: Use market order or aggressive limit (0.1% discount)"
    )
    print("   • Pullback: Use larger discount (1.0%+)")
    print("   • Sideways: Wait for micro-momentum")

    print("\n4️⃣ REAL-TIME ORDER ADJUSTMENT")
    print("   Current: Static limit order")
    print("   Improve: Adjust limit price based on price action")
    print("   • If price pushes 0.5% above order: Cancel and place new limit at +0.2%")
    print("   • If price drops 1.0% below order: Keep but add to position")

    print("\n5️⃣ ORDER BOOK DYNAMICS")
    print("   Current: Simple imbalance check")
    print("   Improve: Analyze order flow")
    print("   • Large buy walls: Place limit just above wall")
    print("   • Large sell walls: Place limit just below wall")
    print("   • Whale activity: Follow large order direction")

    print("\n=" * 80)
    print("✅ STRATEGY VERIFICATION")
    print("=" * 80)

    print(f"\nCurrent Market Conditions: {agent.state['market_regime']}")
    print("Optimal Strategy for Current Conditions: MICRO_HUNTER")
    print("Recommended Action: Adjust ADI limit order to dynamic pricing")


asyncio.run(analyze_current_strategy())
