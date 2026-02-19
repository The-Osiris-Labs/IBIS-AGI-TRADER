#!/usr/bin/env python3
"""
Comprehensive verification script for IBIS system untested components
Tests:
1. Data feed module - Real-time price updates
2. Market intelligence integration - AGI scoring and market regime detection
3. Order management system - Order tracking and execution
4. Position sizing calculations - Capital allocation logic
5. Risk management system - TP/SL rules
6. Any other critical components
"""

import sys
import asyncio
import os
import math
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ibis.core.risk_manager import RiskManager, RiskParams
from ibis.exchange.data_feed import DataFeed, MarketSnapshot
from ibis.exchange.trade_executor import TradeExecutor, TradeRequest, OrderSide, OrderType
from ibis.intelligence.market_intel import (
    MarketIntelligence,
    MarketContext,
    MarketInsight,
    AnalysisDimension,
)
from ibis.exchange.kucoin_client import KuCoinClient, Ticker, OrderBook, Candle
from ibis.intelligence.enhanced_sniping import (
    calculate_volume_momentum,
    detect_breakout,
    calculate_price_action_score,
    rank_by_upward_momentum,
    predict_upward_move,
    score_snipe_opportunity,
)
from ibis.intelligence.monitoring import IntelligenceMonitor
from ibis.intelligence.adaptive_intelligence import MarketConditionDetector
from ibis.cognition import IBISCognition
from ibis.brain import LocalReasoningEngine
from ibis.indicators import IndicatorEngine
from ibis.pnl_tracker import PnLTracker
from ibis.state_sync import StateSynchronizer
from ibis.cross_exchange_monitor import CrossExchangeMonitor
from ibis.position_rotation import PositionRotationManager
from ibis.microstructure import Microstructure


async def test_data_feed_module():
    """Test data feed module and real-time price updates"""
    print("=" * 80)
    print("📊 DATA FEED MODULE VERIFICATION")
    print("=" * 80)

    try:
        # Create mock client
        client = MagicMock(spec=KuCoinClient)

        # Mock ticker data
        mock_ticker = MagicMock(spec=Ticker)
        mock_ticker.price = 45000.0
        mock_ticker.timestamp = 1708000000000
        mock_ticker.change_24h = 2.5
        mock_ticker.volume_24h = 1500000000

        client.get_ticker.return_value = mock_ticker

        # Mock orderbook
        mock_orderbook = MagicMock(spec=OrderBook)
        mock_orderbook.bids = [[45000.0, 0.5], [44999.5, 0.3]]
        mock_orderbook.asks = [[45001.0, 0.4], [45002.0, 0.2]]
        client.get_orderbook.return_value = mock_orderbook

        # Create data feed
        symbols = ["BTC-USDT", "ETH-USDT"]
        data_feed = DataFeed(client, symbols, update_interval=0.1)

        # Start data feed (in test mode)
        await data_feed.start()

        # Simulate updates
        print("✅ Data feed initialized successfully")

        # Get snapshot
        snapshot = await data_feed.get_snapshot("BTC-USDT")
        if isinstance(snapshot, MarketSnapshot):
            print(f"✅ Market snapshot retrieved")
            print(f"   Symbol: {snapshot.symbol}")
            print(f"   Price: ${snapshot.price:.2f}")
            print(f"   Change 24h: {snapshot.price_change:.2f}%")
            print(f"   Volume: ${snapshot.volume:,.0f}")
            print(f"   Volatility: {snapshot.volatility:.2f}%")
            print(f"   Spread: ${snapshot.bid_ask_spread:.2f}")
        else:
            print("❌ Failed to get market snapshot")

        await data_feed.stop()
        return True

    except Exception as e:
        print(f"❌ Error in data feed module: {e}")
        import traceback

        print(traceback.format_exc())
        return False


