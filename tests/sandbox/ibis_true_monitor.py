#!/usr/bin/env python3
"""
🦅 IBIS TRUE MONITOR - Real-time "Logic Engine" Dashboard
"""
import json
import os
import time
import sys
from datetime import datetime
from typing import Dict, Any, List

try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    from rich.box import DOUBLE, ROUNDED
except ImportError:
    print("Rich library not found. Please install: pip install rich")
    sys.exit(1)

# Configuration
BASE_DIR = "/root/projects/Dont enter unless solicited/AGI Trader/data"
STATE_FILE = f"{BASE_DIR}/ibis_true_state.json"
MEMORY_FILE = f"{BASE_DIR}/ibis_true_memory.json"
LOG_FILE = f"{BASE_DIR}/ibis_true.log"
AGENT_SCRIPT = "ibis_true_agent.py"

console = Console()

def load_json(filepath: str) -> Dict[str, Any]:
    if not os.path.exists(filepath): return {}
    try:
        with open(filepath, 'r') as f: return json.load(f)
    except: return {}

def get_process_status() -> bool:
    try:
        return bool(os.popen(f"pgrep -f {AGENT_SCRIPT}").read().strip())
    except: return False

def tail_log(n: int = 15) -> List[str]:
    if not os.path.exists(LOG_FILE): return []
    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
            return [line.strip() for line in lines[-n:]]
    except: return []

def format_currency(value: float) -> str:
    if value < 1: return f"${value:.4f}"
    return f"${value:.2f}"

def make_header(running: bool, last_update: str) -> Panel:
    status_text = Text("ONLINE", style="bold green") if running else Text("OFFLINE", style="bold red")
    
    table = Table.grid(expand=True)
    table.add_column(justify="left")
    table.add_column(justify="center")
    table.add_column(justify="right")
    
    table.add_row(
        Text.assemble("🦅 IBIS TRUE AGENT ", ("v3.1", "dim")),
        Text.assemble("STATUS: ", status_text),
        Text.assemble("LAST SYNC: ", (last_update, "cyan"))
    )
    
    return Panel(table, style="white on black", border_style="bright_blue", box=DOUBLE)

def make_financial_panel(state: Dict) -> Panel:
    daily = state.get("daily", {})
    balance = state.get("usdt_balance", 0.0)
    total_assets = state.get("total_assets", 0.0)
    positions = state.get("positions", {})
    
    unrealized_pnl = 0.0
    invested_value = 0.0
    
    for sym, pos in positions.items():
        qty = pos.get("quantity", 0)
        entry = pos.get("buy_price", 0)
        curr = pos.get("current_price", entry)
        val = qty * curr
        invested_value += val
        unrealized_pnl += (val - (qty * entry))

    equity = total_assets if total_assets > 0 else (balance + invested_value)
    roi_pct = (unrealized_pnl / invested_value * 100) if invested_value > 0 else 0.0
    
    grid = Table.grid(expand=True)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="center", ratio=1)
    
    pnl_color = "green" if unrealized_pnl >= 0 else "red"
    roi_color = "green" if roi_pct >= 0 else "red"
    
    # Row 1: Headers
    grid.add_row(Text("EQUITY", style="dim"), Text("LIQUID CASH", style="dim"), Text("UNREALIZED", style="dim"))
    # Row 2: Values
    grid.add_row(
        Text(f"${equity:.2f}", style="bold white"), 
        Text(f"${balance:.2f}", style="bold cyan"), 
        Text(f"${unrealized_pnl:.2f} ({roi_pct:+.2f}%)", style=f"bold {pnl_color}")
    )
    
    return Panel(grid, title="Financial Overview", border_style="green", box=ROUNDED)

