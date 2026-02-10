"""Simple in-memory market data cache with TTL for spot trading."""

import time
from typing import Any, Dict, Tuple, Optional


class MarketCache:
    def __init__(self, ttl_seconds: float = 5.0):
        self.ttl = ttl_seconds
        self._store: Dict[str, Tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        item = self._store.get(key)
        if not item:
            return None
        ts, value = item
        if (time.time() - ts) > self.ttl:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (time.time(), value)

    def clear(self) -> None:
        self._store.clear()

    def snapshot(self) -> Dict[str, float]:
        """Return cache keys with age in seconds."""
        now = time.time()
        return {k: max(0.0, now - ts) for k, (ts, _v) in self._store.items()}
