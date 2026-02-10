"""Orderbook microstructure utilities (spot)."""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Microstructure:
    spread_pct: float
    imbalance: float
    depth_bid: float
    depth_ask: float


def analyze_orderbook(bids: List[Tuple[float, float]], asks: List[Tuple[float, float]]) -> Microstructure:
    if not bids or not asks:
        return Microstructure(0.0, 0.0, 0.0, 0.0)

    bid0 = bids[0][0]
    ask0 = asks[0][0]
    mid = (bid0 + ask0) / 2 if (bid0 + ask0) else 0.0
    spread_pct = (ask0 - bid0) / mid if mid else 0.0

    depth_bid = sum(b[1] for b in bids[:10])
    depth_ask = sum(a[1] for a in asks[:10])
    total = depth_bid + depth_ask
    imbalance = (depth_bid - depth_ask) / total if total else 0.0

    return Microstructure(spread_pct, imbalance, depth_bid, depth_ask)
