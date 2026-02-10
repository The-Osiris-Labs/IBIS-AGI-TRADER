"""
IBIS Technical Indicators
Comprehensive technical analysis indicators
"""

import asyncio
import math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque


@dataclass
class OHLCV:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class IndicatorResult:
    name: str
    value: float
    signal: str
    strength: float

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "value": self.value,
            "signal": self.signal,
            "strength": self.strength,
        }


@dataclass
class MultiIndicatorResult:
    timestamp: int
    indicators: Dict[str, IndicatorResult] = field(default_factory=dict)
    trend: str = "NEUTRAL"
    momentum: str = "NEUTRAL"
    volatility: str = "NORMAL"
    overall_signal: str = "HOLD"
    confidence: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "indicators": {k: v.to_dict() for k, v in self.indicators.items()},
            "trend": self.trend,
            "momentum": self.momentum,
            "volatility": self.volatility,
            "overall_signal": self.overall_signal,
            "confidence": self.confidence,
        }


class MovingAverage:
    @staticmethod
    def sma(prices: List[float], period: int) -> List[float]:
        result = []
        for i in range(len(prices)):
            if i < period - 1:
                result.append(float("nan"))
            else:
                sma = sum(prices[i - period + 1 : i + 1]) / period
                result.append(sma)
        return result

    @staticmethod
    def ema(prices: List[float], period: int) -> List[float]:
        result = []
        multiplier = 2 / (period + 1)

        ema = sum(prices[:period]) / period
        result.append(ema)

        for i in range(period, len(prices)):
            ema = (prices[i] - ema) * multiplier + ema
            result.append(ema)

        return result

    @staticmethod
    def wma(prices: List[float], period: int) -> List[float]:
        result = []
        denominator = period * (period + 1) / 2

        for i in range(len(prices)):
            if i < period - 1:
                result.append(float("nan"))
            else:
                weighted_sum = sum(
                    prices[i - period + j + 1] * (period - j) for j in range(period)
                )
                result.append(weighted_sum / denominator)

        return result

    @staticmethod
    def cross_signal(
        short_ma: List[float], long_ma: List[float]
    ) -> Tuple[List[str], List[float]]:
        signals = []
        strengths = []

        for i in range(len(short_ma)):
            if math.isnan(short_ma[i]) or math.isnan(long_ma[i]):
                signals.append("NEUTRAL")
                strengths.append(0.0)
            elif short_ma[i] > long_ma[i]:
                signals.append("BULLISH")
                diff = (short_ma[i] - long_ma[i]) / long_ma[i]
                strengths.append(min(diff * 100, 1.0))
            else:
                signals.append("BEARISH")
                diff = (long_ma[i] - short_ma[i]) / short_ma[i]
                strengths.append(min(diff * 100, 1.0))

        return signals, strengths


class RSI:
    @staticmethod
    def calculate(prices: List[float], period: int = 14) -> List[float]:
        if len(prices) < period + 1:
            return [float("nan")] * len(prices)

        deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        gains = [max(d, 0) for d in deltas]
        losses = [-min(d, 0) for d in deltas]

        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        rsi_values = [float("nan")] * period

        for i in range(period, len(prices)):
            if avg_loss == 0:
                rsi_values.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                rsi_values.append(rsi)

            if i < len(prices) - 1:
                avg_gain = (avg_gain * (period - 1) + gains[i]) / period
                avg_loss = (avg_loss * (period - 1) + losses[i]) / period

        return rsi_values

    @staticmethod
    def signal(rsi_values: List[float]) -> Tuple[str, float]:
        valid_values = [v for v in rsi_values if not math.isnan(v)]
        if not valid_values:
            return "NEUTRAL", 0.0

        rsi = valid_values[-1]

        if rsi >= 70:
            return "OVERBOUGHT", min((rsi - 70) / 30, 1.0)
        elif rsi <= 30:
            return "OVERSOLD", min((30 - rsi) / 30, 1.0)
        elif rsi > 50:
            return "BULLISH", (rsi - 50) / 50
        else:
            return "BEARISH", (50 - rsi) / 50


