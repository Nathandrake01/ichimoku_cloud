# Unified Bot Management Script Guide

## Overview

The `bot.sh` script is a **unified management tool** that handles all bot operations through a single command interface.

## Quick Start

```bash
# Start bot (foreground)
./bot.sh start

# Start bot (background - keeps running after logout)
./bot.sh start --background

# Stop bot
./bot.sh stop

# Restart bot
./bot.sh restart

# Check status
./bot.sh status

# View logs
./bot.sh logs
```

---

## All Commands

### 🚀 Start Commands

#### Start in Foreground (Default)
```bash
./bot.sh start
# OR
./bot.sh --start
./bot.sh -s
```
**Use when:**
- Development/debugging
- You want to see real-time output
- You'll keep the terminal open

**Behavior:**
- Runs in current terminal
- Shows live output
- Press Ctrl+C to stop
- Stops when you close terminal/SSH

#### Start in Background
```bash
./bot.sh start --background
# OR
./bot.sh start -b
```
**Use when:**
- Production deployment
- You want to close terminal/SSH
- Running on a server 24/7

**Behavior:**
- Runs detached from terminal
- Outputs to log files
- Keeps running after logout
- Survives terminal close

---

### 🛑 Stop Command

```bash
./bot.sh stop
# OR
./bot.sh --stop
./bot.sh -x
```

**What it does:**
- Gracefully stops backend and frontend
- Kills processes on ports 8000 and 3000
- Cleans up PID files
- Uses SIGTERM first, then SIGKILL if needed

---

### 🔄 Restart Commands

#### Restart in Foreground
```bash
./bot.sh restart
# OR
./bot.sh --restart
./bot.sh -r
```

#### Restart in Background
```bash
./bot.sh restart --background
# OR
./bot.sh restart -b
```

**What it does:**
1. Stops all bot processes
2. Kills any processes hogging ports
3. Starts bot fresh (foreground or background)

**Use when:**
- After code changes
- Port conflicts ("port already in use")
- Bot is unresponsive
- Need a clean slate

---

### 📊 Status Command

```bash
./bot.sh status
# OR
./bot.sh --status
./bot.sh -i
```

**Shows:**
- Server IP addresses (private & public)
- Backend status and PID
- Frontend status and PID
- Port availability
- PID file locations
- Log file sizes
- Overall bot status

**Example output:**
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

---

### 📝 Logs Commands

#### View Recent Logs
```bash
./bot.sh logs
# OR
./bot.sh --logs
./bot.sh -l
```
Shows last 50 lines from both backend and frontend logs.

#### Follow Logs in Real-Time
```bash
./bot.sh logs --follow
# OR
./bot.sh logs -f
```
Continuously streams logs (like `tail -f`). Press Ctrl+C to stop.

**Note:** Logs are only available when running in background mode.

---

### ❓ Help Command

```bash
./bot.sh help
# OR
./bot.sh --help
./bot.sh -h
./bot.sh
```
Shows complete usage guide with all commands and examples.

---

## Common Workflows

### Development Workflow
```bash
# Start in foreground to see output
./bot.sh start

# Make code changes (in another terminal)
# ...

# Restart to apply changes
./bot.sh restart
```

### Production Workflow
```bash
# Start in background
./bot.sh start --background

# Check if running
./bot.sh status

# View logs
./bot.sh logs

# Follow logs
./bot.sh logs --follow

# Restart after updates
./bot.sh restart --background
```

### Troubleshooting Workflow
```bash
# Check status
./bot.sh status

# View recent logs
./bot.sh logs

# Force restart (clears port conflicts)
./bot.sh restart

# Or restart in background
./bot.sh restart --background
```

---

## Comparison: Foreground vs Background

| Feature | Foreground | Background |
|---------|-----------|------------|
| **Output** | Terminal | Log files |
| **Survives logout** | ❌ No | ✅ Yes |
| **Use case** | Development | Production |
| **Stop method** | Ctrl+C | `./bot.sh stop` |
| **View logs** | Terminal | `./bot.sh logs` |
| **Best for** | Debugging | 24/7 operation |

---

## File Locations

When running in background mode:

- **Backend log**: `backend.log`
- **Frontend log**: `frontend.log`
- **Backend PID**: `backend.pid`
- **Frontend PID**: `frontend.pid`

---

## Command Aliases

All commands support multiple formats:

| Command | Aliases |
|---------|---------|
| `start` | `--start`, `-s` |
| `stop` | `--stop`, `-x` |
| `restart` | `--restart`, `-r` |
| `status` | `--status`, `-i` |
| `logs` | `--logs`, `-l` |
| `help` | `--help`, `-h` |

**Examples:**
```bash
./bot.sh start
./bot.sh --start
./bot.sh -s
# All do the same thing!
```

---

## Advanced Usage

### Start in Background with Immediate Log View
```bash
./bot.sh start --background && ./bot.sh logs --follow
```

### Check Status Every 5 Seconds
```bash
watch -n 5 './bot.sh status'
```

### Restart and Follow Logs
```bash
./bot.sh restart --background && sleep 2 && ./bot.sh logs --follow
```

### Quick Status Check
```bash
./bot.sh status | grep "Overall Status"
```

---

## Error Handling

### "Port already in use"
```bash
./bot.sh restart
# This will force-kill the port hoggers
```

### "Bot not responding"
```bash
./bot.sh stop
./bot.sh start --background
```

### "Can't see logs"
Logs are only created in background mode:
```bash
./bot.sh restart --background
./bot.sh logs
```

---

## Tips & Best Practices

### ✅ DO
- Use `--background` for production/server deployments
- Use foreground mode for development
- Check status regularly: `./bot.sh status`
- View logs when troubleshooting: `./bot.sh logs`
- Use `restart` when applying code changes

### ❌ DON'T
- Don't run multiple instances simultaneously
- Don't manually kill processes (use `./bot.sh stop`)
- Don't forget to restart after code changes
- Don't use foreground mode on production servers

---

## Migration from Old Scripts

If you were using the old scripts, here's the mapping:

| Old Script | New Command |
|-----------|-------------|
| `./start.sh` | `./bot.sh start` |
| `./stop.sh` | `./bot.sh stop` |
| `./restart.sh` | `./bot.sh restart` |
| `./status.sh` | `./bot.sh status` |
| `nohup ./start.sh &` | `./bot.sh start --background` |

**The old scripts still work**, but `bot.sh` is recommended for its unified interface.

---

## Quick Reference Card

```bash
# Start
./bot.sh start              # Foreground
./bot.sh start --background # Background (recommended for servers)

# Stop
./bot.sh stop               # Stop everything

# Restart
./bot.sh restart            # Restart (foreground)
./bot.sh restart --background # Restart (background)

# Monitor
./bot.sh status             # Check status
./bot.sh logs               # View logs
./bot.sh logs --follow      # Stream logs

# Help
./bot.sh help               # Show help
```

---

## Support

For more information:
- Full documentation: `README.md`
- Individual scripts: `SCRIPTS_GUIDE.md`
- Quick start: `QUICK_START.md`
- Trading logic: `TRADING_LOGIC_FIX.md`

