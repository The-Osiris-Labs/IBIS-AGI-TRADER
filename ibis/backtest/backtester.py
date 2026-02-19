from ibis.core.logging_config import get_logger
#!/usr/bin/env python3
"""
🦅 IBIS BACKTESTING ENGINE
=========================
Historical Strategy Testing with Dynamic Symbol Support

Features:
• Works with ANY trading pair discovered from API
• Multiple strategy implementations (RSI, Momentum)
• Complete performance metrics
"""

import asyncio
import random
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

logger = get_logger(__name__)


class PositionSide:
    LONG = "LONG"
    SHORT = "SHORT"
    NONE = "NONE"


@dataclass
class Trade:
    symbol: str
    side: str
    entry_time: datetime
    entry_price: float
    exit_time: datetime
    exit_price: float
    size: float
    pnl_pct: float
    pnl_abs: float
    fees: float = 0.0
    holding_period: int = 0
    entry_reason: str = ""
    exit_reason: str = ""


@dataclass
class BacktestConfig:
    initial_balance: float = 10000.0
    position_size_pct: float = 0.20
    stop_loss_pct: float = 0.02
    take_profit_pct: float = 0.06
    max_daily_trades: int = 5
    max_open_positions: int = 3
    fee_pct: float = 0.001
    risk_free_rate: float = 0.05
    slippage_pct: float = 0.0005


class CandleGenerator:
    """Generate historical candles for any symbol."""

    @staticmethod
    def generate_candles(
        symbol: str,
        days: int = 365,
        start_price: float = None,
        volatility: float = 0.02,
    ) -> List[Dict]:
        """Generate realistic historical candles for ANY symbol."""
        candles = []
        price = start_price or random.uniform(10, 1000)
        now = datetime.now()

        for i in range(days * 24):
            timestamp = now - timedelta(hours=days * 24 - i)
            daily_vol = volatility * (1 + 0.5 * random.random())
            trend = 0.0001 * random.gauss(0, 1)
            change = random.gauss(trend, daily_vol)

            open_price = price
            close_price = price * (1 + change)
            high_price = max(open_price, close_price) * (1 + abs(random.gauss(0, daily_vol)))
            low_price = min(open_price, close_price) * (1 - abs(random.gauss(0, daily_vol)))
            volume = random.uniform(1000, 10000) * (1 + abs(change) * 10)

            candles.append({
                "symbol": symbol,
                "timestamp": timestamp,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": volume,
            })
            price = close_price

        return candles


class Strategy:
    """Base strategy - works with any symbol."""

    def __init__(self, config: BacktestConfig):
        self.config = config

    def analyze(self, candles: List[Dict], position: str) -> Dict:
        raise NotImplementedError


class RSI_MeanReversionStrategy(Strategy):
    """RSI-based mean reversion strategy."""

    def analyze(self, candles: List[Dict], position: str) -> Dict:
        if len(candles) < 15:
            return {"action": "HOLD", "reason": "Insufficient data"}

        closes = [c["close"] for c in candles[-15:]]
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]

        avg_gain = sum(gains) / len(gains)
        avg_loss = (sum(losses) / len(losses)) if losses else 1

        rs = avg_gain / avg_loss if avg_loss > 0 else 0
        rsi = 100 - (100 / (1 + rs)) if rs > 0 else 50

        if position == PositionSide.NONE:
            if rsi < 30:
                return {"action": "BUY", "reason": f"RSI oversold ({rsi:.1f})", "strength": (30 - rsi) / 30}
            elif rsi > 70:
                return {"action": "SELL", "reason": f"RSI overbought ({rsi:.1f})", "strength": (rsi - 70) / 30}
            return {"action": "HOLD", "reason": f"RSI neutral ({rsi:.1f})"}
        else:
            if rsi > 50:
                return {"action": "CLOSE", "reason": f"RSI mean reversion ({rsi:.1f})"}
            return {"action": "HOLD", "reason": f"RSI holding ({rsi:.1f})"}


class MomentumStrategy(Strategy):
    """Momentum strategy - works with any symbol."""

    def analyze(self, candles: List[Dict], position: str) -> Dict:
        if len(candles) < 20:
            return {"action": "HOLD", "reason": "Insufficient data"}

        closes = [c["close"] for c in candles[-20:]]
        sma_5 = sum(closes[-5:]) / 5
        sma_20 = sum(closes) / 20
        momentum = (sma_5 - sma_20) / sma_20

        if position == PositionSide.NONE:
            if momentum > 0.02:
                return {"action": "BUY", "reason": f"Momentum up ({momentum*100:.1f}%)", "strength": momentum}
            elif momentum < -0.02:
                return {"action": "SELL", "reason": f"Momentum down ({momentum*100:.1f}%)", "strength": abs(momentum)}
            return {"action": "HOLD", "reason": "Weak momentum"}
        else:
            if momentum < 0:
                return {"action": "CLOSE", "reason": "Momentum reversal"}
            return {"action": "HOLD", "reason": "Momentum intact"}