class MACD:
    @staticmethod
    def calculate(
        prices: List[float],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> Dict[str, List[float]]:
        ema_fast = MovingAverage.ema(prices, fast_period)
        ema_slow = MovingAverage.ema(prices, slow_period)

        ema_fast = [float("nan")] * (len(prices) - len(ema_fast)) + ema_fast
        ema_slow = [float("nan")] * (len(prices) - len(ema_slow)) + ema_slow

        macd_line = []
        for i in range(len(prices)):
            if math.isnan(ema_fast[i]) or math.isnan(ema_slow[i]):
                macd_line.append(float("nan"))
            else:
                macd_line.append(ema_fast[i] - ema_slow[i])

        signal_line = []
        valid_macd = [m for m in macd_line if not math.isnan(m)]
        if valid_macd:
            start_idx = len(macd_line) - len(valid_macd)
            signal = MovingAverage.ema(valid_macd, signal_period)
            signal_line = [float("nan")] * start_idx + signal

        histogram = []
        for i in range(len(macd_line)):
            if i >= len(signal_line):
                histogram.append(float("nan"))
            elif math.isnan(macd_line[i]) or math.isnan(signal_line[i]):
                histogram.append(float("nan"))
            else:
                histogram.append(macd_line[i] - signal_line[i])

        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram,
        }

    @staticmethod
    def signal(macd_data: Dict[str, List[float]]) -> Tuple[str, float]:
        hist = macd_data["histogram"]
        valid_hist = [h for h in hist if not math.isnan(h)]
        if not valid_hist:
            return "NEUTRAL", 0.0

        current = valid_hist[-1]
        previous = valid_hist[-2] if len(valid_hist) > 1 else 0

        if current > 0:
            if current > abs(previous):
                return "BULLISH_STRONG", min(abs(current) / 10, 1.0)
            return "BULLISH", min(abs(current) / 10, 1.0)
        else:
            if abs(current) > abs(previous):
                return "BEARISH_STRONG", min(abs(current) / 10, 1.0)
            return "BEARISH", min(abs(current) / 10, 1.0)


class BollingerBands:
    @staticmethod
    def calculate(
        prices: List[float], period: int = 20, std_multiplier: float = 2.0
    ) -> Dict[str, List[float]]:
        sma = MovingAverage.sma(prices, period)
        upper = []
        lower = []

        for i in range(len(prices)):
            if math.isnan(sma[i]) or i < period - 1:
                upper.append(float("nan"))
                lower.append(float("nan"))
            else:
                window = prices[i - period + 1 : i + 1]
                std = math.sqrt(sum((p - sma[i]) ** 2 for p in window) / period)
                upper.append(sma[i] + std_multiplier * std)
                lower.append(sma[i] - std_multiplier * std)

        return {
            "middle": sma,
            "upper": upper,
            "lower": lower,
        }

    @staticmethod
    def signal(prices: List[float], bb_data: Dict) -> Tuple[str, float]:
        if len(prices) < 2:
            return "NEUTRAL", 0.0

        upper = bb_data["upper"][-1]
        lower = bb_data["lower"][-1]
        current = prices[-1]

        if math.isnan(upper) or math.isnan(lower):
            return "NEUTRAL", 0.0

        if current > upper:
            return "OVERBOUGHT", min((current - upper) / upper, 1.0)
        elif current < lower:
            return "OVERSOLD", min((lower - current) / lower, 1.0)
        elif current > bb_data["middle"][-1]:
            return "BULLISH", min(
                (current - bb_data["middle"][-1])
                / (upper - bb_data["middle"][-1] + 0.001),
                1.0,
            )
        else:
            return "BEARISH", min(
                (bb_data["middle"][-1] - current)
                / (bb_data["middle"][-1] - lower + 0.001),
                1.0,
            )


