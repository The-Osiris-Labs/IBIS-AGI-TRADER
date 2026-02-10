#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              🦅 IBIS AGI TRADING SYSTEM - COMPONENTS 🦅              ║
║                                                                      ║
║              UI Components for Trading Dashboard                        ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import sys
import time
import threading
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Callable, Any, List, Dict
from enum import Enum

from .colors import Colors
from .icons import IconSet

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.columns import Columns
    from rich.text import Text
    from rich.style import Style
    from rich.live import Live
    from rich.layout import Layout
    from rich.box import ROUNDED, HEAVY
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    from rich import print as rprint

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class Spinner:
    """Animated spinner for loading states."""

    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    RADAR_FRAMES = ["◐", "◓", "◑", "◒"]
    DOTS_FRAMES = ["⠁", "⠂", "⠄", "⠂"]
    BAR_FRAMES = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

    def __init__(self, message: str = "Loading...", speed: float = 0.1):
        self.message = message
        self.speed = speed
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def start(self):
        """Start spinner animation."""
        self.running = True
        self.thread = threading.Thread(target=self._animate)
        self.thread.start()

    def stop(self):
        """Stop spinner."""
        self.running = False
        if self.thread:
            self.thread.join()

    def _animate(self):
        idx = 0
        while self.running:
            sys.stdout.write(
                f"\r{Colors.CYAN}{self.FRAMES[idx]} {self.message}{Colors.RESET}"
            )
            sys.stdout.flush()
            time.sleep(self.speed)
            idx = (idx + 1) % len(self.FRAMES)
        sys.stdout.write(f"\r{' ' * (len(self.message) + 10)}\r")
        sys.stdout.flush()


class ProgressBar:
    """Custom progress bar with ETA."""

    def __init__(self, total: int, width: int = 40, prefix: str = ""):
        self.total = total
        self.width = width
        self.prefix = prefix
        self.current = 0
        self.start_time = time.time()

    def update(self, current: int, message: str = ""):
        """Update progress."""
        self.current = current
        elapsed = time.time() - self.start_time
        percent = current / self.total if self.total > 0 else 1.0
        filled = int(self.width * percent)
        bar = "█" * filled + "░" * (self.width - filled)

        eta = 0
        if current > 0:
            eta = (elapsed / current) * (self.total - current)

        status = (
            f"{Colors.GREEN}✓ Complete{Colors.RESET}"
            if percent >= 1.0
            else f"{Colors.YELLOW}⏳{Colors.RESET}"
        )

        sys.stdout.write(
            f"\r{self.prefix} │{bar}│ {current}/{self.total} "
            f"{Colors.CYAN}ETA:{Colors.RESET} {eta:.1f}s {status} {message}"
        )
        sys.stdout.flush()

    def finish(self, final_message: str = ""):
        """Finish progress bar."""
        self.update(self.total, final_message)
        sys.stdout.write("\n")
        sys.stdout.flush()


@dataclass
class TradeResult:
    symbol: str
    side: str
    entry_price: float
    exit_price: float
    size: float
    pnl_pct: float
    pnl_abs: float
    duration: float
    fees_entry: float = 0.0
    fees_exit: float = 0.0
    total_fees: float = 0.0
    confidence: float = 0.0
    entry_reason: str = ""
    exit_reason: str = ""
    timestamp: str = ""
    stop_loss: float = 0.0
    take_profit: float = 0.0
    confluences: Dict[str, float] = None


class ScanAnimator:
    """Animated scan effects."""

    SCAN_FRAMES = [
        "▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁",
        "██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒",
        "▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒",
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓",
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓",
    ]

    @staticmethod
    def animate_scan(duration: float = 2.0):
        """Show scanning animation."""
        start = time.time()
        idx = 0
        while time.time() - start < duration:
            frame = ScanAnimator.SCAN_FRAMES[idx % len(ScanAnimator.SCAN_FRAMES)]
            sys.stdout.write(f"\r{Colors.CYAN}{frame}{Colors.RESET}")
            sys.stdout.flush()
            time.sleep(0.2)
            idx += 1
        sys.stdout.write(f"\r{' ' * 40}\r")

    @staticmethod
    def radar(message: str = "Scanning...", duration: float = 1.0):
        """Show radar spinning animation."""
        start = time.time()
        idx = 0
        while time.time() - start < duration:
            frame = ScanAnimator.RADAR_FRAMES[idx % len(ScanAnimator.RADAR_FRAMES)]
            sys.stdout.write(f"\r{Colors.CYAN}{frame} {message}...{Colors.RESET}")
            sys.stdout.flush()
            time.sleep(0.1)
            idx += 1
        sys.stdout.write(f"\r{' ' * 30}\r")


