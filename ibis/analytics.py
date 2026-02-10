"""
IBIS Performance Analytics
Track and analyze trading performance
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from ibis.database.db import IbisDB


@dataclass
class PerformanceMetrics:
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    total_pnl: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0
    avg_trade_duration_hours: float = 0.0
    best_trade_pct: float = 0.0
    worst_trade_pct: float = 0.0
    consecutive_wins: int = 0
    consecutive_losses: int = 0


class PerformanceAnalytics:
    def __init__(self):
        self.db = IbisDB()

    def get_metrics(self, days: int = 30) -> PerformanceMetrics:
        cutoff = datetime.now() - timedelta(days=days)
        trades = self.db.get_trades(limit=1000)

        filtered_trades = [
            t
            for t in trades
            if t.get("timestamp") and t.get("timestamp", "") >= cutoff.isoformat()
        ]

        metrics = PerformanceMetrics()
        metrics.total_trades = len(filtered_trades)

        if not filtered_trades:
            return metrics

        wins = [t for t in filtered_trades if t.get("pnl", 0) > 0]
        losses = [t for t in filtered_trades if t.get("pnl", 0) <= 0]

        metrics.winning_trades = len(wins)
        metrics.losing_trades = len(losses)
        metrics.win_rate = (
            (len(wins) / len(filtered_trades)) * 100 if filtered_trades else 0
        )

        pnl_values = [t.get("pnl", 0) for t in filtered_trades]
        metrics.total_pnl = sum(pnl_values)

        win_pnls = [t.get("pnl", 0) for t in wins]
        loss_pnls = [t.get("pnl", 0) for t in losses]

        metrics.avg_win = sum(win_pnls) / len(win_pnls) if win_pnls else 0
        metrics.avg_loss = sum(loss_pnls) / len(loss_pnls) if loss_pnls else 0

        gross_profit = sum(win_pnls) if win_pnls else 0
        gross_loss = abs(sum(loss_pnls)) if loss_pnls else 0
        metrics.profit_factor = (
            gross_profit / gross_loss if gross_loss > 0 else float("inf")
        )

        pct_changes = []
        for t in filtered_trades:
            entry = t.get("entry_price", 0)
            exit = t.get("exit_price", 0)
            if entry > 0:
                pct = ((exit / entry) - 1) * 100
                pct_changes.append(pct)
                if pct > metrics.best_trade_pct:
                    metrics.best_trade_pct = pct
                if pct < metrics.worst_trade_pct:
                    metrics.worst_trade_pct = pct

        durations = []
        for t in filtered_trades:
            opened = t.get("opened_at", "")
            closed = t.get("closed_at", "")
            if opened and closed:
                try:
                    d1 = datetime.fromisoformat(opened.replace("Z", "+00:00"))
                    d2 = datetime.fromisoformat(closed.replace("Z", "+00:00"))
                    durations.append((d2 - d1).total_seconds() / 3600)
                except:
                    pass
        metrics.avg_trade_duration_hours = (
            sum(durations) / len(durations) if durations else 0
        )

        current_consec = 0
        max_consec_wins = 0
        max_consec_losses = 0
        for t in filtered_trades:
            if t.get("pnl", 0) > 0:
                current_consec += 1
                max_consec_wins = max(max_consec_wins, current_consec)
            else:
                current_consec = 0

        current_consec = 0
        for t in filtered_trades:
            if t.get("pnl", 0) <= 0:
                current_consec += 1
                max_consec_losses = max(max_consec_losses, current_consec)
            else:
                current_consec = 0

        metrics.consecutive_wins = max_consec_wins
        metrics.consecutive_losses = max_consec_losses

        return metrics

    def get_regime_performance(self) -> Dict[str, Dict]:
        trades = self.db.get_trades(limit=1000)
        regime_stats = {}

        for t in trades:
            regime = t.get("regime", "unknown")
            if regime == "unknown":
                continue

            if regime not in regime_stats:
                regime_stats[regime] = {"trades": 0, "wins": 0, "pnl": 0}

            regime_stats[regime]["trades"] += 1
            if t.get("pnl", 0) > 0:
                regime_stats[regime]["wins"] += 1
            regime_stats[regime]["pnl"] += t.get("pnl", 0)

        for regime, stats in regime_stats.items():
            stats["win_rate"] = (
                (stats["wins"] / stats["trades"]) * 100 if stats["trades"] > 0 else 0
            )

        return regime_stats

    def get_formatted_report(self, days: int = 30) -> str:
        metrics = self.get_metrics(days)

        lines = [
            f"📊 IBIS Performance Report ({days} days)",
            "=" * 40,
            f"Total Trades: {metrics.total_trades}",
            f"Win Rate: {metrics.win_rate:.1f}%",
            f"Total PnL: ${metrics.total_pnl:+.2f}",
            f"Profit Factor: {metrics.profit_factor:.2f}",
            "",
            f"Avg Win: ${metrics.avg_win:+.2f}",
            f"Avg Loss: ${metrics.avg_loss:+.2f}",
            f"Avg Duration: {metrics.avg_trade_duration_hours:.1f}h",
            "",
            f"Best Trade: {metrics.best_trade_pct:+.2f}%",
            f"Worst Trade: {metrics.worst_trade_pct:+.2f}%",
            "",
            f"Max Consec Wins: {metrics.consecutive_wins}",
            f"Max Consec Losses: {metrics.consecutive_losses}",
        ]

        return "\n".join(lines)


def get_analytics() -> PerformanceAnalytics:
    return PerformanceAnalytics()
