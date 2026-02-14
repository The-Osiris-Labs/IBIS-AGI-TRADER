#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
STATE_PATH = BASE / "data" / "ibis_true_state.json"
TRADES_PATH = BASE / "data" / "trade_history.json"
MEMORY_PATH = BASE / "data" / "ibis_true_memory.json"


def _num(v, default=0.0) -> float:
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
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return None
    return None


def _load_state():
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text())
    except Exception:
        return {}


def _load_trades():
    if not TRADES_PATH.exists():
        return []
    try:
        obj = json.loads(TRADES_PATH.read_text())
    except Exception:
        return []
    if isinstance(obj, dict):
        return obj.get("trades", []) or []
    if isinstance(obj, list):
        return obj
    return []


def _load_memory():
    if not MEMORY_PATH.exists():
        return {}
    try:
        return json.loads(MEMORY_PATH.read_text())
    except Exception:
        return {}


def main():
    now = datetime.now(timezone.utc)
    state = _load_state()
    memory = _load_memory()
    trades = _load_trades()

    positions = state.get("positions", {}) or {}
    cap = state.get("capital_awareness", {}) or {}
    daily = state.get("daily", {}) or {}
    buy_orders = cap.get("buy_orders", {}) or {}
    sell_orders = cap.get("sell_orders", {}) or {}

    rows = []
    for r in trades:
        ts = _parse_ts(r.get("timestamp") or r.get("executed_at") or r.get("time"))
        if ts is None:
            continue
        sym = str(r.get("symbol", "")).replace("-USDT", "").replace("-USDC", "")
        side = str(r.get("side", "")).lower()
        funds = _num(r.get("funds", 0), 0)
        fee = _num(r.get("fee", r.get("fees", 0)), 0)
        if not sym or side not in {"buy", "sell"} or funds <= 0:
            continue
        rows.append(
            {
                "ts": ts,
                "symbol": sym,
                "side": side,
                "funds": funds,
                "fee": fee,
                "rate": (fee / funds) if funds > 0 else 0.0,
            }
        )

    rows.sort(key=lambda x: x["ts"])
    window_24h = [r for r in rows if (now - r["ts"]).total_seconds() <= 86400]
    window_7d = [r for r in rows if (now - r["ts"]).total_seconds() <= 7 * 86400]

    def summarize(window):
        buy_funds = sum(r["funds"] for r in window if r["side"] == "buy")
        sell_funds = sum(r["funds"] for r in window if r["side"] == "sell")
        notional = buy_funds + sell_funds
        fees = sum(r["fee"] for r in window)
        fee_pct = (fees / notional * 100) if notional > 0 else 0.0
        return {
            "fills": len(window),
            "buy_funds": round(buy_funds, 6),
            "sell_funds": round(sell_funds, 6),
            "notional": round(notional, 6),
            "fees": round(fees, 6),
            "fee_pct_notional": round(fee_pct, 6),
        }

    by_symbol = defaultdict(lambda: {"fills": 0, "funds": 0.0, "fee": 0.0})
    for r in window_7d:
        b = by_symbol[r["symbol"]]
        b["fills"] += 1
        b["funds"] += r["funds"]
        b["fee"] += r["fee"]

    symbol_fee_drag = []
    for sym, b in by_symbol.items():
        eff = (b["fee"] / b["funds"]) if b["funds"] > 0 else 0.0
        symbol_fee_drag.append(
            {
                "symbol": sym,
                "fills": b["fills"],
                "funds": round(b["funds"], 6),
                "fees": round(b["fee"], 6),
                "effective_fee_per_side_pct": round(eff * 100, 4),
            }
        )
    symbol_fee_drag.sort(key=lambda x: x["effective_fee_per_side_pct"], reverse=True)

    latency_map = memory.get("fill_latency_by_symbol", {}) or {}
    slow_fill_symbols = []
    for sym, row in latency_map.items():
        slow_fill_symbols.append(
            {
                "symbol": sym,
                "samples": int(_num(row.get("samples", 0), 0)),
                "avg_fill_seconds": round(_num(row.get("avg_seconds", 0), 0), 3),
                "ema_fill_seconds": round(_num(row.get("ema_seconds", 0), 0), 3),
                "last_fill_seconds": round(_num(row.get("last_seconds", 0), 0), 3),
            }
        )
    slow_fill_symbols.sort(key=lambda x: x["avg_fill_seconds"], reverse=True)

    rates_7d = [r["rate"] for r in window_7d]
    buckets = {
        "lte_0_11pct": round(
            (sum(1 for x in rates_7d if x <= 0.0011) / len(rates_7d) * 100) if rates_7d else 0.0,
            2,
        ),
        "between_0_11_0_21pct": round(
            (sum(1 for x in rates_7d if 0.0011 < x <= 0.0021) / len(rates_7d) * 100)
            if rates_7d
            else 0.0,
            2,
        ),
        "gt_0_21pct": round(
            (sum(1 for x in rates_7d if x > 0.0021) / len(rates_7d) * 100) if rates_7d else 0.0,
            2,
        ),
    }

    slot_capacity = 15
    slot_notional = 11.0
    pending_buy_limit = 8
    sell_24h = sum(r["funds"] for r in window_24h if r["side"] == "sell")
    velocity_per_slot_per_day = (
        (sell_24h / (slot_capacity * slot_notional)) if slot_capacity > 0 and slot_notional > 0 else 0
    )
    single_bill_cycles = (sell_24h / slot_notional) if slot_notional > 0 else 0.0

    open_sell_count = sum(len(v) for v in sell_orders.values() if isinstance(v, list))
    occupied_slots = len(positions) + len(buy_orders)
    queue_pressure_ratio = (len(buy_orders) / pending_buy_limit) if pending_buy_limit > 0 else 0.0

    out = {
        "ts": now.isoformat(),
        "summary_24h": summarize(window_24h),
        "summary_7d": summarize(window_7d),
        "fee_rate_buckets_7d_pct_of_fills": buckets,
        "velocity_per_slot_per_day": round(velocity_per_slot_per_day, 4),
        "single_11usdt_bill_cycles_per_day": round(single_bill_cycles, 4),
        "positions": len(positions),
        "open_buy_orders": len(buy_orders),
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
        "slot_fill_rate": round((occupied_slots / slot_capacity) if slot_capacity > 0 else 0.0, 4),
        "deployable_usdt": round(
            _num(cap.get("real_trading_capital", cap.get("usdt_available", 0)), 0), 6
        ),
        "top_fee_drag_symbols_7d": symbol_fee_drag[:20],
        "top_slow_fill_symbols": slow_fill_symbols[:20],
        "entry_admission": {
            "enabled": True,
            "min_edge": 45.0,
            "override_score": 90.0,
        },
    }

    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
