#!/usr/bin/env python3
import asyncio
from ibis_true_agent import IBISTrueAgent


async def check_open_order():
    agent = IBISTrueAgent()
    await agent.initialize()

    print("=== CHECKING OPEN ORDERS ===")
    open_orders = await agent.client.get_open_orders()
    print(f"Total open orders: {len(open_orders)}")

    if open_orders:
        for order in open_orders:
            print()
            print(f"Symbol: {order.symbol}")
            print(f"Side: {order.side}")
            print(f"Type: {order.type}")
            print(f"Price: ${order.price}")
            print(f"Size: {order.size}")
            print(f"Status: {order.status}")
            print(f"Order ID: {order.order_id}")

    print()
    print("=== PORTFOLIO STATUS ===")
    await agent.update_capital_awareness()
    capital = agent.state["capital_awareness"]
    print(f"USDT Available: ${capital['usdt_available']:.2f}")
    print(f"USDT Locked in Buy Orders: ${capital['usdt_locked_buy']:.2f}")
    print(f"Holdings Value: ${capital['holdings_value']:.2f}")
    print(f"Total Assets: ${capital['total_assets']:.2f}")

    # Check position awareness
    portfolio = await agent.update_positions_awareness()
    print()
    print("=== CURRENT POSITIONS ===")
    for symbol, pos in portfolio["positions"].items():
        print(f"{symbol}:")
        print(f"  Quantity: {pos['quantity']:.8f}")
        print(f"  Entry Price: ${pos['entry_price']:.6f}")
        print(f"  Current Price: ${pos['current_price']:.6f}")
        print(f"  PnL: ${pos['pnl']:.2f} ({pos['pnl_pct']:.2f}%)")
        print()


asyncio.run(check_open_order())
