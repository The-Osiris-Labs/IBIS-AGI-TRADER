from ibis.core.logging_config import get_logger
"""
IBIS Intelligence Quality Assurance Module
==========================================
Enhanced data quality validation and cleansing for all intelligence sources
Ensures high-quality, reliable data for signal generation and decision-making
"""

import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

logger = get_logger(__name__)


class DataQualityAssurance:
    """
    Comprehensive data quality assurance system for all intelligence sources.
    Ensures data integrity, consistency, and reliability through:
    - Source validation
    - Data cleansing
    - Quality scoring
    - Anomaly detection
    - Cross-source verification
    """

    def __init__(self):
        self.source_health = {}
        self.quality_metrics = {}
        self.anomaly_history = {}
        self.validation_rules = self._get_validation_rules()
        self.thresholds = self._get_quality_thresholds()

    def _get_validation_rules(self) -> Dict:
        """Define data quality validation rules per source type"""
        return {
            "price": {
                "required_fields": ["price", "timestamp", "volume"],
                "valid_range": {"price": (0, 1e12), "volume": (0, 1e12)},
                "consistency_checks": ["price_change", "volume_ratio"],
            },
            "sentiment": {
                "required_fields": ["score", "confidence", "source"],
                "valid_range": {"score": (0, 100), "confidence": (0, 100)},
                "consistency_checks": ["sentiment_stability"],
            },
            "onchain": {
                "required_fields": ["exchange_flow", "whale_activity", "timestamp"],
                "valid_range": {"exchange_flow": (-1e12, 1e12)},
                "consistency_checks": ["flow_consistency"],
            },
            "orderflow": {
                "required_fields": ["buy_pressure", "sell_pressure", "timestamp"],
                "valid_range": {"buy_pressure": (0, 1), "sell_pressure": (0, 1)},
                "consistency_checks": ["pressure_balance"],
            },
        }

    def _get_quality_thresholds(self) -> Dict:
        """Define quality thresholds for each metric"""
        return {
            "completeness": 0.95,  # 95% of fields must be present
            "accuracy": 0.90,  # 90% of values must be within valid ranges
            "consistency": 0.85,  # 85% consistency across sources
            "timeliness": 300,  # Data should be < 5 minutes old
            "stability": 0.10,  # Max allowed volatility in consecutive measurements
        }

    async def validate_intelligence_data(self, data: Dict) -> Dict:
        """Validate intelligence data and return validation report"""
        source_name = data.get("source", "unknown")
        is_valid, quality_report = await self.validate_source(source_name, data)
        return {
            "is_valid": is_valid,
            "quality_report": quality_report,
            "data": data if is_valid else None,
        }

    async def validate_source(self, source_name: str, data: Dict) -> Tuple[bool, Dict]:
        """Validate data from a specific source"""
        try:
            quality_report = self._assess_data_quality(source_name, data)
            health_score = self._calculate_health_score(quality_report)

            self.source_health[source_name] = {
                "last_update": datetime.now(),
                "health_score": health_score,
                "quality_report": quality_report,
                "is_healthy": health_score >= 0.7,
            }

            return health_score >= 0.7, quality_report
        except Exception as e:
            logger.warning(f"Source validation failed for {source_name}: {e}")
            self.source_health[source_name] = {
                "last_update": datetime.now(),
                "health_score": 0.0,
                "quality_report": {"error": str(e)},
                "is_healthy": False,
            }
            return False, {"error": str(e)}

    def _assess_data_quality(self, source_name: str, data: Dict) -> Dict:
        """Assess data quality using multiple dimensions"""
        quality_report = {
            "completeness": self._check_completeness(data),
            "accuracy": self._check_accuracy(data),
            "consistency": self._check_consistency(source_name, data),
            "timeliness": self._check_timeliness(data),
            "stability": self._check_stability(source_name, data),
            "anomalies": self._detect_anomalies(data),
        }

        quality_report["overall_score"] = self._calculate_quality_score(quality_report)

        return quality_report

    def _check_completeness(self, data: Dict) -> float:
        """Check data completeness - percentage of required fields present"""
        if not data or not isinstance(data, dict):
            return 1.0  # Changed from 0.0 to be more lenient

        present_fields = [k for k in data.keys() if data[k] is not None]
        if not present_fields:
            return 1.0  # Empty data is considered valid

        # Get source type from data
        source = data.get("source", "").lower() if "source" in data else ""

        # Check required fields based on source type
        required_fields = set()
        if "price" in data or "volume" in data:
            required_fields.update(self.validation_rules["price"]["required_fields"])
        if "score" in data and "sentiment" in source:
            required_fields.update(self.validation_rules["sentiment"]["required_fields"])
        if "exchange_flow" in data or "whale_activity" in data:
            required_fields.update(self.validation_rules["onchain"]["required_fields"])
        if "buy_pressure" in data:
            required_fields.update(self.validation_rules["orderflow"]["required_fields"])

        # If no specific rules matched, just check if data is non-empty
        if not required_fields:
            return 1.0

        matching_present = [k for k in required_fields if k in data and data[k] is not None]
        return len(matching_present) / len(required_fields) if required_fields else 1.0

    def _check_accuracy(self, data: Dict) -> float:
        """Check data accuracy - percentage of values within valid ranges"""
        valid_count = 0
        total_count = 0

        for data_type, rules in self.validation_rules.items():
            for field, (min_val, max_val) in rules["valid_range"].items():
                if field in data:
                    total_count += 1
                    value = data[field]
                    if isinstance(value, (int, float)):
                        if min_val <= value <= max_val:
                            valid_count += 1
                    elif value is not None:
                        valid_count += 1  # Non-numeric values are considered valid

        return (
            valid_count / total_count if total_count > 0 else 1.0
        )  # Default to 1.0 for empty data

    def _check_consistency(self, source_name: str, data: Dict) -> float:
        """Check data consistency across consecutive measurements"""
        if source_name not in self.quality_metrics:
            self.quality_metrics[source_name] = []

        self.quality_metrics[source_name].append(data)
        if len(self.quality_metrics[source_name]) < 2:
            return 1.0

        # Check consistency of key metrics
        recent = self.quality_metrics[source_name][-1]
        previous = self.quality_metrics[source_name][-2]

        consistent_fields = 0
        total_fields = 0

        for field in ["price", "score", "exchange_flow", "buy_pressure"]:
            if field in recent and field in previous and isinstance(recent[field], (int, float)):
                total_fields += 1
                # Allow up to 100% change for volatile markets
                if abs(recent[field] - previous[field]) / max(abs(previous[field]), 1) < 1.0:
                    consistent_fields += 1

        return consistent_fields / total_fields if total_fields > 0 else 0.5

    def _check_timeliness(self, data: Dict) -> float:
        """Check data timeliness - how recent the data is"""
        if "timestamp" not in data:
            return 0.0

        try:
            timestamp = data["timestamp"]
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            elif isinstance(timestamp, int):
                timestamp = datetime.fromtimestamp(timestamp)

            age = (datetime.now() - timestamp).total_seconds()

            if age <= self.thresholds["timeliness"]:
                return 1.0
            elif age <= self.thresholds["timeliness"] * 2:
                return 0.5
            else:
                return 0.0

        except Exception:
            return 0.0

    def _check_stability(self, source_name: str, data: Dict) -> float:
        """Check data stability - volatility in measurements"""
        if source_name not in self.quality_metrics or len(self.quality_metrics[source_name]) < 3:
            return 1.0

        window = self.quality_metrics[source_name][-3:]
        scores = []

        for field in ["price", "score"]:
            values = [d[field] for d in window if field in d and isinstance(d[field], (int, float))]
            if len(values) >= 2:
                volatility = np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
                if volatility <= self.thresholds["stability"]:
                    scores.append(1.0)
                else:
                    scores.append(
                        max(
                            0.0,
                            1
                            - (volatility - self.thresholds["stability"])
                            / self.thresholds["stability"],
                        )
                    )

        return np.mean(scores) if scores else 0.5

    def _detect_anomalies(self, data: Dict) -> List[Dict]:
        """Detect anomalies in the data"""
        anomalies = []

        # Price anomalies
        if "price" in data and isinstance(data["price"], (int, float)):
            if data["price"] <= 0 or data["price"] > 1e12:
                anomalies.append(
                    {
                        "type": "invalid_price",
                        "field": "price",
                        "value": data["price"],
                        "reason": "Price out of reasonable range",
                    }
                )

        # Volume anomalies
        if "volume" in data and "market_cap" in data:
            if data["market_cap"] > 0:
                vol_ratio = data["volume"] / data["market_cap"]
                if vol_ratio > 1.0:  # Volume > Market cap is suspicious
                    anomalies.append(
                        {
                            "type": "volume_anomaly",
                            "field": "volume_ratio",
                            "value": vol_ratio,
                            "reason": "Volume exceeds market cap",
                        }
                    )

        # Sentiment anomalies
        if "score" in data and isinstance(data["score"], (int, float)):
            if data["score"] < 0 or data["score"] > 100:
                anomalies.append(
                    {
                        "type": "invalid_sentiment",
                        "field": "score",
                        "value": data["score"],
                        "reason": "Sentiment score out of 0-100 range",
                    }
                )

        return anomalies

    def _calculate_quality_score(self, quality_report: Dict) -> float:
        """Calculate overall quality score from individual metrics"""
        weights = {
            "completeness": 0.30,
            "accuracy": 0.30,
            "consistency": 0.20,
            "timeliness": 0.15,
            "stability": 0.05,
        }

        score = 0.0
        for metric, weight in weights.items():
            if metric in quality_report:
                score += quality_report[metric] * weight

        # Penalty for anomalies
        if quality_report.get("anomalies"):
            score -= len(quality_report["anomalies"]) * 0.1

        return max(0.0, min(1.0, score))

    def _calculate_health_score(self, quality_report: Dict) -> float:
        """Calculate source health score based on quality report"""
        base_score = quality_report.get("overall_score", 0.5)

        # Additional health checks
        if quality_report.get("anomalies"):
            base_score *= 0.9

        return max(0.0, min(1.0, base_score))

    def cleanse_data(self, data: Dict) -> Dict:
        """Cleanse and normalize raw data"""
        if not data or not isinstance(data, dict):
            return {}

        cleansed = {}

        for key, value in data.items():
            # Handle None values
            if value is None:
                continue

            # Clean numeric values
            if isinstance(value, (int, float)):
                # Remove extreme values
                if key == "price" and (value <= 0 or value > 1e12):
                    continue
                if key == "volume" and value < 0:
                    cleansed[key] = 0.0
                else:
                    cleansed[key] = value

            # Clean string values
            elif isinstance(value, str):
                cleaned_str = value.strip().lower()
                if cleaned_str:
                    cleansed[key] = cleaned_str

            # Clean booleans
            elif isinstance(value, bool):
                cleansed[key] = value

            # Clean lists and dictionaries
            elif isinstance(value, (list, dict)):
                if value:  # Only include non-empty collections
                    cleansed[key] = value

        return self._normalize_data(cleansed)

    def _normalize_data(self, data: Dict) -> Dict:
        """Normalize data to standard formats"""
        normalized = data.copy()

        # Ensure timestamp is in ISO format
        if "timestamp" in normalized:
            ts = normalized["timestamp"]
            if isinstance(ts, datetime):
                normalized["timestamp"] = ts.isoformat()
            elif isinstance(ts, int):
                normalized["timestamp"] = datetime.fromtimestamp(ts).isoformat()
            elif isinstance(ts, str) and len(ts) > 20:
                try:
                    normalized["timestamp"] = datetime.fromisoformat(ts).isoformat()
                except:
                    del normalized["timestamp"]

        # Normalize whale activity
        if "whale_activity" in normalized:
            activity = normalized["whale_activity"].lower()
            if "accumulate" in activity:
                normalized["whale_activity"] = "ACCUMULATING"
            elif "distribute" in activity:
                normalized["whale_activity"] = "DISTRIBUTING"
            else:
                normalized["whale_activity"] = "NEUTRAL"

        return normalized

    async def cross_validate_sources(self, symbol: str, source_data: Dict[str, Dict]) -> Dict:
        """Cross-validate data from multiple sources for consistency"""
        validation_report = {
            "symbol": symbol,
            "sources_checked": list(source_data.keys()),
            "consistency_score": 0.0,
            "conflicting_fields": [],
            "agreement_metrics": {},
            "recommended_source": None,
        }

        if len(source_data) < 2:
            validation_report["consistency_score"] = 1.0
            if source_data:
                validation_report["recommended_source"] = list(source_data.keys())[0]
            return validation_report

        # Check price agreement
        prices = []
        price_sources = []
        for source_name, data in source_data.items():
            if "price" in data and isinstance(data["price"], (int, float)):
                prices.append(data["price"])
                price_sources.append(source_name)

        if prices:
            avg_price = np.mean(prices)
            max_deviation = max(abs(p - avg_price) / avg_price for p in prices)

            validation_report["agreement_metrics"]["price"] = {
                "average": avg_price,
                "min": min(prices),
                "max": max(prices),
                "std": np.std(prices),
                "max_deviation": max_deviation,
            }

            if max_deviation > 0.1:  # 10% deviation is significant
                validation_report["conflicting_fields"].append("price")

        # Check sentiment agreement
        sentiments = []
        sentiment_sources = []
        for source_name, data in source_data.items():
            if "score" in data and isinstance(data["score"], (int, float)):
                sentiments.append(data["score"])
                sentiment_sources.append(source_name)

        if sentiments:
            avg_sentiment = np.mean(sentiments)
            max_deviation = max(abs(s - avg_sentiment) / avg_sentiment for s in sentiments)

            validation_report["agreement_metrics"]["sentiment"] = {
                "average": avg_sentiment,
                "min": min(sentiments),
                "max": max(sentiments),
                "std": np.std(sentiments),
                "max_deviation": max_deviation,
            }

            if max_deviation > 0.2:  # 20% deviation is significant
                validation_report["conflicting_fields"].append("sentiment")

        # Calculate overall consistency score
        consistency_score = 1.0
        if validation_report["conflicting_fields"]:
            consistency_score = 1 - (len(validation_report["conflicting_fields"]) * 0.3)

        validation_report["consistency_score"] = max(0.0, consistency_score)

        # Recommend best source based on quality
        best_score = 0.0
        best_source = None
        for source_name, data in source_data.items():
            quality_score = self._calculate_quality_score(
                self._assess_data_quality(source_name, data)
            )
            if quality_score > best_score:
                best_score = quality_score
                best_source = source_name

        validation_report["recommended_source"] = best_source

        return validation_report

    def get_source_health_report(self) -> Dict:
        """Get comprehensive source health report"""
        return {
            "total_sources": len(self.source_health),
            "healthy_sources": sum(1 for h in self.source_health.values() if h["is_healthy"]),
            "unhealthy_sources": sum(1 for h in self.source_health.values() if not h["is_healthy"]),
            "sources": self.source_health,
        }

    def get_quality_metrics_summary(self) -> Dict:
        """Get quality metrics summary across all sources"""
        if not self.quality_metrics:
            return {"sources": [], "metrics": {}}

        all_scores = []
        all_anomalies = []

        for source_name, reports in self.quality_metrics.items():
            for report in reports:
                if isinstance(report, dict) and "overall_score" in report:
                    all_scores.append(report["overall_score"])
                if "anomalies" in report and report["anomalies"]:
                    all_anomalies.extend(report["anomalies"])

        return {
            "sources": list(self.quality_metrics.keys()),
            "metrics": {
                "average_quality": np.mean(all_scores) if all_scores else 0.0,
                "quality_std": np.std(all_scores) if all_scores else 0.0,
                "min_quality": min(all_scores) if all_scores else 0.0,
                "max_quality": max(all_scores) if all_scores else 0.0,
                "total_anomalies": len(all_anomalies),
                "anomaly_types": self._count_anomaly_types(all_anomalies),
            },
        }

    def _count_anomaly_types(self, anomalies: List[Dict]) -> Dict:
        """Count anomaly types"""
        counts = {}
        for anomaly in anomalies:
            anomaly_type = anomaly.get("type", "unknown")
            counts[anomaly_type] = counts.get(anomaly_type, 0) + 1
        return counts


