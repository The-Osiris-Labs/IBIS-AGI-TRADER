#!/usr/bin/env python3
"""Market funnel for spot-only low-cap symbol selection.

Pipeline:
1) Universe (USDT spot, trading enabled)
2) Liquidity filter (quote volume)
3) Momentum/volatility scoring
4) Top-N candidates for deep analysis
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import asyncio
import math


@dataclass
class Candidate:
    symbol: str
    price: float
    change_24h: float
    volume_base: float
    volume_quote: float
    score: float
    whale_score: float = 0.0


class MarketFunnel:
    def __init__(self, client, min_quote_volume: float = 1_000_000, exclude=None):
        self.client = client
        self.min_quote_volume = min_quote_volume
        self.exclude = set(exclude or ["BTC", "ETH", "USDC", "DAI", "USD"])

    async def get_universe(self) -> List[str]:
        symbols = await self.client.get_symbols()
        universe = []
        for s in symbols:
            if s.get("quoteCurrency") != "USDT":
                continue
            if not s.get("enableTrading", True):
                continue
            base = s.get("baseCurrency")
            if base in self.exclude:
                continue
            universe.append(s.get("symbol"))
        return universe

    async def rank(self, limit: int = 150) -> List[Candidate]:
        # Pull all tickers once (efficient)
        tickers = await self.client.get_tickers()
        candidates: List[Candidate] = []

        for t in tickers:
            if not t.symbol.endswith("USDT"):
                continue
            base = t.symbol.split("-")[0]
            if base in self.exclude:
                continue

            price = t.price or 0.0
            vol_base = t.volume_24h or 0.0
            vol_quote = vol_base * price
            if vol_quote < self.min_quote_volume:
                continue

            # Score combines liquidity and momentum
            # Momentum favors strong but not extreme moves
            change = t.change_24h or 0.0
            momentum = max(-20.0, min(20.0, change))
            vol_score = math.log10(vol_quote + 1)
            # Whale scan heuristic: extreme volume or strong move with volume
            whale_score = 0.0
            if vol_quote >= self.min_quote_volume * 5:
                whale_score += 0.6
            if abs(change) >= 10 and vol_quote >= self.min_quote_volume * 2:
                whale_score += 0.4
            whale_score = min(1.0, whale_score)

            score = (vol_score * 0.55) + (momentum * 0.35) + (whale_score * 0.10)

            candidates.append(
                Candidate(
                    symbol=t.symbol,
                    price=price,
                    change_24h=change,
                    volume_base=vol_base,
                    volume_quote=vol_quote,
                    score=score,
                    whale_score=whale_score,
                )
            )

        candidates.sort(key=lambda c: c.score, reverse=True)
        return candidates[:limit]

    async def select(self, limit: int = 80) -> List[str]:
        ranked = await self.rank(limit=limit)
        self.last_candidates = {c.symbol: c for c in ranked}
        return [c.symbol for c in ranked]
