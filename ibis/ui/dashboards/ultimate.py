#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              🦅 IBIS AGI TRADING SYSTEM - ULTIMATE DASHBOARD 🦅        ║
║                                                                      ║
║              Ultimate Visual Experience with ASCII Charts               ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import sys
import time
import math
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ..colors import Colors
from ..icons import IconSet


class ASCIIArt:
    """Beautiful ASCII art banners and graphics."""

    @staticmethod
    def ibis_banner():
        return f"""
{Colors.BRIGHT_CYAN}╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   {Colors.BRIGHT_WHITE}██╗{Colors.BRIGHT_CYAN}   {Colors.BRIGHT_WHITE}███╗  {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██╗{Colors.BRIGHT_CYAN}  {Colors.BRIGHT_WHITE}████╗ {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██████╗{Colors.BRIGHT_CYAN}  {Colors.BRIGHT_WHITE}██╗  ██╗{Colors.BRIGHT_CYAN}                                   ║
║   {Colors.BRIGHT_WHITE}██║{Colors.BRIGHT_CYAN}  {Colors.BRIGHT_WHITE}██╔══╝ {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██╔══██╗{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██╔═══╝ {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██║  ██║{Colors.BRIGHT_CYAN}                                   ║
║   {Colors.BRIGHT_WHITE}██║{Colors.BRIGHT_CYAN}  {Colors.BRIGHT_WHITE}████╗  {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}███████║{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██║  ███╗{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}███████╗{Colors.BRIGHT_CYAN}                                   ║
║   {Colors.BRIGHT_WHITE}██║{Colors.BRIGHT_CYAN}  {Colors.BRIGHT_WHITE}██╔══╝ {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██╔══██║{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██║   ██║{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██╔══██║{Colors.BRIGHT_CYAN}                                   ║
║   {Colors.BRIGHT_WHITE}██║{Colors.BRIGHT_CYAN}  {Colors.BRIGHT_WHITE}██║     {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██║  ██║{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}╚██████╔╝{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}██║  ██║{Colors.BRIGHT_CYAN}                                   ║
║   {Colors.BRIGHT_WHITE}╚═╝{Colors.BRIGHT_CYAN}  {Colors.BRIGHT_WHITE}╚═╝     {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}╚═╝  ╚═╝{Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE} ╚═════╝ {Colors.BRIGHT_CYAN}{Colors.BRIGHT_WHITE}╚═╝  ╚═╝{Colors.BRIGHT_CYAN}                                   ║
║                                                                              ║
║   {Colors.BRIGHT_YELLOW}AUTONOMOUS GLOBAL INTELLIGENCE SYSTEM{Colors.BRIGHT_CYAN}                                 ║
║   {Colors.DIM}Version 5.5 | 15-Factor Confluence | Kelly Criterion | Real-Time Learning{Colors.BRIGHT_CYAN}   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}"""

    @staticmethod
    def pulse_bar(percent: float, width: int = 20) -> str:
        filled = int(width * percent)
        empty = width - filled
        pulse = "█" * filled + "░" * empty
        if percent >= 0.8:
            color = Colors.GREEN
        elif percent >= 0.5:
            color = Colors.YELLOW
        else:
            color = Colors.RED
        return f"{color}{pulse}{Colors.RESET}"


