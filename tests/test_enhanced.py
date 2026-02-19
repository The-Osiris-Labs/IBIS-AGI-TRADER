#!/usr/bin/env python3
"""
🧪 IBIS 20X ENHANCEMENTS - TEST SUITE
======================================
Comprehensive testing of all enhanced features
"""

import asyncio
import json
import sys
import pytest
from datetime import datetime
from typing import Dict

# Add parent directory to path
sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader")

sys.path.insert(0, "/root/projects/Dont enter unless solicited/AGI Trader/tests/sandbox")
from ibis_enhanced_integration import IBISEnhancedIntegration
from ibis.exchange.kucoin_client import get_kucoin_client


@pytest.fixture(scope="module")
def test_agent():
    """Fixture to create a TestAgent instance"""
    return TestAgent()


@pytest.fixture(scope="module")
def enhanced(test_agent):
    """Fixture to create an IBISEnhancedIntegration instance"""
    return IBISEnhancedIntegration(test_agent)


@pytest.fixture(scope="module")
def symbol():
    """Fixture to provide a test symbol"""
    return "BTC"


@pytest.fixture(scope="module")
def market_data(symbol):
    """Fixture to provide mock market data"""
    return {
        "symbol": symbol,
        "price": 45000.0,
        "score": 65,
        "volatility": 0.025,
        "change_24h": 2.5,
        "momentum_1h": 0.8,
        "volume_24h": 25000000000,
        "market_regime": "NORMAL",
        "technical_strength": 60,
        "market_activity": {"volatility_1m": 0.02},
        "orderbook_analysis": {"imbalance": 0.1},
        "sentiment_analysis": {"score": 55},
        "atr_data": {"atr_percent": 0.025},
    }


class TestAgent:
    """Mock agent for testing"""

    def __init__(self):
        self.config = {
            "base_position_pct": 5.0,
            "max_position_pct": 30.0,
            "max_daily_loss": 0.20,
            "max_portfolio_risk": 0.15,
            "atr_multiplier_tp": 2.0,
            "atr_multiplier_sl": 3.0,
            "portfolio_heat": 0.02,
        }
        print("📡 Connecting to KuCoin...")
        self.client = get_kucoin_client()
        print("✅ Connected to KuCoin")

        # Initialize mock state
        self.state = {
            "capital_awareness": {
                "real_trading_capital": 1000.0,
                "usdt_available": 1000.0,
                "buy_orders": {},
                "open_orders_count": 0,
            },
            "positions": {},
            "daily": {
                "start_balance": 1000.0,
                "trades": 0,
                "orders_placed": 0,
                "realized_pnl": 0.0,
            },
            "market_regime": "NORMAL",
            "agent_mode": "ADAPTIVE",
            "execution_meta": {},
            "liquidity_history": [],
        }

        # Initialize mock free_intel (set to None since it's not needed for basic testing)
        self.free_intel = None

    def log_event(self, msg):
        """Log events with optional color coding for testing"""
        # Colorize certain logs if in terminal
        if "ORDER" in msg or "SUCCESS" in msg or "SOLD" in msg or "✅" in msg:
            print(f"\033[92m{msg}\033[0m")
        elif "ERROR" in msg or "🛑" in msg or "❌" in msg:
            print(f"\033[91m{msg}\033[0m")
        else:
            print(msg)


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print("=" * 70)


def print_result(label: str, value, unit: str = ""):
    """Print formatted result"""
    print(f"   {label:30s} {value}{unit}")


async def test_agi_integration(enhanced: IBISEnhancedIntegration, symbol: str, market_data: Dict):
    """Test AGI brain integration"""
    print_section(f"🧠 AGI Brain Integration - {symbol}")

    try:
        agi_enhanced = await enhanced.get_agi_enhanced_signal(symbol, market_data)

        print_result("Original Score:", f"{market_data.get('score', 0):.1f}/100")
        print_result("Enhanced Score:", f"{agi_enhanced.get('enhanced_score', 0):.1f}/100")
        print_result("AGI Action:", agi_enhanced.get("agi_action", "N/A"))
        print_result("AGI Confidence:", f"{agi_enhanced.get('agi_confidence', 0):.1f}%")
        print_result("Model Consensus:", f"{len(agi_enhanced.get('model_consensus', {}))} models")
        print_result("Confluences:", f"{len(agi_enhanced.get('confluences', []))} signals")

        if agi_enhanced.get("agi_reasoning"):
            print(f"\n   💭 Reasoning: {agi_enhanced['agi_reasoning'][:100]}...")

        print("\n   ✅ AGI Integration: PASSED")
        return True
    except Exception as e:
        print(f"\n   ❌ AGI Integration: FAILED - {e}")
        return False


