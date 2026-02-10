#!/usr/bin/env python3
"""
IBIS TRUE AGENT - Real-Time Monitor (Enhanced)
Displays live status of the running IBIS agent with health monitoring.
"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, Tuple, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich import print as rprint
import time

console = Console()

STATE_FILE = (
    "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_true_state.json"
)
MEMORY_FILE = (
    "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_true_memory.json"
)
DB_FILE = "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_v8.db"
LOG_FILE = "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_true.log"


def load_json(filepath):
    """Load JSON file safely"""
    try:
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                return json.load(f)
    except Exception as e:
        console.print(f"[red]Error loading {filepath}: {e}[/red]")
    return {}


def load_db_positions():
    """Load positions from SQLite"""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM positions")
        return [dict(row) for row in cur.fetchall()]
    except:
        return []


def calculate_health_score(state: Dict) -> tuple:
    """Calculate portfolio health score"""
    score = 100
    issues = []
    recommendations = []

    positions = state.get("positions", {})
    daily = state.get("daily", {})

    pnl = daily.get("pnl", 0)
    trades = daily.get("trades", 0)
    wins = daily.get("wins", 0)
    losses = daily.get("losses", 0)

    if pnl < 0:
        score += int(pnl * 2)
        issues.append(f"Negative PnL: ${pnl:.2f}")

    if trades > 0:
        win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0
        if win_rate < 0.4:
            score -= 20
            issues.append(f"Low win rate: {win_rate:.0%}")

    if len(positions) > 15:
        recommendations.append("Reduce position count")

    if trades == 0 and pnl > 0:
        recommendations.append("No trades - check capital")

    score = max(0, min(100, score))
    return score, issues, recommendations


def get_recent_logs(lines: int = 10) -> list:
    """Get recent log entries"""
    try:
        with open(LOG_FILE) as f:
            return f.readlines()[-lines:]
    except:
        return []


def create_dashboard():
    """Create the monitoring dashboard"""

    state = load_json(STATE_FILE)
    memory = load_json(MEMORY_FILE)

    # Header
    header = Text()
    header.append("🦅 IBIS TRUE AUTONOMOUS AGENT - LIVE MONITOR\n", style="bold cyan")
    header.append(
        f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="dim"
    )

    # Agent Status
    agent_table = Table(
        title="Agent Status", show_header=True, header_style="bold magenta"
    )
    agent_table.add_column("Metric", style="cyan", width=25)
    agent_table.add_column("Value", style="green", width=50)

    daily = state.get("daily", {})

    health_score, issues, recommendations = calculate_health_score(state)

    health_style = (
        "green" if health_score >= 80 else "yellow" if health_score >= 50 else "red"
    )

    health_table = Table(
        title="Portfolio Health", show_header=True, header_style=f"bold {health_style}"
    )
    health_table.add_column("Metric", style="cyan", width=25)
    health_table.add_column("Value", style="green", width=50)
    health_table.add_row(
        "Health Score", f"[{health_style}]{health_score}/100[/{health_style}]"
    )

    if issues:
        health_table.add_row("Issues", "[red]" + " | ".join(issues) + "[/red]")
    else:
        health_table.add_row("Issues", "[green]No issues detected[/green]")

    if recommendations:
        health_table.add_row(
            "Recommendations", "[yellow]" + " | ".join(recommendations) + "[/yellow]"
        )
    else:
        health_table.add_row("Recommendations", "[green]Optimal configuration[/green]")

    agent_table.add_row("Market Regime", state.get("market_regime", "unknown"))
    agent_table.add_row("Agent Mode", state.get("agent_mode", "unknown"))
    agent_table.add_row("Date", daily.get("date", "N/A"))
    agent_table.add_row("Trades Today", str(daily.get("trades", 0)))
    agent_table.add_row("Wins", str(daily.get("wins", 0)))
    agent_table.add_row("Losses", str(daily.get("losses", 0)))
    agent_table.add_row(
        "Win Rate",
        f"{(daily.get('wins', 0) / max(daily.get('trades', 1), 1) * 100):.2f}%",
    )
    agent_table.add_row("PnL Today", f"${daily.get('pnl', 0):.4f}")
    agent_table.add_row("Start Balance", f"${daily.get('start_balance', 0):.2f}")
    agent_table.add_row("Total Cycles", str(memory.get("total_cycles", 0)))

    # Positions
    positions = state.get("positions", {})
    pos_table = Table(
        title=f"Open Positions ({len(positions)})",
        show_header=True,
        header_style="bold yellow",
    )
    pos_table.add_column("Symbol", style="cyan", width=10)
    pos_table.add_column("Qty", style="white", width=12)
    pos_table.add_column("Buy Price", style="white", width=12)
    pos_table.add_column("Current", style="white", width=12)
    pos_table.add_column("P&L %", style="white", width=10)
    pos_table.add_column("Mode", style="magenta", width=15)
    pos_table.add_column("Order ID", style="dim", width=20)

    for symbol, pos in positions.items():
        buy_price = pos.get("buy_price", 0)
        current_price = pos.get("current_price", buy_price)
        pnl_pct = (
            ((current_price - buy_price) / buy_price * 100) if buy_price > 0 else 0
        )

        pnl_style = "green" if pnl_pct > 0 else "red" if pnl_pct < 0 else "white"

        pos_table.add_row(
            pos.get("symbol", symbol),
            f"{pos.get('quantity', 0):.8f}",
            f"${buy_price:.8f}",
            f"${current_price:.8f}",
            f"[{pnl_style}]{pnl_pct:+.2f}%[/{pnl_style}]",
            pos.get("mode", "N/A"),
            pos.get("order_id", "N/A")[:20],
        )

    # Performance by Symbol
    perf_by_symbol = memory.get("performance_by_symbol", {})
    perf_table = Table(
        title="Historical Performance", show_header=True, header_style="bold green"
    )
    perf_table.add_column("Symbol/Type", style="cyan", width=20)
    perf_table.add_column("Trades", style="white", width=10)
    perf_table.add_column("Wins", style="green", width=10)
    perf_table.add_column("Losses", style="red", width=10)
    perf_table.add_column("Win Rate", style="yellow", width=12)
    perf_table.add_column("Total PnL", style="white", width=15)

    for symbol, perf in sorted(
        perf_by_symbol.items(), key=lambda x: x[1].get("pnl", 0), reverse=True
    )[:10]:
        trades = perf.get("trades", 0)
        wins = perf.get("wins", 0)
        losses = perf.get("losses", 0)
        win_rate = (wins / trades * 100) if trades > 0 else 0
        pnl = perf.get("pnl", 0)

        pnl_style = "green" if pnl > 0 else "red" if pnl < 0 else "white"

        perf_table.add_row(
            symbol,
            str(trades),
            str(wins),
            str(losses),
            f"{win_rate:.1f}%",
            f"[{pnl_style}]${pnl:.4f}[/{pnl_style}]",
        )

    # Recent Market Insights
    insights = memory.get("market_insights", [])
    if insights:
        latest_insight = insights[-1]
        insight_table = Table(
            title="Latest Market Insight", show_header=True, header_style="bold blue"
        )
        insight_table.add_column("Metric", style="cyan", width=30)
        insight_table.add_column("Value", style="white", width=45)

        insight_table.add_row("Time", latest_insight.get("time", "N/A"))
        insight_table.add_row("Cycle", str(latest_insight.get("cycle", 0)))
        insight_table.add_row("Regime", latest_insight.get("regime", "unknown"))
        insight_table.add_row("Avg Score", f"{latest_insight.get('avg_score', 0):.2f}")
        insight_table.add_row(
            "High Confidence Opps",
            str(latest_insight.get("high_confidence_opportunities", 0)),
        )
        insight_table.add_row(
            "Total Symbols Analyzed",
            str(latest_insight.get("total_symbols_analyzed", 0)),
        )
        insight_table.add_row(
            "Trades Today", str(latest_insight.get("trades_today", 0))
        )
        insight_table.add_row("PnL Today", f"${latest_insight.get('pnl_today', 0):.4f}")
    else:
        insight_table = Panel(
            "[yellow]No market insights available yet[/yellow]",
            title="Latest Market Insight",
        )

    # Learned Regimes
    learned_regimes = memory.get("learned_regimes", {})
    regime_table = Table(
        title="Learned Market Regimes", show_header=True, header_style="bold cyan"
    )
    regime_table.add_column("Regime", style="cyan", width=15)
    regime_table.add_column("Win Rate", style="green", width=15)
    regime_table.add_column("Total Trades", style="white", width=15)

    # Handle both dict-of-dicts and simple format
    for regime, data in learned_regimes.items():
        if isinstance(data, dict):
            winrate = data.get("winrate", 0) * 100 if data.get("winrate") else 0
            trades = data.get("trades", 0)
        else:
            winrate = 0
            trades = 0
        regime_table.add_row(regime, f"{winrate:.1f}%", str(trades))

    # Combine all tables
    console.clear()
    console.print(Panel(header, border_style="cyan"))
    console.print(agent_table)
    console.print()
    console.print(pos_table)
    console.print()
    console.print(perf_table)
    console.print()
    console.print(insight_table)
    console.print()
    console.print(regime_table)
    console.print()
    console.print("[dim]Press Ctrl+C to exit[/dim]")


if __name__ == "__main__":
    try:
        while True:
            create_dashboard()
            time.sleep(5)  # Update every 5 seconds
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitor stopped[/yellow]")
