"""
IBIS Agent Server - HTTP control plane for AI agents.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

import os
import asyncio
from aiohttp import web

from ibis.agent_controller import AgentController


controller = AgentController()

AGENT_TOKEN = os.environ.get("AGENT_TOKEN")
DEFAULT_ROLE = os.environ.get("AGENT_DEFAULT_ROLE", "admin")

ROLE_PERMS = {
    "read": {
        "/health",
        "/status",
        "/events",
        "/events/ws",
        "/ibis/memory/stats",
        "/ibis/memory/recent",
        "/state",
    },
    "analyze": {
        "/engine/analyze",
        "/ibis/analyze",
        "/engine/hunt",
        "/backtest/demo",
        "/optimize/demo",
    },
    "control": {
        "/init",
        "/engine/auto/start",
        "/engine/auto/stop",
        "/events/clear",
    },
}


def _role_from_request(request: web.Request) -> str:
    return request.headers.get("X-AGENT-ROLE", DEFAULT_ROLE)


def _is_allowed(role: str, path: str) -> bool:
    if role == "admin":
        return True
    perms = set()
    if role in ROLE_PERMS:
        perms |= ROLE_PERMS[role]
    # allow read endpoints for analyze/control roles
    if role in ("analyze", "control"):
        perms |= ROLE_PERMS.get("read", set())
    return path in perms


def _authorize(request: web.Request) -> Optional[web.Response]:
    if AGENT_TOKEN:
        token = request.headers.get("X-AGENT-TOKEN", "")
        if token != AGENT_TOKEN:
            return web.json_response({"error": "unauthorized"}, status=401)
    role = _role_from_request(request)
    if not _is_allowed(role, request.path):
        return web.json_response({"error": "forbidden"}, status=403)
    return None


async def _json(request: web.Request) -> Dict[str, Any]:
    if request.can_read_body:
        try:
            return await request.json()
        except Exception:
            return {}
    return {}


async def health(_request: web.Request) -> web.Response:
    denied = _authorize(_request)
    if denied:
        return denied
    return web.json_response({"ok": True})


async def init_system(request: web.Request) -> web.Response:
    denied = _authorize(request)
    if denied:
        return denied
    data = await _json(request)
    init_engine = data.get("engine", True)
    init_ibis = data.get("ibis", True)

    engine_ok = True
    ibis_ok = True
    if init_engine:
        engine_ok = await controller.init_engine()
    if init_ibis:
        ibis_ok = await controller.init_ibis()

    return web.json_response({"engine": engine_ok, "ibis": ibis_ok})


async def status(_request: web.Request) -> web.Response:
    denied = _authorize(_request)
    if denied:
        return denied
    return web.json_response(await controller.status())


async def analyze_engine(request: web.Request) -> web.Response:
    denied = _authorize(request)
    if denied:
        return denied
    data = await _json(request)
    symbols = data.get("symbols")
    results = await controller.analyze_engine(symbols)
    return web.json_response({"results": results})


async def analyze_ibis(request: web.Request) -> web.Response:
    denied = _authorize(request)
    if denied:
        return denied
    data = await _json(request)
    context = data.get("context") or {}
    if not context:
        return web.json_response(
            {"error": "missing context"}, status=400
        )
    result = await controller.analyze_ibis(context)
    return web.json_response({"result": result})


async def auto_start(request: web.Request) -> web.Response:
    denied = _authorize(request)
    if denied:
        return denied
    data = await _json(request)
    interval = int(data.get("interval", 60))
    status = await controller.start_auto(interval)
    return web.json_response({"status": status})


async def auto_stop(_request: web.Request) -> web.Response:
    denied = _authorize(_request)
    if denied:
        return denied
    status = await controller.stop_auto()
    return web.json_response({"status": status})


async def events(request: web.Request) -> web.Response:
    denied = _authorize(request)
    if denied:
        return denied
    limit = int(request.query.get("limit", "200"))
    since_id = request.query.get("since_id")
    since_val: Optional[int] = int(since_id) if since_id else None
    data = await controller.get_events(limit=limit, since_id=since_val)
    return web.json_response({"events": data})


async def clear_events(_request: web.Request) -> web.Response:
    denied = _authorize(_request)
    if denied:
        return denied
    await controller.clear_events()
    return web.json_response({"ok": True})

async def memory_stats(_request: web.Request) -> web.Response:
    denied = _authorize(_request)
    if denied:
        return denied
    data = await controller.memory_stats()
    return web.json_response({"memory": data})


async def recent_trades(request: web.Request) -> web.Response:
    denied = _authorize(request)
    if denied:
        return denied
    limit = int(request.query.get("limit", "50"))
    trades = await controller.recent_trades(limit=limit)
    return web.json_response({"trades": trades})


async def state_dump(request: web.Request) -> web.Response:
    denied = _authorize(request)
    if denied:
        return denied
    return web.json_response(await controller.state_dump())


async def hunt(request: web.Request) -> web.Response:
    denied = _authorize(request)
    if denied:
        return denied
    data = await _json(request)
    limit = int(data.get("limit", 20))
    result = await controller.hunt(limit=limit)
    return web.json_response({"results": result})


async def backtest_demo(request: web.Request) -> web.Response:
    denied = _authorize(request)
    if denied:
        return denied
    data = await _json(request)
    symbol = data.get("symbol", "DEMO-USDT")
    days = int(data.get("days", 60))
    result = await controller.backtest_demo(symbol=symbol, days=days)
    return web.json_response({"result": result})


async def optimize_demo(request: web.Request) -> web.Response:
    denied = _authorize(request)
    if denied:
        return denied
    data = await _json(request)
    generations = int(data.get("generations", 5))
    population = int(data.get("population", 10))
    result = await controller.optimize_demo(generations=generations, population=population)
    return web.json_response({"result": result})


async def events_ws(request: web.Request) -> web.WebSocketResponse:
    denied = _authorize(request)
    if denied:
        return denied
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    last_id = 0
    try:
        while True:
            items = await controller.get_events(limit=200, since_id=last_id)
            if items:
                last_id = items[-1]["id"]
                await ws.send_json({"events": items})
            await asyncio.sleep(0.5)
    except asyncio.CancelledError:
        pass
    except Exception:
        pass
    finally:
        await ws.close()
    return ws


def create_app() -> web.Application:
    app = web.Application()
    app.add_routes(
        [
            web.get("/health", health),
            web.post("/init", init_system),
            web.get("/status", status),
            web.post("/engine/analyze", analyze_engine),
            web.post("/ibis/analyze", analyze_ibis),
            web.post("/engine/auto/start", auto_start),
            web.post("/engine/auto/stop", auto_stop),
            web.get("/events", events),
            web.get("/events/ws", events_ws),
            web.post("/events/clear", clear_events),
            web.get("/ibis/memory/stats", memory_stats),
            web.get("/ibis/memory/recent", recent_trades),
            web.get("/state", state_dump),
            web.post("/engine/hunt", hunt),
            web.post("/backtest/demo", backtest_demo),
            web.post("/optimize/demo", optimize_demo),
        ]
    )
    return app


def main():
    app = create_app()
    web.run_app(app, host="127.0.0.1", port=8088)


if __name__ == "__main__":
    main()