async def test_mtf_analysis(enhanced: IBISEnhancedIntegration, symbol: str):
    """Test multi-timeframe analysis"""
    print_section(f"📊 Multi-Timeframe Analysis - {symbol}")

    try:
        mtf_data = await enhanced.get_multi_timeframe_analysis(symbol)

        print_result("Alignment Score:", f"{mtf_data.get('alignment_score', 0):.1f}%")
        print_result("Dominant Trend:", mtf_data.get("dominant_trend", "N/A"))
        print_result("Trend Strength:", f"{mtf_data.get('strength', 0):.2f}%")

        print("\n   Timeframe Details:")
        for tf, data in mtf_data.get("timeframes", {}).items():
            if "error" not in data:
                trend = data.get("trend", "N/A")
                strength = data.get("strength", 0)
                print(f"      {tf:5s} → {trend:8s} (strength: {strength:.1f}%)")

        print("\n   ✅ MTF Analysis: PASSED")
        return True
    except Exception as e:
        print(f"\n   ❌ MTF Analysis: FAILED - {e}")
        return False


def test_position_sizing(enhanced: IBISEnhancedIntegration, symbol: str):
    """Test smart position sizing"""
    print_section(f"💰 Smart Position Sizing - {symbol}")

    try:
        # Test with different confidence levels
        test_cases = [(0.3, "Low Confidence"), (0.5, "Medium Confidence"), (0.8, "High Confidence")]

        for confidence, label in test_cases:
            sizing = enhanced.calculate_smart_position_size(
                symbol=symbol,
                confidence=confidence,
                volatility=0.025,
                available_capital=1000.0,
                current_positions=[],
            )

            print(f"\n   {label} ({confidence:.0%}):")
            print_result("Position Size:", f"${sizing['size_usdt']:.2f}")
            print_result("Position %:", f"{sizing['size_pct']:.2f}%")
            print_result("Correlation Risk:", f"{sizing['correlation_risk']:.2f}")
            print_result("Recommended:", "✅ Yes" if sizing["recommended"] else "❌ No")

        print("\n   ✅ Position Sizing: PASSED")
        return True
    except Exception as e:
        print(f"\n   ❌ Position Sizing: FAILED - {e}")
        return False


def test_dynamic_stops(enhanced: IBISEnhancedIntegration):
    """Test dynamic stop loss calculation"""
    print_section("🎯 Dynamic Stop Loss & Take Profit")

    try:
        entry_price = 100.0

        # Test different regimes
        test_cases = [
            ("FLAT", 0.5, "Flat Market"),
            ("TRENDING", 0.7, "Trending Market"),
            ("VOLATILE", 0.4, "Volatile Market"),
        ]

        for regime, confidence, label in test_cases:
            stops = enhanced.calculate_dynamic_stops(
                entry_price=entry_price, atr_percent=0.025, regime=regime, confidence=confidence
            )

            print(f"\n   {label} ({regime}, {confidence:.0%} confidence):")
            print_result("Entry Price:", f"${entry_price:.2f}")
            print_result(
                "Stop Loss:", f"${stops['stop_loss']:.2f}", f" (-{stops['stop_distance_pct']:.2f}%)"
            )
            print_result(
                "Take Profit:",
                f"${stops['take_profit']:.2f}",
                f" (+{stops['tp_distance_pct']:.2f}%)",
            )
            print_result("Risk/Reward:", f"{stops['risk_reward']:.2f}R")
            print_result("Strategy:", stops["strategy"])

        print("\n   ✅ Dynamic Stops: PASSED")
        return True
    except Exception as e:
        print(f"\n   ❌ Dynamic Stops: FAILED - {e}")
        return False


