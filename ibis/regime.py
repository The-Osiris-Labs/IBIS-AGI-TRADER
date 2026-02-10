"""Market regime detector for spot trading."""

from dataclasses import dataclass
from typing import List
import math


@dataclass
class RegimeResult:
    label: str
    volatility: float
    trend_slope: float
    strength: float


def _linear_slope(values: List[float]) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    x_mean = (n - 1) / 2
    y_mean = sum(values) / n
    num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    den = sum((i - x_mean) ** 2 for i in range(n))
    return num / den if den else 0.0


def detect_regime(closes: List[float]) -> RegimeResult:
    if len(closes) < 20:
        return RegimeResult("UNKNOWN", 0.0, 0.0, 0.0)

    returns = [(closes[i] - closes[i - 1]) / max(closes[i - 1], 1e-9) for i in range(1, len(closes))]
    vol = (sum(r * r for r in returns) / max(len(returns), 1)) ** 0.5
    slope = _linear_slope(closes[-20:])

    # Normalize slope by price
    slope_norm = slope / max(closes[-1], 1e-9)

    if vol > 0.03 and slope_norm > 0:
        label = "HIGH_VOL_UP"
    elif vol > 0.03 and slope_norm < 0:
        label = "HIGH_VOL_DOWN"
    elif slope_norm > 0.0005:
        label = "TREND_UP"
    elif slope_norm < -0.0005:
        label = "TREND_DOWN"
    else:
        label = "RANGE"

    strength = min(1.0, abs(slope_norm) * 200 + vol * 5)
    return RegimeResult(label, vol, slope_norm, strength)
