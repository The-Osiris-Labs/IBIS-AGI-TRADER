#!/usr/bin/env python3
"""
IBIS Position Rotation Test Script
=================================
Test the rotation system independently.
"""

import asyncio
import sys

sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader")

from ibis.position_rotation import PositionRotationManager, run_rotation_cycle
from ibis.database.db import IbisDB


async def test_rotation():
    print("=" * 60)
    print("🦅 IBIS POSITION ROTATION TEST")
    print("=" * 60)

    # Get portfolio summary before
    db = IbisDB()
    positions_before = db.get_open_positions()
    print(f"\n📊 Positions BEFORE: {len(positions_before)}")

    for pos in positions_before:
        print(
            f"   {pos['symbol']}: {pos['quantity']:.4f} @ ${pos.get('entry_price', 0):.4f}"
        )

    # Run rotation
    print("\n🔄 RUNNING ROTATION...")
    results, summary = await run_rotation_cycle()

    print("\n" + "=" * 60)
    print("📊 ROTATION RESULTS")
    print("=" * 60)

    print(f"\n✅ SOLD (TP): {results['sold_tp'] if results['sold_tp'] else 'None'}")
    print(f"❌ SOLD (SL): {results['sold_sl'] if results['sold_sl'] else 'None'}")
    print(
        f"🔄 SOLD (STALE): {results['sold_stale'] if results['sold_stale'] else 'None'}"
    )
    print(
        f"🧹 CONSOLIDATED: {results['consolidated'] if results['consolidated'] else 'None'}"
    )
    print(f"\n💰 Total PnL: ${results['total_realized_pnl']:+.4f}")
    print(f"💵 Capital Freed: ${results['capital_freed']:.2f}")
    print(f"📊 Trades Executed: {results['trades_executed']}")

    print("\n" + "=" * 60)
    print("📊 PORTFOLIO SUMMARY")
    print("=" * 60)

    print(f"Positions: {summary['positions_count']}")
    print(f"Winners: {summary['winners']} | Losers: {summary['losers']}")
    print(f"Total Value: ${summary['total_value']:.2f}")
    print(f"Total PnL: ${summary['total_pnl']:+.4f}")
    print(f"Available USDT: ${summary['available_usdt']:.2f}")
    print(f"Total Portfolio: ${summary['total_portfolio_value']:.2f}")

    print("\n📈 TOP POSITIONS:")
    for pos in summary["positions"][:5]:
        pnl_emoji = "🟢" if pos["pnl"] >= 0 else "🔴"
        print(
            f"   {pnl_emoji} {pos['symbol']}: ${pos['value']:.2f} ({pos['pnl_pct']:+.2f}%)"
        )

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(test_rotation())
