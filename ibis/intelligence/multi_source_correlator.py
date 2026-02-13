"""
IBIS Multi-Source Correlation & Fusion Module
=============================================
Advanced correlation analysis and intelligent fusion of multiple intelligence sources
"""

import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from collections import defaultdict

from ibis.intelligence.quality_assurance import intelligence_qa
from ibis.intelligence.advanced_signal_processor import AdvancedSignalProcessor

logger = logging.getLogger("IBIS")


class MultiSourceCorrelationSystem:
    """
    Advanced multi-source correlation analysis system
    """

    def __init__(self):
        self.correlation_history = defaultdict(list)
        self.signal_fusion = SignalFusionEngine()
        self.correlation_analyzer = CorrelationAnalyzer()
        self.consensus_detector = ConsensusDetector()
        self.pattern_matcher = PatternMatcher()

    async def analyze_correlations(
        self, symbol: str, source_signals: Dict[str, Dict], historical_data: Optional[Dict] = None
    ) -> Dict:
        """
        Analyze correlations between multiple signal sources
        """
        logger.debug(f"Analyzing correlations for {symbol} across {len(source_signals)} sources")

        # Step 1: Validate source signals
        validated_signals = await self._validate_signals(symbol, source_signals)

        # Step 2: Calculate source dependencies
        source_dependencies = await self._calculate_source_dependencies(validated_signals)

        # Step 3: Compute correlation matrix
        correlation_matrix = await self.correlation_analyzer.compute_correlation_matrix(
            validated_signals
        )

        # Step 4: Detect consensus patterns
        consensus_report = await self.consensus_detector.detect_consensus(
            validated_signals, correlation_matrix
        )

        # Step 5: Identify redundant sources
        redundant_sources = await self._identify_redundant_sources(
            validated_signals, correlation_matrix
        )

        # Step 6: Pattern matching across sources
        pattern_report = await self.pattern_matcher.match_patterns(validated_signals)

        # Step 7: Compute information entropy
        information_entropy = await self._compute_information_entropy(validated_signals)

        # Step 8: Calculate signal quality metrics
        quality_metrics = await self._calculate_quality_metrics(validated_signals)

        # Step 9: Fuse signals based on analysis
        fused_signal = await self.signal_fusion.fuse_signals(
            symbol, validated_signals, correlation_matrix, consensus_report
        )

        # Store correlation history
        await self._store_correlation_history(
            symbol, validated_signals, correlation_matrix, consensus_report
        )

        return {
            "symbol": symbol,
            "fused_signal": fused_signal,
            "source_signals": validated_signals,
            "correlation_matrix": correlation_matrix,
            "consensus_report": consensus_report,
            "redundant_sources": redundant_sources,
            "pattern_report": pattern_report,
            "information_entropy": information_entropy,
            "quality_metrics": quality_metrics,
            "source_dependencies": source_dependencies,
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

    async def _calculate_source_dependencies(self, validated_signals: Dict) -> Dict:
        """Calculate dependencies between sources"""
        dependencies = defaultdict(list)

        # Simple dependency detection based on overlapping fields
        source_fields = defaultdict(set)

        for source_name, signal in validated_signals.items():
            source_fields[source_name] = set(signal.keys())

        for source1, fields1 in source_fields.items():
            for source2, fields2 in source_fields.items():
                if source1 != source2:
                    overlap = fields1.intersection(fields2)
                    if overlap:
                        dependencies[source1].append(
                            {
                                "source": source2,
                                "overlap_fields": list(overlap),
                                "overlap_score": len(overlap) / len(fields1),
                            }
                        )

        return dict(dependencies)

    async def _identify_redundant_sources(
        self, validated_signals: Dict, correlation_matrix: Dict
    ) -> List[str]:
        """Identify redundant sources based on high correlation"""
        if len(validated_signals) < 2:
            return []

        redundant = []
        checked_pairs = set()

        sources = list(validated_signals.keys())

        for i in range(len(sources)):
            for j in range(i + 1, len(sources)):
                source1 = sources[i]
                source2 = sources[j]

                if (source1, source2) in checked_pairs or (source2, source1) in checked_pairs:
                    continue

                checked_pairs.add((source1, source2))

                correlation = correlation_matrix.get(source1, {}).get(source2, 0)

                if correlation > 0.95:  # Very high correlation
                    # Keep the source with better quality
                    quality1 = await self._get_source_quality(source1, validated_signals)
                    quality2 = await self._get_source_quality(source2, validated_signals)

                    redundant_source = source2 if quality1 >= quality2 else source1
                    if redundant_source not in redundant:
                        redundant.append(redundant_source)
                        logger.debug(
                            f"Source {redundant_source} is redundant (correlation: {correlation:.3f})"
                        )

        return redundant

    async def _get_source_quality(self, source_name: str, validated_signals: Dict) -> float:
        """Get source quality score"""
        if source_name not in validated_signals:
            return 0.0

        quality_report = intelligence_qa._assess_data_quality(
            source_name, validated_signals[source_name]
        )
        return quality_report["overall_score"]

    async def _compute_information_entropy(self, validated_signals: Dict) -> float:
        """Compute information entropy of source signals"""
        if not validated_signals:
            return 0.0

        # Calculate entropy based on signal direction distribution
        directions = []
        for signal in validated_signals.values():
            direction = signal.get("direction", "NEUTRAL").upper()
            if direction in ["LONG", "SHORT"]:
                directions.append(direction)

        if not directions:
            return 0.0

        # Calculate probabilities
        from collections import Counter

        direction_counts = Counter(directions)
        total = len(directions)

        probabilities = [count / total for count in direction_counts.values()]

        # Calculate entropy
        entropy = -sum(p * np.log2(p) for p in probabilities)

        # Normalize to 0-1 range (max entropy for 2 directions is 1)
        max_entropy = 1.0
        return min(1.0, entropy / max_entropy)

    async def _calculate_quality_metrics(self, validated_signals: Dict) -> Dict:
        """Calculate quality metrics for all sources"""
        if not validated_signals:
            return {
                "sources": 0,
                "avg_quality": 0.0,
                "quality_distribution": {},
            }

        quality_scores = []
        quality_distribution = defaultdict(int)

        for source_name, signal in validated_signals.items():
            quality_report = intelligence_qa._assess_data_quality(source_name, signal)
            quality_score = quality_report["overall_score"]
            quality_scores.append(quality_score)

            # Categorize quality
            if quality_score >= 0.9:
                quality_distribution["excellent"] += 1
            elif quality_score >= 0.8:
                quality_distribution["very_good"] += 1
            elif quality_score >= 0.7:
                quality_distribution["good"] += 1
            elif quality_score >= 0.6:
                quality_distribution["fair"] += 1
            else:
                quality_distribution["poor"] += 1

        return {
            "sources": len(validated_signals),
            "avg_quality": np.mean(quality_scores),
            "quality_distribution": dict(quality_distribution),
            "quality_variance": np.var(quality_scores),
        }

    async def _store_correlation_history(
        self, symbol: str, validated_signals: Dict, correlation_matrix: Dict, consensus_report: Dict
    ):
        """Store correlation history for learning"""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "sources": list(validated_signals.keys()),
            "correlation_matrix": correlation_matrix,
            "consensus_score": consensus_report.get("overall_consensus", 0.0),
            "agreement": consensus_report.get("direction_agreement", 0.0),
            "quality_metrics": await self._calculate_quality_metrics(validated_signals),
        }

        self.correlation_history[symbol].append(history_entry)

        # Trim history to last 100 entries
        if len(self.correlation_history[symbol]) > 100:
            self.correlation_history[symbol] = self.correlation_history[symbol][-50:]


