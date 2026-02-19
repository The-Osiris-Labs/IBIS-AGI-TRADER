"""
Tests for Advanced Intelligence Enhancement Module
==================================================

These tests validate the advanced intelligence capabilities:
1. Fee Analysis Enhancement - Real-time tracking, optimization, historical trends
2. Market Movement Understanding - Trend detection, volatility, regime classification
3. Symbol Movement Analysis - Symbol-specific patterns, volatility, correlation
4. Profitability Attribution - Fee impact, market conditions, regime performance
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ibis.advanced_intelligence import (
    FeeAnalyzer,
    MarketMovementAnalyzer,
    SymbolMovementAnalyzer,
    ProfitabilityAttributor,
    AdvancedIntelligenceEnhancement,
)
from ibis.pnl_tracker import PnLTracker, Trade


class TestFeeAnalyzer:
    """Tests for FeeAnalyzer class"""

    @pytest.fixture
    def mock_trades(self):
        """Create mock matched trades for testing"""

        class MockTrade:
            def __init__(self, symbol, fees, gross_pnl, net_pnl, pnl_pct):
                self.buy_trade = type("obj", (object,), {"symbol": symbol})
                self.sell_trade = type("obj", (object,), {"symbol": symbol})
                self.fees = fees
                self.gross_pnl = gross_pnl
                self.net_pnl = net_pnl
                self.pnl_pct = pnl_pct
                self.quantity = 1
                self.entry_price = 100
                self.exit_price = 105

        return [
            MockTrade("BTC", 0.1, 5, 4.9, 5),
            MockTrade("BTC", 0.12, 6, 5.88, 6),
            MockTrade("ETH", 0.08, 4, 3.92, 4),
            MockTrade("ETH", 0.09, 3, 2.91, 3),
            MockTrade("BTC", 0.11, 5.5, 5.39, 5.5),
        ]

    def test_fee_analysis(self, mock_trades):
        """Test fee analysis functionality"""
        analyzer = FeeAnalyzer()
        result = analyzer.analyze_fee_impact(mock_trades, "BTC")

        assert result.symbol == "BTC"
        assert result.total_fees > 0
        assert 0 <= result.avg_fee_rate <= 0.01  # Between 0 and 1%
        assert result.fee_impact_pct > 0
        assert len(result.fee_by_trade_count) > 0

    def test_optimal_fee_calculation(self, mock_trades):
        """Test optimal fee rate calculation"""
        analyzer = FeeAnalyzer()
        result = analyzer.analyze_fee_impact(mock_trades, "BTC")

        assert result.optimal_fee_rate > 0
        assert result.optimal_fee_rate < result.avg_fee_rate
        assert result.optimization_savings > 0

    def test_fee_optimization_recommendations(self, mock_trades):
        """Test fee optimization recommendations"""

        # Create a mock PnL tracker
        class MockPnLTracker:
            def calculate_average_fees_per_symbol(self):
                return {
                    "BTC": {"maker": 0.0015, "taker": 0.002, "count": 50},
                    "ETH": {"maker": 0.0012, "taker": 0.0018, "count": 40},
                }

        analyzer = FeeAnalyzer(MockPnLTracker())
        recommendations = analyzer.get_fee_optimization_recommendations()

        assert "recommendations" in recommendations
        assert len(recommendations["recommendations"]) > 0
        assert recommendations["total_potential_savings"] > 0

    def test_symbol_specific_fee_recommendations(self, mock_trades):
        """Test symbol-specific fee recommendations"""

        class MockPnLTracker:
            def calculate_average_fees_per_symbol(self):
                return {
                    "BTC": {"maker": 0.0015, "taker": 0.002, "count": 50},
                    "ETH": {"maker": 0.0012, "taker": 0.0018, "count": 40},
                }

        analyzer = FeeAnalyzer(MockPnLTracker())
        recommendations = analyzer.get_fee_optimization_recommendations("BTC")

        assert "recommendations" in recommendations
        assert len(recommendations["recommendations"]) > 0
        assert all(rec["symbol"] == "BTC" for rec in recommendations["recommendations"])


class TestMarketMovementAnalyzer:
    """Tests for MarketMovementAnalyzer class"""

    @pytest.fixture
    def bullish_price_data(self):
        """Create bullish price data"""
        dates = pd.date_range(start="2024-01-01", periods=100, freq="h")
        prices = np.cumsum(np.random.randn(100) * 0.001 + 0.002) + 100
        return pd.Series(prices, index=dates)

    @pytest.fixture
    def bearish_price_data(self):
        """Create bearish price data"""
        dates = pd.date_range(start="2024-01-01", periods=100, freq="h")
        prices = np.cumsum(np.random.randn(100) * 0.001 - 0.002) + 100
        return pd.Series(prices, index=dates)

    @pytest.fixture
    def sideways_price_data(self):
        """Create sideways price data"""
        dates = pd.date_range(start="2024-01-01", periods=100, freq="h")
        prices = np.cumsum(np.random.randn(100) * 0.001) + 100
        return pd.Series(prices, index=dates)

    @pytest.fixture
    def volume_data(self):
        """Create volume data"""
        dates = pd.date_range(start="2024-01-01", periods=100, freq="h")
        volumes = np.random.randint(1000, 10000, size=100)
        return pd.Series(volumes, index=dates)

    def test_trend_detection_bullish(self, bullish_price_data):
        """Test bullish trend detection"""
        analyzer = MarketMovementAnalyzer()
        result = analyzer.detect_trend_strength(bullish_price_data)

        assert result["direction"] == "bullish"
        assert result["strength"] > 50
        assert result["confidence"] > 0.5

    def test_trend_detection_bearish(self, bearish_price_data):
        """Test bearish trend detection"""
        analyzer = MarketMovementAnalyzer()
        result = analyzer.detect_trend_strength(bearish_price_data)

        assert result["direction"] == "bearish"
        assert result["strength"] > 50
        assert result["confidence"] > 0.5

    def test_trend_detection_sideways(self, sideways_price_data):
        """Test sideways trend detection"""
        analyzer = MarketMovementAnalyzer()
        result = analyzer.detect_trend_strength(sideways_price_data)

        # Sideways markets should have trend strength around 50
        assert 30 < result["strength"] < 70

    def test_market_regime_classification(self, bullish_price_data, volume_data):
        """Test market regime classification"""
        analyzer = MarketMovementAnalyzer()
        regime = analyzer.classify_market_regime(bullish_price_data, volume_data)

        assert regime.regime_type in ["strong_trend", "weak_trend", "neutral", "volatile", "stable"]
        assert 0 <= regime.confidence <= 1
        assert regime.volatility > 0
        assert regime.trend_strength > 0
        assert regime.duration > 0

    def test_support_resistance_detection(self, bullish_price_data):
        """Test support and resistance detection"""
        analyzer = MarketMovementAnalyzer()
        levels = analyzer.detect_support_resistance(bullish_price_data, lookback=50)

        assert "support" in levels
        assert "resistance" in levels
        assert "volatility" in levels
        assert len(levels["support"]) >= 0
        assert len(levels["resistance"]) >= 0

    def test_price_action_pattern_recognition(self, bullish_price_data):
        """Test price action pattern recognition"""
        analyzer = MarketMovementAnalyzer()
        patterns = analyzer.analyze_price_action_patterns(bullish_price_data)

        assert isinstance(patterns, list)
        for pattern in patterns:
            assert "name" in pattern
            assert "confidence" in pattern
            assert "direction" in pattern


class TestSymbolMovementAnalyzer:
    """Tests for SymbolMovementAnalyzer class"""

    @pytest.fixture
    def price_data(self):
        """Create test price data"""
        dates = pd.date_range(start="2024-01-01", periods=100, freq="h")
        prices = np.cumsum(np.random.randn(100) * 0.001 + 0.001) + 100
        return pd.Series(prices, index=dates)

    @pytest.fixture
    def volume_data(self):
        """Create test volume data"""
        dates = pd.date_range(start="2024-01-01", periods=100, freq="h")
        volumes = np.random.randint(1000, 10000, size=100)
        return pd.Series(volumes, index=dates)

    @pytest.fixture
    def other_symbols_data(self):
        """Create other symbols data for correlation analysis"""
        dates = pd.date_range(start="2024-01-01", periods=100, freq="h")
        return {
            "ETH": pd.Series(np.cumsum(np.random.randn(100) * 0.001 + 0.0008) + 2000, index=dates),
            "SOL": pd.Series(np.cumsum(np.random.randn(100) * 0.002 + 0.0015) + 100, index=dates),
        }

    def test_symbol_movement_profile(self, price_data, volume_data, other_symbols_data):
        """Test symbol movement profile creation"""
        analyzer = SymbolMovementAnalyzer()
        profile = analyzer.analyze_symbol_movement(
            "BTC", price_data, volume_data, other_symbols_data
        )

        assert profile.symbol == "BTC"
        assert profile.trend_pattern in ["strong_trend", "weak_trend", "sideways"]
        assert profile.volatility_profile in ["high", "average", "low"]
        assert profile.volume_profile in ["high", "average", "low"]
        assert 0 <= profile.liquidity_score <= 1
        assert len(profile.correlation) == len(other_symbols_data)

    def test_correlation_calculation(self, price_data, other_symbols_data):
        """Test correlation calculation between symbols"""
        analyzer = SymbolMovementAnalyzer()
        correlations = analyzer._calculate_correlations("BTC", price_data, other_symbols_data)

        assert len(correlations) == len(other_symbols_data)
        for symbol, corr in correlations.items():
            assert -1 <= corr <= 1
            assert symbol in other_symbols_data

    def test_correlation_matrix(self, price_data, other_symbols_data):
        """Test correlation matrix calculation"""
        analyzer = SymbolMovementAnalyzer()
        symbol_prices = {"BTC": price_data, **other_symbols_data}
        correlation_matrix = analyzer.calculate_symbol_correlations(symbol_prices)

        assert not correlation_matrix.empty
        assert list(correlation_matrix.columns) == list(symbol_prices.keys())
        assert list(correlation_matrix.index) == list(symbol_prices.keys())

        # Diagonal should be 1 (correlation with itself)
        for symbol in symbol_prices.keys():
            assert np.isclose(correlation_matrix.loc[symbol, symbol], 1)


class TestProfitabilityAttributor:
    """Tests for ProfitabilityAttributor class"""

    @pytest.fixture
    def mock_trades(self):
        """Create mock trades for testing"""

        class MockTrade:
            def __init__(self, symbol, net_pnl, fees, gross_pnl, pnl_pct):
                self.buy_trade = type("obj", (object,), {"symbol": symbol})
                self.sell_trade = type("obj", (object,), {"symbol": symbol})
                self.net_pnl = net_pnl
                self.fees = fees
                self.gross_pnl = gross_pnl
                self.pnl_pct = pnl_pct

        return [
            MockTrade("BTC", 4.9, 0.1, 5, 5),
            MockTrade("BTC", 5.88, 0.12, 6, 6),
            MockTrade("ETH", 3.92, 0.08, 4, 4),
            MockTrade("ETH", 2.91, 0.09, 3, 3),
            MockTrade("BTC", 5.39, 0.11, 5.5, 5.5),
        ]

    @pytest.fixture
    def market_conditions(self):
        """Create mock market conditions"""
        return [
            {"regime_type": "strong_trend", "strength": 85},
            {"regime_type": "weak_trend", "strength": 45},
            {"regime_type": "volatile", "strength": 30},
            {"regime_type": "stable", "strength": 25},
            {"regime_type": "strong_trend", "strength": 90},
        ]

    def test_profitability_attribution(self, mock_trades, market_conditions):
        """Test profitability attribution"""
        attributor = ProfitabilityAttributor()
        result = attributor.attribute_profitability(mock_trades, market_conditions, "BTC")

        assert result.symbol == "BTC"
        assert result.total_pnl > 0
        assert result.fee_impact > 0
        assert result.market_conditions_impact > -100
        assert result.market_conditions_impact < 100
        assert len(result.regime_performance) > 0
        assert result.risk_adjusted_return > 0

    def test_fee_impact_calculation(self, mock_trades, market_conditions):
        """Test fee impact calculation"""
        attributor = ProfitabilityAttributor()
        result = attributor.attribute_profitability(mock_trades, market_conditions, "BTC")

        total_fees = sum(t.fees for t in mock_trades if t.buy_trade.symbol == "BTC")
        total_gross_pnl = sum(t.gross_pnl for t in mock_trades if t.buy_trade.symbol == "BTC")
        expected_fee_impact = (total_fees / total_gross_pnl) * 100

        assert np.isclose(result.fee_impact, expected_fee_impact, atol=1)

    def test_risk_adjusted_return(self, mock_trades, market_conditions):
        """Test risk-adjusted return calculation"""
        attributor = ProfitabilityAttributor()
        result = attributor.attribute_profitability(mock_trades, market_conditions, "BTC")

        returns = [t.pnl_pct for t in mock_trades if t.buy_trade.symbol == "BTC"]
        avg_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return > 0:
            expected_sharpe = avg_return / std_return
            assert np.isclose(result.risk_adjusted_return, expected_sharpe, atol=0.1)


class TestAdvancedIntelligenceEnhancement:
    """Tests for AdvancedIntelligenceEnhancement class"""

    @pytest.fixture
    def mock_pnl_tracker(self):
        """Create a mock PnL tracker"""

        class MockPnLTracker:
            def calculate_average_fees_per_symbol(self):
                return {
                    "BTC": {"maker": 0.0015, "taker": 0.002, "count": 50},
                    "ETH": {"maker": 0.0012, "taker": 0.0018, "count": 40},
                }

        return MockPnLTracker()

    @pytest.fixture
    def price_data_dict(self):
        """Create price data for multiple symbols"""
        dates = pd.date_range(start="2024-01-01", periods=100, freq="h")
        return {
            "BTC": pd.Series(np.cumsum(np.random.randn(100) * 0.001 + 0.002) + 100, index=dates),
            "ETH": pd.Series(np.cumsum(np.random.randn(100) * 0.001 + 0.0015) + 2000, index=dates),
            "SOL": pd.Series(np.cumsum(np.random.randn(100) * 0.002 + 0.001) + 100, index=dates),
        }

    @pytest.fixture
    def volume_data_dict(self):
        """Create volume data for multiple symbols"""
        dates = pd.date_range(start="2024-01-01", periods=100, freq="h")
        return {
            "BTC": pd.Series(np.random.randint(10000, 50000, size=100), index=dates),
            "ETH": pd.Series(np.random.randint(5000, 25000, size=100), index=dates),
            "SOL": pd.Series(np.random.randint(2000, 10000, size=100), index=dates),
        }

    @pytest.fixture
    def volume_data_dict(self):
        """Create volume data for multiple symbols"""
        dates = pd.date_range(start="2024-01-01", periods=100, freq="h")
        return {
            "BTC": pd.Series(np.random.randint(10000, 50000, size=100), index=dates),
            "ETH": pd.Series(np.random.randint(5000, 25000, size=100), index=dates),
            "SOL": pd.Series(np.random.randint(2000, 10000, size=100), index=dates),
        }

    @pytest.fixture
    def mock_matched_trades(self):
        """Create mock matched trades"""

        class MockTrade:
            def __init__(self, symbol, net_pnl, fees, gross_pnl, pnl_pct):
                self.buy_trade = type("obj", (object,), {"symbol": symbol})
                self.sell_trade = type("obj", (object,), {"symbol": symbol})
                self.net_pnl = net_pnl
                self.fees = fees
                self.gross_pnl = gross_pnl
                self.pnl_pct = pnl_pct
                self.quantity = 1
                self.entry_price = 100
                self.exit_price = 105

        return [
            MockTrade("BTC", 4.9, 0.1, 5, 5),
            MockTrade("BTC", 5.88, 0.12, 6, 6),
            MockTrade("ETH", 3.92, 0.08, 4, 4),
            MockTrade("ETH", 2.91, 0.09, 3, 3),
            MockTrade("SOL", 2.45, 0.05, 2.5, 2.5),
        ]

    def test_advanced_intelligence_initialization(self, mock_pnl_tracker):
        """Test advanced intelligence initialization"""
        ai = AdvancedIntelligenceEnhancement(mock_pnl_tracker)

        assert ai.fee_analyzer is not None
        assert ai.market_movement_analyzer is not None
        assert ai.symbol_movement_analyzer is not None
        assert ai.profitability_attributor is not None

    def test_comprehensive_analysis(self, mock_matched_trades, price_data_dict, volume_data_dict):
        """Test comprehensive analysis functionality"""
        ai = AdvancedIntelligenceEnhancement()
        results = ai.analyze_all(mock_matched_trades, price_data_dict, volume_data_dict)

        assert "fee_analysis" in results
        assert len(results["fee_analysis"]) > 0
        assert "market_analysis" in results
        assert len(results["market_analysis"]) > 0
        assert "symbol_analysis" in results
        assert len(results["symbol_analysis"]) > 0
        assert "profitability_attribution" in results
        assert len(results["profitability_attribution"]) > 0
        assert "correlation_matrix" in results
        assert results["correlation_matrix"] is not None

    def test_report_generation(self, mock_matched_trades, price_data_dict, volume_data_dict):
        """Test comprehensive report generation"""
        ai = AdvancedIntelligenceEnhancement()
        analysis_results = ai.analyze_all(mock_matched_trades, price_data_dict, volume_data_dict)
        report = ai.generate_comprehensive_report(analysis_results)

        assert "summary" in report
        assert "detailed_analysis" in report
        assert report["summary"]["analysis_complete"] == True
        assert report["summary"]["symbols_analyzed"] > 0

    def test_analysis_with_real_data(self):
        """Test analysis with real (simulated) data"""
        # Create realistic price data
        dates = pd.date_range(start="2024-01-01", periods=200, freq="h")

        # Simulate BTC price with trend and volatility
        btc_prices = np.cumsum(np.random.randn(200) * 0.001 + 0.0015) + 45000
        btc_volumes = np.random.randint(50000, 200000, size=200)

        # Simulate ETH price (correlated with BTC)
        eth_prices = (
            np.cumsum(np.random.randn(200) * 0.001 + 0.0012) * 0.05 + btc_prices * 0.04 + 2500
        )
        eth_volumes = np.random.randint(20000, 100000, size=200)

        price_data = {
            "BTC": pd.Series(btc_prices, index=dates),
            "ETH": pd.Series(eth_prices, index=dates),
        }

        volume_data = {
            "BTC": pd.Series(btc_volumes, index=dates),
            "ETH": pd.Series(eth_volumes, index=dates),
        }

        # Create mock trades
        class MockTrade:
            def __init__(self, symbol, net_pnl, fees, gross_pnl, pnl_pct):
                self.buy_trade = type("obj", (object,), {"symbol": symbol})
                self.sell_trade = type("obj", (object,), {"symbol": symbol})
                self.net_pnl = net_pnl
                self.fees = fees
                self.gross_pnl = gross_pnl
                self.pnl_pct = pnl_pct
                self.quantity = 1
                self.entry_price = 45000
                self.exit_price = 45500

        trades = [
            MockTrade("BTC", 45.5, 0.45, 46, 1.0),
            MockTrade("BTC", 52.8, 0.48, 53.3, 1.15),
            MockTrade("ETH", 18.5, 0.18, 18.7, 0.75),
            MockTrade("ETH", 22.3, 0.21, 22.5, 0.9),
        ]

        ai = AdvancedIntelligenceEnhancement()
        results = ai.analyze_all(trades, price_data, volume_data)

        # Verify comprehensive analysis
        assert "BTC" in [s["symbol"] for s in results["symbol_analysis"]]
        assert "ETH" in [s["symbol"] for s in results["symbol_analysis"]]

        # Check correlation between BTC and ETH
        correlation_matrix = pd.DataFrame(results["correlation_matrix"])
        assert correlation_matrix.loc["BTC", "ETH"] > 0.5
        assert correlation_matrix.loc["ETH", "BTC"] > 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