class ATR:
    @staticmethod
    def calculate(ohlcv: List[OHLCV], period: int = 14) -> List[float]:
        if len(ohlcv) < 2:
            return [float("nan")] * len(ohlcv)

        true_ranges = []

        for i in range(1, len(ohlcv)):
            high_low = ohlcv[i].high - ohlcv[i].low
            high_close = abs(ohlcv[i].high - ohlcv[i - 1].close)
            low_close = abs(ohlcv[i].low - ohlcv[i - 1].close)
            true_ranges.append(max(high_low, high_close, low_close))

        atr_values = [float("nan")] * (period)

        if len(true_ranges) >= period:
            atr = sum(true_ranges[:period]) / period
            atr_values.append(atr)

            for i in range(period, len(true_ranges)):
                atr = (atr * (period - 1) + true_ranges[i]) / period
                atr_values.append(atr)

        return atr_values

    @staticmethod
    def volatility(atr_values: List[float], price: float) -> Tuple[str, float]:
        valid_atr = [v for v in atr_values if not math.isnan(v)]
        if not valid_atr:
            return "NORMAL", 0.0

        atr = valid_atr[-1]
        atr_percent = atr / price * 100

        if atr_percent > 5:
            return "HIGH", min(atr_percent / 10, 1.0)
        elif atr_percent < 1:
            return "LOW", min(1 - atr_percent / 2, 1.0)
        return "NORMAL", 0.5


class VWAP:
    @staticmethod
    def calculate(ohlcv: List[OHLCV]) -> List[float]:
        if not ohlcv:
            return []

        cumulative_tpv = 0.0
        cumulative_volume = 0.0
        vwap_values = []

        for bar in ohlcv:
            typical_price = (bar.high + bar.low + bar.close) / 3
            tpv = typical_price * bar.volume
            cumulative_tpv += tpv
            cumulative_volume += bar.volume

            if cumulative_volume > 0:
                vwap_values.append(cumulative_tpv / cumulative_volume)
            else:
                vwap_values.append(float("nan"))

        return vwap_values

    @staticmethod
    def signal(prices: List[float], vwap_values: List[float]) -> Tuple[str, float]:
        if not vwap_values or math.isnan(vwap_values[-1]):
            return "NEUTRAL", 0.0

        current_price = prices[-1]
        vwap = vwap_values[-1]

        if current_price > vwap:
            return "BULLISH", min((current_price - vwap) / vwap * 10, 1.0)
        else:
            return "BEARISH", min((vwap - current_price) / vwap * 10, 1.0)


class Stochastic:
    @staticmethod
    def calculate(
        ohlcv: List[OHLCV], k_period: int = 14, d_period: int = 3
    ) -> Dict[str, List[float]]:
        k_values = []
        d_values = []

        for i in range(len(ohlcv)):
            if i < k_period - 1:
                k_values.append(float("nan"))
                d_values.append(float("nan"))
                continue

            window = ohlcv[i - k_period + 1 : i + 1]
            highest_high = max(c.high for c in window)
            lowest_low = min(c.low for c in window)

            if highest_high == lowest_low:
                k_values.append(50)
            else:
                current_close = ohlcv[i].close
                k = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
                k_values.append(k)

            if len(k_values) >= d_period:
                valid_k = [k for k in k_values[-d_period:] if not math.isnan(k)]
                if len(valid_k) == d_period:
                    d_values.append(sum(valid_k) / d_period)
                else:
                    d_values.append(float("nan"))
            else:
                d_values.append(float("nan"))

        return {"k": k_values, "d": d_values}

    @staticmethod
    def signal(stoch_data: Dict) -> Tuple[str, float]:
        k = stoch_data["k"][-1]
        d = stoch_data["d"][-1]

        if math.isnan(k) or math.isnan(d):
            return "NEUTRAL", 0.0

        if k >= 80:
            return "OVERBOUGHT", min((k - 80) / 20, 1.0)
        elif k <= 20:
            return "OVERSOLD", min((20 - k) / 20, 1.0)
        elif k > d:
            return "BULLISH", (k - d) / 20
        else:
            return "BEARISH", (d - k) / 20


