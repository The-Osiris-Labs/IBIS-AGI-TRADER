"""Learning phase: derive configuration suggestions from backtest results."""

from dataclasses import asdict
from typing import Dict


def suggest_config_adjustments(result) -> Dict:
    suggestions = {
        "min_score": None,
        "kelly_fraction": None,
        "notes": [],
    }

    if result.total_trades < 10:
        suggestions["notes"].append("Insufficient trades for strong learning signal")
        return suggestions

    if result.win_rate < 45:
        suggestions["min_score"] = "Increase min_score by +0.05"
        suggestions["notes"].append("Low win rate suggests tightening signal quality")
    elif result.win_rate > 60:
        suggestions["min_score"] = "Decrease min_score by -0.02"
        suggestions["notes"].append("High win rate allows slightly more trades")

    if result.max_drawdown > 15:
        suggestions["kelly_fraction"] = "Reduce kelly_fraction by -0.05"
        suggestions["notes"].append("High drawdown suggests reducing sizing")
    elif result.profit_factor > 1.8:
        suggestions["kelly_fraction"] = "Increase kelly_fraction by +0.03"
        suggestions["notes"].append("Strong profit factor may allow modest sizing increase")

    return suggestions
