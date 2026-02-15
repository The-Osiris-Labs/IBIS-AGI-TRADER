#!/usr/bin/env python3
"""
Backfill SQLite trades from data/trade_history.json with order_id deduplication.

Safety:
- Does not touch positions.
- Requires --apply to write.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
TRADE_HISTORY = BASE / "data" / "trade_history.json"
DB_PATH = BASE / "data" / "ibis_v8.db"


def _norm_symbol(sym: str) -> str:
    return str(sym or "").replace("-USDT", "").replace("-USDC", "")


def _to_float(value, default=0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _to_side(value: str) -> str:
    side = str(value or "").upper().strip()
    return side if side in {"BUY", "SELL"} else ""


def _to_db_timestamp(raw) -> str:
    if raw is None:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    try:
        ts = int(str(raw).strip())
        if ts > 1_000_000_000_000:
            ts //= 1000
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _load_trades() -> list[dict]:
    if not TRADE_HISTORY.exists():
        return []
    obj = json.loads(TRADE_HISTORY.read_text())
    if isinstance(obj, dict):
        data = obj.get("trades", [])
    elif isinstance(obj, list):
        data = obj
    else:
        data = []
    return [row for row in data if isinstance(row, dict)]


def _prepare_row(row: dict) -> tuple | None:
    symbol = _norm_symbol(row.get("symbol", ""))
    side = _to_side(row.get("side", ""))
    if not symbol or not side:
        return None

    price = _to_float(row.get("price", 0), 0.0)
    funds = _to_float(row.get("funds", 0), 0.0)
    quantity = _to_float(row.get("size", row.get("quantity", 0)), 0.0)
    if quantity <= 0 and price > 0 and funds > 0:
        quantity = funds / price

    if quantity <= 0 or price <= 0:
        return None

    order_id = str(row.get("order_id", "") or "").strip()
    fees = _to_float(row.get("fee", row.get("fees", 0)), 0.0)
    pnl = row.get("pnl")
    pnl_pct = row.get("pnl_pct")
    reason = row.get("reason")
    ts = _to_db_timestamp(row.get("timestamp", row.get("executed_at")))

    return (symbol, side, order_id, quantity, price, fees, ts, pnl, pnl_pct, reason)


def main() -> int:
    apply = "--apply" in sys.argv
    rows = _load_trades()
    prepared = [r for r in (_prepare_row(x) for x in rows) if r is not None]

    if not DB_PATH.exists():
        print("status=error detail=db_missing")
        return 2

    con = sqlite3.connect(DB_PATH)
    try:
        cur = con.cursor()
        existing = cur.execute("SELECT COUNT(*) FROM trades").fetchone()[0]

        if not apply:
            print(f"history_records={len(rows)}")
            print(f"prepared_records={len(prepared)}")
            print(f"db_trades_before={existing}")
            print("status=dry_run")
            return 0

        inserted = 0
        ignored = 0
        for rec in prepared:
            try:
                cur.execute(
                    """
                    INSERT OR IGNORE INTO trades
                    (symbol, side, order_id, quantity, price, fees, timestamp, pnl, pnl_pct, reason)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    rec,
                )
                if cur.rowcount == 1:
                    inserted += 1
                else:
                    ignored += 1
            except sqlite3.IntegrityError:
                ignored += 1

        con.commit()
        after = cur.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
        print(f"history_records={len(rows)}")
        print(f"prepared_records={len(prepared)}")
        print(f"db_trades_before={existing}")
        print(f"inserted={inserted}")
        print(f"ignored={ignored}")
        print(f"db_trades_after={after}")
        print("status=applied")
        return 0
    except Exception as e:
        print(f"status=error detail={e}")
        return 2
    finally:
        con.close()


if __name__ == "__main__":
    raise SystemExit(main())
