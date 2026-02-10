#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              🦅 IBIS AGI TRADING SYSTEM - ICONS 🦅                    ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""

from enum import Enum


class TradingIcons:
    """Icons related to trading operations."""

    BUY = "🟢"
    SELL = "🔴"
    LONG = "🐂"
    SHORT = "🐻"
    ENTRY = "🎯"
    EXIT = "🚪"
    STOP_LOSS = "🛑"
    TAKE_PROFIT = "🏆"
    LIQUIDATION = "💥"
    LEVERAGE = "⚡"
    POSITION = "💼"
    ORDER = "📝"
    FILLED = "✅"
    PENDING = "⏳"
    CANCELLED = "❌"


class MarketIcons:
    """Icons for market data and analysis."""

    CHART_UP = "📈"
    CHART_DOWN = "📉"
    CHART = "📊"
    CANDLESTICK = "🕯️"
    VOLUME = "📊"
    TREND = "📈"
    TREND_UP = "↗️"
    TREND_DOWN = "↘️"
    TREND_SIDEWAYS = "➡️"
    VOLATILITY = "🌊"
    SUPPORT = "📍"
    RESISTANCE = "🚧"
    BREAKOUT = "💥"
    BREAKDOWN = "⬇️"


class AccountIcons:
    """Icons for account and portfolio."""

    WALLET = "💰"
    BALANCE = "💵"
    PROFIT = "💹"
    LOSS = "📉"
    FEES = "💳"
    TAXES = "📋"
    BONUS = "🎁"
    DEPOSIT = "⬇️"
    WITHDRAWAL = "⬆️"
    TRANSFER = "🔄"


class AnalysisIcons:
    """Icons for analysis and indicators."""

    RSI = "📊"
    MACD = "〰️"
    BOLLINGER = "📐"
    FIBONACCI = "🌀"
    MOVING_AVERAGE = "📏"
    RSI_OVERSOLD = "🔵"
    RSI_OVERBOUGHT = "🔴"
    DIVERGENCE = "↔️"
    CONFluence = "✨"
    SIGNAL = "📡"
    STRENGTH = "💪"
    MOMENTUM = "🚀"


class OnChainIcons:
    """Icons for on-chain metrics."""

    WHALE = "🐋"
    EXCHANGE = "🏦"
    ADDRESS = "🏠"
    TRANSACTION = "💸"
    HOLDER = "🙋"
    ACCUMULATION = "📈"
    DISTRIBUTION = "📉"
    FLOW = "➡️"
    RESERVE = "🏦"
    SUPPLY = "🪙"


class SentimentIcons:
    """Icons for sentiment analysis."""

    FEAR = "😨"
    GREED = "😈"
    NEUTRAL = "😐"
    BULLISH = "🐂"
    BEARISH = "🐻"
    CONFIDENT = "😎"
    UNCERTAIN = "🤔"
    CONFUSION = "😵"
    OPTIMISM = "😊"
    PESSIMISM = "😔"
    FEAR_GREED_INDEX = "🌡️"


class LearningIcons:
    """Icons for AI learning features."""

    BRAIN = "🧠"
    NEURAL = "🕸️"
    LEARNING = "📚"
    MEMORY = "💾"
    PATTERN = "🔄"
    MODEL = "🤖"
    TRAINING = "🏋️"
    PREDICTION = "🔮"
    CONFIDENCE = "🎯"
    ACCURACY = "🎯"
    ITERATION = "🔁"
    EVOLUTION = "🧬"


class SystemIcons:
    """Icons for system status."""

    POWER = "⚡"
    START = "▶️"
    STOP = "⏹️"
    PAUSE = "⏸️"
    RESTART = "🔄"
    SYNC = "🔗"
    UPDATE = "🔃"
    SETTINGS = "⚙️"
    CONFIG = "🔧"
    DATA = "💾"
    LOADING = "⏳"
    SCANNING = "🔍"
    MONITORING = "👁️"
    LIVE = "🔴"
    OFFLINE = "⚫"


