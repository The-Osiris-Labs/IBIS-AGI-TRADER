#!/usr/bin/env python3
import asyncio
from ibis_true_agent import IBISTrueAgent


async def update_positions():
    agent = IBISTrueAgent()
    await agent.initialize()
    await agent.update_positions_awareness()
    await agent.update_capital_awareness()

    # Print position details
    print("=== UPDATED POSITION DETAILS ===")
    portfolio = await agent.update_positions_awareness()
    for sym, pos in portfolio["positions"].items():
        print(f"\n{sym}:")
        print(f"  Quantity: {pos['quantity']:.8f}")
        print(f"  Entry: ${pos['entry_price']:.6f}")
        print(f"  Current: ${pos['current_price']:.6f}")
        print(f"  Value: ${pos['value']:.2f}")
        print(f"  PnL: ${pos['pnl']:.2f} ({pos['pnl_pct']:.2f}%)")
        print(f"  Hold Time: {pos['hold_time']}")


asyncio.run(update_positions())
