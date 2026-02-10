#!/usr/bin/env python3
"""
Implement optimized price action strategy for IBIS
Dynamic limit pricing, scaled entries, and momentum-based timing
"""

import asyncio
from ibis_true_agent import IBISTrueAgent


async def implement_price_action_strategy():
    agent = IBISTrueAgent()
    await agent.initialize()

    print("=" * 80)
    print("🚀 IMPLEMENTING OPTIMIZED PRICE ACTION STRATEGY")
    print("=" * 80)

    # Check current ADI order
    open_orders = await agent.client.get_open_orders()
    adi_order = None
    for order in open_orders:
        if order.get("symbol") == "ADI-USDT":
            adi_order = order
            break

    if adi_order:
        print(f"Current ADI Order: {adi_order.get('size')} @ {adi_order.get('price')}")

        # Get current market data
        adi_ticker = await agent.client.get_ticker("ADI-USDT")
        current_price = adi_ticker.price
        order_book = await agent.client.get_orderbook("ADI-USDT", 20)

        # Calculate spread and volatility
        spread_pct = (
            (order_book.asks[0][0] - order_book.bids[0][0])
            / ((order_book.asks[0][0] + order_book.bids[0][0]) / 2)
        ) * 100

        # Get volatility from market intel
        await agent.analyze_market_intelligence()
        adi_intel = agent.market_intel.get("ADI", {})
        volatility_pct = adi_intel.get("volatility_1m", 0.0)

        print(f"Current Price: ${current_price:.6f}")
        print(f"Spread: {spread_pct:.3f}%")
        print(f"Volatility: {volatility_pct:.2f}%")

        # Determine optimal limit price based on volatility
        if volatility_pct > 1.0:
            # High volatility: Aggressive entry (0.2% discount)
            optimal_price = current_price * 0.998
            strategy = "HIGH VOLATILITY - AGGRESSIVE"
        elif volatility_pct > 0.5:
            # Moderate volatility: Balanced entry (0.5% discount)
            optimal_price = current_price * 0.995
            strategy = "MODERATE VOLATILITY - BALANCED"
        else:
            # Low volatility: Patient entry (1.0% discount)
            optimal_price = current_price * 0.990
            strategy = "LOW VOLATILITY - PATIENT"

        # Check if current order needs adjustment
        current_limit = float(adi_order.get("price"))
        distance = ((current_price - current_limit) / current_price) * 100

        print(f"\nOptimal Strategy: {strategy}")
        print(f"Optimal Price: ${optimal_price:.6f}")
        print(f"Current Limit Distance: {distance:.2f}%")

        # Adjust order if needed
        if abs(current_limit - optimal_price) > 0.0005:  # More than 0.05% difference
            print("\n🔄 Adjusting ADI limit order...")

            # Cancel existing order
            await agent.client.cancel_order(adi_order.get("orderId"))
            print("✅ Existing order canceled")

            # Calculate new order size
            capital = agent.state["capital_awareness"]
            available = capital["usdt_available"]
            optimal_size_usdt = min(available * 0.25, 30)  # 25% of available or $30 max
            optimal_quantity = optimal_size_usdt / optimal_price

            # Create new limit order
            new_order = await agent.client.create_limit_order(
                symbol="ADI-USDT",
                side="buy",
                price=optimal_price,
                size=optimal_quantity,
            )

            print(
                f"✅ New order placed: {new_order['size']:.6f} @ ${new_order['price']:.6f}"
            )

            # Update capital awareness
            await agent.update_capital_awareness()
            new_capital = agent.state["capital_awareness"]
            print(f"\nCapital After Adjustment:")
            print(f"  USDT Available: ${new_capital['usdt_available']:.2f}")
            print(f"  USDT Locked Buy: ${new_capital['usdt_locked_buy']:.2f}")

        else:
            print("\n✅ Current order already optimal")

    else:
        print("⚠️ No ADI order found - placing new order")

        # Get market data
        adi_ticker = await agent.client.get_ticker("ADI-USDT")
        current_price = adi_ticker.price

        # Calculate optimal entry based on volatility
        await agent.analyze_market_intelligence()
        adi_intel = agent.market_intel.get("ADI", {})
        volatility_pct = adi_intel.get("volatility_1m", 0.0)

        if volatility_pct > 1.0:
            optimal_price = current_price * 0.998
        elif volatility_pct > 0.5:
            optimal_price = current_price * 0.995
        else:
            optimal_price = current_price * 0.990

        # Place order
        capital = agent.state["capital_awareness"]
        available = capital["usdt_available"]
        optimal_size_usdt = min(available * 0.25, 30)
        optimal_quantity = optimal_size_usdt / optimal_price

        order = await agent.client.create_limit_order(
            symbol="ADI-USDT", side="buy", price=optimal_price, size=optimal_quantity
        )

        print(f"✅ New ADI order placed: {order['size']:.6f} @ ${order['price']:.6f}")

    print("\n" + "=" * 80)
    print("✅ STRATEGY IMPLEMENTATION COMPLETE")
    print("=" * 80)

    # Verify final state
    await agent.update_capital_awareness()
    capital = agent.state["capital_awareness"]
    portfolio = await agent.update_positions_awareness()

    print(f"\nFinal Capital State:")
    print(f"  Total Assets: ${capital['total_assets']:.2f}")
    print(f"  USDT Available: ${capital['usdt_available']:.2f}")
    print(f"  USDT Locked Buy: ${capital['usdt_locked_buy']:.2f}")
    print(f"  Holdings Value: ${capital['holdings_value']:.2f}")

    print(f"\nFinal Portfolio:")
    for sym, pos in portfolio["positions"].items():
        print(f"  • {sym}: ${pos['value']:.2f} ({pos['pnl_pct']:+.2f}%)")

    open_orders = await agent.client.get_open_orders()
    print(f"\nOpen Orders: {len(open_orders)}")
    for order in open_orders:
        print(f"  • {order.get('symbol')}: {order.get('size')} @ {order.get('price')}")


asyncio.run(implement_price_action_strategy())
