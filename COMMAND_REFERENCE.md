# Command Reference - Quick Lookup

## 🚀 Most Common Commands

```bash
./bot.sh start --background    # Start bot (production)
./bot.sh status                # Check if running
./bot.sh logs --follow         # Watch logs
./bot.sh restart --background  # Restart after changes
./bot.sh stop                  # Stop bot
```

---

## 📋 Complete Command List

### Start Commands

| Command | Description | Use Case |
|---------|-------------|----------|
| `./bot.sh start` | Start in foreground | Development |
| `./bot.sh start --background` | Start in background | Production |
| `./bot.sh --start` | Alias for start | Alternative syntax |
| `./bot.sh -s` | Short alias | Quick typing |

### Stop Commands

| Command | Description |
|---------|-------------|
| `./bot.sh stop` | Stop all processes |
| `./bot.sh --stop` | Alias for stop |
| `./bot.sh -x` | Short alias |

### Restart Commands

| Command | Description | Use Case |
|---------|-------------|----------|
| `./bot.sh restart` | Restart in foreground | Development |
| `./bot.sh restart --background` | Restart in background | Production |
| `./bot.sh --restart` | Alias for restart | Alternative syntax |
| `./bot.sh -r` | Short alias | Quick typing |

### Status Commands

| Command | Description |
|---------|-------------|
| `./bot.sh status` | Show detailed status |
| `./bot.sh --status` | Alias for status |
| `./bot.sh -i` | Short alias |

### Log Commands

| Command | Description | Use Case |
|---------|-------------|----------|
| `./bot.sh logs` | Show last 50 lines | Quick check |
| `./bot.sh logs --follow` | Stream logs live | Monitoring |
| `./bot.sh logs -f` | Short alias | Quick typing |
| `./bot.sh --logs` | Alias for logs | Alternative syntax |
| `./bot.sh -l` | Short alias | Quick typing |

### Help Commands

| Command | Description |
|---------|-------------|
| `./bot.sh help` | Show full help |
| `./bot.sh --help` | Alias for help |
| `./bot.sh -h` | Short alias |
| `./bot.sh` | Show help (no args) |

---

## 🎯 Command Cheat Sheet by Scenario

### First Time Setup
```bash
./install.sh
./configure_firewall.sh
./bot.sh start --background
./bot.sh status
```

### Daily Startup (Production)
```bash
./bot.sh start --background
./bot.sh logs --follow
# Ctrl+C to stop watching logs
```

### Daily Startup (Development)
```bash
./bot.sh start
# Watch output in terminal
# Ctrl+C to stop
```

### Check Status
```bash
./bot.sh status
```

### View Logs
```bash
# Quick check
./bot.sh logs

# Watch live
./bot.sh logs --follow
```

### After Code Changes
```bash
# Development
./bot.sh restart

# Production
./bot.sh restart --background
```

### Troubleshooting
```bash
# Check what's wrong
./bot.sh status
./bot.sh logs

# Force restart
./bot.sh restart --background
```

### Shutdown
```bash
./bot.sh stop
```

---

## 🔄 Workflow Examples

### Development Workflow
```bash
# Start
./bot.sh start

# Make changes in another terminal
# ...

# Restart to apply changes
./bot.sh restart

# Stop when done
./bot.sh stop
```

### Production Workflow
```bash
# Start
./bot.sh start --background

# Check status
./bot.sh status

# Monitor logs
./bot.sh logs --follow

# Update code
git pull

# Restart
./bot.sh restart --background

# Verify
./bot.sh status
```

### Debugging Workflow
```bash
# Check status
./bot.sh status

# View recent logs
./bot.sh logs

# Follow logs live
./bot.sh logs --follow

# Restart if needed
./bot.sh restart
```

---

## 🎨 Output Examples

### Status Output
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ichimoku Cloud Trading Bot Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Server Information:
  Private IP: 10.0.1.100
  Public IP:  203.0.113.50

Backend (Port 8000):
✓ Running (PID: 12345)
  URL: http://localhost:8000
  Docs: http://localhost:8000/docs

Frontend (Port 3000):
✓ Running (PID: 12346)
  URL: http://localhost:3000

Overall Status:
✓ Bot is running
```

### Start Output (Background)
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Starting Ichimoku Cloud Trading Bot (Background)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ Starting backend API server on port 8000...
ℹ Starting frontend server on port 3000...

✓ Bot started in background!

📊 Frontend Dashboard:
   Local:     http://localhost:3000
   Private:   http://10.0.1.100:3000
   Public:    http://203.0.113.50:3000

🔧 Backend API:
   Local:     http://localhost:8000
   Private:   http://10.0.1.100:8000
   Public:    http://203.0.113.50:8000

ℹ Backend PID: 12345 (saved to backend.pid)
ℹ Frontend PID: 12346 (saved to frontend.pid)

ℹ View logs: ./bot.sh logs
ℹ Stop bot: ./bot.sh stop
```

---

## 💡 Tips & Tricks

### Quick Status Check
```bash
./bot.sh status | grep "Overall Status"
```

### Watch Status Every 5 Seconds
```bash
watch -n 5 './bot.sh status'
```

### Start and Watch Logs
```bash
./bot.sh start --background && sleep 2 && ./bot.sh logs --follow
```

### Check if Running (Exit Code)
```bash
./bot.sh status > /dev/null 2>&1 && echo "Running" || echo "Not running"
```

### Save Logs to File
```bash
./bot.sh logs > bot_logs_$(date +%Y%m%d_%H%M%S).txt
```

---

## 🔗 Related Documentation

- **Full Guide**: `UNIFIED_SCRIPT_GUIDE.md`
- **Quick Start**: `QUICK_START.md`
- **Legacy Scripts**: `SCRIPTS_GUIDE.md`
- **Trading Logic**: `TRADING_LOGIC_FIX.md`
- **Main README**: `README.md`

---

## 📞 Quick Help

Forgot a command? Just run:
```bash
./bot.sh help
```

Or with no arguments:
```bash
./bot.sh
```

