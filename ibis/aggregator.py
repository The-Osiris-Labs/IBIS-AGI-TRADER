"""Optional multi-exchange aggregator.

Uses KuCoin client as primary. If ccxt is installed, it can aggregate extra tickers.
"""

from typing import Dict


class MarketAggregator:
    def __init__(self, kucoin_client):
        self.kucoin = kucoin_client
        try:
            import ccxt  # type: ignore

            self.ccxt = ccxt
        except Exception:
            self.ccxt = None

    async def get_primary_tickers(self) -> Dict:
        tickers = await self.kucoin.get_tickers()
        return {t.symbol: t for t in tickers}

    def get_ccxt_tickers(self, exchange_id: str = "binance") -> Dict:
        if not self.ccxt:
            return {}
        ex = getattr(self.ccxt, exchange_id)()
        return ex.fetch_tickers()