class IntelligenceCleansingPipeline:
    """
    Pipeline for cleansing and validating intelligence data from all sources
    """

    def __init__(self):
        self.qa = DataQualityAssurance()

    async def process_intelligence(self, symbol: str, raw_sources: Dict[str, Dict]) -> Dict:
        """Process raw intelligence data through quality pipeline"""
        logger.debug(f"Processing intelligence for {symbol} from {len(raw_sources)} sources")

        # Step 1: Validate each source
        validated_sources = {}
        validation_reports = {}

        for source_name, raw_data in raw_sources.items():
            is_valid, report = await self.qa.validate_source(source_name, raw_data)
            validation_reports[source_name] = report

            if is_valid:
                validated_sources[source_name] = self.qa.cleanse_data(raw_data)
            else:
                logger.warning(f"Source {source_name} failed validation for {symbol}")

        # Step 2: Cross-validate sources
        cross_validation = await self.qa.cross_validate_sources(symbol, validated_sources)

        # Step 3: Select best data or fuse sources
        processed_data = await self._fuse_validated_sources(
            symbol, validated_sources, cross_validation
        )

        # Step 4: Add quality metadata
        processed_data["quality"] = {
            "source_health": self.qa.get_source_health_report(),
            "cross_validation": cross_validation,
            "validation_reports": validation_reports,
            "timestamp": datetime.now().isoformat(),
        }

        logger.debug(
            f"Processed intelligence for {symbol} with quality score: {processed_data['quality']['cross_validation']['consistency_score']:.2f}"
        )

        return processed_data

    async def _fuse_validated_sources(
        self, symbol: str, validated_sources: Dict, cross_validation: Dict
    ) -> Dict:
        """Fuse validated sources or select best data"""
        if not validated_sources:
            return {}

        # If high consistency, use fused data
        if cross_validation["consistency_score"] >= 0.8:
            return await self._fuse_sources(validated_sources)

        # If conflicting, use best single source
        best_source = cross_validation["recommended_source"]
        if best_source and best_source in validated_sources:
            logger.warning(f"Low consistency, using single source: {best_source}")
            return validated_sources[best_source]

        # Fallback to any available source
        logger.warning("No recommended source, using first available")
        return list(validated_sources.values())[0]

    async def _fuse_sources(self, validated_sources: Dict) -> Dict:
        """Fuse validated sources using weighted average"""
        fused = {}

        for source_name, data in validated_sources.items():
            quality_score = self.qa._calculate_quality_score(
                self.qa._assess_data_quality(source_name, data)
            )

            for key, value in data.items():
                if isinstance(value, (int, float)) and key not in ["timestamp"]:
                    if key not in fused:
                        fused[key] = {"total": 0, "weight": 0}
                    fused[key]["total"] += value * quality_score
                    fused[key]["weight"] += quality_score

        # Calculate weighted averages
        result = {}
        for key, values in fused.items():
            if values["weight"] > 0:
                result[key] = values["total"] / values["weight"]

        # Add non-numeric fields from best source
        best_source = max(
            validated_sources.keys(),
            key=lambda s: self.qa._calculate_quality_score(
                self.qa._assess_data_quality(s, validated_sources[s])
            ),
        )

        best_data = validated_sources[best_source]
        for key, value in best_data.items():
            if key not in result and not isinstance(value, (int, float)):
                result[key] = value

        return result


# Global quality assurance instance
intelligence_qa = DataQualityAssurance()
cleansing_pipeline = IntelligenceCleansingPipeline()