class OBV:
    @staticmethod
    def calculate(ohlcv: List[OHLCV]) -> List[float]:
        obv_values = [0]

        for i in range(1, len(ohlcv)):
            if ohlcv[i].close > ohlcv[i - 1].close:
                obv_values.append(obv_values[-1] + ohlcv[i].volume)
            elif ohlcv[i].close < ohlcv[i - 1].close:
                obv_values.append(obv_values[-1] - ohlcv[i].volume)
            else:
                obv_values.append(obv_values[-1])

        return obv_values

    @staticmethod
    def trend(obv_values: List[float]) -> Tuple[str, float]:
        if len(obv_values) < 10:
            return "NEUTRAL", 0.0

        recent = obv_values[-10:]
        if recent[-1] > recent[0]:
            return "BULLISH", min(
                (recent[-1] - recent[0]) / max(recent[0], 1) * 10, 1.0
            )
        elif recent[-1] < recent[0]:
            return "BEARISH", min(
                (recent[0] - recent[-1]) / max(recent[0], 1) * 10, 1.0
            )
        return "NEUTRAL", 0.0


class Ichimoku:
    @staticmethod
    def calculate(ohlcv: List[OHLCV]) -> Dict[str, List[float]]:
        tenkan_period = 9
        kijun_period = 26
        senkou_span_b_period = 52
        senkou_displacement = 26

        n = len(ohlcv)
        full_length = n + senkou_displacement

        tenkan = [float("nan")] * n
        kijun = [float("nan")] * n
        senkou_a = [float("nan")] * full_length
        senkou_b = [float("nan")] * full_length
        chikou = [float("nan")] * full_length

        for i in range(tenkan_period - 1, n):
            window = ohlcv[i - tenkan_period + 1 : i + 1]
            tenkan[i] = (max(c.high for c in window) + min(c.low for c in window)) / 2

        for i in range(kijun_period - 1, n):
            window = ohlcv[i - kijun_period + 1 : i + 1]
            kijun[i] = (max(c.high for c in window) + min(c.low for c in window)) / 2

        for i in range(kijun_period - 1, n):
            if not math.isnan(tenkan[i]) and not math.isnan(kijun[i]):
                sa = (tenkan[i] + kijun[i]) / 2
                senkou_a[i + senkou_displacement] = sa

        for i in range(senkou_span_b_period - 1, n):
            window = ohlcv[i - senkou_span_b_period + 1 : i + 1]
            senkou_b[i + senkou_displacement] = (
                max(c.high for c in window) + min(c.low for c in window)
            ) / 2

        for i in range(n):
            if i >= senkou_displacement:
                chikou[i - senkou_displacement] = ohlcv[i].close

        return {
            "tenkan": tenkan,
            "kijun": kijun,
            "senkou_a": senkou_a,
            "senkou_b": senkou_b,
            "chikou": chikou,
        }

    @staticmethod
    def signal(ichimoku_data: Dict, price: float) -> Tuple[str, float]:
        tenkan = ichimoku_data["tenkan"]
        kijun = ichimoku_data["kijun"]
        senkou_a = ichimoku_data["senkou_a"]
        senkou_b = ichimoku_data["senkou_b"]

        t = tenkan[-1]
        k = kijun[-1]
        sa = senkou_a[-1]
        sb = senkou_b[-1]

        if math.isnan(t) or math.isnan(k) or math.isnan(sa):
            return "NEUTRAL", 0.0

        cloud_top = max(sa, sb)
        cloud_bottom = min(sa, sb)

        signals = 0

        if t > k:
            signals += 1
        else:
            signals -= 1

        if price > cloud_top:
            signals += 2
        elif price < cloud_bottom:
            signals -= 2

        if signals >= 2:
            return "STRONG_BULLISH", min(signals / 4, 1.0)
        elif signals == 1:
            return "BULLISH", 0.5
        elif signals <= -2:
            return "STRONG_BEARISH", min(abs(signals) / 4, 1.0)
        elif signals == -1:
            return "BEARISH", 0.5
        return "NEUTRAL", 0.0


