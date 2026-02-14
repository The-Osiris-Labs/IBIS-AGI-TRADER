#!/usr/bin/env python3
"""
Deep non-strategy integrity audit for IBIS runtime artifacts.
Checks JSON state coherence, DB alignment, order-value constraints, and TP/SL completeness.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Set


def _num(v, default=0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(default)


def _norm_symbol(sym: str) -> str:
    return str(sym).replace("-USDT", "").replace("-USDC", "")


async def _fetch_live_exchange_symbols(min_value_usd: float) -> Set[str]:
    from ibis.exchange.kucoin_client import get_kucoin_client

    stablecoins = {"USDT", "USDC", "DAI", "BUSD", "TUSD", "USD", "KCS"}
    client = get_kucoin_client()
    balances = await client.get_all_balances(min_value_usd=min_value_usd)
    syms: Set[str] = set()
    for currency, bal in (balances or {}).items():
        if currency in stablecoins:
            continue
        amount = _num(bal.get("balance", 0), 0)
        if amount > 0:
            syms.add(_norm_symbol(currency))
    return syms


def main() -> int:
    parser = argparse.ArgumentParser(description="Deep IBIS runtime integrity audit")
    parser.add_argument(
        "--live-exchange",
        action="store_true",
        help="Also compare state symbols to live exchange holdings",
    )
    parser.add_argument(
        "--min-live-usd",
        type=float,
        default=1.0,
        help="Min USD value when loading live exchange holdings",
    )
    args = parser.parse_args()

    base = Path(__file__).resolve().parent.parent
    if str(base) not in sys.path:
        sys.path.insert(0, str(base))
    state_path = base / "data" / "ibis_true_state.json"
    db_path = base / "data" / "ibis_v8.db"

    critical: List[str] = []
    warnings: List[str] = []
    info: List[str] = []

    if not state_path.exists():
        print("CRITICAL: state file missing")
        return 2

    try:
        state = json.loads(state_path.read_text())
    except Exception as e:
        print(f"CRITICAL: state JSON parse failed: {e}")
        return 2

    positions: Dict = state.get("positions", {}) or {}
    cap: Dict = state.get("capital_awareness", {}) or {}
    buy_orders: Dict = cap.get("buy_orders", {}) or {}
    sell_orders: Dict = cap.get("sell_orders", {}) or {}
    sell_order_symbols = {_norm_symbol(sym) for sym in sell_orders.keys()}

    state_symbols = {_norm_symbol(s) for s in positions.keys()}
    info.append(f"state_positions={len(positions)}")

    # Position-level checks
    missing_tp = 0
    missing_sl = 0
    invalid_price_rel = 0
    for sym, pos in positions.items():
        qty = _num(pos.get("quantity", 0))
        buy = _num(pos.get("buy_price", 0))
        tp = pos.get("tp")
        sl = pos.get("sl")
        tpv = _num(tp, -1)
        slv = _num(sl, -1)

        if qty <= 0:
            warnings.append(f"{sym}: non-positive quantity ({qty})")
        if buy <= 0:
            critical.append(f"{sym}: non-positive buy_price ({buy})")
        if tp is None or tpv <= 0:
            missing_tp += 1
        if sl is None or slv <= 0:
            missing_sl += 1
        if buy > 0 and tpv > 0 and slv > 0 and not (tpv > buy and slv < buy):
            invalid_price_rel += 1

    if missing_tp:
        critical.append(f"positions missing TP: {missing_tp}")
    if missing_sl:
        critical.append(f"positions missing SL: {missing_sl}")
    if invalid_price_rel:
        warnings.append(f"positions with TP/SL inconsistent vs buy price: {invalid_price_rel}")

    # Pending buy order checks
    low_value_orders = 0
    for sym, order in buy_orders.items():
        order_type = str(order.get("order_type", "")).lower()
        if order_type == "market":
            # Market buys are funded by quote amount; qty*price in state can be approximate.
            continue
        q = _num(order.get("quantity", 0))
        p = _num(order.get("price", 0))
        # Keep a small tolerance to avoid floating-point false positives around $11.
        if q > 0 and p > 0 and (q * p) < 10.95:
            low_value_orders += 1
    if low_value_orders:
        warnings.append(f"pending buy orders below $11 by qty*price: {low_value_orders}")

    # Open-order count coherence
    sell_order_count = 0
    for _, entries in sell_orders.items():
        if isinstance(entries, list):
            sell_order_count += len(entries)
    expected_open = len(buy_orders) + sell_order_count
    actual_open = int(_num(cap.get("open_orders_count", 0), 0))
    if expected_open != actual_open:
        warnings.append(
            f"capital_awareness open_orders_count mismatch: expected={expected_open}, actual={actual_open}"
        )

    # DB alignment checks
    if not db_path.exists():
        warnings.append("db file missing")
    else:
        try:
            con = sqlite3.connect(db_path)
            cur = con.cursor()
            has_positions = cur.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='positions'"
            ).fetchone()[0]
            has_trades = cur.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='trades'"
            ).fetchone()[0]
            if not has_positions:
                critical.append("db positions table missing")
            if not has_trades:
                warnings.append("db trades table missing")

            db_symbols = set()
            if has_positions:
                rows = cur.execute("SELECT symbol FROM positions").fetchall()
                db_symbols = {_norm_symbol(r[0]) for r in rows}
                info.append(f"db_positions={len(db_symbols)}")
                only_state = state_symbols - db_symbols
                only_db = db_symbols - state_symbols
                if only_state:
                    warnings.append(f"symbols only in state: {len(only_state)}")
                if only_db:
                    warnings.append(f"symbols only in db: {len(only_db)}")
            con.close()
        except Exception as e:
            critical.append(f"db audit failed: {e}")

    # Optional live exchange parity checks.
    if args.live_exchange:
        try:
            live_symbols = asyncio.run(_fetch_live_exchange_symbols(args.min_live_usd))
            info.append(f"live_exchange_symbols={len(live_symbols)}")
            only_state_live = state_symbols - live_symbols
            only_live = live_symbols - state_symbols

            # If a symbol has active sell tracking, allow temporary parity lag.
            only_state_live = only_state_live - sell_order_symbols

            if only_state_live:
                warnings.append(
                    "symbols only in state vs live exchange: "
                    f"{len(only_state_live)} ({','.join(sorted(only_state_live)[:12])})"
                )
            if only_live:
                warnings.append(
                    "symbols only on live exchange vs state: "
                    f"{len(only_live)} ({','.join(sorted(only_live)[:12])})"
                )
        except Exception as e:
            warnings.append(f"live exchange parity check skipped: {e}")

    for line in info:
        print(f"INFO: {line}")
    for line in warnings:
        print(f"WARN: {line}")
    for line in critical:
        print(f"CRITICAL: {line}")

    if critical:
        return 2
    if warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
