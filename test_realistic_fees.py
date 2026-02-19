#!/usr/bin/env python3
"""
Test script to verify realistic transaction cost calculations
"""

import sys
import os

sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader")

from ibis.core.risk_manager import RiskManager
from ibis.core.trading_constants import TRADING

print("=== Realistic Transaction Cost Calculation Test ===")
print()

# Create instance
risk_manager = RiskManager()

# Test 1: ETH transaction
print("1. Testing ETH transaction costs:")
print("   Quantity: 2 ETH")
print("   Entry Price: $2500")
print("   Exit Price: $2600")

try:
    symbol = "ETH"
    quantity = 2
    entry_price = 2500
    exit_price = 2600

    # Get fee rates
    fee_rates = risk_manager._get_fee_rates(symbol)
    entry_fee = quantity * entry_price * fee_rates["maker"]
    exit_fee = quantity * exit_price * fee_rates["taker"]
    total_costs = (
        entry_fee + exit_fee + (quantity * entry_price * TRADING.EXCHANGE.ESTIMATED_SLIPPAGE)
    )

    # Calculate PnL
    gross_pnl = quantity * (exit_price - entry_price)
    net_pnl = gross_pnl - total_costs

    print(f"   Entry Fee: ${entry_fee:.4f} ({fee_rates['maker'] * 100:.4f}%)")
    print(f"   Exit Fee: ${exit_fee:.4f} ({fee_rates['taker'] * 100:.4f}%)")
    print(
        f"   Slippage: ${quantity * entry_price * TRADING.EXCHANGE.ESTIMATED_SLIPPAGE:.4f} ({TRADING.EXCHANGE.ESTIMATED_SLIPPAGE * 100:.4f}%)"
    )
    print(
        f"   Total Costs: ${total_costs:.4f} ({total_costs / (quantity * entry_price) * 100:.4f}%)"
    )
    print(f"   Gross PnL: ${gross_pnl:.2f}")
    print(f"   Net PnL: ${net_pnl:.2f}")

    # Verify fee rates are realistic
    assert fee_rates["maker"] <= 0.001, f"Maker fee {fee_rates['maker'] * 100:.4f}% is too high"
    assert fee_rates["taker"] <= 0.001, f"Taker fee {fee_rates['taker'] * 100:.4f}% is too high"

except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback

    traceback.print_exc()

print()

# Test 2: BTC transaction
print("2. Testing BTC transaction costs:")
print("   Quantity: 0.1 BTC")
print("   Entry Price: $50000")
print("   Exit Price: $55000")

try:
    symbol = "BTC"
    quantity = 0.1
    entry_price = 50000
    exit_price = 55000

    # Get fee rates
    fee_rates = risk_manager._get_fee_rates(symbol)
    entry_fee = quantity * entry_price * fee_rates["maker"]
    exit_fee = quantity * exit_price * fee_rates["taker"]
    total_costs = (
        entry_fee + exit_fee + (quantity * entry_price * TRADING.EXCHANGE.ESTIMATED_SLIPPAGE)
    )

    # Calculate PnL
    gross_pnl = quantity * (exit_price - entry_price)
    net_pnl = gross_pnl - total_costs

    print(f"   Entry Fee: ${entry_fee:.4f} ({fee_rates['maker'] * 100:.4f}%)")
    print(f"   Exit Fee: ${exit_fee:.4f} ({fee_rates['taker'] * 100:.4f}%)")
    print(
        f"   Slippage: ${quantity * entry_price * TRADING.EXCHANGE.ESTIMATED_SLIPPAGE:.4f} ({TRADING.EXCHANGE.ESTIMATED_SLIPPAGE * 100:.4f}%)"
    )
    print(
        f"   Total Costs: ${total_costs:.4f} ({total_costs / (quantity * entry_price) * 100:.4f}%)"
    )
    print(f"   Gross PnL: ${gross_pnl:.2f}")
    print(f"   Net PnL: ${net_pnl:.2f}")

    # Verify fee rates are realistic
    assert fee_rates["maker"] <= 0.001, f"Maker fee {fee_rates['maker'] * 100:.4f}% is too high"
    assert fee_rates["taker"] <= 0.001, f"Taker fee {fee_rates['taker'] * 100:.4f}% is too high"

except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback

    traceback.print_exc()

print()

# Test 3: BNB transaction
print("3. Testing BNB transaction costs:")
print("   Quantity: 5 BNB")
print("   Entry Price: $350")
print("   Exit Price: $380")

try:
    symbol = "BNB"
    quantity = 5
    entry_price = 350
    exit_price = 380

    # Get fee rates
    fee_rates = risk_manager._get_fee_rates(symbol)
    entry_fee = quantity * entry_price * fee_rates["maker"]
    exit_fee = quantity * exit_price * fee_rates["taker"]
    total_costs = (
        entry_fee + exit_fee + (quantity * entry_price * TRADING.EXCHANGE.ESTIMATED_SLIPPAGE)
    )

    # Calculate PnL
    gross_pnl = quantity * (exit_price - entry_price)
    net_pnl = gross_pnl - total_costs

    print(f"   Entry Fee: ${entry_fee:.4f} ({fee_rates['maker'] * 100:.4f}%)")
    print(f"   Exit Fee: ${exit_fee:.4f} ({fee_rates['taker'] * 100:.4f}%)")
    print(
        f"   Slippage: ${quantity * entry_price * TRADING.EXCHANGE.ESTIMATED_SLIPPAGE:.4f} ({TRADING.EXCHANGE.ESTIMATED_SLIPPAGE * 100:.4f}%)"
    )
    print(
        f"   Total Costs: ${total_costs:.4f} ({total_costs / (quantity * entry_price) * 100:.4f}%)"
    )
    print(f"   Gross PnL: ${gross_pnl:.2f}")
    print(f"   Net PnL: ${net_pnl:.2f}")

    # Verify fee rates are realistic
    assert fee_rates["maker"] <= 0.001, f"Maker fee {fee_rates['maker'] * 100:.4f}% is too high"
    assert fee_rates["taker"] <= 0.001, f"Taker fee {fee_rates['taker'] * 100:.4f}% is too high"

except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback

    traceback.print_exc()

print()

# Test 4: Verify TRADING constants
print("4. TRADING Exchange Configuration:")
print(f"   Default Maker Fee: {TRADING.EXCHANGE.MAKER_FEE * 100:.4f}%")
print(f"   Default Taker Fee: {TRADING.EXCHANGE.TAKER_FEE * 100:.4f}%")
print(f"   Slippage: {TRADING.EXCHANGE.ESTIMATED_SLIPPAGE * 100:.4f}%")
print(f"   Total Friction: {TRADING.EXCHANGE.get_total_friction() * 100:.4f}%")

print()
print("=== Test Completed ===")
