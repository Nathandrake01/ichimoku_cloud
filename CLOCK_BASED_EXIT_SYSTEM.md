# Clock-Based Exit System

## Date: November 14, 2025

## Overview

The trading bot now uses a **clock-based hourly candle system** for exit checks, ensuring positions are evaluated only when new hourly candles complete at exact clock times (00:00, 01:00, 02:00, etc.).

## How It Works

### Entry Signals (Every 5 Minutes)
- The bot scans for new entry signals **every 5 minutes**
- Can enter positions at any time when signals are detected
- Uses priority-based signal detection (fresh signals preferred)

### Exit Checks (Hourly Candle Close)
- Exit conditions are checked **ONLY when a new hourly candle completes**
- Clock-based timing: 00:00, 01:00, 02:00, 03:00, etc.
- Check occurs 2+ minutes after the hour to ensure candle data is available
- Tracks `last_exit_check_hour` to prevent duplicate checks

## Implementation Details

```python
# Track last hourly candle we checked for exits (clock-based)
last_exit_check_hour = None

# Check if a new hourly candle has completed
current_hour = current_time.replace(minute=0, second=0, microsecond=0)
is_new_hourly_candle = (
    last_exit_check_hour is None or 
    (current_hour > last_exit_check_hour and current_time.minute >= 2)
)

# Only check exits when new hourly candle completed
if is_new_hourly_candle and len(positions) > 0:
    # Check exit conditions for all positions
    # Update last_exit_check_hour = current_hour
```

## Exit Conditions

### For LONG Positions

**Stop Loss (Immediate Exit):**
- Price drops below Kijun-sen (Base Line)
- Two consecutive candles close inside the cloud

**Target/Take Profit:**
- Price closes below Tenkan-sen (Conversion Line)
- Tenkan-sen crosses below Kijun-sen (bearish crossover)

### For SHORT Positions

**Stop Loss (Immediate Exit):**
- Price rises above Kijun-sen (Base Line)
- Two consecutive candles close inside the cloud

**Target/Take Profit:**
- Price closes above Tenkan-sen (Conversion Line)
- Tenkan-sen crosses above Kijun-sen (bullish crossover)

## Example Timeline

```
04:00:00 - Hourly candle closes
04:02:00 - Bot checks exits (if scan cycle runs between 04:02-04:59)
04:05:00 - Bot scans for entries (5-min cycle)
04:10:00 - Bot scans for entries (5-min cycle)
04:15:00 - Bot scans for entries (5-min cycle)
...
04:55:00 - Bot scans for entries (5-min cycle)
05:00:00 - Hourly candle closes
05:02:00 - Bot checks exits (if scan cycle runs between 05:02-05:59)
05:03:00 - Bot scans for entries (5-min cycle)
```

## Key Benefits

1. **Accurate Timing**: Exits based on completed hourly candles, not arbitrary intervals
2. **No Missed Checks**: Will always check exits within the first hour after candle close
3. **Efficient**: Only checks exits once per hour, not every 5 minutes
4. **Predictable**: Exit checks happen at consistent clock times
5. **No False Signals**: Uses only completed candles, never forming candles

## Logging Examples

### When Exit Check Occurs:
```
📊 New hourly candle completed at 05:00 - Checking exit conditions...
✅ Closed position: XRP/USDT
📉 Closed 1 position(s)
```

### When Holding Between Checks:
```
⏳ Holding 3 position(s) - Next exit check at 06:00
```

### Entry Signal (Any Time):
```
🔍 Scanning for new trading signals...
📡 Found 2 signal(s)
✅ Opened long position: BTC/USDT
```

## Configuration

- **Scan Interval**: 300 seconds (5 minutes) for entry signals
- **Exit Check Window**: 2+ minutes after each hour (e.g., 00:02, 01:02, 02:02)
- **Timeframe**: 1-hour candles
- **Long Leverage**: 1.0x
- **Short Leverage**: 1.0x

## Files Modified

- `/home/ubuntu/ichimoku_cloud/backend/main.py`
  - Added `last_exit_check_hour` tracking
  - Implemented clock-based hourly candle detection
  - Separated entry scanning (5-min) from exit checking (hourly)

## Status

✅ Implemented and running
✅ Bot restarted with new logic
✅ Exit checks now properly aligned with hourly candle closes
✅ No more timing bugs or missed exit checks