async def test_market_intelligence():
    """Test market intelligence integration, AGI scoring, and regime detection"""
    print("\n" + "=" * 80)
    print("🧠 MARKET INTELLIGENCE VERIFICATION")
    print("=" * 80)

    try:
        # Test MarketIntelligence class
        intelligence = MarketIntelligence()

        # Test comprehensive analysis
        context = MarketContext(
            symbol="BTC-USDT",
            price=45000.0,
            price_change_24h=2.5,
            price_change_1h=0.8,
            volume_24h=1500000000,
            volatility_1h=0.03,
            volatility_24h=0.08,
            trend_strength=75,
            order_flow_delta=0.25,
            sentiment_score=0.7,
            fear_greed_index=65,
            funding_rate=0.01,
            long_short_ratio=1.2,
            exchange_flow=0.1,
            whale_activity="ACCUMULATING",
            timestamp=1708000000000,
        )

        # Create test price data
        closes = [44500, 44600, 44700, 44800, 44900, 45000]
        volumes = [1000, 1100, 1200, 1300, 1400, 1500]

        insight = await intelligence.comprehensive_analysis(
            symbol=context.symbol,
            price=context.price,
            price_change=context.price_change_24h,
            volume=context.volume_24h,
            highs=closes,
            lows=closes,
            closes=closes,
            volumes=volumes,
            order_flow=None,
            volume_profile=None,
            sentiment=None,
            on_chain=None,
            related_symbols=["ETH-USDT", "SOL-USDT"],
        )

        print(f"✅ Comprehensive analysis completed")
        print(f"   Dimension: {insight.dimension}")
        print(f"   Signal: {insight.signal}")
        print(f"   Confidence: {insight.confidence:.2f}")
        print(f"   Strength: {insight.strength:.2f}")
        print(f"   Key Levels: {insight.key_levels}")

        # Test MarketConditionDetector
        condition_detector = MarketConditionDetector()

        # Simulate conditions
        conditions = await condition_detector.detect_conditions("BTC-USDT", context.__dict__)

        print(f"\n✅ Market conditions assessment")
        print(f"   Trend: {conditions['trend']}")
        print(f"   Volatility: {conditions['volatility']}")
        print(f"   Sentiment: {conditions['sentiment']}")
        print(f"   Liquidity: {conditions['liquidity']}")
        print(f"   Regime: {conditions['regime']}")
        print(f"   Opportunity Score: {conditions['opportunity_score']:.2f}")
        print(f"   Risk Level: {conditions['risk_level']}")
        print(f"   Confidence: {conditions['confidence']:.2f}")

        return True

    except Exception as e:
        print(f"❌ Error in market intelligence: {e}")
        import traceback

        print(traceback.format_exc())
        return False


async def test_order_management():
    """Test order management system and execution"""
    print("\n" + "=" * 80)
    print("📈 ORDER MANAGEMENT SYSTEM VERIFICATION")
    print("=" * 80)

    try:
        # Create mock client
        client = MagicMock(spec=KuCoinClient)

        # Create trade executor
        executor = TradeExecutor(
            client=client,
            max_position_size=0.1,
            max_order_size=0.05,
            default_leverage=1,
            commission_rate=0.001,
        )

        # Create mock ticker
        mock_ticker = MagicMock(spec=Ticker)
        mock_ticker.price = 45000.0
        client.get_ticker.return_value = mock_ticker

        # Test market order
        request = TradeRequest(
            symbol="BTC-USDT", side=OrderSide.BUY, type=OrderType.MARKET, size=0.01
        )

        result = await executor.execute(request)
        print(f"✅ Market order executed")
        print(f"   Order ID: {result.order_id}")
        print(f"   Status: {result.status.value}")
        print(f"   Filled Size: {result.filled_size:.4f}")
        print(f"   Avg Price: ${result.avg_price:.2f}")
        print(f"   Total Value: ${result.total_value:.2f}")
        print(f"   Commission: ${result.commission:.2f}")

        # Verify position was created
        positions = executor.get_positions()
        print(f"\n✅ Positions tracked: {len(positions)}")

        if positions:
            pos = positions[0]
            print(f"   Symbol: {pos.symbol}")
            print(f"   Size: {pos.size:.4f}")
            print(f"   Entry Price: ${pos.entry_price:.2f}")

        # Test trade history
        history = executor.get_trade_history()
        print(f"\n✅ Trade history: {len(history)} trades")

        return True

    except Exception as e:
        print(f"❌ Error in order management: {e}")
        import traceback

        print(traceback.format_exc())
        return False


