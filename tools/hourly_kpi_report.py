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
daily = state.get("daily", {}) or {}
capital = state.get("capital_awareness", {}) or {}
buy_orders_state = capital.get("buy_orders", {}) or {}
sell_orders_state = capital.get("sell_orders", {}) or {}
rows_pos = []
for s, p in positions.items():
    hold_min = _num(p.get("hold_seconds", 0), 0) / 60
    if hold_min <= 0:
        opened = _parse_ts(p.get("opened"))
        if opened is not None:
            hold_min = max(0.0, (now - opened).total_seconds() / 60.0)
    buy = _num(p.get("buy_price", 0), 0)
    cur = _num(p.get("current_price", 0), 0)
    pnl_pct = ((cur - buy) / buy * 100) if buy > 0 else 0
    rows_pos.append((s, hold_min, pnl_pct))

zombies = [r for r in rows_pos if r[1] > 30 and abs(r[2]) <= 0.2]

trades_obj = {}
if TRADES.exists():
    try:
        trades_obj = json.loads(TRADES.read_text())
    except Exception:
        trades_obj = {}

trades = trades_obj.get("trades", []) if isinstance(trades_obj, dict) else []

last_hour = []
last_24h = []
for r in trades:
    ts = _parse_ts(r.get("timestamp") or r.get("time") or r.get("executed_at"))
    if ts is None:
        continue
    age = (now - ts).total_seconds()
    if age <= 3600:
        last_hour.append(r)
    if age <= 86400:
        last_24h.append(r)

buy_rows = [r for r in last_hour if str(r.get("side", "")).lower() == "buy"]
sell_rows = [r for r in last_hour if str(r.get("side", "")).lower() == "sell"]
buy_rows_24h = [r for r in last_24h if str(r.get("side", "")).lower() == "buy"]
sell_rows_24h = [r for r in last_24h if str(r.get("side", "")).lower() == "sell"]

buy_funds = sum(_num(r.get("funds", 0), 0) for r in buy_rows)
sell_funds = sum(_num(r.get("funds", 0), 0) for r in sell_rows)
fees = sum(_num(r.get("fee", r.get("fees", 0)), 0) for r in last_hour)
total_notional = buy_funds + sell_funds
fees_24h = sum(_num(r.get("fee", r.get("fees", 0)), 0) for r in last_24h)
buy_funds_24h = sum(_num(r.get("funds", 0), 0) for r in buy_rows_24h)
sell_funds_24h = sum(_num(r.get("funds", 0), 0) for r in sell_rows_24h)
total_notional_24h = buy_funds_24h + sell_funds_24h

slot_capacity = 15
slot_notional = 11.0
pending_buy_limit = 8
velocity_per_slot_per_day = 0.0
if slot_capacity > 0 and slot_notional > 0:
    velocity_per_slot_per_day = sell_funds_24h / (slot_capacity * slot_notional)

single_bill_cycles_per_day = sell_funds_24h / slot_notional if slot_notional > 0 else 0.0
open_sell_count = sum(len(v) for v in sell_orders_state.values() if isinstance(v, list))
occupied_slots = len(rows_pos) + len(buy_orders_state)
slot_fill_rate = occupied_slots / slot_capacity if slot_capacity > 0 else 0.0
queue_pressure_ratio = (len(buy_orders_state) / pending_buy_limit) if pending_buy_limit > 0 else 0.0
deployable_usdt = _num(capital.get("real_trading_capital", capital.get("usdt_available", 0)), 0)
total_assets = _num(capital.get("total_assets", 0), 0)
capital_utilization = 0.0
if total_assets > 0:
    capital_utilization = (total_assets - deployable_usdt) / total_assets

record = {
    "ts": now.isoformat(),
    "positions": len(rows_pos),
    "open_buy_orders": len(buy_orders_state),
    "pending_buy_limit": pending_buy_limit,
    "queue_pressure_ratio": round(queue_pressure_ratio, 4),
    "open_sell_orders": open_sell_count,
    "orders_cancelled_today": int(_num(daily.get("orders_cancelled", 0), 0)),
    "stale_buy_cancels_today": int(_num(daily.get("stale_buy_cancels", 0), 0)),
    "avg_buy_fill_latency_seconds_today": round(
        _num(daily.get("avg_buy_fill_latency_seconds", 0), 0), 3
    ),
    "buy_fill_samples_today": int(_num(daily.get("buy_fill_samples", 0), 0)),
    "occupied_slots": occupied_slots,
    "slot_fill_rate": round(slot_fill_rate, 4),
    "zombie_count": len(zombies),
    "zombie_rate": round((len(zombies) / len(rows_pos)) if rows_pos else 0.0, 4),
    "hour_orders": len(last_hour),
    "hour_buys": len(buy_rows),
    "hour_sells": len(sell_rows),
    "hour_buy_funds": round(buy_funds, 6),
    "hour_sell_funds": round(sell_funds, 6),
    "hour_fees": round(fees, 6),
    "hour_fee_pct_notional": round((fees / total_notional * 100) if total_notional > 0 else 0.0, 6),
    "day_orders": len(last_24h),
    "day_buy_funds": round(buy_funds_24h, 6),
    "day_sell_funds": round(sell_funds_24h, 6),
    "day_fees": round(fees_24h, 6),
    "day_fee_pct_notional": round(
        (fees_24h / total_notional_24h * 100) if total_notional_24h > 0 else 0.0, 6
    ),
    "velocity_per_slot_per_day": round(velocity_per_slot_per_day, 4),
    "single_bill_cycles_per_day": round(single_bill_cycles_per_day, 4),
    "deployable_usdt": round(deployable_usdt, 6),
    "capital_utilization_pct": round(capital_utilization * 100, 4),
}

OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open("a") as f:
    f.write(json.dumps(record, sort_keys=True) + "\n")

print(json.dumps(record, sort_keys=True))