class ConfluenceStrategy(Strategy):
    """Simple multi-signal confluence strategy (RSI + momentum + volume)."""

    def analyze(self, candles: List[Dict], position: str) -> Dict:
        if len(candles) < 30:
            return {"action": "HOLD", "reason": "Insufficient data"}

        closes = [c["close"] for c in candles[-30:]]
        volumes = [c["volume"] for c in candles[-30:]]

        # RSI
        deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas[-14:]]
        losses = [-d if d < 0 else 0 for d in deltas[-14:]]
        avg_gain = sum(gains) / 14
        avg_loss = (sum(losses) / 14) if losses else 1
        rs = avg_gain / avg_loss if avg_loss > 0 else 0
        rsi = 100 - (100 / (1 + rs)) if rs > 0 else 50

        # Momentum
        sma_5 = sum(closes[-5:]) / 5
        sma_20 = sum(closes[-20:]) / 20
        momentum = (sma_5 - sma_20) / sma_20

        # Volume spike
        avg_vol = sum(volumes[-20:]) / 20
        vol_ratio = volumes[-1] / avg_vol if avg_vol > 0 else 1

        if position == PositionSide.NONE:
            if rsi < 35 and momentum > 0 and vol_ratio > 1.5:
                return {"action": "BUY", "reason": "Confluence bullish", "strength": 0.7}
            if rsi > 65 and momentum < 0 and vol_ratio > 1.5:
                return {"action": "SELL", "reason": "Confluence bearish", "strength": 0.7}
            return {"action": "HOLD", "reason": "No confluence"}
        else:
            if rsi > 55 and momentum < 0:
                return {"action": "CLOSE", "reason": "Confluence reversal"}
            return {"action": "HOLD", "reason": "Confluence intact"}


@dataclass
class BacktestResult:
    total_return_pct: float = 0.0
    total_return_abs: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    max_drawdown: float = 0.0
    avg_trade_duration: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    best_trade: float = 0.0
    worst_trade: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    expectancy: float = 0.0
    equity_curve: List[Tuple[datetime, float]] = field(default_factory=list)
    trades: List[Trade] = field(default_factory=list)