class IBISUltimateDashboard:
    """The ultimate IBIS dashboard with maximum visual potential."""

    def __init__(self):
        self.session_start = datetime.now()
        self.stats = {
            "cycles": 0,
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "alerts": 0,
            "scans": 0,
        }

    def clear_screen(self):
        print("\033[2J\033[H", end="")

    def print_banner(self):
        print(ASCIIArt.ibis_banner())

    def print_header(self, title: str, subtitle: str = "", width: int = 80):
        print(f"\n{Colors.BOLD}{Colors.BRIGHT_BLUE}{'═' * width}{Colors.RESET}")
        print(
            f"{Colors.BOLD}{Colors.BRIGHT_BLUE}║ {Colors.WHITE}{title:<76}{Colors.BRIGHT_BLUE}║{Colors.RESET}"
        )
        if subtitle:
            print(
                f"{Colors.BOLD}{Colors.BRIGHT_BLUE}║ {Colors.DIM}{subtitle:<76}{Colors.BRIGHT_BLUE}║{Colors.RESET}"
            )
        print(f"{Colors.BOLD}{Colors.BRIGHT_BLUE}{'═' * width}{Colors.RESET}\n")

    def print_account_dashboard(
        self,
        balance: float,
        position: Optional[str],
        pnl: float,
        pnl_pct: float,
        win_rate: float,
        max_drawdown: float,
        learning_trades: int = 0,
    ):
        pnl_color = Colors.GREEN if pnl >= 0 else Colors.RED
        win_color = Colors.GREEN if win_rate >= 50 else Colors.YELLOW
        dd_color = Colors.GREEN if max_drawdown < 10 else Colors.YELLOW if max_drawdown < 20 else Colors.RED

        print(f"""
{Colors.BOLD}{Colors.BRIGHT_MAGENTA}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_MAGENTA}║ {Colors.WHITE}💰 ACCOUNT DASHBOARD {Colors.BRIGHT_MAGENTA:^66}{Colors.WHITE}💰{Colors.BOLD}{Colors.BRIGHT_MAGENTA} ║{Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_MAGENTA}╠══════════════════════════════════════════════════════════════════════════════╣{Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_MAGENTA}║ {Colors.CYAN}Balance:{Colors.RESET} {Colors.BRIGHT_WHITE}${balance:>10.2f}{Colors.BRIGHT_MAGENTA:^48}                       {Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_MAGENTA}║ {Colors.CYAN}Position:{Colors.RESET} {position if position else Colors.DIM + "None" + Colors.RESET:<54}{Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_MAGENTA}║ {Colors.CYAN}P&L:{Colors.RESET} {pnl_color}${pnl:>+10.2f} ({pnl_pct:+.2f}%){Colors.BRIGHT_MAGENTA:^38}                       {Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_MAGENTA}║ {Colors.CYAN}Win Rate:{Colors.RESET} {win_color}{win_rate:>5.1f}%{Colors.BRIGHT_MAGENTA:^50}                       {Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_MAGENTA}║ {Colors.CYAN}Max Drawdown:{Colors.RESET} {dd_color}{max_drawdown:>5.1f}%{Colors.BRIGHT_MAGENTA:^47}                       {Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_MAGENTA}║ {Colors.CYAN}Learning Data:{Colors.RESET} {Colors.BRIGHT_CYAN}{learning_trades} trades{Colors.BRIGHT_MAGENTA:^45}                       {Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_MAGENTA}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}""")

    def print_market_regime_dashboard(
        self,
        regime: str,
        trend: str,
        volatility: float,
        sentiment: str,
        regime_history: List[str] = None,
    ):
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

        vol_bar = ASCIIArt.pulse_bar(volatility * 33, 20)

        print(f"""
{Colors.BOLD}{Colors.BRIGHT_CYAN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_CYAN}║ {Colors.WHITE}👁️ MARKET INTELLIGENCE {Colors.BRIGHT_CYAN:^66}{Colors.WHITE}👁️{Colors.BOLD}{Colors.BRIGHT_CYAN} ║{Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_CYAN}╠══════════════════════════════════════════════════════════════════════════════╣{Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_CYAN}║ {Colors.CYAN}Market Regime:{Colors.RESET} {regime_color}{regime:<20}{Colors.BRIGHT_CYAN:^38}                       {Colors.RES.BOLD}{Colors.BRIGHT_CYAN}║ {Colors.CYAN}Trend DirectionET}
{Colors:{Colors.RESET} {trend_icon} {trend:<18}{Colors.BRIGHT_CYAN:^35}                       {Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_CYAN}║ {Colors.CYAN}Volatility:{Colors.RESET} {volatility * 100:.2f}% {vol_bar}{Colors.BRIGHT_CYAN:^15}                       {Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_CYAN}║ {Colors.CYAN}Sentiment:{Colors.RESET} {sentiment_color}{sentiment:<20}{Colors.BRIGHT_CYAN:^38}                       {Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_CYAN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}""")

    def print_opportunities_matrix(self, opportunities: List[Dict], max_display: int = 10):
        if not opportunities:
            print(f"{Colors.DIM}ℹ️ No opportunities found{Colors.RESET}\n")
            return

        print(f"""
{Colors.BOLD}{Colors.BRIGHT_GREEN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_GREEN}║ {Colors.WHITE}🎯 TRADING OPPORTUNITIES {len(opportunities)} found {Colors.BRIGHT_GREEN:^51}{Colors.WHITE}🎯{Colors.BOLD}{Colors.BRIGHT_GREEN} ║{Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_GREEN}╠══════════════════════════════════════════════════════════════════════════════╣{Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_GREEN}║ {Colors.DIM}#   Symbol        Score    Decision      Key Signals         Tier{Colors.BRIGHT_GREEN:^18}{Colors.DIM}║{Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_GREEN}╠══════════════════════════════════════════════════════════════════════════════╣{Colors.RESET}""")

        for i, opp in enumerate(opportunities[:max_display], 1):
            score = opp.get("score", 0)
            decision = opp.get("decision", "")
            reasons = opp.get("reasons", [])[:2]

            score_color = Colors.GREEN if score >= 0.75 else Colors.YELLOW if score >= 0.65 else Colors.RED
            score_bar = ASCIIArt.pulse_bar(score, 10)

            decision_colors = {
                "STRONG_BUY": Colors.GREEN,
                "BUY": Colors.GREEN,
                "WEAK_BUY": Colors.YELLOW,
                "HOLD": Colors.BLUE,
                "SKIP": Colors.DIM,
            }
            decision_color = decision_colors.get(decision, Colors.WHITE)

            tier = opp.get("tier", 1)
            reasons_str = " • ".join(reasons) if reasons else f"{Colors.DIM}Analyzing...{Colors.RESET}"

            print(
                f"{Colors.BOLD}{Colors.BRIGHT_GREEN}║ {Colors.WHITE}{i:2}. {Colors.CYAN}{opp.get('symbol', 'N/A'):<14} "
                f"{score_color}{score_bar}{Colors.RESET} {score:.0%}  "
                f"{decision_color}{decision:<12} {Colors.DIM}•{Colors.RESET} {reasons_str[:25]} Tier-{tier}"
            )
            print(f"{Colors.BOLD}{Colors.BRIGHT_GREEN}║{Colors.RESET}")

        if len(opportunities) > max_display:
            print(
                f"{Colors.BOLD}{Colors.BRIGHT_GREEN}║ {Colors.DIM}... and {len(opportunities) - max_display} more opportunities{Colors.BRIGHT_GREEN:^56}{Colors.DIM}║{Colors.RESET}"
            )

        print(
            f"{Colors.BOLD}{Colors.BRIGHT_GREEN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}\n"
        )

    def print_confluence_factors(self, factors: Dict[str, float]):
        sorted_factors = sorted(factors.items(), key=lambda x: -x[1])

        print(f"""
{Colors.BOLD}{Colors.BRIGHT_YELLOW}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_YELLOW}║ {Colors.WHITE}🧠 15-FACTOR CONFLUENCE ANALYSIS {Colors.BRIGHT_YELLOW:^53}{Colors.WHITE}🧠{Colors.BOLD}{Colors.BRIGHT_YELLOW} ║{Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_YELLOW}╠══════════════════════════════════════════════════════════════════════════════╣{Colors.RESET}""")

        bullish_count = sum(1 for v in factors.values() if v >= 0.6)
        total = len(factors)

        for name, value in sorted_factors:
            bar = ASCIIArt.pulse_bar(value, 20)
            if value >= 0.6:
                status = f"{Colors.GREEN}🟢 BULLISH{Colors.RESET}"
            elif value >= 0.4:
                status = f"{Colors.YELLOW}🟡 NEUTRAL{Colors.RESET}"
            else:
                status = f"{Colors.RED}🔴 BEARISH{Colors.RESET}"

            name_formatted = name.replace("_", " ").title()[:20]
            print(
                f"{Colors.BOLD}{Colors.BRIGHT_YELLOW}║ {Colors.CYAN}{name_formatted:<22} {bar} {value:.0%} {status:<15}{Colors.BRIGHT_YELLOW}║{Colors.RESET}"
            )

        print(
            f"{Colors.BOLD}{Colors.BRIGHT_YELLOW}╠══════════════════════════════════════════════════════════════════════╣{Colors.RESET}"
        )
        overall = sum(factors.values()) / len(factors) if factors else 0
        overall_bar = ASCIIArt.pulse_bar(overall, 20)
        print(
            f"{Colors.BOLD}{Colors.BRIGHT_YELLOW}║ {Colors.WHITE}OVERALL SCORE: {overall_bar} {overall:.0%}{Colors.BRIGHT_YELLOW:^45}║{Colors.RESET}"
        )
        print(
            f"{Colors.BOLD}{Colors.BRIGHT_YELLOW}║ {Colors.CYAN}Bullish Factors: {bullish_count}/{total} ({bullish_count / total * 100:.0f}%){Colors.BRIGHT_YELLOW:^47}║{Colors.RESET}"
        )
        print(
            f"{Colors.BOLD}{Colors.BRIGHT_YELLOW}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}\n"
        )

    def print_risk_meter(self, risk_score: float):
        meter = ASCIIArt.pulse_bar(risk_score, 30)

        if risk_score >= 0.8:
            risk_level = f"{Colors.RED}🚨 HIGH RISK{Colors.RESET}"
        elif risk_score >= 0.5:
            risk_level = f"{Colors.YELLOW}⚡ MODERATE{Colors.RESET}"
        else:
            risk_level = f"{Colors.GREEN}🛡️ LOW RISK{Colors.RESET}"

        print(f"""
{Colors.BOLD}{Colors.BRIGHT_RED}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_RED}║ {Colors.WHITE}🛡️ RISK MANAGEMENT METER {Colors.BRIGHT_RED:^57}{Colors.WHITE}🛡️{Colors.BOLD}{Colors.BRIGHT_RED} ║{Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_RED}╠══════════════════════════════════════════════════════════════════════════════╣{Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_RED}║ Current Risk Level:{Colors.RESET} {risk_level}{Colors.BRIGHT_RED:^38}                       {Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_RED}║ Risk Score: {meter} {risk_score:.0%}{Colors.BRIGHT_RED:^18}                       {Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_RED}╠══════════════════════════════════════════════════════════════════════════════╣{Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_RED}║ {Colors.DIM}█ = Safe Zone    ▒ = Caution Zone    ▓ = Danger Zone    █ = Stop{Colors.BRIGHT_RED:^44}{Colors.DIM}║{Colors.RESET}
{Colors.BOLD}{Colors.BRIGHT_RED}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}""")

    def print_full_dashboard(self, data: Dict):
        self.clear_screen()
        self.print_banner()

        account = data.get("account", {})
        market = data.get("market", {})
        opportunities = data.get("opportunities", [])
        learning = data.get("learning", {})
        stats = data.get("stats", {})
        watchlist = data.get("watchlist", [])

        self.print_account_dashboard(
            balance=account.get("balance", 0),
            position=account.get("position"),
            pnl=account.get("pnl", 0),
            pnl_pct=account.get("pnl_pct", 0),
            win_rate=account.get("win_rate", 0),
            max_drawdown=account.get("max_drawdown", 0),
            learning_trades=learning.get("total_trades", 0),
        )

        self.print_market_regime_dashboard(
            regime=market.get("regime", "UNKNOWN"),
            trend=market.get("trend", "NEUTRAL"),
            volatility=market.get("volatility", 0),
            sentiment=market.get("sentiment", "NEUTRAL"),
        )

        if opportunities:
            self.print_opportunities_matrix(opportunities, max_display=5)

        if learning.get("factors"):
            self.print_confluence_factors(learning["factors"])

        if data.get("risk_score"):
            self.print_risk_meter(data["risk_score"])

        print(
            f"\n{Colors.DIM}System uptime: {datetime.now() - self.session_start} | "
            f"Cycles: {self.stats['cycles']} | "
            f"Scans: {self.stats['scans']} | "
            f"Alerts: {self.stats['alerts']}{Colors.RESET}\n"
        )


