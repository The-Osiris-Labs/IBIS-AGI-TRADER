#!/usr/bin/env python3
"""
🎯 IBIS True Agent - Performance Monitor
=========================================
Monitors current agent performance and market intelligence
"""

import asyncio
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table

BASE = Path(__file__).resolve().parent.parent
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from ibis_true_agent import IBISAutonomousAgent


async def monitor_performance():
    console = Console()

    console.print("🎯 [bold blue]IBIS True Agent Performance Monitor[/bold blue]")
    console.print("=" * 80)

    try:
        agent = IBISAutonomousAgent()
        await agent.initialize()

        # Get current market intelligence
        if agent.market_intel:
            console.print()
            console.print("[bold green]📊 Current Market Intelligence:[/bold green]")
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Symbol", style="white")
            table.add_column("Score", style="yellow")
            table.add_column("Mode", style="blue")

            sorted_intel = sorted(
                agent.market_intel.items(), key=lambda x: x[1]["score"], reverse=True
            )[:10]

            for symbol, intel in sorted_intel:
                table.add_row(
                    symbol, f"{intel['score']:.1f}/100", intel.get("mode", "AGGRESSIVE")
                )

            console.print(table)

            # Calculate statistics
            scores = [
                intel["score"]
                for symbol, intel in agent.market_intel.items()
                if "score" in intel
            ]
            if scores:
                avg_score = sum(scores) / len(scores)
                console.print(
                    f"[cyan]Average Score:[/cyan] [bold]{avg_score:.1f}/100[/bold]"
                )
                console.print(
                    f"[cyan]Symbols Analyzed:[/cyan] [bold]{len(agent.market_intel)}[/bold]"
                )

        # Print position details
        if agent.state["positions"]:
            console.print()
            console.print("[bold green]💼 Current Positions:[/bold green]")
            pos_table = Table(show_header=True, header_style="bold cyan")
            pos_table.add_column("Symbol", style="white")
            pos_table.add_column("Mode", style="blue")
            pos_table.add_column("Quantity", style="yellow")
            pos_table.add_column("Price", style="green")

            for symbol, pos in agent.state["positions"].items():
                entry_price = (
                    pos.get("buy_price")
                    or pos.get("order_price")
                    or pos.get("current_price")
                    or 0.0
                )
                pos_table.add_row(
                    str(pos.get("symbol", symbol)),
                    str(pos.get("mode", "UNKNOWN")),
                    f"{float(pos.get('quantity', 0) or 0):.4f}",
                    f"${float(entry_price):.6f}",
                )

            console.print(pos_table)

        console.print()
        console.print("[bold green]✅ System is operating at full intelligence!")

    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}")
        import traceback

        console.print(traceback.format_exc())


if __name__ == "__main__":
    try:
        asyncio.run(monitor_performance())
    except KeyboardInterrupt:
        print("\n\n⚠️  Monitoring interrupted by user")
