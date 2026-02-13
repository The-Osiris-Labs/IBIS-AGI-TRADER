"""
Enhanced Intelligence Module
Improves market sniping and price action prediction
"""

from datetime import datetime


def calculate_volume_momentum(volumes: list) -> float:
    """Calculate volume momentum - increasing or decreasing volume"""
    if len(volumes) < 3:
        return 0.5
    recent_avg = sum(volumes[-3:]) / 3
    older_avg = sum(volumes[:-3]) / len(volumes[:-3]) if len(volumes) > 3 else recent_avg
    if older_avg == 0:
        return 0.5
    return min(recent_avg / older_avg, 3.0)  # Cap at 3x


def detect_breakout(closes: list, volume: list, threshold: float = 0.02) -> dict:
    """Detect breakout patterns - strong upward moves with volume confirmation"""
    if len(closes) < 5:
        return {"breakout": False, "strength": 0, "confirmed": False}

    # Price momentum
    price_change = (closes[-1] - closes[-5]) / closes[-5] if closes[-5] > 0 else 0

    # Volume confirmation
    vol_momentum = calculate_volume_momentum(volume)

    # Breakout criteria: price up > threshold% AND volume increasing
    breakout = price_change > threshold and vol_momentum > 1.2

    return {
        "breakout": breakout,
        "strength": price_change * vol_momentum,
        "confirmed": breakout and vol_momentum > 1.5,
        "price_momentum": price_change,
        "volume_momentum": vol_momentum,
    }


def calculate_price_action_score(closes: list, volumes: list) -> float:
    """
    Enhanced price action scoring:
    - Recent momentum (70%)
    - Volume confirmation (20%)
    - Volatility quality (10%)
    """
    if len(closes) < 5:
        return 50.0

    # Recent momentum (last 3 candles)
    recent_returns = [
        (closes[i] - closes[i - 1]) / closes[i - 1] for i in range(-3, 0) if closes[i - 1] > 0
    ]
    momentum = sum(recent_returns) / len(recent_returns) if recent_returns else 0

    # Volume confirmation
    vol_mom = calculate_volume_momentum(volumes)

    # Volatility - lower is better for steady moves
    volatility = sum(abs(r) for r in recent_returns) / len(recent_returns) if recent_returns else 0

    # Combined score (0-100)
    score = (
        (momentum * 10000 * 0.70)  # 70% weight on momentum
        + (vol_mom * 20 * 0.20)  # 20% weight on volume
        + ((1 - min(volatility * 100, 1)) * 50 * 0.10)  # 10% weight on low volatility
    )

    return max(0, min(100, score + 50))  # Center around 50


def rank_by_upward_momentum(opportunities: list) -> list:
    """Rank opportunities by upward momentum potential"""
    scored = []
    for opp in opportunities:
        score = opp.get("score", 50)
        price_action = opp.get("price_action_score", 50)
        volume_mom = opp.get("volume_momentum", 0.5)
        breakout = opp.get("breakout", False)

        # Boost for strong signals
        boost = 0
        if breakout:
            boost += 15
        if volume_mom > 1.5:
            boost += 10
        if price_action > 60:
            boost += 5

        final_score = min(100, score + boost)
        scored.append((opp, final_score))

    # Sort by final score descending
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


def predict_upward_move(closes: list, volumes: list, lookback: int = 6) -> dict:
    """Predict probability of upward move based on patterns"""
    if len(closes) < lookback:
        return {"probability": 50, "confidence": "low"}

    # Pattern analysis
    recent = closes[-lookback:]
    volumes_recent = volumes[-lookback:]

    # Check for accumulation pattern (up close on high volume)
    if len(recent) > 1:
        up_days = sum(1 for i in range(1, len(recent)) if recent[i] > recent[i - 1])
    else:
        up_days = 0
    volume_increasing = calculate_volume_momentum(volumes_recent)

    # Calculate probability
    base_prob = 50

    # Accumulation signals
    if up_days >= lookback * 0.7:  # 70% up days
        base_prob += 15
    if volume_increasing > 1.3:
        base_prob += 10

    # Recent strength
    recent_momentum = (recent[-1] - recent[0]) / recent[0] if recent[0] > 0 else 0
    if recent_momentum > 0.02:  # >2% move
        base_prob += 5

    return {
        "probability": min(95, max(5, base_prob)),
        "confidence": "high" if volume_increasing > 1.5 and up_days >= lookback * 0.6 else "medium",
    }


