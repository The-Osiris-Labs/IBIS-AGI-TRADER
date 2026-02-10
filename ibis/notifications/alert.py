"""
IBIS Alert Integration
TBD - To Be Implemented
Requires TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, DISCORD_WEBHOOK_URL env vars
"""

from typing import Optional


_alert_manager = None


def get_alerts():
    return _alert_manager


async def alert_trade(symbol, side, size, price, pnl=0.0, pnl_percent=0.0):
    pass


async def alert_error(message):
    pass


async def alert_warning(message):
    pass


async def alert_info(message):
    pass


async def alert_system(message):
    pass


async def shutdown_alerts():
    global _alert_manager
    _alert_manager = None
