# Trading Bot Timing Diagram

## Clock-Based Hourly Exit System

```
Hour Timeline (UTC):
═══════════════════════════════════════════════════════════════════════════

04:00:00 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         ┃ Hourly candle CLOSES
         ┃
04:02:00 ┃ ✅ EXIT CHECK (if scan runs between 04:02-04:59)
         ┃    - Check all open positions
         ┃    - Close if exit conditions met
         ┃    - Update last_exit_check_hour = 04:00
         ┃
04:05:00 ┃ 🔍 ENTRY SCAN (5-min cycle)
         ┃    - Scan for new signals
         ┃    - Open positions if signals found
         ┃
04:10:00 ┃ 🔍 ENTRY SCAN (5-min cycle)
         ┃
04:15:00 ┃ 🔍 ENTRY SCAN (5-min cycle)
         ┃
04:20:00 ┃ 🔍 ENTRY SCAN (5-min cycle)
         ┃
04:25:00 ┃ 🔍 ENTRY SCAN (5-min cycle)
         ┃
04:30:00 ┃ 🔍 ENTRY SCAN (5-min cycle)
         ┃
04:35:00 ┃ 🔍 ENTRY SCAN (5-min cycle)
         ┃
04:40:00 ┃ 🔍 ENTRY SCAN (5-min cycle)
         ┃
04:45:00 ┃ 🔍 ENTRY SCAN (5-min cycle)
         ┃
04:50:00 ┃ 🔍 ENTRY SCAN (5-min cycle)
         ┃
04:55:00 ┃ 🔍 ENTRY SCAN (5-min cycle)
         ┃
05:00:00 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         ┃ Hourly candle CLOSES
         ┃
05:02:00 ┃ ✅ EXIT CHECK (if scan runs between 05:02-05:59)
         ┃    - Check all open positions
         ┃    - Close if exit conditions met
         ┃    - Update last_exit_check_hour = 05:00
         ┃
05:03:00 ┃ 🔍 ENTRY SCAN (5-min cycle)
         ┃
         ⋮
```

## Key Points

### Entry Scans (🔍)
- **Frequency**: Every 5 minutes
- **Purpose**: Find new trading signals
- **Action**: Open positions when signals detected
- **Timing**: Can happen at any time

### Exit Checks (✅)
- **Frequency**: Once per hour (after candle close)
- **Purpose**: Evaluate open positions against exit conditions
- **Action**: Close positions when conditions met
- **Timing**: Only when new hourly candle completes (00:00, 01:00, 02:00, etc.)
- **Window**: 2+ minutes after the hour to ensure data availability

## Logic Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    MAIN TRADING LOOP                        │
│                  (Runs every 60 seconds)                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  Time for 5-min scan? │
                └───────────────────────┘
                        │       │
                       Yes      No
                        │       │
                        ▼       └──────────────────┐
            ┌──────────────────────┐               │
            │ New hourly candle?   │               │
            │ (clock-based check)  │               │
            └──────────────────────┘               │
                    │       │                      │
                   Yes      No                     │
                    │       │                      │
                    ▼       ▼                      ▼
        ┌─────────────┐  ┌──────────────┐  ┌──────────────┐
        │ EXIT CHECK  │  │ Skip exit    │  │ Update       │
        │ All Positions│  │ check        │  │ portfolio    │
        └─────────────┘  └──────────────┘  │ value only   │
                    │           │           └──────────────┘
                    └───────────┴──────────────┐
                                               │
                                               ▼
                                    ┌──────────────────┐
                                    │  ENTRY SCAN      │
                                    │  Find signals    │
                                    │  Open positions  │
                                    └──────────────────┘
                                               │
                                               ▼
                                    ┌──────────────────┐
                                    │ Update portfolio │
                                    │ Sleep 60 seconds │
                                    └──────────────────┘
                                               │
                                               └─────► Loop
```

## Example Scenario

### Scenario: Position opened at 04:15, exit signal appears at 04:30

```
04:00:00 - Hourly candle closes
04:12:00 - Entry scan runs, no signals
04:15:00 - Entry scan runs, LONG signal detected → Position opened
04:20:00 - Entry scan runs, position held
04:25:00 - Entry scan runs, position held
04:30:00 - Entry scan runs, position held (exit NOT checked yet)
04:35:00 - Entry scan runs, position held (exit NOT checked yet)
...
04:55:00 - Entry scan runs, position held (exit NOT checked yet)
05:00:00 - Hourly candle closes (exit signal now visible on completed candle)
05:03:00 - Entry scan runs, EXIT CHECK triggered → Position closed ✅
```

**Key Point**: Even though the exit signal appeared at 04:30, the position is held until the hourly candle completes at 05:00. This ensures we're trading on completed candles, not forming ones.

## Benefits of This Approach

1. **No False Signals**: Only uses completed hourly candles
2. **Predictable**: Exit checks at consistent times
3. **Efficient**: Doesn't waste resources checking exits every 5 minutes
4. **Accurate**: Aligns with Ichimoku's hourly timeframe strategy
5. **Reliable**: Never misses an exit check due to timing bugs

## Configuration

```python
scan_interval = 300  # 5 minutes (300 seconds)
exit_check_delay = 2  # Wait 2 minutes after hour for data availability
timeframe = "1h"      # Hourly candles
```

## Monitoring

Watch for these log messages:

### Exit Check Triggered:
```
📊 New hourly candle completed at 05:00 - Checking exit conditions...
✅ Closed position: XRP/USDT
📉 Closed 1 position(s)
```

### Holding Between Checks:
```
⏳ Holding 3 position(s) - Next exit check at 06:00
```

### Entry Scan:
```
🔍 Scanning for new trading signals...
📡 Found 2 signal(s)
✅ Opened short position: BTC/USDT
```

