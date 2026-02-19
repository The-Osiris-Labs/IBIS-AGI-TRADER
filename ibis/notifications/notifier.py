"""
IBIS Notification System
Telegram and Discord alerts for trades, signals, and system events
"""

import asyncio
import json
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
import aiohttp

from ibis.core.logging_config import get_logger
logger = get_logger(__name__)


class NotificationType(Enum):
    TRADE_OPEN = "trade_open"
    TRADE_CLOSE = "trade_close"
    SIGNAL = "signal"
    ALERT = "alert"
    ERROR = "error"
    SYSTEM = "system"
    DAILY_REPORT = "daily_report"


@dataclass
class TradeNotification:
    symbol: str
    side: str
    size: float
    price: float
    pnl: float = 0.0
    pnl_percent: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0
    timestamp: int = field(default_factory=lambda: int(datetime.now().timestamp() * 1000))

    def to_dict(self) -> Dict:
        return {
            "type": "trade",
            "symbol": self.symbol,
            "side": self.side,
            "size": f"{self.size:.4f}",
            "price": f"{self.price:.2f}",
            "pnl": f"{self.pnl:.2f}" if self.pnl != 0 else "0",
            "pnl_percent": f"{self.pnl_percent:.2f}%" if self.pnl_percent != 0 else "0%",
            "stop_loss": f"{self.stop_loss:.2f}" if self.stop_loss else "N/A",
            "take_profit": f"{self.take_profit:.2f}" if self.take_profit else "N/A",
            "timestamp": datetime.fromtimestamp(self.timestamp / 1000).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }

    def to_text(self) -> str:
        emoji = "🟢" if self.side.upper() == "BUY" else "🔴"
        pnl_text = f" | PnL: {self.pnl:.2f} ({self.pnl_percent:.2f}%)" if self.pnl != 0 else ""
        sl_tp = (
            f" | SL: {self.stop_loss:.2f} | TP: {self.take_profit:.2f}" if self.stop_loss else ""
        )
        return f"{emoji} **{self.side.upper()}** {self.symbol}\n📊 Size: {self.size:.4f} @ ${self.price:.2f}{pnl_text}{sl_tp}\n⏰ {datetime.fromtimestamp(self.timestamp / 1000).strftime('%H:%M:%S')}"


@dataclass
class SignalNotification:
    symbol: str
    signal: str
    confidence: float
    reason: str
    indicators: Dict = field(default_factory=dict)
    timestamp: int = field(default_factory=lambda: int(datetime.now().timestamp() * 1000))

    def to_dict(self) -> Dict:
        return {
            "type": "signal",
            "symbol": self.symbol,
            "signal": self.signal,
            "confidence": f"{self.confidence:.0%}",
            "reason": self.reason,
            "indicators": self.indicators,
            "timestamp": datetime.fromtimestamp(self.timestamp / 1000).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }

    def to_text(self) -> str:
        emoji = {
            "STRONG_BUY": "🚀",
            "BUY": "🟢",
            "STRONG_SELL": "🔻",
            "SELL": "🔴",
            "HOLD": "⚪",
        }.get(self.signal, "⚪")
        conf_bar = "█" * int(self.confidence * 10) + "░" * (10 - int(self.confidence * 10))
        return f"{emoji} **{self.signal}** on {self.symbol}\n📈 Confidence: `{conf_bar}` {self.confidence:.0%}\n💡 Reason: {self.reason}\n⏰ {datetime.fromtimestamp(self.timestamp / 1000).strftime('%H:%M:%S')}"


@dataclass
class AlertNotification:
    name: str
    message: str
    severity: str = "INFO"
    timestamp: int = field(default_factory=lambda: int(datetime.now().timestamp() * 1000))

    def to_dict(self) -> Dict:
        return {
            "type": "alert",
            "name": self.name,
            "message": self.message,
            "severity": self.severity,
            "timestamp": datetime.fromtimestamp(self.timestamp / 1000).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }

    def to_text(self) -> str:
        emoji = {
            "CRITICAL": "🚨",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "INFO": "ℹ️",
            "SUCCESS": "✅",
        }.get(self.severity, "ℹ️")
        return f"{emoji} **{self.name}**\n{self.message}\n⏰ {datetime.fromtimestamp(self.timestamp / 1000).strftime('%H:%M:%S')}"


class BaseNotifier(ABC):
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.message_queue: List[Dict] = []
        self._task: Optional[asyncio.Task] = None

    @abstractmethod
    async def _send_message(self, message: str, **kwargs) -> bool:
        pass

    async def send(self, message: str, **kwargs) -> bool:
        if not self.enabled:
            return False

        try:
            success = await self._send_message(message, **kwargs)
            if not success:
                self.message_queue.append({"message": message, "kwargs": kwargs})
            return success
        except Exception as e:
            logger.error(f"Notification failed: {e}", exc_info=True)
            self.message_queue.append({"message": message, "kwargs": kwargs})
            return False

    async def send_trade(self, notification: TradeNotification) -> bool:
        return await self.send(notification.to_text(), notification=notification)

    async def send_signal(self, notification: SignalNotification) -> bool:
        return await self.send(notification.to_text(), notification=notification)

    async def send_alert(self, notification: AlertNotification) -> bool:
        return await self.send(notification.to_text(), notification=notification)

    async def process_queue(self):
        while self.message_queue:
            item = self.message_queue.pop(0)
            success = await self._send_message(item["message"], **item.get("kwargs", {}))
            if not success:
                break
            await asyncio.sleep(1)

    def start_queue_processor(self):
        self._task = asyncio.create_task(self._queue_processor())

    async def _queue_processor(self):
        while True:
            if self.message_queue:
                await self.process_queue()
            await asyncio.sleep(5)

    def stop(self):
        if self._task:
            self._task.cancel()