class Fibonacci:
    @staticmethod
    def levels(high: float, low: float) -> Dict[str, float]:
        diff = high - low
        return {
            "0": high,
            "0.236": high - diff * 0.236,
            "0.382": high - diff * 0.382,
            "0.5": high - diff * 0.5,
            "0.618": high - diff * 0.618,
            "0.786": high - diff * 0.786,
            "1": low,
        }

    @staticmethod
    def retrace(current: float, high: float, low: float) -> str:
        levels = Fibonacci.levels(high, low)

        for name, level in levels.items():
            if abs(current - level) / level < 0.01:
                return f"FIB_{name}"

        if current > high:
            return "ABOVE_0"
        elif current < low:
            return "BELOW_1"
        elif current > levels["0.618"]:
            return "BETWEEN_0_618"
        elif current > levels["0.382"]:
            return "BETWEEN_618_382"
        else:
            return "BETWEEN_382_1"


class SupportResistance:
    @staticmethod
    def find_levels(
        prices: List[float], window: int = 5, threshold: float = 0.02
    ) -> Dict[str, List[float]]:
        if len(prices) < window * 2:
            return {"support": [], "resistance": []}

        highs = []
        lows = []

        for i in range(window, len(prices) - window):
            window_highs = prices[i - window : i + window]
            window_lows = prices[i - window : i + window]

            if prices[i] == max(window_highs):
                highs.append(prices[i])
            if prices[i] == min(window_lows):
                lows.append(prices[i])

        levels = {"support": [], "resistance": []}

        for h in highs:
            is_unique = True
            for existing in levels["resistance"]:
                if abs(h - existing) / existing < threshold:
                    is_unique = False
                    break
            if is_unique:
                levels["resistance"].append(h)

        for l in lows:
            is_unique = True
            for existing in levels["support"]:
                if abs(l - existing) / existing < threshold:
                    is_unique = False
                    break
            if is_unique:
                levels["support"].append(l)

        levels["resistance"].sort(reverse=True)
        levels["support"].sort()

        return levels

    @staticmethod
    def nearest(price: float, levels: Dict[str, List[float]]) -> Tuple[float, float]:
        supports = levels.get("support", [])
        resistances = levels.get("resistance", [])

        nearest_support = max([s for s in supports if s < price] or [price * 0.95])
        nearest_resistance = min(
            [r for r in resistances if r > price] or [price * 1.05]
        )

        return nearest_support, nearest_resistance


