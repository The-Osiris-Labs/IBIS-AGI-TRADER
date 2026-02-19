"""
IBIS AGI Orchestrator - Main Entry Point
By TheOsirisLabs.com | Founder: Youssef SalahEldin

Integrates brain, memory, and cognition systems for autonomous trading.
Uses local reasoning as fallback when LLM requires payment.
"""

import asyncio
import signal
import sys
from datetime import datetime
from typing import Dict, Optional, Any
from dataclasses import dataclass
from ibis.core.logging_config import get_logger

logger = get_logger(__name__)

# Try relative imports (package mode), fall back to absolute (standalone mode)
try:
    from .brain import get_brain, FreeLLMEngine, MarketContext
    from .brain.local_reasoning import get_local_reasoning, LocalReasoningEngine
    from .memory import get_memory, IBISMemory
    from .cognition import IBISCognition, CognitiveState, SelfAssessment
    from .telemetry import emit_event

    PACKAGE_MODE = True
except ImportError:
    from brain import get_brain, FreeLLMEngine, MarketContext
    from brain.local_reasoning import get_local_reasoning, LocalReasoningEngine
    from memory import get_memory, IBISMemory
    from cognition import IBISCognition, CognitiveState, SelfAssessment
    from telemetry import emit_event

    PACKAGE_MODE = False


@dataclass
class IBISConfig:
    """IBIS configuration."""

    name: str = "IBIS"
    version: str = "1.0.0"
    debug: bool = False
    auto_reflect: bool = True
    auto_adapt: bool = True
    reflection_threshold: float = 0.5
    adaptation_threshold: float = 0.4
    use_local_reasoning: bool = True