class IBISDashboard:
    """Main dashboard for IBIS AGI Trading System."""

    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.start_time = datetime.now()
        self.stats = {
            "cycles": 0,
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "alerts": 0,
        }

    def clear_screen(self):
        """Clear terminal screen."""
        print("\033[2J\033[H", end="")

    def print_banner(self):
        """Print IBIS system banner."""
        banner = f"""
{Colors.BRIGHT_CYAN}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   {Colors.BRIGHT_WHITE}██╗{Colors.BRIGHT_CYAN}   {Colors.BRIGHT_WHITE}███╗  {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██╗{Colors.BRIGHT_CYAN}  {Colors.BRIGHT_WHITE}████╗ {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██████╗{Colors.BRIGHT_CYAN}  {Colors.BRIGHT_WHITE}██╗  ██╗{Colors.BRIGHT_CYAN}                                   ║
║   {Colors.BRIGHT_WHITE}██║{Colors.BRIGHT_CYAN}  {Colors.BRIGHT_WHITE}██╔══╝ {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██╔══██╗{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██╔═══╝ {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██║  ██║{Colors.BRIGHT_CYAN}                                   ║
║   {Colors.BRIGHT_WHITE}██║{Colors.BRIGHT_CYAN}  {Colors.BRIGHT_WHITE}████╗  {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}███████║{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██║  ███╗{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}███████╗{Colors.BRIGHT_CYAN}                                   ║
║   {Colors.BRIGHT_WHITE}██║{Colors.BRIGHT_CYAN}  {Colors.BRIGHT_WHITE}██╔══╝ {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██╔══██║{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██║   ██║{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██╔══██║{Colors.BRIGHT_CYAN}                                   ║
║   {Colors.BRIGHT_WHITE}██║{Colors.BRIGHT_CYAN}  {Colors.BRIGHT_WHITE}██║     {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██║  ██║{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}╚██████╔╝{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██║  ██║{Colors.BRIGHT_CYAN}                                   ║
║   {Colors.BRIGHT_WHITE}╚═╝{Colors.BRIGHT_CYAN}  {Colors.BRIGHT_WHITE}╚═╝     {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}╚═╝  ╚═╝{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE} ╚═════╝ {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}╚═╝  ╚═╝{Colors.BRIGHT_CYAN}                                   ║
║                                                                              ║
║   {Colors.BRIGHT_YELLOW}AUTONOMOUS GLOBAL INTELLIGENCE SYSTEM{Colors.BRIGHT_CYAN}                                   ║
║   {Colors.DIM}Version 5.5 - Ultra Enhanced{Colors.RESET}{Colors.BRIGHT_CYAN}                                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.RESET}"""
        print(banner)

    def print_header(self, title: str, subtitle: str = ""):
        """Print section header."""
        width = 80
        print(f"\n{Colors.BOLD}{Colors.BRIGHT_BLUE}{'═' * width}{Colors.RESET}")
        print(
            f"{Colors.BOLD}{Colors.BRIGHT_BLUE}║ {Colors.WHITE}{title:<76}{Colors.BRIGHT_BLUE}║{Colors.RESET}"
        )
        if subtitle:
            print(
                f"{Colors.BOLD}{Colors.BRIGHT_BLUE}║ {Colors.DIM}{subtitle:<76}{Colors.BRIGHT_BLUE}║{Colors.RESET}"
            )
        print(f"{Colors.BOLD}{Colors.BRIGHT_BLUE}{'═' * width}{Colors.RESET}\n")

    def print_status_box(self, status: str, message: str, icon: str = "ℹ️"):
        """Print status message in colored box."""
        colors_map = {
            "RUNNING": Colors.GREEN,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "INFO": Colors.CYAN,
            "COMPLETE": Colors.GREEN,
        }
        color = colors_map.get(status.upper(), Colors.WHITE)

        print(f"{color}┌{'─' * 50}┐{Colors.RESET}")
        print(f"{color}│ {icon} {status:<46}{color}│{Colors.RESET}")
        print(f"{color}│   {message:<46}{color}│{Colors.RESET}")
        print(f"{color}└{'─' * 50}┘{Colors.RESET}\n")

    def print_account_status(
        self,
        balance: float,
        position: Optional[str],
        pnl: float,
        pnl_pct: float,
        win_rate: float = 0,
        max_drawdown: float = 0,
    ):
        """Print account status in formatted box."""
        pnl_color = Colors.GREEN if pnl >= 0 else Colors.RED
        position_str = position if position else f"{Colors.DIM}None{Colors.RESET}"
        win_color = Colors.GREEN if win_rate >= 50 else Colors.YELLOW

        print(f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}┌{'─' * 50}┐{Colors.RESET}")
        print(
            f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}│ {Colors.WHITE}💰 ACCOUNT STATUS{Colors.BRIGHT_MAGENTA:^41}{Colors.WHITE}💰{Colors.BOLD}{Colors.BRIGHT_MAGENTA} ║{Colors.RESET}"
        )
        print(f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}├{'─' * 50}┤{Colors.RESET}")
        print(
            f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}│ {Colors.CYAN}Balance:{Colors.RESET} {Colors.BRIGHT_WHITE}${balance:.2f}{Colors.BRIGHT_MAGENTA:^35}{Colors.RESET}"
        )
        print(
            f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}│ {Colors.CYAN}Position:{Colors.RESET} {position_str}{Colors.BRIGHT_MAGENTA:^36}{Colors.RESET}"
        )
        print(
            f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}│ {Colors.CYAN}P&L:{Colors.RESET} {pnl_color}{pnl:+.2f} ({pnl_pct:+.2f}%){Colors.BRIGHT_MAGENTA:^30}{Colors.RESET}"
        )
        print(
            f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}│ {Colors.CYAN}Win Rate:{Colors.RESET} {win_color}{win_rate:.1f}%{Colors.BRIGHT_MAGENTA:^34}{Colors.RESET}"
        )
        print(
            f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}│ {Colors.CYAN}Max Drawdown:{Colors.RESET} {Colors.YELLOW}{max_drawdown:.2f}%{Colors.BRIGHT_MAGENTA:^30}{Colors.RESET}"
        )
        print(f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}└{'─' * 50}┘{Colors.RESET}\n")

    def print_market_regime(
        self,
        regime: str,
        trend: str,
        volatility: float,
        sentiment: str = "NEUTRAL",
    ):
        """Print market regime analysis."""
        regime_colors = {
            "HIGH_VOLATILITY": Colors.RED,
            "TRENDING": Colors.YELLOW,
            "LOW_VOLATILITY": Colors.GREEN,
            "UNKNOWN": Colors.DIM,
        }
        trend_icons = {
            "STRONG_BULLISH": f"{Colors.GREEN}🐂🚀",
            "BULLISH": f"{Colors.GREEN}🐂",
            "NEUTRAL": f"{Colors.YELLOW}─",
            "BEARISH": f"{Colors.RED}🐻",
            "STRONG_BEARISH": f"{Colors.RED}🐻☁️",
        }
        sentiment_colors = {
            "BULLISH": Colors.GREEN,
            "BEARISH": Colors.RED,
            "NEUTRAL": Colors.YELLOW,
        }

        regime_color = regime_colors.get(regime, Colors.WHITE)
        trend_icon = trend_icons.get(trend, "─")
        sentiment_color = sentiment_colors.get(sentiment, Colors.WHITE)

        print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}┌{'─' * 50}┐{Colors.RESET}")
        print(
            f"{Colors.BOLD}{Colors.BRIGHT_CYAN}│ {Colors.WHITE}👁️ MARKET REGIME{Colors.BRIGHT_CYAN:^42}{Colors.WHITE}👁️{Colors.BOLD}{Colors.BRIGHT_CYAN} ║{Colors.RESET}"
        )
        print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}├{'─' * 50}┤{Colors.RESET}")
        print(
            f"{Colors.BOLD}{Colors.BRIGHT_CYAN}│ {Colors.CYAN}Regime:{Colors.RESET} {regime_color}{regime}{Colors.BRIGHT_CYAN:^36}{Colors.RESET}"
        )
        print(
            f"{Colors.BOLD}{Colors.BRIGHT_CYAN}│ {Colors.CYAN}Trend:{Colors.RESET} {trend_icon} {trend}{Colors.BRIGHT_CYAN:^38}{Colors.RESET}"
        )
        print(
            f"{Colors.BOLD}{Colors.BRIGHT_CYAN}│ {Colors.CYAN}Volatility:{Colors.RESET} {volatility * 100:.2f}%{Colors.BRIGHT_CYAN:^35}{Colors.RESET}"
        )
        print(
            f"{Colors.BOLD}{Colors.BRIGHT_CYAN}│ {Colors.CYAN}Sentiment:{Colors.RESET} {sentiment_color}{sentiment}{Colors.BRIGHT_CYAN:^37}{Colors.RESET}"
        )
        print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}└{'─' * 50}┘{Colors.RESET}\n")

    def print_opportunities(self, opportunities: list, max_display: int = 10):
        """Print trading opportunities."""
        if not opportunities:
            print(f"{Colors.DIM}No opportunities found{Colors.RESET}\n")
            return

        print(f"{Colors.BOLD}{Colors.BRIGHT_GREEN}┌{'─' * 70}┐{Colors.RESET}")
        print(
            f"{Colors.BOLD}{Colors.BRIGHT_GREEN}│ {Colors.WHITE}🎯 TRADING OPPORTUNITIES ({len(opportunities)} found){Colors.BRIGHT_GREEN:^55}{Colors.WHITE}🎯{Colors.BOLD}{Colors.BRIGHT_GREEN} ║{Colors.RESET}"
        )
        print(f"{Colors.BOLD}{Colors.BRIGHT_GREEN}├{'─' * 70}┤{Colors.RESET}")
        print(
            f"{Colors.BOLD}{Colors.BRIGHT_GREEN}│ {Colors.DIM}#   Symbol      Score  Decision    Key Signals{Colors.BRIGHT_GREEN:^46}{Colors.DIM}│{Colors.RESET}"
        )
        print(f"{Colors.BOLD}{Colors.BRIGHT_GREEN}├{'─' * 70}┤{Colors.RESET}")

        for i, opp in enumerate(opportunities[:max_display], 1):
            score = opp.get("score", 0)
            decision = opp.get("decision", "")
            reasons = opp.get("reasons", [])[:3]

            score_color = (
                Colors.GREEN
                if score >= 0.75
                else Colors.YELLOW
                if score >= 0.65
                else Colors.RED
            )

            decision_colors = {
                "STRONG_BUY": Colors.GREEN,
                "BUY": Colors.GREEN,
                "WEAK_BUY": Colors.YELLOW,
                "HOLD": Colors.BLUE,
                "SKIP": Colors.DIM,
            }
            decision_color = decision_colors.get(decision, Colors.WHITE)

            decision_icons = {
                "STRONG_BUY": "🚀",
                "BUY": "🐂",
                "WEAK_BUY": "▲",
                "HOLD": "⏸",
                "SKIP": "❌",
            }
            decision_icon = decision_icons.get(decision, "─")

            reasons_str = (
                f"{Colors.DIM}• {Colors.RESET}".join(reasons)
                if reasons
                else f"{Colors.DIM}Analyzing...{Colors.RESET}"
            )

            print(
                f"{Colors.BOLD}{Colors.BRIGHT_GREEN}│ {Colors.WHITE}{i:2}. {Colors.CYAN}{opp.get('symbol', 'N/A'):<12} {score_color}{score:.0%}  "
                f"{decision_color}{decision_icon} {decision:<9} {Colors.DIM}• {Colors.RESET}{reasons_str[:30]}"
            )
            print(f"{Colors.BOLD}{Colors.BRIGHT_GREEN}│{Colors.RESET}")

        if len(opportunities) > max_display:
            print(
                f"{Colors.BOLD}{Colors.BRIGHT_GREEN}│ {Colors.DIM}... and {len(opportunities) - max_display} more opportunities{Colors.BRIGHT_GREEN:^56}{Colors.RESET}"
            )

        print(f"{Colors.BOLD}{Colors.BRIGHT_GREEN}└{'─' * 70}┘{Colors.RESET}\n")

    def print_execution_result(self, result: dict):
        """Print trade execution result."""
        symbol = result.get("symbol", "N/A")
        side = result.get("side", "")
        price = result.get("entry_price", 0)
        size = result.get("size", 0)
        confidence = result.get("confidence", 0)
        success = result.get("success", False)

        status_color = Colors.GREEN if success else Colors.RED
        status_icon = "✅" if success else "❌"
        status_text = "EXECUTED" if success else "REJECTED"

        print(f"\n{status_color}╔{'═' * 50}╗{Colors.RESET}")
        print(
            f"{status_color}║ ⚔️ TRADE {status_text} ⚔️{status_color:^33}{Colors.RESET}"
        )
        print(f"{status_color}╠{'═' * 50}╣{Colors.RESET}")
        print(
            f"{status_color}║ {Colors.CYAN}Symbol:{Colors.RESET} {Colors.BRIGHT_WHITE}{symbol:<40}{Colors.RESET}"
        )
        print(
            f"{status_color}║ {Colors.CYAN}Side:{Colors.RESET} {Colors.BRIGHT_WHITE}{side:<42}{Colors.RESET}"
        )
        print(
            f"{status_color}║ {Colors.CYAN}Price:{Colors.RESET} ${Colors.BRIGHT_WHITE}{price:<42.4f}{Colors.RESET}"
        )
        print(
            f"{status_color}║ {Colors.CYAN}Size:{Colors.RESET} {Colors.BRIGHT_WHITE}{size:<43}{Colors.RESET}"
        )
        print(
            f"{status_color}║ {Colors.CYAN}Confidence:{Colors.RESET} {Colors.BRIGHT_WHITE}{confidence:.0%}{Colors.BRIGHT_CYAN:^37}{Colors.RESET}"
        )
        print(f"{status_color}╚{'═' * 50}╝{Colors.RESET}\n")

    def print_scan_progress(
        self, phase: str, current: int, total: int, details: str = ""
    ):
        """Print scan progress."""
        percent = current / total if total > 0 else 1.0
        bar_width = 40
        filled = int(bar_width * percent)
        bar = "█" * filled + "░" * (bar_width - filled)

        print(
            f"\r{Colors.CYAN}⚙️ {phase}: [{bar}] {current}/{total} {Colors.DIM}{details}{Colors.RESET}",
            end="",
            flush=True,
        )

    def print_scan_complete(self, opportunities: int, duration: float, alerts: int = 0):
        """Print scan completion summary."""
        print(f"\n\n{Colors.GREEN}✅ SCAN COMPLETE{Colors.RESET}")
        print(f"{Colors.CYAN}Duration:{Colors.RESET} {duration:.2f}s")
        print(f"{Colors.CYAN}Opportunities:{Colors.RESET} {opportunities}")
        if alerts > 0:
            print(f"{Colors.YELLOW}🚨 High-confidence alerts:{Colors.RESET} {alerts}")

    def print_cycle_complete(self, cycle: int, duration: float, stats: dict = None):
        """Print cycle completion summary."""
        print(f"\n{Colors.BOLD}{Colors.BRIGHT_BLUE}─" * 60)
        print(
            f"{Colors.BOLD}{Colors.BRIGHT_BLUE}│ {Colors.WHITE}CYCLE #{cycle} COMPLETE{Colors.BRIGHT_BLUE:^46}│{Colors.RESET}"
        )
        print(f"{Colors.BOLD}{Colors.BRIGHT_BLUE}─" * 60)

        if stats:
            print(
                f"{Colors.BOLD}{Colors.BRIGHT_BLUE}│ {Colors.CYAN}Duration:{Colors.RESET} {duration:.1f}s"
            )
            print(
                f"{Colors.BOLD}{Colors.BRIGHT_BLUE}│ {Colors.CYAN}Opportunities:{Colors.RESET} {stats.get('opportunities', 0)}"
            )
            print(
                f"{Colors.BOLD}{Colors.BRIGHT_BLUE}│ {Colors.CYAN}Watched:{Colors.RESET} {stats.get('watched', 0)} symbols"
            )
            if stats.get("trades_executed"):
                print(
                    f"{Colors.BOLD}{Colors.BRIGHT_BLUE}│ {Colors.GREEN}Trades:{Colors.RESET} {stats['trades_executed']}"
                )
            if stats.get("alerts"):
                print(
                    f"{Colors.BOLD}{Colors.BRIGHT_BLUE}│ {Colors.YELLOW}Alerts:{Colors.RESET} {stats['alerts']}"
                )

        print(f"{Colors.BOLD}{Colors.BRIGHT_BLUE}─" * 60)

    def print_alert(self, symbol: str, message: str, urgency: str = "HIGH"):
        """Print alert message."""
        urgency_colors = {
            "HIGH": Colors.BRIGHT_RED,
            "MEDIUM": Colors.YELLOW,
            "LOW": Colors.CYAN,
        }
        urgency_icon = {
            "HIGH": "🚨",
            "MEDIUM": "⚠️",
            "LOW": "ℹ️",
        }
        color = urgency_colors.get(urgency, Colors.WHITE)
        icon = urgency_icon.get(urgency, "ℹ️")

        print(f"\n{color}{'─' * 60}{Colors.RESET}")
        print(f"{color}{icon} {urgency} PRIORITY ALERT {icon}{color:^45}{Colors.RESET}")
        print(f"{color}{'─' * 60}{Colors.RESET}")
        print(f"{color}{Colors.BRIGHT_WHITE}{symbol}{Colors.RESET}")
        print(f"{color}{Colors.CYAN}{message}{Colors.RESET}")
        print(f"{color}{'─' * 60}{Colors.RESET}\n")

    def print_learning_update(self, trades: int, win_rate: float, total_pnl: float):
        """Print learning engine update."""
        print(f"\n{Colors.BRIGHT_MAGENTA}🧠 LEARNING UPDATE{Colors.RESET}")
        print(f"{Colors.CYAN}Trades recorded:{Colors.RESET} {trades}")
        print(
            f"{Colors.CYAN}Win rate:{Colors.RESET} {Colors.GREEN if win_rate >= 50 else Colors.YELLOW}{win_rate:.1f}%{Colors.RESET}"
        )
        print(
            f"{Colors.CYAN}Total P&L:{Colors.RESET} {Colors.GREEN if total_pnl >= 0 else Colors.RED}{total_pnl:+.2f}%{Colors.RESET}"
        )

    def print_dashboard(self, data: dict):
        """Print complete dashboard view."""
        self.clear_screen()
        self.print_banner()

        account = data.get("account", {})
        market = data.get("market", {})
        opportunities = data.get("opportunities", [])
        stats = data.get("stats", {})

        self.print_account_status(
            balance=account.get("balance", 0),
            position=account.get("position"),
            pnl=account.get("pnl", 0),
            pnl_pct=account.get("pnl_pct", 0),
            win_rate=account.get("win_rate", 0),
            max_drawdown=account.get("max_drawdown", 0),
        )

        self.print_market_regime(
            regime=market.get("regime", "UNKNOWN"),
            trend=market.get("trend", "NEUTRAL"),
            volatility=market.get("volatility", 0),
            sentiment=market.get("sentiment", "NEUTRAL"),
        )

        self.print_opportunities(opportunities, max_display=5)

        print(
            f"{Colors.DIM}System uptime: {stats.get('uptime', '0:00:00')} | Cycle: {stats.get('cycle', 0)} | Status: {stats.get('status', 'IDLE')}{Colors.RESET}\n"
        )


