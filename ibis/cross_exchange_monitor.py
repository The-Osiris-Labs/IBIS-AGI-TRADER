"""
IBIS Cross-Exchange Price Monitor
Detects price leading between exchanges for alpha capture
"""

import asyncio
from typing import Dict, Optional
from ibis.exchange.ccxt_client import CCXTClient
from ibis.core.trading_constants import TRADING


class CrossExchangeMonitor:
    """Monitor price differences across exchanges to detect leading indicators."""

    def __init__(self):
        self.binance = None
        self.price_cache = {}
        self.lead_threshold = TRADING.INTELLIGENCE.CROSS_EXCHANGE_LEAD_THRESHOLD  # 0.2%

    async def initialize(self):
        """Initialize Binance client for price comparison."""
        try:
            import os

            sandbox = os.environ.get("KUCOIN_IS_SANDBOX", "false").lower() == "true"
            paper_trading = os.environ.get("PAPER_TRADING", "false").lower() == "true"

            self.binance = CCXTClient(
                exchange="binance", sandbox=sandbox, paper_trading=paper_trading
            )
            if self.binance.is_available():
                print("✅ Cross-exchange monitor initialized (Binance)")
            else:
                print("⚠️ CCXT not available - cross-exchange monitoring disabled")
                self.binance = None
        except Exception as e:
            print(f"⚠️ Failed to initialize cross-exchange monitor: {e}")
            self.binance = None

    async def get_price_lead_signal(self, symbol: str, kucoin_price: float) -> Dict:
        """
        Compare KuCoin price to Binance to detect price leading.

        Returns:
            {
                'has_lead': bool,
                'lead_pct': float,
                'direction': 'binance_leading' | 'kucoin_leading' | 'neutral',
                'boost': int  # Score boost to apply
            }
        """
        if not self.binance or not self.binance.is_available():
            return {
                "has_lead": False,
                "lead_pct": 0,
                "direction": "neutral",
                "boost": 0,
            }

        try:
            # Convert KuCoin symbol format (BTC-USDT) to Binance format (BTC/USDT)
            binance_symbol = symbol.replace("-", "/")

            # Fetch Binance price
            tickers = await self.binance.fetch_tickers([binance_symbol])

            if not tickers or binance_symbol not in tickers:
                return {
                    "has_lead": False,
                    "lead_pct": 0,
                    "direction": "neutral",
                    "boost": 0,
                }

            binance_price = tickers[binance_symbol].price

            if binance_price <= 0 or kucoin_price <= 0:
                return {
                    "has_lead": False,
                    "lead_pct": 0,
                    "direction": "neutral",
                    "boost": 0,
                }

            # Calculate price difference
            price_diff_pct = ((binance_price - kucoin_price) / kucoin_price) * 100

            # 🚨 CIRCUIT BREAKER: Extreme price differences indicate data errors
            if abs(price_diff_pct) > 10.0:  # More than 10% difference = data error
                return {
                    "has_lead": True,
                    "lead_pct": price_diff_pct,
                    "direction": "data_error",
                    "boost": -100,  # Complete score neutralization
                    "binance_price": binance_price,
                    "kucoin_price": kucoin_price,
                }

            # Determine if there's a significant lead
            if abs(price_diff_pct) < self.lead_threshold * 100:
                return {
                    "has_lead": False,
                    "lead_pct": price_diff_pct,
                    "direction": "neutral",
                    "boost": 0,
                }

            # Binance leading upward = KuCoin likely to follow = BUY signal
            if price_diff_pct > self.lead_threshold * 100:
                boost = min(
                    10, int(price_diff_pct * 20)
                )  # 0.2% lead = +4 boost, 0.5% = +10
                return {
                    "has_lead": True,
                    "lead_pct": price_diff_pct,
                    "direction": "binance_leading",
                    "boost": boost,
                    "binance_price": binance_price,
                    "kucoin_price": kucoin_price,
                }

            # KuCoin leading upward = Binance catching up = potential reversal
            elif price_diff_pct < -self.lead_threshold * 100:
                penalty = min(5, int(abs(price_diff_pct) * 10))
                return {
                    "has_lead": True,
                    "lead_pct": price_diff_pct,
                    "direction": "kucoin_leading",
                    "boost": -penalty,  # Negative boost = caution
                    "binance_price": binance_price,
                    "kucoin_price": kucoin_price,
                }

        except Exception as e:
            # Silently fail - don't disrupt trading if cross-exchange check fails
            pass

        return {"has_lead": False, "lead_pct": 0, "direction": "neutral", "boost": 0}

    async def close(self):
        """Clean up resources."""
        if self.binance:
            self.binance.close()


# Example usage in ibis_true_agent.py:
"""
# In __init__:
self.cross_exchange = CrossExchangeMonitor()

# In initialize():
await self.cross_exchange.initialize()

# In analyze_opportunity():
lead_signal = await self.cross_exchange.get_price_lead_signal(
    symbol=f"{currency}-USDT",
    kucoin_price=current_price
)

if lead_signal['has_lead']:
    if lead_signal['direction'] == 'binance_leading':
        # Binance is ahead, KuCoin likely to follow
        score += lead_signal['boost']
        self.log_event(f"      🔥 PRICE LEAD: Binance +{lead_signal['lead_pct']:.2f}% ahead, boost +{lead_signal['boost']}")
    elif lead_signal['direction'] == 'kucoin_leading':
        # KuCoin ahead, potential reversal risk
        score += lead_signal['boost']  # Negative boost
        self.log_event(f"      ⚠️ PRICE LAG: KuCoin +{abs(lead_signal['lead_pct']):.2f}% ahead, caution -{abs(lead_signal['boost'])}")
"""