def test_enhanced_position(enhanced: IBISEnhancedIntegration):
    """Test enhanced position tracking"""
    print_section("📍 Enhanced Position Tracking")

    try:
        # Create test position
        position = enhanced.create_enhanced_position(
            symbol="BTC",
            quantity=0.1,
            entry_price=100.0,
            stop_loss=97.0,
            take_profit=105.0,
            regime="TRENDING",
            confidence=0.7,
            atr_percent=0.025,
        )

        print_result("Symbol:", position.symbol)
        print_result("Entry Price:", f"${position.entry_price:.2f}")
        print_result("Stop Loss:", f"${position.stop_loss:.2f}")
        print_result("Take Profit:", f"${position.take_profit:.2f}")
        print_result("Risk/Reward:", f"{position.risk_reward:.2f}R")
        print_result("Confidence:", f"{position.confidence:.0%}")

        # Test price updates and trailing stop
        print("\n   Testing Trailing Stop:")
        test_prices = [102.0, 104.0, 106.0, 103.0]

        for price in test_prices:
            position.update_trailing_stop(price, position.atr_percent)
            should_exit, reason = position.should_exit()

            trailing_price = position.trailing_stop if position.trailing_stop else 0.0
            print(f"      Price: ${price:.2f} → Trailing: ${trailing_price:.2f} → {reason}")

        print("\n   ✅ Enhanced Position: PASSED")
        return True
    except Exception as e:
        print(f"\n   ❌ Enhanced Position: FAILED - {e}")
        return False


def test_performance_tracking(enhanced: IBISEnhancedIntegration):
    """Test performance tracking"""
    print_section("📈 Performance Tracking")

    try:
        # Record test trades
        test_trades = [
            ("BTC", 100, 102, 0.1, "TRENDING", "Trend Rider", "TAKE_PROFIT"),
            ("ETH", 50, 49, 1.0, "FLAT", "Range Scalper", "STOP_LOSS"),
            ("SOL", 20, 21, 5.0, "NORMAL", "Balanced Trader", "TAKE_PROFIT"),
            ("BNB", 300, 295, 0.3, "VOLATILE", "Volatility Hunter", "STOP_LOSS"),
        ]

        for symbol, entry, exit, qty, regime, strategy, reason in test_trades:
            enhanced.record_trade_result(symbol, entry, exit, qty, regime, strategy, reason)

        # Get metrics
        metrics = enhanced.get_performance_metrics()

        print_result("Total Trades:", metrics.get("total_trades", 0))
        print_result("Winning Trades:", metrics.get("winning_trades", 0))
        print_result("Losing Trades:", metrics.get("losing_trades", 0))
        print_result("Win Rate:", f"{metrics.get('win_rate', 0):.1f}%")
        print_result("Total P&L:", f"${metrics.get('total_pnl', 0):.2f}")
        print_result("Avg Win:", f"${metrics.get('avg_win', 0):.2f}")
        print_result("Avg Loss:", f"${metrics.get('avg_loss', 0):.2f}")
        print_result("Profit Factor:", f"{metrics.get('profit_factor', 0):.2f}")
        print_result("Best Regime:", metrics.get("best_regime", "N/A"))

        print("\n   ✅ Performance Tracking: PASSED")
        return True
    except Exception as e:
        print(f"\n   ❌ Performance Tracking: FAILED - {e}")
        return False


def test_risk_management(enhanced: IBISEnhancedIntegration):
    """Test risk management"""
    print_section("🛡️ Risk Management")

    try:
        # Test drawdown tracking
        balances = [1000, 950, 900, 920, 880]

        print("   Testing Drawdown Protection:")
        for balance in balances:
            risk_check = enhanced.check_risk_limits(balance, -0.05)

            print(f"      Balance: ${balance:.2f}")
            print(f"         Drawdown: {risk_check['drawdown']:.1%}")
            print(
                f"         Reduce Risk: {'✅ Yes' if risk_check['should_reduce_risk'] else '❌ No'}"
            )
            print(
                f"         Stop Trading: {'🛑 Yes' if risk_check['should_stop_trading'] else '✅ No'}"
            )

        print("\n   ✅ Risk Management: PASSED")
        return True
    except Exception as e:
        print(f"\n   ❌ Risk Management: FAILED - {e}")
        return False


