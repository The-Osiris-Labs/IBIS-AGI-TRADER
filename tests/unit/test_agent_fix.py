#!/usr/bin/env python3
import asyncio
from ibis_true_agent import IBISTrueAgent


async def test_agent():
    agent = IBISTrueAgent()
    await agent.initialize()

    print("=== INITIAL STATE ===")
    print(f"Market Regime: {agent.state['market_regime']}")
    print(f"Agent Mode: {agent.state['agent_mode']}")
    print(f"Positions: {len(agent.state['positions'])}")

    # Update capital awareness
    print("\n=== UPDATE CAPITAL AWARENESS ===")
    await agent.update_capital_awareness()
    capital = agent.state["capital_awareness"]
    print(f"USDT Total: ${capital['usdt_total']:.2f}")
    print(f"USDT Available: ${capital['usdt_available']:.2f}")
    print(f"Holdings Value: ${capital['holdings_value']:.2f}")
    print(f"Total Assets: ${capital['total_assets']:.2f}")
    print(f"Real Trading Capital: ${capital['real_trading_capital']:.2f}")

    # Update positions
    print("\n=== UPDATE POSITIONS ===")
    portfolio = await agent.update_positions_awareness()
    print(f"Portfolio Value: ${portfolio['total_value']:.2f}")
    print(
        f"Portfolio PnL: ${portfolio['total_pnl']:.2f} ({portfolio['total_pnl_pct']:.2f}%)"
    )

    print("\n=== POSITION DETAILS ===")
    for sym, pos in portfolio["positions"].items():
        print(f"{sym}:")
        print(f"  Quantity: {pos['quantity']:.8f}")
        print(f"  Entry: ${pos['entry_price']:.6f}")
        print(f"  Current: ${pos['current_price']:.6f}")
        print(f"  Value: ${pos['value']:.2f}")
        print(f"  PnL: ${pos['pnl']:.2f} ({pos['pnl_pct']:.2f}%)")
        print()


asyncio.run(test_agent())
