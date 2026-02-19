"""
Advanced Intelligence Enhancement Module for IBIS
=================================================

This module enhances the IBIS system's capabilities in four key areas:
1. Fee Analysis Enhancement - Real-time tracking, optimization, historical trends
2. Market Movement Understanding - Trend detection, volatility, regime classification
3. Symbol Movement Analysis - Symbol-specific patterns, volatility, correlation
4. Profitability Attribution - Fee impact, market conditions, regime performance

Key Features:
- Real-time fee tracking and analysis
- Fee optimization recommendations
- Historical fee trend analysis
- Enhanced trend detection and strength measurement
- Multi-timeframe volatility analysis
- Market regime classification improvements
- Support/resistance level detection
- Price action pattern recognition
- Symbol-specific trend patterns
- Volatility profiling per symbol
- Correlation analysis between symbols
- Volume and liquidity analysis
- Recent price action behavior
- Profitability attribution by fee impact, market conditions, and regimes
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from scipy import stats
from ibis.core.logging_config import get_logger

logger = get_logger(__name__)


# ============================================
# Fee Analysis Enhancement
# ============================================


@dataclass
class FeeAnalysisResult:
    """Comprehensive fee analysis results"""

    symbol: str
    total_fees: float
    avg_fee_rate: float
    fee_impact_pct: float
    fee_trend: float
    optimal_fee_rate: float
    optimization_savings: float
    fee_by_trade_count: List[Tuple[int, float]]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class FeeAnalyzer:
    """Advanced fee analysis and optimization engine"""

    def __init__(self, pnl_tracker=None):
        self.pnl_tracker = pnl_tracker
        self.fee_history = []
        self.symbol_fee_profiles = {}

    def analyze_fee_impact(self, matched_trades: List, symbol: str = None) -> FeeAnalysisResult:
        """Analyze fee impact on profitability"""
        if symbol:
            trades = [t for t in matched_trades if t.buy_trade.symbol == symbol]
        else:
            trades = matched_trades

        if not trades:
            return FeeAnalysisResult(
                symbol=symbol or "all",
                total_fees=0,
                avg_fee_rate=0,
                fee_impact_pct=0,
                fee_trend=0,
                optimal_fee_rate=0.001,
                optimization_savings=0,
                fee_by_trade_count=[],
            )

        total_fees = sum(t.fees for t in trades)
        total_net_pnl = sum(t.net_pnl for t in trades)
        total_gross_pnl = sum(t.gross_pnl for t in trades)

        fee_impact_pct = (total_fees / abs(total_gross_pnl)) * 100 if total_gross_pnl != 0 else 0

        # Calculate fee trend
        fee_trends = []
        for i in range(1, len(trades)):
            current_fee = trades[i].fees
            previous_fee = trades[i - 1].fees
            if previous_fee > 0:
                trend = (current_fee - previous_fee) / previous_fee
                fee_trends.append(trend)

        fee_trend = np.mean(fee_trends) if fee_trends else 0

        # Calculate optimal fee rate using historical data
        avg_fee_rate = self._calculate_optimal_fee_rate(trades)
        optimal_fee_rate = max(0.0005, avg_fee_rate * 0.8)  # 20% reduction target
        optimization_savings = total_fees * 0.2  # Potential 20% savings

        # Fee by trade count for trend analysis
        fee_by_trade_count = []
        cumulative_fee = 0
        for i, trade in enumerate(trades):
            cumulative_fee += trade.fees
            fee_by_trade_count.append((i + 1, cumulative_fee))

        return FeeAnalysisResult(
            symbol=symbol or "all",
            total_fees=total_fees,
            avg_fee_rate=avg_fee_rate,
            fee_impact_pct=fee_impact_pct,
            fee_trend=fee_trend,
            optimal_fee_rate=optimal_fee_rate,
            optimization_savings=optimization_savings,
            fee_by_trade_count=fee_by_trade_count,
        )

    def _calculate_optimal_fee_rate(self, trades: List) -> float:
        """Calculate optimal fee rate based on historical data"""
        fee_rates = []
        for trade in trades:
            trade_value = (
                trade.quantity * trade.entry_price + trade.quantity * trade.exit_price
            ) / 2
            if trade_value > 0:
                fee_rate = trade.fees / trade_value
                fee_rates.append(fee_rate)

        if not fee_rates:
            return 0.001  # Default 0.1%

        # Use percentile-based optimal fee rate (25th percentile for minimal fees)
        return np.percentile(fee_rates, 25)

    def get_fee_optimization_recommendations(self, symbol: str = None) -> Dict:
        """Get fee optimization recommendations"""
        if not self.pnl_tracker:
            return {"recommendations": [], "potential_savings": 0}

        symbol_fees = self.pnl_tracker.calculate_average_fees_per_symbol()

        if symbol and symbol not in symbol_fees:
            return {"recommendations": [], "potential_savings": 0}

        recommendations = []

        if symbol:
            fee_data = symbol_fees[symbol]
            recommendations.extend(self._generate_symbol_recommendations(symbol, fee_data))
        else:
            for sym, fee_data in symbol_fees.items():
                recommendations.extend(self._generate_symbol_recommendations(sym, fee_data))

        total_savings = sum(rec.get("potential_savings", 0) for rec in recommendations)

        return {"recommendations": recommendations, "total_potential_savings": total_savings}

    def _generate_symbol_recommendations(self, symbol: str, fee_data: Dict) -> List[Dict]:
        """Generate symbol-specific fee optimization recommendations"""
        recommendations = []

        # Check if fees are higher than expected
        expected_taker_fee = 0.001  # 0.1% default
        if fee_data["taker"] > expected_taker_fee * 1.2:
            recommendations.append(
                {
                    "symbol": symbol,
                    "type": "taker_fee_reduction",
                    "current_rate": fee_data["taker"],
                    "target_rate": expected_taker_fee,
                    "potential_savings": fee_data["taker"] - expected_taker_fee,
                    "action": "Negotiate lower taker fees or switch exchanges",
                    "priority": "high",
                }
            )

        if fee_data["maker"] > 0.0005:  # 0.05%
            recommendations.append(
                {
                    "symbol": symbol,
                    "type": "maker_fee_reduction",
                    "current_rate": fee_data["maker"],
                    "target_rate": 0.0005,
                    "potential_savings": fee_data["maker"] - 0.0005,
                    "action": "Optimize order placement to use maker orders more frequently",
                    "priority": "medium",
                }
            )

        if fee_data["count"] > 50:
            recommendations.append(
                {
                    "symbol": symbol,
                    "type": "volume_discount",
                    "current_volume": fee_data["count"],
                    "target_volume": fee_data["count"] * 1.5,
                    "potential_savings": 0.0002,
                    "action": "Increase trading volume to qualify for volume-based discounts",
                    "priority": "low",
                }
            )

        return recommendations


# ============================================
# Market Movement Understanding
# ============================================


@dataclass
class MarketRegime:
    """Market regime classification"""

    regime_type: str
    confidence: float
    volatility: float
    trend_strength: float
    volume_profile: str
    duration: float


class MarketMovementAnalyzer:
    """Enhanced market movement and regime analysis"""

    def __init__(self):
        self.trend_strength_cache = {}
        self.regime_cache = {}

    def detect_trend_strength(self, price_data: pd.Series, timeframe: str = "1h") -> Dict:
        """Detect trend direction and strength using multiple indicators"""
        if price_data.empty:
            return {"direction": "neutral", "strength": 0, "confidence": 0.5}

        # Calculate trend indicators
        ema_50 = price_data.ewm(span=50).mean()
        ema_200 = price_data.ewm(span=200).mean()
        rsi = self._calculate_rsi(price_data)
        macd, signal, histogram = self._calculate_macd(price_data)

        # Trend direction and strength
        trend_score = 0
        confidence = 0.5

        # EMA crossover strategy
        if ema_50.iloc[-1] > ema_200.iloc[-1]:
            trend_score += 35
            if ema_50.diff().iloc[-1] > 0:
                trend_score += 25
        elif ema_50.iloc[-1] < ema_200.iloc[-1]:
            trend_score -= 35
            if ema_50.diff().iloc[-1] < 0:
                trend_score -= 25

        # RSI strength
        if rsi > 65:
            trend_score += 25
        elif rsi < 35:
            trend_score -= 25

        # MACD strength
        if macd[-1] > signal[-1] and histogram[-1] > 0:
            trend_score += 25
        elif macd[-1] < signal[-1] and histogram[-1] < 0:
            trend_score -= 25

        # Normalize trend strength
        trend_strength = max(0, min(100, abs(trend_score)))
        direction = "bullish" if trend_score > 0 else "bearish" if trend_score < 0 else "neutral"

        # Calculate confidence based on indicator agreement
        agreement_count = 0
        if direction == "bullish":
            if ema_50.iloc[-1] > ema_200.iloc[-1]:
                agreement_count += 1
            if rsi > 50:
                agreement_count += 1
            if macd[-1] > signal[-1]:
                agreement_count += 1
        elif direction == "bearish":
            if ema_50.iloc[-1] < ema_200.iloc[-1]:
                agreement_count += 1
            if rsi < 50:
                agreement_count += 1
            if macd[-1] < signal[-1]:
                agreement_count += 1

        confidence = agreement_count / 3

        return {
            "direction": direction,
            "strength": trend_strength,
            "confidence": confidence,
            "rsi": rsi,
            "macd": macd[-1],
            "signal": signal[-1],
            "ema_50": ema_50.iloc[-1],
            "ema_200": ema_200.iloc[-1],
        }

    def classify_market_regime(self, price_data: pd.Series, volume_data: pd.Series) -> MarketRegime:
        """Classify market regime using volatility, trend, and volume"""
        if price_data.empty or volume_data.empty:
            return MarketRegime(
                regime_type="neutral",
                confidence=0.5,
                volatility=0.05,
                trend_strength=0,
                volume_profile="average",
                duration=0,
            )

        # Calculate volatility measures
        returns = price_data.pct_change().dropna()
        volatility = returns.std() * np.sqrt(24)  # Annualized volatility

        # Calculate trend strength
        trend_result = self.detect_trend_strength(price_data)
        trend_strength = trend_result["strength"]

        # Volume profile
        avg_volume = volume_data.mean()
        current_volume = volume_data.iloc[-1]
        volume_ratio = current_volume / avg_volume

        # Regime classification logic
        if volatility > 0.08 and trend_strength < 30:
            regime_type = "volatile"
        elif volatility < 0.04 and trend_strength < 20:
            regime_type = "stable"
        elif trend_strength > 60 and volatility < 0.06:
            regime_type = "strong_trend"
        elif trend_strength > 40 and volatility < 0.07:
            regime_type = "weak_trend"
        else:
            regime_type = "neutral"

        # Volume profile classification
        if volume_ratio > 1.5:
            volume_profile = "high"
        elif volume_ratio < 0.5:
            volume_profile = "low"
        else:
            volume_profile = "average"

        return MarketRegime(
            regime_type=regime_type,
            confidence=trend_result["confidence"],
            volatility=volatility,
            trend_strength=trend_strength,
            volume_profile=volume_profile,
            duration=len(price_data),
        )

    def detect_support_resistance(self, price_data: pd.Series, lookback: int = 50) -> Dict:
        """Detect support and resistance levels using price action"""
        if len(price_data) < lookback:
            return {"support": [], "resistance": []}

        prices = price_data.tail(lookback).values
        volatility = np.std(prices)

        # Calculate potential support/resistance levels
        support_levels = []
        resistance_levels = []

        # Look for swing highs and lows
        for i in range(2, len(prices) - 2):
            # Swing high (higher than neighbors)
            if (
                prices[i] > prices[i - 1]
                and prices[i] > prices[i - 2]
                and prices[i] > prices[i + 1]
                and prices[i] > prices[i + 2]
            ):
                resistance_levels.append(prices[i])

            # Swing low (lower than neighbors)
            if (
                prices[i] < prices[i - 1]
                and prices[i] < prices[i - 2]
                and prices[i] < prices[i + 1]
                and prices[i] < prices[i + 2]
            ):
                support_levels.append(prices[i])

        # Cluster levels within volatility range
        clustered_support = self._cluster_levels(support_levels, volatility * 0.5)
        clustered_resistance = self._cluster_levels(resistance_levels, volatility * 0.5)

        return {
            "support": sorted(clustered_support),
            "resistance": sorted(clustered_resistance),
            "volatility": volatility,
        }

    def _cluster_levels(self, levels: List[float], tolerance: float) -> List[float]:
        """Cluster similar price levels"""
        if not levels:
            return []

        clusters = []
        levels_sorted = sorted(levels)

        current_cluster = [levels_sorted[0]]

        for level in levels_sorted[1:]:
            if level - current_cluster[-1] <= tolerance:
                current_cluster.append(level)
            else:
                clusters.append(np.mean(current_cluster))
                current_cluster = [level]

        if current_cluster:
            clusters.append(np.mean(current_cluster))

        return clusters

    def analyze_price_action_patterns(self, price_data: pd.Series) -> List[Dict]:
        """Recognize common price action patterns"""
        patterns = []

        if len(price_data) < 10:
            return patterns

        # Simple pattern recognition
        recent_prices = price_data.tail(5)

        # Bullish engulfing pattern
        if (
            recent_prices.iloc[-2] < recent_prices.iloc[-3]
            and recent_prices.iloc[-1] > recent_prices.iloc[-2]
            and recent_prices.iloc[-1] > recent_prices.iloc[-3]
        ):
            patterns.append(
                {
                    "name": "bullish_engulfing",
                    "confidence": 0.7,
                    "direction": "bullish",
                    "pattern_length": 2,
                }
            )

        # Bearish engulfing pattern
        if (
            recent_prices.iloc[-2] > recent_prices.iloc[-3]
            and recent_prices.iloc[-1] < recent_prices.iloc[-2]
            and recent_prices.iloc[-1] < recent_prices.iloc[-3]
        ):
            patterns.append(
                {
                    "name": "bearish_engulfing",
                    "confidence": 0.7,
                    "direction": "bearish",
                    "pattern_length": 2,
                }
            )

        # Hammer pattern
        if (
            recent_prices.iloc[-1] < recent_prices.iloc[-2]
            and recent_prices.iloc[-1] < recent_prices.iloc[-3]
            and (recent_prices.iloc[-1] - min(recent_prices.tail(3)))
            / (max(recent_prices.tail(3)) - min(recent_prices.tail(3)))
            < 0.2
        ):
            patterns.append(
                {"name": "hammer", "confidence": 0.6, "direction": "bullish", "pattern_length": 3}
            )

        return patterns

    def _calculate_rsi(self, price_data: pd.Series, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        delta = price_data.diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)

        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi.iloc[-1]

    def _calculate_macd(
        self, price_data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Tuple:
        """Calculate MACD indicator"""
        ema_fast = price_data.ewm(span=fast).mean()
        ema_slow = price_data.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line

        return macd.values, signal_line.values, histogram.values


# ============================================
# Symbol Movement Analysis
# ============================================


@dataclass
class SymbolMovementProfile:
    """Symbol-specific movement profile"""

    symbol: str
    trend_pattern: str
    volatility_profile: str
    correlation: Dict[str, float]
    volume_profile: str
    liquidity_score: float
    recent_price_behavior: str


class SymbolMovementAnalyzer:
    """Advanced symbol-specific movement analysis"""

    def __init__(self):
        self.symbol_profiles = {}
        self.correlation_matrix = None

    def analyze_symbol_movement(
        self, symbol: str, price_data: pd.Series, volume_data: pd.Series, other_symbols: Dict = None
    ) -> SymbolMovementProfile:
        """Analyze symbol-specific movement patterns"""
        if price_data.empty or volume_data.empty:
            return SymbolMovementProfile(
                symbol=symbol,
                trend_pattern="unknown",
                volatility_profile="average",
                correlation={},
                volume_profile="average",
                liquidity_score=0.5,
                recent_price_behavior="neutral",
            )

        # Trend pattern analysis
        trend_result = MarketMovementAnalyzer().detect_trend_strength(price_data)
        trend_pattern = self._classify_trend_pattern(price_data)

        # Volatility profile
        volatility_profile = self._classify_volatility_profile(price_data)

        # Volume profile
        volume_profile = self._classify_volume_profile(volume_data)

        # Liquidity score
        liquidity_score = self._calculate_liquidity_score(volume_data, price_data)

        # Recent price behavior
        recent_behavior = self._analyze_recent_price_behavior(price_data)

        # Correlation analysis with other symbols
        correlation = {}
        if other_symbols:
            correlation = self._calculate_correlations(symbol, price_data, other_symbols)

        return SymbolMovementProfile(
            symbol=symbol,
            trend_pattern=trend_pattern,
            volatility_profile=volatility_profile,
            correlation=correlation,
            volume_profile=volume_profile,
            liquidity_score=liquidity_score,
            recent_price_behavior=recent_behavior,
        )

    def _classify_trend_pattern(self, price_data: pd.Series) -> str:
        """Classify trend pattern type"""
        returns = price_data.pct_change().dropna()
        trend_strength = abs(returns.mean() / returns.std())

        if trend_strength > 0.15:
            return "strong_trend"
        elif trend_strength > 0.08:
            return "weak_trend"
        else:
            return "sideways"

    def _classify_volatility_profile(self, price_data: pd.Series) -> str:
        """Classify volatility profile"""
        returns = price_data.pct_change().dropna()
        volatility = returns.std()

        if volatility > 0.02:
            return "high"
        elif volatility < 0.008:
            return "low"
        else:
            return "average"

    def _classify_volume_profile(self, volume_data: pd.Series) -> str:
        """Classify volume profile"""
        avg_volume = volume_data.mean()
        volume_std = volume_data.std()

        current_volume = volume_data.iloc[-1]
        volume_zscore = (current_volume - avg_volume) / volume_std

        if volume_zscore > 2:
            return "high"
        elif volume_zscore < -1:
            return "low"
        else:
            return "average"

    def _calculate_liquidity_score(self, volume_data: pd.Series, price_data: pd.Series) -> float:
        """Calculate liquidity score based on volume and price stability"""
        avg_volume = volume_data.mean()
        volume_std = volume_data.std()

        # Volume consistency score
        volume_consistency = 1 - (volume_std / avg_volume) if avg_volume > 0 else 0.5

        # Price stability score
        returns = price_data.pct_change().dropna()
        price_stability = 1 - returns.std()

        return (volume_consistency + price_stability) / 2

    def _analyze_recent_price_behavior(self, price_data: pd.Series) -> str:
        """Analyze recent price behavior"""
        recent_prices = price_data.tail(10)

        # Price movement characteristics
        max_price = recent_prices.max()
        min_price = recent_prices.min()
        current_price = recent_prices.iloc[-1]

        price_range = max_price - min_price
        price_position = (current_price - min_price) / price_range if price_range > 0 else 0.5

        if price_position > 0.8:
            return "near_high"
        elif price_position < 0.2:
            return "near_low"
        else:
            return "mid_range"

    def _calculate_correlations(
        self, symbol: str, price_data: pd.Series, other_symbols: Dict
    ) -> Dict[str, float]:
        """Calculate correlation with other symbols"""
        correlations = {}

        for other_symbol, other_price_data in other_symbols.items():
            if symbol == other_symbol or other_price_data.empty:
                continue

            # Align price data by index
            combined = pd.DataFrame({symbol: price_data, other_symbol: other_price_data}).dropna()

            if len(combined) < 20:
                continue

            correlation = combined[symbol].corr(combined[other_symbol])
            correlations[other_symbol] = round(correlation, 3)

        return correlations

    def calculate_symbol_correlations(self, symbol_prices: Dict[str, pd.Series]) -> pd.DataFrame:
        """Calculate correlation matrix between symbols"""
        if len(symbol_prices) < 2:
            return pd.DataFrame()

        # Create price DataFrame with symbols as columns
        price_data = []
        symbols = list(symbol_prices.keys())

        # Find common time index
        first_symbol = symbols[0]
        common_index = symbol_prices[first_symbol].index

        for symbol in symbols[1:]:
            common_index = common_index.intersection(symbol_prices[symbol].index)

        if len(common_index) < 20:
            return pd.DataFrame()

        # Create aligned price DataFrame
        price_df = pd.DataFrame()
        for symbol in symbols:
            price_df[symbol] = symbol_prices[symbol].loc[common_index]

        # Calculate correlation matrix
        self.correlation_matrix = price_df.pct_change().dropna().corr()

        return self.correlation_matrix


# ============================================
# Profitability Attribution
# ============================================


@dataclass
class ProfitabilityAttribution:
    """Profitability attribution results"""

    symbol: str
    total_pnl: float
    fee_impact: float
    market_conditions_impact: float
    regime_performance: Dict[str, float]
    risk_adjusted_return: float


class ProfitabilityAttributor:
    """Advanced profitability attribution engine"""

    def __init__(self):
        self.attribution_cache = {}

    def attribute_profitability(
        self, matched_trades: List[Dict], market_conditions: List[Dict], symbol: str = None
    ) -> ProfitabilityAttribution:
        """Attribute profitability to fees, market conditions, and regimes"""
        if symbol:
            trades = [t for t in matched_trades if t.buy_trade.symbol == symbol]
        else:
            trades = matched_trades

        if not trades:
            return ProfitabilityAttribution(
                symbol=symbol or "all",
                total_pnl=0,
                fee_impact=0,
                market_conditions_impact=0,
                regime_performance={},
                risk_adjusted_return=0,
            )

        total_pnl = sum(t.net_pnl for t in trades)
        total_fees = sum(t.fees for t in trades)
        total_gross_pnl = sum(t.gross_pnl for t in trades)

        # Fee impact
        fee_impact = (total_fees / abs(total_gross_pnl)) * 100 if total_gross_pnl != 0 else 0

        # Market conditions impact (simplified)
        market_conditions_impact = self._calculate_market_conditions_impact(
            trades, market_conditions
        )

        # Regime performance
        regime_performance = self._calculate_regime_performance(trades)

        # Risk-adjusted return
        risk_adjusted_return = self._calculate_risk_adjusted_return(trades)

        return ProfitabilityAttribution(
            symbol=symbol or "all",
            total_pnl=total_pnl,
            fee_impact=fee_impact,
            market_conditions_impact=market_conditions_impact,
            regime_performance=regime_performance,
            risk_adjusted_return=risk_adjusted_return,
        )

    def _calculate_market_conditions_impact(
        self, trades: List, market_conditions: List[Dict]
    ) -> float:
        """Calculate market conditions impact on profitability"""
        if not market_conditions:
            return 0

        # Simple correlation between market conditions and trade performance
        condition_scores = []
        trade_returns = []

        for trade, condition in zip(trades, market_conditions):
            if "regime_type" in condition and "strength" in condition:
                # Map regime to score
                regime_score = {
                    "strong_trend": 1,
                    "weak_trend": 0.5,
                    "stable": 0.3,
                    "volatile": -0.2,
                    "neutral": 0,
                }.get(condition["regime_type"], 0)

                condition_scores.append(regime_score)
                trade_returns.append(trade.pnl_pct)

        if len(condition_scores) < 2:
            return 0

        correlation, _ = stats.pearsonr(condition_scores, trade_returns)

        return correlation * 100  # Convert to percentage

    def _calculate_regime_performance(self, trades: List) -> Dict[str, float]:
        """Calculate performance per market regime"""
        regimes = {
            "strong_trend": {"pnl": 0, "count": 0},
            "weak_trend": {"pnl": 0, "count": 0},
            "stable": {"pnl": 0, "count": 0},
            "volatile": {"pnl": 0, "count": 0},
            "neutral": {"pnl": 0, "count": 0},
        }

        # Simple regime classification based on volatility
        for trade in trades:
            # Calculate volatility of the symbol during trade duration
            # In real implementation, this would use historical volatility data
            volatility = 0.05  # Default average volatility

            if volatility > 0.08:
                regime = "volatile"
            elif volatility < 0.04:
                regime = "stable"
            else:
                regime = "neutral"

            regimes[regime]["pnl"] += trade.net_pnl
            regimes[regime]["count"] += 1

        # Calculate average PnL per regime
        regime_performance = {}
        for regime, data in regimes.items():
            if data["count"] > 0:
                regime_performance[regime] = data["pnl"] / data["count"]

        return regime_performance

    def _calculate_risk_adjusted_return(self, trades: List) -> float:
        """Calculate risk-adjusted return (Sharpe ratio)"""
        if len(trades) < 2:
            return 0

        returns = [t.pnl_pct for t in trades]
        avg_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return == 0:
            return 0

        # Assuming risk-free rate is 0 for cryptocurrency
        return avg_return / std_return


# ============================================
# Main Intelligence Enhancement Interface
# ============================================


class AdvancedIntelligenceEnhancement:
    """Main interface for all intelligence enhancements"""

    def __init__(self, pnl_tracker=None):
        self.fee_analyzer = FeeAnalyzer(pnl_tracker)
        self.market_movement_analyzer = MarketMovementAnalyzer()
        self.symbol_movement_analyzer = SymbolMovementAnalyzer()
        self.profitability_attributor = ProfitabilityAttributor()

    def analyze_all(
        self,
        matched_trades: List,
        symbol_prices: Dict[str, pd.Series],
        symbol_volumes: Dict[str, pd.Series],
        market_conditions: List[Dict] = None,
    ) -> Dict:
        """Analyze all aspects of fee, market, and symbol intelligence"""
        if not market_conditions:
            market_conditions = []

        results = {}

        # Fee analysis
        results["fee_analysis"] = []
        symbols = set(t.buy_trade.symbol for t in matched_trades)

        for symbol in symbols:
            fee_result = self.fee_analyzer.analyze_fee_impact(matched_trades, symbol)
            results["fee_analysis"].append(fee_result.__dict__)

        # Market movement analysis
        results["market_analysis"] = {}
        for symbol in symbols:
            if symbol in symbol_prices and symbol in symbol_volumes:
                price_data = symbol_prices[symbol]
                volume_data = symbol_volumes[symbol]

                trend_result = self.market_movement_analyzer.detect_trend_strength(price_data)
                regime = self.market_movement_analyzer.classify_market_regime(
                    price_data, volume_data
                )
                support_resistance = self.market_movement_analyzer.detect_support_resistance(
                    price_data
                )
                price_patterns = self.market_movement_analyzer.analyze_price_action_patterns(
                    price_data
                )

                results["market_analysis"][symbol] = {
                    "trend": trend_result,
                    "regime": regime.__dict__,
                    "support_resistance": support_resistance,
                    "price_patterns": price_patterns,
                }

        # Symbol movement analysis
        results["symbol_analysis"] = []
        other_symbols = {
            s: symbol_prices[s]
            for s in symbols
            if s in symbol_prices and not symbol_prices[s].empty
        }

        for symbol in symbols:
            if (
                symbol in symbol_prices
                and symbol in symbol_volumes
                and not symbol_prices[symbol].empty
                and not symbol_volumes[symbol].empty
            ):
                symbol_profile = self.symbol_movement_analyzer.analyze_symbol_movement(
                    symbol, symbol_prices[symbol], symbol_volumes[symbol], other_symbols
                )
                results["symbol_analysis"].append(symbol_profile.__dict__)

        # Profitability attribution
        results["profitability_attribution"] = []
        for symbol in symbols:
            attribution = self.profitability_attributor.attribute_profitability(
                matched_trades, market_conditions, symbol
            )
            results["profitability_attribution"].append(attribution.__dict__)

        # Correlation matrix
        results["correlation_matrix"] = None
        if len(symbol_prices) >= 2:
            correlation_matrix = self.symbol_movement_analyzer.calculate_symbol_correlations(
                symbol_prices
            )
            if not correlation_matrix.empty:
                results["correlation_matrix"] = correlation_matrix.to_dict()

        return results

    def generate_comprehensive_report(self, analysis_results: Dict) -> Dict:
        """Generate comprehensive report from analysis results"""
        report = {"summary": {}, "detailed_analysis": analysis_results}

        # Calculate summary statistics
        total_trades = 0
        total_pnl = 0
        total_fees = 0

        if "profitability_attribution" in analysis_results:
            for attr in analysis_results["profitability_attribution"]:
                total_pnl += attr["total_pnl"]

        if "fee_analysis" in analysis_results:
            for fee in analysis_results["fee_analysis"]:
                total_fees += fee["total_fees"]

        report["summary"] = {
            "total_pnl": total_pnl,
            "total_fees": total_fees,
            "fee_impact_pct": (total_fees / abs(total_pnl)) * 100 if total_pnl != 0 else 0,
            "symbols_analyzed": len(analysis_results.get("symbol_analysis", [])),
            "analysis_complete": True,
        }

        return report


# Global instance
advanced_intelligence = AdvancedIntelligenceEnhancement()