class SignalFusionEngine:
    """
    Intelligent signal fusion engine
    """

    def __init__(self):
        self.fusion_strategies = {
            "weighted_average": self._weighted_average_fusion,
            "bayesian": self._bayesian_fusion,
            "dempster_shafer": self._dempster_shafer_fusion,
            "entropy_weighted": self._entropy_weighted_fusion,
        }

    async def fuse_signals(
        self, symbol: str, validated_signals: Dict, correlation_matrix: Dict, consensus_report: Dict
    ) -> Dict:
        """
        Fuse signals using optimal strategy based on correlation analysis
        """
        logger.debug(f"Fusing {len(validated_signals)} signals for {symbol}")

        # Select fusion strategy based on correlation characteristics
        strategy = await self._select_fusion_strategy(correlation_matrix, consensus_report)

        logger.debug(f"Using fusion strategy: {strategy}")

        # Apply selected fusion strategy
        fusion_function = self.fusion_strategies.get(strategy, self._weighted_average_fusion)
        fused_signal = await fusion_function(
            symbol, validated_signals, correlation_matrix, consensus_report
        )

        return fused_signal

    async def _select_fusion_strategy(
        self, correlation_matrix: Dict, consensus_report: Dict
    ) -> str:
        """Select optimal fusion strategy"""
        consensus_score = consensus_report.get("overall_consensus", 0.0)
        average_correlation = consensus_report.get("average_correlation", 0.0)
        direction_agreement = consensus_report.get("direction_agreement", 0.0)

        # High consensus with good agreement
        if consensus_score > 0.85 and direction_agreement > 0.8:
            return "bayesian"

        # Moderate consensus with low correlation (diverse sources)
        if consensus_score > 0.7 and average_correlation < 0.3:
            return "dempster_shafer"

        # High correlation among sources (redundant information)
        if average_correlation > 0.6:
            return "entropy_weighted"

        # Default: weighted average
        return "weighted_average"

    async def _weighted_average_fusion(
        self, symbol: str, validated_signals: Dict, correlation_matrix: Dict, consensus_report: Dict
    ) -> Dict:
        """Weighted average fusion based on source quality"""
        # Calculate source weights
        source_weights = await self._calculate_source_weights(validated_signals)

        # Fuse numerical fields
        fused = self._fuse_numerical_fields(validated_signals, source_weights)

        # Determine final direction and action
        fused.update(await self._determine_action(validated_signals, source_weights))

        return await self._standardize_fused_signal(
            symbol, fused, validated_signals, source_weights
        )

    async def _bayesian_fusion(
        self, symbol: str, validated_signals: Dict, correlation_matrix: Dict, consensus_report: Dict
    ) -> Dict:
        """Bayesian fusion for high consensus signals"""
        # Simple Bayesian fusion based on direction probabilities
        source_weights = await self._calculate_source_weights(validated_signals)

        # Calculate direction probabilities
        buy_prob = 0.0
        sell_prob = 0.0

        for source_name, signal in validated_signals.items():
            weight = source_weights[source_name]
            direction = signal.get("direction", "NEUTRAL").upper()
            confidence = signal.get("confidence", 0.5)

            if direction == "LONG":
                buy_prob += weight * confidence
            elif direction == "SHORT":
                sell_prob += weight * confidence

        total_prob = buy_prob + sell_prob

        if total_prob > 0:
            buy_prob /= total_prob
            sell_prob /= total_prob

        # Determine final direction and action
        direction, action = self._probability_to_action(buy_prob, sell_prob)

        # Fuse other fields
        fused = self._fuse_numerical_fields(validated_signals, source_weights)
        fused.update(
            {
                "direction": direction,
                "action": action,
                "confidence": max(buy_prob, sell_prob),
                "buy_probability": buy_prob,
                "sell_probability": sell_prob,
            }
        )

        return await self._standardize_fused_signal(
            symbol, fused, validated_signals, source_weights
        )

    async def _dempster_shafer_fusion(
        self, symbol: str, validated_signals: Dict, correlation_matrix: Dict, consensus_report: Dict
    ) -> Dict:
        """Dempster-Shafer evidence theory fusion"""
        # Dempster-Shafer for belief aggregation
        source_weights = await self._calculate_source_weights(validated_signals)

        # Initialize belief functions
        belief = {
            "LONG": 0.0,
            "SHORT": 0.0,
            "NEUTRAL": 0.0,
            "UNKNOWN": 0.0,
        }

        # Combine evidence
        for source_name, signal in validated_signals.items():
            weight = source_weights[source_name]
            direction = signal.get("direction", "NEUTRAL").upper()
            confidence = signal.get("confidence", 0.5)

            # Assign mass to direction and unknown
            belief[direction] += weight * confidence
            belief["UNKNOWN"] += weight * (1 - confidence)

        # Normalize
        total_belief = sum(belief.values())
        if total_belief > 0:
            belief = {k: v / total_belief for k, v in belief.items()}

        # Determine action from belief
        best_direction = max(belief, key=belief.get)
        if best_direction == "LONG":
            action = "BUY"
        elif best_direction == "SHORT":
            action = "SELL"
        else:
            action = "HOLD"

        # Fuse other fields
        fused = self._fuse_numerical_fields(validated_signals, source_weights)
        fused.update(
            {
                "direction": best_direction,
                "action": action,
                "confidence": belief[best_direction],
                "belief_values": belief,
            }
        )

        return await self._standardize_fused_signal(
            symbol, fused, validated_signals, source_weights
        )

    async def _entropy_weighted_fusion(
        self, symbol: str, validated_signals: Dict, correlation_matrix: Dict, consensus_report: Dict
    ) -> Dict:
        """Entropy-weighted fusion for redundant sources"""
        # Calculate information entropy for each source
        source_entropies = {}
        for source_name, signal in validated_signals.items():
            entropy = await self._calculate_signal_entropy(signal)
            source_entropies[source_name] = entropy

        # Convert entropy to weights (lower entropy = higher weight)
        min_entropy = min(source_entropies.values())
        max_entropy = max(source_entropies.values())

        source_weights = {}
        for source_name, entropy in source_entropies.items():
            if max_entropy - min_entropy == 0:
                source_weights[source_name] = 1.0 / len(validated_signals)
            else:
                normalized_entropy = (entropy - min_entropy) / (max_entropy - min_entropy)
                source_weights[source_name] = 1 - normalized_entropy

        # Normalize weights
        total_weight = sum(source_weights.values())
        if total_weight > 0:
            source_weights = {k: v / total_weight for k, v in source_weights.items()}

        # Fuse fields
        fused = self._fuse_numerical_fields(validated_signals, source_weights)
        fused.update(await self._determine_action(validated_signals, source_weights))

        return await self._standardize_fused_signal(
            symbol, fused, validated_signals, source_weights
        )

    async def _calculate_source_weights(self, validated_signals: Dict) -> Dict:
        """Calculate source weights based on quality and reliability"""
        weights = {}

        for source_name, signal in validated_signals.items():
            quality_report = intelligence_qa._assess_data_quality(source_name, signal)
            quality_score = quality_report["overall_score"]
            health_score = intelligence_qa._calculate_health_score(quality_report)

            # Combine quality and health scores
            weight = (quality_score * 0.7) + (health_score * 0.3)
            weights[source_name] = weight

        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight > 0:
            return {k: v / total_weight for k, v in weights.items()}

        # Equal weights if no valid quality scores
        return {k: 1.0 / len(validated_signals) for k in validated_signals}

    def _fuse_numerical_fields(self, validated_signals: Dict, source_weights: Dict) -> Dict:
        """Fuse numerical fields using weighted average"""
        numerical_fields = ["confidence", "strength", "score"]

        fused = {}

        for field in numerical_fields:
            values = []
            weights = []

            for source_name, signal in validated_signals.items():
                if field in signal and isinstance(signal[field], (int, float)):
                    values.append(signal[field])
                    weights.append(source_weights[source_name])

            if values and weights:
                fused[field] = sum(v * w for v, w in zip(values, weights)) / sum(weights)

        return fused

    async def _determine_action(self, validated_signals: Dict, source_weights: Dict) -> Dict:
        """Determine final action from signals"""
        buy_score = 0.0
        sell_score = 0.0

        for source_name, signal in validated_signals.items():
            weight = source_weights[source_name]
            direction = signal.get("direction", "NEUTRAL").upper()
            confidence = signal.get("confidence", 0.5)

            if direction == "LONG":
                buy_score += weight * confidence
            elif direction == "SHORT":
                sell_score += weight * confidence

        if buy_score > sell_score:
            return {
                "action": "BUY",
                "direction": "LONG",
                "confidence": buy_score,
                "strength": max(buy_score, sell_score),
            }
        elif sell_score > buy_score:
            return {
                "action": "SELL",
                "direction": "SHORT",
                "confidence": sell_score,
                "strength": max(buy_score, sell_score),
            }
        else:
            return {
                "action": "HOLD",
                "direction": "NEUTRAL",
                "confidence": 0.5,
                "strength": 0.5,
            }

    def _probability_to_action(self, buy_prob: float, sell_prob: float) -> Tuple[str, str]:
        """Convert probabilities to action/direction"""
        if buy_prob > sell_prob:
            if buy_prob > 0.6:
                return "LONG", "BUY"
            else:
                return "NEUTRAL", "HOLD"
        elif sell_prob > buy_prob:
            if sell_prob > 0.6:
                return "SHORT", "SELL"
            else:
                return "NEUTRAL", "HOLD"
        else:
            return "NEUTRAL", "HOLD"

    async def _calculate_signal_entropy(self, signal: Dict) -> float:
        """Calculate information entropy of a single signal"""
        # Simple entropy calculation based on signal strength and consistency
        strength = signal.get("strength", 0.5)
        confidence = signal.get("confidence", 0.5)

        # Higher strength/confidence = lower entropy
        return 1 - (strength + confidence) / 2

    async def _standardize_fused_signal(
        self, symbol: str, fused: Dict, validated_signals: Dict, source_weights: Dict
    ) -> Dict:
        """Standardize fused signal format"""
        standardized = {
            "symbol": symbol,
            "action": fused.get("action", "HOLD"),
            "direction": fused.get("direction", "NEUTRAL"),
            "confidence": max(0.0, min(1.0, fused.get("confidence", 0.5))),
            "strength": max(0.0, min(1.0, fused.get("strength", 0.5))),
            "score": max(0.0, min(100.0, fused.get("score", 50))),
            "source_count": len(validated_signals),
            "source_weights": source_weights,
            "timeframe": await self._determine_timeframe(validated_signals),
            "reasoning": await self._generate_reasoning(validated_signals, source_weights),
            "timestamp": datetime.now().isoformat(),
        }

        # Add probability information if available
        if "buy_probability" in fused:
            standardized["buy_probability"] = fused["buy_probability"]
        if "sell_probability" in fused:
            standardized["sell_probability"] = fused["sell_probability"]
        if "belief_values" in fused:
            standardized["belief_values"] = fused["belief_values"]

        return standardized

    async def _determine_timeframe(self, validated_signals: Dict) -> str:
        """Determine dominant timeframe"""
        timeframes = [
            s.get("timeframe", "UNKNOWN") for s in validated_signals.values() if "timeframe" in s
        ]

        if not timeframes:
            return "UNKNOWN"

        from collections import Counter

        return Counter(timeframes).most_common(1)[0][0]

    async def _generate_reasoning(self, validated_signals: Dict, source_weights: Dict) -> str:
        """Generate reasoning for fused signal"""
        reasons = []

        for source_name, signal in validated_signals.items():
            weight = source_weights[source_name]
            if weight > 0.1:  # Only include significant sources
                reasoning = signal.get("reasoning", f"{source_name} signal")
                reasons.append(f"• {source_name} ({weight:.1%}): {reasoning}")

        return "\n".join(reasons)


