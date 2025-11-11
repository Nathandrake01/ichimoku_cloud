# Priority-Based Signal System

## 🎯 The Problem with Pure Transition Detection

The strict transition detection (only entering on False→True) was **too restrictive**:
- If bot starts and all signals are 2+ hours old, it enters nothing
- Slots remain empty even when good opportunities exist
- Misses profitable trades waiting for "perfect" fresh signals

## ✅ The Solution: Priority-Based Entry System

Enter signals based on **priority ranking**:

### Priority Levels

**Priority 0: 🆕 FRESH (1 hour old)**
- Signal just appeared in the last hour
- Best entry quality
- Preferred entries

**Priority 1: ⏰ RECENT (2-4 hours old)**
- Signal appeared 2-4 hours ago
- Good entry quality
- Acceptable if no fresh signals

**Priority 2: ⏳ OLDER (5+ hours old)**
- Signal appeared 5+ hours ago
- Acceptable entry quality
- Used to fill remaining slots

---

## 📊 How It Works

### Scanning Process

1. **Scan all eligible symbols** (15 long coins + 50 short candidates)
2. **Calculate priority** for each signal
3. **Sort by priority** (fresh first, then by recency)
4. **Enter positions** starting from highest priority

### Example Scan Result

```
📊 Signal Priority Ranking:
  1. BTC/USDT: 🆕 FRESH (1h ago) - LONG
  2. ETH/USDT: 🆕 FRESH (1h ago) - LONG
  3. SOL/USDT: ⏰ RECENT (3h ago) - LONG
  4. LINK/USDT: ⏰ RECENT (4h ago) - LONG
  5. HYPE/USDT: ⏳ OLDER (6h ago) - LONG
  6. ZEC/USDT: ⏳ OLDER (8h ago) - SHORT
  7. NEAR/USDT: ⏳ OLDER (10h ago) - SHORT
```

**Bot enters in this order:**
1. BTC (fresh)
2. ETH (fresh)
3. SOL (recent)
4. LINK (recent)

If only 4 slots available, stops here. If more slots, continues with older signals.

---

## 🎯 Entry Logic

### When Fresh Signals Available
```
Scan finds:
- BTC: 1h old (fresh)
- ETH: 1h old (fresh)
- SOL: 6h old (older)

Bot enters:
1. BTC ✅ (fresh - best)
2. ETH ✅ (fresh - best)
3. SOL ✅ (older - acceptable, fills slot)
```

### When No Fresh Signals
```
Scan finds:
- LINK: 4h old (recent)
- HYPE: 6h old (older)
- NEAR: 8h old (older)

Bot enters:
1. LINK ✅ (recent - most recent)
2. HYPE ✅ (older - next best)
3. NEAR ✅ (older - fills slot)
```

### Comparison: Two Cryptos
```
Crypto 1: Signal appeared 4h ago
Crypto 2: Signal appeared 6h ago

Bot chooses: Crypto 1 ✅ (more recent)
```

---

## 📈 Expanded Long Coins (15 Total)

### Old List (4 coins)
- HYPE, BNB, SOL, LINK

### New List (15 coins)
- BTC, ETH, BNB, SOL, XRP
- ADA, AVAX, DOT, MATIC, LINK
- UNI, ATOM, LTC, NEAR, HYPE

**Benefits:**
- More opportunities
- Better diversification
- Top market cap coins
- Still manageable (max 4 positions)

---

## 🔍 Real-World Examples

### Example 1: Mixed Priorities

**Scan at 08:02:**
```
Available signals:
- BTC: 1h old (fresh) → Priority 0
- ETH: 3h old (recent) → Priority 1
- SOL: 6h old (older) → Priority 2
- LINK: 8h old (older) → Priority 2

Open slots: 4 long positions

Bot enters:
1. BTC (priority 0, 1h) ✅
2. ETH (priority 1, 3h) ✅
3. SOL (priority 2, 6h) ✅ (more recent than LINK)
4. LINK (priority 2, 8h) ✅ (fills last slot)
```

### Example 2: After Exit

**ZEC exits at 09:02, freeing 1 slot:**
```
Scan finds:
- NEAR: 2h old (recent)
- HYPE: 5h old (older)
- ICP: 10h old (older)

Bot enters:
1. NEAR ✅ (most recent at 2h)

Skips HYPE and ICP (less recent)
```

### Example 3: Bot Startup

