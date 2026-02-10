"""
IBIS Cognition - Higher-Order Thinking
By TheOsirisLabs.com | Founder: Youssef SalahEldin

Implements AGI-level cognitive capabilities:
- Reflection: Self-analysis of decisions
- Planning: Multi-step strategy formulation
- Metacognition: Thinking about thinking
- Adaptation: Real-time strategy adjustment
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class CognitiveState(Enum):
    """IBIS cognitive states."""

    OBSERVING = "observing"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    ACTING = "acting"
    REFLECTING = "reflecting"
    ADAPTING = "adapting"


@dataclass
class Thought:
    """Single thought record."""

    id: str
    timestamp: datetime
    thought_type: str
    content: str
    confidence: float
    related_thoughts: List[str] = field(default_factory=list)
    conclusions: List[str] = field(default_factory=list)


@dataclass
class SelfAssessment:
    """Self-assessment of current state."""

    cognitive_state: str
    confidence_level: float
    performance_score: float
    concerns: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    risk_awareness: float = 0.5


@dataclass
class Plan:
    """Multi-step trading plan."""

    id: str
    timestamp: datetime
    goal: str
    steps: List[Dict]
    contingencies: List[Dict]
    expected_outcome: str
    success_criteria: List[str]
    risk_assessment: str


class ReflectionEngine:
    """Reflection engine for post-decision analysis."""

    def __init__(self, brain, memory):
        self.brain = brain
        self.memory = memory
        self.reflection_history: List[Dict] = []

    async def reflect_on_decision(
        self, decision: Dict, outcome: Dict, market_context: Dict
    ) -> Dict:
        """Comprehensive reflection on a trading decision."""
        prompt = f"""
        IBIS Reflection Analysis

        DECISION MADE:
        - Action: {decision.get("action")}
        - Confidence: {decision.get("confidence")}%
        - Reasoning: {decision.get("reasoning", "N/A")}
        - Regime: {decision.get("regime")}

        OUTCOME:
        - Result: {outcome.get("result", "PENDING")}
        - P&L: {outcome.get("pnl_pct", 0):.2f}%
        - Duration: {outcome.get("duration", "N/A")}

        MARKET CONTEXT:
        - Actual Regime: {market_context.get("regime")}
        - Volatility: {market_context.get("volatility")}%
        - Trend: {market_context.get("trend_strength")}

        Analyze:
        1. Was the regime prediction correct?
        2. Did confidence match reality?
        3. What specific improvement?
        4. One actionable lesson?
        """

        response = await self.brain.complete(prompt, tier="summary")

        reflection = {
            "id": f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "decision_id": decision.get("id"),
            "outcome": outcome,
            "analysis": response.content,
            "confidence": response.confidence,
            "model_used": response.model,
        }

        self.reflection_history.append(reflection)

        lessons = self._extract_lessons(response.content)
        adjustments = self._extract_adjustments(response.content)

        await self.memory.store_reflection(
            decision.get("id", "unknown"),
            {
                "analysis": response.content,
                "lessons": lessons,
                "adjustments": adjustments,
            },
        )

        return reflection

    async def analyze_performance_trend(self, window: int = 50) -> Dict:
        """Analyze recent performance for trends."""
        recent = self.reflection_history[-window:]

        if len(recent) < 5:
            return {"status": "insufficient_data"}

        positive_reflections = sum(1 for r in recent if r.get("confidence", 0) > 0.6)
        negative_reflections = len(recent) - positive_reflections

        trend = (
            "improving" if positive_reflections > negative_reflections else "declining"
        )

        return {
            "window": window,
            "total_reflections": len(recent),
            "positive": positive_reflections,
            "negative": negative_reflections,
            "trend": trend,
            "avg_confidence": sum(r.get("confidence", 0) for r in recent) / len(recent),
        }

    def _extract_lessons(self, content: str) -> List[str]:
        """Extract lessons from reflection."""
        lessons = []
        for line in content.split("\n"):
            if "lesson" in line.lower() or "learn" in line.lower():
                lessons.append(line.strip())

        return lessons[:3]

    def _extract_adjustments(self, content: str) -> List[str]:
        """Extract adjustments from reflection."""
        adjustments = []
        for line in content.split("\n"):
            if "adjust" in line.lower() or "change" in line.lower():
                adjustments.append(line.strip())

        return adjustments[:3]


class PlanningEngine:
    """Multi-step planning engine."""

    def __init__(self, brain, memory):
        self.brain = brain
        self.memory = memory
        self.active_plans: Dict[str, Plan] = {}
        self.plan_history: List[Plan] = []

    async def create_trade_plan(
        self, symbol: str, goal: str, market_context: Dict
    ) -> Plan:
        """Create a multi-step trading plan."""
        prompt = f"""
        IBIS Trading Plan Creation

        GOAL: {goal}
        SYMBOL: {symbol}

        MARKET CONTEXT:
        - Current Regime: {market_context.get("regime")}
        - Volatility: {market_context.get("volatility")}%
        - Trend: {market_context.get("trend_strength")}
        - Confidence: {market_context.get("confidence")}%
        - Risk Level: {market_context.get("risk_level")}

        Create a detailed trading plan with:
        1. Entry trigger (specific conditions)
        2. Position size (based on risk)
        3. Take-profit level(s)
        4. Stop-loss level
        5. 3 contingency plans for adverse scenarios
        6. Success criteria

        Format as structured JSON with clear steps.
        """

        response = await self.brain.complete(prompt, tier="reasoning")

        plan = Plan(
            id=f"PLAN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            timestamp=datetime.now(),
            goal=goal,
            steps=self._parse_steps(response.content),
            contingencies=self._parse_contingencies(response.content),
            expected_outcome=self._extract_outcome(response.content),
            success_criteria=self._extract_criteria(response.content),
            risk_assessment=self._assess_risk(market_context),
        )

        self.active_plans[plan.id] = plan
        self.plan_history.append(plan)

        return plan

    def _parse_steps(self, content: str) -> List[Dict]:
        """Parse plan steps from response."""
        steps = []

        for line in content.split("\n"):
            if any(w in line.lower() for w in ["step", "entry", "exit", "stop"]):
                steps.append(
                    {"description": line.strip(), "completed": False, "timestamp": None}
                )

        return steps

    def _parse_contingencies(self, content: str) -> List[Dict]:
        """Parse contingencies from response."""
        contingencies = []

        for line in content.split("\n"):
            if "contingency" in line.lower() or "if" in line.lower():
                contingencies.append(
                    {"trigger": line.strip(), "action": "", "executed": False}
                )

        return contingencies

    def _extract_outcome(self, content: str) -> str:
        """Extract expected outcome."""
        for line in content.split("\n"):
            if "expected" in line.lower() or "outcome" in line.lower():
                return line.strip()

        return "To be determined"

    def _extract_criteria(self, content: str) -> List[str]:
        """Extract success criteria."""
        criteria = []

        for line in content.split("\n"):
            if "success" in line.lower() or "criteria" in line.lower():
                criteria.append(line.strip())

        return criteria

    def _assess_risk(self, context: Dict) -> str:
        """Assess plan risk."""
        risk_level = context.get("risk_level", "MEDIUM")

        risk_mapping = {
            "LOW": "Conservative plan - minimal deviation from strategy",
            "MEDIUM": "Standard plan - typical risk/reward setup",
            "HIGH": "Aggressive plan - wider stops, larger size",
            "EXTREME": "Speculative plan - high risk consideration",
        }

        return risk_mapping.get(risk_level, "Unknown risk profile")


class MetacognitionEngine:
    """Metacognition engine - thinking about thinking."""

    def __init__(self, brain, memory):
        self.brain = brain
        self.memory = memory
        self.cognitive_state = CognitiveState.OBSERVING
        self.thought_history: List[Thought] = []
        self.self_assessment: Optional[SelfAssessment] = None

    async def assess_current_state(self) -> SelfAssessment:
        """Comprehensive self-assessment of IBIS's current state."""
        memory_stats = await self.memory.get_statistics()
        brain_metrics = self.brain.get_metrics()

        prompt = f"""
        IBIS Metacognitive Self-Assessment

        CURRENT METRICS:
        - Total requests: {brain_metrics.get("total_requests", 0)}
        - Avg latency: {brain_metrics.get("avg_latency_ms", 0):.0f}ms
        - Trades stored: {memory_stats.get("episodic", {}).get("total_trades_stored", 0)}
        - Win rate: {memory_stats.get("episodic", {}).get("win_rate", 0):.1%}
        - Patterns learned: {memory_stats.get("patterns_count", 0)}
        - Rules discovered: {memory_stats.get("rules_count", 0)}

        CURRENT STATE: {self.cognitive_state.value}

        Assess:
        1. Performance quality (0-100)
        2. Confidence level (0-100)
        3. Key strengths
        4. Areas for improvement
        5. Risk awareness (0-100)

        Output as structured assessment.
        """

        response = await self.brain.complete(prompt, tier="reasoning")

        self.self_assessment = SelfAssessment(
            cognitive_state=self.cognitive_state.value,
            confidence_level=response.confidence * 100,
            performance_score=self._calculate_performance(memory_stats),
            concerns=self._extract_concerns(response.content),
            strengths=self._extract_strengths(response.content),
            improvements=self._extract_improvements(response.content),
            risk_awareness=self._estimate_risk_awareness(response.content),
        )

        return self.self_assessment

    async def monitor_decision_quality(self, decision: Dict) -> Dict:
        """Monitor quality of ongoing decisions."""
        decision_confidence = decision.get("confidence", 0.5)
        historical_confidence = self._get_historical_confidence()

        comparison = {
            "current_confidence": decision_confidence,
            "historical_avg": historical_confidence,
            "delta": decision_confidence - historical_confidence,
            "quality_check": self._assess_quality(
                decision_confidence, historical_confidence
            ),
        }

        if abs(comparison["delta"]) > 0.2:
            comparison["alert"] = (
                "Confidence significantly different from historical average"
            )

        return comparison

    async def detect_cognitive_biases(self, decisions: List[Dict]) -> Dict:
        """Detect potential cognitive biases in decisions."""
        biases = {}

        high_confidence_losses = [
            d
            for d in decisions
            if d.get("confidence", 0) > 0.8 and d.get("outcome") == "LOSS"
        ]
        if len(high_confidence_losses) > 3:
            biases["overconfidence"] = {
                "detected": True,
                "severity": len(high_confidence_losses) / len(decisions),
                "recommendation": "Reduce confidence thresholds, implement more validation",
            }

        recent_losses = decisions[-10:]
        loss_streak = sum(1 for d in recent_losses if d.get("outcome") == "LOSS")
        if loss_streak >= 3:
            biases["recency"] = {
                "detected": True,
                "severity": loss_streak / 10,
                "recommendation": "Review historical success rate",
            }

        return biases if biases else {"status": "No significant biases detected"}

    async def optimize_parameters(self) -> Dict:
        """Suggest parameter optimizations based on performance data."""
        prompt = """
        IBIS Parameter Optimization

        Analyze the following performance data and suggest parameter adjustments:

        Current parameters:
        - Scalper: profit_target=0.05%, stop_loss=0.1%
        - Momentum: trailing_stop=2%
        - Volatility: profit_target=8%, stop_loss=4%
        - Confidence threshold: 50%

        Output:
        1. Parameters that should increase
        2. Parameters that should decrease
        3. New parameters to consider
        4. Rationale for each change
        """

        response = await self.brain.complete(prompt, tier="reasoning")

        return {
            "recommendations": response.content,
            "model": response.model,
            "timestamp": datetime.now().isoformat(),
        }

    async def set_cognitive_state(self, new_state: CognitiveState):
        """Update cognitive state."""
        old_state = self.cognitive_state
        self.cognitive_state = new_state

        await self.think(
            thought_type="state_change",
            content=f"Cognitive state: {old_state.value} -> {new_state.value}",
        )

    async def think(
        self,
        thought_type: str,
        content: str,
        confidence: float = 0.5,
        conclusions: List[str] = None,
    ) -> Thought:
        """Record a thought process."""
        thought = Thought(
            id=f"THT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            timestamp=datetime.now(),
            thought_type=thought_type,
            content=content,
            confidence=confidence,
            conclusions=conclusions or [],
        )

        self.thought_history.append(thought)
        return thought

    def _calculate_performance(self, stats: Dict) -> float:
        """Calculate overall performance score."""
        win_rate = stats.get("episodic", {}).get("win_rate", 0.5)
        return win_rate * 100

    def _get_historical_confidence(self) -> float:
        """Get average historical confidence."""
        if not self.thought_history:
            return 0.5
        return sum(t.confidence for t in self.thought_history) / len(
            self.thought_history
        )

    def _assess_quality(self, current: float, historical: float) -> str:
        """Assess decision quality."""
        delta = current - historical

        if abs(delta) < 0.1:
            return "APPROPRIATE"
        elif delta > 0:
            return "ABOVE AVERAGE"
        else:
            return "BELOW AVERAGE"

    def _estimate_risk_awareness(self, content: str) -> float:
        """Estimate risk awareness from content."""
        risk_words = ["risk", "danger", "caution", "safety", "protect", "limit"]
        content_lower = content.lower()
        matches = sum(1 for w in risk_words if w in content_lower)
        return min(1.0, 0.5 + matches * 0.1)

    def _extract_concerns(self, content: str) -> List[str]:
        """Extract concerns from assessment."""
        concerns = []
        for line in content.split("\n"):
            if "concern" in line.lower() or "worry" in line.lower():
                concerns.append(line.strip())
        return concerns[:3]

    def _extract_strengths(self, content: str) -> List[str]:
        """Extract strengths from assessment."""
        strengths = []
        for line in content.split("\n"):
            if "strength" in line.lower() or "strong" in line.lower():
                strengths.append(line.strip())
        return strengths[:3]

    def _extract_improvements(self, content: str) -> List[str]:
        """Extract improvements from assessment."""
        improvements = []
        for line in content.split("\n"):
            if "improve" in line.lower():
                improvements.append(line.strip())
        return improvements[:3]


