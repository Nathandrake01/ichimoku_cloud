# Scripts Guide

Quick reference for all available scripts in the Ichimoku Cloud Trading Bot.

## Management Scripts

### 🚀 start.sh - Start the Bot
```bash
./start.sh
```
**What it does:**
- Checks if ports 8000 and 3000 are available
- Starts backend API server (port 8000)
- Starts frontend dashboard (port 3000)
- Displays access URLs (local, private, public)
- Runs in foreground (Ctrl+C to stop)

**When to use:**
- First time starting the bot
- After stopping with `stop.sh`
- When ports are confirmed to be free

---

### 🛑 stop.sh - Stop the Bot
```bash
./stop.sh
```
**What it does:**
- Finds all bot-related processes
- Gracefully stops backend (SIGTERM first)
- Gracefully stops frontend (SIGTERM first)
- Force kills if graceful shutdown fails (SIGKILL)
- Frees ports 8000 and 3000

**When to use:**
- Gracefully shutting down the bot
- Before making code changes
- Before system maintenance
- When you're done trading for the day

---

### 🔄 restart.sh - Restart the Bot
```bash
./restart.sh
```
**What it does:**
1. **Stop Phase:**
   - Kills all bot-related Python processes
   - Kills any process using port 8000
   - Kills any process using port 3000
   - Uses SIGTERM first, then SIGKILL if needed
   
2. **Start Phase:**
   - Runs `./start.sh` to start fresh

**When to use:**
- Ports are already in use (error: "Port already in use")
- After updating code (trading logic, config, etc.)
- Bot is unresponsive or behaving oddly
- You want a clean slate without manual cleanup
- After pulling new changes from git

**Advantages over stop + start:**
- Handles stuck processes automatically
- Clears port conflicts
- One command instead of two
- More aggressive cleanup

---

## Installation & Setup Scripts

### 📦 install.sh - Initial Installation
```bash
./install.sh
```
**What it does:**
- Installs Python dependencies
- Sets up the environment
- Makes scripts executable

**When to use:**
- First time setup
- After cloning the repository
- When dependencies are missing

---

### 🔒 configure_firewall.sh - Open Firewall Ports
```bash
./configure_firewall.sh
```
**What it does:**
- Opens port 8000 (backend API)
- Opens port 3000 (frontend dashboard)
- Configures UFW firewall rules

**When to use:**
- Making bot accessible from external IPs
- First time setup on a server
- After firewall reset

---

### 📊 status.sh - Check Server Status
```bash
./status.sh
```
**What it does:**
- Shows server IP addresses
- Checks port availability
- Displays firewall status
- Lists running bot processes

**When to use:**
- Checking if bot is running
- Troubleshooting connectivity
- Getting access URLs
- Verifying firewall configuration

---

## Common Workflows

### Starting Fresh
```bash
./install.sh          # First time only
./configure_firewall.sh  # First time only
./start.sh
```

### Daily Operations
```bash
# Start trading
./start.sh

# Stop for the day
./stop.sh

# Quick restart
./restart.sh
```

### After Code Changes
```bash
./restart.sh  # Recommended - handles everything
# OR
./stop.sh
# make your changes
./start.sh
```

### Troubleshooting Port Conflicts
```bash
# If you see "Port already in use" error:
./restart.sh  # This will force-kill the port hoggers

# OR manually:
./stop.sh
lsof -ti :8000 | xargs kill -9  # Force kill port 8000
lsof -ti :3000 | xargs kill -9  # Force kill port 3000
./start.sh
```

### Checking Status
```bash
./status.sh  # See what's running and on which ports
```

---

## Script Comparison

| Script | Graceful Stop | Force Kill | Starts Bot | Use Case |
|--------|--------------|------------|------------|----------|
| `start.sh` | ❌ | ❌ | ✅ | Clean start when ports are free |
| `stop.sh` | ✅ | ✅ (if needed) | ❌ | Graceful shutdown |
| `restart.sh` | ✅ | ✅ (always) | ✅ | Complete restart with cleanup |

---

## Exit Codes & Error Handling

### start.sh
- **Exit 1**: Port already in use
- **Solution**: Use `./restart.sh` or `./stop.sh` first

### stop.sh
- Always succeeds (returns 0)
- Uses force kill as fallback

### restart.sh
- **Exit 1**: `start.sh` not found
- **Exit 1**: Failed to free ports
- **Solution**: Check you're in the correct directory

---

## Process Management Details

### What Gets Killed

**restart.sh and stop.sh target:**
1. Python processes matching `python3.*main.py` (backend)
2. Python processes matching `python3.*http.server.*3000` (frontend)
3. Any process listening on port 8000
4. Any process listening on port 3000

### Kill Sequence
1. **SIGTERM (15)**: Graceful shutdown request
2. **Wait 2-3 seconds**: Allow cleanup
3. **SIGKILL (9)**: Force kill if still running

---

## Tips & Best Practices

### ✅ DO
- Use `./restart.sh` when in doubt
- Run `./status.sh` to check current state
- Use `./stop.sh` before system maintenance
- Check logs after restart for errors

### ❌ DON'T
- Don't run multiple instances simultaneously
- Don't manually kill processes without using scripts
- Don't start without checking port availability (unless using restart.sh)
- Don't forget to stop before making config changes

---

## Logs & Debugging

### View Backend Logs
```bash
tail -f backend.log
```

### View Frontend Logs
```bash
tail -f frontend.log
```

### Check Running Processes
```bash
ps aux | grep python3
lsof -i :8000
lsof -i :3000
```

### Manual Port Cleanup (if scripts fail)
```bash
# Find and kill port 8000
lsof -ti :8000 | xargs kill -9

# Find and kill port 3000
lsof -ti :3000 | xargs kill -9
```

---

## Quick Reference

```bash
# Start
./start.sh

# Stop
./stop.sh

# Restart (recommended for most cases)
./restart.sh

# Check status
./status.sh

# First time setup
./install.sh && ./configure_firewall.sh && ./start.sh
```

