# Trading Logic Fix - Hourly Candle Close Only

## Problem Identified

The bot was executing multiple trades on the same symbol within the same hour because:

1. **Entry signals** were being evaluated on the **currently forming candle** (incomplete hourly candle)
2. **Exit conditions** were also checking the **currently forming candle**
3. The 5-minute polling loop would repeatedly see the same signal on the incomplete candle
4. After closing a position, the same signal would trigger again within minutes

This resulted in rapid open/close cycles like:
- HYPE/USD short @ 03:10
- HYPE/USD short @ 03:15
- HYPE/USD short @ 03:16
- HYPE/USD short @ 03:22
- HYPE/USD short @ 03:27

All within the same hour!

## Solution Implemented

### 1. Trading Loop Only Acts on Hourly Boundaries

The main trading loop now:
- Checks every minute (not every 5 minutes)
- Only executes trades when a new hour starts (at least 2 minutes past the hour)
- Tracks the last hour it acted on to prevent duplicates
- Waits for the next hourly candle close before acting again

### 2. Filter Out Incomplete Candles

Both `check_signal()` and `check_exit_conditions()` now:
- Fetch the latest OHLCV data
- Check if the last candle's timestamp falls within the current clock hour
- If yes, **exclude it** from analysis (use `df.iloc[:-1]`)
- Only evaluate signals/exits on **completed hourly candles**

```python
# Check if the last candle is aligned to clock hour
last_timestamp = df.index[-1]
current_time = datetime.now()

# If last candle's timestamp is within the current hour, it's still forming - exclude it
if last_timestamp.hour == current_time.hour and last_timestamp.date() == current_time.date():
    df = df.iloc[:-1]  # Exclude the forming candle
```

### 3. Track Last Action Per Symbol

Added `self.last_action_timestamp: Dict[str, datetime]` to track when we last acted on each symbol.

**In `open_position()`:**
- Before opening, check if we already acted on this symbol in the current clock hour
- Compare the last action timestamp (normalized to hour) with the last completed candle timestamp
- Skip if we already acted on the same candle
- Record timestamp after successful entry

**In `close_position()`:**
- Record timestamp after closing to prevent immediate re-entry on the same candle

### 4. Main Loop Hour Tracking

The trading loop tracks `last_action_hour` to ensure:
- Only one trading cycle per clock hour
- Waits at least 2 minutes into each hour (ensures candle data is available)
- Checks every minute but only acts once per hour

### 5. Behavior Now

- **Entry**: Only triggered when a new clock hour begins (at least 2 minutes past the hour)
- **Exit**: Only triggered when a new clock hour begins
- **Loop frequency**: Checks every minute, but only acts once per hour
- **No duplicates**: Cannot enter/exit multiple times within the same clock hour
- **Hourly alignment**: All trading decisions happen at HH:02 (e.g., 01:02, 02:02, 03:02)
- **Candle-based**: Only evaluates completed hourly candles (excludes forming candle)

## Expected Results

- Maximum **1 entry** per symbol per clock hour (00:00, 01:00, 02:00, etc.)
- Maximum **1 exit** per symbol per clock hour
- No more rapid-fire trades within the same hour
- Trades align with completed hourly candle closes

## Files Modified

- `backend/main.py`
  - **Modified `trading_loop()` to only act on hourly boundaries**
  - Added `last_action_hour` tracking
  - Changed loop frequency from 5 minutes to 1 minute
  - Only executes trades at HH:02 (2 minutes past each hour)

- `backend/trading_strategy.py`
  - Modified `check_signal()` to exclude forming candles
  - Modified `check_exit_conditions()` to exclude forming candles
  - Added `last_action_timestamp` tracking dictionary
  - Modified `open_position()` to check for duplicate actions
  - Modified `close_position()` to record action timestamp

## Testing Recommendations

1. Monitor the logs for "Already acted on {symbol} for candle..." messages
2. Verify trades only happen at or shortly after clock hour boundaries
3. Confirm no duplicate entries/exits within the same hour
4. Check that the 5-minute loop continues to run but only acts on new completed candles

