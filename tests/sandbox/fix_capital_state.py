#!/usr/bin/env python3
"""
Fix capital awareness state issue
The agent detects capital correctly but state file shows $0.00
"""

import asyncio
import json
import os
from ibis_true_agent import IBISTrueAgent


async def fix_capital_state():
    print("🔧 Fixing capital awareness state issue...")

    agent = IBISTrueAgent()
    await agent.initialize()

    print("\n=== INITIAL CAPITAL STATE ===")
    capital = agent.state["capital_awareness"]
    print(f"USDT Total: ${capital['usdt_total']:.2f}")
    print(f"USDT Available: ${capital['usdt_available']:.2f}")
    print(f"Holdings Value: ${capital['holdings_value']:.2f}")
    print(f"Total Assets: ${capital['total_assets']:.2f}")

    if capital["usdt_total"] == 0:
        print("\n❌ Capital state is incorrect - updating from exchange")

        # Force update capital awareness
        await agent.update_capital_awareness()

        print("\n=== AFTER FORCED UPDATE ===")
        capital = agent.state["capital_awareness"]
        print(f"USDT Total: ${capital['usdt_total']:.2f}")
        print(f"USDT Available: ${capital['usdt_available']:.2f}")
        print(f"Holdings Value: ${capital['holdings_value']:.2f}")
        print(f"Total Assets: ${capital['total_assets']:.2f}")

        # Save the fixed state
        agent._save_state()
        print("✅ State file updated with correct capital values")

    print("\n=== VERIFYING WITH EXCHANGE ===")
    balances = await agent.client.get_all_balances()
    usdt_balance = balances.get("USDT", {})
    print(f"Exchange USDT Balance: ${usdt_balance.get('balance', 0):.2f}")
    print(f"Exchange USDT Available: ${usdt_balance.get('available', 0):.2f}")

    # Verify positions
    print("\n=== POSITIONS VERIFICATION ===")
    portfolio = await agent.update_positions_awareness()
    for sym, pos in portfolio["positions"].items():
        print(f"{sym}: ${pos['current_price']:.6f} | {pos['pnl_pct']:+.2f}%")

    print(f"\nPortfolio Value: ${portfolio['total_value']:.2f}")
    print(f"PnL: ${portfolio['total_pnl']:.2f} ({portfolio['total_pnl_pct']:.2f}%)")


asyncio.run(fix_capital_state())
