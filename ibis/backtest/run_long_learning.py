#!/usr/bin/env python3
"""Run a longer synthetic backtest and write learning suggestions."""

from pathlib import Path
import json
import asyncio
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ibis.backtest.backtester import (
    BacktestConfig,
    BacktestEngine,
    CandleGenerator,
    ConfluenceStrategy,
)
from ibis.backtest.learning import suggest_config_adjustments


async def main():
    config = BacktestConfig(initial_balance=10000, fee_pct=0.001, slippage_pct=0.0005)
    engine = BacktestEngine(config)

    symbols = [
        "AAA-USDT",
        "BBB-USDT",
        "CCC-USDT",
        "DDD-USDT",
        "EEE-USDT",
    ]
    # 120-day run to keep runtime reasonable
    candles = {s: CandleGenerator.generate_candles(s, days=120, volatility=0.03) for s in symbols}

    strategy = ConfluenceStrategy(config)
    result = await engine.run(strategy, candles)

    suggestions = suggest_config_adjustments(result)

    out = {
        "result": {
            "total_return_pct": result.total_return_pct,
            "win_rate": result.win_rate,
            "profit_factor": result.profit_factor,
            "max_drawdown": result.max_drawdown,
            "total_trades": result.total_trades,
        },
        "suggestions": suggestions,
    }

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    out_path = data_dir / "learning_suggestions_long.json"
    out_path.write_text(json.dumps(out, indent=2))

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