def make_intelligence_panel(state: Dict, memory: Dict) -> Panel:
    regime = state.get("market_regime", "UNKNOWN")
    mode = state.get("agent_mode", "IDLE")
    
    # Color logic
    r_color = {"TRENDING": "green", "VOLATILE": "red", "FLAT": "blue"}.get(regime, "yellow")
    m_color = "cyan"
    
    # Intelligence Stats
    perf = memory.get("performance_by_symbol", {})
    total_cycles = memory.get("total_cycles", 0)
    
    # Calculate best strategy based on raw PnL ($)
    strategies = []
    for k, v in perf.items():
        # Ensure we're using the raw PnL value which is in dollars
        pnl_val = v.get("pnl", 0.0)
        strategies.append((k, pnl_val, v.get("wins", 0), v.get("losses", 0)))
        
    best_strat = max(strategies, key=lambda x: x[1]) if strategies else ("None", 0, 0, 0)
    
    grid = Table.grid(expand=True)
    grid.add_column(justify="left", ratio=1)
    grid.add_column(justify="right", ratio=1)
    
    grid.add_row(Text("Current Regime:", style="dim"), Text(regime, style=f"bold {r_color}"))
    grid.add_row(Text("Agent Mode:", style="dim"), Text(mode, style=f"bold {m_color}"))
    grid.add_row(Text("Learning Cycles:", style="dim"), Text(str(total_cycles), style="white"))
    
    # Format: Strategy Name ($PnL)
    strat_name = best_strat[0]
    if len(strat_name) > 20:
        strat_name = strat_name[:18] + ".."
        
    grid.add_row(
        Text("Top Strategy:", style="dim"), 
        Text(f"{strat_name} (${best_strat[1]:.2f})", style="magenta")
    )

    return Panel(grid, title="Intelligence Engine", border_style="magenta", box=ROUNDED)

def make_positions_table(state: Dict) -> Panel:
    table = Table(expand=True, show_header=True, header_style="bold cyan", box=None)
    
    table.add_column("Sym", justify="left")
    table.add_column("Size", justify="right")
    table.add_column("Entry", justify="right")
    table.add_column("Current", justify="right")
    table.add_column("PnL %", justify="right")
    table.add_column("Value", justify="right")
    
    positions = state.get("positions", {})
    sorted_pos = sorted(
        positions.items(),
        key=lambda x: (x[1].get("current_price", x[1].get("buy_price", 0)) / x[1].get("buy_price", 1) - 1),
        reverse=True
    )
    
    for sym, pos in sorted_pos:
        qty = pos.get("quantity", 0)
        entry = pos.get("buy_price", 0)
        curr = pos.get("current_price", entry)
        if entry == 0: continue
            
        val = qty * curr
        pnl_pct = (curr - entry) / entry * 100
        color = "green" if pnl_pct >= 0 else "red"
        
        table.add_row(
            sym, f"{qty:.4f}", format_currency(entry), format_currency(curr),
            Text(f"{pnl_pct:+.2f}%", style=color), f"${val:.2f}"
        )
        
    return Panel(table, title=f"Active Positions ({len(positions)})", border_style="white", box=ROUNDED)

def make_log_panel() -> Panel:
    logs = tail_log(12)
    log_text = Text()
    
    for line in logs:
        # Basic highlighting
        style = "dim"
        if "ORDER" in line or "SUCCESS" in line: style = "bold green"
        elif "ERROR" in line or "🛑" in line: style = "bold red"
        elif "WARNING" in line: style = "yellow"
        elif "OPPORTUNITY" in line: style = "cyan"
        
        # Strip timestamp usually [2024-...]
        clean_line = line
        if len(line) > 20 and line[0] == "[":
            clean_line = line[21:]
            
        log_text.append(clean_line + "\n", style=style)
        
    return Panel(log_text, title="Live Agent Stream", border_style="blue", box=ROUNDED)

def generate_layout(state: Dict, memory: Dict, running: bool) -> Layout:
    layout = Layout()
    
    # Calculate time ago
    updated_str = state.get("updated", "")
    time_ago = "Never"
    if updated_str:
        try:
            dt = datetime.fromisoformat(updated_str)
            seconds = (datetime.now() - dt).total_seconds()
            time_ago = f"{int(seconds)}s ago" if seconds < 60 else f"{int(seconds/60)}m ago"
        except: pass

    # Layout Structure
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1)
    )
    
    layout["main"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=1)
    )
    
    layout["left"].split(
        Layout(name="financials", size=6),
        Layout(name="positions", ratio=1)
    )
    
    layout["right"].split(
        Layout(name="intelligence", size=6),
        Layout(name="logs", ratio=1)
    )
    
    # render
    layout["header"].update(make_header(running, time_ago))
    layout["financials"].update(make_financial_panel(state))
    layout["positions"].update(make_positions_table(state))
    layout["intelligence"].update(make_intelligence_panel(state, memory))
    layout["logs"].update(make_log_panel())
    
    return layout

def main():
    with Live(refresh_per_second=2, screen=True) as live:
        while True:
            try:
                state = load_json(STATE_FILE)
                memory = load_json(MEMORY_FILE)
                running = get_process_status()
                
                layout = generate_layout(state, memory, running)
                live.update(layout)
                time.sleep(0.5)
            except KeyboardInterrupt:
                break
            except Exception:
                time.sleep(1)

if __name__ == "__main__":
    main()