class CorrelationAnalyzer:
    """
    Advanced correlation analysis
    """

    def __init__(self):
        self.correlation_window = 30  # 30-minute window

    async def compute_correlation_matrix(self, validated_signals: Dict) -> Dict:
        """Compute correlation matrix between sources"""
        if len(validated_signals) < 2:
            return {}

        # Create signal vectors
        signal_vectors = await self._create_signal_vectors(validated_signals)

        # Calculate correlation matrix
        correlation_matrix = np.corrcoef(signal_vectors.T)

        # Convert to dict with source names
        sources = list(validated_signals.keys())
        matrix = {}

        for i, source1 in enumerate(sources):
            matrix[source1] = {}
            for j, source2 in enumerate(sources):
                matrix[source1][source2] = float(correlation_matrix[i][j])

        return matrix

    async def _create_signal_vectors(self, validated_signals: Dict) -> np.ndarray:
        """Create normalized signal vectors for correlation calculation"""
        vectors = []

        for source_name, signal in validated_signals.items():
            vector = []

            # Direction: 1 for LONG, -1 for SHORT, 0 for NEUTRAL
            direction = signal.get("direction", "NEUTRAL").upper()
            if direction == "LONG":
                vector.append(1)
            elif direction == "SHORT":
                vector.append(-1)
            else:
                vector.append(0)

            # Confidence (0-1)
            vector.append(max(0.0, min(1.0, signal.get("confidence", 0.5))))

            # Strength (0-1)
            vector.append(max(0.0, min(1.0, signal.get("strength", 0.5))))

            # Score (0-1)
            score = signal.get("score", 50)
            vector.append(max(0.0, min(1.0, score / 100)))

            vectors.append(vector)

        return np.array(vectors)