class AlertIcons:
    """Icons for alerts and notifications."""

    ALERT = "🚨"
    WARNING = "⚠️"
    INFO = "ℹ️"
    TIP = "💡"
    IMPORTANT = "❗"
    QUESTION = "❓"
    SUCCESS = "✅"
    ERROR = "❌"
    CRITICAL = "☠️"
    NOTIFICATION = "🔔"
    MESSAGE = "💬"


class NavigationIcons:
    """Icons for navigation and UI."""

    HOME = "🏠"
    MENU = "📋"
    DASHBOARD = "📊"
    PORTOFOLIO = "💼"
    TRADING = "💹"
    HISTORY = "📜"
    ANALYTICS = "📈"
    SETTINGS = "⚙️"
    HELP = "❓"
    BACK = "⬅️"
    FORWARD = "➡️"
    UP = "⬆️"
    DOWN = "⬇️"
    REFRESH = "🔄"
    EXPAND = "🔽"
    COLLAPSE = "🔼"


class IconSet:
    """Unified icon set combining all categories."""

    BULL = "🐂"
    BEAR = "🐻"
    DRAGON = "🐉"
    PHOENIX = "🔥"

    MONEY = "💰"
    GOLD = "🥇"
    SILVER = "🥈"
    BRONZE = "🥉"

    ROCKET = "🚀"
    SHIELD = "🛡️"
    SWORD = "⚔️"
    CROWN = "👑"

    BRAIN = "🧠"
    EYE = "👁️"
    CLOCK = "🕐"
    GEAR = "⚙️"

    TARGET = "🎯"
    LIGHTNING = "⚡"
    KEY = "🔑"
    LOCK = "🔒"
    UNLOCK = "🔓"
    HEART = "❤️"
    CLOUD = "☁️"
    PAUSE = "⏸️"

    MICROSCOPE = "🔬"
    COMPASS = "🧭"
    MAP = "🗺️"
    GLOBE = "🌐"

    BATTERY_FULL = "🔋"
    BATTERY_HIGH = "🟢"
    BATTERY_MED = "🟡"
    BATTERY_LOW = "🔴"

    ROBOT = "🤖"
    SPARKLE = "✨"
    DIAMOND = "💎"
    TROPHY = "🏆"

    FIRE = "🔥"
    ICE = "❄️"
    STAR = "⭐"
    CHECK = "✅"
    CROSS = "❌"

    ARROW_UP = "▲"
    ARROW_DOWN = "▼"
    ARROW_RIGHT = "▶"
    ARROW_LEFT = "◀"
    MINUS = "─"
    PLUS = "+"

    WARNING = "⚠️"
    INFO = "ℹ️"
    ALERT = "🚨"
    TIP = "💡"

    CHART_UP = "📈"
    CHART_DOWN = "📉"
    CHART = "📊"

    def __init__(self):
        self.trading = TradingIcons()
        self.market = MarketIcons()
        self.account = AccountIcons()
        self.analysis = AnalysisIcons()
        self.onchain = OnChainIcons()
        self.sentiment = SentimentIcons()
        self.learning = LearningIcons()
        self.system = SystemIcons()
        self.alert = AlertIcons()
        self.navigation = NavigationIcons()

    def get(self, key: str, default: str = "❓") -> str:
        """Get icon by key name."""
        attributes = [
            self.trading.__dict__,
            self.market.__dict__,
            self.account.__dict__,
            self.analysis.__dict__,
            self.onchain.__dict__,
            self.sentiment.__dict__,
            self.learning.__dict__,
            self.system.__dict__,
            self.alert.__dict__,
            self.navigation.__dict__,
            self.__dict__,
        ]

        for attr_dict in attributes:
            if key in attr_dict:
                return attr_dict[key]

        return default


Icons = IconSet()
