#!/bin/bash

echo "🛑 Stopping Ichimoku Cloud Trading Bot - ALL-IN Strategy..."

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Stopping all bot processes and freeing ports"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check for running bot processes
echo -e "\033[1;33mChecking for running bot processes...\033[0m"

# Find backend processes (Python running main.py on port 8001)
BACKEND_PIDS=$(ps aux | grep "python.*main.py" | grep -v grep | awk '{print $2}')
if [ ! -z "$BACKEND_PIDS" ]; then
    echo -e "\033[0;31mFound backend processes: $BACKEND_PIDS\033[0m"
    for PID in $BACKEND_PIDS; do
        echo "  Killing backend PID $PID..."
        kill $PID 2>/dev/null || kill -9 $PID 2>/dev/null
    done
    echo -e "\033[0;32m✓ Backend stopped\033[0m"
else
    echo -e "\033[0;32m✓ No backend processes found\033[0m"
fi

# Find frontend processes (http.server on port 3001)
FRONTEND_PIDS=$(lsof -ti:3001 2>/dev/null)
if [ ! -z "$FRONTEND_PIDS" ]; then
    echo -e "\033[0;31mFound frontend processes: $FRONTEND_PIDS\033[0m"
    for PID in $FRONTEND_PIDS; do
        echo "  Killing frontend PID $PID..."
        kill $PID 2>/dev/null || kill -9 $PID 2>/dev/null
    done
    echo -e "\033[0;32m✓ Frontend stopped\033[0m"
else
    echo -e "\033[0;32m✓ No frontend processes found\033[0m"
fi

# Double check ports are free
echo ""
echo -e "\033[1;33mChecking port 8001...\033[0m"
PORT_8001=$(lsof -ti:8001 2>/dev/null)
if [ ! -z "$PORT_8001" ]; then
    echo "  Killing remaining process on port 8001: $PORT_8001"
    kill -9 $PORT_8001 2>/dev/null
fi
echo -e "\033[0;32m✓ No processes on port 8001\033[0m"

echo ""
echo -e "\033[1;33mChecking port 3001...\033[0m"
PORT_3001=$(lsof -ti:3001 2>/dev/null)
if [ ! -z "$PORT_3001" ]; then
    echo "  Killing remaining process on port 3001: $PORT_3001"
    kill -9 $PORT_3001 2>/dev/null
fi
echo -e "\033[0;32m✓ No processes on port 3001\033[0m"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "\033[0;32m✓ All services stopped successfully\033[0m"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
