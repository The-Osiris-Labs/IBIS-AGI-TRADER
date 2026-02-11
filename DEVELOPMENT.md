# Developer Guide

This guide helps developers understand, modify, and extend IBIS.

---

## Project Structure

```
AGI Trader/
├── ibis_true_agent.py        # Main agent (5000+ lines)
├── ibis/                      # Core modules
│   ├── core/
│   │   └── trading_constants.py  # Risk settings
│   ├── exchange/
│   │   └── kucoin_client.py      # KuCoin API wrapper
│   ├── indicators/
│   │   └── indicators.py         # RSI, MACD, BB, etc.
│   ├── enhanced_intel.py         # Intelligence streams
│   ├── free_intelligence.py       # Free data sources
│   ├── cross_exchange_monitor.py # Multi-exchange monitoring
│   └── keys.env                  # API keys (not in git)
├── data/                        # Runtime data
│   ├── ibis_true_state.json      # Positions, capital
│   ├── ibis_true_memory.json     # Learned patterns
│   └── ibis_true.log            # Activity log
├── start_ibis.sh               # Startup script
└── *.md                        # Documentation
```

---

## Core Concepts

### The Main Agent Loop

The agent runs in `run()` function (line ~4954):

```python
async def run(self):
    await self.initialize()
    self._load_state()

    while True:
        # 1. Update awareness
        await self.update_positions_awareness()
        await self.update_capital_awareness()

        # 2. Learn
        await self.learn_from_experience()
        await self.update_adaptive_risk()

        # 3. Analyze markets
        await self.analyze_market_intelligence()

        # 4. Detect regime & decide
        regime = await self.detect_market_regime()
        mode = await self.determine_agent_mode(regime, self.market_intel)

        # 5. Execute
        await self.execute_strategy(regime, mode)
        opportunities = await self.find_all_opportunities(strategy)

        # 6. Monitor
        await self.check_positions(strategy)

        # 7. Sleep
        await asyncio.sleep(interval)
```

### State Management

IBIS has two data stores:

1. **State** - Current runtime data
   - Positions, orders, capital
   - Daily stats
   - Current regime/mode

2. **Memory** - Historical learning
   - Performance by symbol
   - Learned regimes
   - Market insights

Both are JSON files, easy to inspect:

```python
from ibis.data_consolidation import load_state, load_memory

state = load_state()
memory = load_memory()
```

---

## Key Classes

### IBISTrueAgent

The main trading agent. Key methods:

| Method | Purpose |
|--------|---------|
| `run()` | Main loop |
| `initialize()` | Setup connections, load state |
| `analyze_market_intelligence()` | Scan for opportunities |
| `execute_strategy()` | Execute trades |
| `find_all_opportunities()` | Score and rank opportunities |
| `open_position()` | Enter a trade |
| `close_position()` | Exit a trade |
| `check_positions()` | Monitor existing positions |
| `learn_from_experience()` | Update memory |

### KuCoinClient

Exchange connection. Key methods:

```python
client = get_kucoin_client()

# Market data
ticker = await client.get_ticker("BTC-USDT")
candles = await client.get_candles("BTC-USDT", "5min", 24)
orderbook = await client.get_orderbook("BTC-USDT")

# Trading
order = await client.place_order("BTC-USDT", "buy", "limit", price=50000, size=0.001)
await client.cancel_order(order_id)
positions = await client.get_positions()
```

### EnhancedIntelStreams

Multi-source intelligence:

```python
streams = EnhancedIntelStreams()

# Get scores from various sources
sentiment = await streams.get_social_sentiment("BTC")
onchain = await streams.get_onchain_metrics("BTC")
news = await streams.get_news_sentiment("BTC")
orderbook = await streams.get_orderbook_snapshot("BTC")

# Get unified score
unified = await streams.get_unified_intel_score("BTC")
```

---

## Adding New Indicators

To add a new technical indicator:

1. **Add to indicators.py:**

```python
class MyIndicator:
    @staticmethod
    def calculate(prices: List[float], period: int = 14) -> List[float]:
        # Your calculation
        return results

    @staticmethod
    def signal(values: List[float]) -> Tuple[str, float]:
        # Return (signal_name, strength)
        return "BULLISH", 0.75
```

2. **Import in ibis_true_agent.py:**