class ConsensusDetector:
    """
    Consensus detection system
    """

    def __init__(self):
        self.agreement_thresholds = {
            "strong": 0.85,
            "medium": 0.7,
            "weak": 0.5,
        }

    async def detect_consensus(self, validated_signals: Dict, correlation_matrix: Dict) -> Dict:
        """Detect consensus among signals"""
        if not validated_signals:
            return self._create_empty_consensus_report()

        # Direction agreement
        direction_agreement = await self._calculate_direction_agreement(validated_signals)

        # Confidence agreement
        confidence_agreement = await self._calculate_confidence_agreement(validated_signals)

        # Strength agreement
        strength_agreement = await self._calculate_strength_agreement(validated_signals)

        # Correlation agreement
        correlation_agreement = await self._calculate_correlation_agreement(correlation_matrix)

        # Overall consensus score
        overall_consensus = np.mean(
            [
                direction_agreement,
                confidence_agreement,
                strength_agreement,
                correlation_agreement,
            ]
        )

        # Consensus type
        consensus_type = await self._determine_consensus_type(
            overall_consensus, direction_agreement
        )

        return {
            "overall_consensus": overall_consensus,
            "direction_agreement": direction_agreement,
            "confidence_agreement": confidence_agreement,
            "strength_agreement": strength_agreement,
            "correlation_agreement": correlation_agreement,
            "type": consensus_type,
            "source_count": len(validated_signals),
            "agreement_level": await self._determine_agreement_level(overall_consensus),
        }

    async def _calculate_direction_agreement(self, validated_signals: Dict) -> float:
        """Calculate direction agreement score"""
        directions = [s.get("direction", "NEUTRAL").upper() for s in validated_signals.values()]

        from collections import Counter

        direction_counts = Counter(directions)

        most_common = direction_counts.most_common(1)
        if not most_common:
            return 0.0

        max_count, _ = most_common[0]
        return direction_counts[max_count] / len(directions)

    async def _calculate_confidence_agreement(self, validated_signals: Dict) -> float:
        """Calculate confidence agreement (lower variance = higher agreement)"""
        confidences = [s.get("confidence", 0.5) for s in validated_signals.values()]

        if len(confidences) < 2:
            return 0.0

        variance = np.var(confidences)
        return max(0.0, 1 - variance * 10)

    async def _calculate_strength_agreement(self, validated_signals: Dict) -> float:
        """Calculate strength agreement"""
        strengths = [s.get("strength", 0.5) for s in validated_signals.values()]

        if len(strengths) < 2:
            return 0.0

        variance = np.var(strengths)
        return max(0.0, 1 - variance * 10)

    async def _calculate_correlation_agreement(self, correlation_matrix: Dict) -> float:
        """Calculate average correlation agreement"""
        if not correlation_matrix:
            return 0.0

        correlations = []
        sources = list(correlation_matrix.keys())

        for i in range(len(sources)):
            for j in range(i + 1, len(sources)):
                corr = correlation_matrix[sources[i]][sources[j]]
                correlations.append(corr)

        if not correlations:
            return 0.0

        return np.mean(correlations)

    async def _determine_consensus_type(
        self, overall_consensus: float, direction_agreement: float
    ) -> str:
        """Determine consensus type"""
        if overall_consensus >= self.agreement_thresholds["strong"]:
            if direction_agreement >= 0.9:
                return "unanimous"
            else:
                return "strong"
        elif overall_consensus >= self.agreement_thresholds["medium"]:
            return "medium"
        elif overall_consensus >= self.agreement_thresholds["weak"]:
            return "weak"
        else:
            return "conflicting"

    async def _determine_agreement_level(self, overall_consensus: float) -> str:
        """Determine agreement level"""
        if overall_consensus >= self.agreement_thresholds["strong"]:
            return "STRONG"
        elif overall_consensus >= self.agreement_thresholds["medium"]:
            return "MEDIUM"
        elif overall_consensus >= self.agreement_thresholds["weak"]:
            return "WEAK"
        else:
            return "LOW"

    def _create_empty_consensus_report(self) -> Dict:
        """Create empty consensus report"""
        return {
            "overall_consensus": 0.0,
            "direction_agreement": 0.0,
            "confidence_agreement": 0.0,
            "strength_agreement": 0.0,
            "correlation_agreement": 0.0,
            "type": "none",
            "source_count": 0,
            "agreement_level": "LOW",
        }


