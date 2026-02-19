# Advanced Intelligence Enhancement Module for IBIS

This module enhances the IBIS system's capabilities in four key areas:

## 1. Fee Analysis Enhancement

**Real-time fee tracking and analysis** - Monitors fees across all trading activities in real-time
**Fee optimization recommendations** - Provides actionable suggestions to reduce trading costs
**Fee impact on profitability per symbol** - Analyzes how fees affect profitability for each traded symbol
**Historical fee trend analysis** - Tracks fee patterns over time to identify cost-saving opportunities

## 2. Market Movement Understanding

**Enhanced trend detection and strength measurement** - Uses multiple indicators to determine trend direction and strength
**Volatility analysis with multiple timeframes** - Analyzes volatility across different time periods
**Market regime classification improvements** - Identifies market regimes (volatile, stable, trending, etc.)
**Support/resistance level detection** - Automatically detects key support and resistance levels
**Price action pattern recognition** - Recognizes common price patterns (engulfing, hammer, etc.)

## 3. Symbol Movement Analysis

**Symbol-specific trend patterns** - Identifies unique trend characteristics for each symbol
**Volatility profile per symbol** - Creates volatility profiles for individual symbols
**Correlation analysis between symbols** - Measures correlation between different trading pairs
**Volume and liquidity analysis** - Analyzes trading volume and liquidity patterns
**Recent price action behavior** - Tracks recent price movements and behavior patterns

## 4. Profitability Attribution

**Fee impact on P&L for each trade** - Quantifies how fees affect each trade's profitability
**Market conditions impact on profitability** - Analyzes how different market conditions influence performance
**Symbol performance across different market regimes** - Measures symbol performance in various market regimes

## Usage Examples

### Initialize the Advanced Intelligence System

```python
from ibis.advanced_intelligence import AdvancedIntelligenceEnhancement
from ibis.pnl_tracker import PnLTracker

# Create PnL tracker instance
pnl_tracker = PnLTracker()

# Initialize advanced intelligence system
ai = AdvancedIntelligenceEnhancement(pnl_tracker)
```

### Fee Analysis

```python
# Analyze fees for a specific symbol
fee_analysis = pnl_tracker.get_fee_analysis("BTC")
print("Fee Analysis Results:")
print(f"Total Fees: ${fee_analysis['analysis']['total_fees']:.2f}")
print(f"Average Fee Rate: {fee_analysis['analysis']['avg_fee_rate']:.4%}")
print(f"Fee Impact on Profitability: {fee_analysis['analysis']['fee_impact_pct']:.2f}%")

# Get fee optimization recommendations
recommendations = fee_analysis['recommendations']
print("\nOptimization Recommendations:")
for rec in recommendations['recommendations']:
    print(f"{rec['type']}: {rec['action']}")
    print(f"Potential Savings: {rec['potential_savings']:.4%}")
```

### Market Movement Analysis

```python
from ibis.advanced_intelligence import MarketMovementAnalyzer
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Create test price data
dates = pd.date_range(start="2024-01-01", periods=100, freq="h")
prices = np.cumsum(np.random.randn(100) * 0.001 + 0.002) + 100
volume = np.random.randint(1000, 10000, size=100)

price_data = pd.Series(prices, index=dates)
volume_data = pd.Series(volume, index=dates)

# Initialize market movement analyzer
analyzer = MarketMovementAnalyzer()

# Detect trend strength
trend_result = analyzer.detect_trend_strength(price_data)
print("Trend Analysis:")
print(f"Direction: {trend_result['direction']}")
print(f"Strength: {trend_result['strength']:.0f}%")
print(f"Confidence: {trend_result['confidence']:.2f}")

# Classify market regime
regime = analyzer.classify_market_regime(price_data, volume_data)
print("\nMarket Regime:")
print(f"Type: {regime.regime_type}")
print(f"Volatility: {regime.volatility:.4f}")
print(f"Trend Strength: {regime.trend_strength:.0f}%")
print(f"Volume Profile: {regime.volume_profile}")

# Detect support/resistance levels
support_resistance = analyzer.detect_support_resistance(price_data)
print("\nSupport/Resistance Levels:")
print(f"Support: {[f'{x:.2f}' for x in support_resistance['support']]}")
print(f"Resistance: {[f'{x:.2f}' for x in support_resistance['resistance']]}")
```

