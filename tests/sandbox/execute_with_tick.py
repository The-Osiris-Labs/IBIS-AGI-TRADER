#!/usr/bin/env python3
"""
Execute trade with proper tick size calculation
"""

import asyncio
from ibis_true_agent import IBISTrueAgent


async def execute_trade():
    print("🎯 Executing trade with proper tick size")
    agent = IBISTrueAgent()
    await agent.initialize()

    await agent.update_capital_awareness()
    capital = agent.state["capital_awareness"]
    print(f"Capital: ${capital['usdt_available']:.2f} available")

    await agent.analyze_market_intelligence()
    opportunities = []
    for symbol, intel in sorted(
        agent.market_intel.items(), key=lambda x: x[1].get("score", 0), reverse=True
    ):
        score = intel.get("score", 0)
        if score >= 80:
            opportunities.append((symbol, score))

    print(f"High-quality opportunities: {len(opportunities)}")

    if opportunities:
        best_symbol, best_score = opportunities[0]
        print(f"Best opportunity: {best_symbol} (Score: {best_score:.1f})")

        if best_symbol not in agent.state["positions"]:
            print(f"{best_symbol} not in positions - eligible to trade")

            # Get tick size for symbol
            symbol_info = await agent.client.get_symbol_info(f"{best_symbol}-USDT")
            print(f"Symbol info for {best_symbol}-USDT:")
            print(f"  Price increment: {symbol_info['priceIncrement']}")
            print(f"  Size increment: {symbol_info['baseIncrement']}")

            position_size = min(capital["usdt_available"] * 0.25, 30)
            ticker = await agent.client.get_ticker(f"{best_symbol}-USDT")
            current_price = ticker.price
            quantity = position_size / current_price

            print(f"Calculated: ${position_size:.2f} → {quantity:.8f} {best_symbol}")

            # Adjust price to valid tick increment
            price_increment = float(symbol_info["priceIncrement"])
            limit_price = current_price * 0.995
            # Round to nearest valid increment
            valid_price = round(limit_price / price_increment) * price_increment

            # Adjust quantity to valid size increment
            size_increment = float(symbol_info["baseIncrement"])
            valid_quantity = round(quantity / size_increment) * size_increment

            print(f"Adjusted to tick size: ${valid_price:.6f} | {valid_quantity:.8f}")

            try:
                order = await agent.client.create_limit_order(
                    symbol=f"{best_symbol}-USDT",
                    side="buy",
                    price=valid_price,
                    size=valid_quantity,
                )
                print("✅ TRADE EXECUTED!")
                print(f"Order ID: {order.order_id}")
                print(f"Symbol: {best_symbol}-USDT")
                print(f"Price: ${valid_price:.6f}")
                print(f"Quantity: {valid_quantity:.8f}")
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback

                print(traceback.format_exc())
        else:
            print(f"{best_symbol} already in positions")


asyncio.run(execute_trade())