def format_number(num: float, decimals: int = 2) -> str:
    """Format number with commas."""
    return f"{num:,.{decimals}f}"


def format_duration(seconds: float) -> str:
    """Format duration as human-readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds / 60:.1f}m"
    else:
        return f"{seconds / 3600:.1f}h"


def format_pnl(pnl: float) -> str:
    """Format P&L with color."""
    color = Colors.GREEN if pnl >= 0 else Colors.RED
    sign = "+" if pnl >= 0 else ""
    return f"{color}{sign}{pnl:.2f}%{Colors.RESET}"


def format_score(score: float) -> str:
    """Format score with color."""
    if score >= 0.75:
        return f"{Colors.GREEN}{score:.0%}{Colors.RESET}"
    elif score >= 0.65:
        return f"{Colors.YELLOW}{score:.0%}{Colors.RESET}"
    else:
        return f"{Colors.RED}{score:.0%}{Colors.RESET}"


def format_decision(decision: str) -> str:
    """Format decision with color and icon."""
    colors = {
        "STRONG_BUY": Colors.GREEN,
        "BUY": Colors.GREEN,
        "WEAK_BUY": Colors.YELLOW,
        "HOLD": Colors.BLUE,
        "SKIP": Colors.DIM,
    }
    icons = {
        "STRONG_BUY": "🚀",
        "BUY": "🐂",
        "WEAK_BUY": "▲",
        "HOLD": "⏸",
        "SKIP": "❌",
    }
    color = colors.get(decision, Colors.WHITE)
    icon = icons.get(decision, "─")
    return f"{color}{icon} {decision}{Colors.RESET}"


if __name__ == "__main__":
    dashboard = IBISDashboard()
    dashboard.print_banner()
    dashboard.print_help()
