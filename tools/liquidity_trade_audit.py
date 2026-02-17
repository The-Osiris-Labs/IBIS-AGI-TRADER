#!/usr/bin/env python3
"""
Audit recent trades against the latest liquidity signals captured by IBIS.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


def format_trade(entry: dict, matching: dict | None) -> str:
    ts = int(entry.get("timestamp", 0)) / 1000
    time_str = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    symbol = entry.get("symbol", "UNKNOWN")
    side = entry.get("side", "").upper()
    price = entry.get("price", 0)
    size = entry.get("size", 0)
    fee = entry.get("fee", 0)
    parts = [
        f"{time_str} | {symbol:<6} | {side:<4} | price={price:.8f} | size={size:.4f} | fee={fee:.8f}"
    ]
    if matching:
        parts.append(
            f"liquidity_ratio={matching.get('volume_spike_ratio', 0):.2f} "
            f"imbalance={matching.get('orderbook_imbalance', 0):.2f} "
            f"acc_conf={matching.get('accumulation_confidence', 0):.2f}"
        )
    return " | ".join(parts)


def find_matching_liquidity(symbol: str, history: list[dict]) -> dict | None:
    for record in reversed(history):
        for entry in record.get("entries", []):
            if entry.get("symbol") == symbol:
                return entry
    return None


def main():
    trade_path = Path("data/trade_history.json")
    state_path = Path("data/ibis_true_state.json")
    if not trade_path.exists() or not state_path.exists():
        print("Required data files missing.")
        return

    trades_root = json.loads(trade_path.read_text())
    trades = trades_root.get("trades", []) if isinstance(trades_root, dict) else trades_root
    state = json.loads(state_path.read_text())
    history = state.get("liquidity_history", [])

    recent = trades[-10:]
    if not recent:
        print("No trades recorded yet.")
        return

    print("Recent trades w/ liquidity signal (if matched):")
    for trade in reversed(recent):
        match = find_matching_liquidity(trade.get("symbol", ""), history)
        print(format_trade(trade, match))


if __name__ == "__main__":
    main()
