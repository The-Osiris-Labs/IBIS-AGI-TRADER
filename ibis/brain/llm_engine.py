"""
IBIS LLM Engine - Free Model Integration
By TheOsirisLabs.com | Founder: Youssef SalahEldin

Uses only FREE models via kilo CLI:
- minimax/minimax-m2.1:free (primary - fast reasoning)
- arcee-ai/trinity-large-preview:free (secondary - high capacity)
- google/gemini-2.0-flash-lite-001 (fast inference)
- corethink:free (specialized reasoning)
"""

import asyncio
import json
import subprocess
import shlex
from datetime import datetime
from typing import Dict, List, Optional, Any, Generator
from dataclasses import dataclass, field
from enum import Enum


class ModelTier(Enum):
    """Model tiers for different use cases."""

    REASONING = "reasoning"  # Complex analysis
    FAST = "fast"  # Quick decisions
    CREATIVE = "creative"  # Strategy exploration
    SUMMARY = "summary"  # Trade reflection


@dataclass
class FreeModels:
    """Available free models configuration."""

    REASONING = "minimax/minimax-m2.1:free"
    FAST = "google/gemini-2.0-flash-lite-001"
    CREATIVE = "arcee-ai/trinity-large-preview:free"
    SUMMARY = "corethink:free"


@dataclass
class LLMResponse:
    """Response from LLM."""

    content: str
    model: str
    tokens_used: int = 0
    latency_ms: float = 0.0
    confidence: float = 0.0
    cost_usd: float = 0.0  # Always $0 for free models
    timestamp: datetime = field(default_factory=datetime.now)
    raw_output: Optional[str] = None


@dataclass
class MarketContext:
    """Market data for LLM analysis."""

    symbol: str = ""
    price: float = 0.0
    price_change_24h: float = 0.0
    volume_24h: float = 0.0
    volatility_1h: float = 2.5
    volatility_24h: float = 3.0
    trend_strength: float = 50
    spread_avg: float = 0.05
    order_flow: str = "neutral"
    recent_trades: List[Dict] = field(default_factory=list)
    order_book_imbalance: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TradingDecision:
    """Structured trading decision from LLM."""

    action: str
    confidence: float
    reasoning: str
    risk_level: str
    regime: str
    time_horizon: str
    size_pct: float = 0.05
    key_levels: List[float] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)
    model_used: str = ""


