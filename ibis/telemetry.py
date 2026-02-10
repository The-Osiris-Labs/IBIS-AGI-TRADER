"""
IBIS Telemetry - Lightweight event bus for full observability.
Provides a centralized stream of what IBIS "sees" and decides.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


REDACT_KEYS = {"api_key", "api_secret", "api_passphrase", "passphrase", "secret", "key"}


def _redact(obj: Any) -> Any:
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k.lower() in REDACT_KEYS:
                out[k] = "***REDACTED***"
            else:
                out[k] = _redact(v)
        return out
    if isinstance(obj, list):
        return [_redact(v) for v in obj]
    return obj


class EventBus:
    def __init__(self, max_events: int = 10000):
        self.max_events = max_events
        self._events: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()
        self._seq = 0

    async def emit(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        async with self._lock:
            self._seq += 1
            event = {
                "id": self._seq,
                "type": event_type,
                "ts": datetime.now(timezone.utc).isoformat(),
                "payload": _redact(payload),
            }
            self._events.append(event)
            if len(self._events) > self.max_events:
                self._events = self._events[-self.max_events :]
            return event

    async def get_events(
        self, limit: int = 200, since_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        async with self._lock:
            events = self._events
            if since_id is not None:
                events = [e for e in events if e["id"] > since_id]
            return events[-limit:]

    async def clear(self) -> None:
        async with self._lock:
            self._events.clear()


_BUS = EventBus()


async def emit_event(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return await _BUS.emit(event_type, payload)


async def get_events(limit: int = 200, since_id: Optional[int] = None) -> List[Dict[str, Any]]:
    return await _BUS.get_events(limit=limit, since_id=since_id)


async def clear_events() -> None:
    await _BUS.clear()