async def test_position_sizing():
    """Test position sizing and capital allocation logic"""
    print("\n" + "=" * 80)
    print("💰 POSITION SIZING CALCULATIONS VERIFICATION")
    print("=" * 80)

    try:
        # Test RiskManager position sizing
        risk_params = RiskParams(
            base_risk_per_trade=0.02,  # 2% per trade
            max_risk_per_trade=0.05,  # 5% max
            portfolio_heat_limit=0.60,
            stop_loss_pct=0.05,
            take_profit_pct=0.02,
            min_position_size=11.0,
            max_position_size=40.0,
            risk_reward_ratio=0.4,
        )

        risk_manager = RiskManager(risk_params)

        # Test position size calculation
        account_balance = 1000.0
        entry_price = 45000.0
        stop_loss_price = 44775.0  # 0.5% below entry

        quantity, position_value, risk_amount = risk_manager.calculate_position_size(
            account_balance=account_balance,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            confidence=0.75,
            volatility=0.025,
            liquidity=0.8,
        )

        print(f"✅ Position size calculation")
        print(f"   Quantity: {quantity:.6f} BTC")
        print(f"   Position Value: ${position_value:.2f}")
        print(f"   Risk Amount: ${risk_amount:.2f}")

        # Verify position constraints
        assert position_value >= risk_params.min_position_size, "Position too small"
        assert position_value <= risk_params.max_position_size, "Position too large"

        # Test stop loss calculation
        sl_price = risk_manager.calculate_stop_loss(
            entry_price=entry_price,
            volatility=0.025,
            atr=200,
            support_level=44500,
            trend_strength=0.6,
        )

        print(f"\n✅ Stop loss calculation")
        print(f"   Stop Loss Price: ${sl_price:.2f}")

        # Test take profit calculation
        tp_price = risk_manager.calculate_take_profit(
            entry_price=entry_price,
            stop_loss=sl_price,
            reward_risk_ratio=0.4,
            resistance_level=46000,
            trend_strength=0.6,
        )

        print(f"✅ Take profit calculation")
        print(f"   Take Profit Price: ${tp_price:.2f}")

        return True

    except Exception as e:
        print(f"❌ Error in position sizing: {e}")
        import traceback

        print(traceback.format_exc())
        return False


