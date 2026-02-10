from abc import ABC, abstractmethod
from typing import Dict, Any, List

class TradingStrategy(ABC):
    """Base class for all IBIS trading strategies."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self._positions = {}
        self.active = True

    @abstractmethod
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market data and return a signal.
        Args:
            data: Standardized market data (OHLCV, OrderBook, Tickers)
        Returns:
            Dict containing 'signal': 'BUY'|'SELL'|'HOLD', 'score': float, 'reason': str
        """
        pass

    @abstractmethod
    def on_tick(self, tick: Dict[str, Any]):
        """Handle real-time tick data."""
        pass

    @abstractmethod
    def should_exit(self, position: Dict[str, Any], current_price: float) -> bool:
        """Determines if a position should be closed."""
        pass
