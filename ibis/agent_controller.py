"""
Agent controller for IBIS and the unified engine.
Provides a programmable interface for AI agents to manage and inspect the system.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from ibis.orchestrator import IBIS
from ibis.telemetry import get_events, clear_events

from unified_trading_engine import UnifiedTradingEngine
from unified_config import get_config


def _to_dict(obj: Any) -> Any:
    if hasattr(obj, "__dict__"):
        result = {}
        for key, value in obj.__dict__.items():
            if key.startswith("_"):
                continue
            result[key] = _to_dict(value)
        return result
    if isinstance(obj, list):
        return [_to_dict(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _to_dict(v) for k, v in obj.items()}
    return obj


class AgentController:
    def __init__(self):
        self.engine = UnifiedTradingEngine()
        self.ibis = IBIS()
        self._engine_initialized = False
        self._ibis_initialized = False
        self._auto_task: Optional[asyncio.Task] = None

    async def init_engine(self) -> bool:
        if self._engine_initialized:
            return True
        ok = await self.engine.initialize()
        self._engine_initialized = ok
        return ok

    async def init_ibis(self) -> bool:
        if self._ibis_initialized:
            return True
        ok = await self.ibis.initialize()
        self._ibis_initialized = ok
        return ok

    async def status(self) -> Dict[str, Any]:
        engine_status = {
            "initialized": self._engine_initialized,
            "running": self.engine.running,
            "mode": self.engine.config.trading.mode,
            "balance": self.engine.balance,
            "assets": self.engine.assets,
            "positions": list(self.engine.positions.keys()),
            "trade_count": self.engine.trade_count,
            "wins": self.engine.wins,
            "losses": self.engine.losses,
            "pnl": self.engine.pnl,
        }

        ibis_status = None
        if self._ibis_initialized:
            ibis_status = await self.ibis.get_status()

        return {
            "engine": engine_status,
            "ibis": ibis_status,
            "config": _to_dict(get_config()),
        }

    async def analyze_engine(self, symbols: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        await self.init_engine()
        results = await self.engine.analyze_market(symbols)
        return [r.__dict__ for r in results]

    async def analyze_ibis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await self.init_ibis()
        return await self.ibis.analyze_market(**context)

    async def start_auto(self, interval: int = 60) -> str:
        await self.init_engine()
        if self._auto_task and not self._auto_task.done():
            return "auto_trading_already_running"
        self.engine.running = True
        self._auto_task = asyncio.create_task(self.engine.start_auto_trading(interval))
        return "auto_trading_started"

    async def stop_auto(self) -> str:
        self.engine.running = False
        if self._auto_task and not self._auto_task.done():
            self._auto_task.cancel()
        return "auto_trading_stopped"

    async def get_events(self, limit: int = 200, since_id: Optional[int] = None) -> List[Dict[str, Any]]:
        return await get_events(limit=limit, since_id=since_id)

    async def clear_events(self) -> None:
        await clear_events()

    async def memory_stats(self) -> Dict[str, Any]:
        await self.init_ibis()
        return await self.ibis.memory.get_statistics()

    async def recent_trades(self, limit: int = 50) -> List[Dict[str, Any]]:
        await self.init_ibis()
        trades = await self.ibis.memory.episodic.get_recent_trades(limit=limit)
        return [t.__dict__ for t in trades]

    async def hunt(self, limit: int = 20) -> List[Dict[str, Any]]:
        await self.init_engine()
        return await self.engine.hunt_opportunities(limit=limit)

    async def state_dump(self) -> Dict[str, Any]:
        await self.init_engine()
        engine_state = {
            "running": self.engine.running,
            "mode": self.engine.config.trading.mode,
            "balance": self.engine.balance,
            "assets": self.engine.assets,
            "positions": {k: v.__dict__ for k, v in self.engine.positions.items()},
            "open_orders": {k: v.__dict__ for k, v in self.engine.open_orders.items()},
            "order_history_count": len(self.engine.order_history),
            "trade_history_count": len(self.engine.trade_history),
            "recent_trades": [t.__dict__ for t in self.engine.trade_history[-20:]],
            "cache": self.engine.cache.snapshot() if self.engine.cache else {},
        }
        ibis_state = None
        if self._ibis_initialized:
            ibis_state = await self.ibis.get_status()
        return {
            "engine": engine_state,
            "ibis": ibis_state,
            "config": _to_dict(get_config()),
        }

    async def backtest_demo(self, symbol: str = "DEMO-USDT", days: int = 60) -> Dict[str, Any]:
        from ibis.backtest import BacktestEngine, BacktestConfig
        from ibis.backtest.backtester import CandleGenerator, ConfluenceStrategy

        candles = {
            symbol: CandleGenerator.generate_candles(symbol=symbol, days=days, volatility=0.02)
        }
        engine = BacktestEngine(BacktestConfig())
        result = await engine.run(ConfluenceStrategy(BacktestConfig()), candles)
        return result.__dict__

    async def optimize_demo(self, generations: int = 5, population: int = 10) -> Dict[str, Any]:
        from ibis.optimization import GeneticOptimizer, OptimizationConfig

        config = OptimizationConfig(population_size=population, generations=generations)
        optimizer = GeneticOptimizer(config)
        best, history = await optimizer.optimize()
        return {
            "best": best.genes if best else {},
            "fitness": best.fitness if best else 0.0,
            "history": history,
        }
