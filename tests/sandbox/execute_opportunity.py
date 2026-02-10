#!/usr/bin/env python3
"""
Direct opportunity execution script
Executes on high-quality opportunities with unused capital
"""

import asyncio
from ibis_true_agent import IBISTrueAgent


async def execute_opportunity():
    print("🎯 Direct opportunity execution script")
    print("=" * 60)

    agent = IBISTrueAgent()
    await agent.initialize()

    print("\n=== AGENT STATUS ===")
    print(f"Market Regime: {agent.state['market_regime']}")
    print(f"Agent Mode: {agent.state['agent_mode']}")
    print(f"Positions: {len(agent.state['positions'])}")

    print("\n=== CAPITAL ===")
    capital = agent.state["capital_awareness"]
    print(f"USDT Total: ${capital['usdt_total']:.2f}")
    print(f"USDT Available: ${capital['usdt_available']:.2f}")
    print(f"Holdings Value: ${capital['holdings_value']:.2f}")
    print(f"Total Assets: ${capital['total_assets']:.2f}")

    print("\n=== ANALYZING MARKET INTELLIGENCE ===")
    await agent.analyze_market_intelligence()

    # Find best opportunities
    print("\n=== TOP OPPORTUNITIES ===")
    opportunities = []
    for symbol, intel in sorted(
        agent.market_intel.items(), key=lambda x: x[1].get("score", 0), reverse=True
    ):
        score = intel.get("score", 0)
        if score >= 80:
            opportunities.append((symbol, score))

    for i, (symbol, score) in enumerate(opportunities[:5], 1):
        print(f"{i}. {symbol}: {score:.1f}")

    if not opportunities:
        print("❌ No opportunities with score ≥80 found")
        return

    print("\n=== SELECTING BEST OPPORTUNITY ===")
    best_symbol, best_score = opportunities[0]
    print(f"Best opportunity: {best_symbol} (Score: {best_score:.1f})")

    # Check if symbol is already in positions
    if best_symbol in agent.state["positions"]:
        print(f"ℹ️ {best_symbol} already in positions - checking next opportunity")
        if len(opportunities) > 1:
            best_symbol, best_score = opportunities[1]
            print(f"Next best: {best_symbol} (Score: {best_score:.1f})")
        else:
            print("❌ No more opportunities available")
            return

    print("\n=== EXECUTING TRADE ===")

    try:
        # Calculate position size (25% of available capital, max $30)
        position_size = min(capital["usdt_available"] * 0.25, 30)
        print(f"Position size: ${position_size:.2f}")

        # Get current price
        ticker = await agent.client.get_ticker(f"{best_symbol}-USDT")
        current_price = ticker.price
        print(f"Current price: ${current_price:.6f}")

        quantity = position_size / current_price
        print(f"Quantity: {quantity:.8f} {best_symbol}")

        # Place limit order with 0.5% discount
        limit_price = current_price * 0.995
        print(f"Limit price: ${limit_price:.6f}")

        # Execute order
        order = await agent.client.create_limit_order(
            symbol=f"{best_symbol}-USDT", side="buy", price=limit_price, size=quantity
        )

        print(f"\n✅ TRADE EXECUTED SUCCESSFULLY!")
        print(f"Order ID: {order.order_id}")
        print(f"Symbol: {best_symbol}-USDT")
        print(f"Side: BUY")
        print(f"Price: ${limit_price:.6f}")
        print(f"Quantity: {quantity:.8f}")
        print(f"Total: ${position_size:.2f}")

        # Refresh capital awareness
        await agent.update_capital_awareness()
        print(f"\nNew Capital Status:")
        new_capital = agent.state["capital_awareness"]
        print(f"USDT Available: ${new_capital['usdt_available']:.2f}")
        print(f"Holdings Value: ${new_capital['holdings_value']:.2f}")
        print(f"Total Assets: ${new_capital['total_assets']:.2f}")

    except Exception as e:
        print(f"\n❌ TRADE EXECUTION FAILED")
        print(f"Error: {e}")
        import traceback

        print(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(execute_opportunity())