class IBIS:
    """
    IBIS - The AGI Trading Agent.

    Sacred bird of Thoth, hunter of opportunities.
    Uses both LLM and local reasoning for trading decisions.
    """

    def __init__(self, config: IBISConfig = None):
        self.config = config or IBISConfig()
        self.name = self.config.name
        self.version = self.config.version

        self.brain = get_brain()
        self.local_reasoning = get_local_reasoning()
        self.memory = get_memory()
        self.cognition = IBISCognition(self.brain, self.memory)

        self.running = False
        self.start_time: Optional[datetime] = None
        self.llm_available = False

        self.metrics = {
            "decisions": 0,
            "trades": 0,
            "reflections": 0,
            "adaptations": 0,
            "avg_confidence": 0.0,
            "total_pnl": 0.0,
            "local_decisions": 0,
            "llm_decisions": 0,
        }

    async def initialize(self) -> bool:
        """Initialize IBIS systems."""
        logger.info(f"Initializing {self.name} v{self.version}...")
        await emit_event(
            "ibis.initialize.start",
            {"name": self.name, "version": self.version},
        )

        try:
            await self.cognition.metacognition.set_cognitive_state(CognitiveState.OBSERVING)

            stats = await self.memory.get_statistics()
            logger.info(
                f"Memory loaded: {stats.get('episodic', {}).get('total_trades_stored', 0)} trades"
            )

            brain_metrics = self.brain.get_metrics()
            logger.info(f"Brain ready: {brain_metrics.get('total_requests', 0)} requests processed")

            logger.info(f"{self.name} initialized successfully")
            await emit_event(
                "ibis.initialize.ok",
                {"name": self.name, "version": self.version},
            )
            return True

        except Exception as e:
            logger.error(f"Initialization failed: {e}", exc_info=True)
            await emit_event(
                "ibis.initialize.error",
                {"error": str(e)},
            )
            return False

    async def analyze_market(
        self,
        symbol: str,
        price: float,
        price_change_pct: float,
        volume_24h: float,
        volatility_1h: float,
        volatility_24h: float,
        trend_strength: float,
        spread_avg: float,
        order_flow: str,
        recent_trades: list = None,
    ) -> Dict:
        """
        Analyze market and generate trading decision.
        Uses local reasoning when LLM unavailable.
        """
        await self.cognition.metacognition.set_cognitive_state(CognitiveState.ANALYZING)
        await emit_event(
            "ibis.analyze.input",
            {
                "symbol": symbol,
                "price": price,
                "price_change_pct": price_change_pct,
                "volume_24h": volume_24h,
                "volatility_1h": volatility_1h,
                "volatility_24h": volatility_24h,
                "trend_strength": trend_strength,
                "spread_avg": spread_avg,
                "order_flow": order_flow,
            },
        )

        try:
            context = MarketContext(
                symbol=symbol,
                price=price,
                price_change_pct=price_change_pct,
                volume_24h=volume_24h,
                volatility_1h=volatility_1h,
                volatility_24h=volatility_24h,
                trend_strength=trend_strength,
                spread_avg=spread_avg,
                order_flow=order_flow,
                recent_trades=recent_trades or [],
            )

            decision = await self.brain.analyze_market(context)
            self.metrics["llm_decisions"] += 1
            model_used = decision.model_used

        except Exception as e:
            local = self.local_reasoning.analyze_market(
                symbol=symbol,
                price=price,
                price_change_pct=price_change_pct,
                volatility_1h=volatility_1h,
                volatility_24h=volatility_24h,
                trend_strength=trend_strength,
                spread_avg=spread_avg,
                order_flow=order_flow,
                recent_trades=recent_trades,
            )
            decision = local
            model_used = "LOCAL_REASONING"
            self.metrics["local_decisions"] += 1

        await self.memory.working.update_context(
            {
                "symbol": symbol,
                "price": price,
                "regime": decision.regime,
                "action": decision.action,
            }
        )

        await self.cognition.metacognition.think(
            thought_type="decision",
            content=f"Decision: {decision.action} {symbol} @ ${price} (conf: {decision.confidence})",
            confidence=decision.confidence,
            conclusions=[f"Regime: {decision.regime}", f"Risk: {decision.risk_level}"],
        )

        self.metrics["decisions"] += 1
        await emit_event(
            "ibis.analyze.decision",
            {
                "symbol": symbol,
                "action": decision.action,
                "confidence": decision.confidence,
                "risk_level": decision.risk_level,
                "regime": decision.regime,
                "model_used": model_used,
            },
        )

        return {
            "action": decision.action,
            "confidence": decision.confidence,
            "reasoning": decision.reasoning,
            "risk_level": decision.risk_level,
            "regime": decision.regime,
            "time_horizon": getattr(decision, "time_horizon", "SHORT"),
            "size_pct": getattr(decision, "size_pct", 0.05),
            "model_used": model_used,
            "key_levels": getattr(decision, "key_levels", []),
            "alternatives": getattr(decision, "alternatives", []),
        }

    async def quick_decide(
        self,
        symbol: str,
        price: float,
        volatility: float,
        trend: float,
        order_flow: str,
    ) -> Dict:
        """Fast decision for time-sensitive scenarios."""
        await self.cognition.metacognition.set_cognitive_state(CognitiveState.ACTING)
        await emit_event(
            "ibis.quick_decide.input",
            {
                "symbol": symbol,
                "price": price,
                "volatility": volatility,
                "trend": trend,
                "order_flow": order_flow,
            },
        )

        try:
            context = MarketContext(
                symbol=symbol,
                price=price,
                price_change_pct=0,
                volume_24h=0,
                volatility_1h=volatility,
                volatility_24h=volatility,
                trend_strength=trend,
                spread_avg=0,
                order_flow=order_flow,
            )

            decision = await self.brain.quick_decision(context)
            self.metrics["llm_decisions"] += 1
            model_used = decision.model_used

        except Exception:
            local = self.local_reasoning.quick_decide(
                symbol=symbol,
                price=price,
                volatility=volatility,
                trend=trend,
                order_flow=order_flow,
            )
            decision = local
            model_used = "LOCAL"
            self.metrics["local_decisions"] += 1

        self.metrics["decisions"] += 1
        await emit_event(
            "ibis.quick_decide.decision",
            {
                "symbol": symbol,
                "action": decision.action,
                "confidence": decision.confidence,
                "regime": decision.regime,
                "risk_level": decision.risk_level,
                "model_used": model_used,
            },
        )

        return {
            "action": decision.action,
            "confidence": decision.confidence,
            "regime": decision.regime,
            "risk_level": decision.risk_level,
            "model_used": model_used,
        }

    async def record_trade(
        self,
        symbol: str,
        mode: str,
        side: str,
        entry_price: float,
        exit_price: float,
        pnl_pct: float,
        pnl_abs: float,
        duration: float,
        regime: str,
        volatility: float,
        trend_strength: float,
        spread: float,
        order_flow: str,
        confidence_entry: float = 0.5,
    ) -> Dict:
        """Record a completed trade for learning."""
        trade_data = {
            "id": f"TRD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "symbol": symbol,
            "mode": mode,
            "side": side,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "pnl_pct": pnl_pct,
            "pnl_abs": pnl_abs,
            "duration_seconds": duration,
            "regime_before": regime,
            "regime_during": regime,
            "regime_after": regime,
            "volatility": volatility,
            "trend_strength": trend_strength,
            "spread": spread,
            "order_flow": order_flow,
            "confidence_entry": confidence_entry,
            "confidence_exit": self._calculate_exit_confidence(pnl_pct),
        }

        await self.memory.remember_trade(trade_data)

        self.metrics["trades"] += 1
        self.metrics["total_pnl"] += pnl_abs
        await emit_event(
            "ibis.trade.recorded",
            {
                "symbol": symbol,
                "mode": mode,
                "side": side,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "pnl_pct": pnl_pct,
                "pnl_abs": pnl_abs,
                "duration": duration,
                "regime": regime,
                "confidence_entry": confidence_entry,
            },
        )

        await self.cognition.metacognition.think(
            thought_type="trade",
            content=f"Trade recorded: {side} {symbol} {pnl_pct:+.2f}%",
            confidence=self._calculate_exit_confidence(pnl_pct),
        )

        return {"status": "Trade recorded", "trade_id": trade_data["id"]}

    async def get_status(self) -> Dict:
        """Get current IBIS status."""
        uptime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0

        return {
            "name": self.name,
            "version": self.version,
            "running": self.running,
            "uptime_seconds": uptime,
            "cognitive_state": self.cognition.metacognition.cognitive_state.value,
            "metrics": self.metrics,
            "memory_stats": await self.memory.get_statistics(),
            "brain_metrics": self.brain.get_metrics(),
            "active_overrides": self.cognition.adaptation.get_overrides(),
        }

    async def start(self):
        """Start IBIS."""
        self.running = True
        self.start_time = datetime.now()

        await self.cognition.metacognition.set_cognitive_state(CognitiveState.OBSERVING)

        logger.info(f"{self.name} v{self.version} started - Sacred hunter awakens")
        await emit_event(
            "ibis.start",
            {"name": self.name, "version": self.version},
        )

    async def stop(self):
        """Stop IBIS."""
        self.running = False

        await self.cognition.metacognition.set_cognitive_state(CognitiveState.REFLECTING)

        await self.memory.episodic._save()

        logger.info(f"{self.name} stopped - Sacred hunter rests")
        await emit_event(
            "ibis.stop",
            {"name": self.name, "version": self.version},
        )
        # Cleanup sessions
        from .market_intelligence import market_intelligence

        await market_intelligence.close()
        # Closing kucoin client if accessible
        try:
            from .exchange.kucoin_client import get_kucoin_client

            await get_kucoin_client().close()
        except:
            pass

    def _calculate_exit_confidence(self, pnl_pct: float) -> float:
        """Calculate confidence based on outcome."""
        if pnl_pct > 1.0:
            return 0.9
        elif pnl_pct > 0.2:
            return 0.7
        elif pnl_pct > 0:
            return 0.6
        elif pnl_pct > -0.2:
            return 0.4
        else:
            return 0.2


async def main():
    """Main entry point for IBIS."""
    ibis = IBIS()

    if not await ibis.initialize():
        logger.error("Failed to initialize IBIS")
        sys.exit(1)

    await ibis.start()

    print("\nIBIS AGI Trading Agent is now operational.")
    print("Use ibis.analyze_market() for market analysis.")
    print("Use ibis.record_trade() to log trades.")
    print("Use ibis.self_assess() for self-assessment.")

    return ibis


if __name__ == "__main__":
    asyncio.run(main())