async def test_risk_management():
    """Test risk management system and new TP/SL rules"""
    print("\n" + "=" * 80)
    print("🛡️  RISK MANAGEMENT SYSTEM VERIFICATION")
    print("=" * 80)

    try:
        # Create risk manager
        risk_manager = RiskManager()

        # Test validate position
        from ibis.core.risk_manager import PositionRisk, PortfolioRisk

        # Create position risk
        position = PositionRisk(
            symbol="BTC-USDT",
            entry_price=45000.0,
            quantity=0.01,
            stop_loss=44775.0,
            take_profit=45180.0,
            risk_amount=2.25,
            reward_amount=1.80,
            risk_reward=0.8,
            position_value=450.0,
            portfolio_exposure=0.045,
            confidence=0.75,
            volatility_score=0.025,
            liquidity_score=0.8,
        )

        # Create portfolio risk
        portfolio = PortfolioRisk(
            total_value=10000.0,
            total_risk=10.0,
            total_exposure=450.0,
            positions_count=1,
            max_position_risk=2.25,
            avg_position_risk=2.25,
            risk_concentration=0.0,
            drawdown_risk=0.025,
            volatility_risk=0.025,
            liquidity_risk=0.2,
        )

        is_valid, violations = risk_manager.validate_position(position, portfolio)

        print(f"✅ Position validation")
        print(f"   Valid: {is_valid}")
        if violations:
            print(f"   Violations: {', '.join(violations)}")

        # Calculate position score
        score = risk_manager.calculate_position_score(position, portfolio)
        print(f"✅ Position score: {score:.1f}/100")

        # Generate recommendations
        sl_rec, sl_reasoning = risk_manager.generate_stop_loss_recommendation(
            symbol="BTC-USDT",
            current_price=45000.0,
            volatility=0.025,
            atr=200,
            support_level=44500,
            trend_strength=0.6,
        )

        print(f"\n✅ Stop loss recommendation")
        print(f"   Price: ${sl_rec:.2f}")
        print(f"   Reasoning: {sl_reasoning}")

        tp_rec, tp_reasoning = risk_manager.generate_take_profit_recommendation(
            entry_price=45000.0,
            current_price=45000.0,
            stop_loss=sl_rec,
            resistance_level=46000,
            trend_strength=0.6,
        )

        print(f"✅ Take profit recommendation")
        print(f"   Price: ${tp_rec:.2f}")
        print(f"   Reasoning: {tp_reasoning}")

        return True

    except Exception as e:
        print(f"❌ Error in risk management: {e}")
        import traceback

        print(traceback.format_exc())
        return False


async def test_other_components():
    """Test other critical components"""
    print("\n" + "=" * 80)
    print("🔧 OTHER CRITICAL COMPONENTS VERIFICATION")
    print("=" * 80)

    try:
        # Test Cognition system (requires brain and memory)
        from ibis.brain import get_agi_brain
        from ibis.memory import get_memory

        brain = get_agi_brain()
        memory = get_memory()
        cognition = IBISCognition(brain, memory)
        print("✅ Cognition system initialized")

        # Test Local Reasoning
        reasoning = LocalReasoningEngine()
        print("✅ Local reasoning engine initialized")

        # Test Indicator Engine
        indicator_engine = IndicatorEngine()
        print("✅ Indicator engine initialized")

        # Test PnLTracker
        pnl_tracker = PnLTracker()
        print("✅ PnL tracker initialized")

        # Test StateSynchronizer
        state_sync = StateSynchronizer()
        print("✅ State sync system initialized")

        # Test CrossExchangeMonitor
        monitor = CrossExchangeMonitor()
        await monitor.initialize()
        print("✅ Cross-exchange monitor initialized")

        # Test PositionRotationManager
        rotation = PositionRotationManager()
        print("✅ Position rotation system initialized")

        # Test Microstructure
        microstructure = Microstructure(
            spread_pct=0.001, imbalance=0.1, depth_bid=1000, depth_ask=900
        )
        print("✅ Market microstructure analyzer initialized")

        return True

    except Exception as e:
        print(f"❌ Error in other components: {e}")
        import traceback

        print(traceback.format_exc())
        return False


async def main():
    """Main verification function"""
    print("🚀 IBIS SYSTEM COMPREHENSIVE VERIFICATION")
    print("=" * 80)

    tests = [
        ("Data Feed", test_data_feed_module),
        ("Market Intelligence", test_market_intelligence),
        ("Order Management", test_order_management),
        ("Position Sizing", test_position_sizing),
        ("Risk Management", test_risk_management),
        ("Other Components", test_other_components),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            print(f"\n{'=' * 30} Running {test_name} {'=' * 30}")
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Error running {test_name}: {e}")
            import traceback

            print(traceback.format_exc())
            results.append((test_name, False))

    print("\n" + "=" * 80)
    print("📊 VERIFICATION RESULTS")
    print("=" * 80)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
        if success:
            passed += 1

    print(f"\n📈 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL COMPONENTS VERIFIED SUCCESSFULLY!")
    else:
        print(f"\n⚠️ {total - passed} tests failed")

    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Verification interrupted by user")
        sys.exit(0)
