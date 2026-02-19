#!/usr/bin/env python3
"""
Test script to reproduce fee calculation issue without database
"""

from ibis.core.risk_manager import RiskManager, RiskParams


def test_fee_calculation_no_db():
    """Test fee calculations without database (should use TRADING constants)"""
    risk_params = RiskParams()
    risk_manager = RiskManager(risk_params)

    symbol = "ETH"
    entry_price = 2500.0
    quantity = 2.0
    volatility = 0.05
    atr = 50.0
    support_level = 2400.0
    resistance_level = 2600.0
    trend_strength = 0.5
    market_regime = "NORMAL"
    price_history = [entry_price] * 20

    print(f"Testing fee calculations for {symbol} (without database)")
    print(f"Entry price: ${entry_price:.2f}")
    print(f"Quantity: {quantity:.2f} ETH")
    print(f"Position value: ${quantity * entry_price:.2f}")
    print()

    # Get fee rates
    fee_rates = risk_manager._get_fee_rates(symbol)
    print(f"Fee rates:")
    print(f"  Maker fee: {fee_rates['maker']:.4%}")
    print(f"  Taker fee: {fee_rates['taker']:.4%}")
    print(f"  Fee count: {fee_rates['count']}")
    print()

    # Calculate stop loss and take profit
    stop_loss = risk_manager.calculate_stop_loss(
        entry_price,
        volatility,
        atr,
        support_level,
        trend_strength,
        symbol,
        market_regime,
        price_history,
    )

    take_profit = risk_manager.calculate_take_profit(
        entry_price,
        stop_loss,
        None,
        resistance_level,
        trend_strength,
        symbol,
        market_regime,
        price_history,
    )

    print(f"Calculated levels:")
    print(f"  Stop loss: ${stop_loss:.2f}")
    print(f"  Take profit: ${take_profit:.2f}")
    print()

    # Calculate entry and exit fees based on current implementation
    entry_fee_pct = fee_rates["taker"]  # Market order entry
    exit_fee_pct = fee_rates["maker"]  # Limit order exit

    entry_fee = entry_price * entry_fee_pct
    exit_fee = take_profit * exit_fee_pct

    print(f"Current fee calculation:")
    print(f"  Entry fee per ETH: ${entry_fee:.2f}")
    print(f"  Exit fee per ETH: ${exit_fee:.2f}")
    print(f"  Total entry fee for {quantity} ETH: ${entry_fee * quantity:.2f}")
    print(f"  Total exit fee for {quantity} ETH: ${exit_fee * quantity:.2f}")
    print(f"  Total fees: ${(entry_fee + exit_fee) * quantity:.2f}")
    print()

    # Expected fees (0.1% total)
    expected_fee_rate = 0.001  # 0.1%
    expected_total_fees = quantity * entry_price * expected_fee_rate
    print(f"Expected fees (0.1%):")
    print(f"  Total fees: ${expected_total_fees:.2f}")
    print()

    # Check if fees are reasonable
    actual_total_fees = (entry_fee + exit_fee) * quantity
    if actual_total_fees > expected_total_fees * 2:
        print("WARNING: Actual fees are more than 2x expected!")
    elif actual_total_fees < expected_total_fees * 0.5:
        print("WARNING: Actual fees are less than 0.5x expected!")
    else:
        print("Fees appear to be reasonable")


if __name__ == "__main__":
    test_fee_calculation_no_db()