class PatternMatcher:
    """
    Pattern matching system for multi-source signal analysis
    """

    def __init__(self):
        self.known_patterns = {
            "strong_momentum": {
                "name": "Strong Momentum",
                "description": "Multiple sources showing strong upward momentum",
                "required_direction": "LONG",
                "min_sources": 3,
                "min_strength": 0.8,
            },
            "selling_pressure": {
                "name": "Heavy Selling Pressure",
                "description": "Consistent bearish signals across sources",
                "required_direction": "SHORT",
                "min_sources": 2,
                "min_strength": 0.7,
            },
            "neutral_balance": {
                "name": "Neutral Balance",
                "description": "Signals evenly split between bullish and bearish",
                "required_direction": "NEUTRAL",
                "min_sources": 2,
                "min_balance": 0.4,
            },
            "sentiment_shift": {
                "name": "Sentiment Shift",
                "description": "Recent shift in sentiment direction",
                "required_direction": "CHANGE",
                "min_sources": 2,
                "min_confidence_change": 0.3,
            },
        }

    async def match_patterns(self, validated_signals: Dict) -> Dict:
        """Match patterns in multi-source signals"""
        patterns_found = []

        for pattern_name, pattern_info in self.known_patterns.items():
            if await self._match_pattern(validated_signals, pattern_info):
                patterns_found.append(pattern_info)

        return {
            "patterns_found": len(patterns_found),
            "matched_patterns": patterns_found,
        }

    async def _match_pattern(self, validated_signals: Dict, pattern_info: Dict) -> bool:
        """Match a specific pattern"""
        required_direction = pattern_info.get("required_direction", "ANY").upper()

        if required_direction == "CHANGE":
            return await self._match_sentiment_shift(validated_signals, pattern_info)

        # Count signals matching required direction
        matching_signals = []
        for signal in validated_signals.values():
            direction = signal.get("direction", "NEUTRAL").upper()
            if direction == required_direction:
                strength = signal.get("strength", 0.5)
                if strength >= pattern_info.get("min_strength", 0.5):
                    matching_signals.append(signal)

        return len(matching_signals) >= pattern_info.get("min_sources", 2)

    async def _match_sentiment_shift(self, validated_signals: Dict, pattern_info: Dict) -> bool:
        """Match sentiment shift pattern"""
        # Simple sentiment shift detection
        if len(validated_signals) < 2:
            return False

        # Check if we have recent historical data
        return False


# Global instances
multi_source_correlator = MultiSourceCorrelationSystem()
signal_fusion_engine = SignalFusionEngine()