```python
from ibis.indicators.indicators import MyIndicator
```

3. **Use in _calculate_enhanced_intel:**

```python
def _calculate_enhanced_intel(self, candles, price):
    # Calculate
    my_values = MyIndicator.calculate(closes, 14)
    signal, strength = MyIndicator.signal(my_values)

    # Add to result
    result["my_indicator"] = {
        "signal": signal,
        "strength": strength,
        "value": my_values[-1]
    }

    # Add to score
    if signal == "BULLISH":
        score += 10

    return result
```

---

## Adding New Strategies

Strategies are selected in `determine_agent_mode()` (line ~2627):

```python
async def determine_agent_mode(self, regime, market_intel):
    if regime == "STRONG_BULL":
        return "HYPER_INTELLIGENT"
    elif regime == "VOLATILE":
        return "VOLATILE_adaptive"
    # ...
```

To add a new strategy:

1. **Define the strategy logic** in `execute_strategy()`:

```python
async def execute_strategy(self, regime, mode):
    if mode == "MY_NEW_STRATEGY":
        strategy = {
            "name": "MY_NEW_STRATEGY",
            "max_positions": 3,  # Conservative
            "available": capital * 0.2,  # Small positions
            "tp_multiplier": 1.0,  # Normal take profit
            "sl_multiplier": 1.5,  # Wider stops
        }
    # ...
    return strategy
```

2. **Add to mode selection:**

```python
async def determine_agent_mode(self, regime, market_intel):
    if regime == "FLAT" and self._is_opportunity_above_threshold(market_intel):
        return "MY_NEW_STRATEGY"
```

3. **Handle in trade execution** (optional - some strategies share logic)

---

## Modifying Risk Parameters

Risk parameters are in `ibis/core/trading_constants.py`:

```python
@dataclass
class RiskConfig:
    BASE_RISK_PER_TRADE: float = 0.02      # 2% per trade
    MIN_RISK_PER_TRADE: float = 0.005      # 0.5% minimum
    MAX_RISK_PER_TRADE: float = 0.05       # 5% maximum
    STOP_LOSS_PCT: float = 0.05            # 5% stop loss
    TAKE_PROFIT_PCT: float = 0.015          # 1.5% take profit
```

**WARNING:** Changing these affects real money. Always test in paper mode first.

---

## Configuration Access

Throughout the codebase:

```python
from ibis.core.trading_constants import TRADING

# Risk settings
TRADING.RISK.STOP_LOSS_PCT        # 0.05
TRADING.RISK.TAKE_PROFIT_PCT      # 0.015
TRADING.RISK.BASE_RISK_PER_TRADE # 0.02

# Position settings
TRADING.POSITION.MAX_TOTAL_POSITIONS          # 5
TRADING.POSITION.MIN_CAPITAL_PER_TRADE        # 5.0
TRADING.POSITION.MAX_CAPITAL_PER_TRADE        # 30.0

# Score thresholds
TRADING.SCORE.GOD_TIER         # 95
TRADING.SCORE.HIGH_CONFIDENCE  # 90
TRADING.SCORE.STRONG_SETUP     # 85
TRADING.SCORE.GOOD_SETUP       # 80
TRADING.SCORE.STANDARD         # 70

# Technical indicator weights
TRADING.TECHNICAL.WEIGHT_RSI       # 0.10
TRADING.TECHNICAL.WEIGHT_MACD      # 0.15
TRADING.TECHNICAL.WEIGHT_BOLLINGER # 0.10
TRADING.TECHNICAL.WEIGHT_MA        # 0.15
TRADING.TECHNICAL.WEIGHT_OBV       # 0.10
TRADING.TECHNICAL.WEIGHT_STOCH     # 0.10
TRADING.TECHNICAL.WEIGHT_VWAP      # 0.10
TRADING.TECHNICAL.WEIGHT_ATR       # 0.05
TRADING.TECHNICAL.WEIGHT_VOLUME    # 0.15
```

---

## Adding New Data Sources

To add a new intelligence source:

1. **Add method to EnhancedIntelStreams:**

