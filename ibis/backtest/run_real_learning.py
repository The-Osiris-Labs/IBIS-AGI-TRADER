#!/usr/bin/env python3
"""Backtest using real KuCoin candles for a few symbols (spot only).

Note: Requires network access. Does not trade.
"""

from pathlib import Path
import json
import asyncio
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ibis.backtest.backtester import BacktestConfig, BacktestEngine, ConfluenceStrategy
from ibis.exchange import get_kucoin_client
from ibis.backtest.learning import suggest_config_adjustments


async def fetch_candles(client, symbol: str, tf: str = "1hour", days: int = 30):
    # KuCoin returns candles in reverse; use existing method
    candles = await client.get_candles(symbol, tf)
    # Trim to days*24 candles if hourly
    limit = days * 24 if tf == "1hour" else len(candles)
    candles = candles[-limit:]

    # Map to backtest format
    return [
        {
            "symbol": symbol,
            "timestamp": Path(__file__).stat().st_mtime,  # placeholder
            "open": c.open,
            "high": c.high,
            "low": c.low,
            "close": c.close,
            "volume": c.volume,
        }
        for c in candles
    ]


async def main():
    config = BacktestConfig(initial_balance=10000, fee_pct=0.001, slippage_pct=0.0005)
    engine = BacktestEngine(config)
    strategy = ConfluenceStrategy(config)

    client = get_kucoin_client(paper_trading=True)

    symbols = ["SOL-USDT", "ADA-USDT", "DOGE-USDT"]
    candles = {}
    for s in symbols:
        candles[s] = await fetch_candles(client, s, tf="1hour", days=30)

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
    out_path = data_dir / "learning_suggestions_real.json"
    out_path.write_text(json.dumps(out, indent=2))

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
