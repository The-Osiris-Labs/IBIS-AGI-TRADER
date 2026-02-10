#!/usr/bin/env python3
"""
Analyze capital allocation
"""

import sys

sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader")
from ibis_true_agent import IBISTrueAgent
from ibis.core.trading_constants import TRADING
import asyncio


async def analyze_capital_allocation():
    agent = IBISTrueAgent()
    await agent.initialize()

    print("💰 CAPITAL ALLOCATION ANALYSIS")
    print("=" * 50)

    capital = agent.state["capital_awareness"]
    positions = agent.state["positions"]

    print(f"Total Assets:        ${capital.get('total_assets', 0):.2f}")
    print(f"USDT Available:      ${capital.get('usdt_available', 0):.2f}")
    print(f"USDT Locked Buy:     ${capital.get('usdt_locked_buy', 0):.2f}")
    print(f"Holdings Value:      ${capital.get('holdings_value', 0):.2f}")
    print(
        f"Total Locked:        ${capital.get('usdt_locked_buy', 0) + capital.get('holdings_value', 0):.2f}"
    )
    print(
        f"Availability Ratio:  {capital.get('usdt_available', 0) / capital.get('total_assets', 1) * 100:.1f}%"
    )
    print()

    print("🎯 POSITION SIZING CONSTRAINTS")
    print("=" * 50)
    print(f"Min per trade:       ${TRADING.POSITION.MIN_CAPITAL_PER_TRADE:.0f}")
    print(f"Max per trade:       ${TRADING.POSITION.MAX_CAPITAL_PER_TRADE:.0f}")
    print(f"Max position %:      {TRADING.POSITION.MAX_POSITION_PCT:.1f}%")
    print(f"Base position %:     {TRADING.POSITION.BASE_POSITION_PCT:.1f}%")
    print(f"Max total positions: {TRADING.POSITION.MAX_TOTAL_POSITIONS}")
    print()

    standard_size = TRADING.get_standard_position_size(capital.get("usdt_available", 0))
    print(f"Standard Position Size: ${standard_size:.2f}")

    available_risk = capital.get("total_assets", 0) * TRADING.RISK.MAX_PORTFOLIO_RISK
    current_risk = sum(pos.get("current_value", 0) for pos in positions.values())
    remaining_risk = available_risk - current_risk
    print(f"Available Risk Budget: ${available_risk:.2f}")
    print(f"Current Risk Used: ${current_risk:.2f}")
    print(f"Remaining Risk: ${remaining_risk:.2f}")


asyncio.run(analyze_capital_allocation())
