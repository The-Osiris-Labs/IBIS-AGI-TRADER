#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
STATE = BASE / "data" / "ibis_true_state.json"
TRADES = BASE / "data" / "trade_history.json"
OUT = BASE / "data" / "hourly_kpi.log"


def _num(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return float(default)


def _parse_ts(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        t = float(v)
        if t > 1e12:
            t /= 1000
        return datetime.fromtimestamp(t, tz=timezone.utc)
    if isinstance(v, str):
        if v.isdigit():
            t = float(v)
            if t > 1e12:
                t /= 1000
            return datetime.fromtimestamp(t, tz=timezone.utc)
        try:
            s = v.replace("Z", "+00:00")
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return None
    return None


now = datetime.now(timezone.utc)

state = {}
if STATE.exists():
    try:
        state = json.loads(STATE.read_text())
    except Exception:
        state = {}

positions = state.get("positions", {}) or {}
rows_pos = []
for s, p in positions.items():
    hold_min = _num(p.get("hold_seconds", 0), 0) / 60
    buy = _num(p.get("buy_price", 0), 0)
    cur = _num(p.get("current_price", 0), 0)
    pnl_pct = ((cur - buy) / buy * 100) if buy > 0 else 0
    rows_pos.append((s, hold_min, pnl_pct))

zombies = [r for r in rows_pos if r[1] > 30 and abs(r[2]) <= 0.5]

trades_obj = {}
if TRADES.exists():
    try:
        trades_obj = json.loads(TRADES.read_text())
    except Exception:
        trades_obj = {}

trades = trades_obj.get("trades", []) if isinstance(trades_obj, dict) else []

last_hour = []
for r in trades:
    ts = _parse_ts(r.get("timestamp") or r.get("time") or r.get("executed_at"))
    if ts is None:
        continue
    if (now - ts).total_seconds() <= 3600:
        last_hour.append(r)

buy_rows = [r for r in last_hour if str(r.get("side", "")).lower() == "buy"]
sell_rows = [r for r in last_hour if str(r.get("side", "")).lower() == "sell"]

buy_funds = sum(_num(r.get("funds", 0), 0) for r in buy_rows)
sell_funds = sum(_num(r.get("funds", 0), 0) for r in sell_rows)
fees = sum(_num(r.get("fee", r.get("fees", 0)), 0) for r in last_hour)
total_notional = buy_funds + sell_funds

slot_capacity = 15
slot_notional = 11.0
velocity_per_slot_per_day = 0.0
if slot_capacity > 0 and slot_notional > 0:
    velocity_per_slot_per_day = (sell_funds * 24.0) / (slot_capacity * slot_notional)

record = {
    "ts": now.isoformat(),
    "positions": len(rows_pos),
    "zombie_count": len(zombies),
    "zombie_rate": round((len(zombies) / len(rows_pos)) if rows_pos else 0.0, 4),
    "hour_orders": len(last_hour),
    "hour_buys": len(buy_rows),
    "hour_sells": len(sell_rows),
    "hour_buy_funds": round(buy_funds, 6),
    "hour_sell_funds": round(sell_funds, 6),
    "hour_fees": round(fees, 6),
    "hour_fee_pct_notional": round((fees / total_notional * 100) if total_notional > 0 else 0.0, 6),
    "velocity_per_slot_per_day": round(velocity_per_slot_per_day, 4),
}

OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open("a") as f:
    f.write(json.dumps(record, sort_keys=True) + "\n")

print(json.dumps(record, sort_keys=True))