**Bot starts at 10:30, first scan at 11:32:**
```
All signals are old:
- BTC: 8h old
- ETH: 6h old
- SOL: 10h old
- LINK: 4h old

Bot enters by recency:
1. LINK ✅ (4h - most recent)
2. ETH ✅ (6h - next)
3. BTC ✅ (8h - next)
4. SOL ✅ (10h - fills slot)
```

**Result:** Slots filled with best available signals, not left empty.

---

## 📊 Priority Calculation

### How "Hours Since Signal" is Calculated

```python
# Look back through candles to find when signal first appeared
hours_since_signal = 0

for i in range(len(df) - 1, -1, -1):
    if signal_present:
        hours_since_signal += 1
    else:
        break  # Found where signal started
```

### Example Timeline
```
Hour 02:00 - signal: False
Hour 03:00 - signal: False
Hour 04:00 - signal: True  ← Signal first appeared
Hour 05:00 - signal: True
Hour 06:00 - signal: True
Hour 07:00 - signal: True  ← Current time

Hours since signal: 4 (from 04:00 to 07:00)
Priority: 1 (Recent, 2-4 hours)
```

---

## 🎯 Advantages Over Pure Transition

### Pure Transition (Old - Too Restrictive)
```
Scan at 08:02:
- All signals are 2+ hours old
- No fresh transitions
- Result: Enter nothing ❌
- Slots remain empty ❌
```

### Priority System (New - Balanced)
```
Scan at 08:02:
- All signals are 2+ hours old
- No fresh signals, but have recent ones
- Result: Enter most recent signals ✅
- Slots filled intelligently ✅
```

---

## 📝 Log Examples

### Fresh Signals Available
```
⏰ [08:02:00] New hourly candle closed - Running trading cycle...
🔍 Scanning for new trading signals...

📊 Signal Priority Ranking:
  1. BTC/USDT: 🆕 FRESH (1h ago) - LONG
  2. ETH/USDT: 🆕 FRESH (1h ago) - LONG
  3. SOL/USDT: ⏰ RECENT (3h ago) - LONG
  4. LINK/USDT: ⏰ RECENT (4h ago) - LONG

✅ Opened long position: BTC/USDT
✅ Opened long position: ETH/USDT
✅ Opened long position: SOL/USDT
✅ Opened long position: LINK/USDT
📈 Opened 4 new position(s)
```

### No Fresh Signals (Uses Recent)
```
⏰ [09:02:00] New hourly candle closed - Running trading cycle...
🔍 Scanning for new trading signals...

📊 Signal Priority Ranking:
  1. HYPE/USDT: ⏰ RECENT (3h ago) - LONG
  2. NEAR/USDT: ⏰ RECENT (4h ago) - SHORT
  3. ZEC/USDT: ⏳ OLDER (6h ago) - SHORT

✅ Opened long position: HYPE/USDT
✅ Opened short position: NEAR/USDT
✅ Opened short position: ZEC/USDT
📈 Opened 3 new position(s)
```

---

## ⚖️ Balance: Quality vs Opportunity

### Too Strict (Pure Transition)
- ✅ Best entry quality
- ❌ Misses many opportunities
- ❌ Slots often empty
- ❌ Underutilized capital

### Too Loose (No Filtering)
- ❌ Poor entry quality
- ✅ Never misses opportunities
- ✅ Slots always filled
- ❌ Late entries, bad prices

### Priority System (Balanced) ✅
- ✅ Good entry quality (prioritizes fresh)
- ✅ Captures opportunities (uses recent if needed)
- ✅ Slots intelligently filled
- ✅ Capital efficiently used

---

## 🎯 Summary

**Old System:**
- Only entered on fresh signals (1h old)
- Too restrictive
- Missed opportunities

**New System:**
- Prioritizes fresh signals (1h)
- Falls back to recent signals (2-4h)
- Uses older signals to fill slots (5+h)
- Expanded to 15 long coins
- Balanced approach

**Result:**
- Best signals entered first ✅
- Slots filled intelligently ✅
- More opportunities ✅
- Better capital utilization ✅

---

## 📚 Configuration

**Long Coins (15):**
```python
LONG_COINS = [
    "BTC", "ETH", "BNB", "SOL", "XRP", 
    "ADA", "AVAX", "DOT", "MATIC", "LINK",
    "UNI", "ATOM", "LTC", "NEAR", "HYPE"
]
```

**Priority Thresholds:**
- Fresh: 1 hour
- Recent: 2-4 hours
- Older: 5+ hours

**Position Limits:**
- Max long: 4 positions
- Max short: 4 positions

