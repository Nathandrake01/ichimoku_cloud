# Leverage Control Guide - ALL-IN Strategy

## Overview

The ALL-IN strategy supports **independent leverage control** for long and short positions, allowing you to express directional bias while maintaining the strength-based allocation system.

## Frontend Controls

Access the dashboard at: http://YOUR_IP:3001

In the **Configuration** section on the right sidebar, you'll find:

```
Portfolio Value ($): [10000.00]
Long Leverage (x):   [1.0]  ← Adjust this for long positions
Short Leverage (x):  [1.0]  ← Adjust this for short positions
[Update Config]
```

### How to Adjust

1. Enter desired leverage (1.0 to 10.0)
2. Click "Update Config"
3. New positions will use the updated leverage
4. Existing positions keep their original leverage

## API Control

### View Current Settings
```bash
curl http://localhost:8001/api/config | python3 -m json.tool
```

### Update Long Leverage
```bash
curl -X PUT http://localhost:8001/api/config \
  -H "Content-Type: application/json" \
  -d '{"long_leverage": 2.0}'
```

### Update Short Leverage
```bash
curl -X PUT http://localhost:8001/api/config \
  -H "Content-Type: application/json" \
  -d '{"short_leverage": 2.5}'
```

### Update Both at Once
```bash
curl -X PUT http://localhost:8001/api/config \
  -H "Content-Type: application/json" \
  -d '{"long_leverage": 2.0, "short_leverage": 3.0}'
```

## Strategy Examples

### Example 1: Neutral (Default)
**Settings:**
- Long Leverage: 1.0x
- Short Leverage: 1.0x

**Result:**
- 10 positions × $1000 = $10,000 exposure
- Equal treatment of long and short signals

### Example 2: Bullish Bias
**Settings:**
- Long Leverage: 2.0x
- Short Leverage: 1.0x

**Scenario:** 7 longs + 3 shorts selected by strength
**Result:**
- Longs: 7 × $1000 × 2.0 = $14,000 exposure
- Shorts: 3 × $1000 × 1.0 = $3,000 exposure
- Total: $17,000 exposure on $10,000 capital

### Example 3: Bearish Bias
**Settings:**
- Long Leverage: 1.0x
- Short Leverage: 2.5x

**Scenario:** 3 longs + 7 shorts selected by strength
**Result:**
- Longs: 3 × $1000 × 1.0 = $3,000 exposure
- Shorts: 7 × $1000 × 2.5 = $17,500 exposure
- Total: $20,500 exposure on $10,000 capital

### Example 4: Maximum Aggression
**Settings:**
- Long Leverage: 3.0x
- Short Leverage: 3.0x

**Scenario:** Any 10 positions
**Result:**
- 10 × $1000 × 3.0 = $30,000 exposure
- Total: $30,000 exposure on $10,000 capital
- ⚠️ High risk!

## Position Calculation

### Formula
```
Position Exposure = Position Size × Leverage
Margin Used = Position Size / Leverage
Quantity = (Position Size × Leverage) / Entry Price
```

### Example: BTC Long at $98,000
**With 1x Leverage:**
- Position Size: $1,000
- Leverage: 1.0x
- Exposure: $1,000
- Margin Used: $1,000
- Quantity: 0.0102 BTC

**With 2x Leverage:**
- Position Size: $1,000
- Leverage: 2.0x
- Exposure: $2,000
- Margin Used: $1,000
- Quantity: 0.0204 BTC

**With 3x Leverage:**
- Position Size: $1,000
- Leverage: 3.0x
- Exposure: $3,000
- Margin Used: $1,000
- Quantity: 0.0306 BTC

## Risk Management

### Conservative (1.0x - 1.5x)
- Lower risk
- Slower gains/losses
- Good for learning
- Recommended starting point

### Moderate (1.5x - 2.5x)
- Balanced risk/reward
- Noticeable leverage impact
- Requires monitoring
- Good for experienced traders

### Aggressive (2.5x - 5.0x)
- High risk
- Significant gains/losses
- Requires active monitoring
- Only for confident traders

### Extreme (5.0x - 10.0x)
- Very high risk
- Can lead to rapid losses
- Requires constant monitoring
- Only for very experienced traders
- ⚠️ Not recommended for most users

## Important Notes

1. **Existing Positions**: Leverage changes only affect NEW positions
2. **Margin Requirements**: Higher leverage = same margin but more exposure
3. **P&L Impact**: Leverage multiplies both gains AND losses
4. **Liquidation Risk**: Higher leverage = closer to liquidation (in real trading)
5. **Paper Trading**: Currently in paper trading mode, so safe to experiment

## Monitoring Leverage Impact

### Check Current Exposure
```bash
curl -s http://localhost:8001/api/portfolio | python3 -m json.tool
```

### View Position Details
```bash
curl -s http://localhost:8001/api/positions | python3 -m json.tool
```

Each position shows:
- `leverage`: The leverage used for that position
- `quantity`: Affected by leverage
- `pnl`: Multiplied by leverage

## Best Practices

1. **Start Low**: Begin with 1.0x on both sides
2. **Increase Gradually**: Move in 0.5x increments
3. **Monitor Closely**: Watch P&L changes with leverage
4. **Set Limits**: Don't exceed your risk tolerance
5. **Adjust Based on Market**: 
   - Bullish? Increase long leverage
   - Bearish? Increase short leverage
   - Uncertain? Keep both at 1.0x
6. **Compare Results**: Run standard (50/50) vs ALL-IN to see differences

## Troubleshooting

### Leverage Not Updating
- Refresh the page
- Check API response
- Verify backend is running: `curl http://localhost:8001/api/health`

### Positions Not Using New Leverage
- Leverage only affects NEW positions
- Close existing positions for them to re-enter with new leverage
- Or wait for exit conditions to trigger

### Unexpected Exposure
- Check both long and short leverage settings
- Review position distribution (how many longs vs shorts)
- Calculate: Total Exposure = Σ(Position Size × Leverage)

## Example Workflow

### Setting Bullish Bias
```bash
# 1. Check current config
curl -s http://localhost:8001/api/config | python3 -m json.tool

# 2. Increase long leverage
curl -X PUT http://localhost:8001/api/config \
  -H "Content-Type: application/json" \
  -d '{"long_leverage": 2.0}'

# 3. Verify change
curl -s http://localhost:8001/api/config | python3 -m json.tool

# 4. Monitor positions
curl -s http://localhost:8001/api/positions | python3 -m json.tool

# 5. Check P&L impact
curl -s http://localhost:8001/api/portfolio | python3 -m json.tool
```

## Support

For questions or issues:
- Check dashboard: http://YOUR_IP:3001
- View logs: `tail -f /tmp/allin_startup.log`
- Check API health: `curl http://localhost:8001/api/health`

---

**Remember**: Leverage amplifies both gains AND losses. Start conservative and increase gradually as you gain confidence!

