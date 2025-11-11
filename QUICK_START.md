# Quick Start Guide

## TL;DR - Get Running in 30 Seconds

```bash
# First time setup (run once)
./install.sh
./configure_firewall.sh

# Start the bot (foreground)
./bot.sh start

# OR start in background (keeps running after logout)
./bot.sh start --background
```

Access the dashboard at: **http://YOUR_IP:3000**

---

## Unified Management Script (Recommended)

```bash
./bot.sh start              # Start (keeps existing positions)
./bot.sh start --background # Start in background (keeps positions)
./bot.sh stop               # Stop (keeps trading data)
./bot.sh restart            # 🔄 FRESH START (clears everything!)
./bot.sh restart --background # Fresh start in background
./bot.sh status             # Check status
./bot.sh logs               # View logs
./bot.sh logs --follow      # Stream logs
./bot.sh help               # Show all commands
```

**Important:**
- `start` = Continue with existing positions
- `stop` = Pause (keeps your data)
- `restart` = **Fresh start** (clears all positions/data!)

---

## Legacy Scripts (Still Work)

```bash
./start.sh      # Start the bot
./stop.sh       # Stop the bot
./restart.sh    # Restart (kills ports if needed)
./status.sh     # Check if running
```

---

## After Code Changes

```bash
# If you want to keep positions
./bot.sh stop
# make changes
./bot.sh start --background

# If you want fresh start (clears everything)
./bot.sh restart --background
```

---

## Troubleshooting

### "Port already in use" error?
```bash
./bot.sh restart    # This will kill the port hoggers
```

### Bot not responding?
```bash
./bot.sh restart    # Clean restart
```

### Want to see what's running?
```bash
./bot.sh status
```

### Need to keep bot running after logout?
```bash
./bot.sh start --background
```

### Want to start completely fresh?
```bash
./bot.sh restart --background  # Clears ALL positions and data
```

---

## What's Running?

- **Backend API**: Port 8000 (FastAPI server)
- **Frontend Dashboard**: Port 3000 (Web interface)
- **Trading Loop**: Checks every 5 minutes, trades on hourly candle closes

---

## Important Files

- `positions.json` - Current positions (auto-saved)
- `equity_history.json` - Equity curve data
- `backend.log` - Backend logs
- `frontend.log` - Frontend logs

---

## Need More Help?

- Full documentation: `README.md`
- Script details: `SCRIPTS_GUIDE.md`
- Trading logic fix: `TRADING_LOGIC_FIX.md`

