"""
IBIS Data Consolidation Layer
==============================
Ensures consistency between JSON state and SQLite database.
JSON State is source of truth for ibis_true_agent.py
SQLite DB is used for position_rotation.py and analytics
This layer syncs data bidirectionally without losing information.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


STATE_FILE = "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_true_state.json"
MEMORY_FILE = "/root/projects/Dont enter unless solicited/AGI Trader/data/ibis_true_memory.json"


def load_state() -> Dict:
    """Load JSON state file."""
    if not Path(STATE_FILE).exists():
        return {"positions": {}, "daily": {}, "capital_awareness": {}}
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {"positions": {}, "daily": {}, "capital_awareness": {}}


def save_state(state: Dict) -> bool:
    """Save JSON state file."""
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"Error saving state: {e}")
        return False


def load_memory() -> Dict:
    """Load JSON memory file."""
    default_memory = {
        "learned_regimes": {"avoid": "UNKNOWN", "best": "UNKNOWN"},
        "performance_by_symbol": {},
        "market_insights": [],
        "adaptation_history": [],
        "total_cycles": 0,
    }
    if not Path(MEMORY_FILE).exists():
        return default_memory
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return default_memory


def save_memory(memory: Dict) -> bool:
    """Save JSON memory file."""
    try:
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"Error saving memory: {e}")
        return False


def sync_db_trades_to_memory(db_trades: List[Dict]) -> Dict:
    """
    Sync trades from SQLite DB to JSON memory.
    Returns updated performance_by_symbol dict.
    """
    memory = load_memory()
    perf = memory.get("performance_by_symbol", {})

    for trade in db_trades:
        symbol = trade.get("symbol", "")
        reason = trade.get("reason", "unknown").lower()
        pnl = trade.get("pnl", 0)
        pnl_pct = trade.get("pnl_pct", 0)

        regime = "unknown"
        if "_" in symbol:
            parts = symbol.split("-")
            if len(parts) >= 1:
                symbol_only = parts[0]
        else:
            symbol_only = symbol

        strat_key = f"{regime}_{reason}"

        if strat_key not in perf:
            perf[strat_key] = {"trades": 0, "wins": 0, "losses": 0, "pnl": 0}

        perf[strat_key]["trades"] += 1
        if pnl > 0:
            perf[strat_key]["wins"] += 1
        else:
            perf[strat_key]["losses"] += 1
        perf[strat_key]["pnl"] += pnl

    memory["performance_by_symbol"] = perf
    return memory


def sync_db_positions_to_state(db_positions: List[Dict]) -> Dict:
    """
    Sync positions from SQLite DB to JSON state.
    Returns updated state dict.
    """
    state = load_state()
    state_positions = state.get("positions", {})

    for pos in db_positions:
        symbol = pos.get("symbol", "").replace("-USDT", "")
        if symbol in state_positions:
            continue

        state_positions[symbol] = {
            "symbol": symbol,
            "quantity": pos.get("quantity", 0),
            "buy_price": pos.get("entry_price", 0),
            "current_price": pos.get("current_price", 0),
            "mode": pos.get("mode", "EXISTING"),
            "regime": pos.get("regime", "unknown"),
            "opened": pos.get("opened_at", datetime.now().isoformat()),
            "opportunity_score": pos.get("agi_score", 50),
            "tp": pos.get("take_profit", 0),
            "sl": pos.get("stop_loss", 0),
            "highest_pnl": 0,
            "highest_pnl_display": "+0.00%",
        }

    state["positions"] = state_positions
    return state


def merge_daily_stats(state_daily: Dict, db_trades: List[Dict]) -> Dict:
    """
    Merge daily stats from both sources to ensure consistency.
    Prefers JSON state values if available.
    """
    if not state_daily:
        state_daily = {}

    if not db_trades:
        return state_daily

    wins = sum(1 for t in db_trades if t.get("pnl", 0) > 0)
    losses = sum(1 for t in db_trades if t.get("pnl", 0) <= 0)
    pnl = sum(t.get("pnl", 0) for t in db_trades)
    trades = len(db_trades)

    state_daily["trades"] = trades
    state_daily["wins"] = wins
    state_daily["losses"] = losses
    state_daily["pnl"] = round(pnl, 6)

    return state_daily


def sync_state_positions_to_db(state_positions: Dict, db):
    """
    Sync positions from JSON state to SQLite DB.
    """
    for symbol, pos in state_positions.items():
        db.update_position(
            symbol=f"{symbol}-USDT",
            quantity=pos.get("quantity", 0),
            price=pos.get("buy_price", 0),
            stop_loss=pos.get("sl"),
            take_profit=pos.get("tp"),
            agi_score=pos.get("opportunity_score", 50),
            agi_insight="AGI Confirmed",
            entry_fee=0,
            limit_sell_order_id=None,
            limit_sell_price=pos.get("tp"),
        )

    # Remove positions from DB that are not in state file
    db_positions = db.get_open_positions()
    for db_pos in db_positions:
        symbol = db_pos["symbol"].replace("-USDT", "")
        if symbol not in state_positions:
            db.close_position(db_pos["symbol"], db_pos["current_price"], reason="NOT_IN_STATE")


def run_full_sync(db) -> bool:
    """
    Run full bidirectional sync between DB and JSON files.
    Returns True if successful.
    """
    try:
        state = load_state()
        memory = load_memory()

        db_trades = db.get_trades(limit=1000)
        db_positions = db.get_open_positions()

        memory = sync_db_trades_to_memory(db_trades)
        state = sync_db_positions_to_state(db_positions)
        sync_state_positions_to_db(state.get("positions", {}), db)
        state["daily"] = merge_daily_stats(state.get("daily", {}), db_trades)
        state["updated"] = datetime.now().isoformat()

        if save_state(state) and save_memory(memory):
            print("✅ Data consolidation complete")
            return True
        else:
            print("❌ Failed to save consolidated data")
            return False

    except Exception as e:
        print(f"❌ Data consolidation error: {e}")
        return False


async def async_run_full_sync(db) -> bool:
    """Async wrapper for full sync."""
    return run_full_sync(db)


def cleanup_dust_positions(db=None, client=None, threshold: float = 1.0) -> Dict:
    """
    Clean up dust positions (< $1 value) from state.
    These positions are too small to matter but still count in position limits.
    Returns summary of cleaned positions.
    """
    state = load_state()
    positions = state.get("positions", {})
    cleaned = []

    for sym, pos in list(positions.items()):
        qty = pos.get("quantity", 0)
        price = pos.get("current_price", 0)
        value = qty * price

        if value < threshold:
            cleaned.append({"symbol": sym, "quantity": qty, "value": value, "reason": "dust"})
            del positions[sym]

    if cleaned:
        state["positions"] = positions
        state["updated"] = datetime.now().isoformat()
        save_state(state)
        print(f"🧹 Cleaned {len(cleaned)} dust positions: {[p['symbol'] for p in cleaned]}")

    return {"cleaned": cleaned, "count": len(cleaned)}


async def async_cleanup_dust_positions(threshold: float = 1.0) -> Dict:
    """Async wrapper for dust cleanup."""
    return cleanup_dust_positions(threshold=threshold)


if __name__ == "__main__":
    from ibis.database.db import IbisDB

    db = IbisDB()
    run_full_sync(db)
