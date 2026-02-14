#!/usr/bin/env python3
"""
Reconcile SQLite positions table to match live JSON state positions.
Operational safeguard only; does not alter strategy/risk settings.
"""

from __future__ import annotations

import sys
from typing import Dict, Set

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ibis.data_consolidation import load_state, sync_state_positions_to_db
from ibis.database.db import IbisDB


def _norm(sym: str) -> str:
    return str(sym).replace("-USDT", "").replace("-USDC", "")


def _db_symbols(db: IbisDB) -> Set[str]:
    rows = db.get_open_positions()
    return {_norm(r.get("symbol", "")) for r in rows}


def main() -> int:
    apply_fix = "--apply" in sys.argv

    try:
        state = load_state()
        state_positions: Dict = state.get("positions", {}) or {}
        state_syms = {_norm(s) for s in state_positions.keys()}

        db = IbisDB()
        db_syms = _db_symbols(db)

        only_state = sorted(state_syms - db_syms)
        only_db = sorted(db_syms - state_syms)

        print(f"state_positions={len(state_syms)}")
        print(f"db_positions={len(db_syms)}")
        print(f"only_state={len(only_state)}")
        print(f"only_db={len(only_db)}")

        if only_state:
            print(f"symbols_only_in_state={','.join(only_state)}")
        if only_db:
            print(f"symbols_only_in_db={','.join(only_db)}")

        if not only_state and not only_db:
            print("status=already_consistent")
            return 0

        if not apply_fix:
            print("status=mismatch_detected_no_apply")
            return 1

        sync_state_positions_to_db(state_positions, db)
        db_after = _db_symbols(db)
        only_state_after = state_syms - db_after
        only_db_after = db_after - state_syms
        if only_state_after or only_db_after:
            print("status=reconcile_incomplete")
            return 2

        print("status=reconciled")
        return 0
    except Exception as e:
        print(f"status=error detail={e}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