class FreeLLMEngine:
    """
    Free LLM engine using kilo CLI with various free models.
    """

    def __init__(self):
        self.model_config = FreeModels()
        self.response_cache: Dict[str, Dict] = {}
        self.cache_ttl = 300  # 5 minutes

        self.metrics = {
            "total_requests": 0,
            "total_latency_ms": 0.0,
            "model_usage": {},
            "cache_hits": 0,
        }

    async def complete(
        self,
        prompt: str,
        model: str = None,
        tier: ModelTier = ModelTier.REASONING,
        timeout: int = 60,
    ) -> LLMResponse:
        """
        Execute LLM completion using free model.

        Args:
            prompt: The prompt to send
            model: Specific model to use (optional)
            tier: Use predefined tier
            timeout: Max seconds to wait
        """
        model = model or self._get_model_for_tier(tier)

        # Check cache
        cache_key = f"{model}:{hash(prompt) % 10000}"
        cached = self._get_cached(cache_key)
        if cached:
            self.metrics["cache_hits"] += 1
            return cached

        # Execute via kilo CLI
        start_time = datetime.now()

        try:
            cmd = f"kilo run --model {model} --prompt {shlex.quote(prompt)} --timeout {timeout}"

            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=timeout + 10
            )

            latency_ms = (datetime.now() - start_time).total_seconds() * 1000

            if result.returncode == 0:
                response = LLMResponse(
                    content=result.stdout.strip(),
                    model=model,
                    latency_ms=latency_ms,
                    confidence=self._estimate_confidence(result.stdout),
                    raw_output=result.stdout,
                )
            else:
                response = LLMResponse(
                    content=f"[Error] {result.stderr}",
                    model=model,
                    latency_ms=latency_ms,
                    confidence=0.0,
                )

        except subprocess.TimeoutExpired:
            response = LLMResponse(
                content="[Timeout] Request exceeded timeout",
                model=model,
                latency_ms=(datetime.now() - start_time).total_seconds() * 1000,
                confidence=0.0,
            )

        except Exception as e:
            response = LLMResponse(
                content=f"[Exception] {str(e)}",
                model=model,
                latency_ms=(datetime.now() - start_time).total_seconds() * 1000,
                confidence=0.0,
            )

        # Update metrics
        self._update_metrics(response, model)
        self._cache_response(cache_key, response)

        return response

    async def stream_complete(
        self, prompt: str, model: str = None, tier: ModelTier = ModelTier.REASONING
    ) -> Generator[str, None, None]:
        """Stream response from LLM (basic implementation)."""
        response = await self.complete(prompt, model, tier)
        yield response.content

    async def parallel_complete(
        self, prompts: List[Dict[str, str]], primary_model: str = None
    ) -> List[LLMResponse]:
        """
        Run multiple completions in parallel.
        Used for consensus analysis.
        """
        tasks = []
        for p in prompts:
            tier = ModelTier(p.get("tier", "reasoning"))
            tasks.append(self.complete(p["prompt"], p.get("model"), tier))

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to error responses
        results = []
        for i, r in enumerate(responses):
            if isinstance(r, Exception):
                results.append(
                    LLMResponse(
                        content=f"[Parallel Error] {str(r)}",
                        model=prompts[i].get("model", "unknown"),
                        confidence=0.0,
                    )
                )
            else:
                results.append(r)

        return results

    async def analyze_market(self, context: MarketContext) -> TradingDecision:
        """
        Main market analysis using Minimax (best for reasoning).
        """
        prompt = self._build_market_prompt(context)

        response = await self.complete(
            prompt, model=self.model_config.REASONING, tier=ModelTier.REASONING
        )

        return self._parse_decision(response)

    async def quick_decision(self, context: MarketContext) -> TradingDecision:
        """
        Fast decision using Gemini Flash Lite.
        For time-sensitive scenarios.
        """
        prompt = self._build_quick_prompt(context)

        response = await self.complete(
            prompt, model=self.model_config.FAST, tier=ModelTier.FAST, timeout=30
        )

        return self._parse_decision(response, fast=True)

    async def consensus_analysis(self, context: MarketContext) -> Dict:
        """
        Multi-model consensus for important decisions.
        Runs multiple models and synthesizes results.
        """
        prompts = [
            {
                "prompt": self._build_market_prompt(context),
                "model": self.model_config.REASONING,
                "tier": "reasoning",
            },
            {
                "prompt": self._build_quick_prompt(context),
                "model": self.model_config.FAST,
                "tier": "fast",
            },
            {
                "prompt": self._build_analysis_prompt(context),
                "model": self.model_config.CREATIVE,
                "tier": "creative",
            },
        ]

        responses = await self.parallel_complete(prompts)

        return {
            "responses": [r.content for r in responses],
            "avg_confidence": sum(r.confidence for r in responses) / len(responses),
            "models_used": [r.model for r in responses],
            "synthesis": self._synthesize_responses(responses),
        }

    async def reflect_on_trade(
        self, trade_result: Dict, context: MarketContext
    ) -> Dict:
        """
        Post-trade reflection using CoreThink.
        """
        prompt = self._build_reflection_prompt(trade_result, context)

        response = await self.complete(
            prompt, model=self.model_config.SUMMARY, tier=ModelTier.SUMMARY
        )

        return {
            "analysis": response.content,
            "lessons": self._extract_lessons(response.content),
            "adjustments": self._extract_adjustments(response.content),
            "model": response.model,
            "timestamp": response.timestamp.isoformat(),
        }

    async def generate_strategy(self, market_data: Dict) -> Dict:
        """
        Generate strategic insights using Trinity.
        """
        prompt = self._build_strategy_prompt(market_data)

        response = await self.complete(
            prompt, model=self.model_config.CREATIVE, tier=ModelTier.CREATIVE
        )

        return {
            "strategy": response.content,
            "model": response.model,
            "confidence": response.confidence,
        }

    def _get_model_for_tier(self, tier: ModelTier) -> str:
        """Get model for specific tier."""
        models = {
            ModelTier.REASONING: self.model_config.REASONING,
            ModelTier.FAST: self.model_config.FAST,
            ModelTier.CREATIVE: self.model_config.CREATIVE,
            ModelTier.SUMMARY: self.model_config.SUMMARY,
        }
        return models.get(tier, self.model_config.REASONING)

    def _build_market_prompt(self, ctx: MarketContext) -> str:
        """Build comprehensive market analysis prompt."""
        # Handle both MarketContext types with getattr
        symbol = getattr(ctx, "symbol", "")
        price = getattr(ctx, "price", 0)
        change = getattr(ctx, "price_change_24h", getattr(ctx, "price_change_pct", 0))
        volume = getattr(ctx, "volume_24h", 0)
        vol_1h = getattr(ctx, "volatility_1h", 2.5)
        vol_24h = getattr(ctx, "volatility_24h", 3.0)
        trend = getattr(ctx, "trend_strength", 50)
        spread = getattr(ctx, "spread_avg", 0.05)
        flow = getattr(ctx, "order_flow", getattr(ctx, "order_flow_delta", "neutral"))
        imbalance = getattr(ctx, "order_book_imbalance", 0)
        trades = getattr(ctx, "recent_trades", [])

        return f"""IBIS Market Analysis

SYMBOL: {symbol}
PRICE: ${price:,.4f}
24H CHANGE: {change:+.2f}%
VOLUME: ${volume:,.0f}

METRICS:
- 1H Volatility: {vol_1h:.2f}%
- 24H Volatility: {vol_24h:.2f}%
- Trend Strength: {trend:.1f}
- Spread: {spread:.4f}%
- Order Flow: {flow}
- Book Imbalance: {imbalance:+.2f}

RECENT: {trades[-3:] if trades else "None"}

Task: Analyze regime, recommend action, give confidence 0-100.

Output exactly:
REGIME: [SCALPER|MOMENTUM|VOLATILITY|IDLE]
ACTION: [BUY|SELL|HOLD]
CONFIDENCE: XX
RISK: [LOW|MEDIUM|HIGH]
REASONING: [2 sentences max]
"""

    def _build_quick_prompt(self, ctx: MarketContext) -> str:
        """Build quick decision prompt."""
        symbol = getattr(ctx, "symbol", "")
        price = getattr(ctx, "price", 0)
        vol = getattr(ctx, "volatility_1h", 2.5)
        trend = getattr(ctx, "trend_strength", 50)
        flow = getattr(ctx, "order_flow", getattr(ctx, "order_flow_delta", "neutral"))
        change = getattr(ctx, "price_change_24h", getattr(ctx, "price_change_pct", 0))

        return f"""IBIS QUICK: {symbol} @ ${price:,.2f}
Vol={vol:.1f}% Trend={trend:.0f} Flow={flow} Chg={change:+.1f}%
Regime? Action? Confidence?
Format: REGIME ACTION CONF% RISK
Example: MOMENTUM BUY 75 MEDIUM
"""

    def _build_analysis_prompt(self, ctx: MarketContext) -> str:
        """Build deep analysis prompt."""
        symbol = getattr(ctx, "symbol", "")
        change = getattr(ctx, "price_change_24h", getattr(ctx, "price_change_pct", 0))
        vol = getattr(ctx, "volatility_1h", 2.5)
        flow = getattr(ctx, "order_flow", getattr(ctx, "order_flow_delta", "neutral"))

        direction = "bullish" if change > 0 else "bearish"

        return f"""Deep analysis of {symbol}:

Price action suggests {direction} momentum.
Volatility at {vol:.1f}% with {flow} order flow.

Consider:
1. Market structure (higher highs/lower highs?)
2. Volume confirmation
3. Risk/reward setup
4. Best entry levels

Provide detailed analysis.
"""

    def _build_reflection_prompt(self, trade: Dict, ctx: MarketContext) -> str:
        """Build post-trade reflection prompt."""
        flow = getattr(ctx, "order_flow", getattr(ctx, "order_flow_delta", "neutral"))
        vol = getattr(ctx, "volatility_1h", 2.5)

        return f"""IBIS Trade Reflection

RESULT: {trade.get("symbol")} | {trade.get("side")} | ${trade.get("pnl_abs", 0):+.2f} ({trade.get("pnl_pct", 0):+.2f}%)
MODE: {trade.get("mode")}
DURATION: {trade.get("duration", "N/A")}

CONTEXT: {flow} regime, vol={vol:.1f}%

Analyze:
1. What worked?
2. What failed?
3. One specific improvement?
4. One lesson learned?
Keep under 100 words.
"""

    def _build_strategy_prompt(self, data: Dict) -> str:
        """Build strategy generation prompt."""
        return f"""IBIS Strategy Generation

Current performance: {json.dumps(data.get("performance", {}))}
Mode distribution: {json.dumps(data.get("mode_dist", {}))}

Generate:
1. Primary strategy focus
2. Backup approach
3. Key adjustment needed
4. One contrarian insight

Be specific and actionable.
"""

    def _parse_decision(
        self, response: LLMResponse, fast: bool = False
    ) -> TradingDecision:
        """Parse LLM response into trading decision."""
        content = response.content.lower()

        # Extract fields
        regime = "IDLE"
        action = "HOLD"
        confidence = response.confidence or 0.5
        risk = "MEDIUM"
        reasoning = response.content[:200]

        for word in ["scalper", "momentum", "volatility", "idle"]:
            if word in content:
                regime = word.upper()
                break

        if (
            "buy" in content
            and "hold" not in content
            and "hold" not in content[content.find("buy") - 5 : content.find("buy")]
        ):
            action = "BUY"
        elif "sell" in content:
            action = "SELL"

        if "low" in content and "confidence" not in content:
            risk = "LOW"
        elif "high" in content and "confidence" not in content:
            risk = "HIGH"

        # Extract confidence number
        import re

        conf_match = re.search(r"(\d{1,3})", content)
        if conf_match:
            confidence = int(conf_match.group(1)) / 100

        return TradingDecision(
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            risk_level=risk,
            regime=regime,
            time_horizon="SHORT" if fast else "MEDIUM",
            model_used=response.model,
        )

    def _synthesize_responses(self, responses: List[LLMResponse]) -> str:
        """Synthesize multiple model responses."""
        contents = [r.content for r in responses]

        common_themes = []
        for c in contents:
            if "buy" in c.lower():
                common_themes.append("Bullish consensus")
            if "sell" in c.lower():
                common_themes.append("Bearish consensus")

        return f"Models analyzed: {len(responses)}. " + "; ".join(common_themes)

    def _extract_lessons(self, content: str) -> List[str]:
        """Extract lessons from reflection."""
        lessons = []
        for line in content.split("\n"):
            if any(w in line.lower() for w in ["lesson", "learn", "improve", "fix"]):
                lessons.append(line.strip())

        return lessons[:3] if lessons else ["Review trade for insights"]

    def _extract_adjustments(self, content: str) -> List[str]:
        """Extract adjustments from reflection."""
        adjustments = []
        for line in content.split("\n"):
            if any(w in line.lower() for w in ["adjust", "change", "modify", "tweak"]):
                adjustments.append(line.strip())

        return adjustments[:3] if adjustments else ["No adjustments suggested"]

    def _estimate_confidence(self, content: str) -> float:
        """Estimate confidence from response characteristics."""
        if not content or len(content) < 10:
            return 0.3

        confident_words = [
            "clearly",
            "definitely",
            "certainly",
            "strong",
            "high confidence",
        ]
        uncertain_words = [
            "possibly",
            "might",
            "could",
            "uncertain",
            "maybe",
            "unclear",
        ]

        content_lower = content.lower()
        confidence = 0.5

        for w in confident_words:
            if w in content_lower:
                confidence += 0.05

        for w in uncertain_words:
            if w in content_lower:
                confidence -= 0.05

        return max(0.1, min(0.95, confidence))

    def _get_cached(self, key: str) -> Optional[LLMResponse]:
        """Get cached response if valid."""
        if key not in self.response_cache:
            return None

        cached = self.response_cache[key]
        age = (datetime.now() - cached["timestamp"]).total_seconds()

        if age < self.cache_ttl:
            return cached["response"]

        return None

    def _cache_response(self, key: str, response: LLMResponse):
        """Cache response."""
        self.response_cache[key] = {"response": response, "timestamp": datetime.now()}

    def _update_metrics(self, response: LLMResponse, model: str):
        """Update performance metrics."""
        self.metrics["total_requests"] += 1
        self.metrics["total_latency_ms"] += response.latency_ms
        self.metrics["model_usage"][model] = (
            self.metrics["model_usage"].get(model, 0) + 1
        )

    def get_metrics(self) -> Dict:
        """Get engine metrics."""
        return {
            **self.metrics,
            "avg_latency_ms": (
                self.metrics["total_latency_ms"]
                / max(1, self.metrics["total_requests"])
            ),
            "models_available": list(self.model_config.__dict__.values()),
        }


# Global instance
ibis_brain: Optional[FreeLLMEngine] = None


def get_brain() -> FreeLLMEngine:
    """Get or create global brain instance."""
    global ibis_brain

    if ibis_brain is None:
        ibis_brain = FreeLLMEngine()

    return ibis_brain
