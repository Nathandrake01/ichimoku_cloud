#!/bin/bash

# Ichimoku Cloud Trading Bot Stop Script
# This script will gracefully stop all bot processes

echo "🛑 Stopping Ichimoku Cloud Trading Bot..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to kill processes on a specific port
kill_port() {
    local port=$1
    echo -e "${YELLOW}Checking port $port...${NC}"
    
    # Find PIDs using the port
    PIDS=$(lsof -ti :$port 2>/dev/null || true)
    
    if [ -z "$PIDS" ]; then
        echo -e "${GREEN}✓ No processes on port $port${NC}"
        return 0
    fi
    
    echo -e "${RED}Found processes on port $port: $PIDS${NC}"
    
    # Try graceful shutdown first (SIGTERM)
    for pid in $PIDS; do
        if ps -p $pid > /dev/null 2>&1; then
            echo "  Sending SIGTERM to PID $pid..."
            kill -15 $pid 2>/dev/null || true
        fi
    done
    
    # Wait for graceful shutdown
    sleep 3
    
    # Force kill if still running (SIGKILL)
    REMAINING=$(lsof -ti :$port 2>/dev/null || true)
    if [ ! -z "$REMAINING" ]; then
        echo -e "${RED}  Force killing remaining processes...${NC}"
        for pid in $REMAINING; do
            if ps -p $pid > /dev/null 2>&1; then
                echo "  Sending SIGKILL to PID $pid..."
                kill -9 $pid 2>/dev/null || true
            fi
        done
        sleep 1
    fi
    
    # Final check
    FINAL_CHECK=$(lsof -ti :$port 2>/dev/null || true)
    if [ -z "$FINAL_CHECK" ]; then
        echo -e "${GREEN}✓ Port $port is now free${NC}"
    else
        echo -e "${RED}✗ Failed to free port $port${NC}"
        return 1
    fi
}

# Function to kill Python processes related to the bot
kill_bot_processes() {
    echo -e "${YELLOW}Checking for running bot processes...${NC}"
    
    # Kill backend processes
    BACKEND_PIDS=$(pgrep -f "python3.*main.py" 2>/dev/null || true)
    if [ ! -z "$BACKEND_PIDS" ]; then
        echo -e "${RED}Found backend processes: $BACKEND_PIDS${NC}"
        for pid in $BACKEND_PIDS; do
            echo "  Killing backend PID $pid..."
            kill -15 $pid 2>/dev/null || true
        done
        sleep 3
        # Force kill if needed
        BACKEND_PIDS=$(pgrep -f "python3.*main.py" 2>/dev/null || true)
        if [ ! -z "$BACKEND_PIDS" ]; then
            echo -e "${RED}  Force killing backend processes...${NC}"
            for pid in $BACKEND_PIDS; do
                kill -9 $pid 2>/dev/null || true
            done
        fi
        echo -e "${GREEN}✓ Backend stopped${NC}"
    else
        echo -e "${GREEN}✓ No backend processes running${NC}"
    fi
    
    # Kill frontend http.server processes on port 3000
    FRONTEND_PIDS=$(pgrep -f "python3.*http.server.*3000" 2>/dev/null || true)
    if [ ! -z "$FRONTEND_PIDS" ]; then
        echo -e "${RED}Found frontend processes: $FRONTEND_PIDS${NC}"
        for pid in $FRONTEND_PIDS; do
            echo "  Killing frontend PID $pid..."
            kill -15 $pid 2>/dev/null || true
        done
        sleep 3
        # Force kill if needed
        FRONTEND_PIDS=$(pgrep -f "python3.*http.server.*3000" 2>/dev/null || true)
        if [ ! -z "$FRONTEND_PIDS" ]; then
            echo -e "${RED}  Force killing frontend processes...${NC}"
            for pid in $FRONTEND_PIDS; do
                kill -9 $pid 2>/dev/null || true
            done
        fi
        echo -e "${GREEN}✓ Frontend stopped${NC}"
    else
        echo -e "${GREEN}✓ No frontend processes running${NC}"
    fi
}

# Main stop sequence
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Stopping all bot processes and freeing ports"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Kill bot processes
kill_bot_processes
echo ""

# Kill processes on ports
kill_port 8000
echo ""
kill_port 3000
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✓ All services stopped successfully${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

