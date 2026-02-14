#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import json
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set


BASE = Path(__file__).resolve().parent.parent
STATE_PATH = BASE / 'data' / 'ibis_true_state.json'
DB_PATH = BASE / 'data' / 'ibis_v8.db'


def _num(v, default=0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(default)


def _norm(sym: str) -> str:
    return str(sym).replace('-USDT', '').replace('-USDC', '')


async def _live_snapshot() -> Dict:
    if str(BASE) not in sys.path:
        sys.path.insert(0, str(BASE))

    from ibis.exchange.kucoin_client import get_kucoin_client

    stable = {'USDT', 'USDC', 'DAI', 'BUSD', 'TUSD', 'USD', 'KCS'}
    client = get_kucoin_client()

    balances = await client.get_all_balances(min_value_usd=1.0)
    live_symbols: Set[str] = set()
    for ccy, b in (balances or {}).items():
        if ccy in stable:
            continue
        bal = _num(b.get('balance', 0), 0)
        if bal > 0:
            live_symbols.add(_norm(ccy))

    orders = await client.get_open_orders()
    open_sell_symbols: Set[str] = set()
    stale_open_sells = 0
    now = int(time.time())
    for o in (orders or []):
        if str(o.get('side', '')).lower() != 'sell':
            continue
        sym = _norm(str(o.get('symbol', '')))
        if sym:
            open_sell_symbols.add(sym)
        created = o.get('createdAt', 0)
        ts = 0
        if isinstance(created, (int, float)):
            ts = int(created)
        elif isinstance(created, str) and created.isdigit():
            ts = int(created)
        if ts > 1_000_000_000_000:
            ts //= 1000
        if ts and (now - ts) >= 180:
            stale_open_sells += 1

    return {
        'live_symbols': live_symbols,
        'live_open_sell_symbols': open_sell_symbols,
        'live_open_sell_count': len(open_sell_symbols),
        'stale_live_open_sells_180s': stale_open_sells,
    }


def _db_symbols() -> Set[str]:
    if not DB_PATH.exists():
        return set()
    con = sqlite3.connect(DB_PATH)
    try:
        cur = con.cursor()
        has_positions = cur.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='positions'"
        ).fetchone()[0]
        if not has_positions:
            return set()
        rows = cur.execute("SELECT symbol FROM positions").fetchall()
        return {_norm(r[0]) for r in rows}
    finally:
        con.close()


def main() -> int:
    if not STATE_PATH.exists():
        print(json.dumps({'ts': datetime.now(timezone.utc).isoformat(), 'status': 'critical', 'error': 'state_missing'}))
        return 2

    try:
        state = json.loads(STATE_PATH.read_text())
    except Exception as e:
        print(json.dumps({'ts': datetime.now(timezone.utc).isoformat(), 'status': 'critical', 'error': f'state_parse:{e}'}))
        return 2

    positions = state.get('positions', {}) or {}
    cap = state.get('capital_awareness', {}) or {}
    sell_orders = cap.get('sell_orders', {}) or {}
    buy_orders = cap.get('buy_orders', {}) or {}

    state_symbols = {_norm(s) for s in positions.keys()}
    tracked_sell_symbols = {_norm(s) for s in sell_orders.keys()}
    db_symbols = _db_symbols()

    status = 'ok'
    issues: List[str] = []

    if state_symbols != db_symbols:
        status = 'degraded'
        issues.append('state_db_mismatch')

    live = None
    try:
        live = asyncio.run(_live_snapshot())
        only_state_live = sorted(state_symbols - live['live_symbols'])
        only_live_state = sorted(live['live_symbols'] - state_symbols)

        if only_state_live:
            status = 'degraded'
            issues.append('state_live_mismatch')
        if only_live_state:
            status = 'degraded'
            issues.append('live_state_mismatch')

        missing_live_tracking = sorted(live['live_open_sell_symbols'] - tracked_sell_symbols)
        if missing_live_tracking:
            status = 'degraded'
            issues.append('open_sell_tracking_gap')

        if live['stale_live_open_sells_180s'] > 0:
            status = 'degraded'
            issues.append('stale_live_open_sells')

    except Exception as e:
        status = 'degraded' if status == 'ok' else status
        issues.append(f'live_unavailable:{type(e).__name__}')

    out = {
        'ts': datetime.now(timezone.utc).isoformat(),
        'status': status,
        'issues': issues,
        'state_positions': len(state_symbols),
        'db_positions': len(db_symbols),
        'tracked_sell_symbols': len(tracked_sell_symbols),
        'tracked_buy_orders': len(buy_orders),
        'available_usdt': round(_num(cap.get('usdt_available', 0), 0), 6),
    }

    if live:
        out.update(
            {
                'live_positions': len(live['live_symbols']),
                'live_open_sell_symbols': live['live_open_sell_count'],
                'stale_live_open_sells_180s': live['stale_live_open_sells_180s'],
                'state_only_vs_live': sorted(state_symbols - live['live_symbols'])[:10],
                'live_only_vs_state': sorted(live['live_symbols'] - state_symbols)[:10],
                'live_open_sells_not_tracked': sorted(live['live_open_sell_symbols'] - tracked_sell_symbols)[:10],
            }
        )

    print(json.dumps(out, sort_keys=True))

    if status == 'ok':
        return 0
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