def score_snipe_opportunity(
    symbol: str,
    closes: list,
    volumes: list,
    technical_score: float,
    agi_score: float,
    mtf_score: float,
    volume_24h: float,
    fear_greed_index: int = 50,
    momentum_1h: float = 0,
    change_24h: float = 0,
    min_volume: float = 50000,
) -> dict:
    """
    Comprehensive snipe opportunity scoring combining all enhanced signals.
    Returns detailed scoring breakdown and final recommendation.
    """
    # Calculate enhanced signals
    price_action_score = calculate_price_action_score(closes, volumes)
    breakout_data = detect_breakout(closes, volumes)
    upward_prediction = predict_upward_move(closes, volumes)
    volume_momentum = calculate_volume_momentum(volumes)

    # Volume score (0-100)
    if volume_24h > 0:
        vol_ratio = min(volume_24h / min_volume, 10)
        volume_score = min(vol_ratio * 20, 100)
    else:
        volume_score = 0

    # Sentiment score
    if fear_greed_index <= 25:
        sentiment_score = 70
    elif fear_greed_index <= 45:
        sentiment_score = 55
    elif fear_greed_index <= 55:
        sentiment_score = 50
    elif fear_greed_index <= 75:
        sentiment_score = 45
    else:
        sentiment_score = 30

    # Weights for final score - more aggressive
    weights = {
        "technical": 0.15,
        "agi": 0.20,
        "mtf": 0.10,
        "price_action": 0.30,
        "volume": 0.15,
        "sentiment": 0.10,
    }

    # Calculate final unified score
    unified_score = (
        technical_score * weights["technical"]
        + agi_score * weights["agi"]
        + mtf_score * weights["mtf"]
        + price_action_score * weights["price_action"]
        + volume_score * weights["volume"]
        + sentiment_score * weights["sentiment"]
    )

    # Apply boosts from enhanced signals - more aggressive
    boosts = 0
    if breakout_data["breakout"]:
        boosts += 15
        if breakout_data["confirmed"]:
            boosts += 10
    if volume_momentum > 1.3:
        boosts += 8
    if volume_momentum > 1.8:
        boosts += 12
    if upward_prediction["probability"] >= 65:
        boosts += 8
    if upward_prediction["probability"] >= 75:
        boosts += 15
    if upward_prediction["confidence"] == "high":
        boosts += 10

    final_score = min(100, unified_score + boosts)

    # Determine tier
    if final_score >= 90:
        tier = "GOD_TIER"
        position_size = 1.0
        tp_pct = 0.030
    elif final_score >= 80:
        tier = "HIGH_CONFIDENCE"
        position_size = 0.8
        tp_pct = 0.025
    elif final_score >= 70:
        tier = "STRONG_SETUP"
        position_size = 0.6
        tp_pct = 0.020
    elif final_score >= 60:
        tier = "STANDARD"
        position_size = 0.4
        tp_pct = 0.015
    else:
        tier = "WEAK"
        position_size = 0.2
        tp_pct = 0.010

    return {
        "symbol": symbol,
        "final_score": round(final_score, 2),
        "tier": tier,
        "unified_score": round(unified_score, 2),
        "boosts": boosts,
        "components": {
            "technical_score": round(technical_score, 2),
            "agi_score": round(agi_score, 2),
            "mtf_score": round(mtf_score, 2),
            "price_action_score": round(price_action_score, 2),
            "volume_score": round(volume_score, 2),
            "sentiment_score": round(sentiment_score, 2),
        },
        "enhanced_signals": {
            "breakout": breakout_data,
            "volume_momentum": round(volume_momentum, 3),
            "upward_prediction": upward_prediction,
        },
        "recommendation": {
            "action": "BUY" if final_score >= 70 else "WATCH" if final_score >= 60 else "SKIP",
            "position_size_factor": position_size,
            "take_profit_pct": tp_pct,
            "stop_loss_pct": 0.012,
        },
        "timestamp": datetime.now().isoformat(),
    }
