# Ichimoku Cloud Trading Bot - ALL-IN Strategy

## Overview

This is the **ALL-IN Strategy** version of the Ichimoku Cloud Trading Bot. Unlike the balanced 50/50 long/short strategy, this version allocates positions based purely on signal strength, allowing for dynamic allocation across all opportunities.

## Key Differences from Standard Version

### Position Allocation
- **Standard**: 50% long / 50% short split (4 long + 4 short positions)
- **ALL-IN**: Top 10 strongest signals regardless of direction
  - Could be: 10 longs, 10 shorts, or any mix (e.g., 7 longs + 3 shorts)

### Position Sizing
- **Standard**: Variable sizing based on allocation splits
- **ALL-IN**: Fixed $1000 per position × leverage

### Signal Selection
- Ranks ALL signals by strength score
- Takes top 10 signals regardless of long/short ratio
- Strength score = (priority × 100) + hours_since_signal
  - Fresh signals (1h): Score 1-99
  - Recent signals (2-4h): Score 100-199
  - Older signals (5+h): Score 200+

## Configuration

### Ports
- **Backend API**: 8001 (vs 8000 in standard)
- **Frontend**: 3001 (vs 3000 in standard)

### Default Settings
```python
INITIAL_PORTFOLIO_VALUE: 10000.0  # $10,000
MAX_TOTAL_POSITIONS: 10           # 10 positions total
POSITION_SIZE: 1000.0             # $1000 per position
LONG_LEVERAGE: 1.0                # Can be increased for long bias
SHORT_LEVERAGE: 1.0               # Can be increased for short bias
```

### Adjusting Leverage

You can adjust leverage independently for longs and shorts via the API:

```bash
# Set long leverage to 2x (for bullish bias)
curl -X PUT http://localhost:8001/api/config \
  -H "Content-Type: application/json" \
  -d '{"long_leverage": 2.0}'

# Set short leverage to 3x (for bearish bias)
curl -X PUT http://localhost:8001/api/config \
  -H "Content-Type: application/json" \
  -d '{"short_leverage": 3.0}'
```

## Running the Bot

### Start
```bash
./start.sh
```

### Stop
```bash
./stop.sh
```

### Access
- **Dashboard**: http://YOUR_IP:3001
- **API Docs**: http://YOUR_IP:8001/docs

## Strategy Logic

### Entry Process
1. Scan all eligible symbols (long coins + top 50 shortable)
2. Calculate strength score for each signal
3. Sort by strength (lower = better)
4. Take top 10 signals
5. Open $1000 positions with appropriate leverage

### Example Scenarios

**Scenario 1: Strong Bullish Market**
- Top 10 signals: All long positions
- Result: 10 × $1000 × 1x leverage = $10,000 long exposure

**Scenario 2: Strong Bearish Market**
- Top 10 signals: All short positions
- Result: 10 × $1000 × 1x leverage = $10,000 short exposure

**Scenario 3: Mixed Market**
- Top 10 signals: 6 shorts + 4 longs
- Result: $6,000 short + $4,000 long exposure

**Scenario 4: Leveraged Long Bias**
- Long leverage: 2x, Short leverage: 1x
- Top 10 signals: 7 longs + 3 shorts
- Result: 
  - Longs: 7 × $1000 × 2x = $14,000 exposure
  - Shorts: 3 × $1000 × 1x = $3,000 exposure
  - Total: $17,000 exposure on $10,000 capital

### Exit Conditions
Same as standard version:
- Clock-based hourly candle checks (00:00, 01:00, 02:00, etc.)
- Stop loss: Price crosses Kijun-sen or 2 candles in cloud
- Target: Price crosses Tenkan-sen or Tenkan/Kijun crossover

## Advantages

1. **Flexibility**: Not constrained by 50/50 split
2. **Opportunity Maximization**: Takes best signals regardless of direction
3. **Market Adaptation**: Naturally aligns with market conditions
4. **Leverage Control**: Independent long/short leverage for bias expression
5. **Simplicity**: Fixed $1000 per position (easy to understand)

## Risks

1. **Directional Concentration**: Could be 100% long or 100% short
2. **No Built-in Hedging**: Unlike 50/50 split
3. **Leverage Amplification**: Higher leverage = higher risk
4. **Capital Efficiency**: Uses full capital when 10 positions filled

## Monitoring

Watch the dashboard for:
- **Position Distribution**: How many longs vs shorts
- **Strength Scores**: Quality of current signals
- **Leverage Impact**: How leverage affects P&L
- **Drawdown**: Especially important without hedging

## Files Modified

Key files different from standard version:
- `backend/config.py` - ALL-IN position limits and sizing
- `backend/trading_strategy.py` - Strength-based ranking
- `backend/main.py` - Port 8001, strength-based entry logic
- `frontend/index.html` - Port 3001, updated UI

## Comparison Table

| Feature | Standard (50/50) | ALL-IN |
|---------|------------------|--------|
| Max Positions | 4 long + 4 short | 10 total (any mix) |
| Position Size | Variable | Fixed $1000 |
| Allocation | 50% long / 50% short | Strength-based |
| Leverage | 1x long, 1x short | Adjustable per side |
| Backend Port | 8000 | 8001 |
| Frontend Port | 3000 | 3001 |
| Hedging | Built-in (50/50) | None (directional) |
| Capital Usage | Split allocation | Full allocation |

## Recommendations

1. **Start Conservative**: Use 1x leverage on both sides initially
2. **Monitor Closely**: Watch for directional concentration
3. **Adjust Leverage Carefully**: Small increases (1x → 1.5x → 2x)
4. **Set Alerts**: For high directional exposure (e.g., >80% one side)
5. **Compare Performance**: Run both versions to see which works better

## Support

Both versions can run simultaneously on the same server:
- Standard: http://YOUR_IP:3000 (backend: 8000)
- ALL-IN: http://YOUR_IP:3001 (backend: 8001)

This allows direct performance comparison!

