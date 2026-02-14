#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Set


def _num(v, default=0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(default)


def _iter_sell_entries(sell_orders: Dict):
    for sym, entries in (sell_orders or {}).items():
        if isinstance(entries, list):
            for e in entries:
                if isinstance(e, dict):
                    yield sym, e


async def _fetch_live_open_sells() -> List[Dict]:
    from ibis.exchange.kucoin_client import get_kucoin_client

    client = get_kucoin_client()
    orders = await client.get_open_orders()
    live = []
    for o in (orders or []):
        side = str(o.get("side", "")).lower()
        if side != "sell":
            continue
        sym = str(o.get("symbol", "")).replace("-USDT", "").replace("-USDC", "")
        created = o.get("createdAt", 0)
        created_ts = 0
        if isinstance(created, (int, float)):
            created_ts = int(created)
        elif isinstance(created, str) and created.isdigit():
            created_ts = int(created)
        if created_ts > 1_000_000_000_000:
            created_ts //= 1000
        live.append(
            {
                "symbol": sym,
                "order_id": str(o.get("id", "")).strip(),
                "created_at": created_ts,
            }
        )
    return live


def main() -> int:
    parser = argparse.ArgumentParser(description="IBIS execution integrity check")
    parser.add_argument("--state", default="data/ibis_true_state.json")
    parser.add_argument("--min-trade", type=float, default=11.0)
    parser.add_argument("--stale-sell-seconds", type=int, default=180)
    parser.add_argument(
        "--live-open-orders",
        action="store_true",
        help="Compare tracked sell orders against live open sell orders on exchange",
    )
    args = parser.parse_args()

    base = Path(__file__).resolve().parent.parent
    if str(base) not in sys.path:
        sys.path.insert(0, str(base))

    state_path = Path(args.state)
    critical: List[str] = []
    warnings: List[str] = []
    info: List[str] = []

    if not state_path.exists():
        print("CRITICAL: state file missing")
        return 2

    try:
        state = json.loads(state_path.read_text())
    except Exception as e:
        print(f"CRITICAL: state parse failed: {e}")
        return 2

    positions = state.get("positions", {}) or {}
    cap = state.get("capital_awareness", {}) or {}
    buy_orders = cap.get("buy_orders", {}) or {}
    sell_orders = cap.get("sell_orders", {}) or {}

    available = _num(cap.get("usdt_available", 0), 0)
    total_assets = _num(cap.get("total_assets", 0), 0)
    sell_orders_value = _num(cap.get("sell_orders_value", 0), 0)

    info.append(f"positions={len(positions)}")
    info.append(f"buy_orders={len(buy_orders)}")
    info.append(
        "sell_orders="
        + str(sum(len(v) for v in sell_orders.values() if isinstance(v, list)))
    )
    info.append(f"available_usdt={available:.4f}")

    if available < args.min_trade:
        warnings.append(
            f"available capital below min trade (${available:.2f} < ${args.min_trade:.2f})"
        )

    if total_assets > 0:
        blocked_ratio = sell_orders_value / total_assets
        info.append(f"blocked_capital_ratio={blocked_ratio:.4f}")
        if blocked_ratio > 0.75:
            warnings.append(f"high blocked capital ratio: {blocked_ratio:.2%}")

    now = int(time.time())
    stale_sells = 0
    duplicate_order_ids = 0
    seen_ids = set()
    tracked_sell_symbols: Set[str] = set()
    for sym, entry in _iter_sell_entries(sell_orders):
        tracked_sell_symbols.add(str(sym))
        oid = str(entry.get("order_id", "")).strip()
        if oid:
            if oid in seen_ids:
                duplicate_order_ids += 1
            seen_ids.add(oid)

        created = entry.get("created_at")
        created_ts = None
        if isinstance(created, (int, float)):
            created_ts = int(created)
            if created_ts > 1_000_000_000_000:
                created_ts //= 1000
        elif isinstance(created, str) and created.isdigit():
            created_ts = int(created)
            if created_ts > 1_000_000_000_000:
                created_ts //= 1000

        if created_ts:
            age = now - created_ts
            if age >= args.stale_sell_seconds:
                stale_sells += 1

        if sym in buy_orders:
            warnings.append(f"symbol present in both buy_orders and sell_orders: {sym}")

    if stale_sells:
        warnings.append(
            f"stale sell orders >= {args.stale_sell_seconds}s: {stale_sells}"
        )
    if duplicate_order_ids:
        critical.append(f"duplicate sell order ids detected: {duplicate_order_ids}")

    if args.live_open_orders:
        try:
            live_sells = asyncio.run(_fetch_live_open_sells())
            info.append(f"live_open_sell_orders={len(live_sells)}")
            live_symbols = {str(o.get('symbol', '')) for o in live_sells if o.get('symbol')}
            stale_live = [
                o
                for o in live_sells
                if o.get("created_at")
                and (now - int(o["created_at"])) >= args.stale_sell_seconds
            ]
            if stale_live:
                warnings.append(
                    f"stale LIVE sell orders >= {args.stale_sell_seconds}s: {len(stale_live)}"
                )

            only_tracked = sorted(tracked_sell_symbols - live_symbols)
            only_live = sorted(live_symbols - tracked_sell_symbols)
            if only_tracked:
                warnings.append(
                    "tracked sell symbols missing on live exchange: "
                    + ",".join(only_tracked[:10])
                )
            if only_live:
                warnings.append(
                    "live sell symbols missing in state tracking: " + ",".join(only_live[:10])
                )
        except Exception as e:
            warnings.append(f"live open-order parity check skipped: {e}")

    if len(positions) != int(_num(state.get("total_positions", len(positions)), len(positions))):
        warnings.append("total_positions field not aligned with positions map")

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
