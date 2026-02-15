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
from decimal import Decimal, ROUND_DOWN, ROUND_UP, InvalidOperation
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
from ibis.pnl_tracker import PnLTracker
from ibis.brain.agi_brain import get_agi_brain, MarketContext
from ibis.intelligence.enhanced_sniping import (
    score_snipe_opportunity,
    calculate_price_action_score,
    detect_breakout,
    calculate_volume_momentum,
    predict_upward_move,
)
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
    """Round down to nearest increment using Decimal-safe math."""
    if increment is None or increment <= 0:
        return float(qty)
    try:
        qty_d = Decimal(str(qty))
        inc_d = Decimal(str(increment))
        if inc_d <= 0:
            return float(qty_d)
        steps = (qty_d / inc_d).to_integral_value(rounding=ROUND_DOWN)
        return float(steps * inc_d)
    except (InvalidOperation, ValueError, TypeError) as e:
        print(f"⚠️ Round-down error: {e}")
        return float(qty)


def round_up_to_increment(qty: float, increment: float) -> float:
    """Round up to nearest increment using Decimal-safe math."""
    if increment is None or increment <= 0:
        return float(qty)
    try:
        qty_d = Decimal(str(qty))
        inc_d = Decimal(str(increment))
        if inc_d <= 0:
            return float(qty_d)
        steps = (qty_d / inc_d).to_integral_value(rounding=ROUND_UP)
        return float(steps * inc_d)
    except (InvalidOperation, ValueError, TypeError) as e:
        print(f"⚠️ Round-up error: {e}")
        return float(qty)


