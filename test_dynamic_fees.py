#!/usr/bin/env python3
"""
Test script for dynamic fee calculation system
"""

# Test dynamic fee calculation system
from ibis.pnl_tracker import PnLTracker
from ibis.core.trading_constants import TRADING
from ibis.database.db import IbisDB

print("=== Dynamic Fee Calculation System Test ===")

# Test 1: Check if we can create instances
print("\n1. Creating instances...")
tracker = PnLTracker()
db = IbisDB()
print("✓ PnLTracker instance created")
print("✓ IbisDB instance created")

# Test 2: Check if TRADING constants support dynamic fees
print("\n2. Testing TRADING constants...")
print(f"Default maker fee: {TRADING.EXCHANGE.MAKER_FEE:.4%}")
print(f"Default taker fee: {TRADING.EXCHANGE.TAKER_FEE:.4%}")
print(f"Symbol fee rates initially empty: {TRADING.EXCHANGE.symbol_fee_rates}")

# Test 3: Update symbol fees
print("\n3. Testing symbol fee update...")
TRADING.EXCHANGE.update_symbol_fees("BTC", 0.0008, 0.0012)
TRADING.EXCHANGE.update_symbol_fees("ETH", 0.0007, 0.0011)
print(f"Symbol fee rates: {TRADING.EXCHANGE.symbol_fee_rates}")
print(f"BTC maker fee: {TRADING.EXCHANGE.get_maker_fee('BTC'):.4%}")
print(f"BTC taker fee: {TRADING.EXCHANGE.get_taker_fee('BTC'):.4%}")
print(f"ETH maker fee: {TRADING.EXCHANGE.get_maker_fee('ETH'):.4%}")
print(f"ETH taker fee: {TRADING.EXCHANGE.get_taker_fee('ETH'):.4%}")

# Test 4: Get average fees
print("\n4. Testing average fees calculation...")
avg_fees = TRADING.EXCHANGE.get_average_fees()
print(f"Average maker fee: {avg_fees['maker']:.4%}")
print(f"Average taker fee: {avg_fees['taker']:.4%}")

# Test 5: Get fees for unknown symbol
print("\n5. Testing unknown symbol fees...")
print(f"Unknown symbol (SOL) maker fee: {TRADING.EXCHANGE.get_maker_fee('SOL'):.4%}")
print(f"Unknown symbol (SOL) taker fee: {TRADING.EXCHANGE.get_taker_fee('SOL'):.4%}")

# Test 6: Test database fee methods
print("\n6. Testing database fee methods...")
db_fees = db.get_average_fees_per_symbol()
print(f"Database symbol fees: {db_fees}")

# Test 7: Test RiskManager with dynamic fees
from ibis.core.risk_manager import RiskManager

print("\n7. Testing RiskManager...")
risk_manager = RiskManager()
risk_manager.set_database(db)
entry_price = 50000
stop_loss = 48500
tp_without_fees = risk_manager.calculate_take_profit(entry_price, stop_loss)
tp_with_fees = risk_manager.calculate_take_profit(entry_price, stop_loss, symbol="BTC")
print(f"Take profit without fees: ${tp_without_fees:.2f}")
print(f"Take profit with BTC fees: ${tp_with_fees:.2f}")
print(f"Difference (fees): ${tp_with_fees - tp_without_fees:.2f}")

print("\n=== All tests completed successfully ===")
