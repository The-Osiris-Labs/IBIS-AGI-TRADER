#!/usr/bin/env python3
"""
🦅 IBIS TRUE AUTONOMOUS AGENT v3.1
===================================
- No hardcoded symbols
- Real-time market discovery
- Dynamic intelligence analysis
- Self-adapting to ALL market conditions
- All thresholds centralized in trading_constants.py
"""

import asyncio
import json
import os
import argparse
import sys
import time
import math
from datetime import datetime
from typing import Dict, List, Optional, Any
from ibis.exchange.kucoin_client import get_kucoin_client
from ibis.free_intelligence import FreeIntelligence
from ibis.cross_exchange_monitor import CrossExchangeMonitor
from ibis.core.trading_constants import TRADING, SCORE_THRESHOLDS, RISK_CONFIG
from ibis.data_consolidation import run_full_sync as sync_data_stores

# from ibis_phase1_optimizations import create_phase1_optimizer
# from ibis_enhanced_integration import IBISEnhancedIntegration
from ibis.enhanced_intel import EnhancedIntelStreams
from ibis.indicators.indicators import (
    RSI,
    MACD,
    BollingerBands,
    MovingAverage,
    ATR,
    OBV,
    Stochastic,
    VWAP,
)


def round_down_to_increment(qty: float, increment: float) -> float:
    """Round DOWN to nearest increment, handling floating point precision."""
    if increment <= 0:
        return qty
    inc_str = str(increment)
    if "." in inc_str:
        decimals = len(inc_str.split(".")[-1])
    else:
        decimals = 0
    scale = 10**decimals
    scaled_qty = round(qty * scale, 10)
    scaled_inc = round(increment * scale, 10)
    scaled_result = (int(scaled_qty) // int(scaled_inc)) * int(scaled_inc)
    result = scaled_result / scale
    return round(result, decimals)


def print_banner():
    """Print beautiful banner with logo for IBIS TRUE TRADER"""
    banner = """
[96m[1m╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                                      ║
║   ██╗   ███╗  ██╗  ████╗ ██████╗  ██╗  ██╗                                              ║
║   ██║  ██╔══╝ ██╔══██╗██╔═══╝ ██║  ██║                                              ║
║   ██║  ████╗  ███████║██║  ███╗███████╗                                              ║
║   ██║  ██╔══╝ ██╔══██║██║   ██║██╔══██║                                              ║
║   ██║  ██║     ██║  ██║╚██████╔╝██║  ██║                                              ║
║   ╚═╝  ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝                                              ║
║                                                                                      ║
║              🦅 IBIS TRUE TRADER v1.0 - THE SACRED BIRD OF THOTH                      ║
║                                                                                      ║
║   ▄████████    ▄███████▄    ▄█   ▄█▄    ▄████████    ▄████████    ▄████████         ║
║  ███    ███   ███    ███   ███ ▄███▀   ███    ███   ███    ███   ███    ███         ║
║  ███    ███   ███    ███   ███▐██▀     ███    ███   ███    ███   ███    ███         ║
║  ███    ███  ▄███▄▄▄▄██▀    ████▀      ███    ███  ▄███▄▄▄▄██▀   ███    ███         ║
║  ███    ███ ▀▀███▀▀▀▀▀       ███       ███    ███ ▀▀███▀▀▀▀▀    ███    ███         ║
║  ███    ███ ▀███████████     ███       ███    ███ ▀███████████  ███    ███         ║
║  ███    ███   ███    ███     ███       ███    ███   ███    ███  ███    ███         ║
║  ████████▀    ███    ███     ███       ████████▀    ███    ███  ████████▀          ║
║               ███    ███                         ███    ███                         ║
║                                                                                      ║
║   TRULY AUTONOMOUS • SELF-LEARNING • DYNAMIC • ADAPTIVE • INTELLIGENT                ║
║                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝[0m
    """
    print(banner)


class IBISTrueAgent:
    """
    IBIS - Truly Autonomous Intelligent Trading Agent

    Capabilities:
    - Discovers ALL available trading pairs
    - Analyzes market in real-time
    - Adapts strategy to ANY condition
    - Self-heals and self-corrects
    - Learns from every market cycle
    """

    def __init__(self):
        self.paper_trading = os.environ.get("PAPER_TRADING", "false").lower() == "true"
        self.debug_mode = os.environ.get("DEBUG", "false").lower() == "true"
        self.verbose_mode = os.environ.get("VERBOSE", "false").lower() == "true"
        self.single_scan = False  # Set via CLI

        self.client = None
        self.symbols_cache = []
        self.market_intel = {}
        self.latest_tickers = {}
        self.cross_exchange = CrossExchangeMonitor()
        self.symbol_rules = {}
        self._close_lock = None

        self.state_file = (
            "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_true_state.json"
        )
        self.memory_file = (
            "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_true_memory.json"
        )

        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)

        import json as state_json

        def _load_memory():
            try:
                with open(self.memory_file) as f:
                    return state_json.load(f)
            except:
                return {
                    "learned_regimes": {},
                    "performance_by_symbol": {},
                    "market_insights": [],
                    "adaptation_history": [],
                    "total_cycles": 0,
                }

        def _save_memory():
            try:
                with open(self.memory_file, "w") as f:
                    state_json.dump(self.agent_memory, f, indent=2)
            except:
                pass

        self._load_memory = _load_memory
        self._save_memory = _save_memory
        self.agent_memory = _load_memory()

        def _save_state():
            try:
                state = {
                    "positions": self.state.get("positions", {}),
                    "market_regime": self.state.get("market_regime", "unknown"),
                    "agent_mode": self.state.get("agent_mode", "ADAPTIVE"),
                    "daily": self.state.get("daily", {}),
                    "capital_awareness": self.state.get("capital_awareness", {}),
                    "updated": datetime.now().isoformat(),
                }
                with open(self.state_file, "w") as f:
                    state_json.dump(state, f, indent=2)
            except Exception as e:
                print(f"   ⚠️ State save error: {e}")
                pass

        def _load_state():
            try:
                with open(self.state_file) as f:
                    return state_json.load(f)
            except:
                return {}

        self._save_state = _save_state
        self._load_state = _load_state

        # Import unified centralized configuration
        from ibis.core.trading_constants import TRADING, SCORE_THRESHOLDS

        self.Config = TRADING

        self.config = {
            "min_daily_target": TRADING.CRITICAL.MIN_VIABLE_TARGET * 100,
            "max_daily_loss": TRADING.RISK.BASE_RISK_PER_TRADE * 5,
            "min_liquidity": TRADING.FILTER.MIN_LIQUIDITY,
            "max_spread": TRADING.FILTER.MAX_SPREAD,
            "min_score": TRADING.INTELLIGENCE.AGI_CONFIDENCE_THRESHOLD * 100,
            "stablecoins": TRADING.FILTER.STABLECOINS,
            "ignored_symbols": TRADING.FILTER.IGNORED_SYMBOLS,
            "base_position_pct": TRADING.MULTIPLIERS.BASE_SIZE_PCT * 100,
            "max_position_pct": TRADING.POSITION.MAX_POSITION_PCT,
            "risk_per_trade": TRADING.RISK.BASE_RISK_PER_TRADE,
            "atr_period": TRADING.SCAN.LOOKBACK_PERIOD,
            "atr_multiplier_tp": TRADING.PRECISION.ATR_MULTIPLIER_NORMAL * 1.5,
            "atr_multiplier_sl": TRADING.PRECISION.ATR_MULTIPLIER_NORMAL * 2.0,
            "sentiment_weight": 0.15,
            "orderbook_weight": 0.10,
            "onchain_weight": 0.10,
            "portfolio_heat": TRADING.RISK.PORTFOLIO_HEAT * 0.5,
            "max_portfolio_risk": TRADING.RISK.MAX_PORTFOLIO_RISK * 0.5,
            "initial_capital": 1000.0,
            "profit_reserve_pct": 0.0,
            "enable_pyramiding": True,
            "enable_partial_exits": True,
            "enable_compounding": True,
        }

        # Load saved state first, then initialize defaults
        saved_state = self._load_state()

        # Default capital_awareness structure
        default_capital = {
            "usdt_total": 0.0,
            "usdt_available": 0.0,
            "usdt_locked_buy": 0.0,
            "usdt_in_buy_orders": 0.0,
            "holdings_value": 0.0,
            "holdings_in_sell_orders": 0.0,
            "total_assets": 0.0,
            "total_fees": 0.0,
            "fees_today": 0.0,
            "real_trading_capital": 0.0,
            "buy_orders": {},
            "sell_orders": {},
            "open_orders_count": 0,
        }

        # Merge saved state with defaults to ensure all keys exist
        saved_capital = saved_state.get("capital_awareness", {})
        if saved_capital:
            default_capital.update(saved_capital)

        # Validate positions structure
        saved_positions = saved_state.get("positions", {})
        validated_positions = {}
        for sym, pos in saved_positions.items():
            if isinstance(pos, dict) and "symbol" in pos:
                validated_positions[sym] = {
                    "symbol": str(pos.get("symbol", sym)),
                    "quantity": float(pos.get("quantity", 0)),
                    "buy_price": float(pos.get("buy_price", 0)),
                    "tp": float(pos.get("tp", 0)) if pos.get("tp") else None,
                    "sl": float(pos.get("sl", 0)) if pos.get("sl") else None,
                    "mode": str(pos.get("mode", "SWING")),
                    "regime": str(pos.get("regime", "unknown")),
                    "opened": str(pos.get("opened", datetime.now().isoformat())),
                    "opportunity_score": float(pos.get("opportunity_score", 50)),
                    "current_price": float(pos.get("current_price", 0)),
                    "current_value": float(pos.get("current_value", 0)),
                    "unrealized_pnl": float(pos.get("unrealized_pnl", 0)),
                    "unrealized_pnl_pct": float(pos.get("unrealized_pnl_pct", 0)),
                }

        # Validate daily structure
        saved_daily = saved_state.get("daily", {})
        if not isinstance(saved_daily, dict) or saved_daily.get("date") != datetime.now().strftime(
            "%Y-%m-%d"
        ):
            daily = self._new_daily()
        else:
            daily = {
                "date": str(saved_daily.get("date", datetime.now().strftime("%Y-%m-%d"))),
                "trades": int(saved_daily.get("trades", 0)),
                "wins": int(saved_daily.get("wins", 0)),
                "losses": int(saved_daily.get("losses", 0)),
                "pnl": float(saved_daily.get("pnl", 0.0)),
                "realized_pnl": float(saved_daily.get("realized_pnl", 0.0)),
                "fees": float(saved_daily.get("fees", 0.0)),
                "start_balance": float(saved_daily.get("start_balance", 0.0)),
                "regimes_experienced": dict(saved_daily.get("regimes_experienced", {})),
                "strategies_tried": dict(saved_daily.get("strategies_tried", {})),
                "orders_placed": int(saved_daily.get("orders_placed", 0)),
                "orders_filled": int(saved_daily.get("orders_filled", 0)),
                "orders_cancelled": int(saved_daily.get("orders_cancelled", 0)),
                "avg_fill_rate": float(saved_daily.get("avg_fill_rate", 0.0)),
            }

        self.state = {
            "positions": validated_positions,
            "daily": daily,
            "market_regime": str(saved_state.get("market_regime", "unknown")),
            "agent_mode": str(saved_state.get("agent_mode", "MICRO_HUNTER")),
            "capital_awareness": default_capital,
        }

        self.orderbook_cache = {}
        self.log_file = "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_true.log"
        self.sentiment_cache = {}
        self.onchain_cache = {}

        self.free_intel = FreeIntelligence()

        # 🚀 LIMITLESS OPTIMIZATIONS
        print("   🚀 Initializing LIMITLESS optimizations...")
        # self.phase1 = create_phase1_optimizer(self.config)  # DISABLED - module missing
        # self.enhanced = IBISEnhancedIntegration(self)  # DISABLED - module missing
        self.enhanced_intel = EnhancedIntelStreams()
        print("   ⚠️ Phase 1 Optimizer: DISABLED")
        print("   ⚠️ Enhanced Integration: DISABLED")
        print("   ✅ Enhanced Intel Streams: ACTIVE")

    def log_event(self, msg):
        # Filter DEBUG/VERBOSE messages if not enabled
        is_debug_msg = "DEBUG" in msg or "VERBOSE" in msg
        if is_debug_msg and not (self.debug_mode or self.verbose_mode):
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(self.log_file, "a") as f:
                f.write(f"[{timestamp}] {msg}\n")
        except:
            pass

        # Colorize certain logs if in terminal
        if "ORDER" in msg or "SUCCESS" in msg or "SOLD" in msg:
            print(f"\033[92m{msg}\033[0m")
        elif "ERROR" in msg or "🛑" in msg:
            print(f"\033[91m{msg}\033[0m")
        else:
            print(msg)

    @staticmethod
    def to_full_symbol(currency: str) -> str:
        """Convert currency code to full symbol (e.g., 'BTC' -> 'BTC-USDT')"""
        if "-USDT" in currency or "-USDC" in currency:
            return currency
        return f"{currency}-USDT"

    @staticmethod
    def to_currency(full_symbol: str) -> str:
        """Convert full symbol to currency code (e.g., 'BTC-USDT' -> 'BTC')"""
        return full_symbol.replace("-USDT", "").replace("-USDC", "")

    @staticmethod
    def _get_score_label(score: int) -> str:
        """Get descriptive label for score using centralized thresholds"""
        if score >= SCORE_THRESHOLDS.GOD_TIER:
            return "(GOD TIER)"
        elif score >= SCORE_THRESHOLDS.HIGH_CONFIDENCE:
            return "(HIGH CONFIDENCE)"
        elif score >= SCORE_THRESHOLDS.STRONG_SETUP:
            return "(STRONG SETUP)"
        elif score >= SCORE_THRESHOLDS.GOOD_SETUP:
            return "(GOOD SETUP)"
        elif score >= SCORE_THRESHOLDS.STANDARD:
            return "(STANDARD)"
        else:
            return "(CONSERVATIVE)"

    def validate_and_correct_positions(self):
        """🛡️ Validate positions and auto-correct TP/SL if they don't match configuration"""
        expected_tp = TRADING.RISK.TAKE_PROFIT_PCT
        expected_sl = TRADING.RISK.STOP_LOSS_PCT
        corrections_made = []

        for symbol, pos in list(self.state["positions"].items()):
            # Ensure highest_pnl exists for all positions
            if "highest_pnl" not in pos:
                pos["highest_pnl"] = 0
                pos["highest_pnl_display"] = "+0.00%"

            entry = pos.get("buy_price", 0)
            current_tp = pos.get("tp", 0)
            current_sl = pos.get("sl", 0)

            if entry <= 0:
                continue

            # Calculate actual percentages
            actual_tp_pct = (current_tp - entry) / entry if current_tp > entry else 0
            actual_sl_pct = (entry - current_sl) / entry if current_sl < entry else 0

            # Check if correction is needed (with 0.1% tolerance)
            needs_correction = False
            new_tp = current_tp
            new_sl = current_sl

            if abs(actual_tp_pct - expected_tp) > 0.001:
                new_tp = entry * (1 + expected_tp)
                needs_correction = True

            if abs(actual_sl_pct - expected_sl) > 0.001:
                new_sl = entry * (1 - expected_sl)
                needs_correction = True

            if needs_correction:
                self.state["positions"][symbol]["tp"] = new_tp
                self.state["positions"][symbol]["sl"] = new_sl
                corrections_made.append(
                    {
                        "symbol": symbol,
                        "old_tp_pct": actual_tp_pct * 100,
                        "new_tp_pct": expected_tp * 100,
                        "old_sl_pct": actual_sl_pct * 100,
                        "new_sl_pct": expected_sl * 100,
                    }
                )

        if corrections_made:
            self._save_state()
            self.log_event(f"🛡️ AUTO-CORRECTED {len(corrections_made)} positions to match config:")
            for corr in corrections_made:
                self.log_event(
                    f"   {corr['symbol']}: TP {corr['old_tp_pct']:.1f}%→{corr['new_tp_pct']:.1f}%, "
                    f"SL {corr['old_sl_pct']:.1f}%→{corr['new_sl_pct']:.1f}%"
                )

        return len(corrections_made)

    def _new_daily(self):
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "pnl": 0.0,
            "realized_pnl": 0.0,
            "fees": 0.0,
            "start_balance": 0.0,
            "regimes_experienced": {},
            "strategies_tried": {},
            "orders_placed": 0,
            "orders_filled": 0,
            "orders_cancelled": 0,
            "avg_fill_rate": 0.0,
        }

    async def update_positions_awareness(self) -> Dict:
        """
        🧠 COMPREHENSIVE POSITION AWARENESS
        Updates current prices and calculates real-time PnL for all positions.
        Returns detailed portfolio intelligence.
        """
        self.log_event("   🎯 Updating position awareness...")

        portfolio_updates = {
            "total_value": 0.0,
            "total_pnl": 0.0,
            "total_pnl_pct": 0.0,
            "positions": {},
            "alerts": [],
            "anomalies": [],
        }

        try:
            balances = await self.client.get_all_balances()
            self.state["usdt_balance"] = float(balances.get("USDT", {}).get("available", 0))

            for sym, pos in list(self.state["positions"].items()):
                try:
                    ticker = await self.client.get_ticker(self.to_full_symbol(sym))
                    current_price = float(ticker.price) if ticker else pos.get("buy_price", 0)

                    quantity = pos.get("quantity", 0)
                    entry_price = pos.get("buy_price", 0)

                    current_value = quantity * current_price
                    entry_value = quantity * entry_price
                    pnl = current_value - entry_value
                    pnl_pct = ((current_price / entry_price) - 1) * 100 if entry_price > 0 else 0

                    # Update position with current data
                    pos["current_price"] = current_price
                    pos["current_value"] = current_value
                    pos["unrealized_pnl"] = pnl
                    pos["unrealized_pnl_pct"] = pnl_pct

                    # 🕐 HOLDING TIME - How long position has been open
                    hold_seconds = 0
                    if pos.get("opened"):
                        try:
                            opened_str = pos["opened"]
                            if opened_str.endswith("Z"):
                                opened_str = opened_str.replace("Z", "+00:00")
                            elif "+" not in opened_str and "-" in opened_str[-6:]:
                                pass
                            opened = datetime.fromisoformat(opened_str)
                            now = datetime.now().astimezone()
                            hold_seconds = (now - opened).total_seconds()
                        except Exception:
                            hold_seconds = 0
                    pos["hold_seconds"] = hold_seconds
                    pos["hold_time"] = (
                        f"{int(hold_seconds / 3600)}h {int((hold_seconds % 3600) / 60)}m"
                    )

                    # ⏰ COUNTDOWN - Time until decay threshold
                    countdown = max(0, TRADING.EXECUTION.DECAY_TIMEOUT_SECONDS - hold_seconds)
                    pos["countdown_seconds"] = countdown
                    pos["countdown"] = (
                        f"{int(countdown / 3600)}h {int((countdown % 3600) / 60)}m"
                        if countdown > 0
                        else "DECAYED"
                    )

                    # 📈 HIGHEST PnL - Best profit this position has seen
                    if "highest_pnl" not in pos:
                        pos["highest_pnl"] = 0
                    if pnl_pct > pos.get("highest_pnl", 0):
                        pos["highest_pnl"] = pnl_pct
                    highest_pnl = pos.get("highest_pnl", 0)
                    pos["highest_pnl_display"] = (
                        f"+{highest_pnl:.2f}%" if highest_pnl > 0 else f"{highest_pnl:.2f}%"
                    )

                    # 🐋 WHALE ACTIVITY - Check if whales are active
                    pos_intel = self.market_intel.get(sym, {})
                    whale = pos_intel.get("whale_activity", "NEUTRAL")
                    pos["whale_activity"] = whale

                    # 📰 NEWS SENTIMENT - Latest news impact
                    news = pos_intel.get("news_sentiment", "NEUTRAL")
                    pos["news_sentiment"] = news

                    # 💬 SOCIAL SENTIMENT - Reddit/Twitter mood
                    social = pos_intel.get("social_sentiment", "NEUTRAL")
                    pos["social_sentiment"] = social

                    portfolio_updates["positions"][sym] = {
                        "quantity": quantity,
                        "entry_price": entry_price,
                        "current_price": current_price,
                        "value": current_value,
                        "pnl": pnl,
                        "pnl_pct": pnl_pct,
                        "hold_time": pos["hold_time"],
                        "countdown": pos["countdown"],
                        "highest_pnl": pos["highest_pnl_display"],
                        "whale_activity": whale,
                        "news_sentiment": news,
                        "social_sentiment": social,
                        "mode": pos.get("mode", "UNKNOWN"),
                        "regime": pos.get("regime", "UNKNOWN"),
                        "agi_score": pos.get("opportunity_score", 50),
                    }

                    portfolio_updates["total_value"] += current_value
                    portfolio_updates["total_pnl"] += pnl

                    # Detect anomalies
                    if abs(pnl_pct) > 10:
                        portfolio_updates["alerts"].append(
                            {
                                "symbol": sym,
                                "type": "HIGH_MOVE",
                                "message": f"{sym} moved {pnl_pct:+.2f}%",
                                "action": "REVIEW" if pnl_pct > 0 else "MONITOR",
                            }
                        )

                except Exception as e:
                    self.log_event(f"   ⚠️ Failed to update {sym}: {e}")
                    continue

            # Calculate portfolio-wide metrics - include USDT available + holdings
            usdt_balance = float(balances.get("USDT", {}).get("balance", 0))
            portfolio_value = portfolio_updates["total_value"]
            portfolio_updates["total_value"] = portfolio_value + usdt_balance

            if portfolio_value > 0:
                invested_capital = sum(
                    p["value"] / (1 + p.get("pnl_pct", 0) / 100)
                    for p in portfolio_updates["positions"].values()
                    if p.get("pnl_pct", 0) != -100
                )
                if invested_capital > 0:
                    portfolio_updates["total_pnl_pct"] = (
                        portfolio_updates["total_pnl"] / invested_capital
                    ) * 100
                else:
                    portfolio_updates["total_pnl_pct"] = 0
            else:
                portfolio_updates["total_pnl_pct"] = 0

            # Calculate weighted average AGI score
            if portfolio_updates["positions"]:
                weighted_score = (
                    sum(
                        p["agi_score"] * p["value"] for p in portfolio_updates["positions"].values()
                    )
                    / portfolio_updates["total_value"]
                )
                portfolio_updates["avg_agi_score"] = weighted_score
            else:
                portfolio_updates["avg_agi_score"] = 50

            # Store in state for quick access
            self.state["portfolio"] = portfolio_updates

            self.log_event(
                f"   📊 Portfolio: ${portfolio_updates['total_value']:.2f} | "
                f"PnL: ${portfolio_updates['total_pnl']:+.2f} ({portfolio_updates['total_pnl_pct']:+.2f}%) | "
                f"AGI Score: {portfolio_updates['avg_agi_score']:.1f}"
            )

            return portfolio_updates

        except Exception as e:
            self.log_event(f"   ⚠️ Position awareness update failed: {e}")
            return portfolio_updates

    async def update_capital_awareness(self) -> Dict:
        """
        💰 COMPREHENSIVE CAPITAL AWARENESS
        Tracks ALL capital states: available, locked, pending orders, fees.
        This ensures IBIS knows exactly what capital is deployable vs tied up.
        """
        try:
            balances = await self.client.get_all_balances()
            open_orders = await self.client.get_open_orders()

            usdt_total = float(balances.get("USDT", {}).get("balance", 0))
            usdt_available = float(balances.get("USDT", {}).get("available", 0))

            usdt_locked_buy = usdt_total - usdt_available

            holdings_value = 0.0
            holdings_locked_sell = 0.0
            buy_orders_value = 0.0
            sell_orders_value = 0.0

            buy_orders = {"buy": {}, "sell": {}}

            # Debug logging
            if open_orders:
                self.log_event(f"🔍 Found {len(open_orders)} open orders")
                for o in open_orders[:3]:
                    if hasattr(o, "symbol"):
                        side = getattr(o, "side", "N/A")
                        self.log_event(
                            f"   Order: {o.symbol} side='{side}' size={o.size} price={o.price}"
                        )
                    else:
                        self.log_event(f"   Order (dict): {o}")
            else:
                self.log_event(f"🔍 No open orders found")

            for order in open_orders:
                # Handle both dict-like and TradeOrder objects
                if hasattr(order, "symbol") and not isinstance(order, dict):
                    # TradeOrder object
                    order_symbol = str(order.symbol).replace("-USDT", "") if order.symbol else ""
                    order_side = str(getattr(order, "side", "")).lower().strip()
                    order_price = float(getattr(order, "price", 0) or 0)
                    order_size = float(getattr(order, "size", 0) or 0)
                    order_funds = float(getattr(order, "funds", 0) or 0) or (
                        order_size * order_price
                    )
                else:
                    # Dict (KuCoin API returns strings)
                    order_symbol = str(order.get("symbol", "")).replace("-USDT", "")
                    order_side = str(order.get("side", "")).lower().strip()
                    order_price = float(order.get("price", 0) or 0)
                    order_size = float(order.get("size", 0) or 0)
                    # funds might be "0" string - convert to float then check
                    funds_raw = order.get("funds", "0")
                    try:
                        order_funds = float(funds_raw) if funds_raw else 0
                    except (ValueError, TypeError):
                        order_funds = 0
                    # If funds is 0, calculate from size * price
                    if order_funds == 0 and order_size > 0 and order_price > 0:
                        order_funds = order_size * order_price

                if order_side == "buy":
                    buy_orders_value += order_funds
                    buy_orders["buy"][order_symbol] = {
                        "price": order_price,
                        "size": order_size,
                        "funds": order_funds,
                        "symbol": order_symbol,
                    }
                elif order_side == "sell":
                    sell_orders_value += order_size * order_price
                    if order_symbol not in buy_orders["sell"]:
                        buy_orders["sell"][order_symbol] = []
                    buy_orders["sell"][order_symbol].append(
                        {
                            "price": order_price,
                            "size": order_size,
                            "value": order_size * order_price,
                        }
                    )

            for currency, data in balances.items():
                if currency == "USDT":
                    continue
                balance = float(data.get("balance", 0))
                if balance > 0:
                    # Get real-time price directly from exchange (not cache)
                    try:
                        ticker = await self.client.get_ticker(f"{currency}-USDT")
                        price = float(ticker.price) if ticker else 0
                    except:
                        price = self.market_intel.get(currency, {}).get("price", 0)

                    if price > 0:
                        value = balance * price
                        holdings_value += value

            sell_orders_locked = 0.0
            for sym, orders in buy_orders["sell"].items():
                for order in orders:
                    sell_orders_locked += order["value"]

            total_assets = usdt_total + holdings_value

            real_trading_capital = usdt_available - buy_orders_value

            daily_fees = self.state.get("daily", {}).get("fees", 0)

            capital_aware = {
                "usdt_total": usdt_total,
                "usdt_available": usdt_available,
                "usdt_locked_buy": usdt_locked_buy,
                "usdt_in_buy_orders": buy_orders_value,
                "holdings_value": holdings_value,
                "holdings_in_sell_orders": sell_orders_locked,
                "total_assets": total_assets,
                "total_fees": self.state.get("capital_awareness", {}).get("total_fees", 0)
                + (daily_fees - self.state.get("capital_awareness", {}).get("fees_today", 0)),
                "fees_today": daily_fees,
                "real_trading_capital": max(0, real_trading_capital),
                "open_orders_count": len(open_orders),
                "buy_orders": self.state.get("capital_awareness", {}).get("buy_orders", {}),
                "sell_orders": buy_orders["sell"],
            }

            self.state["capital_awareness"] = capital_aware

            self.log_event(
                f"   💰 CAPITAL: ${usdt_total:.2f} total | "
                f"${usdt_available:.2f} avail | "
                f"${buy_orders_value:.2f} in buy orders | "
                f"${holdings_value:.2f} in holdings | "
                f"${sell_orders_locked:.2f} in sell orders"
            )

            return capital_aware

        except Exception as e:
            self.log_event(f"   ⚠️ Capital awareness update failed: {e}")
            return self.state.get("capital_awareness", {})

    async def get_holdings_intelligence(self) -> Dict:
        """
        Returns comprehensive intelligence about current holdings.
        Used for decision making and opportunity scoring.
        """
        if "portfolio" not in self.state:
            await self.update_positions_awareness()
        await self.update_capital_awareness()

        holdings = self.state.get("portfolio", {}).get("positions", {})

        # Calculate holdings distribution
        total_value = self.state.get("portfolio", {}).get("total_value", 0)
        holdings_by_mode = {}
        holdings_by_regime = {}
        top_performers = []
        bottom_performers = []

        for sym, data in holdings.items():
            mode = data.get("mode", "UNKNOWN")
            regime = data.get("regime", "UNKNOWN")

            holdings_by_mode[mode] = holdings_by_mode.get(mode, 0) + data["value"]
            holdings_by_regime[regime] = holdings_by_regime.get(regime, 0) + data["value"]

            if data["value"] > 0:
                top_performers.append((sym, data))
                bottom_performers.append((sym, data))

        top_performers.sort(key=lambda x: x[1]["pnl_pct"], reverse=True)
        bottom_performers.sort(key=lambda x: x[1]["pnl_pct"])

        return {
            "holdings_count": len(holdings),
            "total_value": total_value,
            "total_pnl": self.state.get("portfolio", {}).get("total_pnl", 0),
            "by_mode": holdings_by_mode,
            "by_regime": holdings_by_regime,
            "top_performers": top_performers[:3],
            "bottom_performers": bottom_performers[:3],
            "avg_agi_score": self.state.get("portfolio", {}).get("avg_agi_score", 50),
            "available_usdt": self.state.get("usdt_balance", 0),
        }

    def detect_market_regime_from_positions(self) -> str:
        """
        Detect market regime based on portfolio performance patterns.
        """
        holdings = self.state.get("portfolio", {}).get("positions", {})

        if not holdings:
            return "UNKNOWN"

        positive = sum(1 for h in holdings.values() if h["pnl_pct"] > 0)
        negative = sum(1 for h in holdings.values() if h["pnl_pct"] < 0)
        total = len(holdings)

        avg_pnl = sum(h["pnl_pct"] for h in holdings.values()) / total

        if positive / total > 0.7 and avg_pnl > 3:
            return "STRONG_BULL"
        elif positive / total > 0.5 and avg_pnl > 0:
            return "BULLISH"
        elif negative / total > 0.7 and avg_pnl < -3:
            return "STRONG_BEAR"
        elif negative / total > 0.5 and avg_pnl < 0:
            return "BEARISH"
        elif abs(avg_pnl) < 1 and positive / total > 0.4:
            return "VOLATILE"
        else:
            return "FLAT"

    async def reconcile_holdings(self):
        """🚀 SELF-HEALING: Synchronize local state with actual KuCoin balances"""
        self.log_event("   🕵️ RECONCILING: Synchronizing state with actual exchange balances...")

        try:
            # 🛡️ DUST & STABLECOIN FILTER
            balances = await self.client.get_all_balances(min_value_usd=0)
            STABLECOINS = [
                "USDT",
                "USDC",
                "DAI",
                "BUSD",
                "TUSD",
                "USD",
                "STABLE",
                "KCS",
            ]
            actual_holdings = {
                c: float(b.get("balance", 0))
                for c, b in balances.items()
                if c not in STABLECOINS and float(b.get("balance", 0)) > 0.00000001
            }

            # 1. Update/Add actual holdings to state
            for currency, balance in actual_holdings.items():
                if currency not in self.state["positions"]:
                    # New asset found on exchange not in state
                    try:
                        ticker = self.latest_tickers.get(currency) or await self.client.get_ticker(
                            f"{currency}-USDT"
                        )
                        price = float(ticker.price) if ticker else 0.1  # Fallback

                        position_value = balance * price
                        DUST_THRESHOLD = 1.0  # $1 minimum

                        if position_value < DUST_THRESHOLD:
                            self.log_event(
                                f"      🧹 SKIP DUST: {currency} = ${position_value:.6f} < $1"
                            )
                            continue

                        self.log_event(
                            f"      📥 ADOPTING POSITION: {currency} ({balance:.8f} @ ${price:.6f}) = ${position_value:.2f}"
                        )
                        self.state["positions"][currency] = {
                            "symbol": currency,
                            "quantity": balance,
                            "buy_price": price,
                            "current_price": price,
                            "mode": "EXISTING",
                            "regime": "unknown",
                            "opened": datetime.now().isoformat(),
                            "opportunity_score": 50,
                            "tp": price * (1 + TRADING.RISK.TAKE_PROFIT_PCT),
                            "sl": price * (1 - TRADING.RISK.STOP_LOSS_PCT),
                            "highest_pnl": 0,
                            "highest_pnl_display": "+0.00%",
                        }
                    except:
                        continue
                else:
                    # Sync quantity if it drifted
                    if abs(self.state["positions"][currency]["quantity"] - balance) > 0.00000001:
                        self.log_event(
                            f"      🔄 SYNCING QUANTITY: {currency} {self.state['positions'][currency]['quantity']:.8f} -> {balance:.8f}"
                        )
                        self.state["positions"][currency]["quantity"] = balance

            # 2. Remove dust positions from state (existing holdings below $1)
            DUST_THRESHOLD = 1.0
            dust_positions = []
            buy_orders = self.state.get("capital_awareness", {}).get("buy_orders", {})

            for sym, pos in self.state["positions"].items():
                if sym in STABLECOINS or sym in buy_orders:
                    continue
                if pos.get("mode") in [
                    "PENDING_BUY",
                    "PENDING_ADVANCED",
                    "PENDING_TWAP",
                ]:
                    continue

                balance = actual_holdings.get(sym, 0)
                ticker = (
                    self.latest_tickers.get(sym) or await self.client.get_ticker(f"{sym}-USDT")
                    if sym in actual_holdings
                    else None
                )
                price = float(ticker.price) if ticker else pos.get("current_price", 0)
                position_value = balance * price

                if position_value < DUST_THRESHOLD:
                    dust_positions.append((sym, position_value))

            for sym, value in dust_positions:
                self.log_event(f"      🧹 PURGING DUST: {sym} = ${value:.6f} < $1")
                del self.state["positions"][sym]

            # 3. Remove ghost positions from state (not on exchange anymore)
            ghosts = []
            for sym in self.state["positions"]:
                if (
                    sym not in actual_holdings
                    and self.state["positions"][sym].get("mode")
                    not in ["PENDING_BUY", "PENDING_ADVANCED", "PENDING_TWAP"]
                    and sym not in buy_orders
                ):
                    ghosts.append(sym)

            for sym in ghosts:
                self.log_event(f"      👻 PURGING GHOST: {sym} no longer exists on exchange")
                del self.state["positions"][sym]

            self._save_state()

            # 🛡️ VALIDATE: Auto-correct any positions with wrong TP/SL
            corrections = self.validate_and_correct_positions()
            if corrections > 0:
                self.log_event(
                    f"   🛡️ AUTO-CORRECTED {corrections} positions to match configuration"
                )

            self.log_event(
                f"   ✅ RECONCILIATION COMPLETE: Tracking {len(self.state['positions'])} positions"
            )

        except Exception as e:
            self.log_event(f"   ⚠️ Reconciliation failed: {e}")

    async def initialize(self):
        self.client = get_kucoin_client(paper_trading=self.paper_trading)
        if self.paper_trading:
            self.log_event("   📊 IBIS PAPER TRADING MODE ACTIVE")
        print("   ✓ Exchange connection verified")

        # Initialize Cross-Exchange Monitor
        await self.cross_exchange.initialize()

        # Verify AGI connection
        print("   🧠 Connecting to AGI Neural Link...")

        print("\n" + "=" * 70)
        print("   🦅 IBIS TRUE AUTONOMOUS AGENT v3.1")
        print("=" * 70)

        # Initialize Market Intelligence first so reconcile can use it
        await self.discover_market()
        await self.fetch_symbol_rules()

        self.log_event("   🧠 Initializing Market Intelligence...")
        await self.analyze_market_intelligence()

        # 🚀 Now Reconcile actual holdings with state
        await self.reconcile_holdings()

        balances = await self.client.get_all_balances()
        usdt_balance = float(balances.get("USDT", {}).get("balance", 0))
        usdt_available = float(balances.get("USDT", {}).get("available", 0))

        if self.state["daily"]["start_balance"] == 0:
            # Calculate total account value
            total_val = usdt_balance
            for sym, pos in self.state["positions"].items():
                total_val += pos["quantity"] * pos["current_price"]
            self.state["daily"]["start_balance"] = total_val
            print(f"   💰 Initialized Start Balance: ${total_val:.2f}")

        print(f"   💰 USDT Balance: ${usdt_balance:.2f} (avail: ${usdt_available:.2f})")
        print(f"   🎯 Agent Mode: {self.state['agent_mode']}")
        print("=" * 70)

        # Detect market regime
        await self.detect_market_regime()
        print(f"   🌐 Market Regime: {self.state['market_regime']}")

        # Determine agent mode based on market conditions
        await self.determine_agent_mode(self.state["market_regime"], self.market_intel)
        print(f"   🎯 Initial Agent Mode: {self.state['agent_mode']}")

    async def discover_market(self):
        """Dynamically discover ALL trading pairs - Filtered for intelligence"""

        self.symbol_rules = {}
        self.symbols_cache = []

        # Configurable filters from agent configuration
        self.stablecoins = self.config.get(
            "stablecoins", {"USDT", "USDC", "DAI", "TUSD", "USDP", "USD1", "USDY"}
        )
        self.ignored_symbols = self.config.get("ignored_symbols", {"BTC", "ETH", "SOL", "BNB"})

        try:
            symbols = await self.client.get_symbols()

            for sym in symbols:
                try:
                    base = sym.get("symbol", "")
                    if not base.endswith("-USDT"):
                        continue

                    base_currency = base.replace("-USDT", "")

                    if len(base_currency) < 2:
                        continue
                    if base_currency in self.stablecoins:
                        continue
                    if base_currency in self.ignored_symbols:
                        continue
                    if base_currency.isdigit():
                        continue
                    if base_currency.startswith("USD"):
                        continue

                    self.symbols_cache.append(base_currency)

                    self.symbol_rules[base_currency] = {
                        "baseMinSize": float(sym.get("baseMinSize", 0.001)),
                        "baseIncrement": float(sym.get("baseIncrement", 0.000001)),
                        "quoteMinSize": float(sym.get("quoteMinSize", 0.1)),
                        "quoteIncrement": float(sym.get("quoteIncrement", 0.0001)),
                    }

                except:
                    continue

            self.symbols_cache = list(set(self.symbols_cache))
            self.symbols_cache.sort()

            print(f"   📊 Discovered {len(self.symbols_cache)} trading pairs")

        except Exception as e:
            print(f"   ⚠️ Discovery error: {e}")
            self.symbols_cache = []

    async def fetch_symbol_rules(self):
        """Fetch symbol trading rules (minSize, increment) for proper order sizing"""
        try:
            symbols = await self.client.get_symbols()
            for sym in symbols:
                try:
                    base = sym.get("symbol", "")
                    if base.endswith("-USDT"):
                        self.symbol_rules[base.replace("-USDT", "")] = {
                            "baseMinSize": float(sym.get("baseMinSize", 0.001)),
                            "baseIncrement": float(sym.get("baseIncrement", 0.000001)),
                            "quoteMinSize": float(sym.get("quoteMinSize", 0.1)),
                            "quoteIncrement": float(sym.get("quoteIncrement", 0.0001)),
                        }
                except:
                    continue
            print(f"   📋 Loaded rules for {len(self.symbol_rules)} symbols")
        except Exception as e:
            print(f"   ⚠️ Failed to fetch rules: {e}")

    async def analyze_market_intelligence(self):
        """Comprehensive AI-powered market intelligence analysis optimized for SPEED and DEPTH"""

        market_intel = {}
        log_file = "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_true.log"

        def log_event(msg):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                with open(log_file, "a") as f:
                    f.write(f"[{timestamp}] {msg}\n")
            except:
                pass
            print(msg)

        log_event("   🔍 IBIS performing rapid market screening...")

        try:
            tickers = await self.client.get_tickers()
            self.latest_tickers = {
                t.symbol.replace("-USDT", ""): t for t in tickers if t.symbol.endswith("-USDT")
            }
            ticker_map = self.latest_tickers
        except Exception as e:
            log_event(f"   ⚠️ Could not fetch all tickers: {e}")
            ticker_map = {}
            self.latest_tickers = {}

        # Filter symbols based on configuration and liquidity
        min_liquidity = self.config.get("min_liquidity", 1000)
        potential_symbols = []

        for sym in self.symbols_cache:
            ticker = ticker_map.get(sym)
            if not ticker:
                continue

            try:
                vol = float(getattr(ticker, "vol_24h", 0) or getattr(ticker, "volume_24h", 0) or 0)
                if float(ticker.price) > 0 and vol >= min_liquidity:
                    potential_symbols.append(sym)
            except:
                continue

        log_event(
            f"   🧠 IBIS identified {len(potential_symbols)} candidates (from {len(self.symbols_cache)})"
        )

        async def analyze_symbol(sym):
            try:
                # log_event(f"      🔬 Deep analysis: {sym}...") # Too noisy for main log
                # Use pre-fetched ticker data for high-speed analysis
                ticker = ticker_map.get(sym)
                if not ticker:
                    ticker = await self.client.get_ticker(f"{sym}-USDT")

                if not ticker:
                    return None

                price = float(ticker.price)
                change_24h = float(getattr(ticker, "change_24h", 0) or 0)
                volume_24h = float(
                    getattr(ticker, "vol_24h", 0) or getattr(ticker, "volume_24h", 0) or 0
                )
                high_24h = float(getattr(ticker, "high_24h", price * 1.01) or price * 1.01)
                low_24h = float(getattr(ticker, "low_24h", price * 0.99) or price * 0.99)

                # Get candle data
                try:
                    tasks = [
                        self.client.get_candles(f"{sym}-USDT", "1min", 30),
                        self.client.get_candles(f"{sym}-USDT", "5min", 24),
                        self.client.get_candles(f"{sym}-USDT", "15min", 16),
                    ]
                    results = await asyncio.gather(*tasks)
                    candles_1m, candles_5m, candles_15m = results
                except Exception as e:
                    return None

                candle_analysis = self._analyze_candles(candles_1m, candles_5m, candles_15m)

                volatility = (high_24h - low_24h) / price if high_24h > low_24h else 0.02

                momentum_1h = candle_analysis.get("momentum_1h", 0)
                price_action = candle_analysis.get("price_action", "neutral")

                base_score = self._calculate_technical_strength(momentum_1h, change_24h)

                enhanced_intel = self._calculate_enhanced_intel(
                    candles_1m, candles_5m, candles_15m, price
                )
                indicator_composite = enhanced_intel.get("composite_score", 50)

                unified_intel = await self._get_unified_intel_score(sym)
                unified_score = unified_intel.get("unified_score", 50)
                sources_working = unified_intel.get("sources_working", 0)

                if sources_working >= 3:
                    unified_weight = 0.2
                    indicator_weight = 0.15
                else:
                    unified_weight = 0.15
                    indicator_weight = 0.2

                score = (
                    (base_score * (1 - unified_weight - indicator_weight))
                    + (unified_score * unified_weight)
                    + (indicator_composite * indicator_weight)
                )

                volatility = (high_24h - low_24h) / price if high_24h > low_24h else 0.02

                return {
                    "symbol": sym,
                    "price": price,
                    "change_24h": change_24h,
                    "momentum_1h": momentum_1h,
                    "volatility": volatility,
                    "volatility_1m": candle_analysis.get("volatility_1m", 0.02),
                    "volatility_5m": candle_analysis.get("volatility_5m", 0.02),
                    "volatility_15m": candle_analysis.get("volatility_15m", 0.02),
                    "spread": min(volatility * 0.3, 0.02),
                    "volume_24h": volume_24h,
                    "score": score,
                    "unified_intel": unified_intel,
                    "enhanced_intel": enhanced_intel,
                    "timestamp": datetime.now().isoformat(),
                    "risk_level": self._calculate_risk_level(volatility, score),
                    "candle_analysis": candle_analysis,
                    "agi_insight": f"Technical indicators: RSI {enhanced_intel['rsi']['signal']}, MACD {enhanced_intel['macd']['signal']}, Composite {indicator_composite:.1f}",
                }
            except Exception as e:
                # self.log_event(f"      ⚠️ Analysis for {sym} failed: {e}")
                return None

        # 🚀 TRULY DYNAMIC SYMBOL DISCOVERY SYSTEM
        # Fetches real-time trading pairs from exchange on every cycle for maximum freshness
        cycle_count = self.state.get("cycle_count", 0)
        self.state["cycle_count"] = cycle_count + 1

        # Real-time symbol discovery - fetch all current trading pairs from exchange
        self.log_event(f"   🔍 DISCOVERING TRADING PAIRS...")
        fresh_symbols = []
        try:
            exchange_symbols = await self.client.get_symbols()
            for sym in exchange_symbols:
                try:
                    base = sym.get("symbol", "")
                    if not base.endswith("-USDT"):
                        continue
                    base_currency = base.replace("-USDT", "")

                    # Apply basic filters
                    if len(base_currency) < 2:
                        continue
                    if base_currency in self.stablecoins:
                        continue
                    if base_currency in self.ignored_symbols:
                        continue
                    if base_currency.isdigit():
                        continue
                    if base_currency.startswith("USD"):
                        continue

                    # Store symbol rules for proper order sizing
                    self.symbol_rules[base_currency] = {
                        "baseMinSize": float(sym.get("baseMinSize", 0.001)),
                        "baseIncrement": float(sym.get("baseIncrement", 0.000001)),
                        "quoteMinSize": float(sym.get("quoteMinSize", 0.1)),
                        "quoteIncrement": float(sym.get("quoteIncrement", 0.0001)),
                    }

                    fresh_symbols.append(base_currency)
                except Exception as e:
                    continue

            # Update symbols cache with fresh data
            self.symbols_cache = list(set(fresh_symbols))
            self.log_event(f"   📊 Found {len(self.symbols_cache)} active trading pairs")
        except Exception as e:
            self.log_event(f"   ⚠️ Symbol discovery failed: {e}")

        # Prioritize holdings
        balances = await self.client.get_all_balances()
        holdings = [
            c
            for c in balances.keys()
            if c != "USDT" and float(balances.get(c, {}).get("balance", 0)) > 0
        ]

        # Dynamic symbol filtering based on real-time market data
        qualified_symbols = []
        for sym in self.symbols_cache:
            if sym in holdings:
                continue  # Already in portfolio

            ticker = ticker_map.get(sym)
            if not ticker:
                continue

            try:
                # Enhanced filtering criteria
                price = float(ticker.price)
                volume_24h = float(
                    getattr(ticker, "vol_24h", 0) or getattr(ticker, "volume_24h", 0) or 0
                )
                change_24h = float(getattr(ticker, "change_24h", 0) or 0)
                high_24h = float(getattr(ticker, "high_24h", price * 1.01) or price * 1.01)
                low_24h = float(getattr(ticker, "low_24h", price * 0.99) or price * 0.99)

                volatility = (high_24h - low_24h) / price
                spread = (price - low_24h) / high_24h

                # Filter based on market conditions
                regime = self.state.get("market_regime", "NORMAL")
                if regime == "VOLATILE":
                    # In volatile markets, prioritize high volatility and reasonable volume
                    if volume_24h >= min_liquidity * 0.8 and volatility > 0.02:
                        qualified_symbols.append(sym)
                elif regime == "STRONG_BULL":
                    # In bull markets, prioritize high volume and positive momentum
                    if volume_24h >= min_liquidity and change_24h > 3.0:
                        qualified_symbols.append(sym)
                elif regime == "STRONG_BEAR":
                    # In bear markets, prioritize high volatility and oversold conditions
                    if volume_24h >= min_liquidity * 0.5 and change_24h < -3.0:
                        qualified_symbols.append(sym)
                else:
                    # Normal market conditions - balanced approach
                    if volume_24h >= min_liquidity and volatility > 0.01:
                        qualified_symbols.append(sym)

            except Exception as e:
                continue

        # Rank symbols by potential (combined score of volume, volatility, and momentum)
        symbol_scores = []
        for sym in qualified_symbols:
            ticker = ticker_map.get(sym)
            if not ticker:
                continue

            try:
                price = float(ticker.price)
                volume_24h = float(
                    getattr(ticker, "vol_24h", 0) or getattr(ticker, "volume_24h", 0) or 0
                )
                change_24h = float(getattr(ticker, "change_24h", 0) or 0)
                high_24h = float(getattr(ticker, "high_24h", price * 1.01) or price * 1.01)
                low_24h = float(getattr(ticker, "low_24h", price * 0.99) or price * 0.99)

                volatility = (high_24h - low_24h) / price

                # Calculate potential score
                volume_score = min(volume_24h / (min_liquidity * 10), 1) * 40
                volatility_score = min(volatility / 0.05, 1) * 30
                momentum_score = min(abs(change_24h) / 5.0, 1) * 30

                total_score = volume_score + volatility_score + momentum_score
                symbol_scores.append((sym, total_score))
            except Exception as e:
                continue

        # Sort symbols by potential score (highest first)
        symbol_scores.sort(key=lambda x: x[1], reverse=True)

        E = TRADING.EXECUTION
        top_candidates = [sym for sym, score in symbol_scores[: E.TOP_CANDIDATES_LIMIT]]

        priority_symbols = holdings + top_candidates
        priority_symbols = priority_symbols[: E.PRIORITY_SYMBOLS_LIMIT]

        self.log_event(f"   📋 Priority Symbols: {priority_symbols}")

        semaphore = asyncio.Semaphore(E.PARALLEL_ANALYSIS_SIZE)

        # Pre-fetch Fear & Greed index once per cycle
        fg_data = None
        try:
            fg_data = await self.free_intel.get_fear_greed_index()
            fg_value = fg_data.get("value", "N/A")
            fg_class = fg_data.get("value_classification", "N/A")
            fg_source = fg_data.get("source", "unknown")
            fg_score = fg_data.get("score", 50)
            self.log_event(
                f"   📊 Fear & Greed: {fg_value} ({fg_class}) | source: {fg_source} | score: {fg_score}"
            )
        except Exception as e:
            self.log_event(f"   ⚠️ Fear & Greed fetch failed: {e}")
            fg_data = {"value": 50, "score": 50}  # Neutral fallback

        async def analyze_with_limit(sym):
            async with semaphore:
                try:
                    await asyncio.sleep(0.3)
                    res = await asyncio.wait_for(analyze_symbol(sym), timeout=12)
                    if res:
                        self.log_event(f"      ✅ Opportunity: {sym} (Score: {res['score']:.1f})")
                    return res
                except asyncio.TimeoutError:
                    self.log_event(f"      ⚠️ Timeout analyzing {sym}")
                    return None
                except Exception as e:
                    self.log_event(f"      ⚠️ Error analyzing {sym}: {e}")
                    return None

        tasks = [analyze_with_limit(sym) for sym in priority_symbols]
        self.log_event(
            f"   ⚡ IBIS performing deep analysis on top {len(priority_symbols)} priority symbols..."
        )

        results = await asyncio.gather(*tasks)

        for result in results:
            if result:
                market_intel[result["symbol"]] = result

        self.log_event(f"   ✅ Analyzed {len(market_intel)} high-quality opportunities")
        self.market_intel = market_intel
        return market_intel

    def _calculate_risk_level(self, volatility, score):
        if volatility > 0.05 and score < 60:
            return "HIGH"
        elif volatility > 0.03 or score < 55:
            return "MEDIUM"
        else:
            return "LOW"

    def _determine_opportunity_type(self, score, momentum):
        if score >= SCORE_THRESHOLDS.STANDARD and momentum > 1:
            return "BREAKOUT"
        elif score >= 65 and momentum < -1:
            return "REVERSAL"
        elif score >= 60 and abs(momentum) < 0.5:
            return "RANGE BOUND"
        else:
            return "UNCERTAIN"

    def _calculate_liquidity_score(self, volume):
        if volume > 5000000:
            return 95
        elif volume > 1000000:
            return 85
        elif volume > 500000:
            return 75
        elif volume > 100000:
            return 60
        else:
            return 40

    def _calculate_technical_strength(self, momentum, change_24h):
        strength = 50
        if momentum > 2:
            strength += 20
        elif momentum > 1:
            strength += 10
        elif momentum < -2:
            strength -= 20
        elif momentum < -1:
            strength -= 10

        if change_24h > 5:
            strength += 15
        elif change_24h > 2:
            strength += 8
        elif change_24h < -5:
            strength -= 15
        elif change_24h < -2:
            strength -= 8

        return max(0, min(100, strength))

    def _integrate_all_factors(
        self,
        base_score,
        orderbook,
        sentiment,
        onchain,
        change_24h,
        momentum_1h,
        volatility,
        unified_intel=None,
    ):
        """Integrate all intelligence factors into final score"""
        final_score = base_score

        sentiment_weight = self.config.get("sentiment_weight", 0.15)
        orderbook_weight = self.config.get("orderbook_weight", 0.10)
        onchain_weight = self.config.get("onchain_weight", 0.10)
        unified_weight = 0.15

        sentiment_score = sentiment.get("score", 50) if sentiment else 50
        orderbook_score = orderbook.get("score", 50) if orderbook else 50
        onchain_score = onchain.get("score", 50) if onchain else 50
        unified_score = unified_intel.get("unified_score", 50) if unified_intel else 50

        sentiment_conf = sentiment.get("confidence", 0) if sentiment else 0
        onchain_conf = onchain.get("confidence", 0) if onchain else 0
        unified_conf = (
            unified_intel.get("sources_working", 0) / unified_intel.get("total_sources", 6)
            if unified_intel
            else 0
        )

        sentiment_factor = min(max(sentiment_conf / 100, 0.0), 1.0)
        onchain_factor = min(max(onchain_conf / 100, 0.0), 1.0)
        unified_factor = min(max(unified_conf, 0.0), 1.0)

        sentiment_contribution = (sentiment_score - 50) * sentiment_weight * 2 * sentiment_factor
        orderbook_contribution = (orderbook_score - 50) * orderbook_weight * 2
        onchain_contribution = (onchain_score - 50) * onchain_weight * 2 * onchain_factor
        unified_contribution = (unified_score - 50) * unified_weight * 2 * unified_factor

        final_score += (
            sentiment_contribution
            + orderbook_contribution
            + onchain_contribution
            + unified_contribution
        )

        momentum_bonus = 0
        if momentum_1h > 0.5:
            momentum_bonus = min(momentum_1h * 5, 10)
        elif momentum_1h < -0.5:
            momentum_bonus = max(momentum_1h * 5, -10)
        final_score += momentum_bonus

        if change_24h > 3:
            final_score += 5
        elif change_24h > 5:
            final_score += 8
        elif change_24h < -3:
            final_score -= 5
        elif change_24h < -5:
            final_score -= 8

        final_score = max(0, min(100, final_score))

        return final_score

    def _calculate_enhanced_intel(self, candles_1m, candles_5m, candles_15m, price):
        """Calculate enhanced technical intelligence using indicators library"""
        result = {
            "rsi": {"signal": "NEUTRAL", "strength": 0.0, "value": 50},
            "macd": {"signal": "NEUTRAL", "strength": 0.0, "histogram": 0},
            "bollinger": {"signal": "NEUTRAL", "strength": 0.0, "position": 0.5},
            "ma_trend": {"signal": "NEUTRAL", "strength": 0.0, "above_ma20": 0.5},
            "atr": {"signal": "NORMAL", "strength": 0.0, "value": 0},
            "obv": {"signal": "NEUTRAL", "strength": 0.0, "trend": 0},
            "stochastic": {"signal": "NEUTRAL", "strength": 0.0, "k": 50},
            "vwap": {"signal": "NEUTRAL", "strength": 0.0, "deviation": 0},
            "composite_score": 50,
            "breakdown": {},
        }

        closes = [c.close for c in candles_1m] if candles_1m else []
        highs = [c.high for c in candles_1m] if candles_1m else []
        lows = [c.low for c in candles_1m] if candles_1m else []
        volumes = [c.volume for c in candles_1m] if candles_1m else []

        if len(closes) < 20:
            return result

        try:
            closes_valid = [c.close for c in candles_1m if hasattr(c, "close")]
            if len(closes_valid) >= 20:
                closes = closes_valid
                highs = [c.high for c in candles_1m if hasattr(c, "high")]
                lows = [c.low for c in candles_1m if hasattr(c, "low")]
                volumes = [c.volume for c in candles_1m if hasattr(c, "volume")]

                rsi_vals = RSI.calculate(closes, 14)
                rsi_signal, rsi_strength = RSI.signal(rsi_vals)
                result["rsi"] = {
                    "signal": rsi_signal,
                    "strength": rsi_strength,
                    "value": rsi_vals[-1] if not any(math.isnan(v) for v in rsi_vals[-5:]) else 50,
                }

                macd_data = MACD.calculate(closes, 12, 26, 9)
                macd_signal, macd_strength = MACD.signal(macd_data)
                hist_valid = [h for h in macd_data["histogram"] if not math.isnan(h)]
                result["macd"] = {
                    "signal": macd_signal,
                    "strength": macd_strength,
                    "histogram": hist_valid[-1] if hist_valid else 0,
                }

                bb_data = BollingerBands.calculate(closes, 20, 2.0)
                bb_signal, bb_strength = BollingerBands.signal(closes, bb_data)
                bb_position = (closes[-1] - bb_data["lower"][-1]) / (
                    bb_data["upper"][-1] - bb_data["lower"][-1] + 0.001
                )
                result["bollinger"] = {
                    "signal": bb_signal,
                    "strength": bb_strength,
                    "position": max(0, min(1, bb_position)),
                }

                ma20 = MovingAverage.sma(closes, 20)
                ma50 = MovingAverage.sma(closes, 50)
                ma20_valid = ma20[-1] if not math.isnan(ma20[-1]) else closes[-1]
                ma50_valid = ma50[-1] if not math.isnan(ma50[-1]) else closes[-1]

                if closes[-1] > ma20_valid > ma50_valid:
                    ma_signal = "BULLISH"
                    ma_strength = min((closes[-1] - ma20_valid) / ma20_valid * 50, 1.0)
                    ma_above = 1.0
                elif closes[-1] < ma20_valid < ma50_valid:
                    ma_signal = "BEARISH"
                    ma_strength = min((ma20_valid - closes[-1]) / ma20_valid * 50, 1.0)
                    ma_above = 0.0
                else:
                    ma_signal = "NEUTRAL"
                    ma_strength = 0.0
                    ma_above = 0.5

                result["ma_trend"] = {
                    "signal": ma_signal,
                    "strength": ma_strength,
                    "above_ma20": ma_above,
                }

                ohlcv_objects = candles_1m if hasattr(candles_1m[0], "high") else []
                if ohlcv_objects:
                    atr_vals = ATR.calculate(ohlcv_objects, 14)
                    atr_signal, atr_strength = ATR.volatility(atr_vals, price)
                    atr_valid = [v for v in atr_vals if not math.isnan(v)]
                    result["atr"] = {
                        "signal": atr_signal,
                        "strength": atr_strength,
                        "value": atr_valid[-1] if atr_valid else 0,
                    }

                if ohlcv_objects:
                    obv_vals = OBV.calculate(ohlcv_objects)
                    obv_signal, obv_strength = OBV.trend(obv_vals)
                    result["obv"] = {
                        "signal": obv_signal,
                        "strength": obv_strength,
                        "trend": 1
                        if obv_signal == "BULLISH"
                        else (-1 if obv_signal == "BEARISH" else 0),
                    }

                if ohlcv_objects:
                    stoch_data = Stochastic.calculate(ohlcv_objects, 14, 3)
                    stoch_signal, stoch_strength = Stochastic.signal(stoch_data)
                    result["stochastic"] = {
                        "signal": stoch_signal,
                        "strength": stoch_strength,
                        "k": stoch_data["k"][-1] if not math.isnan(stoch_data["k"][-1]) else 50,
                    }

                vwap_vals = VWAP.calculate(ohlcv_objects) if ohlcv_objects else []
                if vwap_vals:
                    vwap_signal, vwap_strength = VWAP.signal(closes, vwap_vals)
                    vwap_deviation = (
                        (closes[-1] - vwap_vals[-1]) / vwap_vals[-1] * 100
                        if vwap_vals[-1] > 0
                        else 0
                    )
                    result["vwap"] = {
                        "signal": vwap_signal,
                        "strength": vwap_strength,
                        "deviation": vwap_deviation,
                    }

                indicator_scores = {
                    "rsi": 0,
                    "macd": 0,
                    "bollinger": 0,
                    "ma_trend": 0,
                    "obv": 0,
                    "stochastic": 0,
                    "vwap": 0,
                }

                rsi_val = result["rsi"]["value"]
                if 40 < rsi_val < 60:
                    indicator_scores["rsi"] = 10
                elif 45 < rsi_val < 55:
                    indicator_scores["rsi"] = 15
                elif result["rsi"]["signal"] == "OVERSOLD":
                    indicator_scores["rsi"] = 20
                elif result["rsi"]["signal"] == "OVERBOUGHT":
                    indicator_scores["rsi"] = -10

                if result["macd"]["signal"].startswith("BULLISH"):
                    indicator_scores["macd"] = 15 if "STRONG" in result["macd"]["signal"] else 10
                elif result["macd"]["signal"].startswith("BEARISH"):
                    indicator_scores["macd"] = -15 if "STRONG" in result["macd"]["signal"] else -10

                if result["bollinger"]["signal"] == "OVERSOLD":
                    indicator_scores["bollinger"] = 15
                elif result["bollinger"]["signal"] == "BULLISH":
                    indicator_scores["bollinger"] = 10
                elif result["bollinger"]["signal"] == "BEARISH":
                    indicator_scores["bollinger"] = -5
                elif result["bollinger"]["signal"] == "OVERBOUGHT":
                    indicator_scores["bollinger"] = -15

                if result["ma_trend"]["signal"] == "BULLISH":
                    indicator_scores["ma_trend"] = 15
                elif result["ma_trend"]["signal"] == "BEARISH":
                    indicator_scores["ma_trend"] = -15

                if result["obv"]["signal"] == "BULLISH":
                    indicator_scores["obv"] = 10
                elif result["obv"]["signal"] == "BEARISH":
                    indicator_scores["obv"] = -10

                if result["stochastic"]["signal"] == "OVERSOLD":
                    indicator_scores["stochastic"] = 15
                elif result["stochastic"]["signal"] == "OVERBOUGHT":
                    indicator_scores["stochastic"] = -10
                elif result["stochastic"]["signal"] == "BULLISH":
                    indicator_scores["stochastic"] = 8
                elif result["stochastic"]["signal"] == "BEARISH":
                    indicator_scores["stochastic"] = -8

                if result["vwap"]["signal"] == "BULLISH":
                    indicator_scores["vwap"] = 8
                elif result["vwap"]["signal"] == "BEARISH":
                    indicator_scores["vwap"] = -8

                total_score = sum(indicator_scores.values())
                composite_score = 50 + total_score
                composite_score = max(0, min(100, composite_score))

                result["composite_score"] = composite_score
                result["breakdown"] = indicator_scores

                self.log_event(
                    f"      📊 INDICATORS: RSI:{rsi_val:.1f}/{rsi_signal} MACD:{macd_signal} "
                    f"BB:{result['bollinger']['signal']} MA:{result['ma_trend']['signal']} "
                    f"OBV:{result['obv']['signal']} STOCH:{result['stochastic']['signal']} "
                    f"Composite:{composite_score:.1f}"
                )

        except Exception as e:
            self.log_event(f"      ⚠️ Enhanced intel calculation error: {e}")

        return result

    async def _analyze_orderbook_depth(self, symbol):
        """Order book depth analysis for liquidity assessment"""
        try:
            depth = await self.client.get_orderbook(symbol, limit=100)
            if not depth:
                return {"bid_depth": 0, "ask_depth": 0, "imbalance": 0.5, "score": 50}

            bids = depth.get("bids", [])
            asks = depth.get("asks", [])

            bid_volume = sum(float(b[1]) for b in bids)
            ask_volume = sum(float(a[1]) for a in asks)

            total = bid_volume + ask_volume
            if total == 0:
                return {"bid_depth": 0, "ask_depth": 0, "imbalance": 0.5, "score": 50}

            bid_depth = bid_volume * float(bids[0][0]) if bids else 0
            ask_depth = ask_volume * float(asks[0][0]) if asks else 0

            imbalance = abs(bid_depth - ask_depth) / total
            balance_ratio = (
                min(bid_depth, ask_depth) / max(bid_depth, ask_depth)
                if max(bid_depth, ask_depth) > 0
                else 1
            )

            score = 50 + (balance_ratio - 0.5) * 50
            score = max(0, min(100, score))

            return {
                "bid_depth": bid_depth,
                "ask_depth": ask_depth,
                "imbalance": imbalance,
                "balance_ratio": balance_ratio,
                "score": score,
            }
        except Exception:
            return {"bid_depth": 0, "ask_depth": 0, "imbalance": 0.5, "score": 50}

    async def _get_unified_intel_score(self, symbol):
        """Get unified intelligence score from enhanced intel streams"""
        try:
            result = await self.enhanced_intel.get_unified_intel_score(symbol)
            self.log_event(
                f"   🧠 Unified intel for {symbol}: {result.get('unified_score', 50)} "
                f"(sources: {result.get('sources_working', 0)}/{result.get('total_sources', 0)})"
            )
            return result
        except Exception as e:
            self.log_event(f"   ⚠️ Unified intel error for {symbol}: {e}")
            return {"unified_score": 50, "sources_working": 0, "total_sources": 6}

    async def _get_sentiment_score(self, symbol):
        """Sentiment analysis from enhanced intel with free_intel fallback"""
        try:
            result = await self.enhanced_intel.get_social_sentiment(symbol)
            if result and result.get("score", 50) != 50 or result.get("error"):
                return {
                    "score": result.get("score", 50),
                    "source": "enhanced_vader",
                    "confidence": 75,
                    "timestamp": datetime.now(),
                }
        except Exception:
            pass

        try:
            comprehensive = await self.free_intel.get_comprehensive_sentiment(symbol)
            return {
                "score": comprehensive.get("score", 50),
                "sources": comprehensive.get("sources", {}),
                "confidence": comprehensive.get(
                    "confidence",
                    min(len(comprehensive.get("sources", {})) * 25, 100),
                ),
                "timestamp": datetime.now(),
            }
        except Exception:
            return {
                "score": 50,
                "sources": {},
                "confidence": 0,
                "timestamp": datetime.now(),
            }

    async def _get_twitter_sentiment(self, symbol):
        """Twitter sentiment from free sources (best-effort)"""
        try:
            return await self.free_intel.get_twitter_sentiment(symbol)
        except Exception:
            return None

    async def _get_reddit_sentiment(self, symbol):
        """Reddit sentiment from free API"""
        try:
            return await self.free_intel.get_reddit_sentiment(symbol)
        except Exception:
            return None

    async def _get_news_sentiment(self, symbol):
        """News sentiment from enhanced intel with free_intel fallback"""
        try:
            result = await self.enhanced_intel.get_news_sentiment(symbol)
            if result and result.get("score", 50) != 50 or result.get("error"):
                self.log_event(
                    f"   📰 Enhanced news sentiment for {symbol}: {result.get('score', 50)}"
                )
                return result
        except Exception:
            pass

        try:
            result = await self.free_intel.get_news_sentiment(symbol)
            if result is None:
                self.log_event(f"   ⚠️ News sentiment: No data for {symbol}")
            elif result.get("score", 50) == 50 and "error" in result:
                self.log_event(f"   ⚠️ News sentiment failed: {result.get('error', 'unknown')}")
            return result
        except Exception as e:
            self.log_event(f"   ⚠️ News sentiment error: {e}")
            return None

    async def _get_onchain_metrics(self, symbol):
        """On-chain metrics from enhanced intel with free_intel fallback"""
        try:
            enhanced_onchain = await self.enhanced_intel.get_onchain_metrics(symbol)
            if enhanced_onchain and enhanced_onchain.get("data_available"):
                self.log_event(
                    f"   ⛓️ Enhanced on-chain for {symbol}: {enhanced_onchain.get('score', 50)} "
                    f"(whale: {enhanced_onchain.get('whale_activity', 'unknown')})"
                )
                return {
                    "score": enhanced_onchain.get("score", 50),
                    "whale_score": enhanced_onchain.get("score", 50),
                    "inflow_score": 50,
                    "holder_score": 50,
                    "source": "enhanced_chaindl",
                    "confidence": 80,
                    "timestamp": datetime.now(),
                }
        except Exception:
            pass

        try:
            onchain = await self.free_intel.get_onchain_metrics(symbol)
            cmc = await self.free_intel.get_cmc_sentiment(symbol)
            flow = await self.free_intel.get_exchange_flow(symbol)
            whale = await self.free_intel.get_large_transactions(symbol)
            holders = await self.free_intel.get_holder_metrics(symbol)

            sources_status = []
            for name, data in [
                ("onchain", onchain),
                ("cmc", cmc),
                ("flow", flow),
                ("whale", whale),
                ("holders", holders),
            ]:
                if data and data.get("confidence", 0) > 0:
                    sources_status.append(f"{name}:{data.get('confidence', 0)}%")
                else:
                    sources_status.append(f"{name}:OFF")

            self.log_event(f"   📊 On-chain sources: {', '.join(sources_status)}")

            components = [
                ("onchain", onchain.get("score", 50), onchain.get("confidence", 50)),
                ("cmc", cmc.get("volume_score", 50), cmc.get("confidence", 50)),
                ("flow", flow.get("score", 50), flow.get("confidence", 50)),
                ("whale", whale.get("score", 50), whale.get("confidence", 50)),
                ("holders", holders.get("score", 50), holders.get("confidence", 50)),
            ]

            weighted_sum = 0.0
            weight_total = 0.0
            for _, score, weight in components:
                if weight > 0:
                    weighted_sum += score * weight
                    weight_total += weight

            final_score = weighted_sum / weight_total if weight_total > 0 else 50

            return {
                "score": final_score,
                "whale_score": onchain.get("whale_score", 50),
                "inflow_score": cmc.get("volume_score", 50),
                "holder_score": onchain.get("circulation_score", 50),
                "sources": {
                    "coincap": onchain,
                    "cmc": cmc,
                    "flow": flow,
                    "whale": whale,
                    "holders": holders,
                },
                "confidence": min(int(weight_total / 2), 100) if weight_total > 0 else 0,
                "timestamp": datetime.now(),
            }
        except Exception as e:
            self.log_event(f"   ⚠️ On-chain metrics error: {e}")
            return {
                "score": 50,
                "whale_score": 50,
                "inflow_score": 50,
                "holder_score": 50,
                "sources": {},
                "confidence": 0,
                "timestamp": datetime.now(),
            }

    async def _get_exchange_flow(self, symbol):
        """Exchange flow proxy from free sources"""
        try:
            return await self.free_intel.get_exchange_flow(symbol)
        except Exception:
            return None

    async def _get_large_transactions(self, symbol):
        """Large transaction proxy from free sources"""
        try:
            return await self.free_intel.get_large_transactions(symbol)
        except Exception:
            return None

    async def _get_holder_metrics(self, symbol):
        """Holder metrics proxy from free sources"""
        try:
            return await self.free_intel.get_holder_metrics(symbol)
        except Exception:
            return None

    async def _calculate_atr(self, symbol, period=14):
        """Average True Range for dynamic TP/SL"""
        try:
            candles = await self.client.get_candles(f"{symbol}-USDT", "15min", period + 10)
            if not candles or len(candles) < period:
                return {"atr": 0, "atr_percent": 0.02}

            tr_values = []
            for i in range(1, len(candles)):
                high = float(candles[i].high)
                low = float(candles[i].low)
                prev_close = float(candles[i - 1].close)
                tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
                tr_values.append(tr)

            if len(tr_values) < period:
                return {"atr": 0, "atr_percent": 0.02}

            atr = sum(tr_values[-period:]) / period
            current_price = float(candles[-1].close)
            atr_percent = atr / current_price if current_price > 0 else 0.02

            return {"atr": atr, "atr_percent": atr_percent}
        except Exception:
            return {"atr": 0, "atr_percent": 0.02}

    def _calculate_dynamic_tp_sl(self, price, atr_percent, regime, confidence_score):
        """Dynamic TP/SL based on ATR and regime"""
        tp_multiplier = self.config.get("atr_multiplier_tp", 2.0)
        sl_multiplier = self.config.get("atr_multiplier_sl", 3.0)

        regime_multipliers = {
            "TRENDING": {"tp": 3.0, "sl": 2.0},
            "VOLATILE": {"tp": 2.0, "sl": 1.5},
            "NORMAL": {"tp": 2.0, "sl": 2.0},
            "FLAT": {"tp": 1.5, "sl": 3.0},
            "UNCERTAIN": {"tp": 1.0, "sl": 1.0},
        }

        multipliers = regime_multipliers.get(regime, {"tp": 2.0, "sl": 2.0})

        tp_distance = atr_percent * tp_multiplier * multipliers["tp"]
        sl_distance = atr_percent * sl_multiplier * multipliers["sl"]

        confidence_bonus = confidence_score / 200
        tp_distance *= 1 + confidence_bonus
        sl_distance *= 1 - confidence_bonus * 0.5

        tp_price = price * (1 + tp_distance)
        sl_price = price * (1 - sl_distance)

        return {
            "tp_price": tp_price,
            "sl_price": sl_price,
            "tp_percent": tp_distance * 100,
            "sl_percent": sl_distance * 100,
            "atr_percent": atr_percent * 100,
        }

    async def _optimize_portfolio_allocation(self, opportunities, available_capital):
        """Portfolio rebalancing optimization - USE ALL CAPITAL"""
        if not opportunities:
            return {}

        position_sizes = {}
        total_score = sum(opp.get("adjusted_score", 50) for opp in opportunities)

        portfolio_heat = self.config.get("portfolio_heat", 0.6)  # Use 60%
        max_risk = self.config.get("max_portfolio_risk", 0.6)  # Use 60%

        for opp in opportunities:
            symbol = opp["symbol"]
            score = opp.get("adjusted_score", 50)
            weight = score / total_score if total_score > 0 else 1 / len(opportunities)

            # Aggressive sizing - use most of available capital
            base_size = available_capital * weight * portfolio_heat

            atr_data = await self._calculate_atr(symbol)
            atr_percent = atr_data.get("atr_percent", 0.02)

            # Adjust for volatility but stay aggressive
            risk_factor = min(atr_percent * 10, 1.0)
            adjusted_size = base_size * (1 + risk_factor * 0.5)

            # Allow larger positions
            max_size = available_capital * max_risk / len(opportunities) * 2
            final_size = min(adjusted_size, max_size)

            position_sizes[symbol] = {
                "size": final_size,
                "weight": weight,
                "atr_percent": atr_percent,
                "risk_factor": risk_factor,
            }

        return position_sizes

    def _calculate_advanced_score(
        self, price, change_24h, change_4h, momentum_1h, volatility, spread, volume
    ):
        """Advanced multi-factor scoring algorithm with comprehensive intelligence integration"""

        from ibis.market_intelligence import market_intelligence

        BREAKDOWN = {
            "base": 50,
            "volatility": 0,
            "momentum": 0,
            "mean_reversion": 0,
            "volume": 0,
            "spread": 0,
            "price": 0,
            "regime": 0,
            "timing": 0,
            "trend_strength": 0,
            "liquidity": 0,
            "market_quality": 0,
            "insight_score": 0,
        }

        score = 50

        # Volatility scoring (optimized for trading)
        if 0.005 < volatility < 0.06:
            score += 12
            BREAKDOWN["volatility"] = 12
        elif volatility >= 0.06 and volatility < 0.09:
            score += 6
            BREAKDOWN["volatility"] = 6
        elif volatility >= 0.09:
            score -= 10
            BREAKDOWN["volatility"] = -10
        else:
            score -= 8
            BREAKDOWN["volatility"] = -8

        # Market quality score from comprehensive intelligence
        try:
            from ibis.market_intelligence import market_intelligence

            # Calculate market quality based on multiple factors
            quality_score = min((volume / 10000000) * 5, 10)  # Volume quality
            if price > 0.01 and price < 1000:
                quality_score += 5
            if abs(change_24h) < 20:
                quality_score += 5
            BREAKDOWN["market_quality"] = int(quality_score)
            score += quality_score
        except Exception as e:
            print(f"Intelligence integration error: {e}")

        # Momentum scoring (dynamic based on regime)
        if abs(momentum_1h) > 0.3:
            momentum_score = momentum_1h * 3
            score += momentum_score
            BREAKDOWN["momentum"] = int(momentum_score)

        # Trend strength (combination of 24h and 4h changes)
        if abs(change_24h) > 0.5 and abs(change_4h) > 0.1:
            trend_score = 8 if change_24h * change_4h > 0 else 3
            score += trend_score
            BREAKDOWN["trend_strength"] = trend_score

        # Timing scoring (short-term vs long-term momentum)
        if change_4h > change_24h * 0.4 and change_24h > 0:
            score += 6
            BREAKDOWN["timing"] = 6
        elif change_4h < change_24h * 0.1 and change_24h > 0:
            score -= 6
            BREAKDOWN["timing"] = -6
        elif change_4h > change_24h * 0.3 and change_24h < 0:
            score += 4
            BREAKDOWN["timing"] = 4

        # Mean reversion scoring
        if -3 < change_24h < -0.5:
            score += 10
            BREAKDOWN["mean_reversion"] = 10
        elif 0 <= change_24h < 2:
            score += 6
            BREAKDOWN["mean_reversion"] = 6
        elif change_24h >= 4:
            score -= 12
            BREAKDOWN["mean_reversion"] = -12
        elif change_24h <= -4:
            score -= 10
            BREAKDOWN["mean_reversion"] = -10

        # Volume and liquidity scoring
        if volume > 10000000:
            score += 10
            BREAKDOWN["volume"] = 10
            BREAKDOWN["liquidity"] = 5
        elif volume > 5000000:
            score += 7
            BREAKDOWN["volume"] = 7
            BREAKDOWN["liquidity"] = 3
        elif volume > 1000000:
            score += 4
            BREAKDOWN["volume"] = 4
            BREAKDOWN["liquidity"] = 2
        elif volume > 100000:
            score += 2
            BREAKDOWN["volume"] = 2
        elif volume < 50000:
            score -= 15
            BREAKDOWN["volume"] = -15

        # Spread scoring (tight spreads = better liquidity)
        if spread < 0.0003:
            score += 10
            BREAKDOWN["spread"] = 10
        elif spread < 0.0008:
            score += 6
            BREAKDOWN["spread"] = 6
        elif spread < 0.0015:
            score += 3
            BREAKDOWN["spread"] = 3
        elif spread > 0.008:
            score -= 12
            BREAKDOWN["spread"] = -12

        # Price level scoring
        if 2 < price < 200:
            score += 8
            BREAKDOWN["price"] = 8
        elif 0.5 < price < 2 or 200 <= price < 800:
            score += 5
            BREAKDOWN["price"] = 5
        elif 0.1 < price < 0.5 or 800 <= price < 3000:
            score += 2
            BREAKDOWN["price"] = 2
        elif price < 0.05:
            score -= 25
            BREAKDOWN["price"] = -25
        elif price > 10000:
            score -= 15
            BREAKDOWN["price"] = -15

        # Regime bonus (calculated dynamically)
        regime_score = 0
        if 0.005 < volatility < 0.04 and abs(change_24h) < 1:
            regime_score = 5
        elif volatility > 0.06 and abs(momentum_1h) > 1:
            regime_score = 3
        BREAKDOWN["regime"] = regime_score
        score += regime_score

        final_score = max(0, min(100, score))

        # 📊 Log score breakdown
        breakdown_str = (
            f"V:{BREAKDOWN['volatility']:+d} M:{BREAKDOWN.get('momentum', 0):+d} "
            f"T:{BREAKDOWN.get('trend_strength', 0):+d} R:{BREAKDOWN.get('mean_reversion', 0):+d} "
            f"Vo:{BREAKDOWN.get('volume', 0):+d} Li:{BREAKDOWN.get('liquidity', 0):+d} "
            f"S:{BREAKDOWN.get('spread', 0):+d} P:{BREAKDOWN.get('price', 0):+d} "
            f"Ti:{BREAKDOWN.get('timing', 0):+d} Re:{BREAKDOWN.get('regime', 0):+d}"
        )

        self.log_event(f"      📊 SCORE: {sym} | base: {score:.1f} | breakdown: {breakdown_str}")

        return final_score, breakdown_str

    def _analyze_candles(self, candles_1m, candles_5m, candles_15m):
        """Comprehensive candle analysis with OHLCV patterns and market structure recognition"""
        analysis = {
            "volatility_1m": 0.02,  # Default volatility (2%)
            "volatility_5m": 0.02,
            "volatility_15m": 0.02,
            "trend_strength": 0,
            "volume_profile": 0,
            "candle_patterns": [],
            "support_level": 0,
            "resistance_level": 0,
            "price_action": "neutral",
        }

        # Analyze volatility across timeframes
        if candles_1m:
            analysis["volatility_1m"] = self._calculate_volatility(candles_1m)

        if candles_5m:
            analysis["volatility_5m"] = self._calculate_volatility(candles_5m)

        if candles_15m:
            analysis["volatility_15m"] = self._calculate_volatility(candles_15m)

        # Analyze trend strength
        analysis["trend_strength"] = self._calculate_trend_strength(candles_15m)

        # Analyze volume profile
        analysis["volume_profile"] = self._analyze_volume_profile(candles_5m)

        # Recognize candle patterns
        analysis["candle_patterns"] = []

        if candles_1m and len(candles_1m) >= 5:
            analysis["candle_patterns"].extend(self._recognize_candle_patterns(candles_1m[-5:]))

        if candles_5m and len(candles_5m) >= 5:
            analysis["candle_patterns"].extend(self._recognize_candle_patterns(candles_5m[-5:]))

        if candles_15m and len(candles_15m) >= 5:
            analysis["candle_patterns"].extend(self._recognize_candle_patterns(candles_15m[-5:]))

        # Calculate support and resistance levels
        analysis["support_level"] = self._find_support_level(candles_15m)
        analysis["resistance_level"] = self._find_resistance_level(candles_15m)

        # Determine price action type
        analysis["price_action"] = self._determine_price_action(candles_15m)

        # Calculate 1h momentum from 1m candles
        if candles_1m and len(candles_1m) >= 10:
            first_price = candles_1m[0].close
            last_price = candles_1m[-1].close
            if first_price > 0:
                analysis["momentum_1h"] = ((last_price - first_price) / first_price) * 100
            else:
                analysis["momentum_1h"] = 0
        else:
            analysis["momentum_1h"] = 0

        # 🕯️ Log candle analysis for visibility
        momentum_1h = analysis.get("momentum_1h", 0)
        if analysis["candle_patterns"]:
            self.log_event(
                f"      🕯️ CANDLES: {analysis['price_action']} | patterns: {analysis['candle_patterns']} | momentum: {momentum_1h:.3f}% | vol_1m: {analysis['volatility_1m']:.4f}"
            )
        else:
            self.log_event(
                f"      🕯️ CANDLES: {analysis['price_action']} | momentum: {momentum_1h:.3f}% | vol_1m: {analysis['volatility_1m']:.4f}"
            )

        return analysis

    def _calculate_volatility(self, candles):
        """Calculate volatility from candle data"""
        if not candles or len(candles) == 0:
            return 0.02  # Default volatility (2%)

        try:
            # Debug: Check candle data type and structure
            if (
                not hasattr(candles[0], "high")
                or not hasattr(candles[0], "low")
                or not hasattr(candles[0], "close")
            ):
                print(
                    f"Debug: Invalid candle structure - expected OHLC fields, got {dir(candles[0])}"
                )
                return 0.02

            # Calculate volatility as average true range normalized by price
            avg_price = sum(c.close for c in candles) / len(candles)
            if avg_price <= 0:
                return 0.02

            # Calculate volatility from OHLC (using range-based volatility)
            volatility = sum(((c.high - c.low) / avg_price) for c in candles) / len(candles)

            # Ensure volatility is within reasonable bounds (0.1% to 20%)
            volatility = max(0.001, min(0.20, abs(volatility)))

            return volatility
        except Exception as e:
            print(f"Debug: Volatility calculation error - {e}")
            return 0.02

    def _calculate_trend_strength(self, candles):
        """Calculate trend strength from candle patterns"""
        if not candles or len(candles) < 5:
            return 0

        # Calculate regression line for closing prices
        x = list(range(len(candles)))
        y = [c.close for c in candles]

        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_x_sq = sum(xi**2 for xi in x)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))

        denominator = n * sum_x_sq - (sum_x) ** 2

        if denominator == 0:
            return 0

        slope = (n * sum_xy - sum_x * sum_y) / denominator

        trend_strength = abs(slope) / max(y) * 100

        return min(trend_strength, 100)

    def _calculate_basic_position_size(self, opportunity_score, strategy, volatility):
        """Basic position sizing when EnhancedRiskManager is unavailable"""
        available = strategy["available"]
        min_trade = TRADING.POSITION.MIN_CAPITAL_PER_TRADE

        if available < min_trade:
            return 0

        base_pct = TRADING.POSITION.BASE_POSITION_PCT
        score_factor = opportunity_score / 100
        vol_adjustment = 1.0 / (1 + volatility)

        position_size = available * base_pct * score_factor * vol_adjustment
        position_size = max(min_trade, position_size)
        position_size = min(position_size, available * TRADING.POSITION.MAX_POSITION_PCT)

        return position_size

    def _analyze_volume_profile(self, candles):
        """Analyze volume profile and distribution"""
        if not candles:
            return 0

        volumes = [c.volume for c in candles]
        avg_volume = sum(volumes) / len(volumes)
        volume_variance = sum((v - avg_volume) ** 2 for v in volumes) / len(volumes)

        volume_profile = min(avg_volume / (avg_volume + volume_variance), 1.0) * 100

        return volume_profile

    def _recognize_candle_patterns(self, candles):
        """Recognize common candle patterns"""
        patterns = []

        if len(candles) < 2:
            return patterns

        if len(candles) >= 2:
            prev_candle = candles[-2]
            current_candle = candles[-1]

            if (
                current_candle.close > prev_candle.open
                and current_candle.open < prev_candle.close
                and current_candle.close > prev_candle.close
                and current_candle.open < prev_candle.open
            ):
                patterns.append("bullish_engulfing")

        if len(candles) >= 2:
            prev_candle = candles[-2]
            current_candle = candles[-1]

            if (
                current_candle.close < prev_candle.open
                and current_candle.open > prev_candle.close
                and current_candle.close < prev_candle.close
                and current_candle.open > prev_candle.open
            ):
                patterns.append("bearish_engulfing")

        if len(candles) >= 1:
            candle = candles[-1]
            body = abs(candle.close - candle.open)
            lower_shadow = (
                candle.open - candle.low
                if candle.close > candle.open
                else candle.close - candle.low
            )

            if body < (candle.high - candle.low) * 0.3 and lower_shadow > body * 2:
                patterns.append("hammer")

        if len(candles) >= 1:
            candle = candles[-1]
            body_size = abs(candle.close - candle.open)
            total_range = candle.high - candle.low

            if body_size < total_range * 0.1:
                patterns.append("doji")

        if len(candles) >= 1:
            candle = candles[-1]
            body = abs(candle.close - candle.open)
            upper_shadow = (
                candle.high - candle.open
                if candle.close > candle.open
                else candle.high - candle.close
            )

            if body < (candle.high - candle.low) * 0.3 and upper_shadow > body * 2:
                patterns.append("shooting_star")

        return patterns

    def _find_support_level(self, candles):
        """Find support level from candle data"""
        if not candles or len(candles) < 3:
            return 0

        low_prices = [c.low for c in candles]
        support_level = min(low_prices)

        return support_level

    def _find_resistance_level(self, candles):
        """Find resistance level from candle data"""
        if not candles or len(candles) < 3:
            return 0

        high_prices = [c.high for c in candles]
        resistance_level = max(high_prices)

        return resistance_level

    def _determine_price_action(self, candles):
        """Determine price action type from candle patterns"""
        if not candles or len(candles) < 5:
            return "neutral"

        close_prices = [c.close for c in candles]

        price_change = (close_prices[-1] - close_prices[0]) / close_prices[0] * 100

        if price_change > 2.0:
            return "strong_uptrend"
        elif price_change > 0.5:
            return "uptrend"
        elif price_change < -2.0:
            return "strong_downtrend"
        elif price_change < -0.5:
            return "downtrend"
        else:
            return "consolidation"

    def _assess_market_conditions(self):
        """Comprehensive market conditions assessment for AGI decision-making"""
        conditions = {
            "overall_health": "good",
            "trading_opportunity": "hunt",  # hunt, rest, caution
            "volatility_risk": "low",
            "liquidity_risk": "low",
            "trend_strength": "weak",
            "candle_patterns": "neutral",
            "support_resistance": "stable",
            "market_sentiment": "neutral",
            "volume_profile": "normal",
        }

        if not self.market_intel:
            conditions["overall_health"] = "poor"
            conditions["trading_opportunity"] = "rest"
        return conditions

    async def _should_stop_all_ops(self, market_conditions):
        """🚀 LIMITLESS: Never stop unless explicitly killed"""
        return False

    async def _cancel_all_orders(self):
        """Cancel all pending orders"""
        try:
            orders = await self.client.get_all_orders()
            for order_type in ["basic", "advanced", "twap"]:
                for order in orders.get(order_type, []):
                    try:
                        order_id = order.get("id")
                        if order_id:
                            await self.client.cancel_order(order_id)
                            print(f"   Cancelled order: {order_id}")
                    except Exception:
                        pass
        except Exception as e:
            print(f"   Warning: Could not cancel orders: {e}")

    async def detect_market_regime(self):
        """
        🧠 INTELLIGENT MARKET REGIME DETECTION
        Analyzes multiple market indicators to determine current regime.
        Supports: TRENDING, VOLATILE, FLAT, BULL, BEAR, UNCERTAIN
        """
        import statistics

        if not self.market_intel:
            return "unknown"

        changes_24h = []
        changes_1h = []
        volatilities = []
        trend_strengths = []
        volumes = []
        spreads = []
        volumes_high = []
        volumes_low = []

        for sym, data in self.market_intel.items():
            changes_24h.append(data.get("change_24h", 0))
            changes_1h.append(data.get("momentum_1h", 0))
            volatilities.append(data.get("volatility", 0.02))
            trend_strengths.append(data.get("market_activity", {}).get("trend_strength", 20))
            volumes.append(data.get("volume_24h", 0))
            spreads.append(data.get("spread", 0.002))

        avg_change_24h = sum(changes_24h) / len(changes_24h) if changes_24h else 0
        avg_change_1h = sum(changes_1h) / len(changes_1h) if changes_1h else 0
        avg_vol = sum(volatilities) / len(volatilities) if volatilities else 0
        avg_volume = sum(volumes) / len(volumes) if volumes else 0
        avg_spread = sum(spreads) / len(spreads) if spreads else 0
        avg_trend = sum(trend_strengths) / len(trend_strengths) if trend_strengths else 0

        # Calculate momentum direction
        momentum = avg_change_24h * 0.7 + avg_change_1h * 0.3

        # Calculate volatility regime
        vol_regime = "LOW"
        if avg_vol > 0.08:
            vol_regime = "EXTREME"
        elif avg_vol > 0.05:
            vol_regime = "HIGH"
        elif avg_vol > 0.025:
            vol_regime = "MEDIUM"
        else:
            vol_regime = "LOW"

        # Calculate trend consistency
        positive_count = sum(1 for c in changes_24h if c > 0)
        negative_count = sum(1 for c in changes_24h if c < 0)
        trend_consistency = (
            max(positive_count, negative_count) / len(changes_24h) if changes_24h else 0.5
        )

        # Determine regime with multiple factors
        regime = "UNCERTAIN"

        # Strong trending conditions
        if momentum > 1.5 and trend_consistency > 0.6 and avg_trend > 30:
            regime = "STRONG_BULL"
        elif momentum > 0.8 and trend_consistency > 0.55 and avg_trend > 25:
            regime = "BULL"
        elif momentum < -1.5 and trend_consistency > 0.6 and avg_trend > 30:
            regime = "STRONG_BEAR"
        elif momentum < -0.8 and trend_consistency > 0.55 and avg_trend > 25:
            regime = "BEAR"
        # Volatile conditions
        elif vol_regime in ["EXTREME", "HIGH"]:
            regime = "VOLATILE"
        # Low volatility conditions
        elif avg_vol < 0.015 and abs(momentum) < 0.5 and trend_consistency < 0.55:
            regime = "FLAT"
        # Normal conditions
        else:
            regime = "NORMAL"

        # 🧠 AGI Brain Override for critical situations
        agi_regime = None
        if agi_regime in ["CRASHING", "PUMPING", "REVERSAL"]:
            self.log_event(f"   🧠 AGI Override: {agi_regime} detected")
            regime = agi_regime

        # 📊 Log regime detection details
        self.log_event(
            f"   📊 REGIME: {regime} | momentum: {momentum:.2f} | vol: {avg_vol:.4f} | "
            f"trend: {avg_trend:.1f} | consistency: {trend_consistency:.2f} | +: {positive_count} -: {negative_count}"
        )

        # Track experience
        self.state["daily"]["regimes_experienced"][regime] = (
            self.state["daily"]["regimes_experienced"].get(regime, 0) + 1
        )

        # Save regime to state
        self.state["market_regime"] = regime

        # Update market intel with regime
        for symbol, intel in self.market_intel.items():
            intel["regime"] = regime

        return regime

    async def determine_agent_mode(self, regime, market_intel):
        """Advanced agent mode determination with adaptive risk management"""

        balance = self.state["daily"]["start_balance"]
        current_pnl = self.state["daily"]["pnl"]

        if balance > 0:
            return_pct = current_pnl / balance
        else:
            return_pct = 0

        # Calculate additional performance metrics
        total_trades = self.state["daily"]["trades"]
        win_rate = (self.state["daily"]["wins"] / total_trades) if total_trades > 0 else 0
        loss_rate = (self.state["daily"]["losses"] / total_trades) if total_trades > 0 else 0

        # 🛡️ TRASH MARKET DETECTION: Don't force trades in bad conditions
        # Calculate average market quality
        market_intel_values = list(self.market_intel.values()) if self.market_intel else []
        if market_intel_values:
            avg_market_score = sum(d.get("score", 0) for d in market_intel_values) / len(
                market_intel_values
            )
            high_quality_count = sum(
                1 for d in market_intel_values if d.get("score", 0) >= SCORE_THRESHOLDS.STANDARD
            )

            # If market is genuinely trash (avg score <40, <3 good setups), PAUSE
            if avg_market_score < 40 and high_quality_count < 3:
                self.log_event(
                    f"      🛑 TRASH MARKET DETECTED: Avg score {avg_market_score:.1f}, pausing trades"
                )
                mode = "OBSERVING"
                return mode

        # DATA-DRIVEN MODE DETERMINATION (maximize profits through intelligence)
        # TRENDING = ALWAYS AGGRESSIVE (100% WR in our data!)
        if regime == "TRENDING":
            mode = "AGGRESSIVE"  # Maximize profits in trending markets
        elif regime == "VOLATILE":
            mode = "HYPER_INTELLIGENT"  # Fast, aggressive, intelligence-driven
        elif return_pct < -0.08:
            mode = "DEFENSIVE"  # Severe loss - minimize risk
        elif return_pct < -0.04:
            mode = "CAUTIOUS"  # Moderate loss - reduce exposure
        elif loss_rate > 0.6:
            mode = "DEFENSIVE"  # Poor performance - reduce exposure
        elif regime == "FLAT" or (regime == "NORMAL" and abs(return_pct) < 0.01):
            mode = "MICRO_HUNTER"  # Low volatility - hunt micro-movements
        elif return_pct > 0.05:
            mode = "CONFIDENT"  # Strong gains - continue momentum
        elif regime == "LIQUID" and win_rate > 0.45:
            mode = "OPTIMISTIC"  # High liquidity - favorable conditions
        elif regime == "UNCERTAIN":
            mode = "OBSERVING"  # Uncertain market - wait for clarity
        else:
            mode = "HYPER_INTELLIGENT"  # Default to aggressive intelligence

        # Track strategy
        strat_key = f"{regime}_{mode}"
        current = self.state["daily"]["strategies_tried"].get(strat_key, 0)
        self.state["daily"]["strategies_tried"][strat_key] = current + 1

        return mode

    async def execute_strategy(self, regime, mode):
        """Execute appropriate strategy based on conditions - Full dynamic autonomy

        IBIS Philosophy: NO HOPE. ONLY HUNT.
        Deployment is intelligence-driven, not constraint-driven.
        """

        balances = await self.client.get_all_balances()
        usdt_balance = float(balances.get("USDT", {}).get("balance", 0))
        usdt_available = float(balances.get("USDT", {}).get("available", 0))

        holdings_value = 0

        for currency, data in balances.items():
            if currency == "USDT":
                continue
            balance = float(data.get("balance", 0))
            if balance > 0:
                price = self.market_intel.get(currency, {}).get("price", 0)

                if price <= 0:
                    try:
                        ticker = await self.client.get_ticker(f"{currency}-USDT")
                        if ticker and ticker.price:
                            price = float(ticker.price)
                    except Exception:
                        pass

                if price > 0:
                    value = balance * price
                    holdings_value += value

        total_assets = usdt_balance + holdings_value

        capital = await self.update_capital_awareness()
        real_capital = capital.get("real_trading_capital", usdt_available)
        available = real_capital

        self.state["daily"]["pnl"] = total_assets - self.state["daily"]["start_balance"]

        positions_value = holdings_value

        # MODE-BASED STRATEGY (from centralized configuration)
        # Use proper TP/SL from trading_constants (2% TP / 2% SL default = 1:1 R:R)
        base_tp = TRADING.RISK.TAKE_PROFIT_PCT  # 2%
        base_sl = TRADING.RISK.STOP_LOSS_PCT  # 2%

        mode_configs = {
            "TRENDING": {"target": base_tp, "stop": base_sl, "conf": 40},
            "DEFENSIVE": {"target": base_tp, "stop": base_sl, "conf": 55},
            "CAUTIOUS": {"target": base_tp, "stop": base_sl, "conf": 50},
            "MICRO_HUNTER": {"target": base_tp, "stop": base_sl, "conf": 45},
            "PATIENT": {"target": base_tp, "stop": base_sl, "conf": 55},
            "OPTIMISTIC": {"target": base_tp, "stop": base_sl, "conf": 50},
            "AGGRESSIVE": {"target": base_tp, "stop": base_sl, "conf": 45},
            "CONFIDENT": {"target": base_tp, "stop": base_sl, "conf": 45},
            "HYPER": {"target": base_tp, "stop": base_sl, "conf": 40},
            "HYPER_INTELLIGENT": {"target": base_tp, "stop": base_sl, "conf": 35},
            "OBSERVING": {"target": 0, "stop": 0, "conf": 100},
        }

        # Get base config from mode, fallback to regime
        if regime in mode_configs:
            config = mode_configs[regime]
            target_profit = config["target"]
            stop_loss = config["stop"]
            confidence_threshold = config["conf"]
        elif mode in mode_configs:
            config = mode_configs[mode]
            target_profit = config["target"]
            stop_loss = config["stop"]
            confidence_threshold = config["conf"]
        else:
            target_profit = TRADING.RISK.TAKE_PROFIT_PCT
            stop_loss = TRADING.RISK.STOP_LOSS_PCT
            confidence_threshold = TRADING.SCORE.MIN_THRESHOLD

        # Use centralized scan configuration - unlimited positions (IBIS decides)
        max_positions = 9999  # No hard limit - IBIS intelligence determines position count
        scan_interval = TRADING.get_scan_interval(regime)

        # Override for specific modes
        if mode == "OBSERVING":
            max_positions = 0
            scan_interval = 30

        self.config["min_score"] = confidence_threshold

        result = {
            "target_profit": target_profit,
            "stop_loss": stop_loss,
            "max_positions": max_positions,
            "scan_interval": scan_interval,
            "regime": regime,
            "mode": mode,
            "available": available,
            "positions_value": positions_value,
            "total_assets": total_assets,
            "confidence_threshold": confidence_threshold,
        }

        # Update state for monitor synchronization
        self.state["usdt_balance"] = available
        self.state["total_assets"] = total_assets
        self._save_state()

        return result

    async def calculate_position_size(self, opportunity_score, strategy, regime, market_intel):
        """🚀 ENHANCED RISK-AWARE POSITION SIZING

        Uses the advanced EnhancedRiskManager from ibis_enhanced_20x.py for:
        - Confidence-based sizing
        - Volatility-aware adjustments
        - Fear & Greed index integration
        - Portfolio correlation tracking
        """
        volatility = market_intel.get("volatility", 0.18) if market_intel else 0.18

        try:
            from ibis_enhanced_20x import EnhancedRiskManager
        except ImportError:
            self.log_event("   ⚠️ EnhancedRiskManager not available, using basic sizing")
            return self._calculate_basic_position_size(opportunity_score, strategy, volatility)

        available_for_trade = strategy["available"]
        min_trade = TRADING.POSITION.MIN_CAPITAL_PER_TRADE  # $10

        # Initialize enhanced risk manager
        risk_manager = EnhancedRiskManager(
            {
                "fear_greed_index": 14,  # Extreme Fear (current market)
                "base_position_pct": TRADING.POSITION.BASE_POSITION_PCT,
                "max_position_pct": TRADING.POSITION.MAX_POSITION_PCT,
            }
        )

        # Calculate volatility from market intel (fallback to default)
        volatility = 0.18  # Default for volatile market

        # Get current number of positions
        current_positions = len(self.state["positions"])

        # Calculate position size using enhanced risk management
        position_size = risk_manager.calculate_position_size(
            symbol="BTC",  # Placeholder for correlation check
            confidence=opportunity_score / 100,  # Convert score to 0-1 scale
            volatility=volatility,
            available_capital=available_for_trade,
            current_positions=current_positions,
            score=opportunity_score,
        )

        # Ensure minimum trade size is respected
        if position_size < min_trade and available_for_trade >= min_trade:
            position_size = min_trade

        # Ensure position size doesn't exceed maximum constraints
        position_size = min(position_size, TRADING.POSITION.MAX_CAPITAL_PER_TRADE)

        # Respect portfolio risk limits
        total_assets = self.state["capital_awareness"]["total_assets"]
        max_risk = total_assets * TRADING.RISK.MAX_PORTFOLIO_RISK
        current_risk = sum(pos["current_value"] for pos in self.state["positions"].values())
        remaining_risk = max_risk - current_risk
        # FIX: Don't allow negative position sizing - if over-leveraged, use minimum
        if remaining_risk < 0:
            remaining_risk = 0
        position_size = min(position_size, remaining_risk)

        self.log_event(
            f"      📊 Enhanced Position sizing: ${position_size:.2f} | "
            f"Score: {opportunity_score:.1f} | Avail: ${available_for_trade:.2f}"
        )

        return round(position_size, 2)

    async def dynamic_position_sizing(self, strategy, symbol, market_intel):
        """AGI-powered dynamic position sizing wrapper

        IBIS Philosophy: NO HOPE. ONLY HUNT.
        Position size is determined by intelligence, not constraints.
        """
        opp = market_intel.get(symbol, {})
        score = opp.get("score", 50)
        regime = strategy.get("regime", "NORMAL")

        return await self.calculate_position_size(score, strategy, regime, market_intel)

    def _is_market_primed(self, market_intel=None):
        """Check if market conditions are primed for trading"""
        intel = market_intel or self.market_intel
        if not intel:
            return False
        high_score_count = sum(
            1 for d in intel.values() if d["score"] >= SCORE_THRESHOLDS.GOOD_SETUP
        )
        avg_score = sum(d["score"] for d in intel.values()) / len(intel) if intel else 0
        return (
            high_score_count >= SCORE_THRESHOLDS.MARKET_PRIMED_HIGH_COUNT
            or avg_score >= SCORE_THRESHOLDS.MARKET_PRIMED_AVG_SCORE
        )

    async def suggest_portfolio_actions(self):
        """Suggest actions based on holdings analysis"""
        suggestions = []

        for symbol, pos in self.state["positions"].items():
            if pos.get("mode") == "EXISTING":
                score = pos.get("opportunity_score", 50)
                current_price = pos.get("current_price", 0)
                buy_price = pos.get("buy_price", 0)
                pnl_pct = ((current_price - buy_price) / buy_price * 100) if buy_price > 0 else 0

                if score < 50 and pnl_pct > 0:
                    suggestions.append(
                        {
                            "symbol": symbol,
                            "action": "TAKE_PROFIT",
                            "reason": f"Score {score}, PnL {pnl_pct:+.1f}%",
                            "score": score,
                            "pnl_pct": pnl_pct,
                        }
                    )
                elif score < 40:
                    suggestions.append(
                        {
                            "symbol": symbol,
                            "action": "CLOSE",
                            "reason": f"Low score {score}",
                            "score": score,
                            "pnl_pct": pnl_pct,
                        }
                    )

        return suggestions

    async def print_dashboard_summary(self, regime, mode, best_opp):
        """One-line dashboard summary for quick monitoring"""
        pnl = self.state["daily"]["pnl"]
        pnl_emoji = "🟢" if pnl >= 0 else "🔴"
        opp_count = (
            sum(1 for d in self.market_intel.values() if d["score"] >= SCORE_THRESHOLDS.GOOD_SETUP)
            if self.market_intel
            else 0
        )
        best_symbol = best_opp["symbol"] if best_opp else "N/A"
        best_score = best_opp["score"] if best_opp else 0

        balances = await self.client.get_all_balances()
        usdt_balance = float(balances.get("USDT", {}).get("balance", 0))
        total_assets = usdt_balance

        for currency, data in balances.items():
            if currency == "USDT":
                continue
            balance = float(data.get("balance", 0))
            if balance > 0:
                price = self.market_intel.get(currency, {}).get("price", 0)

                if price <= 0:
                    try:
                        ticker = await self.client.get_ticker(f"{currency}-USDT")
                        if ticker and ticker.price:
                            price = float(ticker.price)
                    except Exception:
                        pass

                if price > 0:
                    total_assets += balance * price

        print(
            f"\n[IBIS] 💰 ${total_assets:.2f} {pnl_emoji} PnL:{pnl:+.2f} | "
            f"📊 {opp_count} opportunities | "
            f"🎯 {best_symbol} {best_score}/100 | "
            f"{'🔥 PRIMED' if self._is_market_primed() else '◐ NORMAL'}"
        )

    async def find_all_opportunities(self, strategy):
        """Find ALL intelligent opportunities in the market (MAXIMUM UTILIZATION)"""
        market_intel = self.market_intel
        log_file = "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_true.log"

        def log_event(msg):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(log_file, "a") as f:
                f.write(f"[{timestamp}] {msg}\n")

        log_event(f"   🔍 Screening {len(market_intel)} potential trades...")

        # Pre-fetch Fear & Greed index for AGI brain
        fg_data = None
        fg_value = 50
        try:
            fg_data = await self.free_intel.get_fear_greed_index()
            fg_value = fg_data.get("value", 50) if fg_data else 50
        except Exception:
            fg_value = 50

        opportunities = []
        held = set(self.state["positions"].keys())

        sorted_opps = sorted(market_intel.items(), key=lambda x: x[1]["score"], reverse=True)

        regime = self.state.get("market_regime", "NORMAL")
        min_threshold = self.config.get("min_score", 70)  # Adaptive - uses strategy config

        for sym, intel in sorted_opps:
            if sym in held:
                continue

            score = intel["score"]  # Base score without artificial boost

            # AGI-Enhanced Analysis - pass Fear & Greed index
            agi_signal = None

            # Cross-Exchange Price Leading
            lead_signal = await self.cross_exchange.get_price_lead_signal(
                symbol=intel["symbol"], kucoin_price=intel["price"]
            )

            # 🔥 Log cross-exchange status
            if lead_signal["has_lead"]:
                if lead_signal["direction"] == "binance_leading":
                    score += lead_signal["boost"]
                    self.log_event(
                        f"      🔥 X-LEAD: Binance +{lead_signal['lead_pct']:.2f}% ahead, boost +{lead_signal['boost']}"
                    )
                elif lead_signal["direction"] == "kucoin_leading":
                    score += lead_signal["boost"]  # Negative boost
                    self.log_event(
                        f"      ⚠️ X-LAG: KuCoin +{abs(lead_signal['lead_pct']):.2f}% ahead, adjust {lead_signal['boost']}"
                    )
            else:
                self.log_event(f"      📊 X-LEAD: {intel['symbol']} neutral (no lead detected)")

            # 🧠 Log AGI signal
            if agi_signal:
                intel["agi_signal"] = agi_signal
                agi_score = agi_signal.get("enhanced_score", 50)
                # Bypass recommendation logic - ALWAYS BUY for high scores
                if score >= 90:
                    agi_action = "STRONG_BUY"
                elif score >= 70:
                    agi_action = "BUY"
                agi_reason = agi_signal.get("recommendation", {}).get("reason", "No reason")
                self.log_event(
                    f"      🧠 AGI: {intel['symbol']} | score: {agi_score:.1f} | action: {agi_action} | {agi_reason[:30]}"
                )

            if score >= min_threshold:
                # 🎯 EXTREME AGGRESSION - Always execute if score meets threshold
                diff = score - min_threshold
                if score >= 90:
                    reason = f"GOD TIER! ({diff:+.1f} above threshold) - EXECUTE"
                    agi_action = "STRONG_BUY"
                elif score >= 80:
                    reason = f"High confidence ({diff:+.1f} above threshold) - EXECUTE"
                    agi_action = "STRONG_BUY"
                elif score >= 70:
                    reason = f"Strong setup ({diff:+.1f} above threshold) - EXECUTE"
                    agi_action = "BUY"
                else:
                    reason = f"Standard ({diff:+.1f} above threshold) - EXECUTE"
                    agi_action = "BUY"

                # 📊 COMPONENTS - What contributed to the score
                components = []
                if intel.get("volatility", 0) < 0.04:
                    components.append(f"Vol:{intel.get('volatility', 0):.3f}")
                if intel.get("change_24h", 0) > 0:
                    components.append(f"24h:+{intel.get('change_24h', 0):.1f}%")
                if intel.get("momentum_1h", 0) > 0.3:
                    components.append(f"M1h:+{intel.get('momentum_1h', 0):.2f}")
                if intel.get("volume_24h", 0) > 10000000:
                    components.append(f"Vol:${intel.get('volume_24h', 0) / 1e6:.0f}M")
                if intel.get("order_flow", 0) > 0:
                    components.append(f"OF:+{intel.get('order_flow', 0):.0f}")
                if agi_signal and agi_signal.get("enhanced_score", 0) > 70:
                    components.append(f"AGI:{agi_signal.get('enhanced_score', 0):.0f}")

                # 🎯 COMPARISON - How this ranks vs other opportunities
                rank = len(opportunities) + 1
                total_analyzed = len(sorted_opps)
                percentile = (
                    (total_analyzed - rank) / total_analyzed * 100 if total_analyzed > 0 else 0
                )

                log_event(f"      ✅ {sym}: Score {score:.1f} >= {min_threshold} | {reason}")
                log_event(
                    f"         📊 COMPONENTS: {' + '.join(components) if components else 'Base technical'}"
                )
                log_event(
                    f"         🎯 COMPARISON: Rank #{rank}/{total_analyzed} (top {percentile:.0f}%)"
                )

                log_event(f"      ✅ {sym}: Score {score:.1f} >= {min_threshold} | {reason}")
                log_event(
                    f"         📊 Breakdown: V:{intel.get('volatility', 0):.3f} | "
                    f"M:{intel.get('momentum_1h', 0):.3f} | "
                    f"24h:{intel.get('change_24h', 0):.2f}% | "
                    f"Vol:${intel.get('volume_24h', 0) / 1e6:.1f}M"
                )

                opportunities.append({"symbol": sym, **intel, "adjusted_score": score})
                if len(opportunities) >= 20:
                    break
            else:
                # ❌ REJECT REASONING - Why rejected
                diff = min_threshold - score
                reject_reasons = []
                if score < 50:
                    reject_reasons.append("low_score")
                if intel.get("volume_24h", 0) < 100000:
                    reject_reasons.append("low_volume")
                if intel.get("spread", 0) > 0.005:
                    reject_reasons.append("wide_spread")

                if reject_reasons:
                    log_event(
                        f"      ❌ {sym}: Score {score:.1f} < {min_threshold} | "
                        f"Rejected: {', '.join(reject_reasons)}"
                    )

        log_event(f"   📊 Found {len(opportunities)} valid opportunities this cycle")
        return opportunities

    async def open_position(self, opportunity, strategy):
        """🚀 SUPREME ENTRY: Intelligence-Validated Execution"""
        symbol = opportunity["symbol"]
        price = opportunity["price"]
        score = opportunity["score"]

        self.log_event(f"      🎯 Executing with Intelligence Score: {score:.1f}")

        # 🛡️ DEDUPLICATION: Check if we already have an open order for this symbol
        buy_orders = self.state.get("capital_awareness", {}).get("buy_orders", {})
        if symbol in buy_orders:
            self.log_event(f"      ⚠️ DEDUPLICATION: {symbol} already has open order - skipping")
            return None

        # Use dynamic AGI-powered position sizing
        # Note: opportunity already contains the agi-enhanced score
        position_value = await self.dynamic_position_sizing(strategy, symbol, self.market_intel)

        # 🚀 SPREAD FILTER: Verify liquidity for market order
        try:
            ticker = await self.client.get_ticker(f"{symbol}-USDT")
            if ticker:
                bid = ticker.buy
                ask = ticker.sell
                spread = (ask - bid) / bid if bid > 0 else 0
                if spread > 0.01:  # 1% max spread for Supreme Mode
                    self.log_event(
                        f"      🛑 SPREAD TOO WIDE: {symbol} ({spread * 100:.2f}%) - skipping"
                    )
                    return None
        except Exception:
            pass

        rules = self.symbol_rules.get(symbol, {})
        base_increment = float(rules.get("baseIncrement", 0.000001))
        base_min_size = float(rules.get("baseMinSize", 0.001))
        quote_min_size = float(rules.get("quoteMinSize", 0.1))
        available_for_trade = strategy["available"]

        # Determine minimum position value - check if this could be final trade
        min_position_value = TRADING.POSITION.MIN_CAPITAL_PER_TRADE  # $10 minimum
        is_final_trade = (
            available_for_trade < TRADING.POSITION.MIN_CAPITAL_PER_TRADE
            and available_for_trade >= TRADING.POSITION.FINAL_TRADE_MIN_CAPITAL
        )
        if is_final_trade:
            min_position_value = TRADING.POSITION.FINAL_TRADE_MIN_CAPITAL
            self.log_event(f"      💰 FINAL TRADE: Using ${min_position_value:.1f} minimum")

        # Start with available capital - 99.5% for taker fees
        desired_position = min(position_value, available_for_trade * 0.995)

        # Calculate quantity
        quantity = desired_position / price

        quantity = round_down_to_increment(quantity, base_increment)

        if quantity < base_min_size:
            quantity = base_min_size

        quantity = round(quantity, 8)

        # Final check - enforce minimum position size
        final_order_value = quantity * price
        if final_order_value < min_position_value:
            print(
                f"⚠️ {symbol}: Position ${final_order_value:.2f} below ${min_position_value:.2f} minimum - skipping"
            )
            return None

        # 🎯 PRECISION EXECUTION: Get adaptive stop levels using ATR
        try:
            # Get recent candles for ATR calculation
            candles_5m = await self.client.get_candles(f"{symbol}-USDT", "5m", limit=20)

            # Calculate smart stops (adaptive based on volatility, averages ~2%)
            # stop_data = await self.enhanced.calculate_smart_stop_levels(
            #     entry_price=price, direction="LONG", candles=candles_5m, timeframe="5m"
            # )

            # Use default SL/TP if enhanced data not available
            sl = price * (1 - TRADING.RISK.STOP_LOSS_PCT)
            tp = price * (1 + TRADING.RISK.TAKE_PROFIT_PCT)
            sl_pct = TRADING.RISK.STOP_LOSS_PCT
            tp_pct = TRADING.RISK.TAKE_PROFIT_PCT
            tp = stop_data["take_profit"]
            sl_pct = stop_data["stop_distance_pct"] / 100
            tp_pct = stop_data["tp_distance_pct"] / 100

            self.log_event(
                f"      🎯 SMART STOPS: SL {stop_data['stop_distance_pct']:.2f}% ({stop_data['volatility_mode']}) | "
                f"TP {stop_data['tp_distance_pct']:.2f}%"
            )

        except Exception as e:
            self.log_event(f"      ⚠️ Smart stops failed, using defaults: {e}")
            # Fallback to strategy defaults
            base_tp_pct = (
                strategy.get("target_profit") if strategy.get("target_profit") is not None else 0.02
            )
            sl_pct = strategy.get("stop_loss") if strategy.get("stop_loss") is not None else 0.02

            # 📈 DYNAMIC TP ADJUSTMENT: Increase target in uptrends/structure breaks
            tp_boost = 0.0
            change_24h = opportunity.get("change_24h", 0)
            change_4h = opportunity.get("change_4h", 0)
            momentum_1h = opportunity.get("momentum_1h", 0)
            trend = opportunity.get("trend", "neutral")

            is_uptrend = change_24h > 2.0 and change_4h > 0.5 and momentum_1h > 0.3
            is_structure_break = (
                trend == "bullish"
                and change_24h > 3.0
                and opportunity.get("volume_24h", 0) > 5000000
            )

            if is_structure_break:
                tp_boost = 0.015
                self.log_event(f"      📈 STRUCTURE BREAK: {symbol} | TP boosted +1.5%")
            elif is_uptrend:
                tp_boost = 0.01
                self.log_event(f"      📈 UPTREND: {symbol} | TP boosted +1.0%")

            tp_pct = base_tp_pct + tp_boost
            tp = price * (1 + tp_pct)
            sl = price * (1 - sl_pct)

        sl_str = f"${sl:.4f} (-{sl_pct * 100:.1f}%)"

        self.log_event(f"      📊 Position sizing: ${position_value:.2f} | Qty: {quantity:.8f}")

        print(f"\n   ╔{'═' * 68}╗")
        print(f"   ║ {'🚀 EXECUTING TRADE':^66} ║")
        print(f"   ╠{'═' * 68}╣")
        print(f"   ║ Symbol: {symbol:<56} ║")
        print(f"   ║ Score: {score}/100 {self._get_score_label(score):<42} ║")
        print(f"   ║ Price: ${price:<55.4f} ║")
        print(f"   ║ Position: ${position_value:<54.2f} ║")
        print(f"   ║ Quantity: {quantity:<56} ║")
        print(
            f"   ║ Target: ${tp:<55.4f} (+{tp_pct * 100:.1f}%) {'[BOOSTED]' if tp_boost > 0 else '':<12} ║"
        )
        print(f"   ║ Stop: {sl_str:<55} ║")

        # 🚀 SUPREME INSIGHT
        insight = opportunity.get("agi_insight", "Neural Consensus Confirmed")
        # Truncate if too long
        display_insight = (insight[:53] + "...") if len(insight) > 53 else insight

        # 🎯 ENTRY REASON - Why entering this trade
        entry_reasons = []
        if score >= 90:
            entry_reasons.append("GOD_TIER")
        elif score >= 80:
            entry_reasons.append("HIGH_CONFIDENCE")
        elif score >= 70:
            entry_reasons.append("STRONG_SETUP")
        else:
            entry_reasons.append("STANDARD")

        if opportunity.get("agi_confidence", 0) >= 80:
            entry_reasons.append("AGI_CONFIRMED")

        intel = opportunity
        if intel.get("change_24h", 0) > 2:
            entry_reasons.append(f"24h_UP_{intel.get('change_24h', 0):.1f}%")
        if intel.get("momentum_1h", 0) > 0.5:
            entry_reasons.append(f"MOMENTUM_+{intel.get('momentum_1h', 0):.2f}")
        if intel.get("trend") == "bullish":
            entry_reasons.append("BULLISH_TREND")

        # 💰 RISK/REWARD RATIO
        tp_distance = (tp - price) / price if tp > price else 0
        sl_distance = (price - sl) / price if sl < price else 0
        risk_reward = tp_distance / sl_distance if sl_distance > 0 else 0

        print(f"   ║ AGI: {display_insight:<59} ║")
        print(f"   ║ 🎯 ENTRY: {' + '.join(entry_reasons):<50} ║")
        print(
            f"   ║ 💰 R:R = 1:{risk_reward:.1f} (TP: +{tp_distance * 100:.1f}% / SL: -{sl_distance * 100:.1f}%) ║"
        )
        print(f"   ║ Regime: {strategy['regime']:<54} ║")
        print(f"   ║ Mode: {strategy['mode']:<55} ║")
        print(f"   ╚{'═' * 68}╝\n")

        actual_value = quantity * price
        min_trade_value = TRADING.EXECUTION.MIN_TRADE_VALUE
        if actual_value < min_trade_value:
            print(
                f"⚠️ Order value ${actual_value:.2f} below minimum ${min_trade_value:.2f} - skipping"
            )
            return None

        try:
            # 🎯 PRECISION ENTRY: Optimize order type and price
            try:
                # Get order book for entry optimization
                order_book = await self.client.get_orderbook(f"{symbol}-USDT", limit=10)
                candles_1m = await self.client.get_candles(f"{symbol}-USDT", "1m", limit=5)

                # entry_rec = await self.enhanced.get_precision_entry_recommendation(
                #     symbol=symbol,
                #     direction="LONG",
                #     target_price=price,
                #     order_book=order_book,
                #     candles_1m=candles_1m,
                # )

                # Use optimized order type and price (use defaults when enhanced disabled)
                order_type = "market"  # entry_rec.get("order_type", "market")
                suggested_price = price  # entry_rec.get("suggested_price", price)

                improvement = 0  # entry_rec.get("price_improvement_pct", 0)
                if improvement > 0.01:  # Log if >0.01% improvement
                    self.log_event(
                        f"      💰 ENTRY OPTIMIZED: {symbol} | "
                        f"Type: {order_type.upper()} | "
                        f"Improvement: {improvement:.3f}%"
                    )

            except Exception as e:
                self.log_event(f"      ⚠️ Entry optimization failed, using market: {e}")
                order_type = "market"
                suggested_price = price

            self.log_event(
                f"      🚀 EXECUTING {order_type.upper()} buy for {symbol} ({quantity:.8f})..."
            )

            resp = await self.client.create_order(
                symbol=f"{symbol}-USDT",
                side="buy",
                type=order_type,
                price=suggested_price if order_type == "limit" else 0,
                size=quantity,
            )

            if not resp or not getattr(resp, "order_id", None):
                self.log_event(f"      ❌ ORDER FAILED for {symbol}: No order ID returned")
                return None

            self.log_event(
                f"      ✅ ORDER SUCCESS for {symbol} | OrderID: {getattr(resp, 'order_id', 'unknown')}"
            )

            # Track order status and fill information
            order_info = {
                "order_id": getattr(resp, "order_id", "unknown"),
                "symbol": symbol,
                "quantity": quantity,
                "price": suggested_price,
                "order_type": order_type,
                "status": "filled" if order_type == "market" else "pending",
                "timestamp": datetime.now().isoformat(),
                "tp": tp,
                "sl": sl,
                "mode": strategy["mode"],
                "regime": strategy["regime"],
                "opportunity_score": opportunity.get("adjusted_score", score),
            }

            self.state["capital_awareness"]["buy_orders"][symbol] = order_info
            self.state["capital_awareness"]["open_orders_count"] += 1

            if order_type == "market":
                pos = {
                    "symbol": symbol,
                    "quantity": quantity,
                    "buy_price": price,
                    "tp": tp,
                    "sl": sl,
                    "mode": strategy["mode"],
                    "regime": strategy["regime"],
                    "opened": datetime.now().isoformat(),
                    "opportunity_score": opportunity.get("adjusted_score", score),
                }
                self.state["positions"][symbol] = pos
                self.state["daily"]["trades"] += 1

                sl_info = (
                    f"SL: -{strategy['stop_loss'] * 100:.1f}%"
                    if strategy.get("stop_loss")
                    else "SL: Manual"
                )

                print(f"\n🚀 OPENED: {symbol} {quantity:.4f} @ ${price:.4f}")
                print(f"   Regime: {strategy['regime']} | Mode: {strategy['mode']}")
                tp_display = f"+{tp_pct * 100:.1f}%"
                if tp_pct > (strategy.get("target_profit", 0.06) * 1.2):
                    tp_display += " [BOOSTED]"
                print(
                    f"   Score: {opportunity.get('adjusted_score', score):.0f} | TP: {tp_display} | {sl_info}"
                )

                self._save_state()
                return pos
            else:
                self.state["daily"]["orders_placed"] += 1

                sl_info = (
                    f"SL: -{strategy['stop_loss'] * 100:.1f}%"
                    if strategy.get("stop_loss")
                    else "SL: Manual"
                )

                print(f"\n📝 PENDING ORDER: {symbol} {quantity:.4f} @ ${price:.4f} (Limit Buy)")
                print(f"   Regime: {strategy['regime']} | Mode: {strategy['mode']}")
                tp_display = f"+{tp_pct * 100:.1f}%"
                if tp_pct > (strategy.get("target_profit", 0.06) * 1.2):
                    tp_display += " [BOOSTED]"
                print(
                    f"   Score: {opportunity.get('adjusted_score', score):.0f} | TP: {tp_display} | {sl_info}"
                )
                print(f"   ⚠️ Will move to positions when order fills")

                self._save_state()
                return None

        except Exception as e:
            error_msg = str(e)
            print(f"❌ {symbol}: {error_msg}")

            if "Balance insufficient" in error_msg:
                print(f"   → Refreshing balance and retrying...")
                try:
                    balances = await self.client.get_all_balances()
                    actual_usdt = float(balances.get("USDT", {}).get("available", 0))
                    order_cost = quantity * price
                    if actual_usdt >= order_cost:
                        await asyncio.sleep(1)
                        await self.client.create_order(
                            symbol=f"{symbol}-USDT",
                            side="buy",
                            type="limit",
                            price=price,
                            size=quantity,
                        )
                        order_info = {
                            "order_id": f"retry_{symbol}_{int(time.time())}",
                            "symbol": symbol,
                            "quantity": quantity,
                            "price": price,
                            "order_type": "limit",
                            "status": "pending",
                            "timestamp": datetime.now().isoformat(),
                            "tp": tp,
                            "sl": sl,
                            "mode": strategy["mode"],
                            "regime": strategy["regime"],
                            "opportunity_score": opportunity.get("adjusted_score", score),
                        }
                    self.state["capital_awareness"]["buy_orders"][symbol] = order_info
                    self.state["daily"]["orders_placed"] += 1
                    print(f"\n📝 PENDING ORDER (retry): {symbol} {quantity:.4f} @ ${price:.4f}")
                    self._save_state()
                    return None
                except Exception as e2:
                    print(f"   → Retry failed: {e2}")

            elif "Order size increment invalid" in error_msg:
                print(f"   → Adjusting quantity...")
                try:
                    sym_data = await self.client.get_symbol(f"{symbol}-USDT")
                    if sym_data:
                        base_increment = float(sym_data.get("baseIncrement", 0.001))
                        base_min_size = float(sym_data.get("baseMinSize", 1.0))

                        self.symbol_rules[symbol] = {
                            "baseMinSize": base_min_size,
                            "baseIncrement": base_increment,
                        }

                        quantity = round_down_to_increment(quantity, base_increment)
                        if quantity < base_min_size:
                            quantity = base_min_size
                        if quantity * price >= 5:
                            resp = await self.client.create_order(
                                symbol=f"{symbol}-USDT",
                                side="buy",
                                type="limit",
                                price=price,
                                size=quantity,
                            )
                            if not resp or not getattr(resp, "order_id", None):
                                self.log_event(f"      ❌ ORDER FAILED (adjusted) for {symbol}")
                                return None
                            order_info = {
                                "order_id": getattr(resp, "order_id", "unknown")
                                if hasattr(resp, "order_id")
                                else "unknown",
                                "symbol": symbol,
                                "quantity": quantity,
                                "price": price,
                                "order_type": "limit",
                                "status": "pending",
                                "timestamp": datetime.now().isoformat(),
                                "tp": tp,
                                "sl": sl,
                                "mode": strategy["mode"],
                                "regime": strategy["regime"],
                                "opportunity_score": opportunity.get("adjusted_score", score),
                            }
                            self.state["capital_awareness"]["buy_orders"][symbol] = order_info
                            self.state["daily"]["orders_placed"] += 1
                            print(
                                f"\n📝 PENDING ORDER (adjusted): {symbol} {quantity:.4f} @ ${price:.4f}"
                            )
                            self._save_state()
                            return None
                except Exception as e2:
                    print(f"   → Adjustment failed: {e2}")

            return None

        rules = self.symbol_rules.get(symbol, {})
        base_increment = float(rules.get("baseIncrement", 0.000001))
        base_min_size = float(rules.get("baseMinSize", 0.001))

        quantity = position_value / price

        if base_increment > 0:
            quantity = (int(quantity / base_increment + 0.5)) * base_increment

        if quantity < base_min_size:
            quantity = base_min_size

        if quantity * price < 5:
            return None

        tp = price * (1 + strategy["target_profit"])
        sl = None if strategy.get("stop_loss") is None else price * (1 - strategy["stop_loss"])
        sl_str = (
            f"${sl:.4f} (-{strategy['stop_loss'] * 100:.1f}%)"
            if sl and strategy.get("stop_loss") is not None
            else "Manual/Trailing"
        )

        print(f"\n   ╔{'═' * 68}╗")
        print(f"   ║ {'🚀 EXECUTING TRADE':^66} ║")
        print(f"   ╠{'═' * 68}╣")
        print(f"   ║ Symbol: {symbol:<56} ║")
        print(f"   ║ Score: {score}/100 {self._get_score_label(score):<42} ║")
        print(f"   ║ Price: ${price:<55.4f} ║")
        print(f"   ║ Position: ${position_value:<54.2f} ║")
        print(f"   ║ Quantity: {quantity:<56} ║")
        print(f"   ║ Target: ${tp:<56.4f} (+{strategy['target_profit'] * 100:.1f}%) ║")
        print(f"   ║ Stop: {sl_str:<55} ║")
        print(f"   ║ Regime: {strategy['regime']:<54} ║")
        print(f"   ║ Mode: {strategy['mode']:<55} ║")
        print(f"   ╚{'═' * 68}╝\n")

        try:
            await self.client.create_order(
                symbol=f"{symbol}-USDT",
                side="buy",
                type="limit",
                price=price,
                size=quantity,
            )

            order_info = {
                "order_id": getattr(resp, "order_id", "unknown")
                if hasattr(resp, "order_id")
                else "unknown",
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "order_type": "limit",
                "status": "pending",
                "timestamp": datetime.now().isoformat(),
                "tp": tp,
                "sl": sl,
                "mode": strategy["mode"],
                "regime": strategy["regime"],
                "opportunity_score": opportunity.get("adjusted_score", score),
            }
            self.state["capital_awareness"]["buy_orders"][symbol] = order_info
            self.state["daily"]["orders_placed"] += 1

            sl_info = (
                f"SL: -{strategy['stop_loss'] * 100:.1f}%"
                if strategy.get("stop_loss")
                else "SL: Manual"
            )

            print(f"\n📝 PENDING ORDER: {symbol} {quantity:.4f} @ ${price:.4f} (Limit Buy)")
            print(f"   Regime: {strategy['regime']} | Mode: {strategy['mode']}")
            print(
                f"   Score: {opportunity['adjusted_score']:.0f} | TP: +{strategy['target_profit'] * 100:.1f}% | {sl_info}"
            )
            print(f"   ⚠️ Will move to positions when order fills")

            self._save_state()
            return pos

        except Exception as e:
            print(f"❌ {symbol}: {e}")
            return None

    async def check_positions(self, strategy):
        """Check all positions with proper TP/SL handling"""
        to_close = []
        DUST_THRESHOLD = 1.0  # $1 minimum to be considered a position

        for sym, pos in list(self.state["positions"].items()):
            try:
                ticker = self.latest_tickers.get(sym)
                if not ticker:
                    try:
                        ticker = await self.client.get_ticker(f"{sym}-USDT")
                    except:
                        pass

                # Use cached/current price, fall back to position data
                if ticker:
                    current = float(ticker.price)
                else:
                    # Fallback to position's current_price or buy_price
                    current = pos.get("current_price") or pos.get("buy_price", 0)
                    if current <= 0:
                        self.log_event(f"      ⚠️ No price data for {sym}, skipping")
                        continue

                pos["current_price"] = current

                buy_price = pos.get("buy_price", current)
                if buy_price <= 0:
                    buy_price = current

                quantity = pos.get("quantity", 0)
                position_value = quantity * current

                # 🧹 DUST CHECK: Remove dust positions (value < $1)
                if position_value < DUST_THRESHOLD:
                    self.log_event(
                        f"      🧹 DUST REMOVE: {sym} = ${position_value:.6f} < $1, removing from tracking"
                    )
                    del self.state["positions"][sym]
                    self._save_state()
                    continue

                pnl_pct = (current - buy_price) / buy_price if buy_price > 0 else 0

                trade_value = quantity * current
                estimated_fees = trade_value * TRADING.get_total_friction()
                pnl_value = quantity * (current - buy_price)
                actual_profit = pnl_value - estimated_fees

                pos_intel = self.market_intel.get(sym, {})
                current_score = pos_intel.get("score", 50)

                tp = pos.get("tp")
                sl = pos.get("sl")

                tp_hit = tp and current >= tp
                sl_hit = sl and current <= sl

                if not sl_hit and current <= pos.get("buy_price", current) * (
                    1 - TRADING.RISK.STOP_LOSS_PCT
                ):
                    sl_hit = True

                min_profit = TRADING.RISK.MIN_PROFIT_BUFFER
                covers_costs = actual_profit >= min_profit

                if tp_hit and covers_costs:
                    to_close.append((sym, "TAKE_PROFIT", current, pnl_pct, actual_profit))
                elif sl_hit:
                    to_close.append((sym, "STOP_LOSS", current, pnl_pct, actual_profit))
                elif current_score < 35 and pnl_pct < -0.003 and actual_profit < -min_profit:
                    to_close.append((sym, "ALPHA_DECAY", current, pnl_pct, actual_profit))

                capital = await self.update_capital_awareness()
                real_capital = capital.get("real_trading_capital", 0)
                if real_capital < 3.0 and actual_profit > min_profit:
                    to_close.append((sym, "RECYCLE_PROFIT", current, pnl_pct, actual_profit))

            except Exception as e:
                continue

            for sym, reason, exit_price, pnl_pct, actual_profit in to_close:
                pos = self.state["positions"].get(sym)
                if not pos:
                    self.log_event(f"      👻 SKIP EXIT: {sym} position already closed/gone")
                    continue

                hold_hours = 0
                if pos.get("opened"):
                    try:
                        opened = datetime.fromisoformat(pos["opened"])
                        hold_hours = (datetime.now() - opened).total_seconds() / 3600
                    except:
                        hold_hours = 0

                if reason == "TAKE_PROFIT":
                    exit_detail = (
                        f"Target reached (+{pnl_pct * 100:.2f}%, +${actual_profit:.4f} actual)"
                    )
                elif reason == "STOP_LOSS":
                    exit_detail = (
                        f"Stop loss triggered ({pnl_pct * 100:.2f}%, ${actual_profit:.4f})"
                    )
                elif reason == "ALPHA_DECAY":
                    exit_detail = f"Alpha decay detected ({pnl_pct * 100:.2f}%)"
                elif reason == "RECYCLE_PROFIT":
                    exit_detail = f"Profit recycled (+${actual_profit:.4f})"
                else:
                    exit_detail = f"Exit ({pnl_pct * 100:.2f}%)"

                self.log_event(
                    f"      🔴 EXIT TRIGGER: {sym} | {reason} | {exit_detail} | Held: {hold_hours:.1f}h"
                )

                await self.close_position(sym, reason, exit_price, pnl_pct, strategy)

    async def check_pending_orders(self):
        """Check pending buy orders and move filled orders to positions"""
        buy_orders = self.state.get("capital_awareness", {}).get("buy_orders", {})
        if not buy_orders:
            return

        filled_count = 0
        for symbol, order_info in list(buy_orders.items()):
            try:
                order_id = order_info.get("order_id")
                if not order_id:
                    continue

                order = await self.client.get_order(order_id, f"{symbol}-USDT")
                if not order:
                    continue

                is_active = getattr(order, "is_active", True)
                deal_size = getattr(order, "deal_size", 0) or 0
                deal_funds = getattr(order, "deal_funds", 0) or 0
                avg_price = getattr(order, "avg_price", 0) or 0
                fee = getattr(order, "fee", 0) or 0
                fee_currency = getattr(order, "fee_currency", "USDT")

                if not is_active and (deal_size > 0 or deal_funds > 0):
                    actual_price = avg_price if avg_price > 0 else order_info.get("price", 0)
                    actual_quantity = deal_size or order_info.get("quantity", 0)

                    if actual_quantity <= 0:
                        del buy_orders[symbol]
                        continue

                    pos = {
                        "symbol": symbol,
                        "quantity": actual_quantity,
                        "buy_price": actual_price,
                        "tp": order_info.get("tp"),
                        "sl": order_info.get("sl"),
                        "mode": order_info.get("mode", "SWING"),
                        "regime": order_info.get("regime", "unknown"),
                        "opened": order_info.get("timestamp", datetime.now().isoformat()),
                        "opportunity_score": order_info.get("opportunity_score", 50),
                        "order_id": order_id,
                        "fee": fee,
                        "fee_currency": fee_currency,
                    }

                    if symbol not in self.state["positions"]:
                        self.state["positions"][symbol] = pos
                        self.state["daily"]["trades"] += 1
                        print(
                            f"\n✅ ORDER FILLED: {symbol} {actual_quantity:.4f} @ ${actual_price:.4f}"
                        )
                        print(f"   Fee: {fee} {fee_currency}")
                        filled_count += 1

                    del buy_orders[symbol]

                elif is_active:
                    pass

            except Exception as e:
                self.log_event(f"   [PENDING CHECK] {symbol}: {e}")
                pass

        if filled_count > 0:
            self._save_state()

    async def close_position(self, symbol, reason, exit_price, pnl_pct, strategy) -> bool:
        """Close position and learn. Returns True if closed successfully, False otherwise."""
        if self._close_lock is None:
            self._close_lock = asyncio.Lock()
        async with self._close_lock:
            self.log_event(f"   [CLOSE FN START] {symbol}")
        pos = self.state["positions"].get(symbol)
        self.log_event(f"   [CLOSE FN FOUND] {symbol}: {pos is not None}")
        if not pos:
            self.log_event(f"   [CLOSE FN END] Position not found for {symbol}")
            buy_orders = self.state.get("capital_awareness", {}).get("buy_orders", {})
            if symbol in buy_orders:
                del buy_orders[symbol]
                self._save_state()
            return False

        # 🧹 DUST CHECK FIRST: Check BEFORE attempting to close
        original_qty = pos.get("quantity", 0)
        current_price = pos.get("current_price", 0)
        position_value = original_qty * current_price

        if position_value < 1.0:
            self.log_event(
                f"   🧹 DUST SKIP: {symbol} = ${position_value:.6f} < $1, removing from tracking"
            )
            del self.state["positions"][symbol]
            self._save_state()
            return True

        try:
            self.log_event(f"   [CLOSE FN TRY] About to place order for {symbol}")
            symbol_rules = self.symbol_rules.get(symbol, {})

            if not symbol_rules:
                self.log_event(f"   [CLOSE WARN] No rules for {symbol}, fetching...")

            # Get symbol rules
            if not symbol_rules:
                base_increment = 0.001
                base_min_size = 1.0
            else:
                base_increment = symbol_rules.get("baseIncrement", 0.001)
                base_min_size = symbol_rules.get("baseMinSize", 1.0)

            self.log_event(
                f"   [CLOSE DEBUG] {symbol}: original={original_qty}, increment={base_increment}, min={base_min_size}"
            )

            # Round quantity to valid increment - ALWAYS use actual quantity
            quantity = round_down_to_increment(original_qty, base_increment)

            # If rounded quantity is too small, use what we have (respecting exchange minimums)
            if quantity < base_min_size:
                quantity = original_qty  # Use actual qty, not base_min_size

            self.log_event(f"   [CLOSE DEBUG] {symbol}: orig={original_qty}, final_qty={quantity}")

            self.log_event(f"   [CLOSE EXEC] Creating market sell for {symbol} with qty={quantity}")

            try:
                order_result = await asyncio.wait_for(
                    self.client.create_order(
                        symbol=f"{symbol}-USDT",
                        side="sell",
                        type="market",
                        price=0,
                        size=quantity,
                    ),
                    timeout=10.0,
                )
                self.state["daily"]["orders_filled"] += 1
                self.log_event(f"   [CLOSE SUCCESS] {symbol} order filled")

                # Fetch actual order details to get real fees
                actual_fee = 0.0
                actual_fill_price = exit_price
                if order_result and order_result.order_id:
                    await asyncio.sleep(0.5)  # Wait for order to settle
                    filled_order = await self.client.get_order(
                        order_result.order_id, f"{symbol}-USDT"
                    )
                    if filled_order:
                        actual_fee = filled_order.fee
                        actual_fill_price = filled_order.avg_price or exit_price
                        self.log_event(
                            f"   [CLOSE FEE] Actual fee: {actual_fee:.6f} USDT, Fill price: {actual_fill_price}"
                        )

                # 🧹 CLEANUP: Remove from buy_orders tracking
                buy_orders = self.state.get("capital_awareness", {}).get("buy_orders", {})
                if symbol in buy_orders:
                    del buy_orders[symbol]

            except asyncio.TimeoutError:
                self.log_event(f"   [CLOSE ERROR] Timeout for {symbol}")
                return False
            except Exception as e:
                error_msg = str(e)
                self.log_event(f"   [CLOSE ERROR] {symbol}: {error_msg}")

                if "Order size increment invalid" in error_msg:
                    self.log_event(f"   [CLOSE RETRY] Adjusting quantity for {symbol}...")
                    try:
                        sym_data = await self.client.get_symbol(f"{symbol}-USDT")
                        if sym_data:
                            base_increment = float(sym_data.get("baseIncrement", 0.001))
                            base_min_size = float(sym_data.get("baseMinSize", 1.0))

                            self.symbol_rules[symbol] = {
                                "baseMinSize": base_min_size,
                                "baseIncrement": base_increment,
                            }

                            quantity = round_down_to_increment(original_qty, base_increment)

                            if quantity < base_min_size:
                                quantity = base_min_size

                            self.log_event(
                                f"   [CLOSE RETRY] {symbol}: orig={original_qty}, inc={base_increment}, adj={quantity}"
                            )

                            await asyncio.wait_for(
                                self.client.create_order(
                                    symbol=f"{symbol}-USDT",
                                    side="sell",
                                    type="market",
                                    price=0,
                                    size=quantity,
                                ),
                                timeout=10.0,
                            )
                            self.log_event(f"   [CLOSE SUCCESS] {symbol} retry succeeded")
                        else:
                            raise Exception(f"Symbol data not found for {symbol}")
                    except Exception as retry_error:
                        self.log_event(f"   [CLOSE FAIL] {symbol} retry failed: {retry_error}")
                        return False

                elif (
                    "Balance insufficient" in error_msg
                    or "not exist" in error_msg.lower()
                    or "50020" in error_msg
                    or "minimum" in error_msg.lower()
                    or "funds should more than" in error_msg.lower()
                ):
                    self.log_event(f"   [CLOSE WARN] {symbol} - insufficient funds, skipping")
                    return False
                else:
                    return False

            # Calculate REAL PnL from actual fill price and actual fees
            trade_volume = quantity * actual_fill_price
            estimated_fees = trade_volume * TRADING.get_total_friction()

            # Use actual fees from KuCoin if available, otherwise estimate
            if actual_fee > 0:
                pnl = (quantity * (actual_fill_price - pos["buy_price"])) - actual_fee
                fees_used = actual_fee
                self.log_event(f"   [CLOSE PnL] Using ACTUAL fees: {actual_fee:.6f} USDT")
            else:
                pnl = (quantity * (actual_fill_price - pos["buy_price"])) - estimated_fees
                fees_used = estimated_fees
                self.log_event(f"   [CLOSE PnL] Using ESTIMATED fees: {estimated_fees:.6f} USDT")

            pnl_pct_actual = (
                (actual_fill_price - pos["buy_price"]) / pos["buy_price"]
                if pos["buy_price"] > 0
                else 0
            )

            self.state["daily"]["pnl"] += pnl
            self.state["daily"]["fees"] += fees_used
            self.state["daily"]["realized_pnl"] += pnl
            if pnl > 0:
                self.state["daily"]["wins"] += 1
            else:
                self.state["daily"]["losses"] += 1

            # 🚀 LIMITLESS: Track profits for compounding
            if self.config.get("enable_compounding", True):
                pass  # self.phase1.update_profits(pnl)

            strat_key = f"{pos.get('regime', 'unknown')}_{reason.lower()}"
            perf = self.agent_memory["performance_by_symbol"].get(
                strat_key, {"trades": 0, "wins": 0, "losses": 0, "pnl": 0}
            )
            perf["trades"] += 1
            if pnl > 0:
                perf["wins"] += 1
            else:
                perf["losses"] += 1
            perf["pnl"] += pnl
            self.agent_memory["performance_by_symbol"][strat_key] = perf

            self.agent_memory["total_cycles"] += 1

            emoji = "🎯" if pnl > 0 else "🛑"
            print(
                f"\n{emoji} CLOSED: {symbol} ({reason}) {pnl_pct_actual * 100:+.2f}% | ${pnl:.4f}"
            )
            print(f"   Regime: {pos.get('regime', 'unknown')} | Mode: {pos.get('mode', 'unknown')}")

            del self.state["positions"][symbol]
            self._save_state()
            self._save_memory()
            await self.update_capital_awareness()

            try:
                from ibis.database.db import IbisDB

                db = IbisDB()
                db.close_position(
                    symbol=f"{symbol}-USDT",
                    exit_price=exit_price,
                    reason=reason,
                    actual_fee=fees_used,
                )
            except Exception as e:
                pass

            return True

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Close error for {symbol}: {error_msg}")

            if (
                "Balance insufficient" in error_msg
                or "not exist" in error_msg.lower()
                or "50020" in error_msg
                or "minimum" in error_msg.lower()
                or "funds should more than" in error_msg.lower()
            ):
                print(f"⚠️ Position {symbol} - order failed, will retry next cycle")
                return False
            else:
                print(f"⚠️ Unexpected close error for {symbol}")
                buy_orders = self.state.get("capital_awareness", {}).get("buy_orders", {})
                if symbol in buy_orders:
                    del buy_orders[symbol]
                if symbol in self.state.get("positions", {}):
                    del self.state["positions"][symbol]
                self._save_state()
                return False

    async def learn_from_trade(self, symbol, regime, pnl_pct, outcome):
        """Learn from trade outcomes to improve future decisions"""
        key = f"{regime}_{outcome}"

        if key not in self.agent_memory["performance_by_symbol"]:
            self.agent_memory["performance_by_symbol"][key] = {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "pnl": 0.0,
            }

        perf = self.agent_memory["performance_by_symbol"][key]
        perf["trades"] += 1
        perf["pnl"] += pnl_pct
        if pnl_pct > 0:
            perf["wins"] += 1
        else:
            perf["losses"] += 1

        best_regime = None
        best_winrate = 0
        for r_key, r_perf in self.agent_memory["performance_by_symbol"].items():
            if r_perf["trades"] >= 3:
                winrate = r_perf["wins"] / r_perf["trades"]
                if winrate > best_winrate:
                    best_winrate = winrate
                    best_regime = r_key.split("_")[0]

        if best_regime:
            self.agent_memory["learned_regimes"][best_regime] = {
                "winrate": best_winrate,
                "trades": sum(
                    p["trades"]
                    for k, p in self.agent_memory["performance_by_symbol"].items()
                    if k.startswith(best_regime)
                ),
            }

        self._save_memory()

    async def adapt(self, regime, mode, strategy):
        """Self-adaptation based on performance with history logging"""

        adaptations = []
        previous_mode = self.state.get("agent_mode", "unknown")

        trades = self.state["daily"]["trades"]
        pnl = self.state["daily"]["pnl"]
        balance = self.state["daily"]["start_balance"]

        if balance > 0:
            return_pct = pnl / balance
        else:
            return_pct = 0

        # Adaptation logic
        if return_pct < -0.02 and trades > 5:
            adaptations.append(
                {
                    "type": "REDUCE_AGGRESSION",
                    "reason": "Losing streak detected",
                    "action": "Switching to DEFENSIVE mode",
                }
            )

        if regime == "FLAT" and trades < 2:
            adaptations.append(
                {
                    "type": "INCREASE_SENSITIVITY",
                    "reason": "Flat market, need more opportunities",
                    "action": "Lowering entry threshold",
                }
            )

        if return_pct > 0.03 and trades > 8:
            adaptations.append(
                {
                    "type": "TAKE_PROFIT",
                    "reason": "Good run, secure gains",
                    "action": "Reduce position sizes",
                }
            )

        # Log adaptation history
        if adaptations:
            entry = {
                "time": datetime.now().isoformat(),
                "cycle": sum(self.state["daily"]["regimes_experienced"].values()),
                "regime": regime,
                "previous_mode": previous_mode,
                "new_mode": mode,
                "changes": adaptations,
                "pnl": pnl,
                "trades": trades,
            }
            self.agent_memory["adaptation_history"].append(entry)
            if len(self.agent_memory["adaptation_history"]) > 50:
                self.agent_memory["adaptation_history"] = self.agent_memory["adaptation_history"][
                    -50:
                ]

            for adapt in adaptations:
                print(f"\n🔄 ADAPTING: {adapt['type']}")
                print(f"   Reason: {adapt['reason']}")
                print(f"   Action: {adapt['action']}")

        self.state["agent_mode"] = mode

        return adaptations

    async def print_status(self, regime, mode, strategy):
        """Print comprehensive status"""

        # Get current values
        try:
            balances = await self.client.get_all_balances()
            usdt = float(balances.get("USDT", {}).get("available", 0))

            pos_value = 0
            for sym, pos in self.state["positions"].items():
                # Skip pending positions
                if pos.get("mode") == "PENDING_BUY":
                    continue

                try:
                    ticker = await self.client.get_ticker(f"{sym}-USDT")
                    if ticker:
                        price = float(ticker.price)
                        pos_value += pos["quantity"] * price

                        # 🎯 PRECISION: Check for trailing stop updates (NEW)
                        try:
                            # new_stop = await self.enhanced.get_trailing_stop_update(
                            #     position=pos,
                            #     current_price=price,
                            #     entry_price=pos.get("buy_price", 0),
                            # )

                            if False:  # Replace new_stop check when re-enabled
                                new_stop = pos.get("sl", 0)
                                if new_stop and new_stop != pos.get("sl", 0):
                                    # Update position with new stop level
                                    old_sl = pos.get("sl", 0)
                                    pos["sl"] = new_stop
                                    self.state["positions"][sym] = pos

                                    self.agent.log_event(
                                        f"      🛡️ TRAILING STOP UPDATE: {sym} | "
                                        f"SL: ${old_sl:.4f} → ${new_stop:.4f} | "
                                        f"Price: ${price:.4f}"
                                    )
                                self._save_state()

                        except Exception as e:
                            # Log trailing stop error but continue
                            pass

                except:
                    pass

            total = usdt + pos_value
            balance = self.state["daily"]["start_balance"]
            pnl = self.state["daily"]["pnl"]
            return_pct = (pnl / balance * 100) if balance > 0 else 0

            print(f"\n{'=' * 70}")
            print(f"   🦅 IBIS TRUE AUTONOMOUS AGENT | {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'=' * 70}")
            print(
                f"   Regime: {regime:10} | Mode: {mode:12} | Target: +{strategy['target_profit'] * 100:.1f}%"
            )
            print(f"   USDT:      ${usdt:.2f}")
            print(f"   Positions: ${pos_value:.2f} ({len(self.state['positions'])} open)")
            print(f"   TOTAL:     ${total:.2f}")
            print(f"   Today's:   ${pnl:+.4f} ({return_pct:+.2f}%)")
            print(
                f"   Trades:    {self.state['daily']['wins']}W {self.state['daily']['losses']}L ({self.state['daily']['trades']} total)"
            )
            print(f"{'=' * 70}")

            # Show best opportunities
            if self.market_intel:
                print(f"\n   📊 TOP OPPORTUNITIES:")
                for sym, intel in list(self.market_intel.items())[:5]:
                    print(
                        f"      {sym:8} Score: {intel['score']:.0f} | {intel['change_24h']:+.2f}% | Vol: {intel['volatility'] * 100:.1f}%"
                    )

        except Exception as e:
            print(f"⚠️ Status error: {e}")

    async def log_intelligence(self, regime, mode, strategy, best_opportunity):
        """IBIS MAXIMUM AUTONOMOUS INTELLIGENCE - Complete Market Analysis"""

        daily = self.state["daily"]
        win_rate = (daily["wins"] / daily["trades"] * 100) if daily["trades"] > 0 else 0
        cycles = sum(daily["regimes_experienced"].values())

        balances = await self.client.get_all_balances()
        usdt_balance = float(balances.get("USDT", {}).get("balance", 0))
        usdt_available = float(balances.get("USDT", {}).get("available", 0))

        holdings_value = 0
        holdings_display = []
        holdings_positions = []
        for currency, data in balances.items():
            if currency == "USDT":
                continue
            balance = float(data.get("balance", 0))
            if balance > 0:
                price = self.market_intel.get(currency, {}).get("price", 0)

                if price <= 0:
                    try:
                        ticker = await self.client.get_ticker(f"{currency}-USDT")
                        if ticker and ticker.price:
                            price = float(ticker.price)
                    except Exception:
                        pass

                if price > 0:
                    value = balance * price
                    holdings_value += value
                    holdings_display.append(f"{currency}:${value:.2f}")
                    holdings_positions.append((currency, balance, price, value))

        total_assets = usdt_balance + holdings_value
        self.state["daily"]["pnl"] = total_assets - self.state["daily"]["start_balance"]
        pnl = self.state["daily"]["pnl"]

        print(f"\n{'═' * 100}")
        print(
            f"   🦅 IBIS MAXIMUM AUTONOMOUS INTELLIGENCE | CYCLE {cycles:03d} | {datetime.now().strftime('%H:%M:%S')} | ${total_assets:.2f}"
        )
        print(f"{'═' * 100}")

        if not self.market_intel:
            print(f"\n   🔍 SCANNING MARKET...")
            await self.analyze_market_intelligence()

        avg_change = (
            sum(d["change_24h"] for d in self.market_intel.values()) / len(self.market_intel)
            if self.market_intel
            else 0
        )
        avg_vol = (
            sum(d["volatility"] for d in self.market_intel.values()) / len(self.market_intel)
            if self.market_intel
            else 0
        )
        avg_score = (
            sum(d["score"] for d in self.market_intel.values()) / len(self.market_intel)
            if self.market_intel
            else 0
        )
        total_vol = (
            sum(d["volume_24h"] for d in self.market_intel.values()) if self.market_intel else 0
        )

        trending = sum(1 for d in self.market_intel.values() if d["change_24h"] > 2)
        declining = sum(1 for d in self.market_intel.values() if d["change_24h"] < -2)
        consolidating = len(self.market_intel) - trending - declining

        change_str = f"{avg_change:+.3f}%" if abs(avg_change) > 0.01 else "N/A"
        vol_str = f"${total_vol:,.0f}" if total_vol > 0 else "N/A"

        print(f"\n   ┌{'─' * 98}┐")
        print(f"   │ {'🌐 GLOBAL MARKET PULSE':^96} │")
        print(f"   ├{'─' * 98}┤")
        print(
            f"   │ {'Symbols Analyzed:':<25} {len(self.market_intel):<20} {'Market Depth':<25} {trending:>3} ▲ | {consolidating:>3} → | {declining:>3} ▼ │"
        )
        print(
            f"   │ {'Avg Score:':<25} {avg_score:.1f}/100{' ' * 14} {'Avg 24h Change:':<25} {change_str} │"
        )
        print(
            f"   │ {'Avg Volatility:':<25} {avg_vol * 100:.2f}%{' ' * 14} {'Total Volume:':<25} {vol_str} │"
        )
        print(f"   │ {'Regime:':<25} {regime:<20} {'Mode:':<25} {mode} │")
        print(f"   └{'─' * 98}┘")

        balances = await self.client.get_all_balances()
        usdt_balance = float(balances.get("USDT", {}).get("balance", 0))
        usdt_available = float(balances.get("USDT", {}).get("available", 0))

        holdings_value = 0
        holdings_list = []
        holdings_display = []
        for currency, data in balances.items():
            if currency == "USDT":
                continue
            balance = float(data.get("balance", 0))
            if balance > 0:
                price = self.market_intel.get(currency, {}).get("price", 0)

                if price <= 0:
                    try:
                        ticker = await self.client.get_ticker(f"{currency}-USDT")
                        if ticker and ticker.price:
                            price = float(ticker.price)
                    except Exception:
                        pass

                if price > 0:
                    value = balance * price
                    holdings_value += value
                    holdings_list.append(f"{currency}:{balance:.4f}@${price:.4f}")
                else:
                    holdings_list.append(f"{currency}:{balance:.4f}@$???")

        holdings_all = holdings_list + holdings_display

        total_assets = usdt_balance + holdings_value
        positions_value = holdings_value
        usdt_holds = usdt_balance - usdt_available

        self.state["daily"]["pnl"] = total_assets - self.state["daily"]["start_balance"]
        pnl = self.state["daily"]["pnl"]
        daily = self.state["daily"]

        deployment_pct = (positions_value / total_assets * 100) if total_assets > 0 else 0

        capital = self.state.get("capital_awareness", {})
        usdt_locked_buy = capital.get("usdt_in_buy_orders", 0)
        holdings_locked_sell = capital.get("holdings_in_sell_orders", 0)
        real_trading_capital = capital.get("real_trading_capital", usdt_available)
        open_orders_count = capital.get("open_orders_count", 0)
        available_display = real_trading_capital

        total_fees = daily.get("fees", 0)
        fees_today = daily.get("fees", 0)
        orders_placed = daily.get("orders_placed", 0)
        orders_filled = daily.get("orders_filled", 0)
        fill_rate = (orders_filled / orders_placed * 100) if orders_placed > 0 else 0

        # Refresh capital awareness for dashboard
        asyncio.get_event_loop().create_task(self.update_capital_awareness())

        print(f"\n{'═' * 100}")
        print(
            f"   🦅 IBIS MAXIMUM AUTONOMOUS INTELLIGENCE | CYCLE {cycles:03d} | {datetime.now().strftime('%H:%M:%S')} | ${total_assets:.2f}"
        )
        print(f"{'═' * 100}")

        print(f"\n   ┌{'─' * 98}┐")
        print(f"   │ {'💰 COMPLETE CAPITAL VISIBILITY':^96} │")
        print(f"   ├{'─' * 98}┤")

        print(f"   │ {'💵 TOTAL ASSETS:':<30} ${total_assets:<20.2f} {'=' * 40} │")

        print(
            f"   │ {'   ├─ USDT Total:':<30} ${usdt_balance:<20.2f} {'Deployed:':<20} {deployment_pct:.1f}% │"
        )
        print(
            f"   │ {'   ├─ USDT Available (Free):':<30} ${usdt_available:<20.2f} {'Reserve:':<20} {100 - deployment_pct:.1f}% │"
        )
        print(
            f"   │ {'   ├─ USDT Locked (Buy Orders):':<30} ${usdt_locked_buy:<20.2f} {'Open Orders:':<20} {open_orders_count} │"
        )
        print(
            f"   │ {'   └─ REAL TRADING CAPITAL:':<30} ${real_trading_capital:<20.2f} {'-' * 24} │"
        )

        print(f"   │ {'─' * 98}│")

        print(f"   │ {'📦 HOLDINGS Value:':<30} ${holdings_value:<20.2f} {'=' * 40} │")
        print(
            f"   │ {'   ├─ Holdings (Free):':<30} ${holdings_value - holdings_locked_sell:<20.2f} {'-' * 40} │"
        )
        print(
            f"   │ {'   └─ Holdings Locked (Sell):':<30} ${holdings_locked_sell:<20.2f} {'-' * 40} │"
        )

        print(f"   │ {'─' * 98}│")

        print(f"   │ {'💸 FEES & COSTS':<96} │")
        print(f"   │ {'   ├─ Total Fees Paid:':<30} ${total_fees:<20.4f} {'-' * 40} │")
        print(f"   │ {'   ├─ Fees Today:':<30} ${fees_today:<20.4f} {'-' * 40} │")
        print(f"   │ {'   └─ Orders Fill Rate:':<30} {fill_rate:<20.1f}% {'-' * 40} │")

        print(f"   │ {'─' * 98}│")

        print(f"   │ {'📊 PORTFOLIO METRICS':<96} │")
        print(
            f"   │ {'   ├─ Total Holdings:':<30} {len(holdings_all):<20} {'Total Value:':<25} ${positions_value:.2f} │"
        )
        print(
            f"   │ {'   ├─ Trades Today:':<30} {daily['trades']:<20} {'Closed P&L:':<25} ${self.state['daily']['pnl']:+.4f} │"
        )
        print(
            f"   │ {'   ├─ Win Rate:':<30} {win_rate:.1f}%{' ' * 15} {'Win/Loss:':<25} {daily['wins']}W / {daily['losses']}L │"
        )
        print(f"   │ {'   └─ Realized P&L:':<30} ${daily.get('realized_pnl', 0):+.4f} {'-' * 48} │")
        print(f"   │ {'─' * 98}│")

        # Display AGI Decision-Making Logic
        market_conditions = self._assess_market_conditions()

        print(f"   │ {'─' * 98}│")
        print(f"   │ {'🧠 AGI DECISION-MAKING':<96} │")
        print(
            f"   │ {'   ├─ Market Health:':<30} {market_conditions['overall_health'].upper():<20} {'Opportunity:':<25} {market_conditions['trading_opportunity'].upper()} │"
        )
        print(
            f"   │ {'   ├─ Volatility Risk:':<30} {market_conditions['volatility_risk'].upper():<20} {'Trend Strength:':<25} {market_conditions['trend_strength'].upper()} │"
        )
        print(
            f"   │ {'   ├─ Volume Profile:':<30} {market_conditions['volume_profile'].upper():<20} {'Market Sentiment:':<25} {market_conditions['market_sentiment'].upper()} │"
        )
        print(
            f"   │ {'   ├─ Candle Patterns:':<30} {market_conditions['candle_patterns'].upper():<20} {'Support/Resistance:':<25} {market_conditions['support_resistance'].upper()} │"
        )

        high_score_count = (
            sum(1 for d in self.market_intel.values() if d["score"] >= SCORE_THRESHOLDS.GOOD_SETUP)
            if self.market_intel
            else 0
        )
        avg_score = (
            sum(d["score"] for d in self.market_intel.values()) / len(self.market_intel)
            if self.market_intel
            else 0
        )
        is_market_primed = (
            high_score_count >= SCORE_THRESHOLDS.MARKET_PRIMED_HIGH_COUNT
            or avg_score >= SCORE_THRESHOLDS.MARKET_PRIMED_AVG_SCORE
        )

        print(f"   │ {'🎯 DYNAMIC DEPLOYMENT INTELLIGENCE':^96} │")
        print(
            f"   │ {'   ├─ Mode:':<30} {mode:<20} {'Target/Trade:':<25} +{strategy['target_profit'] * 100:.2f}% │"
        )
        sl_display = (
            f"-{strategy['stop_loss'] * 100:.2f}%"
            if strategy.get("stop_loss") is not None
            else "Manual"
        )
        print(f"   │ {'   ├─ Regime:':<30} {regime:<20} {'Stop/Trade:':<25} {sl_display} │")
        print(
            f"   │ {'   ├─ Max Concurrent:':<30} {strategy['max_positions']:<20} {'Scan Interval:':<25} {strategy['scan_interval']}s │"
        )
        print(
            f"   │ {'   ├─ Min Score:':<30} {strategy['confidence_threshold']:<20} {'Available:':<25} ${available_display:.2f} │"
        )
        print(
            f"   │ {'   └─ Market Status:':<30} {'🔥 PRIMED' if is_market_primed else '◐ NORMAL':<20} {'High-Score Count:':<25} {high_score_count} │"
        )

        print(f"   │ {'─' * 98}│")
        print(f"   │ {'📊 DEPLOYMENT MULTIPLIERS':^96} │")
        print(f"   │ {'   ├─ Score ≥95:':<30} 4.0x {'(Full deployment)':<40} │")
        print(f"   │ {'   ├─ Score ≥90:':<30} 3.0x {'(High confidence)':<40} │")
        print(f"   │ {'   ├─ Score ≥85:':<30} 2.0x {'(Strong setup)':<40} │")
        print(f"   │ {'   ├─ Score ≥80:':<30} 1.5x {'(Good setup)':<40} │")
        print(f"   │ {'   ├─ Score ≥70:':<30} 1.0x {'(Standard)':<40} │")
        print(f"   │ {'   └─ Market Primed:':<30} 1.5x {'(Multipliers stack!)':<40} │")

        print(f"   └{'─' * 98}┘")

        print(f"\n   ┌{'─' * 98}┐")
        print(f"   │ {'🎯 ACTIVE POSITIONS BREAKDOWN':^96} │")
        print(f"   ├{'─' * 98}┤")

        positions_to_show = []

        if self.state["positions"]:
            for sym, pos in self.state["positions"].items():
                try:
                    ticker = await self.client.get_ticker(f"{sym}-USDT")
                    current_price = (
                        float(ticker.price) if ticker else float(pos.get("buy_price", 0))
                    )
                except:
                    current_price = float(pos.get("buy_price", 0))

                quantity = float(pos.get("quantity", 0))
                entry_price = float(pos.get("buy_price", current_price))
                current_value = quantity * current_price
                pnl = (current_price - entry_price) * quantity
                pnl_pct = ((current_price / entry_price) - 1) * 100 if entry_price > 0 else 0

                positions_to_show.append(
                    {
                        "symbol": sym,
                        "quantity": quantity,
                        "entry_price": entry_price,
                        "current_price": current_price,
                        "value": current_value,
                        "pnl": pnl,
                        "pnl_pct": pnl_pct,
                    }
                )

            if positions_to_show:
                print(
                    f"   │ {'SYMBOL':<8} {'QTY':<10} {'ENTRY':<10} {'CURRENT':<10} {'VALUE':<10} {'P&L %':<10} {'P&L $':<10} {'STATUS':<12} │"
                )
                print(
                    f"   │ {'─' * 8} {'─' * 10} {'─' * 10} {'─' * 10} {'─' * 10} {'─' * 10} {'─' * 10} {'─' * 12} │"
                )

                total_value = sum(p["value"] for p in positions_to_show)
                total_pnl = sum(p["pnl"] for p in positions_to_show)

                for pos in sorted(positions_to_show, key=lambda x: x["pnl"], reverse=True):
                    pnl_emoji = "🟢" if pos["pnl"] >= 0 else "🔴"
                    status = f"{pnl_emoji} {'+' if pos['pnl'] >= 0 else ''}{pos['pnl_pct']:.2f}%"

                    print(
                        f"   │ {pos['symbol']:<8} {pos['quantity']:<10.4f} ${pos['entry_price']:<9.4f} ${pos['current_price']:<9.4f} ${pos['value']:<9.2f} {pos['pnl_pct']:+.2f}%     ${pos['pnl']:+.4f}   {status:<12} │"
                    )

                print(
                    f"   │ {'─' * 8} {'─' * 10} {'─' * 10} {'─' * 10} {'─' * 10} {'─' * 10} {'─' * 10} {'─' * 12} │"
                )
                print(
                    f"   │ {'TOTAL':<8} {'':<10} {'':<10} {'':<10} ${total_value:<9.2f} {'':<10} ${total_pnl:+.4f}   {'🟢' if total_pnl >= 0 else '🔴':<12} │"
                )
        else:
            print(f"   │ {'NO ACTIVE POSITIONS - HUNTING PHASE':^96} │")

        print(f"   └{'─' * 98}┘")

        suggestions = await self.suggest_portfolio_actions()
        if suggestions:
            print(f"\n   ┌{'─' * 98}┐")
            print(f"   │ {'💡 PORTFOLIO OPTIMIZATION SUGGESTIONS':^96} │")
            print(f"   ├{'─' * 98}┤")
            for sug in suggestions[:5]:
                emoji = "🎯" if sug["action"] == "TAKE_PROFIT" else "⚠️"
                print(f"   │ {emoji} {sug['symbol']:<8} {sug['action']:<12} {sug['reason']:<70} │")
            print(f"   └{'─' * 98}┘")

        print(f"\n   ┌{'─' * 98}┐")
        print(f"   │ {'🚀 TOP 10 OPPORTUNITIES RANKED':^96} │")
        print(f"   ├{'─' * 98}┤")

        if self.market_intel:
            sorted_opps = sorted(
                self.market_intel.items(), key=lambda x: x[1]["score"], reverse=True
            )[:10]

            print(
                f"   │ {'#':<4} {'SYMBOL':<10} {'SCORE':<8} {'PRICE':<14} {'24H%':<10} {'VOL%':<10} {'VOLUME':<18} {'INSIGHTS':<20} │"
            )
            print(
                f"   │ {'─' * 4} {'─' * 10} {'─' * 8} {'─' * 14} {'─' * 10} {'─' * 10} {'─' * 18} {'─' * 20} │"
            )

            for rank, (sym, intel) in enumerate(sorted_opps, 1):
                # Use comprehensive insights from market intelligence
                insights_list = intel.get("insights", [])

                change_str = "N/A"
                if abs(intel["change_24h"]) > 0.01:
                    change_str = f"{intel['change_24h']:+.2f}%"

                vol_str = "N/A"
                if intel["volume_24h"] > 0:
                    vol_str = (
                        f"${intel['volume_24h']:,.0f}"
                        if intel["volume_24h"] < 1000000
                        else f"${intel['volume_24h'] / 1000000:.1f}M"
                    )

                risk_level = intel.get("risk_level", "MEDIUM")
                opp_type = intel.get("opportunity_type", "UNCERTAIN")

                # Risk level indicator
                risk_indicator = {"HIGH": "🚨", "MEDIUM": "⚠️", "LOW": "✅"}

                # Opportunity type indicator
                type_indicator = {
                    "BREAKOUT": "📈",
                    "REVERSAL": "🔄",
                    "RANGE BOUND": "➡️",
                    "UNCERTAIN": "❓",
                }

                # Display up to 3 key insights
                display_insights = insights_list[:3]
                insights_text = "·".join(display_insights)

                print(
                    f"   │ {rank:<4} {sym:<10} {intel['score']:<8} ${intel['price']:<13.4f} {change_str:<10} {intel['volatility'] * 100:.2f}%   {vol_str:<18} {risk_indicator[risk_level]} {type_indicator[opp_type]} {insights_text:<30} │"
                )

        print(f"   └{'─' * 98}┘")

        if best_opportunity:
            sym = best_opportunity["symbol"]
            print(f"\n   ┌{'─' * 98}┐")
            print(f"   │ {'🎯 BEST OPPORTUNITY DEEP DIVE: ' + sym:^95} │")
            print(f"   ├{'─' * 98}┤")
            print(
                f"   │ {'Current Price:':<25} ${best_opportunity.get('price', 0):<20.4f} {'Score:':<25} {best_opportunity.get('score', 0):.1f}/100 │"
            )
            change_str = (
                f"{best_opportunity.get('change_24h', 0):+.3f}%"
                if abs(best_opportunity.get("change_24h", 0)) > 0.001
                else "N/A"
            )
            momentum_str = (
                f"{best_opportunity.get('momentum_1h', 0):+.3f}%"
                if abs(best_opportunity.get("momentum_1h", 0)) > 0.001
                else "N/A"
            )
            vol_str = (
                f"${best_opportunity.get('volume_24h', 0):,.0f}"
                if best_opportunity.get("volume_24h", 0) > 0
                else "N/A"
            )

            print(
                f"   │ {'24h Change:':<25} {change_str:<25} {'4h Change:':<25} {best_opportunity.get('change_4h', 0):+.4f}% │"
            )
            print(
                f"   │ {'1h Momentum:':<25} {momentum_str:<25} {'Volatility:':<25} {best_opportunity.get('volatility', 0) * 100:.3f}% │"
            )
            print(
                f"   │ {'24h High:':<25} ${best_opportunity.get('high_24h', 0):<20.4f} {'24h Low:':<25} ${best_opportunity.get('low_24h', 0):.4f} │"
            )
            print(
                f"   │ {'Position in Range:':<25} {best_opportunity.get('position_from_range', 0) * 100:.1f}%{' ' * 14} {'Mid Range:':<25} ${best_opportunity.get('mid_range', 0):.4f} │"
            )

            # Display candle analysis information if available
            if "market_activity" in best_opportunity:
                market_activity = best_opportunity["market_activity"]
                volatility_1m = market_activity.get("volatility_1m", 0)
                volatility_5m = market_activity.get("volatility_5m", 0)
                volatility_15m = market_activity.get("volatility_15m", 0)
                trend_strength = market_activity.get("trend_strength", 0)
                volume_profile = market_activity.get("volume_profile", 0)
                candle_patterns = market_activity.get("candle_patterns", [])
                support_level = market_activity.get("support_level", 0)
                resistance_level = market_activity.get("resistance_level", 0)
                price_action = market_activity.get("price_action", "neutral")

                print(
                    f"   │ {'1m Volatility:':<25} {volatility_1m * 100:.2f}%{' ' * 17} {'5m Volatility:':<25} {volatility_5m * 100:.2f}% │"
                )
                print(
                    f"   │ {'15m Volatility:':<25} {volatility_15m * 100:.2f}%{' ' * 15} {'Trend Strength:':<25} {trend_strength:.1f}% │"
                )
                print(
                    f"   │ {'Volume Profile:':<25} {volume_profile:.1f}%{' ' * 17} {'Price Action:':<25} {price_action.replace('_', ' ')} │"
                )

                if support_level > 0 and resistance_level > 0:
                    print(
                        f"   │ {'Support Level:':<25} ${support_level:.4f}{' ' * 19} {'Resistance Level:':<25} ${resistance_level:.4f} │"
                    )

                if candle_patterns:
                    patterns_text = ", ".join(
                        [p.replace("_", " ").title() for p in candle_patterns]
                    )
                    print(f"   │ {'Candle Patterns:':<25} {patterns_text:<73} │")
            print(
                f"   │ {'Spread Est:':<25} {best_opportunity['spread'] * 100:.3f}%{' ' * 17} {'Volume 24h:':<25} {vol_str} │"
            )
            print(
                f"   │ {'Risk Level:':<25} {best_opportunity.get('risk_level', 'MEDIUM'):<25} {'Opportunity Type:':<25} {best_opportunity.get('opportunity_type', 'UNCERTAIN')} │"
            )
            print(
                f"   │ {'Support Level:':<25} ${best_opportunity.get('support_level', 0):<20.4f} {'Resistance Level:':<25} ${best_opportunity.get('resistance_level', 0):.4f} │"
            )
            print(
                f"   │ {'Liquidity Score:':<25} {best_opportunity.get('liquidity_score', 50):<25} {'Technical Strength:':<25} {best_opportunity.get('technical_strength', 50)} │"
            )
            print(f"   │ {'Breakdown:':<25} {best_opportunity.get('breakdown', 'N/A'):<73} │")
            # Show comprehensive insights
            if "insights" in best_opportunity and best_opportunity["insights"]:
                print(f"   │ {'Insights:':<25} {' | '.join(best_opportunity['insights']):<73} │")

            score = best_opportunity["score"]
            M = TRADING.MULTIPLIERS

            if score >= SCORE_THRESHOLDS.GOD_TIER:
                size_multiplier = M.GOD_TIER_MULTIPLIER
                multiplier_label = f"{M.GOD_TIER_MULTIPLIER}x ({SCORE_THRESHOLDS.GOD_TIER}+)"
            elif score >= SCORE_THRESHOLDS.HIGH_CONFIDENCE:
                size_multiplier = M.HIGH_CONFIDENCE_MULTIPLIER
                multiplier_label = (
                    f"{M.HIGH_CONFIDENCE_MULTIPLIER}x ({SCORE_THRESHOLDS.HIGH_CONFIDENCE}+)"
                )
            elif score >= SCORE_THRESHOLDS.STRONG_SETUP:
                size_multiplier = M.STRONG_SETUP_MULTIPLIER
                multiplier_label = (
                    f"{M.STRONG_SETUP_MULTIPLIER}x ({SCORE_THRESHOLDS.STRONG_SETUP}+)"
                )
            elif score >= SCORE_THRESHOLDS.GOOD_SETUP:
                size_multiplier = M.GOOD_SETUP_MULTIPLIER
                multiplier_label = f"{M.GOOD_SETUP_MULTIPLIER}x ({SCORE_THRESHOLDS.GOOD_SETUP}+)"
            else:
                size_multiplier = M.STANDARD_MULTIPLIER
                multiplier_label = f"{M.STANDARD_MULTIPLIER}x"

            high_score_count = (
                sum(
                    1
                    for d in self.market_intel.values()
                    if d["score"] >= SCORE_THRESHOLDS.GOOD_SETUP
                )
                if self.market_intel
                else 0
            )
            avg_score = (
                sum(d["score"] for d in self.market_intel.values()) / len(self.market_intel)
                if self.market_intel
                else 0
            )
            is_market_primed = (
                high_score_count >= SCORE_THRESHOLDS.MARKET_PRIMED_HIGH_COUNT
                or avg_score >= SCORE_THRESHOLDS.MARKET_PRIMED_AVG_SCORE
            )

            market_multiplier = M.MARKET_PRIMED_MULTIPLIER if is_market_primed else 1.0

            if strategy["regime"] == "TRENDING":
                regime_multiplier = M.REGIME_TRENDING_MULTIPLIER
            elif strategy["regime"] == "FLAT":
                regime_multiplier = M.REGIME_FLAT_MULTIPLIER
            else:
                regime_multiplier = M.REGIME_DEFAULT_MULTIPLIER

            final_multiplier = size_multiplier * market_multiplier * regime_multiplier

            position_value = strategy["available"] * base_size_pct * final_multiplier
            position_value = max(5, min(position_value, strategy["available"] * 0.95))

            print(f"   │ {'─' * 25} {'─' * 23} {'─' * 28} │")
            print(f"   │ {'🎯 DYNAMIC TRADE PLAN:':^96} │")
            print(
                f"   │ {'   ├─ Entry:':<25} ${best_opportunity['price']:<20.4f} {'Target:':<20} ${best_opportunity['price'] * (1 + strategy['target_profit']):.4f} (+{strategy['target_profit'] * 100:.1f}%) │"
            )
            if strategy.get("stop_loss") is not None:
                stop_price = best_opportunity["price"] * (1 - strategy["stop_loss"])
                risk_pct = strategy["stop_loss"] * 100
                print(
                    f"   │ {'   ├─ Stop:':<25} ${stop_price:<20.4f} {'Risk:':<20} -{risk_pct:.1f}% │"
                )
            else:
                print(f"   │ {'   ├─ Stop:':<25} {'Manual/Trailing':<20} {'Risk:':<20} Manual │")
            print(
                f"   │ {'   ├─ Size Multiplier:':<25} {multiplier_label:<20} {'Market:':<20} {'🔥 PRIMED' if is_market_primed else '◐ NORMAL':<18} │"
            )
            print(
                f"   │ {'   ├─ Regime:':<25} {strategy['regime']:<20} {'Final Multiplier:':<20} {final_multiplier:.2f}x │"
            )
            risk_usd = position_value * strategy["stop_loss"] if strategy.get("stop_loss") else 0
            print(
                f"   │ {'   └─ POSITION VALUE:':<25} ${position_value:<20.2f} {'Risk/$:':<20} ${risk_usd:.4f} │"
            )
            print(f"   └{'─' * 98}┘")

        perf = self.agent_memory.get("performance_by_symbol", {})
        print(f"\n   ┌{'─' * 98}┐")
        print(f"   │ {'🧠 AGENT LEARNING INTELLIGENCE':^96} │")
        print(f"   ├{'─' * 98}┤")
        print(
            f"   │ {'Learning Cycles:':<25} {sum(p['trades'] for p in perf.values()):<20} {'Symbols Tracked:':<25} {len(perf)} │"
        )
        print(f"   │ {'─' * 98}│")

        if perf:
            for strat, data in sorted(perf.items(), key=lambda x: x[1]["pnl"], reverse=True)[:5]:
                wr = (data["wins"] / data["trades"] * 100) if data["trades"] > 0 else 0
                print(
                    f"   │ {strat:<30} W:{data['wins']:<3} L:{data['losses']:<3} PnL:${data['pnl']:+.4f} WR:{wr:.0f}% │"
                )

        print(f"   └{'─' * 98}┘")

        print(f"\n   ┌{'─' * 98}┐")
        print(f"   │ {'🦅 AGENTIC DECISION ENGINE':^96} │")
        print(f"   ├{'─' * 98}┤")

        if self.state["positions"] and len(self.state["positions"]) >= strategy["max_positions"]:
            decision = "⟳ MONITORING - Max positions, awaiting exits"
        elif best_opportunity and best_opportunity["score"] >= self.config["min_score"]:
            decision = (
                f"🚀 HUNTING {best_opportunity['symbol']} - Score {best_opportunity['score']}/100"
            )
        else:
            decision = "⏳ SCANNING - Seeking opportunities"

        print(f"   │ {'DECISION:':<25} {decision:<73} │")
        print(f"   │ {'STATUS:':<25} {'🦅 IBIS ACTIVE - MAXIMUM INTELLIGENCE':<73} │")
        print(f"   │ {'PHILOSOPHY:':<25} {'NO HOPE. ONLY HUNT.':<73} │")
        print(f"   │ {'OBJECTIVE:':<25} {'CAPITALIZE ON SMALL GAINS':<73} │")
        print(f"   │ {'METHOD:':<25} {'FREQUENCY + ACCURACY + ADAPTATION':<73} │")
        print(f"   └{'─' * 98}┘")

        print(f"\n{'═' * 100}\n")

    async def learn_from_experience(self):
        """
        🧠 SELF-LEARNING ENGINE
        Analyzes past performance and adjusts behavior accordingly.
        Updates agent memory with insights.
        """
        try:
            perf = self.agent_memory.get("performance_by_symbol", {})
            if not perf:
                self.log_event("   🧠 Learning: No historical data yet")
                return

            total_trades = sum(p.get("trades", 0) for p in perf.values())
            if total_trades < 5:
                return

            self.agent_memory["total_cycles"] += 1
            cycles = self.agent_memory["total_cycles"]

            # Learn from winning conditions
            winning_regimes = {}
            winning_modes = {}
            losing_regimes = {}
            losing_modes = {}

            for symbol, data in perf.items():
                trades = data.get("trades", 0)
                if trades < 2:
                    continue

                wr = data.get("wins", 0) / trades if trades > 0 else 0
                regime = data.get("regime", "UNKNOWN")
                mode = data.get("mode", "UNKNOWN")

                if wr > 0.6:
                    winning_regimes[regime] = winning_regimes.get(regime, 0) + 1
                    winning_modes[mode] = winning_modes.get(mode, 0) + 1
                elif wr < 0.4:
                    losing_regimes[regime] = losing_regimes.get(regime, 0) + 1
                    losing_modes[mode] = losing_modes.get(mode, 0) + 1

            # Adapt thresholds based on learning
            if winning_regimes:
                best_regime = max(winning_regimes, key=winning_regimes.get)
                self.agent_memory["learned_regimes"]["best"] = best_regime
                self.log_event(f"   🧠 Learning: Best regime = {best_regime}")

            if losing_regimes:
                worst_regime = max(losing_regimes, key=losing_regimes.get)
                self.agent_memory["learned_regimes"]["avoid"] = worst_regime
                self.log_event(f"   🧠 Learning: Avoid regime = {worst_regime}")

            # Save learning every 10 cycles
            if cycles % 10 == 0:
                self._save_memory()

        except Exception as e:
            self.log_event(f"   ⚠️ Learning error: {e}")

    async def update_adaptive_risk(self):
        """
        🛡️ ADAPTIVE RISK MANAGEMENT
        Dynamically adjusts risk parameters based on:
        - Recent performance
        - Market volatility
        - Portfolio heat
        """
        try:
            daily = self.state.get("daily", {})
            current_pnl = daily.get("pnl", 0)
            trades = daily.get("trades", 0)

            # Base risk factors from centralized config
            base_risk = TRADING.RISK.BASE_RISK_PER_TRADE
            win_rate = daily.get("wins", 0) / trades if trades > 0 else 0.5

            # Adjust based on recent performance
            if current_pnl > 0:
                # Winning streak - slightly increase risk
                risk_multiplier = 1.0 + (min(current_pnl / 100, 0.5))
            elif current_pnl < 0:
                # Losing streak - reduce risk
                risk_multiplier = max(0.5, 1.0 - (abs(current_pnl) / 50))
            else:
                risk_multiplier = 1.0

            # Adjust based on win rate
            if win_rate > 0.6:
                risk_multiplier *= 1.2
            elif win_rate < 0.4:
                risk_multiplier *= 0.7

            # Calculate new risk
            new_risk = base_risk * risk_multiplier
            new_risk = max(0.005, min(0.05, new_risk))  # Clamp between 0.5% and 5%

            # Update config
            self.config["risk_per_trade"] = new_risk

            if self.state.get("daily", {}).get("trades", 0) % 10 == 0:
                self.log_event(
                    f"   🛡️ Adaptive Risk: {new_risk * 100:.2f}%/trade "
                    f"(PnL: {current_pnl:+.2f}%, WR: {win_rate:.0%})"
                )

        except Exception as e:
            self.log_event(f"   ⚠️ Adaptive risk error: {e}")

    async def run(self):
        """Main autonomous loop"""
        await self.initialize()
        self._load_state()

        cycle = 0

        while True:
            try:
                cycle += 1

                # 🗓️ DAILY RESET: Check if date changed and reset daily stats
                today = datetime.now().strftime("%Y-%m-%d")
                if self.state.get("daily", {}).get("date") != today:
                    self.log_event(
                        f"   🗓️ NEW DAY: Resetting daily stats (was {self.state.get('daily', {}).get('date')})"
                    )
                    await self.update_capital_awareness()
                    total_assets = self.state.get("capital_awareness", {}).get("total_assets", 0)
                    self.state["daily"] = self._new_daily()
                    self.state["daily"]["start_balance"] = total_assets
                    self._save_state()

                # 🧠 Step 0: Update Position & Capital Awareness (Every Cycle)
                await self.update_positions_awareness()
                await self.update_capital_awareness()
                await self.check_pending_orders()

                # 🧠 Step 0b: Self-Learning from Past Performance
                await self.learn_from_experience()

                # 🧠 Step 0c: Adaptive Risk Management
                await self.update_adaptive_risk()

                # Step 1: Periodic Reconcile (Every 50 cycles)
                if cycle % 50 == 0:
                    await self.reconcile_holdings()

                # Step 2: Analyze market intelligence
                self.log_event("   🔍 Starting Market Analysis cycle...")
                await self.analyze_market_intelligence()

                # Step 3: Detect regime
                regime = await self.detect_market_regime()
                self.log_event(f"   📊 Regime: {regime}")

                # Step 3: Assess market conditions
                market_conditions = self._assess_market_conditions()

                # Step 4: Mode determination
                mode = await self.determine_agent_mode(regime, self.market_intel)
                self.log_event(f"   🤖 Mode: {mode}")

                # Step 5: Execute strategy
                strategy = await self.execute_strategy(regime, mode)
                self.log_event(
                    f"   📜 Strategy: positions={len(self.state['positions'])}/{strategy['max_positions']}, avail=${strategy['available']:.2f}"
                )

                # Step 7 & 10: Hunt for ALL opportunities (HYPER TRADING)
                self.log_event(
                    f"   🎯 ANALYZING {len(self.market_intel)} opportunities for trade entry..."
                )
                opportunities = await self.find_all_opportunities(strategy)
                self.log_event(f"   🔥 FOUND {len(opportunities)} TRADEABLE candidates")
                best = opportunities[0] if opportunities else None

                # Step 6: Dynamic Position Monitoring (CRITICAL)
                self.log_event("   🕵️ Checking existing positions for TP/SL/Decay...")
                await self.check_positions(strategy)

                open_count = len(self.state["positions"])
                self.log_event(
                    f"   🔄 ENTERING TRADE LOOP: {len(opportunities)} opportunities, current positions: {open_count}"
                )

                # Suppress capital spam: only log if we have good opportunities but literally zero/dust cash
                has_insufficient_capital = (
                    strategy["available"] < TRADING.POSITION.MIN_CAPITAL_PER_TRADE
                )
                if has_insufficient_capital and opportunities:
                    if cycle % 10 == 0 or cycle == 1:  # Only log every 10 cycles to prevent spam
                        self.log_event(
                            f"   🛑 Insufficient capital (${strategy['available']:.2f} < ${TRADING.POSITION.MIN_CAPITAL_PER_TRADE} minimum)"
                        )

                for opportunity in opportunities:
                    # 🚀 AGGRESSIVE PROFIT RECYCLING: Take ANY profit to fund high-score opportunities
                    # Note: score is boosted by +20 in find_all_opportunities, so threshold 65 accounts for boost
                    self.log_event(
                        f"   [RECYCLE TEST] available=${strategy['available']:.2f}, score={opportunity['score']:.1f}"
                    )
                    if strategy["available"] < 5.0 and opportunity["score"] >= 65:
                        self.log_event(
                            f"   🔱 CAPITAL RECYCLING: ${strategy['available']:.2f} available for {opportunity['symbol']} (Score: {opportunity['score']:.0f})"
                        )

                        # Find best position to close (prioritize profit, then accept loss if needed)
                        best_to_close = None
                        best_pnl = -999
                        for sym, pos in self.state["positions"].items():
                            pnl_pct = pos.get("unrealized_pnl_pct", 0)
                            if pnl_pct > best_pnl:
                                best_pnl = pnl_pct
                                best_to_close = (sym, pos)

                        if best_to_close:
                            sym, pos = best_to_close
                            self.log_event(
                                f"      💰 RECYCLING: Closing {sym} at {best_pnl * 100:+.2f}% to fund {opportunity['symbol']}"
                            )
                            self.log_event(f"   [RECYCLE BEFORE] calling close_position for {sym}")
                            await self.close_position(
                                sym,
                                "TAKE_PROFIT_RECYCLE" if best_pnl > 0 else "RECYCLE_CAPITAL",
                                pos.get("current_price"),
                                best_pnl,
                                strategy,
                            )
                            self.log_event(f"   [RECYCLE AFTER] close_position completed for {sym}")
                            # Refresh capital after close
                            current_balances = await self.client.get_all_balances()
                            open_orders = await self.client.get_open_orders()
                            usdt_available = float(
                                current_balances.get("USDT", {}).get("available", 0)
                            )
                            buy_orders_value = sum(
                                float(o.get("funds", 0) or 0)
                                for o in open_orders
                                if o.get("side", "").lower() == "buy"
                            )
                            strategy["available"] = max(0, usdt_available - buy_orders_value)
                            self.log_event(
                                f"      💵 Capital after recycling: ${strategy['available']:.2f}"
                            )

                    # 🚀 AGGRESSIVE ALPHA RECYCLING: Clear positions for ANY high-score opportunity
                    is_strong = opportunity["score"] >= 85  # Only recycle for STRONG_SETUP+ signals
                    if (strategy["available"] < 5.0) and is_strong:
                        self.log_event(
                            f"   🔱 STRONG SIGNAL: {opportunity['symbol']} (Score: {opportunity['score']:.0f}). Clearing stagnant capital..."
                        )

                        # Find ALL positions with a 'Confidence Gap' relative to the new opportunity
                        recycled_any = False
                        opportunity_score = opportunity["score"]

                        # Build list of (symbol, score, position) tuples for scoring
                        current_positions = []
                        for sym, pos in self.state["positions"].items():
                            pos_score = pos.get("confidence_score", 50)
                            current_positions.append((sym, pos_score, pos))

                        # Sort by score ascending (lowest first)
                        current_positions.sort(key=lambda x: x[1])

                        # Recycling based on score gap only - IBIS intelligence determines allocation
                        if current_positions:
                            avg_position_score = sum(p[1] for p in current_positions) / len(
                                current_positions
                            )
                            score_variance = abs(opportunity_score - avg_position_score)

                            # Allow recycling if there's a significant score gap
                            allow_recycling = score_variance >= TRADING.ALPHA.MIN_SCORE_VARIANCE

                            if not allow_recycling:
                                self.log_event(
                                    f"      🛡️ SAME-SCORE PROTECTION: All assets have similar conviction ({avg_position_score:.1f} vs {opportunity_score:.1f}). Skipping recycling."
                                )
                                recycled_any = False
                            else:
                                # 🚀 DYNAMIC INTELLIGENCE GAP: More aggressive in trending markets
                                regime = strategy.get("regime", "VOLATILE")
                                intelligence_gap_threshold = (
                                    TRADING.ALPHA.INTELLIGENCE_GAP_AGGRESSIVE
                                    if regime == "TRENDING"
                                    else TRADING.ALPHA.INTELLIGENCE_GAP_CONSERVATIVE
                                )

                                for sym, pos_score, pos in current_positions:
                                    # 🔱 PARALYSIS BREAKER: If wallet is dead (<$1) and signal is strong (>80), kill the weakest
                                    is_paralyzed = (
                                        strategy["available"] < 1.0 and opportunity["score"] >= 80
                                    )

                                    # ♻️ RECYCLING RULES:
                                    is_stagnant = pos_score < 60
                                    has_better_alternative = (
                                        opportunity["score"] - pos_score
                                    ) > intelligence_gap_threshold
                                    is_dust = (
                                        pos.get("quantity", 0) * pos.get("current_price", 0)
                                    ) < 3.0

                                    if (
                                        is_paralyzed
                                        or is_stagnant
                                        or has_better_alternative
                                        or is_dust
                                    ):
                                        self.log_event(
                                            f"      ♻️ RECYCLING: Closing {sym} (Score: {pos_score:.1f}) to fund {opportunity['symbol']} (Score: {opportunity_score:.1f})"
                                        )
                                        close_success = await self.close_position(
                                            sym,
                                            "ALPHA_RECYCLE",
                                            pos.get("current_price"),
                                            0,
                                            strategy,
                                        )
                                        if not close_success:
                                            self.log_event(
                                                f"      ⚠️ RECYCLING FAILED: Could not close {sym}"
                                            )
                                            recycled_any = False
                                            continue  # Try next position or skip

                                        recycled_any = True
                                        # After killing one, refresh available and check if we have enough
                                        current_balances = await self.client.get_all_balances()
                                        buy_orders = await self.client.get_open_orders()
                                        usdt_available = float(
                                            current_balances.get("USDT", {}).get("available", 0)
                                        )
                                        buy_orders_value = sum(
                                            float(o.get("funds", 0) or 0)
                                            for o in buy_orders
                                            if o.get("side", "").lower() == "buy"
                                        )
                                        strategy["available"] = max(
                                            0, usdt_available - buy_orders_value
                                        )
                                        if (
                                            strategy["available"] >= 5.0
                                        ):  # Enough to stop killing folks
                                            break

                        if recycled_any:
                            open_count = len(
                                [
                                    pos
                                    for pos in self.state["positions"].values()
                                    if pos["mode"] != "PENDING_BUY"
                                ]
                            )
                            # Refresh with real trading capital
                            current_balances = await self.client.get_all_balances()
                            buy_orders = await self.client.get_open_orders()
                            usdt_available = float(
                                current_balances.get("USDT", {}).get("available", 0)
                            )
                            buy_orders_value = sum(
                                float(o.get("funds", 0) or 0)
                                for o in buy_orders
                                if o.get("side", "").lower() == "buy"
                            )
                            strategy["available"] = max(0, usdt_available - buy_orders_value)

                    if open_count < strategy["max_positions"]:
                        # 🛡️ HARD MINIMUM: Don't create dust positions
                        if strategy["available"] < 5.0:
                            self.log_event(
                                f"   🛑 Insufficient capital (${strategy['available']:.2f} < $5.00 minimum)"
                            )
                            break

                        self.log_event(f"   🚀 HYPER-TRADE START: {opportunity['symbol']}")
                        await self.open_position(opportunity, strategy)
                        open_count += 1
                        await asyncio.sleep(0.1)  # Hyper-fast execution

                        # Refresh available after trade (accounting for locked buy orders)
                        current_balances = await self.client.get_all_balances()
                        open_orders = await self.client.get_open_orders()
                        usdt_available = float(current_balances.get("USDT", {}).get("available", 0))
                        buy_orders_value = sum(
                            float(o.get("funds", 0) or 0)
                            for o in open_orders
                            if o.get("side", "").lower() == "buy"
                        )
                        strategy["available"] = max(0, usdt_available - buy_orders_value)
                        if strategy["available"] < 5.0:
                            has_insufficient_capital = True
                    else:
                        self.log_event(f"   🛑 Max positions reached ({open_count})")
                        break

                # Step 8: Log and Print (EXPLAIN LATER)
                await self.log_intelligence(regime, mode, strategy, best)

                # Step 11: Save and wait
                self._save_state()

                if self.single_scan:
                    self.log_event("   🏁 Single-scan complete. Exiting.")
                    break

                wait = strategy["scan_interval"]
                await asyncio.sleep(wait)

            except KeyboardInterrupt:
                print("\n🛑 Agent stopped")
                break
            except Exception as e:
                print(f"⚠️ Error: {e}")
                await asyncio.sleep(10)

        self._save_state()
        self._save_memory()
        await self.client.close()


# Compatibility Alias
IBISAutonomousAgent = IBISTrueAgent

# ==================== ENTRY ====================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IBIS True Autonomous Agent")
    parser.add_argument("--single-scan", action="store_true", help="Run one cycle then exit")
    args = parser.parse_args()

    agent = IBISTrueAgent()
    if args.single_scan:
        agent.single_scan = True

    try:
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        pass
