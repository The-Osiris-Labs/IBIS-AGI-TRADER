"""
IBIS v8 LIMITLESS SWING STRATEGY
Targets >2% moves to overcome basic fee tiers.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from .base import TradingStrategy

class LimitlessSwing(TradingStrategy):
    def __init__(self, config):
        super().__init__("LimitlessSwing_v1", config)
        self.min_roi = config['MIN_VIABLE_TARGET']  # 0.8%
        self.stop_loss = config['STOP_LOSS_PCT']  # 2.5%
        self.take_profit = config['TAKE_PROFIT_PCT']  # 4.0%
        
    def calculate_indicators(self, candles: pd.DataFrame):
        """Calculate basic trend indicators."""
        df = candles.copy()
        
        # EMA for Trend
        df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        
        # RSI for Momentum
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df.iloc[-1]  # Return latest candle with indicators

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze standardized market data to determine BUY/SELL.
        Required data keys: 'ohlcv_15m', 'current_price', 'agi_score'
        """
        candles = pd.DataFrame(data['ohlcv_15m'])
        if candles.empty:
            return {'signal': 'HOLD', 'score': 0, 'reason': 'No Data'}
            
        current = self.calculate_indicators(candles)
        price = data['current_price']
        agi_score = data.get('agi_score', 50)  # Default neutral
        
        # 1. Trend Filter: Price > EMA 50 (Uptrend)
        trend_bullish = price > current['ema_50']
        
        # 2. Momentum Filter: RSI > 45 (Not Overbought yet) and < 70
        momentum_ok = 45 < current['rsi'] < 70
        
        # 3. AGI Confirmation
        agi_bullish = agi_score >= 70
        
        # 4. Cross-Exchange Helper (Binance Lead)
        binance_lead = data.get('lead_signal', {}).get('has_lead', False)
        
        # SIGNAL LOGIC
        score = 50
        reason = []
        
        if trend_bullish:
            score += 20
            reason.append("Trend Bullish")
        
        if momentum_ok:
            score += 10
            reason.append("Momentum Healthy")
            
        if agi_bullish:
            score += 15
            reason.append("AGI Confirmed")
            
        if binance_lead:
            score += 15  # Strong signal
            reason.append("Binance Leading")
            
        if score >= 85:  # High conviction only for swing
            return {
                'signal': 'BUY',
                'score': score,
                'target': price * (1 + self.take_profit),
                'stop': price * (1 - self.stop_loss),
                'reason': ", ".join(reason)
            }
            
        return {'signal': 'HOLD', 'score': score, 'reason': "Weak Conviction"}

    def should_exit(self, position: Dict[str, Any], current_price: float) -> bool:
        """
        Check if we hit TP or SL.
        """
        entry = position['entry_price']
        pnl_pct = (current_price - entry) / entry
        
        # Hard Stop Loss
        if pnl_pct <= -self.stop_loss:
            return True, "STOP_LOSS"
            
        # Take Profit
        if pnl_pct >= self.take_profit:
            return True, "TAKE_PROFIT"
            
        # Trailing Stop (Dynamic)
        # If we are up 1.5%, move stop to breakeven + fees
        if pnl_pct > 0.015 and current_price < position.get('highest_price', 0) * 0.995:
             return True, "TRAILING_STOP"
             
        return False, None
