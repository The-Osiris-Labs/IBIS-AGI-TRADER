"""
Tests for IBIS Dynamic TP/SL System
"""

import unittest
from datetime import datetime, timedelta
from ibis.core.risk_manager import RiskManager, RiskParams
from ibis.database.db import IbisDB


class TestDynamicTPSL(unittest.TestCase):
    """Tests for the dynamic TP/SL calculation system"""

    def setUp(self):
        """Set up test environment"""
        self.risk_params = RiskParams()
        self.risk_manager = RiskManager(self.risk_params)
        self.db = IbisDB()
        self.risk_manager.set_database(self.db)

        # Sample data
        self.entry_price = 100.0
        self.volatility = 0.08
        self.atr = 2.5
        self.support_level = 95.0
        self.resistance_level = 108.0
        self.trend_strength = 0.6
        self.symbol = "BTC"
        self.market_regime = "VOLATILE"
        self.price_history = [
            100,
            101,
            102,
            103,
            104,
            105,
            104,
            103,
            102,
            101,
            100,
            99,
            98,
            97,
            96,
            95,
            96,
            97,
            98,
            99,
        ]

    def test_calculate_stop_loss_basic(self):
        """Test basic stop loss calculation"""
        stop_loss = self.risk_manager.calculate_stop_loss(
            self.entry_price,
            self.volatility,
            self.atr,
            self.support_level,
            self.trend_strength,
            self.symbol,
            self.market_regime,
            self.price_history,
        )

        self.assertIsInstance(stop_loss, float)
        self.assertGreater(stop_loss, 0)
        self.assertLess(stop_loss, self.entry_price)

    def test_calculate_stop_loss_with_regime(self):
        """Test stop loss calculation with different market regimes"""
        regimes = ["NORMAL", "VOLATILE", "STRONG_BULL", "STRONG_BEAR"]
        sl_values = []

        for regime in regimes:
            sl = self.risk_manager.calculate_stop_loss(
                self.entry_price,
                self.volatility,
                self.atr,
                self.support_level,
                self.trend_strength,
                self.symbol,
                regime,
                self.price_history,
            )
            sl_values.append(sl)

        # Volatile regime should have wider or equal stop loss
        self.assertLessEqual(
            sl_values[regimes.index("VOLATILE")], sl_values[regimes.index("NORMAL")]
        )
        # Strong bull should have tighter or equal stop loss
        self.assertGreaterEqual(
            sl_values[regimes.index("STRONG_BULL")], sl_values[regimes.index("NORMAL")]
        )

    def test_calculate_take_profit_basic(self):
        """Test basic take profit calculation"""
        stop_loss = self.risk_manager.calculate_stop_loss(
            self.entry_price,
            self.volatility,
            self.atr,
            self.support_level,
            self.trend_strength,
            self.symbol,
            self.market_regime,
            self.price_history,
        )

        take_profit = self.risk_manager.calculate_take_profit(
            self.entry_price,
            stop_loss,
            None,
            self.resistance_level,
            self.trend_strength,
            self.symbol,
            self.market_regime,
            self.price_history,
        )

        # Test multiple TP levels
        self.assertIsInstance(take_profit, list)
        self.assertGreater(len(take_profit), 0)
        for level in take_profit:
            self.assertIsInstance(level, float)
            self.assertGreater(level, self.entry_price)

        # Test single TP level
        single_tp = self.risk_manager.calculate_take_profit(
            self.entry_price,
            stop_loss,
            None,
            self.resistance_level,
            self.trend_strength,
            self.symbol,
            self.market_regime,
            self.price_history,
            return_multiple_levels=False,
        )
        self.assertIsInstance(single_tp, float)
        self.assertGreater(single_tp, self.entry_price)

    def test_calculate_trailing_stop(self):
        """Test trailing stop calculation"""
        # Test with profit (should activate)
        trailing_stop = self.risk_manager.calculate_trailing_stop(
            self.entry_price, 105.0, 106.0, self.volatility, self.atr, self.symbol
        )

        self.assertIsInstance(trailing_stop, float)
        self.assertGreater(trailing_stop, self.entry_price)

        # Test without profit (should not activate)
        trailing_stop = self.risk_manager.calculate_trailing_stop(
            self.entry_price, 100.5, 100.5, self.volatility, self.atr, self.symbol
        )

        self.assertIsNone(trailing_stop)

    def test_fee_rates_update(self):
        """Test fee rates update from database"""
        # Should not raise exceptions
        self.risk_manager.update_fee_rates(days=7)

    def test_get_fee_rates(self):
        """Test fee rates retrieval"""
        fee_rates = self.risk_manager._get_fee_rates(self.symbol, days=7)

        self.assertIn("maker", fee_rates)
        self.assertIn("taker", fee_rates)
        self.assertGreaterEqual(fee_rates["maker"], 0)
        self.assertLessEqual(fee_rates["maker"], 0.05)
        self.assertGreaterEqual(fee_rates["taker"], 0)
        self.assertLessEqual(fee_rates["taker"], 0.05)

    def test_position_size_calculation(self):
        """Test position size calculation with dynamic SL"""
        stop_loss = self.risk_manager.calculate_stop_loss(
            self.entry_price,
            self.volatility,
            self.atr,
            self.support_level,
            self.trend_strength,
            self.symbol,
            self.market_regime,
            self.price_history,
        )

        quantity, position_value, risk_amount = self.risk_manager.calculate_position_size(
            1000.0, self.entry_price, stop_loss
        )

        self.assertGreater(quantity, 0)
        self.assertGreater(position_value, 0)
        self.assertGreater(risk_amount, 0)
        self.assertLessEqual(position_value, self.risk_params.max_position_size)
        self.assertGreaterEqual(position_value, self.risk_params.min_position_size)

    def test_risk_calculations(self):
        """Test comprehensive risk calculations"""
        stop_loss = self.risk_manager.calculate_stop_loss(
            self.entry_price,
            self.volatility,
            self.atr,
            self.support_level,
            self.trend_strength,
            self.symbol,
            self.market_regime,
            self.price_history,
        )

        take_profit = self.risk_manager.calculate_take_profit(
            self.entry_price,
            stop_loss,
            None,
            self.resistance_level,
            self.trend_strength,
            self.symbol,
            self.market_regime,
            self.price_history,
        )

        # Test position assessment
        position_risk = self.risk_manager.assess_position_risk(
            self.symbol, 0.1, self.entry_price, self.entry_price, stop_loss, take_profit, 1000.0
        )

        self.assertEqual(position_risk.symbol, self.symbol)
        self.assertEqual(position_risk.entry_price, self.entry_price)
        self.assertGreater(position_risk.risk_reward, 0)

    def test_portfolio_risk_assessment(self):
        """Test portfolio risk assessment"""
        stop_loss = self.risk_manager.calculate_stop_loss(
            self.entry_price,
            self.volatility,
            self.atr,
            self.support_level,
            self.trend_strength,
            self.symbol,
            self.market_regime,
            self.price_history,
        )

        take_profit = self.risk_manager.calculate_take_profit(
            self.entry_price,
            stop_loss,
            None,
            self.resistance_level,
            self.trend_strength,
            self.symbol,
            self.market_regime,
            self.price_history,
        )

        # Calculate appropriate position size
        quantity, position_value, risk_amount = self.risk_manager.calculate_position_size(
            1000.0, self.entry_price, stop_loss
        )

        position = self.risk_manager.assess_position_risk(
            self.symbol,
            quantity,
            self.entry_price,
            self.entry_price,
            stop_loss,
            take_profit,
            1000.0,
        )

        portfolio = self.risk_manager.assess_portfolio_risk([position], 1000.0, 1000.0)

        self.assertEqual(portfolio.positions_count, 1)
        self.assertGreater(portfolio.total_value, 0)
        self.assertLessEqual(portfolio.total_exposure, 1)


if __name__ == "__main__":
    unittest.main()
