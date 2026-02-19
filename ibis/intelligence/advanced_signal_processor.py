from ibis.core.logging_config import get_logger
"""
IBIS Enhanced Signal Processing & Scoring Module
=================================================
Advanced signal processing for highest quality signals with probability scoring
"""

import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from ibis.intelligence.quality_assurance import IntelligenceCleansingPipeline, intelligence_qa

logger = get_logger(__name__)


class AdvancedSignalProcessor:
    """
    Advanced signal processing system combining multiple signal sources
    with intelligent fusion and probability scoring
    """

    def __init__(self):
        self.signal_history = {}
        self.pattern_recognizer = PatternRecognizer()
        self.correlation_analyzer = CorrelationAnalyzer()
        self.scorer = SignalQualityScorer()
        self.cleansing_pipeline = IntelligenceCleansingPipeline()

    async def process_combined_signals(self, symbol: str, source_signals: Dict[str, Dict]) -> Dict:
        """
        Process and fuse signals from multiple sources
        """
        logger.debug(f"Processing {len(source_signals)} signal sources for {symbol}")

        # Step 1: Cleanse and validate signals
        validated_signals = await self._validate_signals(symbol, source_signals)

        # Step 2: Extract and standardize signals
        standardized_signals = await self._standardize_signals(validated_signals)

        # Step 3: Score each signal
        scored_signals = await self._score_signals(standardized_signals)

        # Step 4: Correlation analysis
        correlation_report = await self._analyze_correlations(standardized_signals)

        # Step 5: Signal fusion and final scoring
        fused_signal = await self._fuse_signals(symbol, scored_signals, correlation_report)

        # Step 6: Pattern recognition enhancement
        enhanced_signal = await self._enhance_with_patterns(symbol, fused_signal)

        # Step 7: Risk assessment
        risk_assessment = await self._assess_risk(symbol, enhanced_signal, scored_signals)

        # Step 8: Store in history
        await self._store_signal_history(symbol, enhanced_signal, scored_signals)

        return {
            "symbol": symbol,
            "signal": enhanced_signal,
            "risk_assessment": risk_assessment,
            "source_signals": scored_signals,
            "correlation_report": correlation_report,
            "quality_metrics": await self._get_quality_metrics(validated_signals),
            "timestamp": datetime.now().isoformat(),
        }

    async def _validate_signals(self, symbol: str, source_signals: Dict[str, Dict]) -> Dict:
        """Validate and cleanse source signals"""
        validated = {}
        for source_name, signal in source_signals.items():
            is_valid, report = await intelligence_qa.validate_source(
                f"{source_name}_signal", signal
            )
            if is_valid:
                validated[source_name] = intelligence_qa.cleanse_data(signal)
            else:
                logger.warning(f"Signal from {source_name} failed validation: {report}")
        return validated

    async def _standardize_signals(self, validated_signals: Dict) -> List[Dict]:
        """Standardize signals to common format"""
        standardized = []

        for source_name, signal in validated_signals.items():
            # Standardize fields
            std_signal = {
                "source": source_name,
                "symbol": signal.get("symbol", "UNKNOWN"),
                "action": self._standardize_action(signal.get("action", "HOLD")),
                "direction": self._standardize_direction(signal.get("direction", "NEUTRAL")),
                "confidence": self._standardize_confidence(signal.get("confidence", 0.5)),
                "strength": self._standardize_strength(signal.get("strength", 0.5)),
                "score": self._standardize_score(signal.get("score", 50)),
                "timestamp": signal.get("timestamp", datetime.now().isoformat()),
                "raw_signal": signal,
            }

            # Extract metadata
            std_signal.update(await self._extract_signal_metadata(signal))

            standardized.append(std_signal)

        return standardized

    def _standardize_action(self, action: str) -> str:
        """Standardize action to BUY/SELL/HOLD"""
        action = str(action).upper().strip()
        if "BUY" in action or "LONG" in action:
            return "BUY"
        elif "SELL" in action or "SHORT" in action:
            return "SELL"
        else:
            return "HOLD"

    def _standardize_direction(self, direction: str) -> str:
        """Standardize direction to LONG/SHORT/NEUTRAL"""
        direction = str(direction).upper().strip()
        if "LONG" in direction or "BULL" in direction:
            return "LONG"
        elif "SHORT" in direction or "BEAR" in direction:
            return "SHORT"
        else:
            return "NEUTRAL"

    def _standardize_confidence(self, confidence: float) -> float:
        """Standardize confidence to 0-1 range"""
        if isinstance(confidence, (int, float)):
            if confidence > 1:
                return min(1.0, confidence / 100)
            return max(0.0, min(1.0, confidence))
        return 0.5

    def _standardize_strength(self, strength: float) -> float:
        """Standardize strength to 0-1 range"""
        return self._standardize_confidence(strength)

    def _standardize_score(self, score: float) -> float:
        """Standardize score to 0-100 range"""
        if isinstance(score, (int, float)):
            if 0 <= score <= 100:
                return score
            if score > 100:
                return min(100.0, score)
            return max(0.0, score)
        return 50.0

    async def _extract_signal_metadata(self, signal: Dict) -> Dict:
        """Extract additional metadata from signal"""
        metadata = {}

        # Timeframe
        if "timeframe" in signal:
            metadata["timeframe"] = str(signal["timeframe"]).upper()
        else:
            metadata["timeframe"] = "UNKNOWN"

        # Reasoning
        if "reasoning" in signal:
            metadata["reasoning"] = str(signal["reasoning"])

        # Confluences
        if "confluences" in signal and isinstance(signal["confluences"], list):
            metadata["confluences"] = [str(c) for c in signal["confluences"]]

        # Risk/reward
        if "risk_reward" in signal:
            metadata["risk_reward"] = float(signal["risk_reward"])

        return metadata

    async def _score_signals(self, standardized_signals: List[Dict]) -> List[Dict]:
        """Score each standardized signal"""
        scored = []

        for signal in standardized_signals:
            score_report = self.scorer.score_signal(signal)
            scored.append(
                {
                    **signal,
                    **score_report,
                }
            )

        return scored

    async def _analyze_correlations(self, signals: List[Dict]) -> Dict:
        """Analyze correlations between signals"""
        if len(signals) < 2:
            return {
                "correlation_matrix": {},
                "average_correlation": 0.0,
                "confidence_agreement": 0.0,
                "direction_agreement": 0.0,
                "strength_agreement": 0.0,
            }

        # Calculate signal correlations
        correlation_report = await self.correlation_analyzer.analyze_signals(signals)

        return correlation_report

    async def _fuse_signals(
        self, symbol: str, scored_signals: List[Dict], correlation_report: Dict
    ) -> Dict:
        """Fuse signals using intelligent fusion algorithm"""
        if not scored_signals:
            return self._create_neutral_signal(symbol)

        # Calculate source weights based on quality
        source_weights = await self._calculate_source_weights(scored_signals)

        # Fuse signals based on direction agreement
        buy_signals = [s for s in scored_signals if s["direction"] == "LONG"]
        sell_signals = [s for s in scored_signals if s["direction"] == "SHORT"]

        if len(buy_signals) > len(sell_signals):
            final_direction = "LONG"
            final_action = "BUY"
            selected_signals = buy_signals
        elif len(sell_signals) > len(buy_signals):
            final_direction = "SHORT"
            final_action = "SELL"
            selected_signals = sell_signals
        else:
            final_direction = "NEUTRAL"
            final_action = "HOLD"
            selected_signals = scored_signals

        # Calculate weighted average metrics
        final_confidence = self._weighted_average(
            [s["confidence"] for s in selected_signals],
            [s["quality_score"] for s in selected_signals],
        )

        final_strength = self._weighted_average(
            [s["strength"] for s in selected_signals],
            [s["quality_score"] for s in selected_signals],
        )

        final_score = self._weighted_average(
            [s["score"] for s in selected_signals], [s["quality_score"] for s in selected_signals]
        )

        # Calculate agreement score
        agreement_score = await self._calculate_agreement_score(selected_signals, final_direction)

        # Combine reasoning
        reasoning = await self._combine_reasoning(selected_signals)

        # Confluences
        confluences = await self._extract_confluences(selected_signals)

        return {
            "symbol": symbol,
            "action": final_action,
            "direction": final_direction,
            "confidence": final_confidence,
            "strength": final_strength,
            "score": final_score,
            "agreement_score": agreement_score,
            "reasoning": reasoning,
            "confluences": confluences,
            "source_count": len(scored_signals),
            "selected_source_count": len(selected_signals),
            "timeframe": await self._determine_timeframe(selected_signals),
            "risk_reward": await self._calculate_risk_reward(selected_signals),
            "timestamp": datetime.now().isoformat(),
        }

    async def _calculate_source_weights(self, signals: List[Dict]) -> Dict:
        """Calculate source weights based on quality and reliability"""
        weights = {}

        for signal in signals:
            source = signal["source"]
            quality_score = signal.get("quality_score", 0.5)

            # Base weight on quality
            base_weight = quality_score

            # Add reliability bonus for consistent sources
            reliability_bonus = await self._get_source_reliability_bonus(source)
            base_weight *= 1 + reliability_bonus

            weights[source] = base_weight

        # Normalize to sum to 1
        total_weight = sum(weights.values())
        if total_weight > 0:
            for source in weights:
                weights[source] /= total_weight

        return weights

    async def _get_source_reliability_bonus(self, source: str) -> float:
        """Get reliability bonus based on source history"""
        if source not in self.signal_history:
            return 0.0

        # Calculate reliability from history
        history = self.signal_history[source]
        valid_signals = [s for s in history if s.get("is_valid", True)]

        if len(valid_signals) < 10:
            return 0.0

        # Reliability = average quality score * consistency
        avg_quality = np.mean([s.get("quality_score", 0.5) for s in valid_signals])
        consistency = await self._calculate_source_consistency(source)

        reliability = avg_quality * consistency
        return min(0.3, reliability * 0.3)  # Max 30% bonus

    async def _calculate_source_consistency(self, source: str) -> float:
        """Calculate source consistency"""
        history = self.signal_history.get(source, [])
        if len(history) < 5:
            return 1.0

        # Calculate variance in confidence scores
        confidences = [s.get("confidence", 0.5) for s in history[-10:]]
        variance = np.var(confidences)

        # Normalize to 0-1 (lower variance = higher consistency)
        return max(0.0, min(1.0, 1 - variance * 10))

    def _weighted_average(self, values: List[float], weights: List[float]) -> float:
        """Calculate weighted average"""
        if not values or not weights or sum(weights) == 0:
            return 0.5

        total = sum(v * w for v, w in zip(values, weights))
        return total / sum(weights)

    async def _calculate_agreement_score(self, signals: List[Dict], target_direction: str) -> float:
        """Calculate agreement score among signals"""
        if not signals:
            return 0.0

        agreement_count = sum(1 for s in signals if s["direction"] == target_direction)
        return agreement_count / len(signals)

    async def _combine_reasoning(self, signals: List[Dict]) -> str:
        """Combine reasoning from multiple signals"""
        reasoning = []

        for signal in signals:
            if "reasoning" in signal and signal["reasoning"]:
                reasoning.append(f"• {signal['source']}: {signal['reasoning']}")

        if not reasoning:
            return "Multiple signals analyzed"

        return "\n".join(reasoning)

    async def _extract_confluences(self, signals: List[Dict]) -> List[str]:
        """Extract confluences from signals"""
        confluences = []

        for signal in signals:
            if "confluences" in signal and isinstance(signal["confluences"], list):
                for confluence in signal["confluences"]:
                    if confluence not in confluences:
                        confluences.append(confluence)

        return confluences

    async def _determine_timeframe(self, signals: List[Dict]) -> str:
        """Determine dominant timeframe from signals"""
        timeframes = [s.get("timeframe", "UNKNOWN") for s in signals]

        if not timeframes:
            return "UNKNOWN"

        # Count timeframe occurrences
        timeframe_counts = {}
        for tf in timeframes:
            timeframe_counts[tf] = timeframe_counts.get(tf, 0) + 1

        # Return most frequent
        return max(timeframe_counts, key=timeframe_counts.get)

    async def _calculate_risk_reward(self, signals: List[Dict]) -> float:
        """Calculate average risk/reward ratio"""
        rr_values = [s.get("risk_reward", 1.0) for s in signals if "risk_reward" in s]

        if not rr_values:
            return 1.0

        return np.mean(rr_values)

    async def _enhance_with_patterns(self, symbol: str, signal: Dict) -> Dict:
        """Enhance signal with pattern recognition"""
        # TODO: Implement pattern recognition enhancement
        return signal

    async def _assess_risk(self, symbol: str, signal: Dict, source_signals: List[Dict]) -> Dict:
        """Assess signal risk"""
        risk_assessment = {
            "signal_quality_risk": 1 - signal.get("quality_score", 0.5),
            "divergence_risk": await self._calculate_divergence_risk(source_signals),
            "source_reliability_risk": await self._calculate_source_reliability_risk(
                source_signals
            ),
            "confidence_risk": 1 - signal.get("confidence", 0.5),
        }

        # Calculate total risk score (0-1)
        total_risk = np.mean(list(risk_assessment.values()))

        risk_assessment["total_risk"] = total_risk
        risk_assessment["risk_level"] = self._categorize_risk(total_risk)

        return risk_assessment

    async def _calculate_divergence_risk(self, signals: List[Dict]) -> float:
        """Calculate risk from signal divergence"""
        if len(signals) < 2:
            return 0.0

        # Calculate divergence in signal direction
        buy_count = sum(1 for s in signals if s["direction"] == "LONG")
        sell_count = sum(1 for s in signals if s["direction"] == "SHORT")

        divergence = min(buy_count, sell_count) / len(signals)
        return divergence

    async def _calculate_source_reliability_risk(self, signals: List[Dict]) -> float:
        """Calculate risk from source reliability"""
        avg_quality = np.mean([s.get("quality_score", 0.5) for s in signals])
        return max(0.0, 1 - avg_quality)

    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize risk level"""
        if risk_score <= 0.25:
            return "LOW"
        elif risk_score <= 0.5:
            return "MEDIUM"
        elif risk_score <= 0.75:
            return "HIGH"
        else:
            return "EXTREME"

    async def _store_signal_history(
        self, symbol: str, fused_signal: Dict, source_signals: List[Dict]
    ):
        """Store signal history for learning and reliability tracking"""
        if symbol not in self.signal_history:
            self.signal_history[symbol] = []

        # Trim history to last 100 signals
        if len(self.signal_history[symbol]) >= 100:
            self.signal_history[symbol] = self.signal_history[symbol][-50:]

        self.signal_history[symbol].append(
            {
                "timestamp": datetime.now().isoformat(),
                "fused_signal": fused_signal,
                "source_signals": source_signals,
                "is_valid": True,
            }
        )

    def _create_neutral_signal(self, symbol: str) -> Dict:
        """Create neutral signal when no valid signals available"""
        return {
            "symbol": symbol,
            "action": "HOLD",
            "direction": "NEUTRAL",
            "confidence": 0.5,
            "strength": 0.5,
            "score": 50.0,
            "agreement_score": 0.0,
            "reasoning": "No valid signals available",
            "confluences": [],
            "source_count": 0,
            "selected_source_count": 0,
            "timeframe": "UNKNOWN",
            "risk_reward": 1.0,
            "timestamp": datetime.now().isoformat(),
        }

    async def _get_quality_metrics(self, validated_signals: Dict) -> Dict:
        """Get quality metrics for processed signals"""
        quality_scores = []
        health_scores = []

        for source_name, signal in validated_signals.items():
            quality_report = intelligence_qa._assess_data_quality(source_name, signal)
            quality_scores.append(quality_report["overall_score"])
            health_scores.append(intelligence_qa._calculate_health_score(quality_report))

        return {
            "validated_sources": len(validated_signals),
            "avg_quality_score": np.mean(quality_scores) if quality_scores else 0.0,
            "avg_health_score": np.mean(health_scores) if health_scores else 0.0,
        }


class SignalQualityScorer:
    """
    Advanced signal quality scoring system
    """

    def __init__(self):
        self.scoring_weights = {
            "confidence": 0.30,
            "strength": 0.25,
            "source_quality": 0.20,
            "consistency": 0.15,
            "timeliness": 0.10,
        }

    def score_signal(self, signal: Dict) -> Dict:
        """Calculate comprehensive signal quality score"""
        scores = {}

        # Confidence score
        scores["confidence_score"] = signal.get("confidence", 0.5)

        # Strength score
        scores["strength_score"] = signal.get("strength", 0.5)

        # Source quality score (based on QA)
        scores["source_quality_score"] = self._calculate_source_quality(signal)

        # Consistency score
        scores["consistency_score"] = self._calculate_consistency_score(signal)

        # Timeliness score
        scores["timeliness_score"] = self._calculate_timeliness_score(signal)

        # Comprehensive quality score
        quality_score = 0.0
        for metric, weight in self.scoring_weights.items():
            score_name = f"{metric}_score"
            if score_name in scores:
                quality_score += scores[score_name] * weight

        scores["quality_score"] = max(0.0, min(1.0, quality_score))

        # Signal tier (GOD_TIER, HIGH_CONFIDENCE, etc.)
        scores["tier"] = self._determine_signal_tier(scores["quality_score"])

        return scores

    def _calculate_source_quality(self, signal: Dict) -> float:
        """Calculate source quality score"""
        source = signal.get("source", "unknown")
        raw_signal = signal.get("raw_signal", {})

        quality_report = intelligence_qa._assess_data_quality(source, raw_signal)
        return quality_report["overall_score"]

    def _calculate_consistency_score(self, signal: Dict) -> float:
        """Calculate signal consistency score"""
        action = signal.get("action", "HOLD")
        direction = signal.get("direction", "NEUTRAL")

        # Check consistency between action and direction
        if (action == "BUY" and direction == "LONG") or (action == "SELL" and direction == "SHORT"):
            return 1.0
        elif action == "HOLD" and direction == "NEUTRAL":
            return 1.0
        else:
            return 0.5

    def _calculate_timeliness_score(self, signal: Dict) -> float:
        """Calculate timeliness score"""
        if "timestamp" not in signal:
            return 0.5

        try:
            timestamp = signal["timestamp"]
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            elif isinstance(timestamp, int):
                timestamp = datetime.fromtimestamp(timestamp)

            age = (datetime.now() - timestamp).total_seconds()

            if age <= 300:  # 5 minutes
                return 1.0
            elif age <= 600:  # 10 minutes
                return 0.75
            elif age <= 1800:  # 30 minutes
                return 0.5
            else:
                return 0.25

        except Exception:
            return 0.5

    def _determine_signal_tier(self, quality_score: float) -> str:
        """Determine signal tier based on quality score"""
        if quality_score >= 0.95:
            return "GOD_TIER"
        elif quality_score >= 0.90:
            return "HIGH_CONFIDENCE"
        elif quality_score >= 0.85:
            return "STRONG_SETUP"
        elif quality_score >= 0.80:
            return "GOOD_SETUP"
        elif quality_score >= 0.70:
            return "STANDARD"
        elif quality_score >= 0.60:
            return "WEAK"
        else:
            return "BELOW_THRESHOLD"


class CorrelationAnalyzer:
    """
    Signal correlation analysis system
    """

    def __init__(self):
        self.correlation_history = {}

    async def analyze_signals(self, signals: List[Dict]) -> Dict:
        """Analyze signal correlations"""
        if len(signals) < 2:
            return {
                "correlation_matrix": {},
                "average_correlation": 0.0,
                "confidence_agreement": 0.0,
                "direction_agreement": 0.0,
                "strength_agreement": 0.0,
            }

        # Calculate signal vectors for comparison
        signal_vectors = await self._create_signal_vectors(signals)

        # Calculate correlation matrix
        correlation_matrix = await self._calculate_correlation_matrix(signal_vectors)

        # Calculate agreement scores
        direction_agreement = await self._calculate_direction_agreement(signals)
        confidence_agreement = await self._calculate_confidence_agreement(signals)
        strength_agreement = await self._calculate_strength_agreement(signals)

        # Calculate overall agreement
        overall_agreement = np.mean([direction_agreement, confidence_agreement, strength_agreement])

        return {
            "correlation_matrix": correlation_matrix,
            "average_correlation": overall_agreement,
            "direction_agreement": direction_agreement,
            "confidence_agreement": confidence_agreement,
            "strength_agreement": strength_agreement,
        }

    async def _create_signal_vectors(self, signals: List[Dict]) -> np.ndarray:
        """Create normalized signal vectors"""
        vectors = []

        for signal in signals:
            vector = []

            # Direction (1 for LONG, -1 for SHORT, 0 for NEUTRAL)
            if signal["direction"] == "LONG":
                vector.append(1)
            elif signal["direction"] == "SHORT":
                vector.append(-1)
            else:
                vector.append(0)

            # Confidence
            vector.append(signal["confidence"])

            # Strength
            vector.append(signal["strength"])

            # Score (normalized 0-1)
            vector.append(signal["score"] / 100)

            vectors.append(vector)

        return np.array(vectors)

    async def _calculate_correlation_matrix(self, vectors: np.ndarray) -> Dict:
        """Calculate correlation matrix between signals"""
        correlation_matrix = np.corrcoef(vectors.T)

        # Convert to dict for output
        result = {}
        for i, vec1 in enumerate(vectors):
            result[f"signal_{i}"] = {}
            for j, vec2 in enumerate(vectors):
                result[f"signal_{i}"][f"signal_{j}"] = float(correlation_matrix[i][j])

        return result

    async def _calculate_direction_agreement(self, signals: List[Dict]) -> float:
        """Calculate direction agreement score"""
        directions = [s["direction"] for s in signals]

        # Count agreement
        agreements = 0
        total_comparisons = len(signals) * (len(signals) - 1) // 2

        for i in range(len(directions)):
            for j in range(i + 1, len(directions)):
                if directions[i] == directions[j]:
                    agreements += 1

        return agreements / total_comparisons if total_comparisons > 0 else 0.0

    async def _calculate_confidence_agreement(self, signals: List[Dict]) -> float:
        """Calculate confidence agreement score (lower variance = higher agreement)"""
        confidences = [s["confidence"] for s in signals]

        if len(confidences) < 2:
            return 0.0

        variance = np.var(confidences)
        return max(0.0, 1 - variance * 10)

    async def _calculate_strength_agreement(self, signals: List[Dict]) -> float:
        """Calculate strength agreement score"""
        strengths = [s["strength"] for s in signals]

        if len(strengths) < 2:
            return 0.0

        variance = np.var(strengths)
        return max(0.0, 1 - variance * 10)


class PatternRecognizer:
    """
    Pattern recognition system for enhancing signals
    """

    def __init__(self):
        self.known_patterns = {
            "strong_momentum": {
                "description": "Strong momentum across multiple timeframes",
                "weight": 0.3,
            },
            "volume_spike": {"description": "Volume spike with price confirmation", "weight": 0.25},
            "divergence": {"description": "Momentum divergence", "weight": 0.2},
            "support_resistance": {
                "description": "Price at key support/resistance",
                "weight": 0.15,
            },
            "sentiment_convergence": {
                "description": "Sentiment convergence across sources",
                "weight": 0.1,
            },
        }

    async def recognize_patterns(
        self, symbol: str, signal: Dict, historical_data: Optional[Dict] = None
    ) -> List[Dict]:
        """Recognize patterns in signal and historical data"""
        patterns = []

        # Strong momentum pattern
        if signal["strength"] > 0.8 and signal["confidence"] > 0.85:
            patterns.append(
                {
                    "name": "strong_momentum",
                    "weight": self.known_patterns["strong_momentum"]["weight"],
                    "description": self.known_patterns["strong_momentum"]["description"],
                }
            )

        # Sentiment convergence
        if "confluences" in signal and len(signal["confluences"]) > 3:
            patterns.append(
                {
                    "name": "sentiment_convergence",
                    "weight": self.known_patterns["sentiment_convergence"]["weight"],
                    "description": self.known_patterns["sentiment_convergence"]["description"],
                }
            )

        return patterns


# Global instances
advanced_signal_processor = AdvancedSignalProcessor()
signal_quality_scorer = SignalQualityScorer()