class IndicatorEngine:
    def __init__(self):
        self.indicators = {
            "sma_20": None,
            "sma_50": None,
            "sma_200": None,
            "ema_12": None,
            "ema_26": None,
            "rsi": None,
            "macd": None,
            "bollinger": None,
            "atr": None,
            "vwap": None,
            "stochastic": None,
            "obv": None,
            "ichimoku": None,
        }

    async def calculate_all(self, candles: List[OHLCV]) -> MultiIndicatorResult:
        if len(candles) < 200:
            raise ValueError(f"Need at least 200 candles, got {len(candles)}")

        closes = [c.close for c in candles]
        highs = [c.high for c in candles]
        lows = [c.low for c in candles]
        opens = [c.open for c in candles]
        volumes = [c.volume for c in candles]

        result = MultiIndicatorResult(timestamp=candles[-1].timestamp)

        sma_20 = MovingAverage.sma(closes, 20)
        sma_50 = MovingAverage.sma(closes, 50)
        sma_200 = MovingAverage.sma(closes, 200)

        sma_cross = []
        for i in range(len(closes)):
            if math.isnan(sma_20[i]) or math.isnan(sma_50[i]):
                sma_cross.append("NEUTRAL")
            elif sma_20[i] > sma_50[i]:
                sma_cross.append("BULLISH")
            else:
                sma_cross.append("BEARISH")

        self.indicators["sma_20"] = sma_20[-1]
        self.indicators["sma_50"] = sma_50[-1]
        self.indicators["sma_200"] = sma_200[-1]

        result.indicators["sma_20"] = IndicatorResult(
            "SMA_20",
            sma_20[-1],
            sma_cross[-1],
            min(abs(sma_20[-1] - closes[-1]) / closes[-1] * 10, 1.0)
            if not math.isnan(sma_20[-1])
            else 0,
        )

        rsi_values = RSI.calculate(closes, 14)
        rsi_signal, rsi_strength = RSI.signal(rsi_values)
        self.indicators["rsi"] = rsi_values[-1]
        result.indicators["rsi"] = IndicatorResult(
            "RSI", rsi_values[-1], rsi_signal, rsi_strength
        )

        macd_data = MACD.calculate(closes, 12, 26, 9)
        macd_signal, macd_strength = MACD.signal(macd_data)
        self.indicators["macd"] = macd_data["macd"][-1]
        self.indicators["macd_signal"] = macd_data["signal"][-1]
        self.indicators["macd_hist"] = macd_data["histogram"][-1]
        result.indicators["macd"] = IndicatorResult(
            "MACD", macd_data["histogram"][-1], macd_signal, macd_strength
        )

        bb_data = BollingerBands.calculate(closes, 20, 2.0)
        bb_signal, bb_strength = BollingerBands.signal(closes, bb_data)
        self.indicators["bollinger_upper"] = bb_data["upper"][-1]
        self.indicators["bollinger_middle"] = bb_data["middle"][-1]
        self.indicators["bollinger_lower"] = bb_data["lower"][-1]
        result.indicators["bollinger"] = IndicatorResult(
            "BB", closes[-1], bb_signal, bb_strength
        )

        atr_values = ATR.calculate(candles, 14)
        atr_signal, atr_strength = ATR.volatility(atr_values, closes[-1])
        self.indicators["atr"] = atr_values[-1] if not math.isnan(atr_values[-1]) else 0
        result.indicators["atr"] = IndicatorResult(
            "ATR",
            atr_values[-1] if not math.isnan(atr_values[-1]) else 0,
            atr_signal,
            atr_strength,
        )

        vwap_values = VWAP.calculate(candles)
        vwap_signal, vwap_strength = VWAP.signal(closes, vwap_values)
        self.indicators["vwap"] = vwap_values[-1] if vwap_values else 0
        result.indicators["vwap"] = IndicatorResult(
            "VWAP", vwap_values[-1] if vwap_values else 0, vwap_signal, vwap_strength
        )

        stoch_data = Stochastic.calculate(candles, 14, 3)
        stoch_signal, stoch_strength = Stochastic.signal(stoch_data)
        self.indicators["stochastic_k"] = stoch_data["k"][-1]
        self.indicators["stochastic_d"] = stoch_data["d"][-1]
        result.indicators["stochastic"] = IndicatorResult(
            "STOCH", stoch_data["k"][-1], stoch_signal, stoch_strength
        )

        obv_values = OBV.calculate(candles)
        obv_signal, obv_strength = OBV.trend(obv_values)
        self.indicators["obv"] = obv_values[-1]
        result.indicators["obv"] = IndicatorResult(
            "OBV", obv_values[-1], obv_signal, obv_strength
        )

        ichimoku_data = Ichimoku.calculate(candles)
        ichimoku_signal, ichimoku_strength = Ichimoku.signal(ichimoku_data, closes[-1])
        self.indicators["ichimoku"] = ichimoku_signal
        result.indicators["ichimoku"] = IndicatorResult(
            "ICHIMOKU", 0, ichimoku_signal, ichimoku_strength
        )

        fib_levels = Fibonacci.levels(max(highs[-50:]), min(lows[-50:]))
        current_fib = Fibonacci.retrace(closes[-1], max(highs[-50:]), min(lows[-50:]))
        result.indicators["fibonacci"] = IndicatorResult(
            "FIBONACCI", 0, current_fib, 0.5
        )

        sr_levels = SupportResistance.find_levels(closes[-200:], 5, 0.02)
        sr_support, sr_resistance = SupportResistance.nearest(closes[-1], sr_levels)
        result.indicators["support"] = IndicatorResult(
            "SUPPORT", sr_support, "SUPPORT", 0.5
        )
        result.indicators["resistance"] = IndicatorResult(
            "RESISTANCE", sr_resistance, "RESISTANCE", 0.5
        )

        bullish_signals = ["BULLISH", "BULLISH_STRONG", "STRONG_BULLISH", "OVERSOLD"]
        bearish_signals = ["BEARISH", "BEARISH_STRONG", "STRONG_BEARISH", "OVERBOUGHT"]

        bullish_count = sum(
            1 for ind in result.indicators.values() if ind.signal in bullish_signals
        )
        bearish_count = sum(
            1 for ind in result.indicators.values() if ind.signal in bearish_signals
        )

        # Calculate confidence based on signal strength and confluence
        total_strength = sum(ind.strength for ind in result.indicators.values())
        avg_strength = total_strength / len(result.indicators)

        if bullish_count > bearish_count + 3:
            result.overall_signal = "STRONG_BUY"
            result.confidence = min(
                0.95, 0.5 + (bullish_count - bearish_count) * 0.05 + avg_strength * 0.3
            )
        elif bullish_count > bearish_count:
            result.overall_signal = "BUY"
            result.confidence = min(
                0.85, 0.5 + (bullish_count - bearish_count) * 0.03 + avg_strength * 0.25
            )
        elif bearish_count > bullish_count + 3:
            result.overall_signal = "STRONG_SELL"
            result.confidence = min(
                0.95, 0.5 + (bearish_count - bullish_count) * 0.05 + avg_strength * 0.3
            )
        elif bearish_count > bullish_count:
            result.overall_signal = "SELL"
            result.confidence = min(
                0.85, 0.5 + (bearish_count - bullish_count) * 0.03 + avg_strength * 0.25
            )
        else:
            result.overall_signal = "HOLD"
            result.confidence = 0.5

        if (
            result.indicators["rsi"].signal in bullish_signals
            and result.indicators["macd"].signal in bullish_signals
        ):
            result.momentum = "BULLISH"
        elif (
            result.indicators["rsi"].signal in bearish_signals
            and result.indicators["macd"].signal in bearish_signals
        ):
            result.momentum = "BEARISH"
        else:
            result.momentum = "NEUTRAL"

        if result.indicators["atr"].signal == "HIGH":
            result.volatility = "HIGH"
        elif result.indicators["atr"].signal == "LOW":
            result.volatility = "LOW"

        if sma_20[-1] > sma_50[-1] > sma_200[-1]:
            result.trend = "STRONG_UPTREND"
        elif sma_20[-1] > sma_50[-1]:
            result.trend = "UPTREND"
        elif sma_20[-1] < sma_50[-1] < sma_200[-1]:
            result.trend = "STRONG_DOWNTREND"
        elif sma_20[-1] < sma_50[-1]:
            result.trend = "DOWNTREND"
        else:
            result.trend = "NEUTRAL"

        return result


async def calculate_indicators(candles: List[OHLCV]) -> MultiIndicatorResult:
    engine = IndicatorEngine()
    return await engine.calculate_all(candles)
