#!/usr/bin/env python3
"""
Debug get_all_balances()
"""

import sys

sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader")
from ibis_true_agent import IBISTrueAgent
import asyncio


async def debug_balances():
    agent = IBISTrueAgent()
    await agent.initialize()

    print("💰 DEBUG GET ALL BALANCES")
    print("=" * 50)

    balances = await agent.client.get_all_balances()

    print("📊 Exchange Balances:")
    for currency, data in balances.items():
        if currency == "USDT":
            print(
                f"   💵 {currency}: Available={data['available']:.4f}, Balance={data['balance']:.4f}"
            )
        else:
            print(
                f"   📈 {currency}: Available={data['available']:.4f}, Balance={data['balance']:.4f}"
            )

    print(
        f"\n🎯 Holdings count: {len([c for c in balances.keys() if c != 'USDT' and float(balances.get(c, {}).get('balance', 0)) > 0])}"
    )

    await agent.analyze_market_intelligence()

    print(f"\n✅ Debug complete")


asyncio.run(debug_balances())
