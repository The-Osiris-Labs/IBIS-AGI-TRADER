"""
IBIS v8 LIMITLESS SWING STRATEGY (NATIVE PYTHON)
Targets >2% moves to overcome basic fee tiers.
Uses NO heavy dependencies (pandas/numpy).
"""

from typing import Dict, Any, List
from .base import TradingStrategy
from ..core.config import Config

class Indicators:
    @staticmethod
    def calculate_ema(data: List[float], span: int) -> float:
        """Calculate latest EMA."""
        if not data: return 0.0
        alpha = 2 / (span + 1)
        ema = data[0]
        for price in data[1:]:
            ema = (price * alpha) + (ema * (1 - alpha))
        return ema

    @staticmethod
    def calculate_rsi(data: List[float], period: int = 14) -> float:
        """Calculate latest RSI."""
        if len(data) < period + 1: return 50.0  # Default neutral
        
        deltas = [data[i] - data[i-1] for i in range(1, len(data))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [abs(d) if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        if avg_loss == 0: return 100.0
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

class NativeLimitlessSwing(TradingStrategy):
    def __init__(self, config):
        config_dict = {
            'MIN_VIABLE_TARGET': Config.MIN_VIABLE_TARGET,
            'STOP_LOSS_PCT': Config.STOP_LOSS_PCT,
            'TAKE_PROFIT_PCT': Config.TAKE_PROFIT_PCT
        }
        super().__init__("LimitlessSwing_v1_Native", config_dict)
        self.min_roi = Config.MIN_VIABLE_TARGET
        self.stop_loss = Config.STOP_LOSS_PCT
        self.take_profit = Config.TAKE_PROFIT_PCT
        
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze using pure python lists.
        Required: data['ohlcv_15m'] (Listing of closing prices)
        """
        closes = data.get('closes_15m', [])
        if not closes or len(closes) < 50:
            return {'signal': 'HOLD', 'score': 0, 'reason': 'Insufficient Data'}
            
        current_price = data['current_price']
        
        # Calculate Indicators
        ema_50 = Indicators.calculate_ema(closes, 50)
        rsi_14 = Indicators.calculate_rsi(closes, 14)
        
        # 1. Trend Filter: Price > EMA 50
        trend_bullish = current_price > ema_50
        
        # 2. Momentum Filter: 45 < RSI < 70
        momentum_ok = 45 < rsi_14 < 70
        
        # 3. AGI Confirmation
        agi_score = data.get('agi_score', 50)
        agi_bullish = agi_score >= 70
        
        # 4. Cross-Exchange Helper
        binance_lead = data.get('lead_signal', {}).get('has_lead', False)
        
        score = 50
        reasons = []
        
        if trend_bullish:
            score += 20
            reasons.append(f"Trend > EMA50 ({ema_50:.4f})")
            
        if momentum_ok:
            score += 10
            reasons.append(f"Momentum OK ({rsi_14:.1f})")
            
        if agi_bullish:
            score += 15
            reasons.append(f"AGI Strong ({agi_score})")
            
        if binance_lead:
            score += 15
            reasons.append("Binance Lead")
            
        # BUY SIGNAL
        if score >= 85:
            return {
                'signal': 'BUY',
                'score': score,
                'target': current_price * (1 + self.take_profit),
                'stop': current_price * (1 - self.stop_loss),
                'price': current_price,
                'reason': ", ".join(reasons)
            }
            
        return {'signal': 'HOLD', 'score': score, 'reason': "Weak Signal"}

    def should_exit(self, position_key: str, entry_price: float, current_price: float, highest_price: float) -> (bool, str):
        """
        Check exit conditions.
        """
        pnl_pct = (current_price - entry_price) / entry_price
        
        # Hard Stop Loss
        if pnl_pct <= -self.stop_loss:
            return True, "STOP_LOSS"
            
        # Take Profit
        if pnl_pct >= self.take_profit:
            return True, "TAKE_PROFIT"
            
        # Trailing Stop Breakdown (Profit Protection)
        # If up > 1.5%, trail stop at 0.5% below high
        if pnl_pct > 0.015:
            trail_stop = highest_price * 0.995
            if current_price < trail_stop:
                return True, "TRAILING_STOP"
             
        return False, None

    def on_tick(self, tick: Dict[str, Any]):
        """Handle real-time tick data."""
        # Simple swing strategy doesn't need tick-level updates yet
        pass
