# New Command Logic - Simplified & Intuitive

## 🎯 The New Way (Much Better!)

### Commands Overview

| Command | What It Does | Trading Data | Logs | Ports |
|---------|-------------|--------------|------|-------|
| `./bot.sh start` | Start bot | ✅ **Keeps** | Creates new | Uses existing |
| `./bot.sh stop` | Stop bot | ✅ **Keeps** | Clears | Frees |
| `./bot.sh restart` | **Fresh start** | ❌ **Clears ALL** | Clears | Frees |

---

## 📖 Detailed Behavior

### `./bot.sh start` - Normal Start
**Keeps everything, continues where you left off**

```bash
./bot.sh start              # Foreground
./bot.sh start --background # Background
```

**What it does:**
- ✅ Loads existing positions from `positions.json`
- ✅ Continues with your current P&L
- ✅ Resumes trading with existing positions
- ✅ Keeps equity history

**Use when:**
- Restarting after a server reboot
- Continuing trading after a stop
- You want to keep your positions and P&L

---

### `./bot.sh stop` - Clean Stop
**Stops bot but preserves your trading data**

```bash
./bot.sh stop
```

**What it does:**
- ✅ Stops all bot processes
- ✅ Frees ports 8000 and 3000
- ✅ Clears log files
- ✅ **KEEPS** positions.json
- ✅ **KEEPS** equity_history.json

**Use when:**
- Taking a break from trading
- Doing maintenance
- Shutting down temporarily
- You want to resume later with same positions

---

### `./bot.sh restart` - Fresh Start 🔄
**Clears EVERYTHING and starts from scratch**

```bash
./bot.sh restart              # Foreground
./bot.sh restart --background # Background
```

**What it does:**
- ❌ **DELETES** all positions
- ❌ **DELETES** all trade history
- ❌ **DELETES** equity curve data
- ❌ **CLEARS** all logs
- ✅ Frees all ports
- ✅ Starts bot with clean slate
- ✅ Resets P&L to $0
- ✅ Portfolio value resets to config value

**Use when:**
- You want to start completely fresh
- Testing new strategy changes
- Clearing out old test trades
- Starting a new trading period
- You made a mistake and want to reset

---

## 🎬 Real-World Scenarios

### Scenario 1: Daily Trading
```bash
# Morning - start trading
./bot.sh start --background

# Evening - stop for the day (keeps positions)
./bot.sh stop

# Next morning - resume with same positions
./bot.sh start --background
```

### Scenario 2: Fresh Start
```bash
# I want to start completely fresh
./bot.sh restart --background

# Everything cleared, starting from $0 P&L
```

### Scenario 3: After Code Changes
```bash
# If you want to keep positions
./bot.sh stop
# make code changes
./bot.sh start --background

# If you want fresh start
./bot.sh restart --background
```

### Scenario 4: Testing
```bash
# Test run
./bot.sh start --background

# Made mistakes, want to reset
./bot.sh restart --background

# Clean slate, test again
```

---

## 🔍 What Gets Cleared

### `stop` command clears:
- ✅ Log files (backend.log, frontend.log)
- ✅ PID files (backend.pid, frontend.pid)
- ❌ Does NOT clear positions or equity history

### `restart` command clears:
- ✅ **positions.json** (all positions and trade history)
- ✅ **equity_history.json** (equity curve data)
- ✅ Log files (backend.log, frontend.log)
- ✅ PID files (backend.pid, frontend.pid)
- ✅ Everything!

---

## 💡 Quick Reference

```bash
# Continue trading (keeps positions)
./bot.sh start --background

# Stop for now (keeps positions for later)
./bot.sh stop

# Start completely fresh (clears everything)
./bot.sh restart --background

# Check what's running
./bot.sh status

# Watch logs
./bot.sh logs --follow
```

---

## ⚠️ Important Notes

### Before Using `restart`:
- **All positions will be closed and deleted**
- **All trade history will be lost**
- **Equity curve will be reset**
- **P&L will reset to $0**
- **Cannot be undone!**

### If You Want to Keep Data:
Use `stop` then `start` instead of `restart`:
```bash
./bot.sh stop
# make changes
./bot.sh start --background
```

---

## 🆚 Old vs New Behavior

### OLD Way (Confusing):
- `restart` = just restart (kept data)
- Had to manually delete files
- Unclear what gets cleared

### NEW Way (Clear):
- `start` = continue trading (keeps data)
- `stop` = pause trading (keeps data)
- `restart` = fresh start (clears everything)

---

## 📝 Summary

**Think of it this way:**

- 🟢 **start** = "Continue where I left off"
- 🔴 **stop** = "Pause, I'll be back"
- 🔄 **restart** = "Reset everything, fresh start"

Simple, intuitive, and does what you expect!

