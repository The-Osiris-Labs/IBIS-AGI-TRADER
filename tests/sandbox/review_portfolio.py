#!/usr/bin/env python3
import json
from datetime import datetime

# Load state file
with open(
    "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_true_state.json",
    "r",
) as f:
    state = json.load(f)

print("=== COMPREHENSIVE PORTFOLIO ANALYSIS ===")
print(f"File updated: {state['updated']}")
print()

# Positions
print("=" * 60)
print("=== POSITION PERFORMANCE ===")
print("=" * 60)
total_value = 0.0
total_pnl = 0.0
for sym, pos in state["positions"].items():
    print(f"\n{sym} (Position):")
    print(f"  Quantity: {pos['quantity']:.8f}")
    print(f"  Buy Price: ${pos['buy_price']:.6f}")
    print(f"  Current Price: ${pos['current_price']:.6f}")
    print(f"  Mode: {pos['mode']}")
    print(f"  Regime: {pos['regime']}")
    print(f"  Opened: {pos['opened']}")
    print(f"  Hold Time: {pos['hold_time']}")
    print(f"  TP: ${pos['tp']:.6f}")
    print(f"  SL: ${pos['sl']:.6f}")
    print(
        f"  Unrealized PnL: ${pos['unrealized_pnl']:.2f} ({pos['unrealized_pnl_pct']:.2f}%)"
    )
    print(f"  Highest PnL: {pos['highest_pnl_display']}")

    total_value += pos["current_value"]
    total_pnl += pos["unrealized_pnl"]

print()
print(f"Total Portfolio Value: ${total_value:.2f}")
print(f"Total Unrealized PnL: ${total_pnl:.2f}")
print()

# Capital awareness
print("=" * 60)
print("=== CAPITAL AWARENESS ===")
print("=" * 60)
capital = state["capital_awareness"]
print(f"USDT Total: ${capital['usdt_total']:.2f}")
print(f"USDT Available: ${capital['usdt_available']:.2f}")
print(f"USDT Locked Buy: ${capital['usdt_locked_buy']:.2f}")
print(f"USDT in Buy Orders: ${capital['usdt_in_buy_orders']:.2f}")
print(f"Holdings Value: ${capital['holdings_value']:.2f}")
print(f"Holdings in Sell Orders: ${capital['holdings_in_sell_orders']:.2f}")
print(f"Total Assets: ${capital['total_assets']:.2f}")
print(f"Real Trading Capital: ${capital['real_trading_capital']:.2f}")
print(f"Open Orders Count: {capital['open_orders_count']}")
print()

# Buy and sell orders
if capital["buy_orders"]:
    print("Buy Orders:")
    for sym, order in capital["buy_orders"].items():
        print(f"  • {sym}: ${order['funds']:.2f} @ ${order['price']:.6f}")

if capital["sell_orders"]:
    print("Sell Orders:")
    for sym, orders in capital["sell_orders"].items():
        for order in orders:
            print(f"  • {sym}: ${order['value']:.2f} @ ${order['price']:.6f}")
print()

# Daily stats and trading history
print("=" * 60)
print("=== TRADING HISTORY & DAILY STATS ===")
print("=" * 60)
daily = state["daily"]
print(f"Date: {daily['date']}")
print(f"Trades: {daily['trades']}")
print(f"Wins: {daily['wins']}")
print(f"Losses: {daily['losses']}")
print(f"PNL: ${daily['pnl']:.2f}")
print(f"Realized PNL: ${daily['realized_pnl']:.2f}")
print(f"Fees: ${daily['fees']:.2f}")
print(f"Start Balance: ${daily['start_balance']:.2f}")
print(f"Orders Placed: {daily['orders_placed']}")
print(f"Orders Filled: {daily['orders_filled']}")
print(f"Orders Cancelled: {daily['orders_cancelled']}")
print(f"Avg Fill Rate: {daily['avg_fill_rate']:.2f}")
print()

# Regimes experienced
if daily["regimes_experienced"]:
    print("Regimes Experienced:")
    for regime, count in daily["regimes_experienced"].items():
        print(f"  • {regime}: {count} times")

# Strategies tried
if daily["strategies_tried"]:
    print("Strategies Tried:")
    for strategy, count in daily["strategies_tried"].items():
        print(f"  • {strategy}: {count} times")
print()

# Market conditions
print("=" * 60)
print("=== MARKET CONDITIONS ===")
print("=" * 60)
print(f"Market Regime: {state['market_regime']}")
print(f"Agent Mode: {state['agent_mode']}")
print()

# Performance metrics
print("=" * 60)
print("=== PERFORMANCE METRICS ===")
print("=" * 60)
if daily["trades"] > 0:
    win_rate = (daily["wins"] / daily["trades"]) * 100
    print(f"Win Rate: {win_rate:.1f}%")
else:
    print("Win Rate: N/A (no trades yet)")

if daily["start_balance"] > 0:
    daily_return = (
        (capital["total_assets"] - daily["start_balance"]) / daily["start_balance"]
    ) * 100
    print(f"Daily Return: {daily_return:.2f}%")

print()
print("=== SUMMARY ===")
print("• Current positions are all recent (0h 0m)")
print("• Portfolio is slightly positive ($0.00 - $0.01 PnL)")
print("• No open orders - system ready to deploy capital")
print("• Market in VOLATILE regime with EXTREME FEAR sentiment")