```python
async def get_my_new_data(self, symbol: str) -> Dict:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.example.com/{symbol}") as resp:
                data = await resp.json()
                return {
                    "score": self._convert_to_score(data),
                    "confidence": 0.8,
                    "source": "my_new_source"
                }
    except Exception as e:
        return {"score": 50, "confidence": 0, "error": str(e)}
```

2. **Add to unified intel** in `get_unified_intel_score()`:

```python
async def get_unified_intel_score(self, symbol):
    # Existing sources...
    my_source = await self.get_my_new_data(symbol)

    # Include in calculation
    sources_working += 1
    total_sources += 1

    return {
        "unified_score": weighted_average,
        "sources_working": sources_working,
        "total_sources": total_sources,
        # ...
    }
```

---

## Debugging Tips

### Enable Verbose Logging

```bash
export DEBUG=true
export VERBOSE=true
./start_ibis.sh restart
```

### Inspect Specific Symbols

```python
python3 -c "
import asyncio
from ibis_true_agent import IBISTrueAgent

async def debug():
    agent = await IBISTrueAgent().initialize()
    intel = agent._calculate_enhanced_intel(
        agent.client.get_candles('FLOCK-USDT', '5min', 24),
        float((await agent.client.get_ticker('FLOCK-USDT')).price)
    )
    print(intel)

asyncio.run(debug())
```

### Check Position Logic

```python
python3 -c "
from ibis.data_consolidation import load_state
s = load_state()
for sym, pos in s.get('positions', {}).items():
    pnl = (pos['current_price'] - pos['buy_price']) / pos['buy_price']
    print(f'{sym}: entry={pos[\"buy_price\"]:.6f} current={pos[\"current_price\"]:.6f} pnl={pnl*100:.2f}%')
"
```

---

## Testing

### Unit Tests

```bash
python3 -m pytest tests/
```

### Paper Trading

Always test changes in paper mode first:

```bash
export PAPER_TRADING=true
./start_ibis.sh restart
```

### Manual Trade Testing

```python
python3 -c "
import asyncio
from ibis_true_agent import IBISTrueAgent

async def test():
    agent = await IBISTrueAgent().initialize()

    # Get an opportunity
    opp = {
        'symbol': 'BTC',
        'price': 50000,
        'score': 85,
        'volatility': 0.02
    }

    # Check if it would trade
    should_trade = opp['score'] >= 70
    print(f'Should trade: {should_trade}')

asyncio.run(test())
```

---

## Code Style

- Use async/await for all I/O
- Type hints for function signatures
- Log important events with `self.log_event()`
- Handle exceptions gracefully
- Add comments for complex logic
- Keep functions under 100 lines when possible

---

## Common Patterns

### Async Gathering

```python
# Fetch multiple things in parallel
results = await asyncio.gather(
    self.client.get_ticker(symbol1),
    self.client.get_ticker(symbol2),
    self.client.get_ticker(symbol3),
)
```

### Error Handling with Fallback

```python
async def get_data(symbol):
    try:
        return await primary_source(symbol)
    except Exception as e:
        self.log_event(f"   ⚠️ Primary failed: {e}")
        try:
            return await fallback_source(symbol)
        except:
            return {"score": 50, "confidence": 0}
```

### Rate Limiting

```python
semaphore = asyncio.Semaphore(5)

async def fetch_with_limit(symbol):
    async with semaphore:
        return await self.client.get_ticker(symbol)
```

---

## Performance

### Hot Paths

Most time spent on:
1. API calls to KuCoin
2. Indicator calculations
3. JSON serialization

### Optimization Tips

- Cache expensive calculations
- Use `asyncio.gather()` for parallel requests
- Limit candle history to what's needed
- Batch database writes

---

## Deployment

### Production Setup

```bash
# Run as systemd service
sudo cp deploy/ibis.service /etc/systemd/system/
sudo systemctl enable ibis
sudo systemctl start ibis

# Monitor
journalctl -u ibis -f
```

### Docker (Coming Soon)

```bash
docker build -t ibis .
docker run -d --name ibis ibis
```

---

## Version History

See [CHANGELOG.md](CHANGELOG.md) for full history.

---

## Getting Help

1. Read the code - it's well commented
2. Check existing patterns in the codebase
3. Search issues in the repo
4. Ask specific questions with:
   - What you tried
   - What you expected
   - What actually happened
   - Relevant log snippets

---

**Happy coding!** 🦅