### Symbol Movement Analysis

```python
from ibis.advanced_intelligence import SymbolMovementAnalyzer

# Initialize symbol movement analyzer
symbol_analyzer = SymbolMovementAnalyzer()

# Analyze symbol movement (BTC)
btc_profile = symbol_analyzer.analyze_symbol_movement("BTC", price_data, volume_data)
print("BTC Movement Profile:")
print(f"Trend Pattern: {btc_profile.trend_pattern}")
print(f"Volatility Profile: {btc_profile.volatility_profile}")
print(f"Volume Profile: {btc_profile.volume_profile}")
print(f"Liquidity Score: {btc_profile.liquidity_score:.2f}")
print(f"Recent Behavior: {btc_profile.recent_price_behavior}")
```

### Profitability Attribution

```python
from ibis.advanced_intelligence import ProfitabilityAttributor

# Initialize profitability attributor
attributor = ProfitabilityAttributor()

# Load matched trades
matched_trades = pnl_tracker.match_trades_fifo()

# Attribute profitability to fees, market conditions, and regimes
attribution = attributor.attribute_profitability(matched_trades)
print("Profitability Attribution:")
print(f"Total PnL: ${attribution.total_pnl:.2f}")
print(f"Fee Impact: {attribution.fee_impact:.2f}%")
print(f"Market Conditions Impact: {attribution.market_conditions_impact:.2f}%")
print(f"Risk-Adjusted Return: {attribution.risk_adjusted_return:.2f}")

# Regime performance
print("\nRegime Performance:")
for regime, performance in attribution.regime_performance.items():
    print(f"{regime}: ${performance:.2f}")
```

### Comprehensive Analysis

```python
# Get comprehensive analysis of all symbols
analysis_results = ai.analyze_all(
    matched_trades,
    {"BTC": price_data},
    {"BTC": volume_data}
)

# Generate comprehensive report
report = ai.generate_comprehensive_report(analysis_results)

print("Comprehensive Analysis Report:")
print(f"Total PnL: ${report['summary']['total_pnl']:.2f}")
print(f"Total Fees: ${report['summary']['total_fees']:.2f}")
print(f"Fee Impact: {report['summary']['fee_impact_pct']:.2f}%")
print(f"Symbols Analyzed: {report['summary']['symbols_analyzed']}")
```

## Integration Points

### With Existing Systems

1. **PnL Tracker Integration** - Enhances existing fee calculation functionality
2. **Market Intelligence Integration** - Improves market analysis capabilities
3. **Risk Management Integration** - Provides better risk assessment through volatility analysis
4. **Trading Strategy Integration** - Enables strategy optimization based on fee and market analysis

### API Endpoints

The advanced intelligence module exposes several key methods:

- `get_fee_analysis()` - Returns fee analysis results
- `detect_trend_strength()` - Detects trend direction and strength
- `classify_market_regime()` - Classifies market regimes
- `detect_support_resistance()` - Identifies support/resistance levels
- `analyze_symbol_movement()` - Analyzes symbol-specific movement
- `attribute_profitability()` - Attributes profitability to various factors
- `analyze_all()` - Provides comprehensive analysis of all aspects
- `generate_comprehensive_report()` - Generates detailed reports

## Technical Requirements

- Python 3.8+
- pandas
- numpy
- scipy
- pytest (for testing)

## Installation

The module is automatically available when installing the IBIS system. No additional installation is required.

## Testing

Run the comprehensive test suite:

```bash
python3 -m pytest test_advanced_intelligence.py -v
```

The tests cover all key functionality:
- Fee analyzer tests
- Market movement analyzer tests
- Symbol movement analyzer tests
- Profitability attributor tests
- Advanced intelligence integration tests