def format_decimal_for_increment(value: float, increment: float) -> float:
    """Format value to increment precision without scientific notation drift."""
    try:
        inc_d = Decimal(str(increment))
        val_d = Decimal(str(value))
        if inc_d <= 0:
            return float(val_d)
        decimals = max(0, -inc_d.as_tuple().exponent)
        quant = Decimal("1").scaleb(-decimals)
        return float(val_d.quantize(quant))
    except Exception as e:
        print(f"⚠️ Format error: {e}")
        return float(value)


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
        self._closing_symbols = set()

        self.state_file = (
            "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_true_state.json"
        )
        self.memory_file = (
            "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_true_memory.json"
        )

        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)

        import json as state_json
        import fcntl
        from ibis.database.db import IbisDB

        def _normalize_symbol(sym: str) -> str:
            return str(sym).replace("-USDT", "").replace("-USDC", "")

        def _sync_state_positions_to_db():
            """Mirror in-memory state positions into SQLite for monitor/reconciliation consistency."""
            try:
                lock_path = os.path.join(os.path.dirname(self.state_file), "ibis_db.lock")
                with open(lock_path, "w") as lock_f:
                    fcntl.flock(lock_f, fcntl.LOCK_EX)

                    db = IbisDB()
                    active_symbols = set()
                    for sym, pos in self.state.get("positions", {}).items():
                        db_sym = _normalize_symbol(sym)
                        active_symbols.add(db_sym)
                        qty = float(pos.get("quantity", 0) or 0)
                        entry = float(
                            pos.get("buy_price", 0)
                            or pos.get("entry_price", 0)
                            or pos.get("current_price", 0)
                            or 0
                        )
                        if qty <= 0 or entry <= 0:
                            continue
                        db.update_position(
                            symbol=db_sym,
                            quantity=qty,
                            price=entry,
                            stop_loss=pos.get("sl"),
                            take_profit=pos.get("tp"),
                            agi_score=pos.get("opportunity_score"),
                            agi_insight=pos.get("agi_insight"),
                            entry_fee=pos.get("fee"),
                        )

                    # Remove stale rows to keep DB aligned with live state.
                    with db.get_conn() as conn:
                        rows = conn.execute("SELECT symbol FROM positions").fetchall()
                        db_symbols = {str(r["symbol"]) for r in rows}
                        stale = db_symbols - active_symbols
                        for stale_sym in stale:
                            conn.execute("DELETE FROM positions WHERE symbol = ?", (stale_sym,))

                    fcntl.flock(lock_f, fcntl.LOCK_UN)
            except Exception as e:
                self.log_event(f"   ⚠️ DB position sync failed: {e}")

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
                tmp_memory_file = f"{self.memory_file}.tmp"
                with open(tmp_memory_file, "w") as f:
                    state_json.dump(self.agent_memory, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp_memory_file, self.memory_file)
            except:
                pass

        self._load_memory = _load_memory
        self._save_memory = _save_memory
        self.agent_memory = _load_memory()
        self.agent_memory.setdefault("fill_latency_by_symbol", {})
        self.agent_memory.setdefault("fill_latency_recent", [])
        self.agent_memory.setdefault("recycle_close_ts", {})
        self.agent_memory.setdefault("buy_reentry_cooldown_until", {})
        self.agent_memory.setdefault("stale_buy_cancel_counts", {})
        self.agent_memory.setdefault("stale_buy_last_cancel", {})
        self._last_db_sync_ts = 0.0
        self._symbol_fee_profile = {}
        self._symbol_fee_counts = {}
        self._last_fee_profile_refresh_ts = 0.0
        self._last_open_orders_log_sig = ""
        self._last_open_orders_log_ts = 0.0
        self._last_recycle_close_ts = self.agent_memory.get("recycle_close_ts", {}) or {}
        if not isinstance(self._last_recycle_close_ts, dict):
            self._last_recycle_close_ts = {}
            self.agent_memory["recycle_close_ts"] = self._last_recycle_close_ts
        self._recycle_closes_this_cycle = 0

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
                tmp_state_file = f"{self.state_file}.tmp"
                with open(tmp_state_file, "w") as f:
                    state_json.dump(state, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp_state_file, self.state_file)

                # Keep SQLite view fresh for monitors and reconciliations.
                now_ts = time.time()
                if now_ts - self._last_db_sync_ts >= 5:
                    _sync_state_positions_to_db()
                    self._last_db_sync_ts = now_ts
            except Exception as e:
                print(f"   ⚠️ State save error: {e}")
                pass

        def _save_state_immediate(self):
            """Force immediate state save after trades"""
            self._save_state()
            print(f"   💾 State saved at {datetime.now().strftime('%H:%M:%S')}")

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
            # Execution throughput controls (non-strategy layer)
            "maker_first_execution": True,
            "stale_buy_cancel_seconds": 60,
            "stale_buy_cancel_max_per_cycle": 6,
            "stale_buy_pressure_min_pending": 2,
            "stale_sell_reprice_seconds": 60,
            "stale_sell_hard_seconds": 180,
            "stale_sell_min_projected_profit_usdt": 0.02,
            "stale_reprice_cooldown_seconds": 45,
            "stale_reprice_max_per_cycle": 2,
            "take_profit_force_limit": True,
            "take_profit_limit_fallback_market": True,
            "take_profit_limit_wait_seconds": 2,
            "market_entry_score_threshold": 90,
            "market_entry_max_spread": 0.0035,
            "zombie_max_hold_minutes": 30,
            "zombie_stagnation_band_pct": 0.002,
            "zombie_max_evictions_per_cycle": 1,
            "zombie_prune_allow_loss": False,
            "zombie_prune_min_pnl_pct": 0.0,
            "zombie_prune_min_projected_profit_usdt": 0.02,
            "recycle_capital_trigger_usdt": TRADING.POSITION.MIN_CAPITAL_PER_TRADE,
            "recycle_min_projected_profit_usdt": 0.03,
            "recycle_min_projected_pnl_pct": 0.003,
            "reconcile_cycle_interval": 10,
            "fee_profile_history_limit": 400,
            "execution_fee_guard_enabled": True,
            "execution_fee_max_per_side": 0.0025,
            "execution_fee_override_score": 90,
            "execution_fee_min_symbol_fills": 4,
            "execution_fee_blocklist_max_symbols": 30,
            "latency_guard_enabled": True,
            "latency_guard_max_avg_fill_seconds": 75,
            "latency_guard_min_samples": 3,
            "latency_guard_override_score": 90,
            "max_open_buy_orders": 8,
            "stale_buy_pressure_relief_seconds": 45,
            "stale_buy_pressure_trigger": 4,
            "stale_buy_hard_seconds": 120,
            "stale_buy_reentry_cooldown_seconds": 75,
            "stale_buy_reentry_cooldown_max_seconds": 240,
            "stale_buy_reentry_price_window_seconds": 300,
            "stale_buy_reentry_price_improvement_bps": 8,
            "entry_admission_enabled": True,
            "entry_admission_min_edge": 45.0,
            "entry_admission_fee_penalty_points": 4000.0,
            "entry_admission_latency_penalty_cap": 10.0,
            "entry_admission_queue_penalty_cap": 6.0,
            "entry_admission_override_score": 90.0,
            "recycle_allow_loss": False,
            "recycle_min_pnl_pct": 0.003,
            "recycle_max_closes_per_cycle": 1,
            "recycle_symbol_cooldown_seconds": 300,
            "recycle_min_hold_seconds": 120,
            "recycle_requires_empty_buy_queue": True,
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
                "stale_buy_cancels": int(saved_daily.get("stale_buy_cancels", 0)),
                "avg_buy_fill_latency_seconds": float(
                    saved_daily.get("avg_buy_fill_latency_seconds", 0.0)
                ),
                "buy_fill_samples": int(saved_daily.get("buy_fill_samples", 0)),
                "avg_fill_rate": float(saved_daily.get("avg_fill_rate", 0.0)),
            }

        self.state = {
            "positions": validated_positions,
            "daily": daily,
            "market_regime": str(saved_state.get("market_regime", "unknown")),
            "agent_mode": str(saved_state.get("agent_mode", "MICRO_HUNTER")),
            "capital_awareness": default_capital,
            "execution_meta": dict(saved_state.get("execution_meta", {})),
        }

        if "last_sell_reprice" not in self.state["execution_meta"]:
            self.state["execution_meta"]["last_sell_reprice"] = {}

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
        self.pnl_tracker = PnLTracker()
        self.agi_brain = get_agi_brain()
        print("   ⚠️ Phase 1 Optimizer: DISABLED")
        print("   ⚠️ Enhanced Integration: DISABLED")
        print("   ✅ Enhanced Intel Streams: ACTIVE")
        print("   ✅ PnL Tracker: ACTIVE")
        print("   ✅ AGI Brain: ACTIVE")

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

    @staticmethod
    def _get_dynamic_tp_pct(score: int) -> float:
        """Dynamic TP percentage based on signal strength - using configuration constants"""
        from ibis.core.trading_constants import TRADING

        base_tp = TRADING.RISK.TAKE_PROFIT_PCT

        if score >= 95:  # God tier / Exceptional signal
            return 0.05  # 5.0% - Higher target for god tier
        elif score >= 90:  # High confidence / Excellent
            return 0.04  # 4.0%
        elif score >= 85:  # Strong setup / High quality
            return 0.035  # 3.5%
        elif score >= 80:  # Good opportunity / Quality
            return 0.03  # 3.0%
        elif score >= 75:  # Standard opportunity / Baseline
            return 0.025  # 2.5%
        else:  # Conservative - use configuration value
            return base_tp

    def validate_and_correct_positions(self):
        """🛡️ Validate positions and auto-correct TP/SL if they don't match configuration"""
        corrections_made = []
        expected_tp = TRADING.RISK.TAKE_PROFIT_PCT
        expected_sl = TRADING.RISK.STOP_LOSS_PCT

        for symbol, pos in list(self.state["positions"].items()):
            # Ensure highest_pnl exists for all positions
            if "highest_pnl" not in pos:
                pos["highest_pnl"] = 0
                pos["highest_pnl_display"] = "+0.00%"

            entry = pos.get("buy_price", 0)
            current_tp = pos.get("tp", 0)
            current_sl = pos.get("sl", 0)

            if entry <= 0:
                # Fix invalid entry price
                ticker = self.latest_tickers.get(symbol)
                if ticker:
                    pos["buy_price"] = float(ticker.price)
                    entry = pos["buy_price"]
                    self.log_event(
                        f"      🔧 FIXED: {symbol} entry price from $0.00 to ${entry:.6f}"
                    )

            if entry <= 0:
                continue

            # Calculate actual percentages
            actual_tp_pct = (current_tp - entry) / entry if current_tp > entry and entry > 0 else 0
            actual_sl_pct = (entry - current_sl) / entry if current_sl < entry and entry > 0 else 0

            # Check if correction is needed (with 0.1% tolerance)
            needs_correction = False
            new_tp = current_tp
            new_sl = current_sl

            # Always ensure TP/SL are calculated correctly for existing positions
            if abs(actual_tp_pct - expected_tp) > 0.001 or current_tp <= 0:
                new_tp = entry * (1 + expected_tp)
                needs_correction = True

            if abs(actual_sl_pct - expected_sl) > 0.001 or current_sl <= 0:
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
            "stale_buy_cancels": 0,
            "avg_buy_fill_latency_seconds": 0.0,
            "buy_fill_samples": 0,
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
                            # Handle both offset-aware and offset-naive datetime objects
                            if isinstance(opened, str):
                                # If opened is a string, parse it
                                try:
                                    opened = datetime.fromisoformat(opened.replace("Z", "+00:00"))
                                except:
                                    opened = datetime.now()
                            elif (
                                hasattr(opened, "tzinfo")
                                and opened.tzinfo is not None
                                and opened.tzinfo.utcoffset(opened) is not None
                            ):
                                # If opened is offset-aware, make now offset-aware in same timezone
                                now = datetime.now(opened.tzinfo)
                            else:
                                # If opened is naive, use naive datetime
                                now = datetime.now()
                            hold_seconds = (now - opened).total_seconds()
                        except (TypeError, ValueError) as e:
                            self.log_event(f"⚠️ Failed to parse timestamp for {pos['symbol']}: {e}")
                            hold_seconds = 0
                        except Exception as e:
                            self.log_event(
                                f"⚠️ Unexpected error parsing timestamp for {pos['symbol']}: {e}"
                            )
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

            # Throttle repeated open-order logs to reduce noise.
            now_ts = time.time()
            if open_orders:
                summary_parts = []
                for o in open_orders[:5]:
                    if hasattr(o, "symbol") and not isinstance(o, dict):
                        oid = str(getattr(o, "order_id", "") or "")
                        sym = str(getattr(o, "symbol", "") or "")
                        side = str(getattr(o, "side", "") or "")
                        status = str(getattr(o, "status", "") or "")
                    else:
                        oid = str(o.get("id", "") or o.get("orderId", "") or "")
                        sym = str(o.get("symbol", "") or "")
                        side = str(o.get("side", "") or "")
                        status = "ACTIVE" if o.get("isActive", True) else "DONE"
                    summary_parts.append(f"{sym}:{side}:{status}:{oid}")
                open_sig = f"open:{len(open_orders)}|" + "|".join(summary_parts)
            else:
                open_sig = "open:0"

            should_log_orders = (
                open_sig != getattr(self, "_last_open_orders_log_sig", "")
                or (now_ts - getattr(self, "_last_open_orders_log_ts", 0.0)) >= 60
            )
            if should_log_orders:
                if open_orders:
                    self.log_event(f"🔍 Found {len(open_orders)} open orders")
                    for o in open_orders[:3]:
                        if hasattr(o, "symbol") and not isinstance(o, dict):
                            side = getattr(o, "side", "N/A")
                            self.log_event(
                                f"   Order: {o.symbol} side='{side}' size={o.size} price={o.price}"
                            )
                        else:
                            sym = o.get("symbol", "N/A")
                            side = o.get("side", "N/A")
                            size = o.get("size", "0")
                            price = o.get("price", "0")
                            oid = o.get("id", "") or o.get("orderId", "") or "N/A"
                            self.log_event(
                                f"   Order: {sym} side='{side}' size={size} price={price} id={oid}"
                            )
                else:
                    self.log_event("🔍 No open orders found")
                self._last_open_orders_log_sig = open_sig
                self._last_open_orders_log_ts = now_ts

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
                    order_id = ""
                    if hasattr(order, "order_id") and not isinstance(order, dict):
                        order_id = str(getattr(order, "order_id", "") or "")
                    else:
                        order_id = str(order.get("id", "") or order.get("orderId", "") or "")
                    buy_orders["buy"][order_symbol] = {
                        "order_id": order_id,
                        "price": order_price,
                        "size": order_size,
                        "funds": order_funds,
                        "symbol": order_symbol,
                    }
                elif order_side == "sell":
                    sell_orders_value += order_size * order_price
                    order_id = ""
                    created_at = 0
                    if hasattr(order, "order_id") and not isinstance(order, dict):
                        order_id = str(getattr(order, "order_id", "") or "")
                        created_at = int(getattr(order, "created_at", 0) or 0)
                    else:
                        order_id = str(order.get("id", "") or order.get("orderId", "") or "")
                        try:
                            created_at = int(order.get("createdAt", 0) or 0)
                        except (TypeError, ValueError):
                            created_at = 0
                    if order_symbol not in buy_orders["sell"]:
                        buy_orders["sell"][order_symbol] = []
                    buy_orders["sell"][order_symbol].append(
                        {
                            "order_id": order_id,
                            "price": order_price,
                            "size": order_size,
                            "value": order_size * order_price,
                            "created_at": created_at,
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

            # `usdt_available` is already net of exchange-held funds for active buy orders.
            # Do not subtract buy orders again, otherwise deployable capital is understated.
            real_trading_capital = usdt_available

            daily_fees = self.state.get("daily", {}).get("fees", 0)

            # Reconcile pending buy_orders with actual active exchange buy orders.
            # This prevents duplicate entries after restarts and clears stale local-only pending orders.
            existing_buy_orders = self.state.get("capital_awareness", {}).get("buy_orders", {})
            reconciled_buy_orders = {}
            for sym, details in buy_orders["buy"].items():
                merged = dict(existing_buy_orders.get(sym, {}))
                merged.update(
                    {
                        "symbol": sym,
                        "order_id": details.get("order_id") or merged.get("order_id"),
                        "price": details.get("price", merged.get("price", 0)),
                        "quantity": details.get("size", merged.get("quantity", 0)),
                        "funds": details.get("funds", merged.get("funds", 0)),
                        "status": "pending",
                    }
                )
                reconciled_buy_orders[sym] = merged

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
                "buy_orders": reconciled_buy_orders,
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

    def _extract_order_side_and_funds(self, order) -> tuple[str, float]:
        """Normalize side/funds extraction for dict and TradeOrder objects."""
        if hasattr(order, "symbol") and not isinstance(order, dict):
            side = str(getattr(order, "side", "")).lower().strip()
            price = float(getattr(order, "price", 0) or 0)
            size = float(getattr(order, "size", 0) or 0)
            funds = float(getattr(order, "funds", 0) or 0) or (size * price)
            return side, funds

        side = str(order.get("side", "")).lower().strip()
        price = float(order.get("price", 0) or 0)
        size = float(order.get("size", 0) or 0)
        try:
            funds = float(order.get("funds", 0) or 0)
        except (TypeError, ValueError):
            funds = 0.0
        if funds <= 0 and price > 0 and size > 0:
            funds = size * price
        return side, funds

    async def _refresh_strategy_available(self, strategy: Dict, context: str = "") -> float:
        """Refresh deployable USDT from capital awareness without double-subtraction."""
        capital = await self.update_capital_awareness()
        deployable = float(capital.get("real_trading_capital", capital.get("usdt_available", 0)) or 0)
        strategy["available"] = max(0.0, deployable)
        if context:
            self.log_event(f"   💵 Capital refresh ({context}): ${strategy['available']:.2f}")
        return strategy["available"]

    def _load_symbol_fee_profile(self, force: bool = False) -> Dict[str, float]:
        """Build rolling fee-rate profile from recent fills: symbol -> fee_rate_per_side."""
        now_ts = time.time()
        if (
            not force
            and self._symbol_fee_profile
            and now_ts - self._last_fee_profile_refresh_ts < 60
        ):
            return self._symbol_fee_profile

        profile: Dict[str, float] = {}
        counts: Dict[str, int] = {}
        history_limit = int(self.config.get("fee_profile_history_limit", 400))
        trade_history_path = os.path.join(os.path.dirname(self.state_file), "trade_history.json")

        try:
            with open(trade_history_path, "r") as f:
                trade_obj = json.load(f)
            trades = trade_obj.get("trades", []) if isinstance(trade_obj, dict) else []
            recent = trades[-history_limit:] if history_limit > 0 else trades

            accum: Dict[str, Dict[str, float]] = {}
            for row in recent:
                symbol = (
                    str(row.get("symbol", "")).replace("-USDT", "").replace("-USDC", "").strip()
                )
                if not symbol:
                    continue
                try:
                    funds = float(row.get("funds", 0) or 0)
                    fee = float(row.get("fee", row.get("fees", 0)) or 0)
                except (TypeError, ValueError):
                    continue
                if funds <= 0 or fee < 0:
                    continue
                if symbol not in accum:
                    accum[symbol] = {"fee": 0.0, "funds": 0.0}
                    counts[symbol] = 0
                accum[symbol]["fee"] += fee
                accum[symbol]["funds"] += funds
                counts[symbol] += 1

            for sym, vals in accum.items():
                if vals["funds"] > 0:
                    profile[sym] = vals["fee"] / vals["funds"]
        except Exception:
            profile = {}
            counts = {}

        self._symbol_fee_profile = profile
        self._symbol_fee_counts = counts
        self._last_fee_profile_refresh_ts = now_ts
        return profile

    def _get_execution_fee_blocklist(self) -> set:
        """Symbols to avoid for execution efficiency based on observed fee pressure."""
        profile = self._load_symbol_fee_profile()
        min_fills = int(self.config.get("execution_fee_min_symbol_fills", 4))
        max_fee = float(self.config.get("execution_fee_max_per_side", 0.0025))
        cap = int(self.config.get("execution_fee_blocklist_max_symbols", 30))
        offenders = [
            (sym, rate)
            for sym, rate in profile.items()
            if self._symbol_fee_counts.get(sym, 0) >= min_fills and rate > max_fee
        ]
        offenders.sort(key=lambda x: x[1], reverse=True)
        return {sym for sym, _ in offenders[: max(0, cap)]}

    def _estimate_total_friction_for_symbol(self, symbol: str) -> float:
        """Estimate total round-trip friction with symbol-specific fee floor."""
        base = TRADING.get_total_friction()
        per_side = self._load_symbol_fee_profile().get(symbol, 0.0)
        if per_side <= 0:
            return base

        # Use symbol-observed fee pressure as floor while preserving baseline slippage estimate.
        observed_floor = (2 * per_side) + TRADING.EXCHANGE.ESTIMATED_SLIPPAGE
        return max(base, observed_floor)

    def _record_fill_latency(self, symbol: str, latency_seconds: float) -> None:
        """Track buy order fill latency per symbol for execution quality throttling."""
        if latency_seconds <= 0:
            return
        mem = self.agent_memory.setdefault("fill_latency_by_symbol", {})
        row = mem.get(symbol, {"samples": 0, "avg_seconds": 0.0, "ema_seconds": 0.0, "last_seconds": 0.0})
        prev_n = int(row.get("samples", 0))
        prev_avg = float(row.get("avg_seconds", 0.0))
        prev_ema = float(row.get("ema_seconds", 0.0))
        n = prev_n + 1
        avg = ((prev_avg * prev_n) + latency_seconds) / n
        alpha = 0.35
        ema = latency_seconds if prev_n == 0 else (alpha * latency_seconds + (1 - alpha) * prev_ema)
        row.update(
            {
                "samples": n,
                "avg_seconds": avg,
                "ema_seconds": ema,
                "last_seconds": latency_seconds,
                "updated": datetime.now().isoformat(),
            }
        )
        mem[symbol] = row

        recent = self.agent_memory.setdefault("fill_latency_recent", [])
        recent.append(
            {
                "symbol": symbol,
                "latency_seconds": round(latency_seconds, 3),
                "ts": datetime.now().isoformat(),
            }
        )
        if len(recent) > 200:
            del recent[:-200]

    def _get_slow_fill_symbols(self) -> set:
        """Symbols with repeatedly slow fills that should be throttled for execution quality."""
        if not self.config.get("latency_guard_enabled", True):
            return set()
        max_avg = float(self.config.get("latency_guard_max_avg_fill_seconds", 75))
        min_samples = int(self.config.get("latency_guard_min_samples", 3))
        mem = self.agent_memory.get("fill_latency_by_symbol", {}) or {}
        return {
            sym
            for sym, row in mem.items()
            if int(row.get("samples", 0)) >= min_samples
            and float(row.get("avg_seconds", 0)) > max_avg
        }

    def _estimate_entry_edge(self, opportunity: Dict, strategy: Dict) -> float:
        """Execution-only edge score used to prioritize admission order."""
        symbol = str(opportunity.get("symbol", ""))
        score = float(opportunity.get("score", 0))
        fee_rate = float(self._load_symbol_fee_profile().get(symbol, 0.0) or 0.0)
        fee_penalty_points = float(self.config.get("entry_admission_fee_penalty_points", 4000.0))
        fee_penalty = fee_rate * fee_penalty_points

        latency_row = self.agent_memory.get("fill_latency_by_symbol", {}).get(symbol, {}) or {}
        avg_fill_seconds = float(latency_row.get("avg_seconds", 0.0) or 0.0)
        latency_penalty_cap = float(self.config.get("entry_admission_latency_penalty_cap", 10.0))
        latency_penalty = min(latency_penalty_cap, avg_fill_seconds / 10.0)

        pending_buys = len(self.state.get("capital_awareness", {}).get("buy_orders", {}) or {})
        pending_limit = max(1, int(self.config.get("max_open_buy_orders", 8)))
        queue_ratio = min(1.0, pending_buys / pending_limit)
        queue_penalty_cap = float(self.config.get("entry_admission_queue_penalty_cap", 6.0))
        queue_penalty = queue_ratio * queue_penalty_cap

        spread = float(opportunity.get("spread", 0.0) or 0.0)
        spread_penalty = min(3.0, spread * 300.0)

        return score - fee_penalty - latency_penalty - queue_penalty - spread_penalty

    def _admission_rank_opportunities(self, opportunities: List[Dict], strategy: Dict) -> List[Dict]:
        """Sort/filter entry candidates by execution edge while keeping strategy score intact."""
        if not self.config.get("entry_admission_enabled", True) or not opportunities:
            return opportunities

        min_edge = float(self.config.get("entry_admission_min_edge", 45.0))
        override_score = float(self.config.get("entry_admission_override_score", 90.0))

        ranked = []
        for opp in opportunities:
            edge = self._estimate_entry_edge(opp, strategy)
            ranked.append((edge, opp))

        ranked.sort(key=lambda x: (x[0], x[1].get("score", 0)), reverse=True)
        filtered = []
        rejected = 0
        for edge, opp in ranked:
            score = float(opp.get("score", 0))
            if edge < min_edge and score < override_score:
                rejected += 1
                continue
            out = dict(opp)
            out["entry_edge"] = edge
            filtered.append(out)

        self.log_event(
            f"   🧭 ADMISSION: kept={len(filtered)}/{len(opportunities)} | rejected={rejected} | min_edge={min_edge:.1f}"
        )
        for opp in filtered[:5]:
            self.log_event(
                f"      🧭 EDGE {opp.get('symbol')}: edge={opp.get('entry_edge', 0):.2f}, score={opp.get('score', 0):.1f}"
            )
        return filtered

    @staticmethod
    def _is_recycle_reason(reason: str) -> bool:
        recycle_reasons = {
            "RECYCLE_CAPITAL",
            "TAKE_PROFIT_RECYCLE",
            "ALPHA_RECYCLE",
            "RECYCLE_PROFIT",
            "THROUGHPUT_ZOMBIE_PRUNE",
        }
        return str(reason) in recycle_reasons

    def _recycle_guard_check(self, symbol: str, reason: str) -> tuple:
        if not self._is_recycle_reason(reason):
            return True, ""

        max_closes = max(0, int(self.config.get("recycle_max_closes_per_cycle", 1)))
        if self._recycle_closes_this_cycle >= max_closes:
            return (
                False,
                f"cycle cap reached ({self._recycle_closes_this_cycle}/{max_closes})",
            )

        cooldown = max(0, int(self.config.get("recycle_symbol_cooldown_seconds", 300)))
        if cooldown <= 0:
            return True, ""

        last_ts = float(self._last_recycle_close_ts.get(symbol, 0) or 0)
        if last_ts <= 0:
            return True, ""

        age = time.time() - last_ts
        if age < cooldown:
            return False, f"symbol cooldown active ({age:.0f}s < {cooldown}s)"
        return True, ""

    def _position_hold_seconds(self, pos: Dict) -> float:
        opened_raw = (pos or {}).get("opened")
        if not opened_raw:
            return 0.0
        try:
            opened_dt = datetime.fromisoformat(str(opened_raw).replace("Z", "+00:00"))
            if opened_dt.tzinfo is not None:
                now_dt = datetime.now(opened_dt.tzinfo)
            else:
                now_dt = datetime.now()
            return max(0.0, (now_dt - opened_dt).total_seconds())
        except Exception:
            return 0.0

    def _record_recycle_close(self, symbol: str, reason: str) -> None:
        if not self._is_recycle_reason(reason):
            return
        self._recycle_closes_this_cycle += 1
        self._last_recycle_close_ts[symbol] = time.time()
        # Prevent unbounded growth in persisted memory.
        if len(self._last_recycle_close_ts) > 300:
            oldest = sorted(self._last_recycle_close_ts.items(), key=lambda x: x[1])[:50]
            for sym, _ in oldest:
                self._last_recycle_close_ts.pop(sym, None)
        self.agent_memory["recycle_close_ts"] = self._last_recycle_close_ts

    def _mark_buy_reentry_cooldown(self, symbol: str, seconds: int) -> None:
        cooldown_seconds = max(0, int(seconds))
        if cooldown_seconds <= 0:
            return
        now_ts = time.time()
        cooldown_map = self.agent_memory.setdefault("buy_reentry_cooldown_until", {})
        cooldown_map[symbol] = now_ts + cooldown_seconds
        # Keep cooldown map bounded.
        if len(cooldown_map) > 400:
            for sym, ts in sorted(cooldown_map.items(), key=lambda x: x[1])[:120]:
                if ts <= now_ts:
                    cooldown_map.pop(sym, None)

    def _get_buy_reentry_cooldown_remaining(self, symbol: str) -> float:
        cooldown_map = self.agent_memory.get("buy_reentry_cooldown_until", {}) or {}
        until_ts = float(cooldown_map.get(symbol, 0) or 0)
        if until_ts <= 0:
            return 0.0
        remaining = until_ts - time.time()
        if remaining <= 0:
            cooldown_map.pop(symbol, None)
            return 0.0
        return remaining

    def _next_stale_buy_reentry_cooldown(self, symbol: str) -> int:
        """Escalate reentry cooldown for symbols repeatedly canceled as stale."""
        base_seconds = max(0, int(self.config.get("stale_buy_reentry_cooldown_seconds", 75)))
        max_seconds = max(base_seconds, int(self.config.get("stale_buy_reentry_cooldown_max_seconds", 240)))
        counts = self.agent_memory.setdefault("stale_buy_cancel_counts", {})
        n = int(counts.get(symbol, 0) or 0) + 1
        counts[symbol] = n
        if n <= 1:
            return base_seconds
        if n == 2:
            return min(max_seconds, base_seconds * 2)
        return min(max_seconds, base_seconds * 3)

    def _reset_stale_buy_cancel_count(self, symbol: str) -> None:
        counts = self.agent_memory.setdefault("stale_buy_cancel_counts", {})
        if symbol in counts:
            counts.pop(symbol, None)

    def _record_stale_buy_cancel(self, symbol: str, reference_price: float) -> None:
        last = self.agent_memory.setdefault("stale_buy_last_cancel", {})
        last[symbol] = {
            "ts": time.time(),
            "price": float(reference_price or 0.0),
        }
        # Keep map bounded to avoid unbounded memory growth.
        if len(last) > 400:
            oldest = sorted(last.items(), key=lambda x: float((x[1] or {}).get("ts", 0)))[:120]
            for sym, _ in oldest:
                last.pop(sym, None)

    def _stale_reentry_price_guard(self, symbol: str, current_price: float) -> tuple:
        """
        Skip re-entry shortly after stale cancel unless price has improved enough.
        For buys, improvement means a lower price than previous canceled price.
        """
        last = self.agent_memory.get("stale_buy_last_cancel", {}) or {}
        row = last.get(symbol, {}) or {}
        ts = float(row.get("ts", 0) or 0)
        old_price = float(row.get("price", 0) or 0)
        if ts <= 0 or old_price <= 0 or current_price <= 0:
            return False, ""

        age = time.time() - ts
        window = max(0, int(self.config.get("stale_buy_reentry_price_window_seconds", 300)))
        if age > window:
            return False, ""

        improvement_bps = float(self.config.get("stale_buy_reentry_price_improvement_bps", 8))
        required_price = old_price * (1 - (improvement_bps / 10000.0))
        if current_price <= required_price:
            return False, ""

        return (
            True,
            f"price guard ({age:.0f}s/{window}s): current {current_price:.8f} > required {required_price:.8f}",
        )

    async def get_holdings_intelligence(self) -> Dict:
        """
        Returns comprehensive intelligence about current holdings.
        Used for decision making and opportunity scoring.
        """
        if "portfolio" not in self.state:
            await self.update_positions_awareness()
            self._save_state()
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
                    # Fix invalid entry price
                    if self.state["positions"][currency]["buy_price"] == 0.0:
                        ticker = self.latest_tickers.get(currency) or await self.client.get_ticker(
                            f"{currency}-USDT"
                        )
                        price = (
                            float(ticker.price)
                            if ticker
                            else self.state["positions"][currency]["current_price"]
                        )
                        self.log_event(
                            f"      🔧 FIXING {currency}: Buy price from $0.00 to ${price:.6f}"
                        )
                        self.state["positions"][currency]["buy_price"] = price
                        self.state["positions"][currency]["tp"] = price * (
                            1 + TRADING.RISK.TAKE_PROFIT_PCT
                        )
                        self.state["positions"][currency]["sl"] = price * (
                            1 - TRADING.RISK.STOP_LOSS_PCT
                        )

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

    async def sync_pnl_from_kucoin(self):
        """Sync PnL from actual KuCoin trade history"""
        try:
            self.log_event("   💰 Syncing PnL from KuCoin trade history...")

            # Fetch trades from KuCoin
            await self.pnl_tracker.sync_trades_from_kucoin(self.client)

            # Match trades FIFO
            self.pnl_tracker.match_trades_fifo()

            # Update state with trade-based PnL
            weekly = self.pnl_tracker.get_weekly_pnl()
            monthly = self.pnl_tracker.get_monthly_pnl()
            all_time = self.pnl_tracker.get_all_time_pnl()

            # Update daily stats from trade history
            self.state["daily"]["pnl"] = weekly["pnl"]
            self.state["daily"]["trades"] = weekly["trades"]
            self.state["daily"]["wins"] = weekly["wins"]
            self.state["daily"]["losses"] = weekly["losses"]

            self.log_event(
                f"   ✅ PnL Synced: Weekly ${weekly['pnl']:.2f} ({weekly['trades']} trades, "
                f"{weekly['wins']}W/{weekly['losses']}L) | Monthly ${monthly['pnl']:.2f}"
            )

            return weekly, monthly, all_time

        except Exception as e:
            self.log_event(f"   ⚠️ PnL sync failed: {e}")
            return None, None, None

    async def get_pnl_report(self, period: str = "weekly") -> Dict:
        """Get PnL report for specified period"""
        if period == "weekly":
            return self.pnl_tracker.get_weekly_pnl()
        elif period == "monthly":
            return self.pnl_tracker.get_monthly_pnl()
        else:
            return self.pnl_tracker.get_all_time_pnl()

    async def initialize(self):
        """Initialize the agent with basic setup"""
        self.log_file = "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_true.log"

        self.log_event("=" * 70)
        self.log_event("🦅 IBIS TRUE AUTONOMOUS AGENT v3.1")
        self.log_event("=" * 70)

        # Load state
        self._load_state()
        self.state["agent_mode"] = "HYPER_INTELLIGENT"

        # Initialize KuCoin client
        self.client = get_kucoin_client()
        if not self.client:
            raise Exception("Failed to initialize KuCoin client")

        # Initialize cross-exchange monitor (Binance)
        await self.cross_exchange.initialize()

        # Fetch symbol rules first
        await self.fetch_symbol_rules()

        # ALWAYS use real-time symbol discovery - NO CACHING!
        await self.discover_market()

        self.log_event(f"   📊 Discovered {len(self.symbols_cache)} trading pairs (REAL-TIME)")
        self.log_event(f"   📋 Loaded rules for {len(self.symbol_rules)} symbols")

        # Get actual balances
        balances = await self.client.get_all_balances()
        usdt_balance = float(balances.get("USDT", {}).get("balance", 0))
        usdt_available = float(balances.get("USDT", {}).get("available", 0))

        if self.state["daily"]["start_balance"] == 0:
            self.state["daily"]["start_balance"] = usdt_balance

        print(f"   💰 USDT Balance: ${usdt_balance:.2f} (avail: ${usdt_available:.2f})")
        print(f"   🎯 Agent Mode: HYPER_INTELLIGENT")
        print("=" * 70)

        # Use basic regime
        self.state["market_regime"] = "VOLATILE"
        print(f"   🌐 Market Regime: VOLATILE (default)")
        print("=" * 70)

    async def discover_market(self):
        """Dynamically discover ALL trading pairs - Filtered for intelligence"""

        self.symbol_rules = {}
        self.symbols_cache = []

        # Configurable filters from agent configuration
        self.stablecoins = self.config.get(
            "stablecoins", {"USDT", "USDC", "DAI", "TUSD", "USDP", "USD1", "USDY"}
        )
        # STABLE is tracked as a regular position, not excluded
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
                        "priceIncrement": float(sym.get("priceIncrement", 0.000001)),
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
                            "priceIncrement": float(sym.get("priceIncrement", 0.000001)),
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

        # Get Fear & Greed index early for scoring
        fg_score = 50
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

        # Enhanced symbol discovery and rapid screening - ALWAYS use fresh data
        min_liquidity = self.config.get("min_liquidity", 1000)
        potential_symbols = []

        log_event("   📊 Using REAL-TIME dynamic symbol discovery")
        for ticker_symbol, ticker in ticker_map.items():
            try:
                vol = float(getattr(ticker, "volume_24h", 0) or 0)
                if float(ticker.price) > 0 and vol >= min_liquidity:
                    potential_symbols.append(ticker_symbol)
            except:
                continue

        # Sort potential symbols by volume (descending) for priority analysis
        sorted_symbols = []
        volume_map = {}
        for sym in potential_symbols:
            try:
                ticker = ticker_map.get(sym)
                vol = float(getattr(ticker, "vol_24h", 0) or getattr(ticker, "volume_24h", 0) or 0)
                volume_map[sym] = vol
            except:
                continue

        # Sort by volume descending
        sorted_symbols = sorted(volume_map.items(), key=lambda x: x[1], reverse=True)
        potential_symbols = [sym for sym, vol in sorted_symbols]

        log_event(
            f"   🧠 IBIS identified {len(potential_symbols)} candidates (from {len(self.symbols_cache)})"
        )

        async def analyze_symbol(sym):
            try:
                ticker = ticker_map.get(sym)
                if not ticker:
                    return None

                price = float(ticker.price)
                change_24h = float(getattr(ticker, "change_24h", 0) or 0)
                volume_24h = float(
                    getattr(ticker, "vol_24h", 0) or getattr(ticker, "volume_24h", 0) or 0
                )

                # Get candle data
                try:
                    tasks = [
                        self.client.get_candles(f"{sym}-USDT", "1min", limit=61),
                        self.client.get_candles(f"{sym}-USDT", "5min", limit=24),
                        self.client.get_candles(f"{sym}-USDT", "15min", limit=16),
                    ]
                    results = await asyncio.gather(*tasks)
                    candles_1m, candles_5m, candles_15m = results
                except Exception as e:
                    return None

                candle_analysis = self._analyze_candles(candles_1m, candles_5m, candles_15m)

                # Extract closes and volumes from 1-minute candles
                closes = [candle.close for candle in candles_1m] if candles_1m else []
                volumes = [candle.volume for candle in candles_1m] if candles_1m else []

                high_24h = float(getattr(ticker, "high_24h", price * 1.01) or price * 1.01)
                low_24h = float(getattr(ticker, "low_24h", price * 0.99) or price * 0.99)
                volatility = (high_24h - low_24h) / price if high_24h > low_24h else 0.02

                momentum_1h = candle_analysis.get("momentum_1h", 0)
                momentum_1h_raw = candle_analysis.get("momentum_1h_raw", momentum_1h)
                momentum_15m = candle_analysis.get("momentum_15m", 0)
                momentum_5m = candle_analysis.get("momentum_5m", 0)
                volume_momentum = candle_analysis.get("volume_momentum", 0)
                momentum_confidence = candle_analysis.get("momentum_confidence", 0.0)
                # Calculate base score first
                base_score = self._calculate_technical_strength(momentum_1h, change_24h)
                indicator_composite = candle_analysis.get("composite_score", 50)
                momentum_mtf_score = max(
                    0,
                    min(
                        100,
                        50
                        + (momentum_5m * 6.0)
                        + (momentum_15m * 8.0)
                        + (momentum_1h_raw * 4.0),
                    ),
                )
                volume_momentum_score = max(0, min(100, 50 + (volume_momentum * 0.4)))
                blended_volume_score = max(
                    0, min(100, (volume_momentum_score * 0.65) + (self._calculate_liquidity_score(volume_24h) * 0.35))
                )

                # Create comprehensive symbol data for unified scoring
                symbol_data = {
                    "price": price,
                    "change_1h": momentum_1h,
                    "momentum_1h_raw": momentum_1h_raw,
                    "momentum_15m": momentum_15m,
                    "momentum_5m": momentum_5m,
                    "volume_momentum_1m": volume_momentum,
                    "change_24h": change_24h,
                    "change_7d": getattr(ticker, "change_7d", 0),
                    "volatility": volatility,
                    "volume_24h": volume_24h,
                    "volume_profile": {
                        "type": "accumulation" if volume_24h > 500000 else "normal",
                        "density": min(volume_24h / 1000000, 1),
                    },
                    "spread": min(volatility * 0.3, 0.02),
                    "market_correlation": 0.5,  # Default
                    "sentiment": {"score": fg_score, "source": "alternative.me", "confidence": 0.8},
                    "onchain": {"network_growth": 100, "active_addresses": 500, "hashrate": 1000},
                    "candle_analysis": candle_analysis,
                    "technical_score": base_score,
                    "agi_score": indicator_composite,
                    "mtf_score": momentum_mtf_score,
                    "volume_score": blended_volume_score,
                    "sentiment_score": fg_score,
                }

                # Calculate unified score
                from ibis.core.unified_scoring import unified_scorer

                unified_result = unified_scorer.calculate_unified_score(
                    technical_score=base_score,
                    agi_score=indicator_composite,
                    mtf_score=momentum_mtf_score,
                    volume_score=blended_volume_score,
                    sentiment_score=fg_score,
                    symbol=sym,
                    symbol_data=symbol_data,
                )

                # Calculate funnel score
                funnel_score = unified_scorer.calculate_funnel_score(symbol_data)

                # Calculate final score with funnel adjustment
                score = unified_result["score"] * (0.8 + (funnel_score / 500))

                # Get snipe score for comparison
                if len(closes) >= 10 and len(volumes) >= 10:
                    snipe_result = score_snipe_opportunity(
                        symbol=sym,
                        closes=closes,
                        volumes=volumes,
                        technical_score=base_score,
                        agi_score=indicator_composite,
                        mtf_score=momentum_mtf_score,
                        volume_24h=volume_24h,
                        fear_greed_index=fg_score,
                        momentum_1h=momentum_1h,
                        change_24h=change_24h,
                    )
                else:
                    snipe_result = {"final_score": 50, "tier": "STANDARD"}

                return {
                    "symbol": sym,
                    "price": price,
                    "current_price": price,
                    "change_24h": change_24h,
                    "momentum_1h": momentum_1h,
                    "momentum_1h_raw": momentum_1h_raw,
                    "momentum_15m": momentum_15m,
                    "momentum_5m": momentum_5m,
                    "volume_momentum": volume_momentum,
                    "momentum_confidence": momentum_confidence,
                    "momentum_mtf_score": momentum_mtf_score,
                    "volatility": volatility,
                    "volatility_1m": candle_analysis.get("volatility_1m", 0.02),
                    "volatility_5m": candle_analysis.get("volatility_5m", 0.02),
                    "volatility_15m": candle_analysis.get("volatility_15m", 0.02),
                    "spread": min(volatility * 0.3, 0.02),
                    "volume_24h": volume_24h,
                    "score": score,
                    "unified_score": unified_result["score"],
                    "unified_confidence": unified_result["confidence"],
                    "funnel_score": funnel_score,
                    "snipe_score": snipe_result,
                    "unified_intel": unified_result,
                    "enhanced_intel": candle_analysis,
                    "timestamp": datetime.now().isoformat(),
                    "risk_level": self._calculate_risk_level(volatility, score),
                    "candle_analysis": candle_analysis,
                    "agi_insight": f"Score: {score:.1f} | Confidence: {unified_result['confidence']:.1f} | Funnel: {funnel_score:.1f}",
                }
            except Exception as e:
                import traceback

                self.log_event(f"      ⚠️ Analysis FAILED for {sym}: {str(e)}")
                self.log_event(f"      🐛 Traceback: {traceback.format_exc()}")
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
                        "priceIncrement": float(sym.get("priceIncrement", 0.000001)),
                    }

                    fresh_symbols.append(base_currency)
                except Exception as e:
                    continue

            # Update symbols cache with fresh data
            self.symbols_cache = list(set(fresh_symbols))
            self.log_event(f"   📊 Found {len(self.symbols_cache)} active trading pairs")

            # Verify cache has symbols
            if not self.symbols_cache:
                self.log_event("   ⚠️ No trading pairs found - attempting fallback discovery")
                # Fallback to fetching symbols directly from tickers
                try:
                    tickers = await self.client.get_tickers()
                    fallback_symbols = []
                    # Use local definitions since self.stablecoins/self.ignored_symbols may not be defined
                    stablecoins = {"USDT", "USDC", "DAI", "TUSD", "USDP", "USD1", "USDY"}
                    ignored_symbols = {"BTC", "ETH", "SOL", "BNB"}
                    for ticker in tickers:
                        if ticker.symbol.endswith("-USDT"):
                            base_currency = ticker.symbol.replace("-USDT", "")
                            if (
                                len(base_currency) >= 2
                                and base_currency not in stablecoins
                                and base_currency not in ignored_symbols
                                and not base_currency.isdigit()
                                and not base_currency.startswith("USD")
                            ):
                                fallback_symbols.append(base_currency)
                    self.symbols_cache = list(set(fallback_symbols))
                    self.log_event(
                        f"   📊 Fallback discovery found {len(self.symbols_cache)} symbols"
                    )
                except Exception as e:
                    self.log_event(f"   ⚠️ Fallback discovery failed: {e}")
                    # If all else fails, use minimal default list
                    self.symbols_cache = ["BTC", "ETH"]
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

        # Get current tickers
        tickers = await self.client.get_tickers()
        ticker_map = {}
        for t in tickers:
            if t.symbol.endswith("-USDT"):
                sym = t.symbol.replace("-USDT", "")
                ticker_map[sym] = t

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

                # Calculate volatility and spread - handle cases where 24h data is missing
                if high_24h <= 0 or low_24h <= 0 or high_24h <= low_24h:
                    volatility = 0.02  # Default volatility if data is missing
                    spread = 0.005  # Default spread if data is missing
                else:
                    volatility = (high_24h - low_24h) / price
                    spread = min(volatility * 0.3, 0.02)

                # Enhanced quality filtering - only select high-quality symbols
                regime = self.state.get("market_regime", "NORMAL")

                # Simple but effective quality criteria
                quality_score = 0

                # Volume requirement - minimum liquidity
                if volume_24h >= min_liquidity * 3:
                    quality_score += 40
                elif volume_24h >= min_liquidity * 2:
                    quality_score += 30
                elif volume_24h >= min_liquidity * 1.5:
                    quality_score += 20
                elif volume_24h >= min_liquidity * 1.0:
                    quality_score += 15
                elif volume_24h >= min_liquidity * 0.8:
                    quality_score += 10
                else:
                    continue  # Skip very low volume symbols

                # Volatility requirement - accept reasonable ranges
                if 0.03 < volatility < 0.15:
                    quality_score += 35
                elif 0.02 < volatility <= 0.03 or 0.15 <= volatility < 0.25:
                    quality_score += 25
                elif 0.01 < volatility <= 0.02 or 0.25 <= volatility < 0.35:
                    quality_score += 15
                else:
                    continue  # Skip extremely stable or volatile

                # Momentum requirement - accept wider range
                if abs(change_24h) > 8.0:
                    quality_score += 45
                elif abs(change_24h) > 5.0:
                    quality_score += 35
                elif abs(change_24h) > 3.0:
                    quality_score += 25
                elif abs(change_24h) > 1.5:
                    quality_score += 15
                else:
                    continue  # Skip very low momentum

                # Include symbols with reasonable quality
                if quality_score >= 35:
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

                # Enhanced quality scoring - prioritize high-quality metrics
                volume_score = (
                    min(volume_24h / (min_liquidity * 10), 1) * 50
                )  # More weight on volume
                volatility_score = min(volatility / 0.05, 1) * 25  # Less weight on volatility
                momentum_score = min(abs(change_24h) / 5.0, 1) * 25  # Less weight on momentum

                # Additional quality factors
                quality_bonus = 0
                if volume_24h >= min_liquidity * 3:
                    quality_bonus += 15
                if abs(change_24h) > 8:
                    quality_bonus += 10
                if 0.04 < volatility < 0.12:
                    quality_bonus += 5

                total_score = volume_score + volatility_score + momentum_score + quality_bonus
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

        async def analyze_with_limit(sym):
            try:
                async with semaphore:
                    res = await analyze_symbol(sym)
                    if res:
                        self.log_event(
                            f"      ✅ Opportunity: {res['symbol']} (Score: {res['score']:.1f})"
                        )
                    return res
            except Exception as e:
                self.log_event(f"      ⚠️ Error analyzing {sym}: {e}")
                return None

        self.log_event(
            f"   ⚡ IBIS performing deep analysis on top {len(priority_symbols)} priority symbols..."
        )

        # Create analysis tasks
        tasks = []
        for sym in priority_symbols:
            tasks.append(analyze_with_limit(sym))

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

    def _calculate_technical_strength(self, momentum, change_24h, volatility=0.05, volume_24h=0):
        """Use unified scorer for technical strength calculation"""
        from ibis.core.unified_scoring import unified_scorer

        return unified_scorer.calculate_technical_score(
            momentum_1h=momentum,
            change_24h=change_24h,
            volatility=volatility,
            volume_24h=volume_24h,
        )

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
        """Integrate all intelligence factors into final score using unified scorer"""
        from ibis.core.unified_scoring import unified_scorer

        # Get scores from different sources
        sentiment_score = sentiment.get("score", 50) if sentiment else 50
        orderbook_score = orderbook.get("score", 50) if orderbook else 50
        onchain_score = onchain.get("score", 50) if onchain else 50
        unified_score = unified_intel.get("unified_score", 50) if unified_intel else 50

        # Calculate unified score using regime-adaptive weights
        result = unified_scorer.calculate_unified_score(
            technical_score=base_score,
            agi_score=unified_score,
            mtf_score=50,  # Default if not available
            volume_score=50,  # Default if not available
            sentiment_score=sentiment_score,
        )

        return result["score"]

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
        except (TypeError, ValueError) as e:
            self.log_event(f"⚠️ Failed to parse order book for {symbol}: {e}")
            return {"bid_depth": 0, "ask_depth": 0, "imbalance": 0.5, "score": 50}
        except Exception as e:
            self.log_event(f"⚠️ Unexpected error getting order book for {symbol}: {e}")
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
        except (TypeError, ValueError) as e:
            self.log_event(f"⚠️ Failed to parse data: {e}")
        except Exception as e:
            self.log_event(f"⚠️ Unexpected error: {e}")
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
        except (TypeError, ValueError) as e:
            self.log_event(f"⚠️ Failed to parse data: {e}")
        except Exception as e:
            self.log_event(f"⚠️ Unexpected error: {e}")
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
        except (TypeError, ValueError) as e:
            self.log_event(f"⚠️ Failed to parse data: {e}")
        except Exception as e:
            self.log_event(f"⚠️ Unexpected error: {e}")
            return None

    async def _get_reddit_sentiment(self, symbol):
        """Reddit sentiment from free API"""
        try:
            return await self.free_intel.get_reddit_sentiment(symbol)
        except (TypeError, ValueError) as e:
            self.log_event(f"⚠️ Failed to parse data: {e}")
        except Exception as e:
            self.log_event(f"⚠️ Unexpected error: {e}")
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
        except (TypeError, ValueError) as e:
            self.log_event(f"⚠️ Failed to parse data: {e}")
        except Exception as e:
            self.log_event(f"⚠️ Unexpected error: {e}")
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
        except (TypeError, ValueError) as e:
            self.log_event(f"⚠️ Failed to parse data: {e}")
        except Exception as e:
            self.log_event(f"⚠️ Unexpected error: {e}")
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
        except (TypeError, ValueError) as e:
            self.log_event(f"⚠️ Failed to parse data: {e}")
        except Exception as e:
            self.log_event(f"⚠️ Unexpected error: {e}")
            return None

    async def _get_large_transactions(self, symbol):
        """Large transaction proxy from free sources"""
        try:
            return await self.free_intel.get_large_transactions(symbol)
        except (TypeError, ValueError) as e:
            self.log_event(f"⚠️ Failed to parse data: {e}")
        except Exception as e:
            self.log_event(f"⚠️ Unexpected error: {e}")
            return None

    async def _get_holder_metrics(self, symbol):
        """Holder metrics proxy from free sources"""
        try:
            return await self.free_intel.get_holder_metrics(symbol)
        except (TypeError, ValueError) as e:
            self.log_event(f"⚠️ Failed to parse data: {e}")
        except Exception as e:
            self.log_event(f"⚠️ Unexpected error: {e}")
            return None

    async def _calculate_atr(self, symbol, period=14):
        """Average True Range for dynamic TP/SL"""
        try:
            candles = await self.client.get_candles(f"{symbol}-USDT", "15min", limit=period + 10)
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
        except (TypeError, ValueError) as e:
            self.log_event(f"⚠️ Failed to parse data: {e}")
        except Exception as e:
            self.log_event(f"⚠️ Unexpected error: {e}")
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
            "momentum_5m": 0.0,
            "momentum_15m": 0.0,
            "momentum_1h_raw": 0.0,
            "momentum_composite": 0.0,
            "volume_momentum": 0.0,
            "trend_strength": 0,
            "volume_profile": 0,
            "candle_patterns": [],
            "support_level": 0,
            "resistance_level": 0,
            "price_action": "neutral",
            "composite_score": 50,  # Default composite score
            "indicators": {},  # Indicator results
        }

        # Integrate IndicatorEngine for comprehensive technical analysis
        if candles_1m and len(candles_1m) >= 200:
            try:
                from ibis.indicators.indicators import IndicatorEngine

                engine = IndicatorEngine()
                indicator_result = engine.calculate_all(candles_1m)
                analysis["indicators"] = indicator_result.to_dict()
                analysis["composite_score"] = indicator_result.confidence * 100

                # Extract key indicator signals
                analysis["trend"] = indicator_result.trend
                analysis["momentum"] = indicator_result.momentum
                analysis["volatility"] = indicator_result.volatility
                analysis["overall_signal"] = indicator_result.overall_signal
            except Exception as e:
                print(f"Indicator engine error: {e}")

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

        # Multi-timeframe momentum bundle from 1m/5m/15m candles.
        momentum_1h_raw = 0.0
        momentum_15m = 0.0
        momentum_5m = 0.0
        volume_momentum = 0.0
        momentum_confidence = 0.0

        if candles_1m and len(candles_1m) >= 2:
            try:
                # 1h momentum from available 1m candles (up to 60 bars)
                lookback_1h = min(60, len(candles_1m) - 1)
                first_1h = float(candles_1m[-(lookback_1h + 1)].close)
                last_1h = float(candles_1m[-1].close)
                if first_1h > 0:
                    momentum_1h_raw = ((last_1h - first_1h) / first_1h) * 100.0

                # Fast momentum from last 15m / 5m of 1m bars
                if len(candles_1m) >= 16:
                    p15 = float(candles_1m[-16].close)
                    if p15 > 0:
                        momentum_15m = ((last_1h - p15) / p15) * 100.0
                if len(candles_1m) >= 6:
                    p5 = float(candles_1m[-6].close)
                    if p5 > 0:
                        momentum_5m = ((last_1h - p5) / p5) * 100.0

                # Volume momentum: recent 10 bars vs prior 10 bars
                if len(candles_1m) >= 20:
                    recent_vol = sum(float(c.volume) for c in candles_1m[-10:])
                    prior_vol = sum(float(c.volume) for c in candles_1m[-20:-10])
                    if prior_vol > 0:
                        volume_momentum = ((recent_vol / prior_vol) - 1.0) * 100.0

                # Confidence from data coverage and continuity
                confidence_1m = min(1.0, len(candles_1m) / 60.0)
                confidence_5m = min(1.0, len(candles_5m) / 12.0) if candles_5m else 0.0
                confidence_15m = min(1.0, len(candles_15m) / 8.0) if candles_15m else 0.0
                momentum_confidence = (
                    (confidence_1m * 0.6) + (confidence_5m * 0.25) + (confidence_15m * 0.15)
                ) * 100.0
            except Exception:
                pass

        # Fallback reinforcement from 5m candles for momentum_15m when available
        if candles_5m and len(candles_5m) >= 4:
            try:
                p15_5m = float(candles_5m[-4].close)
                last_5m = float(candles_5m[-1].close)
                if p15_5m > 0:
                    momentum_15m = ((last_5m - p15_5m) / p15_5m) * 100.0
            except Exception:
                pass

        # Clamp to avoid outlier spikes from micro-cap prints distorting signal quality
        momentum_1h_raw = max(-15.0, min(15.0, momentum_1h_raw))
        momentum_15m = max(-8.0, min(8.0, momentum_15m))
        momentum_5m = max(-5.0, min(5.0, momentum_5m))
        volume_momentum = max(-250.0, min(250.0, volume_momentum))

        # Composite momentum used by downstream scoring (bias to faster data under volatility)
        raw_composite = (0.45 * momentum_1h_raw) + (0.35 * momentum_15m) + (0.20 * momentum_5m)
        confidence_alpha = max(0.25, min(1.0, momentum_confidence / 100.0))
        momentum_composite = raw_composite * confidence_alpha

        analysis["momentum_1h_raw"] = momentum_1h_raw
        analysis["momentum_15m"] = momentum_15m
        analysis["momentum_5m"] = momentum_5m
        analysis["volume_momentum"] = volume_momentum
        analysis["momentum_confidence"] = momentum_confidence
        analysis["momentum_composite"] = momentum_composite
        analysis["momentum_1h"] = momentum_composite

        # 🕯️ Log candle analysis for visibility
        momentum_1h = analysis.get("momentum_1h", 0)
        if analysis["candle_patterns"]:
            self.log_event(
                f"      🕯️ CANDLES: {analysis['price_action']} | patterns: {analysis['candle_patterns']} | "
                f"M5:{analysis['momentum_5m']:+.3f}% M15:{analysis['momentum_15m']:+.3f}% "
                f"M1h(raw):{analysis['momentum_1h_raw']:+.3f}% Mx:{momentum_1h:+.3f}% "
                f"Vmom:{analysis['volume_momentum']:+.1f}% C:{analysis['momentum_confidence']:.0f}% | vol_1m: {analysis['volatility_1m']:.4f}"
            )
        else:
            self.log_event(
                f"      🕯️ CANDLES: {analysis['price_action']} | "
                f"M5:{analysis['momentum_5m']:+.3f}% M15:{analysis['momentum_15m']:+.3f}% "
                f"M1h(raw):{analysis['momentum_1h_raw']:+.3f}% Mx:{momentum_1h:+.3f}% "
                f"Vmom:{analysis['volume_momentum']:+.1f}% C:{analysis['momentum_confidence']:.0f}% | vol_1m: {analysis['volatility_1m']:.4f}"
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
        """Basic position sizing - use MORE capital for high scores"""
        available = strategy["available"]
        min_trade = TRADING.POSITION.MIN_CAPITAL_PER_TRADE

        if available < min_trade:
            return 0

        # Use higher percentage of capital for better scores
        score_factor = opportunity_score / 100

        # Dynamic position percentage based on score - CAPITALIZE ON INTELLIGENCE
        if opportunity_score >= 95:  # GOD TIER (95+) - Maximum capital
            position_pct = 0.50  # 50% for exceptional opportunities
        elif opportunity_score >= 90:  # HIGH CONFIDENCE (90-94) - High capital
            position_pct = 0.40  # 40% for high confidence
        elif opportunity_score >= 85:  # STRONG SETUP (85-89) - Strong capital
            position_pct = 0.35  # 35% for strong setups
        elif opportunity_score >= 80:  # GOOD SETUP (80-84) - Good capital
            position_pct = 0.30  # 30% for good opportunities
        elif opportunity_score >= 70:  # STANDARD (70-79) - Standard capital
            position_pct = 0.25  # 25% for standard opportunities
        elif opportunity_score >= 60:  # MODERATE (60-69) - Reduced capital
            position_pct = 0.20  # 20% for moderate setups
        else:  # WEAK (<60) - Minimum capital
            position_pct = 0.15  # 15% for weak signals

        vol_adjustment = 1.0 / (1 + volatility)
        position_size = available * position_pct * vol_adjustment

        # Ensure position size meets minimum requirements
        position_size = max(min_trade, position_size)
        # Ensure position size does not exceed available capital or max per trade
        position_size = min(position_size, available)
        position_size = min(position_size, TRADING.POSITION.MAX_CAPITAL_PER_TRADE)

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
        else:
            # Analyze market intelligence to determine conditions
            symbols_analyzed = len(self.market_intel)
            if symbols_analyzed < 20:
                conditions["overall_health"] = "poor"
                conditions["trading_opportunity"] = "rest"
            else:
                # Calculate average score
                avg_score = (
                    sum(float(opp.get("score", 0)) for opp in self.market_intel.values())
                    / symbols_analyzed
                )

                # Determine trading opportunity based on average score
                if avg_score >= 75:
                    conditions["trading_opportunity"] = "hunt"
                    conditions["overall_health"] = "excellent"
                elif avg_score >= 65:
                    conditions["trading_opportunity"] = "hunt"
                    conditions["overall_health"] = "good"
                elif avg_score >= 55:
                    conditions["trading_opportunity"] = "caution"
                    conditions["overall_health"] = "fair"
                else:
                    conditions["trading_opportunity"] = "rest"
                    conditions["overall_health"] = "poor"

                # Determine trend strength based on momentum
                avg_momentum = (
                    sum(float(opp.get("momentum_1h", 0)) for opp in self.market_intel.values())
                    / symbols_analyzed
                )
                if abs(avg_momentum) > 2.0:
                    conditions["trend_strength"] = "strong"
                elif abs(avg_momentum) > 0.5:
                    conditions["trend_strength"] = "moderate"
                else:
                    conditions["trend_strength"] = "weak"

                # Determine volatility risk
                avg_volatility = (
                    sum(float(opp.get("volatility", 0.02)) for opp in self.market_intel.values())
                    / symbols_analyzed
                )
                if avg_volatility > 0.15:
                    conditions["volatility_risk"] = "high"
                elif avg_volatility > 0.08:
                    conditions["volatility_risk"] = "moderate"
                else:
                    conditions["volatility_risk"] = "low"

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
                    except Exception as e:
                        print(f"   Warning: Could not cancel order {order_id}: {e}")
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

        # Count high-quality opportunities
        high_score_count = sum(1 for s in changes_24h if s > 0)
        very_high_score_count = sum(1 for c in changes_24h if c > 5)  # >5% gainers
        avg_score = sum(changes_24h) / len(changes_24h) if changes_24h else 0

        # 🌟 PERFECT STORM DETECTION - Maximum aggression mode
        # When everything aligns: strong momentum, high consistency, many winners
        perfect_conditions = (
            momentum > 2.0  # Strong momentum
            and trend_consistency > 0.70  # 70%+ of symbols moving same direction
            and avg_trend > 40  # Strong trend
            and very_high_score_count > len(changes_24h) * 0.5  # >50% of symbols up >5%
            and avg_change_24h > 3  # Market up 3%+ overall
        )

        if perfect_conditions:
            regime = "PERFECT"
            self.log_event(f"   🌟 PERFECT STORM DETECTED! Maximum aggression mode activated!")
            self.log_event(
                f"      Momentum: {momentum:.2f} | Consistency: {trend_consistency:.0%} | >5% Winners: {very_high_score_count}/{len(changes_24h)}"
            )
        # Strong trending conditions
        elif momentum > 1.5 and trend_consistency > 0.6 and avg_trend > 30:
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

        # Set perfect storm flag for order type decisions
        self._perfect_storm = regime == "PERFECT"

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

            # DISABLED: Market intelligence issues - let IBIS trade based on actual opportunities
            # if avg_market_score < 40 and high_quality_count < 3:
            #     self.log_event(
            #         f"      🛑 TRASH MARKET DETECTED: Avg score {avg_market_score:.1f}, pausing trades"
            #     )
            #     mode = "OBSERVING"
            #     return mode

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

    async def _validate_market_intel_prices(self):
        """Validate and enrich market intelligence with current price data

        Ensures that every symbol in market intel has valid current price information
        by cross-referencing with exchange ticker data.
        """
        if not self.market_intel:
            return False

        try:
            tickers = await self.client.get_tickers()
            ticker_map = {
                t.symbol.replace("-USDT", ""): t for t in tickers if t.symbol.endswith("-USDT")
            }

            fixed = 0
            missing = 0

            for sym, intel in self.market_intel.items():
                # Skip if already has valid price
                if (
                    intel.get("current_price")
                    and intel.get("price")
                    and float(intel["current_price"]) > 0
                ):
                    continue

                # Try to get price from ticker map
                if sym in ticker_map:
                    ticker = ticker_map[sym]
                    if hasattr(ticker, "price") and ticker.price:
                        price = float(ticker.price)
                        if price > 0:
                            intel["current_price"] = price
                            intel["price"] = price
                            fixed += 1
                            continue

                missing += 1
                self.log_event(f"   ⚠️ No valid price for {sym}")

            self.log_event(f"   📊 Price validation: Fixed {fixed} | Missing {missing}")
            return True

        except Exception as e:
            self.log_event(f"   ⚠️ Price validation failed: {e}")
            return False

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
                    except (TypeError, ValueError) as e:
                        self.log_event(f"⚠️ Failed to parse price for {currency}: {e}")
                    except Exception as e:
                        self.log_event(f"⚠️ Unexpected error getting price for {currency}: {e}")

                if price > 0:
                    value = balance * price
                    holdings_value += value

        total_assets = usdt_balance + holdings_value

        # Validate and enrich market intelligence with current price data
        await self._validate_market_intel_prices()

        capital = await self.update_capital_awareness()
        real_capital = capital.get("real_trading_capital", usdt_available)
        available = real_capital

        positions_value = holdings_value

        # MODE-BASED STRATEGY (from centralized configuration)
        # Use FIXED TP/SL: 1.5% TP / 5% SL always
        base_tp = TRADING.RISK.TAKE_PROFIT_PCT  # 1.5%
        base_sl = TRADING.RISK.STOP_LOSS_PCT  # 5%

        mode_configs = {
            "TRENDING": {"target": base_tp, "stop": base_sl, "conf": 70},
            "DEFENSIVE": {"target": base_tp, "stop": base_sl, "conf": 80},
            "CAUTIOUS": {"target": base_tp, "stop": base_sl, "conf": 75},
            "MICRO_HUNTER": {"target": base_tp, "stop": base_sl, "conf": 70},
            "PATIENT": {"target": base_tp, "stop": base_sl, "conf": 85},
            "OPTIMISTIC": {"target": base_tp, "stop": base_sl, "conf": 70},
            "AGGRESSIVE": {"target": base_tp, "stop": base_sl, "conf": 65},
            "CONFIDENT": {"target": base_tp, "stop": base_sl, "conf": 80},
            "HYPER": {"target": base_tp, "stop": base_sl, "conf": 70},
            "HYPER_INTELLIGENT": {"target": base_tp, "stop": base_sl, "conf": 70},
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
            from ibis.intelligence.market_intel import AdvancedRiskManager
        except ImportError:
            self.log_event("   ⚠️ AdvancedRiskManager not available, using basic sizing")
            return self._calculate_basic_position_size(opportunity_score, strategy, volatility)

        available_for_trade = strategy["available"]
        min_trade = TRADING.POSITION.MIN_CAPITAL_PER_TRADE  # $11

        # Initialize advanced risk manager
        risk_manager = AdvancedRiskManager()

        # Keep symbol-specific volatility when available; fallback remains at function entry.

        # Get current number of positions
        current_positions = len(self.state["positions"])

        # Calculate position size using advanced risk management
        # First, calculate dynamic TP/SL to use with risk manager
        base_tp_pct = self._get_dynamic_tp_pct(opportunity_score)
        base_sl_pct = TRADING.RISK.STOP_LOSS_PCT

        # For God tier signals, use tighter SL and higher TP
        if opportunity_score >= 95:
            sl_pct = 0.03  # 3% SL for god tier (tighter risk)
            tp_pct = 0.06  # 6% TP for god tier (higher reward)
        elif opportunity_score >= 90:
            sl_pct = 0.035  # 3.5% SL for high confidence
            tp_pct = 0.05  # 5% TP for high confidence
        elif opportunity_score >= 85:
            sl_pct = 0.04  # 4% SL for strong setup
            tp_pct = 0.04  # 4% TP for strong setup
        else:
            sl_pct = base_sl_pct
            tp_pct = base_tp_pct

        # Calculate stop loss price (assuming entry price from market intel)
        entry_price = market_intel.get("current_price", 0)
        if entry_price <= 0:
            entry_price = market_intel.get("price", 0)

        if entry_price <= 0:
            self.log_event("   ⚠️ No valid entry price, using basic sizing")
            return self._calculate_basic_position_size(opportunity_score, strategy, volatility)

        stop_loss = entry_price * (1 - sl_pct)

        position_size = risk_manager.calculate_position_size(
            capital=available_for_trade,
            entry_price=entry_price,
            stop_loss=stop_loss,
            volatility=volatility,
            correlation_exposure=0,  # Default to no correlation risk
        )

        # Ensure minimum trade size is respected
        if position_size < min_trade and available_for_trade >= min_trade:
            position_size = min_trade

        # Ensure position size doesn't exceed maximum constraints
        position_size = min(position_size, TRADING.POSITION.MAX_CAPITAL_PER_TRADE)

        # Respect portfolio risk limits - use available capital, not remaining_risk
        # The remaining_risk calculation was causing positions to be $0 due to holdings value
        available_for_position = min(available_for_trade, TRADING.POSITION.MAX_CAPITAL_PER_TRADE)

        # Ensure minimum position size is respected
        min_trade = TRADING.POSITION.MIN_CAPITAL_PER_TRADE
        if available_for_position < min_trade:
            available_for_position = min_trade

        # Use available capital, not remaining_risk which was blocking trades
        position_size = min(position_size, available_for_position)

        # Ensure position doesn't exceed available capital
        position_size = min(position_size, available_for_trade)

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
        opp = market_intel.get(symbol, {}) if isinstance(market_intel, dict) else {}
        score = opp.get("score", 50)
        regime = strategy.get("regime", "NORMAL")

        return await self.calculate_position_size(score, strategy, regime, opp)

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
                    except (TypeError, ValueError) as e:
                        self.log_event(f"⚠️ Failed to parse price for {currency}: {e}")
                    except Exception as e:
                        self.log_event(f"⚠️ Unexpected error getting price for {currency}: {e}")

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
        except (TypeError, ValueError) as e:
            self.log_event(f"⚠️ Failed to parse data: {e}")
        except Exception as e:
            self.log_event(f"⚠️ Unexpected error: {e}")
            fg_value = 50

        opportunities = []
        held = set(self.state["positions"].keys())

        # 🎯 ENHANCED QUALITY SORTING: Prioritize by score + volume + volatility
        sorted_opps = sorted(
            market_intel.items(),
            key=lambda x: (
                x[1]["score"],  # Primary: Score
                x[1].get("volume_24h", 0) / 1e6,  # Secondary: Volume (millions)
                -abs(x[1].get("volatility", 0)),  # Tertiary: Lower volatility (more stable)
                x[1].get("change_24h", 0),  # Quaternary: Positive momentum
            ),
            reverse=True,
        )

        regime = self.state.get("market_regime", "NORMAL")
        min_threshold = self.config.get(
            "min_score", 70
        )  # More aggressive threshold for opportunities
        fee_guard_enabled = bool(self.config.get("execution_fee_guard_enabled", True))
        max_fee_per_side = float(self.config.get("execution_fee_max_per_side", 0.0025))
        fee_override_score = float(self.config.get("execution_fee_override_score", 90))
        fee_profile = self._load_symbol_fee_profile()
        fee_blocklist = self._get_execution_fee_blocklist()
        slow_fill_symbols = self._get_slow_fill_symbols()
        latency_override_score = float(self.config.get("latency_guard_override_score", 90))
        log_event(f"   🎯 Filtering with MIN_SCORE: {min_threshold:.1f}")

        # 🎯 STRICT QUALITY FILTERING
        for sym, intel in sorted_opps:
            if sym in held:
                continue

            score = intel["score"]  # Base score without artificial boost

            # Execution economics guardrail: avoid high-fee symbols unless conviction is strong.
            sym_fee_rate = fee_profile.get(sym, 0.0)
            if fee_guard_enabled and sym in fee_blocklist and score < fee_override_score:
                log_event(
                    f"      ❌ REJECTED: {sym} (fee-blocklisted {sym_fee_rate * 100:.3f}%/side, fills={self._symbol_fee_counts.get(sym, 0)})"
                )
                continue
            if fee_guard_enabled and sym_fee_rate > max_fee_per_side and score < fee_override_score:
                log_event(
                    f"      ❌ REJECTED: {sym} (high fee {sym_fee_rate * 100:.3f}%/side > {max_fee_per_side * 100:.3f}% cap)"
                )
                continue
            if sym in slow_fill_symbols and score < latency_override_score:
                row = self.agent_memory.get("fill_latency_by_symbol", {}).get(sym, {})
                log_event(
                    f"      ❌ REJECTED: {sym} (slow fills avg={float(row.get('avg_seconds', 0)):.1f}s, samples={int(row.get('samples', 0))})"
                )
                continue

            # Reject low quality opportunities early
            if score < min_threshold:
                log_event(f"      ❌ REJECTED: {sym} (Score: {score:.1f} < {min_threshold:.1f})")
                continue

            # Additional quality checks
            volume = intel.get("volume_24h", 0)
            volatility = intel.get("volatility", 0.02)
            momentum = intel.get("momentum_1h", 0)

            if volume < 500000:  # < $500K volume
                log_event(f"      ❌ REJECTED: {sym} (Low volume: ${volume / 1000:.0f}K)")
                continue

            # Strict filtering for high-quality signals with upward potential
            if volatility > 0.25:  # > 25% volatility (too erratic for quality trades)
                log_event(f"      ❌ REJECTED: {sym} (Extreme volatility: {volatility * 100:.1f}%)")
                continue

            if momentum < -0.1:  # Negative momentum (avoid downward pressure)
                log_event(f"      ❌ REJECTED: {sym} (Negative momentum: {momentum:.2f})")
                continue

            # Require minimum upward momentum for god tier signals
            if score >= 90 and momentum < 0.3:
                log_event(
                    f"      ❌ REJECTED: {sym} (Insufficient upward momentum: {momentum:.2f} for score {score:.1f})"
                )
                continue

            # Require strong 24h performance for high-confidence signals
            if score >= 85 and intel.get("change_24h", 0) < 2:
                log_event(
                    f"      ❌ REJECTED: {sym} (Weak 24h performance: {intel.get('change_24h', 0):.1f}% for score {score:.1f})"
                )
                continue

            # AGI-Enhanced Analysis - pass Fear & Greed index
            agi_signal = None
            try:
                # Create market context for AGI brain
                context = MarketContext(
                    symbol=intel["symbol"],
                    price=intel["price"],
                    price_change_24h=intel.get("change_24h", 0),
                    price_change_1h=intel.get("momentum_1h", 0),
                    volume_24h=intel.get("volume_24h", 0),
                    volatility_1h=intel.get("volatility", 0.02),
                    volatility_24h=intel.get("volatility", 0.02),
                    trend_strength=intel.get("trend_strength", 0),
                    order_flow_delta=intel.get("order_flow", 0),
                    sentiment_score=fg_value,
                    fear_greed_index=fg_value,
                    funding_rate=intel.get("funding_rate", 0),
                    long_short_ratio=intel.get("long_short_ratio", 1),
                    exchange_flow=intel.get("exchange_flow", 0),
                    whale_activity=intel.get("whale_activity", "NEUTRAL"),
                    volume_profile=intel.get("volume_profile", {}),
                    recent_trades=intel.get("recent_trades", []),
                    correlated_assets=intel.get("correlated_assets", {}),
                )

                # Get AGI brain analysis
                agi_signal = await self.agi_brain.comprehensive_analysis(context)
                self.log_event(
                    f"      🧠 AGI Analysis: {intel['symbol']} - Action: {agi_signal.action}, Confidence: {agi_signal.confidence * 100:.1f}%, Risk: {agi_signal.risk_reward:.2f}"
                )
                self.log_event(
                    f"      🧠 Confluences: {len(agi_signal.confluences)} factors, Model Consensus: {len(agi_signal.model_consensus)} models"
                )
            except Exception as e:
                self.log_event(f"      ⚠️ AGI analysis failed: {e}")
                import traceback

                self.log_event(f"      ⚠️ Traceback: {traceback.format_exc()}")

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
                # Convert TradeSignal to dict for compatibility
                agi_signal_dict = agi_signal.__dict__
                agi_score = agi_signal_dict.get("confidence", 0.5) * 100
                # Bypass recommendation logic - ALWAYS BUY for high scores
                if score >= 90:
                    agi_action = "STRONG_BUY"
                elif score >= 70:
                    agi_action = "BUY"
                agi_reason = agi_signal_dict.get("reasoning", "No reasoning")
                self.log_event(
                    f"      🧠 AGI: {intel['symbol']} | score: {agi_score:.1f} | action: {agi_action} | {agi_reason[:30]}"
                )

            if score >= min_threshold:
                # 🎯 EXTREME AGGRESSION - Always execute if score meets threshold
                diff = score - min_threshold
                if score >= 90:
                    reason = f"GOD TIER! ({diff:+.1f} above threshold) - EXECUTE"
                    agi_action = "STRONG_BUY"
                # 🎯 QUALITY TIER CLASSIFICATION
                if score >= 90:
                    reason = f"⭐ GOD TIER ({diff:+.1f} above threshold) - MAXIMUM EXECUTION"
                    agi_action = "GOD_BUY"
                elif score >= 85:
                    reason = f"🔥 EXCELLENT ({diff:+.1f} above threshold) - HIGH EXECUTION"
                    agi_action = "EXCELLENT_BUY"
                elif score >= 80:
                    reason = f"💎 HIGH CONFIDENCE ({diff:+.1f} above threshold) - MEDIUM EXECUTION"
                    agi_action = "STRONG_BUY"
                elif score >= 75:
                    reason = f"📈 STRONG SETUP ({diff:+.1f} above threshold) - STANDARD EXECUTION"
                    agi_action = "BUY"
                else:
                    reason = f"⚠️ LOW QUALITY ({diff:+.1f} above threshold) - MINIMUM EXECUTION"
                    agi_action = "CAUTIOUS_BUY"

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
                if agi_signal and agi_signal.confidence > 70:
                    components.append(f"AGI:{agi_signal.confidence:.0f}")

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
                if intel.get("spread", 0) > TRADING.FILTER.MAX_SPREAD:
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
        except (TypeError, ValueError) as e:
            self.log_event(f"⚠️ Failed to parse data: {e}")
        except Exception as e:
            self.log_event(f"⚠️ Unexpected error: {e}")
            pass

        rules = self.symbol_rules.get(symbol, {})
        base_increment = float(rules.get("baseIncrement", 0.000001))
        base_min_size = float(rules.get("baseMinSize", 0.001))
        quote_min_size = float(rules.get("quoteMinSize", 0.1))
        price_increment = float(rules.get("priceIncrement", rules.get("quoteIncrement", 0.0000001)))
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

        quantity = format_decimal_for_increment(quantity, base_increment)

        # Final check - enforce minimum position size with tolerance for floating point
        final_order_value = quantity * price
        tolerance = 0.05  # Allow 5 cents tolerance
        if final_order_value < min_position_value - tolerance:
            print(
                f"⚠️ {symbol}: Position ${final_order_value:.2f} below ${min_position_value:.2f} minimum - skipping"
            )
            return None

        # 🎯 PRECISION EXECUTION: Get adaptive stop levels using ATR
        candles_5m = await self.client.get_candles(f"{symbol}-USDT", "5min", limit=20)

        # Calculate smart stops (adaptive based on volatility, averages ~2%)
        try:
            # Use self.enhanced if available, otherwise skip
            if hasattr(self, "enhanced") and self.enhanced:
                stop_data = await self.enhanced.calculate_smart_stop_levels(
                    entry_price=price, direction="LONG", candles=candles_5m, timeframe="5m"
                )

                tp = stop_data["take_profit"]
                sl_pct = stop_data["stop_distance_pct"] / 100
                tp_pct = stop_data["tp_distance_pct"] / 100

                self.log_event(
                    f"      🎯 SMART STOPS: SL {stop_data['stop_distance_pct']:.2f}% ({stop_data['volatility_mode']}) | "
                    f"TP {stop_data['tp_distance_pct']:.2f}%"
                )
            else:
                # Fallback: use dynamic TP from score with god tier optimization
                tp_pct = self._get_dynamic_tp_pct(score)
                sl_pct = TRADING.RISK.STOP_LOSS_PCT

                # God tier signals get tighter SL and higher TP
                if score >= 95:
                    sl_pct = 0.03  # 3% SL for god tier (tighter risk)
                    tp_pct = 0.06  # 6% TP for god tier (higher reward)
                elif score >= 90:
                    sl_pct = 0.035  # 3.5% SL for high confidence
                    tp_pct = 0.05  # 5% TP for high confidence
                elif score >= 85:
                    sl_pct = 0.04  # 4% SL for strong setup
                    tp_pct = 0.04  # 4% TP for strong setup

                tp = price * (1 + tp_pct)

        except Exception as e:
            self.log_event(f"      ⚠️ Smart stops calculation failed: {e}")
            # Fallback: use dynamic TP from score
            tp_pct = self._get_dynamic_tp_pct(score)
            sl_pct = TRADING.RISK.STOP_LOSS_PCT
            tp = price * (1 + tp_pct)

        # Keep the calculated dynamic TP/SL (do NOT overwrite)
        if "tp" not in locals() or "sl" not in locals():
            tp_pct = self._get_dynamic_tp_pct(score)
            sl_pct = TRADING.RISK.STOP_LOSS_PCT
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
        print(f"   ║ Target: ${tp:<55.4f} (+{tp_pct * 100:.1f}%) ║")
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

        # Check for existing pending order before creating new one
        buy_orders = self.state.get("capital_awareness", {}).get("buy_orders", {})
        if symbol in buy_orders:
            print(f"⚠️ Pending order already exists for {symbol} - skipping duplicate")
            return None

        min_trade_value = TRADING.EXECUTION.MIN_TRADE_VALUE
        actual_value = quantity * price
        # Add small epsilon for floating-point precision
        if actual_value < min_trade_value - 0.01:
            print(
                f"⚠️ Order value ${actual_value:.2f} below minimum ${min_trade_value:.2f} - skipping"
            )
            return None

        try:
            # 🎯 ENTRY TYPE: MARKET for PERFECT/STRONG_BULL, LIMIT otherwise
            # In perfect conditions, we want instant entry to capture moves
            order_regime = strategy.get("regime", "NORMAL")
            use_market = TRADING.SCAN.MARKET_ORDERS_BY_REGIME.get(order_regime, False)
            if self.config.get("maker_first_execution", True) and use_market:
                # Guardrail: allow taker only when signal strength and spread justify it.
                market_score_min = float(self.config.get("market_entry_score_threshold", 90))
                market_max_spread = float(self.config.get("market_entry_max_spread", 0.0035))
                if score < market_score_min:
                    use_market = False
                    self.log_event(
                        f"      🧩 MAKER-FIRST: {symbol} score {score:.1f} < {market_score_min:.0f}, using limit"
                    )
                else:
                    try:
                        ticker_for_spread = await self.client.get_ticker(f"{symbol}-USDT")
                        bid = float(getattr(ticker_for_spread, "buy", 0) or 0)
                        ask = float(getattr(ticker_for_spread, "sell", 0) or 0)
                        spread_now = ((ask - bid) / bid) if bid > 0 and ask > 0 else 0
                        if spread_now > market_max_spread:
                            use_market = False
                            self.log_event(
                                f"      🧩 MAKER-FIRST: {symbol} spread {spread_now * 100:.2f}% > {market_max_spread * 100:.2f}%, using limit"
                            )
                    except Exception:
                        use_market = False

            if use_market:
                # MARKET order for instant entry in optimal conditions
                order_type = "market"
                suggested_price = price
                self.log_event(
                    f"      🚀 EXECUTING MARKET buy for {symbol} @ ${price:.6f} (PERFECT CONDITIONS - MAX SPEED)"
                )
            else:
                # LIMIT order for better price in normal conditions
                order_type = "limit"
                discount_pct = 0.002  # 0.2% below current price
                suggested_price = price * (1 - discount_pct)

                # Round price to valid increment based on symbol rules.
                # Use downward rounding for buy limits to avoid crossing.
                if price_increment > 0:
                    suggested_price = round_down_to_increment(suggested_price, price_increment)
                    suggested_price = max(suggested_price, price_increment)
                    suggested_price = format_decimal_for_increment(suggested_price, price_increment)

                self.log_event(
                    f"      🚀 EXECUTING LIMIT buy for {symbol} @ ${suggested_price:.8f} (${price:.6f} - 0.2%)..."
                )

                # Ensure submitted limit notional respects the hard minimum.
                required_notional = min_trade_value + 0.01
                actual_limit_value = quantity * suggested_price
                if actual_limit_value < required_notional:
                    required_qty = required_notional / max(suggested_price, 1e-12)
                    quantity = round_up_to_increment(required_qty, base_increment)
                    quantity = max(quantity, base_min_size)
                    quantity = format_decimal_for_increment(quantity, base_increment)
                    actual_limit_value = quantity * suggested_price
                    self.log_event(
                        f"      🔧 ADJUSTED QTY FOR MIN NOTIONAL: qty={quantity:.8f}, value=${actual_limit_value:.2f}"
                    )

                max_affordable = available_for_trade * 0.995
                if actual_limit_value > max_affordable + 1e-9:
                    self.log_event(
                        f"      🛑 LIMIT NOTIONAL EXCEEDS AVAILABLE: ${actual_limit_value:.2f} > ${max_affordable:.2f}"
                    )
                    return None

                # Re-check against minimum using the ACTUAL submitted limit price.
                if actual_limit_value < min_trade_value - 0.01:
                    self.log_event(
                        f"      🛑 LIMIT VALUE TOO LOW: ${actual_limit_value:.2f} < ${min_trade_value:.2f} minimum for {symbol}"
                    )
                    return None

            if order_type == "market":
                # For market buy orders, KuCoin uses funds (USD amount) instead of size (quantity)
                resp = await self.client.create_order(
                    symbol=f"{symbol}-USDT",
                    side="buy",
                    type=order_type,
                    price=0,
                    size=position_value,
                )
            else:
                # For limit orders, use quantity
                resp = await self.client.create_order(
                    symbol=f"{symbol}-USDT",
                    side="buy",
                    type=order_type,
                    price=suggested_price,
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
                "status": "pending",
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
                print(
                    f"   Score: {opportunity.get('adjusted_score', score):.0f} | TP: {tp_display} | {sl_info}"
                )
                print(f"   ⚠️ Will move to positions when order fills")

                self._save_state()
                return None

        except Exception as e:
            error_msg = str(e)
            print(f"❌ {symbol}: {error_msg}")

            # Check if order already exists before creating new one
            buy_orders = self.state.get("capital_awareness", {}).get("buy_orders", {})
            if symbol in buy_orders:
                print(f"   ⚠️ Order already exists for {symbol} - skipping duplicate")
                return None

            # Simple error handling without complex retry logic for now
            return None
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
        capital = await self.update_capital_awareness()
        real_capital = float(capital.get("real_trading_capital", capital.get("usdt_available", 0)) or 0)
        recycle_capital_trigger = float(
            self.config.get("recycle_capital_trigger_usdt", TRADING.POSITION.MIN_CAPITAL_PER_TRADE)
        )
        recycle_min_projected_profit = float(
            self.config.get("recycle_min_projected_profit_usdt", 0.03)
        )
        recycle_min_projected_pnl_pct = float(
            self.config.get("recycle_min_projected_pnl_pct", 0.003)
        )

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
                estimated_fees = trade_value * self._estimate_total_friction_for_symbol(sym)
                pnl_value = quantity * (current - buy_price)
                actual_profit = pnl_value - estimated_fees

                pos_intel = self.market_intel.get(sym, {})
                current_score = pos_intel.get("score", 50)

                buy_price = pos.get("buy_price", current)
                tp = pos.get("tp")
                sl = pos.get("sl")

                expected_tp = buy_price * (1 + TRADING.RISK.TAKE_PROFIT_PCT)
                expected_sl = buy_price * (1 - TRADING.RISK.STOP_LOSS_PCT)

                if not tp:
                    tp = expected_tp
                if not sl:
                    sl = expected_sl

                tp_hit = current >= tp
                sl_hit = current <= sl

                if pnl_pct > 0.01:
                    self.log_event(
                        f"      🔍 {sym}: ${current:.4f} | Buy: ${buy_price:.4f} | "
                        f"PnL: {pnl_pct * 100:.2f}% | TP: ${tp:.4f} ({tp_hit}) | SL: ${sl:.4f} ({sl_hit})"
                    )

                min_profit = TRADING.RISK.MIN_PROFIT_BUFFER

                if tp_hit:
                    to_close.append((sym, "TAKE_PROFIT", current, pnl_pct, actual_profit))
                elif sl_hit:
                    to_close.append((sym, "STOP_LOSS", current, pnl_pct, actual_profit))
                elif current_score < 35 and pnl_pct < -0.003 and actual_profit < -min_profit:
                    to_close.append((sym, "ALPHA_DECAY", current, pnl_pct, actual_profit))

                if (
                    real_capital < recycle_capital_trigger
                    and actual_profit > max(min_profit, recycle_min_projected_profit)
                    and pnl_pct >= recycle_min_projected_pnl_pct
                ):
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
                exit_detail = f"Target reached (+{pnl_pct * 100:.2f}%, +${actual_profit:.4f} actual)"
            elif reason == "STOP_LOSS":
                exit_detail = f"Stop loss triggered ({pnl_pct * 100:.2f}%, ${actual_profit:.4f})"
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
        canceled_count = 0
        stale_buy_seconds = int(self.config.get("stale_buy_cancel_seconds", 90))
        pressure_relief_seconds = int(self.config.get("stale_buy_pressure_relief_seconds", 45))
        pressure_trigger = int(self.config.get("stale_buy_pressure_trigger", 4))
        pressure_min_pending = max(
            1, int(self.config.get("stale_buy_pressure_min_pending", 2))
        )
        stale_buy_hard_seconds = int(
            self.config.get(
                "stale_buy_hard_seconds",
                max(stale_buy_seconds * 2, pressure_relief_seconds),
            )
        )
        stale_buy_max_per_cycle = int(self.config.get("stale_buy_cancel_max_per_cycle", 3))
        min_trade_capital = float(TRADING.POSITION.MIN_CAPITAL_PER_TRADE)
        available_usdt = float(
            self.state.get("capital_awareness", {}).get("real_trading_capital", 0)
            or self.state.get("capital_awareness", {}).get("usdt_available", 0)
            or 0
        )
        under_capital_pressure = available_usdt < min_trade_capital and len(buy_orders) > 0
        if len(buy_orders) >= pressure_trigger or under_capital_pressure:
            stale_buy_seconds = min(stale_buy_seconds, pressure_relief_seconds)
        if under_capital_pressure:
            # Reclaim deployable USDT quickly when available is below the $11 hard minimum.
            stale_buy_max_per_cycle = max(stale_buy_max_per_cycle, min(len(buy_orders), pressure_trigger))
        live_balances_cache = None
        for symbol, order_info in list(buy_orders.items()):
            try:
                order_id = order_info.get("order_id")
                if not order_id:
                    continue

                order = await self.client.get_order(order_id, f"{symbol}-USDT")
                if not order:
                    continue

                is_active = order.status == "ACTIVE"
                deal_size = order.filled_size
                deal_funds = float(getattr(order, "deal_funds", 0) or 0)
                avg_price = order.avg_price
                fee = order.fee
                fee_currency = order.fee_currency

                print(
                    f"DEBUG: {symbol} order - Active: {is_active}, Filled size: {deal_size}, Avg price: {avg_price}"
                )
                print(
                    f"DEBUG: Order info quantity: {order_info.get('quantity')}, price: {order_info.get('price')}"
                )

                if not is_active and (deal_size > 0 or deal_funds > 0):
                    actual_price = float(avg_price if avg_price > 0 else order_info.get("price", 0) or 0)
                    actual_quantity = float(deal_size or 0)
                    if actual_quantity <= 0 and deal_funds > 0 and actual_price > 0:
                        actual_quantity = deal_funds / actual_price
                    if actual_quantity <= 0:
                        actual_quantity = float(order_info.get("quantity", 0) or 0)
                    fill_latency_seconds = 0.0
                    try:
                        created_at_ms = int(getattr(order, "created_at", 0) or 0)
                    except Exception:
                        created_at_ms = 0
                    if created_at_ms > 0:
                        fill_latency_seconds = max(0.0, (time.time() * 1000 - created_at_ms) / 1000.0)
                    elif order_info.get("timestamp"):
                        try:
                            opened_at = datetime.fromisoformat(str(order_info.get("timestamp")))
                            fill_latency_seconds = max(
                                0.0, (datetime.now() - opened_at).total_seconds()
                            )
                        except Exception:
                            fill_latency_seconds = 0.0

                    if actual_quantity <= 0:
                        del buy_orders[symbol]
                        continue

                    # If symbol already exists in positions, update it
                    if symbol in self.state["positions"]:
                        self.state["positions"][symbol]["quantity"] = actual_quantity
                        self.state["positions"][symbol]["buy_price"] = actual_price
                        if fee > 0:
                            self.state["positions"][symbol]["fee"] = fee
                            self.state["positions"][symbol]["fee_currency"] = fee_currency
                    else:
                        # Create new position
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
                        self.state["positions"][symbol] = pos
                        self.state["daily"]["trades"] += 1
                        print(
                            f"\n✅ ORDER FILLED: {symbol} {actual_quantity:.4f} @ ${actual_price:.4f}"
                        )
                        print(f"   Fee: {fee} {fee_currency}")
                        filled_count += 1

                    if fill_latency_seconds > 0:
                        self._record_fill_latency(symbol, fill_latency_seconds)
                        daily = self.state.setdefault("daily", {})
                        prev_avg = float(daily.get("avg_buy_fill_latency_seconds", 0.0) or 0.0)
                        prev_samples = int(daily.get("buy_fill_samples", 0) or 0)
                        new_samples = prev_samples + 1
                        daily["avg_buy_fill_latency_seconds"] = (
                            ((prev_avg * prev_samples) + fill_latency_seconds) / new_samples
                        )
                        daily["buy_fill_samples"] = new_samples
                        self._save_memory()

                    # Successful fill clears stale-cancel escalation history for this symbol.
                    self._reset_stale_buy_cancel_count(symbol)
                    self.agent_memory.setdefault("stale_buy_last_cancel", {}).pop(symbol, None)
                    self._save_memory()

                    # Delete the pending order regardless
                    del buy_orders[symbol]
                    self._save_state()

                elif is_active:
                    # Throughput policy: actively free capital from stale, unfilled buy orders.
                    # Only applies to fully unfilled active buys.
                    if canceled_count >= stale_buy_max_per_cycle:
                        continue
                    created_at = int(getattr(order, "created_at", 0) or 0)
                    age_seconds = (
                        max(0.0, (time.time() * 1000 - created_at) / 1000.0) if created_at > 0 else 0
                    )
                    soft_stale = age_seconds >= stale_buy_seconds and (
                        len(buy_orders) >= pressure_trigger
                        or (under_capital_pressure and len(buy_orders) >= pressure_min_pending)
                    )
                    hard_stale = age_seconds >= stale_buy_hard_seconds
                    if deal_size <= 0 and created_at > 0 and (soft_stale or hard_stale):
                        try:
                            await self.client.cancel_order(order_id)
                            self.log_event(
                                f"   [STALE BUY CANCELED] {symbol}: age={age_seconds:.0f}s | "
                                f"soft={soft_stale} hard={hard_stale} (soft>={stale_buy_seconds}s hard>={stale_buy_hard_seconds}s) | "
                                f"avail=${available_usdt:.2f} | pending={len(buy_orders)} | pressure={under_capital_pressure}"
                            )
                            if symbol in buy_orders:
                                del buy_orders[symbol]
                            daily = self.state.setdefault("daily", {})
                            daily["orders_cancelled"] = int(daily.get("orders_cancelled", 0) or 0) + 1
                            prev_stale_cancels = daily.get("stale_buy_cancels", 0)
                            try:
                                prev_stale_cancels = int(prev_stale_cancels or 0)
                            except Exception:
                                prev_stale_cancels = 0
                            daily["stale_buy_cancels"] = prev_stale_cancels + 1
                            reentry_cooldown_seconds = self._next_stale_buy_reentry_cooldown(symbol)
                            self._mark_buy_reentry_cooldown(symbol, reentry_cooldown_seconds)
                            self._record_stale_buy_cancel(
                                symbol, float(order_info.get("price", 0) or order.price or 0)
                            )
                            canceled_count += 1
                            self._save_state()
                            self._save_memory()
                            continue
                        except Exception as cancel_e:
                            self.log_event(f"   [STALE BUY CANCEL WARN] {symbol}: {cancel_e}")
                else:
                    # Order inactive with zero reported fills. Check live balance to avoid missing fills.
                    if live_balances_cache is None:
                        try:
                            live_balances_cache = await self.client.get_all_balances(min_value_usd=0)
                        except Exception:
                            live_balances_cache = {}

                    bal_row = (
                        live_balances_cache.get(symbol, {})
                        if isinstance(live_balances_cache, dict)
                        else {}
                    )
                    exch_total_qty = float(bal_row.get("balance", 0) or 0)
                    exch_available_qty = float(bal_row.get("available", 0) or 0)
                    symbol_price = float(order_info.get("price", 0) or 0)
                    if symbol_price <= 0:
                        ticker = self.latest_tickers.get(symbol)
                        if ticker and getattr(ticker, "price", 0):
                            symbol_price = float(ticker.price)
                        else:
                            try:
                                t = await self.client.get_ticker(f"{symbol}-USDT")
                                symbol_price = float(getattr(t, "price", 0) or 0)
                            except Exception:
                                symbol_price = 0.0
                    exch_value = exch_total_qty * symbol_price if symbol_price > 0 else 0.0

                    if exch_total_qty > 0 and exch_value >= 1.0:
                        self.log_event(
                            f"   [PENDING RECOVERED] {symbol}: inactive order but live balance={exch_total_qty:.8f}, reconstructing position"
                        )
                        if symbol in self.state["positions"]:
                            self.state["positions"][symbol]["quantity"] = exch_total_qty
                            if symbol_price > 0:
                                self.state["positions"][symbol]["buy_price"] = symbol_price
                            self.state["positions"][symbol]["current_price"] = symbol_price
                        else:
                            pos = {
                                "symbol": symbol,
                                "quantity": exch_total_qty,
                                "buy_price": symbol_price,
                                "current_price": symbol_price,
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
                            self.state["positions"][symbol] = pos
                            self.state["daily"]["trades"] += 1
                        if symbol in buy_orders:
                            del buy_orders[symbol]
                        self._save_state()
                        continue

                    # No live balance => clear stale marker.
                    if symbol in buy_orders:
                        self.log_event(
                            f"   [PENDING CLEARED] {symbol}: inactive with zero fill (avail={exch_available_qty:.8f}, total={exch_total_qty:.8f}), removing stale pending order"
                        )
                        del buy_orders[symbol]
                        self._save_state()

            except Exception as e:
                error_str = str(e)
                if "The order does not exist" in error_str or "order.*not.*exist" in error_str:
                    # Order no longer exists on exchange, remove from pending
                    self.log_event(
                        f"   [ORDER EXPIRED] {symbol}: Order no longer exists on exchange"
                    )
                    if symbol in buy_orders:
                        del buy_orders[symbol]
                        self._save_state()
                else:
                    self.log_event(f"   [PENDING CHECK] {symbol}: {e}")
                pass

        if filled_count > 0:
            self._save_state()

    async def manage_stale_sell_orders(self):
        """
        Throughput policy: keep stale sell limits near the top of book
        so capital is recycled faster.
        """
        try:
            open_orders = await self.client.get_open_orders()
            if not open_orders:
                return

            now_ms = int(time.time() * 1000)
            stale_seconds = int(self.config.get("stale_sell_reprice_seconds", 60))
            hard_seconds = int(self.config.get("stale_sell_hard_seconds", 180))
            stale_sell_min_projected_profit = float(
                self.config.get("stale_sell_min_projected_profit_usdt", 0.02)
            )
            cooldown_seconds = int(self.config.get("stale_reprice_cooldown_seconds", 45))
            max_reprices = int(self.config.get("stale_reprice_max_per_cycle", 2))
            repriced = 0

            meta = self.state.setdefault("execution_meta", {})
            last_reprice = meta.setdefault("last_sell_reprice", {})

            for order in open_orders:
                if repriced >= max_reprices:
                    break

                # Dict-oriented handling (live KuCoin path)
                order_side = str(order.get("side", "")).lower().strip() if isinstance(order, dict) else ""
                if order_side != "sell":
                    continue

                full_symbol = str(order.get("symbol", "")).strip()
                symbol = full_symbol.replace("-USDT", "").replace("-USDC", "")
                if not full_symbol.endswith("-USDT"):
                    continue
                if symbol not in self.state.get("positions", {}):
                    continue

                try:
                    order_id = str(order.get("id", "") or order.get("orderId", "") or "")
                    order_price = float(order.get("price", 0) or 0)
                    order_size = float(order.get("size", 0) or 0)
                    created_at = int(order.get("createdAt", 0) or 0)
                except (TypeError, ValueError):
                    continue

                if not order_id or order_price <= 0 or order_size <= 0 or created_at <= 0:
                    continue

                age_seconds = max(0, (now_ms - created_at) / 1000.0)
                if age_seconds < stale_seconds:
                    continue

                last_ts = int(last_reprice.get(order_id, 0) or 0)
                if last_ts > 0 and ((now_ms - last_ts) / 1000.0) < cooldown_seconds:
                    continue

                rules = self.symbol_rules.get(symbol, {})
                price_increment = float(rules.get("priceIncrement", 0.0) or 0.0)
                if price_increment <= 0:
                    price_increment = max(order_price * 0.0001, 1e-10)

                try:
                    orderbook = await self.client.get_orderbook(full_symbol, limit=20)
                except Exception as e:
                    self.log_event(f"   [STALE SELL] {symbol}: orderbook unavailable ({e})")
                    continue

                if not orderbook.bids or not orderbook.asks:
                    continue

                best_bid = float(orderbook.bids[0][0])
                top_asks = [float(a[0]) for a in orderbook.asks[:3] if a and float(a[0]) > 0]
                if not top_asks or best_bid <= 0:
                    continue

                # Keep order competitive near top-3 asks, and force tighter pricing for hard-stale orders.
                target_price = min(top_asks)
                top3_ceiling = max(top_asks)
                if order_price <= top3_ceiling and age_seconds < hard_seconds:
                    continue

                spread = max(0.0, target_price - best_bid)
                if spread > price_increment * 2:
                    target_price = max(best_bid + price_increment, target_price - price_increment)
                if age_seconds >= hard_seconds:
                    target_price = max(best_bid + price_increment, min(target_price, best_bid + (2 * price_increment)))

                # Round down to valid increment.
                target_price = round_down_to_increment(target_price, price_increment)
                if target_price <= 0:
                    continue
                if target_price >= order_price:
                    continue

                # Profitability guard: never reprice below fee-aware minimum profitable exit.
                pos = self.state.get("positions", {}).get(symbol, {}) or {}
                buy_price = float(pos.get("buy_price", 0) or 0)
                qty = float(pos.get("quantity", order_size) or order_size or 0)
                est_friction = float(self._estimate_total_friction_for_symbol(symbol) or 0)
                if buy_price > 0 and qty > 0 and est_friction < 0.999:
                    min_profitable_price = (buy_price + (stale_sell_min_projected_profit / qty)) / (
                        1.0 - est_friction
                    )
                    min_profitable_price = round_down_to_increment(
                        min_profitable_price, price_increment
                    )
                    if target_price < min_profitable_price:
                        self.log_event(
                            f"   🛡️ STALE SELL GUARD: {symbol} reprice blocked ${target_price:.8f} < min profitable ${min_profitable_price:.8f}"
                        )
                        continue

                try:
                    await self.client.cancel_order(order_id)
                    await asyncio.sleep(0.1)
                    await self.client.create_order(
                        symbol=full_symbol,
                        side="sell",
                        type="limit",
                        price=target_price,
                        size=order_size,
                    )
                    repriced += 1
                    last_reprice[order_id] = now_ms
                    self.log_event(
                        f"   ♻️ STALE SELL REPRICE: {symbol} age={age_seconds:.0f}s "
                        f"${order_price:.8f} -> ${target_price:.8f}"
                    )
                except Exception as e:
                    self.log_event(f"   [STALE SELL WARN] {symbol}: reprice failed ({e})")

            if repriced > 0:
                self._save_state()
        except Exception as e:
            self.log_event(f"   [STALE SELL ERROR] {e}")

    async def apply_zombie_pruning(self, strategy, opportunities):
        """
        Throughput policy: evict stagnant positions when capital is below
        minimum deployable trade size and fresh opportunities exist.
        """
        try:
            if not opportunities:
                return

            min_trade = TRADING.POSITION.MIN_CAPITAL_PER_TRADE
            if float(strategy.get("available", 0) or 0) >= min_trade:
                return

            max_hold_minutes = float(self.config.get("zombie_max_hold_minutes", 30))
            stagnation_band = float(self.config.get("zombie_stagnation_band_pct", 0.002))
            max_evictions = int(self.config.get("zombie_max_evictions_per_cycle", 1))
            zombie_allow_loss = bool(self.config.get("zombie_prune_allow_loss", False))
            zombie_min_pnl_pct = float(self.config.get("zombie_prune_min_pnl_pct", 0.0))
            zombie_min_projected_profit = float(
                self.config.get("zombie_prune_min_projected_profit_usdt", 0.02)
            )
            if max_evictions <= 0:
                return

            sell_orders = self.state.get("capital_awareness", {}).get("sell_orders", {})
            candidates = []
            now = datetime.now()

            for sym, pos in list(self.state.get("positions", {}).items()):
                if sym in sell_orders and sell_orders.get(sym):
                    continue

                opened_raw = pos.get("opened")
                if not opened_raw:
                    continue

                try:
                    opened_dt = datetime.fromisoformat(str(opened_raw).replace("Z", "+00:00"))
                    if opened_dt.tzinfo is not None:
                        opened_dt = opened_dt.astimezone().replace(tzinfo=None)
                except Exception:
                    continue

                age_minutes = (now - opened_dt).total_seconds() / 60.0
                if age_minutes < max_hold_minutes:
                    continue

                buy_price = float(pos.get("buy_price", 0) or 0)
                current_price = float(pos.get("current_price", 0) or buy_price or 0)
                if buy_price <= 0 or current_price <= 0:
                    continue

                pnl_pct = (current_price - buy_price) / buy_price
                if abs(pnl_pct) > stagnation_band:
                    continue

                candidates.append((age_minutes, abs(pnl_pct), sym, current_price, pnl_pct))

            if not candidates:
                return

            # Evict oldest, flattest positions first.
            candidates.sort(key=lambda x: (x[0], -x[1]), reverse=True)
            evicted = 0
            for age_minutes, _, sym, exit_price, pnl_pct in candidates:
                if evicted >= max_evictions:
                    break

                pos = self.state.get("positions", {}).get(sym) or {}
                qty = float(pos.get("quantity", 0) or 0)
                buy_price = float(pos.get("buy_price", 0) or 0)
                if qty <= 0 or buy_price <= 0 or exit_price <= 0:
                    continue
                est_fees = qty * exit_price * self._estimate_total_friction_for_symbol(sym)
                projected_profit = (qty * (exit_price - buy_price)) - est_fees
                if (not zombie_allow_loss) and (pnl_pct < zombie_min_pnl_pct):
                    self.log_event(
                        f"   🛡️ ZOMBIE PRUNE GUARD: skip {sym} pnl={pnl_pct * 100:+.2f}% < {zombie_min_pnl_pct * 100:+.2f}%"
                    )
                    continue
                if projected_profit < zombie_min_projected_profit:
                    self.log_event(
                        f"   🛡️ ZOMBIE PRUNE GUARD: skip {sym} projected net ${projected_profit:+.4f} < ${zombie_min_projected_profit:.4f}"
                    )
                    continue

                self.log_event(
                    f"   🧹 ZOMBIE PRUNE: {sym} age={age_minutes:.1f}m "
                    f"pnl={pnl_pct * 100:+.2f}% projected_net=${projected_profit:+.4f} to free deployable capital"
                )
                closed = await self.close_position(
                    sym,
                    "THROUGHPUT_ZOMBIE_PRUNE",
                    exit_price,
                    pnl_pct,
                    strategy,
                )
                if closed:
                    evicted += 1

            if evicted > 0:
                # Refresh deployable capital after evictions.
                await self._refresh_strategy_available(strategy, "zombie_prune")
                self.log_event(
                    f"   ✅ ZOMBIE PRUNE COMPLETE: evicted={evicted}, available=${strategy['available']:.2f}"
                )
        except Exception as e:
            self.log_event(f"   [ZOMBIE PRUNE ERROR] {e}")

    async def close_position(self, symbol, reason, exit_price, pnl_pct, strategy) -> bool:
        """Close position and learn. Returns True if closed successfully, False otherwise."""
        pos = self.state["positions"].get(symbol)
        if self._is_recycle_reason(reason) and pos:
            min_hold_seconds = max(0, int(self.config.get("recycle_min_hold_seconds", 120)))
            hold_seconds = self._position_hold_seconds(pos)
            if hold_seconds < min_hold_seconds:
                self.log_event(
                    f"   🛡️ RECYCLE HOLD GUARD: skip close {symbol} ({reason}) hold={hold_seconds:.0f}s < {min_hold_seconds}s"
                )
                return False

        allowed, guard_reason = self._recycle_guard_check(symbol, reason)
        if not allowed:
            self.log_event(
                f"   🛡️ RECYCLE THROTTLE: skip close {symbol} ({reason}) - {guard_reason}"
            )
            return False

        if self._close_lock is None:
            self._close_lock = asyncio.Lock()
        async with self._close_lock:
            if symbol in self._closing_symbols:
                self.log_event(f"   [CLOSE SKIP] {symbol} close already in-flight")
                return False
            self._closing_symbols.add(symbol)
            self.log_event(f"   [CLOSE FN START] {symbol} reason={reason}")
        pos = self.state["positions"].get(symbol)
        self.log_event(f"   [CLOSE FN FOUND] {symbol}: {pos is not None}")
        if not pos:
            self.log_event(f"   [CLOSE FN END] Position not found for {symbol}")
            buy_orders = self.state.get("capital_awareness", {}).get("buy_orders", {})
            if symbol in buy_orders:
                del buy_orders[symbol]
                self._save_state()
            self._closing_symbols.discard(symbol)
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
            self._closing_symbols.discard(symbol)
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

            # Use MARKET for PERFECT conditions (instant exit), LIMIT otherwise
            # In perfect storm, we want instant exit to capture profits
            is_take_profit = "TAKE_PROFIT" in reason
            is_perfect = getattr(self, "_perfect_storm", False)
            take_profit_force_limit = bool(self.config.get("take_profit_force_limit", True))

            if is_perfect and is_take_profit and not take_profit_force_limit:
                # MARKET order for instant exit in perfect conditions
                close_type = "market"
                close_price = 0
                self.log_event(
                    f"   [CLOSE EXEC] Creating MARKET sell for {symbol} @ CURRENT (PERFECT CONDITIONS - MAX SPEED)"
                )
            elif is_take_profit:
                # Limit order at exit price to save maker fees
                close_type = "limit"
                close_price = exit_price
                self.log_event(
                    f"   [CLOSE EXEC] Creating LIMIT sell for {symbol} @ ${close_price:.6f} with qty={quantity}"
                )
            else:
                # Market order for immediate execution on SL/Recycle
                close_type = "market"
                close_price = 0
                self.log_event(
                    f"   [CLOSE EXEC] Creating MARKET sell for {symbol} with qty={quantity}"
                )

            # Check if there's already an open sell order for this symbol
            existing_sell_orders = self.state.get("capital_awareness", {}).get("sell_orders", {})
            if symbol in existing_sell_orders and existing_sell_orders[symbol]:
                self.log_event(
                    f"   [CLOSE WARN] Already has open sell order for {symbol}, skipping"
                )
                self._closing_symbols.discard(symbol)
                return False

            try:
                order_result = await asyncio.wait_for(
                    self.client.create_order(
                        symbol=f"{symbol}-USDT",
                        side="sell",
                        type=close_type,
                        price=close_price,
                        size=quantity,
                    ),
                    timeout=10.0,
                )
                # Fetch order details and require confirmed fills before finalizing close.
                actual_fee = 0.0
                actual_fill_price = exit_price
                filled_qty = 0.0
                if order_result and order_result.order_id:
                    wait_seconds = (
                        float(self.config.get("take_profit_limit_wait_seconds", 2))
                        if close_type == "limit"
                        else 1.0
                    )
                    deadline = time.time() + max(0.5, wait_seconds)
                    filled_order = None
                    while time.time() <= deadline:
                        await asyncio.sleep(0.5)
                        filled_order = await self.client.get_order(
                            order_result.order_id, f"{symbol}-USDT"
                        )
                        if not filled_order:
                            continue
                        actual_fee = float(getattr(filled_order, "fee", 0) or 0)
                        actual_fill_price = float(
                            getattr(filled_order, "avg_price", 0) or actual_fill_price
                        )
                        filled_qty = float(getattr(filled_order, "filled_size", 0) or 0)
                        if (
                            str(getattr(filled_order, "status", "")) != "ACTIVE"
                            or filled_qty >= (quantity * 0.999)
                        ):
                            break

                    # TP limit orders that remain unfilled are force-closed with market fallback.
                    if (
                        close_type == "limit"
                        and filled_qty < (quantity * 0.999)
                        and bool(self.config.get("take_profit_limit_fallback_market", True))
                    ):
                        remaining_qty = max(0.0, quantity - filled_qty)
                        try:
                            await self.client.cancel_order(order_result.order_id)
                        except Exception:
                            pass
                        if remaining_qty > 0:
                            self.log_event(
                                f"   [CLOSE FALLBACK] {symbol}: TP limit unfilled, fallback MARKET for {remaining_qty:.8f}"
                            )
                            market_result = await asyncio.wait_for(
                                self.client.create_order(
                                    symbol=f"{symbol}-USDT",
                                    side="sell",
                                    type="market",
                                    price=0,
                                    size=remaining_qty,
                                ),
                                timeout=10.0,
                            )
                            await asyncio.sleep(0.5)
                            market_order = await self.client.get_order(
                                market_result.order_id, f"{symbol}-USDT"
                            )
                            if market_order:
                                market_qty = float(getattr(market_order, "filled_size", 0) or 0)
                                market_fee = float(getattr(market_order, "fee", 0) or 0)
                                market_price = float(
                                    getattr(market_order, "avg_price", 0) or actual_fill_price or exit_price
                                )
                                total_qty = filled_qty + market_qty
                                if total_qty > 0:
                                    weighted_price = (
                                        (filled_qty * actual_fill_price) + (market_qty * market_price)
                                    ) / total_qty
                                    actual_fill_price = weighted_price
                                filled_qty = total_qty
                                actual_fee += market_fee

                # If close wasn't fully filled, keep position with remaining qty and retry next cycle.
                if filled_qty < (quantity * 0.999):
                    if filled_qty > 0:
                        remaining_qty = max(0.0, quantity - filled_qty)
                        self.state["positions"][symbol]["quantity"] = remaining_qty
                        self._save_state()
                        self.log_event(
                            f"   [CLOSE PARTIAL] {symbol}: filled={filled_qty:.8f}, remaining={remaining_qty:.8f}"
                        )
                    else:
                        self.log_event(
                            f"   [CLOSE PENDING] {symbol}: order not filled yet, keeping position open"
                        )
                    self._closing_symbols.discard(symbol)
                    return False

                self.state["daily"]["orders_filled"] += 1
                self.log_event(
                    f"   [CLOSE SUCCESS] {symbol} filled qty={filled_qty:.8f} @ {actual_fill_price:.8f}"
                )

                # 🧹 CLEANUP: Remove from buy_orders tracking
                buy_orders = self.state.get("capital_awareness", {}).get("buy_orders", {})
                if symbol in buy_orders:
                    del buy_orders[symbol]

            except asyncio.TimeoutError:
                self.log_event(f"   [CLOSE ERROR] Timeout for {symbol}")
                self._closing_symbols.discard(symbol)
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

                            # Use same order type as original attempt
                            await asyncio.wait_for(
                                self.client.create_order(
                                    symbol=f"{symbol}-USDT",
                                    side="sell",
                                    type=close_type,
                                    price=close_price,
                                    size=quantity,
                                ),
                                timeout=10.0,
                            )
                            self.log_event(f"   [CLOSE SUCCESS] {symbol} retry succeeded")
                        else:
                            raise Exception(f"Symbol data not found for {symbol}")
                    except Exception as retry_error:
                        self.log_event(f"   [CLOSE FAIL] {symbol} retry failed: {retry_error}")
                        self._closing_symbols.discard(symbol)
                        return False

                elif (
                    "Balance insufficient" in error_msg
                    or "not exist" in error_msg.lower()
                    or "50020" in error_msg
                    or "minimum" in error_msg.lower()
                    or "funds should more than" in error_msg.lower()
                ):
                    self.log_event(f"   [CLOSE WARN] {symbol} - insufficient funds, reconciling")
                    try:
                        balances = await self.client.get_all_balances(min_value_usd=0)
                        sym_bal = balances.get(symbol, {}) if isinstance(balances, dict) else {}
                        exch_available = float(sym_bal.get("available", 0) or 0)
                        exch_total = float(sym_bal.get("balance", exch_available) or exch_available)
                        if exch_total <= 0:
                            self.log_event(
                                f"   [CLOSE RECONCILE] {symbol}: exchange balance is 0, removing stale local position"
                            )
                            self.state.get("positions", {}).pop(symbol, None)
                            self.state.get("capital_awareness", {}).get("buy_orders", {}).pop(
                                symbol, None
                            )
                            self.state.get("capital_awareness", {}).get("sell_orders", {}).pop(
                                symbol, None
                            )
                            self._save_state()
                            try:
                                from ibis.database.db import IbisDB

                                db = IbisDB()
                                db.close_position(
                                    symbol=f"{symbol}-USDT",
                                    exit_price=exit_price,
                                    reason="RECONCILED_NO_EXCHANGE_BALANCE",
                                    actual_fee=0.0,
                                )
                            except Exception:
                                pass
                            self._closing_symbols.discard(symbol)
                            return True

                        adjusted_qty = round_down_to_increment(exch_total, base_increment)
                        if exch_available <= 0 and exch_total > 0:
                            # Position is fully locked (usually by open sell order). Keep it tracked.
                            if symbol in self.state.get("positions", {}):
                                self.state["positions"][symbol]["quantity"] = adjusted_qty
                                self._save_state()
                            self.log_event(
                                f"   [CLOSE RECONCILE] {symbol}: balance locked (avail=0, total={exch_total}), keeping position tracked"
                            )
                            self._closing_symbols.discard(symbol)
                            return False

                        if adjusted_qty <= 0:
                            self.log_event(
                                f"   [CLOSE RECONCILE] {symbol}: only dust remains ({exch_total}), removing local position"
                            )
                            self.state.get("positions", {}).pop(symbol, None)
                            self.state.get("capital_awareness", {}).get("buy_orders", {}).pop(
                                symbol, None
                            )
                            self.state.get("capital_awareness", {}).get("sell_orders", {}).pop(
                                symbol, None
                            )
                            self._save_state()
                            self._closing_symbols.discard(symbol)
                            return True

                        if symbol in self.state.get("positions", {}):
                            self.state["positions"][symbol]["quantity"] = adjusted_qty
                            self._save_state()
                        self.log_event(
                            f"   [CLOSE RECONCILE] {symbol}: adjusted local qty {original_qty} -> {adjusted_qty}, will retry next cycle"
                        )
                    except Exception as rec_err:
                        self.log_event(f"   [CLOSE RECONCILE ERROR] {symbol}: {rec_err}")
                    self._closing_symbols.discard(symbol)
                    return False
                else:
                    self._closing_symbols.discard(symbol)
                    return False

            # Calculate REAL PnL from actual fill price and actual fees
            close_qty = float(filled_qty or quantity)
            trade_volume = close_qty * actual_fill_price
            estimated_fees = trade_volume * self._estimate_total_friction_for_symbol(symbol)

            # Use actual fees from KuCoin if available, otherwise estimate
            if actual_fee > 0:
                pnl = (close_qty * (actual_fill_price - pos["buy_price"])) - actual_fee
                fees_used = actual_fee
                self.log_event(f"   [CLOSE PnL] Using ACTUAL fees: {actual_fee:.6f} USDT")
            else:
                pnl = (close_qty * (actual_fill_price - pos["buy_price"])) - estimated_fees
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
            self._save_state()  # Save again after capital update

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

            self._record_recycle_close(symbol, reason)
            self._closing_symbols.discard(symbol)
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
                self._closing_symbols.discard(symbol)
                return False
            else:
                print(f"⚠️ Unexpected close error for {symbol}")
                buy_orders = self.state.get("capital_awareness", {}).get("buy_orders", {})
                if symbol in buy_orders:
                    del buy_orders[symbol]
                if symbol in self.state.get("positions", {}):
                    del self.state["positions"][symbol]
                self._save_state()
                self._closing_symbols.discard(symbol)
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

                                    self.log_event(
                                        f"      🛡️ TRAILING STOP UPDATE: {sym} | "
                                        f"SL: ${old_sl:.4f} → ${new_stop:.4f} | "
                                        f"Price: ${price:.4f}"
                                    )
                                self._save_state()
                        except Exception as e:
                            # Log trailing stop error but continue
                            pass
                except Exception as e:
                    # Log error but continue
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
                    except (TypeError, ValueError) as e:
                        self.log_event(f"⚠️ Failed to parse data: {e}")
                    except Exception as e:
                        self.log_event(f"⚠️ Unexpected error: {e}")

                if price > 0:
                    value = balance * price
                    holdings_value += value
                    holdings_display.append(f"{currency}:${value:.2f}")
                    holdings_positions.append((currency, balance, price, value))

        total_assets = usdt_balance + holdings_value
        pnl = self.state["daily"]["pnl"]  # Will be updated from trade history

        print(f"\n{'═' * 100}")
        print(
            f"   🦅 IBIS MAXIMUM AUTONOMOUS INTELLIGENCE | CYCLE {cycles:03d} | {datetime.now().strftime('%H:%M:%S')} | ${total_assets:.2f}"
        )
        print(f"{'═' * 100}")

        if not self.market_intel:
            print(f"\n   🔍 SCANNING MARKET...")
            # await self.analyze_market_intelligence()  # Disabled - use simple scoring

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

        # Show PERFECT storm status
        if getattr(self, "_perfect_storm", False):
            print(f"   │ {'🌟 PERFECT STORM: ACTIVE!':<80} │")
            print(f"   │ {'🚀 MAX AGGRESSION - ALL MARKET ORDERS':<80} │")

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
                    except (TypeError, ValueError) as e:
                        self.log_event(f"⚠️ Failed to parse data: {e}")
                    except Exception as e:
                        self.log_event(f"⚠️ Unexpected error: {e}")

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

        pnl = self.state["daily"]["pnl"]  # Updated from trade history
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

                score_display = f"{float(intel.get('score', 0) or 0):.2f}"
                print(
                    f"   │ {rank:<4} {sym:<10} {score_display:<8} ${intel['price']:<13.4f} {change_str:<10} {intel['volatility'] * 100:.2f}%   {vol_str:<18} {risk_indicator[risk_level]} {type_indicator[opp_type]} {insights_text:<30} │"
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

            position_value = (
                strategy["available"] * TRADING.MULTIPLIERS.BASE_SIZE_PCT * final_multiplier
            )
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
                self._recycle_closes_this_cycle = 0

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
                self._save_state()
                await self.update_capital_awareness()
                await self.check_pending_orders()

                # 🧠 Step 0b: Self-Learning from Past Performance
                await self.learn_from_experience()

                # 🧠 Step 0c: Adaptive Risk Management
                await self.update_adaptive_risk()

                reconcile_every = max(1, int(self.config.get("reconcile_cycle_interval", 15)))
                # Reconcile on startup and then on fixed cadence to reduce state/live drift windows.
                if cycle == 1 or cycle % reconcile_every == 0:
                    await self.reconcile_holdings()
                    await self.sync_pnl_from_kucoin()

                # Step 2: Analyze market intelligence
                self.log_event("   🔍 Starting Market Analysis cycle...")
                await self.analyze_market_intelligence()

                # Step 3: Detect regime
                regime = "VOLATILE"
                self.log_event(f"   📊 Regime: {regime} (default)")

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

                # Simple inline market scan if market_intel is empty
                if not self.market_intel:
                    self.log_event("   ⚡ Quick market scan...")
                    try:
                        tickers = await self.client.get_tickers()
                        min_score = self.config.get("min_score", 70)  # Use strategy threshold
                        for t in tickers[:20]:  # Top 20 by volume
                            sym = t.symbol.replace("-USDT", "")
                            if t.symbol.endswith("-USDT"):
                                change = float(getattr(t, "change_24h", 0) or 0)
                                vol = float(getattr(t, "volume_24h", 0) or 0)
                                score = 50 + (abs(change) * 5)  # Simple score based on momentum
                                # Skip symbols with scores below threshold
                                if score < min_score:
                                    continue
                                self.market_intel[sym] = {
                                    "symbol": sym,
                                    "price": float(t.price),
                                    "change_24h": change,
                                    "volume_24h": vol,
                                    "score": min(95, max(5, score)),
                                    "volatility": 0.02,
                                    "momentum_1h": change,
                                }
                        self.log_event(
                            f"   ✅ Scanned {len(self.market_intel)} symbols (score ≥ {min_score})"
                        )
                    except Exception as e:
                        self.log_event(f"   ⚠️ Scan failed: {e}")

                # Step 7 & 10: Hunt for ALL opportunities (HYPER TRADING)
                self.log_event(
                    f"   🎯 ANALYZING {len(self.market_intel)} opportunities for trade entry..."
                )
                opportunities = await self.find_all_opportunities(strategy)
                opportunities = self._admission_rank_opportunities(opportunities, strategy)
                self.log_event(f"   🔥 FOUND {len(opportunities)} TRADEABLE candidates")
                best = opportunities[0] if opportunities else None

                # Step 6: Dynamic Position Monitoring (CRITICAL)
                self.log_event("   🕵️ Checking existing positions for TP/SL/Decay...")
                await self.check_positions(strategy)
                await self.manage_stale_sell_orders()
                await self.update_capital_awareness()

                open_count = len(self.state["positions"])
                self.log_event(
                    f"   🔄 ENTERING TRADE LOOP: {len(opportunities)} opportunities, current positions: {open_count}"
                )

                # Throughput policy: prune stagnant inventory only when capital is below minimum
                # and fresh candidates are available.
                await self.apply_zombie_pruning(strategy, opportunities)

                # Suppress capital spam: only log if we have good opportunities but literally zero/dust cash
                has_insufficient_capital = (
                    strategy["available"] < TRADING.POSITION.MIN_CAPITAL_PER_TRADE
                )
                if has_insufficient_capital and opportunities:
                    if cycle % 10 == 0 or cycle == 1:  # Only log every 10 cycles to prevent spam
                        self.log_event(
                            f"   🛑 Insufficient capital (${strategy['available']:.2f} < ${TRADING.POSITION.MIN_CAPITAL_PER_TRADE} minimum)"
                        )

                recycle_decision_made = False
                alpha_recycle_decision_made = False
                tracked_open_order_symbols = set(
                    (self.state.get("capital_awareness", {}).get("buy_orders", {}) or {}).keys()
                )
                tracked_open_order_symbols.update(
                    (self.state.get("capital_awareness", {}).get("sell_orders", {}) or {}).keys()
                )
                for opportunity in opportunities:
                    min_trade_capital = TRADING.POSITION.MIN_CAPITAL_PER_TRADE
                    max_open_buy_orders = int(self.config.get("max_open_buy_orders", 8))
                    pending_buys_now = len(
                        self.state.get("capital_awareness", {}).get("buy_orders", {}) or {}
                    )
                    recycle_requires_empty_buy_queue = bool(
                        self.config.get("recycle_requires_empty_buy_queue", True)
                    )
                    if pending_buys_now >= max_open_buy_orders:
                        self.log_event(
                            f"   🧱 QUEUE GUARD: pending buys {pending_buys_now}/{max_open_buy_orders}, deferring new entries this cycle"
                        )
                        break
                    # 🚀 PROFIT RECYCLING: Only recycle for high-quality opportunities (score >= 70)
                    # This prevents costly recycling for marginal opportunities
                    self.log_event(
                        f"   [RECYCLE TEST] available=${strategy['available']:.2f}, score={opportunity['score']:.1f}"
                    )
                    if (
                        not recycle_decision_made
                        and strategy["available"] < min_trade_capital
                        and opportunity["score"] >= 70
                    ):
                        if recycle_requires_empty_buy_queue and pending_buys_now > 0:
                            self.log_event(
                                f"   🧱 RECYCLE DEFERRED: pending buys={pending_buys_now}, waiting for queue to clear before recycling capital"
                            )
                            continue
                        self.log_event(
                            f"   🔱 CAPITAL RECYCLING: ${strategy['available']:.2f} available for {opportunity['symbol']} (Score: {opportunity['score']:.0f})"
                        )
                        recycle_decision_made = True

                        # Find best position to close by projected net after execution friction.
                        best_to_close = None
                        best_profit = -999.0
                        best_pnl = -999.0
                        for sym, pos in self.state["positions"].items():
                            qty = float(pos.get("quantity", 0) or 0)
                            buy_px = float(pos.get("buy_price", 0) or 0)
                            current_px = float(pos.get("current_price", 0) or buy_px or 0)
                            if qty <= 0 or buy_px <= 0 or current_px <= 0:
                                continue
                            pnl_pct = (current_px - buy_px) / buy_px
                            est_fees = qty * current_px * self._estimate_total_friction_for_symbol(sym)
                            projected_profit = (qty * (current_px - buy_px)) - est_fees
                            if projected_profit > best_profit:
                                best_profit = projected_profit
                                best_pnl = pnl_pct
                                best_to_close = (sym, pos, projected_profit)

                        if best_to_close:
                            sym, pos, projected_profit = best_to_close
                            recycle_allow_loss = bool(self.config.get("recycle_allow_loss", False))
                            recycle_min_pnl_pct = float(self.config.get("recycle_min_pnl_pct", 0.0))
                            recycle_min_projected_profit = float(
                                self.config.get("recycle_min_projected_profit_usdt", 0.03)
                            )
                            if projected_profit < recycle_min_projected_profit:
                                self.log_event(
                                    f"      🛡️ RECYCLE GUARD: skipping recycle close for {sym}, projected net ${projected_profit:+.4f} < ${recycle_min_projected_profit:.4f}"
                                )
                                continue
                            if (not recycle_allow_loss) and (best_pnl < recycle_min_pnl_pct):
                                self.log_event(
                                    f"      🛡️ RECYCLE GUARD: skipping recycle close for {sym} at {best_pnl * 100:+.2f}%"
                                )
                                continue
                            self.log_event(
                                f"      💰 RECYCLING: Closing {sym} at {best_pnl * 100:+.2f}% (projected net ${projected_profit:+.4f}) to fund {opportunity['symbol']}"
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
                            await self._refresh_strategy_available(strategy, "recycle_close")

                    # 🚀 AGGRESSIVE ALPHA RECYCLING: Clear positions for ANY high-score opportunity
                    is_strong = opportunity["score"] >= 85  # Only recycle for STRONG_SETUP+ signals
                    if (
                        not alpha_recycle_decision_made
                        and (strategy["available"] < min_trade_capital)
                        and is_strong
                    ):
                        if recycle_requires_empty_buy_queue and pending_buys_now > 0:
                            self.log_event(
                                f"   🧱 ALPHA RECYCLE DEFERRED: pending buys={pending_buys_now}, skipping recycle this cycle"
                            )
                            continue
                        self.log_event(
                            f"   🔱 STRONG SIGNAL: {opportunity['symbol']} (Score: {opportunity['score']:.0f}). Clearing stagnant capital..."
                        )
                        alpha_recycle_decision_made = True

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
                                    recycle_allow_loss = bool(
                                        self.config.get("recycle_allow_loss", False)
                                    )
                                    recycle_min_pnl_pct = float(
                                        self.config.get("recycle_min_pnl_pct", 0.0)
                                    )
                                    recycle_min_projected_profit = float(
                                        self.config.get("recycle_min_projected_profit_usdt", 0.03)
                                    )
                                    # Use ratio-space PnL for execution guards.
                                    # Stored `unrealized_pnl_pct` is in percentage points.
                                    pos_pnl = (current_px - buy_px) / buy_px if buy_px > 0 else 0.0
                                    qty = float(pos.get("quantity", 0) or 0)
                                    buy_px = float(pos.get("buy_price", 0) or 0)
                                    current_px = float(pos.get("current_price", 0) or buy_px or 0)
                                    if qty <= 0 or buy_px <= 0 or current_px <= 0:
                                        continue
                                    est_fees = (
                                        qty * current_px * self._estimate_total_friction_for_symbol(sym)
                                    )
                                    projected_profit = (qty * (current_px - buy_px)) - est_fees
                                    # 🔱 PARALYSIS BREAKER: If wallet is dead (<$1) and signal is strong (>80), kill the weakest
                                    is_paralyzed = (
                                        strategy["available"] < 1.0 and opportunity["score"] >= 80
                                    )
                                    if projected_profit < recycle_min_projected_profit:
                                        continue
                                    if (not recycle_allow_loss) and (pos_pnl < recycle_min_pnl_pct):
                                        continue

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
                                        await self._refresh_strategy_available(
                                            strategy, "alpha_recycle"
                                        )
                                        if (
                                            strategy["available"] >= min_trade_capital
                                        ):  # Enough to stop recycling
                                            break

                        if recycled_any:
                            open_count = len(
                                [
                                    pos
                                    for pos in self.state["positions"].values()
                                    if pos["mode"] != "PENDING_BUY"
                                ]
                            )
                            await self._refresh_strategy_available(strategy, "post_recycle")

                    if open_count < strategy["max_positions"]:
                        # 🛡️ HARD MINIMUM: Don't create dust positions
                        if strategy["available"] < min_trade_capital:
                            self.log_event(
                                f"   🛑 Insufficient capital (${strategy['available']:.2f} < ${min_trade_capital:.2f} minimum)"
                            )
                            break

                        # 🎯 SCORE CHECK: Only execute if opportunity meets minimum score threshold
                        min_score = self.config.get("min_score", 70)
                        if opportunity["score"] < min_score:
                            self.log_event(
                                f"   ❌ SKIPPING: {opportunity['symbol']} (Score: {opportunity['score']:.1f} < {min_score:.1f} threshold)"
                            )
                            continue

                        # 🛡️ CHECK FOR EXISTING POSITION OR OPEN ORDER BEFORE BUYING
                        symbol = opportunity["symbol"]

                        # Check if we already have a position in this symbol
                        if symbol in self.state["positions"]:
                            self.log_event(f"   🛑 SKIPPING: Already have position in {symbol}")
                            continue

                        # Check tracked open orders (synced by update_capital_awareness) to avoid duplicate buys.
                        if symbol in tracked_open_order_symbols:
                            self.log_event(f"   🛑 SKIPPING: Already have open order for {symbol}")
                            continue

                        cooldown_remaining = self._get_buy_reentry_cooldown_remaining(symbol)
                        if cooldown_remaining > 0:
                            self.log_event(
                                f"   🧊 SKIPPING: Reentry cooldown active for {symbol} ({cooldown_remaining:.0f}s remaining)"
                            )
                            continue

                        current_price = float(opportunity.get("price", 0) or 0)
                        price_guard_skip, price_guard_reason = self._stale_reentry_price_guard(
                            symbol, current_price
                        )
                        if price_guard_skip:
                            self.log_event(
                                f"   🧊 SKIPPING: Reentry price guard for {symbol} - {price_guard_reason}"
                            )
                            continue

                        # 🛡️ CHECK MINIMUM TRADE SIZE ($11 minimum)
                        position_size = await self.dynamic_position_sizing(
                            strategy, symbol, self.market_intel
                        )
                        if position_size < TRADING.POSITION.MIN_CAPITAL_PER_TRADE:
                            self.log_event(
                                f"   🛑 SKIPPING: Position size ${position_size:.2f} < $11 minimum for {symbol}"
                            )
                            continue

                        self.log_event(f"   🚀 HYPER-TRADE START: {symbol} (${position_size:.2f})")
                        await self.open_position(opportunity, strategy)
                        tracked_open_order_symbols.add(symbol)
                        self._save_state()  # Save state after opening position
                        open_count += 1
                        await asyncio.sleep(0.1)  # Hyper-fast execution

                        await self._refresh_strategy_available(strategy, "post_open")
                        if strategy["available"] < min_trade_capital:
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