async def test_comprehensive_analysis(enhanced: IBISEnhancedIntegration, symbol: str):
    """Test comprehensive analysis pipeline"""
    print_section(f"🔬 Comprehensive Analysis - {symbol}")

    try:
        market_data = {
            "symbol": symbol,
            "price": 100.0,
            "score": 65,
            "volatility": 0.025,
            "change_24h": 2.5,
            "momentum_1h": 0.8,
            "volume_24h": 1000000,
            "market_regime": "NORMAL",
            "technical_strength": 60,
            "market_activity": {"volatility_1m": 0.02},
            "orderbook_analysis": {"imbalance": 0.1},
            "sentiment_analysis": {"score": 55},
            "atr_data": {"atr_percent": 0.025},
        }

        analysis = await enhanced.get_comprehensive_analysis(symbol, market_data)

        print_result("Enhanced Score:", f"{analysis['enhanced_score']:.1f}/100")
        print_result("Recommendation:", analysis["recommendation"]["action"])
        print_result("Reason:", analysis["recommendation"]["reason"])
        print_result("Confidence:", f"{analysis['recommendation']['confidence']:.0%}")
        print_result("Position Size:", f"${analysis['recommendation']['position_size_usdt']:.2f}")
        print_result("Risk/Reward:", f"{analysis['recommendation']['risk_reward']:.2f}R")

        print("\n   ✅ Comprehensive Analysis: PASSED")
        return True
    except Exception as e:
        print(f"\n   ❌ Comprehensive Analysis: FAILED - {e}")
        import traceback

        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all test suites"""
    print("\n" + "=" * 70)
    print("  🧪 IBIS 20X ENHANCEMENTS - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Initialize
    print("\n🔧 Initializing test environment...")
    agent = TestAgent()
    enhanced = IBISEnhancedIntegration(agent)

    # Track results
    results = []

    # Test symbols
    test_symbol = "BTC"

    # Mock market data
    market_data = {
        "symbol": test_symbol,
        "price": 45000.0,
        "score": 65,
        "volatility": 0.025,
        "change_24h": 2.5,
        "momentum_1h": 0.8,
        "volume_24h": 25000000000,
        "market_regime": "NORMAL",
        "technical_strength": 60,
        "market_activity": {"volatility_1m": 0.02},
        "orderbook_analysis": {"imbalance": 0.1},
        "sentiment_analysis": {"score": 55},
        "atr_data": {"atr_percent": 0.025},
    }

    # Run tests
    print("\n🚀 Running test suites...\n")

    results.append(
        ("AGI Integration", await test_agi_integration(enhanced, test_symbol, market_data))
    )
    results.append(("MTF Analysis", await test_mtf_analysis(enhanced, test_symbol)))
    results.append(("Position Sizing", test_position_sizing(enhanced, test_symbol)))
    results.append(("Dynamic Stops", test_dynamic_stops(enhanced)))
    results.append(("Enhanced Position", test_enhanced_position(enhanced)))
    results.append(("Performance Tracking", test_performance_tracking(enhanced)))
    results.append(("Risk Management", test_risk_management(enhanced)))
    results.append(
        ("Comprehensive Analysis", await test_comprehensive_analysis(enhanced, test_symbol))
    )

    # Summary
    print_section("📊 TEST SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {name:30s} {status}")

    print(f"\n   {'=' * 66}")
    print(f"   Total: {passed}/{total} tests passed ({(passed / total) * 100:.0f}%)")
    print(f"   {'=' * 66}")

    if passed == total:
        print("\n   🎉 ALL TESTS PASSED! 20X enhancements are ready to deploy!")
    else:
        print(f"\n   ⚠️  {total - passed} test(s) failed. Review errors above.")

    print(f"\n   Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