class AdaptationEngine:
    """Real-time adaptation engine."""

    def __init__(self, brain, memory, metacognition):
        self.brain = brain
        self.memory = memory
        self.metacognition = metacognition
        self.adaptations: List[Dict] = []
        self.parameter_overrides: Dict = {}

    async def adapt_to_regime(self, new_regime: str, context: Dict) -> Dict:
        """Adapt strategy to new market regime."""
        adaptation = {
            "timestamp": datetime.now().isoformat(),
            "trigger": f"Regime change to {new_regime}",
            "previous_regime": context.get("previous_regime"),
            "new_regime": new_regime,
            "changes": [],
            "reasoning": "",
        }

        if new_regime == "SCALPER":
            adaptation["changes"] = [
                {"param": "mode", "value": "SCALPER"},
                {"param": "profit_target", "value": "0.05%"},
                {"param": "stop_loss", "value": "0.1%"},
            ]
            adaptation["reasoning"] = "Calm market - focus on spread harvesting"

        elif new_regime == "MOMENTUM":
            adaptation["changes"] = [
                {"param": "mode", "value": "MOMENTUM"},
                {"param": "trailing_stop", "value": "2%"},
            ]
            adaptation["reasoning"] = "Trending market - ride momentum"

        elif new_regime == "VOLATILITY":
            adaptation["changes"] = [
                {"param": "mode", "value": "VOLATILITY"},
                {"param": "profit_target", "value": "8%"},
                {"param": "stop_loss", "value": "4%"},
            ]
            adaptation["reasoning"] = "Chaotic market - exploit volatility"

        self.adaptations.append(adaptation)
        self._apply_overrides(adaptation["changes"])

        return adaptation

    async def adapt_to_loss_streak(self, streak_length: int) -> Dict:
        """Adapt strategy after consecutive losses."""
        adaptation = {
            "timestamp": datetime.now().isoformat(),
            "trigger": f"Loss streak: {streak_length} consecutive losses",
            "changes": [],
            "reasoning": "",
        }

        if streak_length >= 3:
            adaptation["changes"] = [
                {"param": "confidence_threshold", "value": "0.7"},
                {"param": "position_size_multiplier", "value": "0.5"},
            ]
            adaptation["reasoning"] = "Increased caution after losses"

        if streak_length >= 5:
            adaptation["changes"].extend(
                [
                    {"param": "mode", "value": "SCALPER"},
                    {"param": "position_size_multiplier", "value": "0.25"},
                ]
            )
            adaptation["reasoning"] = "Maximum caution - scalper mode only"

        self.adaptations.append(adaptation)
        self._apply_overrides(adaptation["changes"])

        return adaptation

    def _apply_overrides(self, changes: List[Dict]):
        """Apply parameter overrides."""
        for change in changes:
            self.parameter_overrides[change["param"]] = change["value"]

    def get_overrides(self) -> Dict:
        """Get current parameter overrides."""
        return self.parameter_overrides

    def clear_overrides(self):
        """Clear all parameter overrides."""
        self.parameter_overrides = {}


class IBISCognition:
    """Unified cognition system coordinating all cognitive engines."""

    def __init__(self, brain, memory):
        self.brain = brain
        self.memory = memory

        self.reflection = ReflectionEngine(brain, memory)
        self.planning = PlanningEngine(brain, memory)
        self.metacognition = MetacognitionEngine(brain, memory)
        self.adaptation = AdaptationEngine(brain, memory, self.metacognition)

    async def full_cycle(self, decision: Dict, outcome: Dict, context: Dict) -> Dict:
        """Complete cognitive cycle: Act -> Reflect -> Learn -> Adapt."""
        await self.memory.working.store_decision(decision)

        if outcome:
            reflection = await self.reflection.reflect_on_decision(
                decision, outcome, context
            )

            if outcome.get("outcome") == "LOSS":
                adaptation = await self.adaptation.adapt_to_loss_streak(
                    self._count_consecutive_losses()
                )
            else:
                adaptation = None

            return {
                "reflection": reflection,
                "adaptation": adaptation,
                "new_parameters": self.adaptation.get_overrides(),
            }

        return {"status": "Decision stored, awaiting outcome"}
