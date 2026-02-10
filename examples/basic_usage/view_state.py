#!/usr/bin/env python3
"""
View current IBIS state

Shows current positions, portfolio value, market regime, and recent activity.
"""

from ibis.data_consolidation import load_state
import json
from datetime import datetime

def main():
    state = load_state()
    
    print("\n" + "="*70)
    print("🦅 IBIS CURRENT STATE")
    print("="*70)
    
    # Portfolio overview
    print("\n💰 PORTFOLIO OVERVIEW:")
    capital = state.get('capital_awareness', {})
    print(f"   Total Assets:       ${capital.get('usdt_total', 0):.2f}")
    print(f"   Available (USDT):   ${capital.get('usdt_available', 0):.2f}")
    print(f"   Locked in Orders:   ${capital.get('usdt_locked_buy', 0):.2f}")
    print(f"   Holdings Value:     ${capital.get('holdings_value', 0):.2f}")
    
    # Active positions
    print("\n🎯 ACTIVE POSITIONS:")
    positions = state.get('positions', {})
    if positions:
        for symbol, pos in positions.items():
            value = pos.get('quantity', 0) * pos.get('current_price', 0)
            pnl = pos.get('unrealized_pnl_pct', 0)
            print(f"   {symbol:12} {pos.get('quantity', 0):>12.8f} @ ${pos.get('current_price', 0):.8f}")
            print(f"               Value: ${value:.2f} | PnL: {pnl:+.2f}%")
    else:
        print("   (No active positions)")
    
    # Market conditions
    print("\n⚡ MARKET CONDITIONS:")
    print(f"   Current Regime:     {state.get('market_regime', 'UNKNOWN')}")
    print(f"   Agent Mode:         {state.get('agent_mode', 'UNKNOWN')}")
    
    # Daily stats
    print("\n📊 TODAY'S ACTIVITY:")
    daily = state.get('daily', {})
    print(f"   Trades:            {daily.get('trades', 0)}")
    print(f"   Wins:              {daily.get('wins', 0)}")
    print(f"   Losses:            {daily.get('losses', 0)}")
    print(f"   Daily P&L:         ${daily.get('pnl', 0):+.2f}")
    
    # Pending orders
    print("\n📋 PENDING ORDERS:")
    buy_orders = capital.get('buy_orders', {})
    sell_orders = capital.get('sell_orders', {})
    
    if buy_orders:
        print("   Buy Orders:")
        for symbol, order in buy_orders.items():
            print(f"      {symbol}: {order.get('size', 0):.8f} @ ${order.get('price', 0):.8f}")
    else:
        print("   (No buy orders)")
    
    if sell_orders:
        print("   Sell Orders:")
        for symbol, order in sell_orders.items():
            print(f"      {symbol}: {order.get('size', 0):.8f} @ ${order.get('price', 0):.8f}")
    else:
        print("   (No sell orders)")
    
    # Last update
    print(f"\n⏱️  Last Updated: {state.get('updated', 'Unknown')}")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