class TelegramNotifier(BaseNotifier):
    def __init__(
        self,
        bot_token: str = "",
        chat_id: str = "",
        enabled: bool = True,
    ):
        super().__init__(enabled)
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _send_message(self, message: str, **kwargs) -> bool:
        if not self.bot_token or not self.chat_id:
            return False

        try:
            session = await self._get_session()
            url = f"{self.base_url}/sendMessage"

            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            }

            async with session.post(url, json=payload) as resp:
                return resp.status == 200
        except Exception as e:
             logger.error(f"Telegram send failed: {e}", exc_info=True)
            return False

    async def test_connection(self) -> bool:
        if not self.bot_token:
            return False
        try:
            session = await self._get_session()
            url = f"{self.base_url}/getMe"
            async with session.get(url) as resp:
                data = await resp.json()
                return data.get("ok", False)
        except:
            return False

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()


class DiscordNotifier(BaseNotifier):
    def __init__(
        self,
        webhook_url: str = "",
        enabled: bool = True,
        username: str = "IBIS Trading Bot",
        avatar_url: str = "",
    ):
        super().__init__(enabled)
        self.webhook_url = webhook_url
        self.username = username
        self.avatar_url = avatar_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _send_message(self, message: str, **kwargs) -> bool:
        if not self.webhook_url:
            return False

        try:
            session = await self._get_session()
            payload = {
                "content": message,
                "username": self.username,
            }

            if self.avatar_url:
                payload["avatar_url"] = self.avatar_url

            async with session.post(self.webhook_url, json=payload) as resp:
                return resp.status in [200, 204]
        except Exception as e:
             logger.error(f"Discord send failed: {e}", exc_info=True)
            return False

    async def send_embed(
        self,
        title: str,
        description: str,
        color: int = 0x00FF00,
        fields: List[Dict] = None,
        footer: str = None,
    ):
        if not self.webhook_url:
            return False

        try:
            session = await self._get_session()
            payload = {
                "username": self.username,
                "embeds": [
                    {
                        "title": title,
                        "description": description,
                        "color": color,
                        "fields": fields or [],
                        "footer": {"text": footer} if footer else None,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ],
            }

            if self.avatar_url:
                payload["avatar_url"] = self.avatar_url

            async with self.session.post(self.webhook_url, json=payload) as resp:
                return resp.status in [200, 204]
        except Exception as e:
             logger.error(f"Discord embed failed: {e}", exc_info=True)
            return False

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()


class NotificationManager:
    def __init__(self):
        self.telegram: Optional[TelegramNotifier] = None
        self.discord: Optional[DiscordNotifier] = None
        self._trade_callbacks: List[Callable] = []
        self._signal_callbacks: List[Callable] = []
        self._alert_callbacks: List[Callable] = []

        self.trade_history: List[TradeNotification] = []
        self.signal_history: List[SignalNotification] = []
        self.alert_history: List[AlertNotification] = []

    def setup_telegram(self, bot_token: str, chat_id: str, enabled: bool = True):
        self.telegram = TelegramNotifier(bot_token, chat_id, enabled)

    def setup_discord(self, webhook_url: str, enabled: bool = True, username: str = "IBIS"):
        self.discord = DiscordNotifier(webhook_url, enabled, username)

    def on_trade(self, callback: Callable[[TradeNotification], None]):
        self._trade_callbacks.append(callback)

    def on_signal(self, callback: Callable[[SignalNotification], None]):
        self._signal_callbacks.append(callback)

    def on_alert(self, callback: Callable[[AlertNotification], None]):
        self._alert_callbacks.append(callback)

    async def send_trade(self, notification: TradeNotification):
        self.trade_history.append(notification)
        self.trade_history = self.trade_history[-100:]

        if self.telegram:
            await self.telegram.send_trade(notification)
        if self.discord:
            await self.discord.send_trade(notification)

        for callback in self._trade_callbacks:
            try:
                callback(notification)
            except Exception as e:
                 logger.error(f"Trade callback error: {e}", exc_info=True)

    async def send_signal(self, notification: SignalNotification):
        self.signal_history.append(notification)
        self.signal_history = self.signal_history[-100:]

        if self.telegram:
            await self.telegram.send_signal(notification)
        if self.discord:
            await self.discord.send_signal(notification)

        for callback in self._signal_callbacks:
            try:
                callback(notification)
            except Exception as e:
                 logger.error(f"Signal callback error: {e}", exc_info=True)

    async def send_alert(self, notification: AlertNotification):
        self.alert_history.append(notification)
        self.alert_history = self.alert_history[-100:]

        if self.telegram:
            await self.telegram.send_alert(notification)
        if self.discord:
            await self.discord.send_alert(notification)

        for callback in self._alert_callbacks:
            try:
                callback(notification)
            except Exception as e:
                 logger.error(f"Alert callback error: {e}", exc_info=True)

    async def send_custom(self, message: str):
        if self.telegram:
            await self.telegram.send(message)
        if self.discord:
            await self.discord.send(message)

    async def close(self):
        if self.telegram:
            await self.telegram.close()
        if self.discord:
            await self.discord.close()

    def get_summary(self) -> Dict:
        today = datetime.now().strftime("%Y-%m-%d")
        today_trades = [
            t
            for t in self.trade_history
            if datetime.fromtimestamp(t.timestamp / 1000).strftime("%Y-%m-%d") == today
        ]
        total_pnl = sum(t.pnl for t in today_trades)

        return {
            "today_trades": len(today_trades),
            "today_pnl": total_pnl,
            "total_trades": len(self.trade_history),
            "pending_alerts": len(self.alert_history),
        }


def get_notification_manager() -> NotificationManager:
    return NotificationManager()
