"""
IBIS Market Intelligence Module
By TheOsirisLabs.com | Founder: Youssef SalahEldin

True AGI Trading requires Multi-Dimensional Market Analysis:
1. On-Chain Data (whale movements, exchange flows)
2. Sentiment Analysis (social, news, FGI)
3. Order Flow Analysis (real-time tape reading)
4. Volume Profile (smart money tracking)
5. Cross-Asset Correlation
6. Low Cap Coin Discovery
7. Market Regime Detection
8. Advanced Risk Management
9. Self-Learning & Adaptation
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict


class AnalysisDimension(Enum):
    """Market analysis dimensions."""

    PRICE_ACTION = "price_action"
    VOLUME_PROFILE = "volume_profile"
    ORDER_FLOW = "order_flow"
    SENTIMENT = "sentiment"
    ON_CHAIN = "on_chain"
    CORRELATION = "correlation"
    REGIME = "regime"
    RISK = "risk"


@dataclass
class MarketContext:
    """Market context for analysis."""

    symbol: str = ""
    price: float = 0.0
    price_change_24h: float = 0.0
    price_change_1h: float = 0.0
    volume_24h: float = 0.0
    volatility_1h: float = 0.0
    volatility_24h: float = 0.0
    trend_strength: float = 50.0
    order_flow_delta: float = 0.0
    sentiment_score: float = 0.5
    fear_greed_index: int = 50
    funding_rate: float = 0.0
    long_short_ratio: float = 1.0
    exchange_flow: float = 0.0
    whale_activity: str = "NEUTRAL"
    timestamp: int = 0

    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "price": self.price,
            "price_change_24h": self.price_change_24h,
            "price_change_1h": self.price_change_1h,
            "volume_24h": self.volume_24h,
            "volatility_1h": self.volatility_1h,
            "volatility_24h": self.volatility_24h,
            "trend_strength": self.trend_strength,
            "order_flow_delta": self.order_flow_delta,
            "sentiment_score": self.sentiment_score,
            "fear_greed_index": self.fear_greed_index,
            "funding_rate": self.funding_rate,
            "long_short_ratio": self.long_short_ratio,
            "exchange_flow": self.exchange_flow,
            "whale_activity": self.whale_activity,
            "timestamp": self.timestamp,
        }


@dataclass
class MarketInsight:
    """Multi-dimensional market insight."""

    dimension: str
    signal: str  # BULLISH, BEARISH, NEUTRAL
    confidence: float
    strength: float  # 0-1
    key_levels: List[float] = field(default_factory=list)
    volume_profile: Dict = field(default_factory=dict)
    order_flow: Dict = field(default_factory=dict)
    sentiment: Dict = field(default_factory=dict)
    on_chain: Dict = field(default_factory=dict)
    correlations: Dict = field(default_factory=dict)
    reasoning: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CoinOpportunity:
    """Low cap coin opportunity."""

    symbol: str
    name: str
    market_cap: float
    volume_24h: float
    volume_mc_ratio: float  # Volume / Market Cap
    price_change_24h: float
    price_change_1h: float
    volatility: float
    liquidity_score: float
    whale_activity: str  # ACCUMULATING, DISTRIBUTING, NEUTRAL
    social_score: float
    setup_quality: float  # Technical setup quality
    risk_score: float
    overall_score: float
    entry_zone: float
    target_1: float
    target_2: float
    stop_loss: float
    reasoning: str = ""


@dataclass
class OrderFlowData:
    """Real-time order flow analysis."""

    buying_pressure: float
    selling_pressure: float
    delta: float  # Buy - Sell pressure
    cumulative_delta: float
    absorption_zones: List[float] = field(default_factory=list)
    exhaustion_zones: List[float] = field(default_factory=list)
    bid_ask_imbalance: float = 0.0
    tape_reading: str = ""


@dataclass
class VolumeProfile:
    """Volume profile analysis."""

    poc: float  # Point of Control
    va_high: float  # Value Area High
    va_low: float  # Value Area Low
    volume_by_price: Dict[float, float] = field(default_factory=dict)
    accepted_price: float = 0.0
    rejected_price: float = 0.0


@dataclass
class SentimentData:
    """Multi-source sentiment."""

    fear_greed_index: int  # 0-100
    fear_greed_class: str  # EXTREME_FEAR, FEAR, NEUTRAL, GREED, EXTREME_GREED
    social_volume: float  # Social media activity
    social_sentiment: float  # -1 to 1
    news_sentiment: float  # -1 to 1
    funding_rate: float
    long_short_ratio: float
    whale_sentiment: float  # -1 to 1


@dataclass
class OnChainData:
    """On-chain metrics."""

    exchange_inflow_24h: float
    exchange_outflow_24h: float
    net_exchange_flow: float
    whale_transactions: int
    whale_volume: float
    holder_growth: float
    burn_rate: float
    nvt_ratio: float
    mvrv_ratio: float
    funding_rate: float
    whale_activity: str = "NEUTRAL"


class MarketIntelligence:
    """
    Multi-dimensional market intelligence for IBIS.
    Analyzes: Price, Volume, Order Flow, Sentiment, On-Chain, Correlations
    """

    def __init__(self):
        self.analysis_history: List[MarketInsight] = []
        self.correlation_matrix: Dict[str, Dict[str, float]] = {}
        self.low_cap_universe: List[CoinOpportunity] = []
        self.regime_history: List[Dict] = []

    async def comprehensive_analysis(
        self,
        symbol: str,
        price: float,
        price_change: float,
        volume: float,
        highs: List[float],
        lows: List[float],
        closes: List[float],
        volumes: List[float],
        order_flow: Optional[OrderFlowData],
        volume_profile: Optional[VolumeProfile],
        sentiment: Optional[SentimentData],
        on_chain: Optional[OnChainData],
        related_symbols: List[str] = None,
    ) -> MarketInsight:
        """
        Comprehensive multi-dimensional market analysis.
        """
        if order_flow is None:
            order_flow = OrderFlowData(
                buying_pressure=0.0,
                selling_pressure=0.0,
                delta=0.0,
                cumulative_delta=0.0,
                absorption_zones=[],
                exhaustion_zones=[],
                bid_ask_imbalance=0.0,
                tape_reading="NEUTRAL",
            )
        if volume_profile is None:
            volume_profile = VolumeProfile(
                poc=price,
                va_high=max(highs) if highs else price,
                va_low=min(lows) if lows else price,
                volume_by_price={},
                accepted_price=price,
                rejected_price=price,
            )
        if sentiment is None:
            sentiment = SentimentData(
                fear_greed_index=50,
                fear_greed_class="NEUTRAL",
                social_volume=0.0,
                social_sentiment=0.0,
                news_sentiment=0.0,
                funding_rate=0.0,
                long_short_ratio=1.0,
                whale_sentiment=0.0,
            )
        if on_chain is None:
            on_chain = OnChainData(
                exchange_inflow_24h=0.0,
                exchange_outflow_24h=0.0,
                net_exchange_flow=0.0,
                whale_transactions=0,
                whale_volume=0.0,
                whale_activity="NEUTRAL",
                holder_growth=0.0,
                burn_rate=0.0,
                nvt_ratio=0.0,
                mvrv_ratio=0.0,
                funding_rate=0.0,
            )
        insight = MarketInsight(
            dimension="COMPREHENSIVE",
            signal="NEUTRAL",
            confidence=0.5,
            strength=0.5,
            order_flow=order_flow.__dict__,
            volume_profile=volume_profile.__dict__,
            sentiment=sentiment.__dict__,
            on_chain=on_chain.__dict__,
        )

        # 1. Price Action Analysis
        price_signal = await self._analyze_price_action(
            price, price_change, highs, lows, closes
        )
        insight.strength += price_signal["strength"] * 0.2

        # 2. Volume Profile Analysis
        volume_signal = await self._analyze_volume_profile(price, volume_profile)
        insight.strength += volume_signal["strength"] * 0.15

        # 3. Order Flow Analysis
        flow_signal = await self._analyze_order_flow(order_flow)
        insight.strength += flow_signal["strength"] * 0.2

        # 4. Sentiment Analysis
        sentiment_signal = await self._analyze_sentiment(sentiment)
        insight.strength += sentiment_signal["strength"] * 0.15

        # 5. On-Chain Analysis
        chain_signal = await self._analyze_on_chain(on_chain)
        insight.strength += chain_signal["strength"] * 0.15

        # 6. Cross-Asset Correlation
        if related_symbols:
            corr_signal = await self._analyze_correlations(
                symbol, related_symbols, price_change
            )
            insight.correlations = corr_signal
            insight.strength += corr_signal.get("strength", 0.5) * 0.15

        # Determine overall signal
        bullish_score = sum(
            1
            for s in [
                price_signal,
                volume_signal,
                flow_signal,
                sentiment_signal,
                chain_signal,
            ]
            if s["signal"] == "BULLISH"
        )
        bearish_score = sum(
            1
            for s in [
                price_signal,
                volume_signal,
                flow_signal,
                sentiment_signal,
                chain_signal,
            ]
            if s["signal"] == "BEARISH"
        )

        if bullish_score > bearish_score:
            insight.signal = "BULLISH"
            insight.confidence = min(0.95, 0.5 + (bullish_score - bearish_score) * 0.1)
        elif bearish_score > bullish_score:
            insight.signal = "BEARISH"
            insight.confidence = min(0.95, 0.5 + (bearish_score - bullish_score) * 0.1)
        else:
            insight.signal = "NEUTRAL"
            insight.confidence = 0.5

        # Generate reasoning
        insight.reasoning = self._generate_reasoning(
            price_signal,
            volume_signal,
            flow_signal,
            sentiment_signal,
            chain_signal,
            insight.signal,
        )

        self.analysis_history.append(insight)
        return insight

    async def _analyze_price_action(
        self,
        price: float,
        change: float,
        highs: List[float],
        lows: List[float],
        closes: List[float],
    ) -> Dict:
        """Analyze price action patterns."""
        signal = "NEUTRAL"
        strength = 0.5

        # Higher highs / Higher lows = Uptrend
        if len(highs) >= 3:
            hh = all(highs[i] < highs[i + 1] for i in range(len(highs) - 1))
            hl = all(lows[i] < lows[i + 1] for i in range(len(lows) - 1))
            if hh and hl:
                signal = "BULLISH"
                strength = 0.7
            elif not hh and not hl:
                signal = "BEARISH"
                strength = 0.7

        # Strong move
        if abs(change) > 5:
            signal = "BULLISH" if change > 0 else "BEARISH"
            strength = 0.8

        # RSI Analysis
        if len(closes) >= 14:
            rsi = self._calculate_rsi(closes)
            if rsi < 30:
                signal = "BULLISH"
                strength = 0.65
            elif rsi > 70:
                signal = "BEARISH"
                strength = 0.65

        return {"signal": signal, "strength": strength}

    def _calculate_rsi(self, closes: List[float], period: int = 14) -> float:
        """Calculate RSI."""
        if len(closes) < period + 1:
            return 50

        deltas = [closes[i + 1] - closes[i] for i in range(len(closes) - 1)]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    async def _analyze_volume_profile(
        self, price: float, profile: VolumeProfile
    ) -> Dict:
        """Analyze volume profile."""
        signal = "NEUTRAL"
        strength = 0.5

        # Price above POC = Bullish
        if profile.poc > 0:
            if price > profile.poc:
                signal = "BULLISH"
                strength = 0.6
            elif price < profile.poc:
                signal = "BEARISH"
                strength = 0.6

        # Wide value area = High volatility
        va_range = profile.va_high - profile.va_low
        if va_range > price * 0.05:
            strength = 0.7  # Clearer signal

        return {"signal": signal, "strength": strength}

    async def _analyze_order_flow(self, flow: OrderFlowData) -> Dict:
        """Analyze order flow."""
        signal = "NEUTUAL"
        strength = 0.5

        # Delta analysis
        if flow.delta > 0:
            signal = "BULLISH"
            strength = min(0.9, 0.5 + flow.delta * 0.1)
        elif flow.delta < 0:
            signal = "BEARISH"
            strength = min(0.9, 0.5 + abs(flow.delta) * 0.1)

        # Bid/Ask imbalance
        if abs(flow.bid_ask_imbalance) > 0.3:
            if flow.bid_ask_imbalance > 0:
                signal = "BULLISH"
            else:
                signal = "BEARISH"

        return {"signal": signal, "strength": strength}

    async def _analyze_sentiment(self, sent: SentimentData) -> Dict:
        """Analyze sentiment data."""
        signal = "NEUTRAL"
        strength = 0.5

        # Fear & Greed Index
        if sent.fear_greed_index < 25:
            signal = "BULLISH"  # Fear = Opportunity
            strength = 0.65
        elif sent.fear_greed_index > 75:
            signal = "BEARISH"  # Greed = Risk
            strength = 0.65

        # Funding Rate
        if sent.funding_rate > 0.1:
            signal = "BEARISH"  # Overleveraged long
            strength = 0.6
        elif sent.funding_rate < -0.1:
            signal = "BULLISH"  # Overleveraged short
            strength = 0.6

        # Long/Short Ratio
        if sent.long_short_ratio > 1.5:
            signal = "BEARISH"  # Crowded long
            strength = 0.55
        elif sent.long_short_ratio < 0.67:
            signal = "BULLISH"  # Crowded short
            strength = 0.55

        return {"signal": signal, "strength": strength}

    async def _analyze_on_chain(self, chain: OnChainData) -> Dict:
        """Analyze on-chain metrics."""
        signal = "NEUTRAL"
        strength = 0.5

        # Net exchange flow
        if chain.net_exchange_flow < 0:
            signal = "BULLISH"  # More leaving exchanges = Accumulation
            strength = 0.6
        elif chain.net_exchange_flow > 0:
            signal = "BEARISH"  # More to exchanges = Distribution
            strength = 0.6

        # Whale activity
        if chain.whale_activity == "ACCUMULATING":
            signal = "BULLISH"
            strength = 0.7
        elif chain.whale_activity == "DISTRIBUTING":
            signal = "BEARISH"
            strength = 0.7

        # NVT Ratio (Network Value to Transactions)
        if chain.nvt_ratio < 20:
            signal = "BULLISH"  # Undervalued
            strength = 0.6
        elif chain.nvt_ratio > 100:
            signal = "BEARISH"  # Overvalued
            strength = 0.6

        return {"signal": signal, "strength": strength}

    async def _analyze_correlations(
        self, symbol: str, related: List[str], change: float
    ) -> Dict:
        """Analyze cross-asset correlations."""
        strength = 0.5

        # Simplified - in production would fetch real correlation data
        correlations = {}
        for rel in related:
            correlations[rel] = 0.7  # Placeholder for real correlation

        # If related assets moving same direction = Confirmation
        strength = 0.6

        return {
            "strength": strength,
            "correlations": correlations,
            "signal": "BULLISH" if change > 0 else "BEARISH",
        }

    def _generate_reasoning(
        self,
        price: Dict,
        volume: Dict,
        flow: Dict,
        sentiment: Dict,
        chain: Dict,
        overall: str,
    ) -> str:
        """Generate human-readable reasoning."""
        reasons = []

        if price["signal"] == overall:
            reasons.append(f"Price action ({price['signal'].lower()})")

        if volume["signal"] == overall:
            reasons.append(f"Volume profile ({volume['signal'].lower()})")

        if flow["signal"] == overall:
            reasons.append(f"Order flow ({flow['signal'].lower()})")

        if sentiment["signal"] == overall:
            reasons.append(f"Sentiment ({sentiment['signal'].lower()})")

        if chain["signal"] == overall:
            reasons.append(f"On-chain ({chain['signal'].lower()})")

        return f"{overall} based on: {', '.join(reasons)}"


class LowCapDiscovery:
    """
    Discovers and analyzes low market cap coin opportunities.
    """

    def __init__(self):
        self.watchlist: List[CoinOpportunity] = []
        self.scoring_weights = {
            "liquidity": 0.2,
            "whale": 0.2,
            "social": 0.15,
            "setup": 0.25,
            "momentum": 0.2,
        }

    async def discover_opportunities(
        self,
        symbol: str,
        market_cap: float,
        volume_24h: float,
        price_change_24h: float,
        price_change_1h: float,
        volatility: float,
        social_mentions: int,
        funding_rate: float,
    ) -> CoinOpportunity:
        """
        Discover and score low cap coin opportunity.
        """
        # Calculate metrics
        vol_mc_ratio = volume_24h / market_cap if market_cap > 0 else 0
        liquidity_score = min(1.0, vol_mc_ratio / 0.5)  # 50% volume/mc = max score
        social_score = min(1.0, social_mentions / 1000)  # 1000 mentions = max score

        # Momentum scoring
        momentum = (price_change_24h + price_change_1h) / 2

        # Overall scoring
        overall_score = (
            liquidity_score * self.scoring_weights["liquidity"]
            + social_score * self.scoring_weights["social"]
            + (0.5 + momentum * 0.05) * self.scoring_weights["momentum"]
        )

        # Risk scoring (higher = more risky)
        risk_score = min(1.0, volatility / 5) + (1 - liquidity_score) * 0.3

        # Calculate entry/stop/target
        entry_zone = price_change_24h * 0.5  # Buy half the daily move
        target_1 = 1.10  # 10% gain
        target_2 = 1.20  # 20% gain
        stop_loss = 0.95  # 5% stop

        opportunity = CoinOpportunity(
            symbol=symbol,
            name=symbol.replace("USDT", ""),
            market_cap=market_cap,
            volume_24h=volume_24h,
            volume_mc_ratio=vol_mc_ratio,
            price_change_24h=price_change_24h,
            price_change_1h=price_change_1h,
            volatility=volatility,
            liquidity_score=liquidity_score,
            whale_activity="NEUTRAL",
            social_score=social_score,
            setup_quality=overall_score,
            risk_score=risk_score,
            overall_score=overall_score,
            entry_zone=entry_zone,
            target_1=target_1,
            target_2=target_2,
            stop_loss=stop_loss,
            reasoning=self._generate_opportunity_reasoning(
                overall_score, risk_score, momentum, liquidity_score
            ),
        )

        self.watchlist.append(opportunity)
        return opportunity

    def _generate_opportunity_reasoning(
        self, score: float, risk: float, momentum: float, liquidity: float
    ) -> str:
        """Generate opportunity analysis."""
        reasons = []

        if score > 0.7:
            reasons.append("Strong setup quality")
        elif score > 0.5:
            reasons.append("Moderate setup quality")

        if liquidity > 0.5:
            reasons.append("Good liquidity")
        else:
            reasons.append("Lower liquidity - higher slippage risk")

        if momentum > 3:
            reasons.append("Strong upward momentum")
        elif momentum < -3:
            reasons.append("Weak downward momentum")

        if risk < 0.5:
            reasons.append("Lower risk profile")
        elif risk > 0.7:
            reasons.append("Higher volatility risk")

        return f"{score:.0%} quality score: {', '.join(reasons)}"

    async def get_top_opportunities(
        self, min_score: float = 0.5, max_risk: float = 0.7, limit: int = 10
    ) -> List[CoinOpportunity]:
        """Get top ranked opportunities."""
        filtered = [
            o
            for o in self.watchlist
            if o.overall_score >= min_score and o.risk_score <= max_risk
        ]

        return sorted(filtered, key=lambda x: x.overall_score, reverse=True)[:limit]


class AdvancedRiskManager:
    """
    Advanced risk management for AGI trading.
    """

    def __init__(self):
        self.max_position_size = 0.05  # 5% max per trade
        self.max_portfolio_risk = 0.10  # 10% max portfolio risk
        self.max_correlation_risk = 0.30  # Max correlated exposure

    def calculate_position_size(
        self,
        capital: float,
        entry_price: float,
        stop_loss: float,
        volatility: float,
        correlation_exposure: float = 0,
    ) -> float:
        """Calculate optimal position size."""
        # Risk per trade
        risk_amount = capital * self.max_position_size

        # Distance to stop
        stop_distance = abs(entry_price - stop_loss) / entry_price

        # Volatility adjustment
        vol_adjustment = min(1.0, 0.02 / volatility)  # Higher vol = smaller size

        # Correlation adjustment
        corr_adjustment = max(0.5, 1 - correlation_exposure)

        # Calculate size
        size = (risk_amount / stop_distance) * vol_adjustment * corr_adjustment

        # Apply portfolio risk limit
        max_size = capital * self.max_portfolio_risk

        return min(size, max_size)

    def calculate_kelly_fraction(
        self, win_rate: float, avg_win: float, avg_loss: float
    ) -> float:
        """Calculate Kelly criterion for position sizing."""
        if avg_loss == 0:
            return 0

        win_loss_ratio = avg_win / abs(avg_loss)
        kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio

        # Use fractional Kelly (1/2 Kelly for safety)
        return max(0, kelly * 0.5)


class RegimeDetector:
    """
    Advanced market regime detection.
    """

    def __init__(self):
        self.regime_history: List[Dict] = []

    async def detect_regime(
        self,
        prices: List[float],
        volumes: List[float],
        order_flows: List[float],
        volatilities: List[float],
    ) -> Dict:
        """
        Detect current market regime.
        Returns: regime type, regime confidence, regime characteristics
        """
        if len(prices) < 20:
            return {"regime": "UNKNOWN", "confidence": 0.5}

        # Calculate regime metrics
        returns = self._calculate_returns(prices)
        volatility = self._calculate_volatility(returns)
        trend = self._calculate_trend(prices)
        volume_trend = self._calculate_volume_trend(volumes)
        flow_bias = sum(order_flows) / len(order_flows) if order_flows else 0

        # Regime detection logic
        regime = "RANGING"
        confidence = 0.5
        characteristics = []

        # Strong trend regime
        if abs(trend) > 0.01 and volatility < 0.03:
            regime = "TRENDING"
            confidence = min(0.95, 0.5 + abs(trend) * 50)
            characteristics = [
                f"Strong trend: {'up' if trend > 0 else 'down'}",
                f"Low volatility: {volatility:.2%}",
                f"Order flow bias: {'buying' if flow_bias > 0 else 'selling'}",
            ]

        # High volatility regime
        elif volatility > 0.05:
            regime = "VOLATILE"
            confidence = min(0.95, 0.5 + (volatility - 0.05) * 10)
            characteristics = [
                f"High volatility: {volatility:.2%}",
                f"Volume spike: {'yes' if volume_trend > 1.5 else 'no'}",
            ]

        # Low volatility regime
        elif volatility < 0.01:
            regime = "CALM"
            confidence = 0.8
            characteristics = [
                f"Low volatility: {volatility:.2%}",
                "Potential breakout setup",
            ]

        # Reversal signals
        if len(prices) >= 10:
            recent = returns[-5:]
            early = returns[-10:-5]
            if sum(recent) * sum(early) < 0:
                regime = "REVERSING"
                confidence = 0.6
                characteristics = ["Potential reversal detected"]

        result = {
            "regime": regime,
            "confidence": confidence,
            "characteristics": characteristics,
            "metrics": {
                "volatility": volatility,
                "trend": trend,
                "volume_trend": volume_trend,
                "flow_bias": flow_bias,
            },
        }

        self.regime_history.append(result)
        return result

    def _calculate_returns(self, prices: List[float]) -> List[float]:
        """Calculate period returns."""
        return [(prices[i + 1] - prices[i]) / prices[i] for i in range(len(prices) - 1)]

    def _calculate_volatility(self, returns: List[float]) -> float:
        """Calculate volatility (standard deviation)."""
        if len(returns) < 2:
            return 0.02

        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / len(returns)
        return (variance**0.5) * (252**0.5)  # Annualized

    def _calculate_trend(self, prices: List[float]) -> float:
        """Calculate trend direction and strength."""
        if len(prices) < 2:
            return 0

        return (prices[-1] - prices[0]) / prices[0]

    def _calculate_volume_trend(self, volumes: List[float]) -> float:
        """Calculate volume trend."""
        if len(volumes) < 2:
            return 1.0

        return volumes[-1] / max(0.001, sum(volumes[:-1]) / len(volumes[:-1]))


# Main Intelligence Class
class IBISIntelligence:
    """
    Unified market intelligence for IBIS AGI.
    Combines: Analysis, Discovery, Risk, Regime Detection
    """

    def __init__(self):
        self.market_intel = MarketIntelligence()
        self.low_cap_discovery = LowCapDiscovery()
        self.risk_manager = AdvancedRiskManager()
        self.regime_detector = RegimeDetector()

    async def full_market_analysis(
        self,
        symbol: str,
        price: float,
        price_change: float,
        volume: float,
        highs: List[float],
        lows: List[float],
        closes: List[float],
        volumes: List[float],
        order_flow: Dict,
        volume_profile: Dict = None,
        sentiment: Dict = None,
        on_chain: Dict = None,
        related_symbols: List[str] = None,
    ) -> Dict:
        """
        Complete market analysis combining all dimensions.
        """
        # Create data objects
        flow_data = OrderFlowData(**order_flow)
        if sentiment:
            sent_data = SentimentData(**sentiment)
        else:
            sent_data = SentimentData(
                fear_greed_index=50,
                fear_greed_class="NEUTRAL",
                social_volume=0.0,
                social_sentiment=0.0,
                news_sentiment=0.0,
                funding_rate=0.0,
                long_short_ratio=1.0,
                whale_sentiment=0.0,
            )
        if on_chain:
            chain_data = OnChainData(**on_chain)
        else:
            chain_data = OnChainData(
                exchange_inflow_24h=0.0,
                exchange_outflow_24h=0.0,
                net_exchange_flow=0.0,
                whale_transactions=0,
                whale_volume=0.0,
                whale_activity="NEUTRAL",
                holder_growth=0.0,
                burn_rate=0.0,
                nvt_ratio=0.0,
                mvrv_ratio=0.0,
                funding_rate=0.0,
            )
        if volume_profile:
            vp_data = VolumeProfile(**volume_profile)
        else:
            vp_data = VolumeProfile(
                poc=price,
                va_high=max(highs) if highs else price,
                va_low=min(lows) if lows else price,
                volume_by_price={},
                accepted_price=price,
                rejected_price=price,
            )

        # Run comprehensive analysis
        insight = await self.market_intel.comprehensive_analysis(
            symbol,
            price,
            price_change,
            volume,
            highs,
            lows,
            closes,
            volumes,
            flow_data,
            vp_data,
            sent_data,
            chain_data,
            related_symbols,
        )

        # Detect regime
        prices_needed = closes[-30:] if len(closes) >= 30 else closes
        vols_needed = volumes[-30:] if len(volumes) >= 30 else volumes
        regime = await self.regime_detector.detect_regime(
            prices_needed, vols_needed, [flow_data.delta] * 10, [0.02] * 10
        )

        return {
            "insight": insight.__dict__,
            "regime": regime,
            "recommended_action": self._determine_action(insight, regime),
            "risk_parameters": self._calculate_risk_parameters(price, regime),
        }

    def _determine_action(self, insight: MarketInsight, regime: Dict) -> Dict:
        """Determine recommended action based on analysis."""
        base_action = insight.signal
        confidence = insight.confidence
        regime_modifier = regime.get("confidence", 0.5)

        # Adjust confidence based on regime
        final_confidence = confidence * 0.7 + regime_modifier * 0.3

        if base_action == "NEUTRAL" or final_confidence < 0.6:
            action = "WAIT"
        else:
            action = "TRADE_" + base_action

        return {
            "action": action,
            "confidence": final_confidence,
            "regime": regime.get("regime", "UNKNOWN"),
            "reasoning": insight.reasoning,
        }

    def _calculate_risk_parameters(self, price: float, regime: Dict) -> Dict:
        """Calculate risk parameters based on regime."""
        base_stop = 0.05  # 5%
        regime_type = regime.get("regime", "RANGING")

        if regime_type == "VOLATILE":
            base_stop = 0.08  # Wider stop
        elif regime_type == "TRENDING":
            base_stop = 0.03  # Tighter stop
        elif regime_type == "CALM":
            base_stop = 0.04

        return {
            "stop_loss_pct": base_stop,
            "position_size_pct": self.risk_manager.max_position_size,
            "risk_per_trade": self.risk_manager.max_position_size,
        }


# Global instance
ibis_intelligence: Optional[IBISIntelligence] = None


def get_intelligence() -> IBISIntelligence:
    """Get or create global intelligence instance."""
    global ibis_intelligence

    if ibis_intelligence is None:
        ibis_intelligence = IBISIntelligence()

    return ibis_intelligence