def demo_ultimate_dashboard():
    """Demonstrate the ultimate dashboard."""
    dashboard = IBISUltimateDashboard()

    demo_data = {
        "account": {
            "balance": 47.72,
            "position": None,
            "pnl": 0.0,
            "pnl_pct": 0.0,
            "win_rate": 0.0,
            "max_drawdown": 0.0,
        },
        "market": {
            "regime": "LOW_VOLATILITY",
            "trend": "BEARISH",
            "volatility": 0.0056,
            "sentiment": "NEUTRAL",
        },
        "opportunities": [
            {"symbol": "BTC-USDT", "score": 0.72, "decision": "STRONG_BUY", "reasons": ["Multi-timeframe bullish", "RSI oversold"], "tier": 2},
            {"symbol": "ETH-USDT", "score": 0.68, "decision": "BUY", "reasons": ["On-chain accumulation", "Volume spike"], "tier": 2},
            {"symbol": "SOL-USDT", "score": 0.65, "decision": "WEAK_BUY", "reasons": ["Pattern formation"], "tier": 1},
        ],
        "learning": {
            "total_trades": 5,
            "wins": 3,
            "losses": 2,
            "factors": {
                "performance_24h": 0.65,
                "mtf_bullish": 0.80,
                "rsi_oversold": 0.85,
                "volume_confirm": 0.70,
                "trend_aligned": 0.60,
                "structure": 0.55,
                "support_test": 0.75,
                "momentum": 0.65,
                "symbol_history": 0.50,
                "regime_quality": 0.45,
                "sentiment": 0.55,
                "onchain_accumulation": 0.70,
                "orderbook_buy_pressure": 0.60,
                "pattern_bullish": 0.65,
                "market_alignment": 0.55,
            },
        },
        "risk_score": 0.35,
    }

    dashboard.clear_screen()
    dashboard.print_full_dashboard(demo_data)


if __name__ == "__main__":
    demo_ultimate_dashboard()
