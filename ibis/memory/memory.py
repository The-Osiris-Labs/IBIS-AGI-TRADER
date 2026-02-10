"""
IBIS Memory System - Learning & Experience Storage
By TheOsirisLabs.com | Founder: Youssef SalahEldin

Stores trading experiences for continuous learning:
- Episodic: Specific trade memories
- Semantic: Learned patterns and rules
- Working: Current context window
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict


class MemoryType(Enum):
    """Types of memories."""

    TRADE_EXPERIENCE = "trade"
    PATTERN_LEARNED = "pattern"
    RULE_DISCOVERED = "rule"
    FAILURE_ANALYZED = "failure"
    SUCCESS_PATTERN = "success"
    REGIME_MEMORY = "regime"
    ADJUSTMENT_MADE = "adjustment"


@dataclass
class TradeMemory:
    """Single trade experience memory."""

    id: str
    timestamp: datetime
    symbol: str
    mode: str
    side: str
    entry_price: float
    exit_price: float
    pnl_pct: float
    pnl_abs: float
    duration_seconds: float
    regime_before: str
    regime_during: str
    regime_after: str
    volatility: float
    trend_strength: float
    spread: float
    order_flow: str
    outcome: str
    lessons: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    reflection: str = ""
    confidence_at_entry: float = 0.5
    confidence_at_exit: float = 0.5


@dataclass
class PatternMemory:
    """Learned market pattern."""

    id: str
    timestamp: datetime
    pattern_name: str
    description: str
    conditions: Dict
    success_rate: float
    sample_count: int
    avg_pnl: float
    avg_duration: float
    best_mode: str
    best_timeframe: str
    market_conditions: List[str]
    tags: List[str] = field(default_factory=list)
    confidence: float = 0.5
    last_validated: datetime = field(default_factory=datetime.now)


@dataclass
class RuleMemory:
    """Discovered trading rule."""

    id: str
    timestamp: datetime
    rule_text: str
    category: str
    evidence_count: int
    success_count: int
    failure_count: int
    success_rate: float
    avg_pnl: float
    context: Dict
    confidence: float = 0.5
    validated: bool = False


class EpisodicMemory:
    """Episodic memory - stores specific trade experiences."""

    def __init__(self, storage_path: str = "data/ibis_memories.json"):
        self.storage_path = storage_path
        self.trades: List[TradeMemory] = []
        self.max_trades = 10000
        self._load()

    async def store_trade(self, trade_data: Dict) -> TradeMemory:
        """Store a trade experience."""
        trade = TradeMemory(
            id=trade_data.get("id", f"TRD-{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            timestamp=trade_data.get("timestamp", datetime.now()),
            symbol=trade_data.get("symbol"),
            mode=trade_data.get("mode"),
            side=trade_data.get("side"),
            entry_price=trade_data.get("entry_price"),
            exit_price=trade_data.get("exit_price"),
            pnl_pct=trade_data.get("pnl_pct", 0),
            pnl_abs=trade_data.get("pnl_abs", 0),
            duration_seconds=trade_data.get("duration_seconds", 0),
            regime_before=trade_data.get("regime_before"),
            regime_during=trade_data.get("regime_during"),
            regime_after=trade_data.get("regime_after"),
            volatility=trade_data.get("volatility", 0),
            trend_strength=trade_data.get("trend_strength", 0),
            spread=trade_data.get("spread", 0),
            order_flow=trade_data.get("order_flow"),
            outcome=self._determine_outcome(trade_data),
            lessons=trade_data.get("lessons", []),
            tags=trade_data.get("tags", []),
            reflection=trade_data.get("reflection", ""),
            confidence_at_entry=trade_data.get("confidence_entry", 0.5),
            confidence_at_exit=trade_data.get("confidence_exit", 0.5),
        )

        self.trades.append(trade)

        if len(self.trades) > self.max_trades:
            self.trades = self.trades[-self.max_trades :]

        await self._save()
        return trade

    async def get_recent_trades(
        self, symbol: str = None, mode: str = None, limit: int = 50
    ) -> List[TradeMemory]:
        """Get recent trades with optional filters."""
        filtered = self.trades

        if symbol:
            filtered = [t for t in filtered if t.symbol == symbol]
        if mode:
            filtered = [t for t in filtered if t.mode == mode]

        return sorted(filtered, key=lambda x: x.timestamp, reverse=True)[:limit]

    async def get_winning_patterns(self) -> Dict:
        """Analyze winning trades for patterns."""
        wins = [t for t in self.trades if t.outcome == "WIN"]
        patterns = defaultdict(lambda: {"count": 0, "total_pnl": 0, "avg_pnl": 0})

        for trade in wins:
            key = f"{trade.mode}_{trade.regime_during}"
            patterns[key]["count"] += 1
            patterns[key]["total_pnl"] += trade.pnl_abs

        for key in patterns:
            patterns[key]["avg_pnl"] = (
                patterns[key]["total_pnl"] / patterns[key]["count"]
            )

        return dict(patterns)

    async def get_failure_patterns(self) -> Dict:
        """Analyze losing trades for patterns."""
        losses = [t for t in self.trades if t.outcome == "LOSS"]
        patterns = defaultdict(lambda: {"count": 0, "total_loss": 0})

        for trade in losses:
            key = f"{trade.mode}_{trade.regime_during}"
            patterns[key]["count"] += 1
            patterns[key]["total_loss"] += abs(trade.pnl_abs)

        return dict(patterns)

    async def get_mode_performance(self) -> Dict:
        """Calculate performance metrics by mode."""
        performance = {}

        for mode in ["SCALPER", "MOMENTUM", "VOLATILITY"]:
            mode_trades = [t for t in self.trades if t.mode == mode]

            if mode_trades:
                wins = len([t for t in mode_trades if t.outcome == "WIN"])
                total_pnl = sum(t.pnl_abs for t in mode_trades)

                performance[mode] = {
                    "total_trades": len(mode_trades),
                    "wins": wins,
                    "losses": len(mode_trades) - wins,
                    "win_rate": wins / len(mode_trades),
                    "total_pnl": total_pnl,
                    "avg_pnl": total_pnl / len(mode_trades),
                    "avg_duration": sum(t.duration_seconds for t in mode_trades)
                    / len(mode_trades),
                }

        return performance

    async def get_statistics(self) -> Dict:
        """Get overall memory statistics."""
        total = len(self.trades)
        wins = len([t for t in self.trades if t.outcome == "WIN"])

        return {
            "total_trades_stored": total,
            "wins": wins,
            "losses": total - wins,
            "win_rate": wins / max(1, total),
            "total_pnl": sum(t.pnl_abs for t in self.trades),
            "avg_confidence": sum(t.confidence_at_entry for t in self.trades)
            / max(1, total),
            "memory_filled_pct": min(100, (total / self.max_trades) * 100),
        }

    def _determine_outcome(self, trade_data: Dict) -> str:
        """Determine trade outcome category."""
        pnl_pct = trade_data.get("pnl_pct", 0)

        if pnl_pct > 0.1:
            return "WIN"
        elif pnl_pct < -0.1:
            return "LOSS"
        else:
            return "BREAK_EVEN"

    def _load(self):
        """Load memories from disk."""
        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                self.trades = [TradeMemory(**t) for t in data.get("trades", [])]
        except:
            self.trades = []

    async def _save(self):
        """Save memories to disk."""
        data = {
            "last_saved": datetime.now().isoformat(),
            "trades": [asdict(t) for t in self.trades],
        }

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: open(self.storage_path, "w").write(
                json.dumps(data, indent=2, default=str)
            ),
        )


class SemanticMemory:
    """Semantic memory - stores learned patterns and rules."""

    def __init__(self, storage_path: str = "data/ibis_semantic.json"):
        self.storage_path = storage_path
        self.patterns: List[PatternMemory] = []
        self.rules: List[RuleMemory] = []
        self._load()

    async def store_pattern(self, pattern_data: Dict) -> PatternMemory:
        """Store a discovered pattern."""
        pattern = PatternMemory(
            id=pattern_data.get("id", f"PAT-{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            timestamp=datetime.now(),
            pattern_name=pattern_data.get("name"),
            description=pattern_data.get("description"),
            conditions=pattern_data.get("conditions", {}),
            success_rate=pattern_data.get("success_rate", 0),
            sample_count=pattern_data.get("sample_count", 0),
            avg_pnl=pattern_data.get("avg_pnl", 0),
            avg_duration=pattern_data.get("avg_duration", 0),
            best_mode=pattern_data.get("best_mode"),
            best_timeframe=pattern_data.get("timeframe"),
            market_conditions=pattern_data.get("conditions", []),
            tags=pattern_data.get("tags", []),
            confidence=pattern_data.get("confidence", 0.5),
        )

        self.patterns.append(pattern)
        await self._save()
        return pattern

    async def store_rule(self, rule_data: Dict) -> RuleMemory:
        """Store a discovered rule."""
        rule = RuleMemory(
            id=rule_data.get("id", f"RUL-{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            timestamp=datetime.now(),
            rule_text=rule_data.get("rule"),
            category=rule_data.get("category", "general"),
            evidence_count=rule_data.get("evidence_count", 0),
            success_count=rule_data.get("success_count", 0),
            failure_count=rule_data.get("failure_count", 0),
            success_rate=rule_data.get("success_rate", 0),
            avg_pnl=rule_data.get("avg_pnl", 0),
            context=rule_data.get("context", {}),
            confidence=rule_data.get("confidence", 0.5),
            validated=rule_data.get("validated", False),
        )

        self.rules.append(rule)
        await self._save()
        return rule

    async def get_patterns_for_context(self, context: Dict) -> List[PatternMemory]:
        """Get relevant patterns for current context."""
        relevant = []

        for pattern in self.patterns:
            if self._matches_context(pattern, context):
                relevant.append(pattern)

        return sorted(relevant, key=lambda x: x.confidence, reverse=True)

    async def get_rules_for_context(self, context: Dict) -> List[RuleMemory]:
        """Get relevant rules for current context."""
        relevant = []

        for rule in self.rules:
            if self._matches_context_rule(rule, context):
                relevant.append(rule)

        return sorted(relevant, key=lambda x: x.confidence, reverse=True)

    def _matches_context(self, pattern: PatternMemory, context: Dict) -> bool:
        """Check if pattern matches current context."""
        conditions = pattern.conditions

        if "mode" in conditions:
            if conditions["mode"] != context.get("mode"):
                return False

        if "regime" in conditions:
            if conditions["regime"] != context.get("regime"):
                return False

        return True

    def _matches_context_rule(self, rule: RuleMemory, context: Dict) -> bool:
        """Check if rule matches current context."""
        rule_context = rule.context

        if "mode" in rule_context:
            if rule_context["mode"] != context.get("mode"):
                return False

        return True

    def _load(self):
        """Load from disk."""
        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                self.patterns = [PatternMemory(**p) for p in data.get("patterns", [])]
                self.rules = [RuleMemory(**r) for r in data.get("rules", [])]
        except:
            self.patterns = []
            self.rules = []

    async def _save(self):
        """Save to disk."""
        data = {
            "last_saved": datetime.now().isoformat(),
            "patterns": [asdict(p) for p in self.patterns],
            "rules": [asdict(r) for r in self.rules],
        }

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: open(self.storage_path, "w").write(
                json.dumps(data, indent=2, default=str)
            ),
        )


class WorkingMemory:
    """Working memory - current context window."""

    def __init__(self, max_items: int = 100):
        self.max_items = max_items
        self.items: List[Dict] = []
        self.current_context: Dict = {}
        self.recent_decisions: List[Dict] = []
        self.attention_focus: str = ""

    async def store(self, item: Dict, item_type: str):
        """Store item in working memory."""
        self.items.append(
            {"type": item_type, "data": item, "timestamp": datetime.now().isoformat()}
        )

        if len(self.items) > self.max_items:
            self.items = self.items[-self.max_items :]

    async def update_context(self, context: Dict):
        """Update current context."""
        self.current_context = {
            **self.current_context,
            **context,
            "updated_at": datetime.now().isoformat(),
        }

    async def store_decision(self, decision: Dict):
        """Store trading decision."""
        self.recent_decisions.append(
            {**decision, "timestamp": datetime.now().isoformat()}
        )

        if len(self.recent_decisions) > 20:
            self.recent_decisions = self.recent_decisions[-20:]

    async def get_recent_items(
        self, item_type: str = None, limit: int = 10
    ) -> List[Dict]:
        """Get recent items."""
        filtered = self.items
        if item_type:
            filtered = [i for i in filtered if i["type"] == item_type]

        return filtered[-limit:]

    async def get_context(self) -> Dict:
        """Get current context."""
        return self.current_context

    def clear(self):
        """Clear working memory."""
        self.items = []
        self.current_context = {}
        self.recent_decisions = []
        self.attention_focus = ""


class IBISMemory:
    """Unified memory system coordinating episodic, semantic, and working memory."""

    def __init__(self):
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.working = WorkingMemory()

    async def remember_trade(self, trade_data: Dict):
        """Store trade in episodic memory."""
        trade = await self.episodic.store_trade(trade_data)
        await self.working.store(trade_data, "trade")
        return trade

    async def store_reflection(self, trade_id: str, reflection: Dict):
        """Store trade reflection."""
        for trade in self.episodic.trades:
            if trade.id == trade_id:
                trade.reflection = reflection.get("analysis", "")
                trade.lessons = reflection.get("lessons", [])
                await self.episodic._save()
                break

    async def get_statistics(self) -> Dict:
        """Get overall memory statistics."""
        return {
            "episodic": await self.episodic.get_statistics(),
            "patterns_count": len(self.semantic.patterns),
            "rules_count": len(self.semantic.rules),
            "working_items": len(self.working.items),
        }


# Global memory instance
ibis_memory: Optional[IBISMemory] = None


def get_memory() -> IBISMemory:
    """Get or create global memory instance."""
    global ibis_memory

    if ibis_memory is None:
        ibis_memory = IBISMemory()

    return ibis_memory