class BacktestEngine:
    """Backtesting engine - works with ANY symbol(s) discovered from API."""

    def __init__(self, config: BacktestConfig = None):
        self.config = config or BacktestConfig()
        self.balance = self.config.initial_balance
        self.equity_curve = [(datetime.now(), self.balance)]
        self.trades: List[Trade] = []
        self.positions: Dict[str, Dict] = {}
        self.daily_pnl: Dict[datetime, float] = {}

    async def run(self, strategy: Strategy, candles: Dict[str, List[Dict]]) -> BacktestResult:
        """Run backtest with any symbols provided."""
        self.balance = self.config.initial_balance
        self.equity_curve = []
        self.trades = []
        self.positions = {}
        self.daily_pnl = {}

        all_timestamps = sorted(set(
            c["timestamp"] for symbol_candles in candles.values()
            for c in symbol_candles
        ))

        for timestamp in all_timestamps:
            for symbol, symbol_candles in candles.items():
                candle = next((c for c in symbol_candles if c["timestamp"] == timestamp), None)
                if candle and symbol in self.positions:
                    self._update_position(symbol, candle, self.positions[symbol])

            for symbol, symbol_candles in candles.items():
                candle = next((c for c in symbol_candles if c["timestamp"] == timestamp), None)
                if candle:
                    analysis = strategy.analyze(symbol_candles[:symbol_candles.index(candle)+1], PositionSide.NONE)
                    if analysis["action"] == "BUY" and symbol not in self.positions:
                        self._open_position(symbol, candle, PositionSide.LONG, analysis.get("reason", ""))
                    elif analysis["action"] == "SELL" and symbol not in self.positions:
                        self._open_position(symbol, candle, PositionSide.SHORT, analysis.get("reason", ""))

            self.equity_curve.append((timestamp, self.balance))

        return self._generate_report()

    def _open_position(self, symbol: str, candle: Dict, side: str, reason: str):
        if len(self.positions) >= self.config.max_open_positions:
            return

        position_size = self.balance * self.config.position_size_pct
        price = candle["close"]
        # Apply slippage
        slip = self.config.slippage_pct
        if side == PositionSide.LONG:
            price = price * (1 + slip)
        else:
            price = price * (1 - slip)
        size = position_size / price

        self.balance -= price * size * self.config.fee_pct

        self.positions[symbol] = {
            "side": side,
            "entry_time": candle["timestamp"],
            "entry_price": price,
            "size": size,
            "stop_loss": price * (1 - self.config.stop_loss_pct),
            "take_profit": price * (1 + self.config.take_profit_pct),
            "entry_reason": reason,
        }

    def _update_position(self, symbol: str, candle: Dict, position: Dict):
        price = candle["close"]
        side = position["side"]

        if side == PositionSide.LONG:
            pnl_pct = (price - position["entry_price"]) / position["entry_price"]
        else:
            pnl_pct = (position["entry_price"] - price) / position["entry_price"]

        closed = False
        exit_reason = ""

        if price <= position["stop_loss"]:
            exit_reason = "Stop loss hit"
            closed = True
        elif price >= position["take_profit"]:
            exit_reason = "Take profit hit"
            closed = True

        if closed:
            self._close_position(symbol, candle, position, exit_reason)

    def _close_position(self, symbol: str, candle: Dict, position: Dict, reason: str):
        price = candle["close"]
        slip = self.config.slippage_pct
        side = position["side"]

        if side == PositionSide.LONG:
            price = price * (1 - slip)
            pnl_pct = (price - position["entry_price"]) / position["entry_price"]
        else:
            price = price * (1 + slip)
            pnl_pct = (position["entry_price"] - price) / position["entry_price"]

        pnl_abs = position["size"] * price * pnl_pct
        exit_fee = price * position["size"] * self.config.fee_pct

        self.balance += position["size"] * price - exit_fee + pnl_abs

        holding_period = (candle["timestamp"] - position["entry_time"]).total_seconds() / 3600

        self.trades.append(Trade(
            symbol=symbol,
            side=side,
            entry_time=position["entry_time"],
            entry_price=position["entry_price"],
            exit_time=candle["timestamp"],
            exit_price=price,
            size=position["size"],
            pnl_pct=pnl_pct,
            pnl_abs=pnl_abs,
            fees=exit_fee,
            holding_period=holding_period,
            entry_reason=position["entry_reason"],
            exit_reason=reason,
        ))

        date_key = candle["timestamp"].date()
        if date_key not in self.daily_pnl:
            self.daily_pnl[date_key] = 0
        self.daily_pnl[date_key] += pnl_abs

        del self.positions[symbol]

    def _generate_report(self) -> BacktestResult:
        if not self.trades:
            return BacktestResult()

        winning = [t for t in self.trades if t.pnl_pct > 0]
        losing = [t for t in self.trades if t.pnl_pct <= 0]

        total_return_pct = (self.balance - self.config.initial_balance) / self.config.initial_balance * 100
        win_rate = len(winning) / len(self.trades) * 100 if self.trades else 0

        gross_profit = sum(t.pnl_abs for t in winning) if winning else 0
        gross_loss = abs(sum(t.pnl_abs for t in losing)) if losing else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

        avg_win = sum(t.pnl_pct for t in winning) / len(winning) if winning else 0
        avg_loss = sum(t.pnl_pct for t in losing) / len(losing) if losing else 0

        returns = [t.pnl_pct for t in self.trades]
        avg_return = statistics.mean(returns) if returns else 0
        std_return = statistics.stdev(returns) if len(returns) > 1 else 0
        sharpe = (avg_return - self.config.risk_free_rate / 252) / std_return if std_return > 0 else 0

        equity_values = [e[1] for e in self.equity_curve]
        peak = max(equity_values)
        drawdowns = [(peak - e) / peak * 100 for e in equity_values]
        max_drawdown = max(drawdowns) if drawdowns else 0

        return BacktestResult(
            total_return_pct=total_return_pct,
            total_return_abs=self.balance - self.config.initial_balance,
            win_rate=win_rate,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe,
            max_drawdown=max_drawdown,
            total_trades=len(self.trades),
            winning_trades=len(winning),
            losing_trades=len(losing),
            best_trade=max(t.pnl_pct for t in self.trades) if self.trades else 0,
            worst_trade=min(t.pnl_pct for t in self.trades) if self.trades else 0,
            avg_win=avg_win,
            avg_loss=avg_loss,
            expectancy=(win_rate / 100 * avg_win) - ((100 - win_rate) / 100 * abs(avg_loss)),
            equity_curve=self.equity_curve,
            trades=self.trades,
        )
