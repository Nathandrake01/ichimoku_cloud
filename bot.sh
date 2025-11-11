#!/bin/bash

# Ichimoku Cloud Trading Bot - Unified Management Script
# Usage: ./bot.sh [command]
# Commands: start, stop, restart, status, logs, background, help

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"
BACKEND_LOG="backend.log"
FRONTEND_LOG="frontend.log"
BACKEND_PID_FILE="backend.pid"
FRONTEND_PID_FILE="frontend.pid"
POSITIONS_FILE="backend/positions.json"
EQUITY_FILE="backend/equity_history.json"

# Function to print colored messages
print_header() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Function to clear all trading data
clear_data() {
    local silent=$1
    
    if [ "$silent" != "silent" ]; then
        print_info "Clearing trading data..."
    fi
    
    # Remove positions and equity history
    /bin/rm -f "$POSITIONS_FILE" 2>/dev/null || true
    /bin/rm -f "$EQUITY_FILE" 2>/dev/null || true
    
    # Remove logs
    /bin/rm -f "$BACKEND_LOG" 2>/dev/null || true
    /bin/rm -f "$FRONTEND_LOG" 2>/dev/null || true
    
    # Remove PID files
    /bin/rm -f "$BACKEND_PID_FILE" 2>/dev/null || true
    /bin/rm -f "$FRONTEND_PID_FILE" 2>/dev/null || true
    
    if [ "$silent" != "silent" ]; then
        print_success "All trading data cleared"
    fi
}

# Function to kill processes on a specific port
kill_port() {
    local port=$1
    local pids=$(lsof -ti :$port 2>/dev/null || true)
    
    if [ -z "$pids" ]; then
        return 0
    fi
    
    print_info "Killing processes on port $port: $pids"
    
    # Try graceful shutdown first
    for pid in $pids; do
        if ps -p $pid > /dev/null 2>&1; then
            kill -15 $pid 2>/dev/null || true
        fi
    done
    
    sleep 2
    
    # Force kill if still running
    local remaining=$(lsof -ti :$port 2>/dev/null || true)
    if [ ! -z "$remaining" ]; then
        for pid in $remaining; do
            if ps -p $pid > /dev/null 2>&1; then
                kill -9 $pid 2>/dev/null || true
            fi
        done
        sleep 1
    fi
    
    # Final check
    if [ -z "$(lsof -ti :$port 2>/dev/null || true)" ]; then
        print_success "Port $port is free"
        return 0
    else
        print_error "Failed to free port $port"
        return 1
    fi
}

# Function to kill bot processes
kill_bot_processes() {
    print_info "Stopping bot processes..."
    
    # Kill backend
    local backend_pids=$(pgrep -f "python3.*main.py" 2>/dev/null || true)
    if [ ! -z "$backend_pids" ]; then
        for pid in $backend_pids; do
            kill -15 $pid 2>/dev/null || true
        done
        sleep 2
        backend_pids=$(pgrep -f "python3.*main.py" 2>/dev/null || true)
        if [ ! -z "$backend_pids" ]; then
            for pid in $backend_pids; do
                kill -9 $pid 2>/dev/null || true
            done
        fi
    fi
    
    # Kill frontend
    local frontend_pids=$(pgrep -f "python3.*http.server.*3000" 2>/dev/null || true)
    if [ ! -z "$frontend_pids" ]; then
        for pid in $frontend_pids; do
            kill -15 $pid 2>/dev/null || true
        done
        sleep 2
        frontend_pids=$(pgrep -f "python3.*http.server.*3000" 2>/dev/null || true)
        if [ ! -z "$frontend_pids" ]; then
            for pid in $frontend_pids; do
                kill -9 $pid 2>/dev/null || true
            done
        fi
    fi
    
    # Clean up PID files
    rm -f $BACKEND_PID_FILE $FRONTEND_PID_FILE
    
    print_success "Bot processes stopped"
}

# Function to get server IP addresses
get_server_ip() {
    local private_ip=$(hostname -I | awk '{print $1}')
    if [ -z "$private_ip" ]; then
        private_ip=$(ip route get 8.8.8.8 | awk 'NR==1 {print $7}')
    fi
    
    local public_ip=$(curl -s --max-time 5 https://api.ipify.org 2>/dev/null || echo "Unable to detect")
    
    echo "$private_ip|$public_ip"
}

# Function to check if bot is running
is_running() {
    local backend_running=false
    local frontend_running=false
    
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        backend_running=true
    fi
    
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        frontend_running=true
    fi
    
    if [ "$backend_running" = true ] && [ "$frontend_running" = true ]; then
        return 0
    else
        return 1
    fi
}

# Function to start bot in foreground
start_foreground() {
    print_header "Starting Ichimoku Cloud Trading Bot (Foreground)"
    
    # Check if already running
    if is_running; then
        print_error "Bot is already running!"
        print_info "Use './bot.sh stop' first or './bot.sh restart' to restart"
        exit 1
    fi
    
    # Check ports
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_error "Port $BACKEND_PORT is already in use"
        print_info "Use './bot.sh restart' to force restart"
        exit 1
    fi
    
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_error "Port $FRONTEND_PORT is already in use"
        print_info "Use './bot.sh restart' to force restart"
        exit 1
    fi
    
    # Start backend
    print_info "Starting backend API server on port $BACKEND_PORT..."
    cd $BACKEND_DIR
    python3 main.py &
    BACKEND_PID=$!
    cd ..
    
    sleep 3
    
    # Start frontend
    print_info "Starting frontend server on port $FRONTEND_PORT..."
    cd $FRONTEND_DIR
    python3 -m http.server --bind 0.0.0.0 $FRONTEND_PORT &
    FRONTEND_PID=$!
    cd ..
    
    # Get server IPs
    local ip_info=$(get_server_ip)
    local private_ip=$(echo $ip_info | cut -d'|' -f1)
    local public_ip=$(echo $ip_info | cut -d'|' -f2)
    
    echo ""
    print_success "Ichimoku Cloud Trading Bot is running!"
    echo ""
    echo -e "${MAGENTA}📊 Frontend Dashboard:${NC}"
    echo "   Local:     http://localhost:$FRONTEND_PORT"
    echo "   Private:   http://$private_ip:$FRONTEND_PORT"
    echo "   Public:    http://$public_ip:$FRONTEND_PORT"
    echo ""
    echo -e "${MAGENTA}🔧 Backend API:${NC}"
    echo "   Local:     http://localhost:$BACKEND_PORT"
    echo "   Private:   http://$private_ip:$BACKEND_PORT"
    echo "   Public:    http://$public_ip:$BACKEND_PORT"
    echo ""
    echo -e "${MAGENTA}📚 API Documentation:${NC}"
    echo "   http://localhost:$BACKEND_PORT/docs"
    echo ""
    print_warning "Press Ctrl+C to stop all services"
    
    # Cleanup function
    cleanup() {
        echo ""
        print_info "Stopping services..."
        kill $BACKEND_PID 2>/dev/null || true
        kill $FRONTEND_PID 2>/dev/null || true
        print_success "Services stopped"
        exit 0
    }
    
    trap cleanup SIGINT SIGTERM
    wait
}

# Function to start bot in background
start_background() {
    print_header "Starting Ichimoku Cloud Trading Bot (Background)"
    
    # Check if already running
    if is_running; then
        print_error "Bot is already running!"
        print_info "Use './bot.sh stop' first or './bot.sh restart' to restart"
        exit 1
    fi
    
    # Check ports
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_error "Port $BACKEND_PORT is already in use"
        print_info "Use './bot.sh restart --background' to force restart"
        exit 1
    fi
    
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_error "Port $FRONTEND_PORT is already in use"
        print_info "Use './bot.sh restart --background' to force restart"
        exit 1
    fi
    
    # Start backend in background
    print_info "Starting backend API server on port $BACKEND_PORT..."
    cd $BACKEND_DIR
    nohup python3 main.py > ../$BACKEND_LOG 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../$BACKEND_PID_FILE
    cd ..
    
    sleep 3
    
    # Start frontend in background
    print_info "Starting frontend server on port $FRONTEND_PORT..."
    cd $FRONTEND_DIR
    nohup python3 -m http.server --bind 0.0.0.0 $FRONTEND_PORT > ../$FRONTEND_LOG 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../$FRONTEND_PID_FILE
    cd ..
    
    # Get server IPs
    local ip_info=$(get_server_ip)
    local private_ip=$(echo $ip_info | cut -d'|' -f1)
    local public_ip=$(echo $ip_info | cut -d'|' -f2)
    
    echo ""
    print_success "Bot started in background!"
    echo ""
    echo -e "${MAGENTA}📊 Frontend Dashboard:${NC}"
    echo "   Local:     http://localhost:$FRONTEND_PORT"
    echo "   Private:   http://$private_ip:$FRONTEND_PORT"
    echo "   Public:    http://$public_ip:$FRONTEND_PORT"
    echo ""
    echo -e "${MAGENTA}🔧 Backend API:${NC}"
    echo "   Local:     http://localhost:$BACKEND_PORT"
    echo "   Private:   http://$private_ip:$BACKEND_PORT"
    echo "   Public:    http://$public_ip:$BACKEND_PORT"
    echo ""
    print_info "Backend PID: $BACKEND_PID (saved to $BACKEND_PID_FILE)"
    print_info "Frontend PID: $FRONTEND_PID (saved to $FRONTEND_PID_FILE)"
    echo ""
    print_info "View logs: ./bot.sh logs"
    print_info "Stop bot: ./bot.sh stop"
}

# Function to stop bot
stop_bot() {
    print_header "Stopping Ichimoku Cloud Trading Bot"
    
    if ! is_running; then
        print_warning "Bot is not running"
    fi
    
    # Always clean up processes and ports
    kill_bot_processes
    echo ""
    kill_port $BACKEND_PORT
    echo ""
    kill_port $FRONTEND_PORT
    echo ""
    
    # Clear PID files and logs (but keep trading data)
    /bin/rm -f "$BACKEND_PID_FILE" 2>/dev/null || true
    /bin/rm -f "$FRONTEND_PID_FILE" 2>/dev/null || true
    /bin/rm -f "$BACKEND_LOG" 2>/dev/null || true
    /bin/rm -f "$FRONTEND_LOG" 2>/dev/null || true
    
    print_success "All services stopped and cleaned up"
    print_info "Trading data preserved (positions.json, equity_history.json)"
}

# Function to restart bot (FRESH START - clears all data)
restart_bot() {
    local background_mode=$1
    
    print_header "Restarting Ichimoku Cloud Trading Bot (Fresh Start)"
    
    # Stop everything
    print_info "Step 1: Stopping existing processes"
    echo ""
    kill_bot_processes
    echo ""
    kill_port $BACKEND_PORT
    echo ""
    kill_port $FRONTEND_PORT
    echo ""
    
    # Clear all data for fresh start
    print_info "Step 2: Clearing all trading data and logs"
    clear_data "silent"
    print_success "All data cleared - starting fresh"
    echo ""
    
    # Start fresh
    print_info "Step 3: Starting bot with clean slate"
    echo ""
    
    if [ "$background_mode" = "background" ]; then
        start_background
    else
        start_foreground
    fi
}

# Function to show status
show_status() {
    print_header "Ichimoku Cloud Trading Bot Status"
    
    # Get server IPs
    local ip_info=$(get_server_ip)
    local private_ip=$(echo $ip_info | cut -d'|' -f1)
    local public_ip=$(echo $ip_info | cut -d'|' -f2)
    
    echo ""
    echo -e "${MAGENTA}Server Information:${NC}"
    echo "  Private IP: $private_ip"
    echo "  Public IP:  $public_ip"
    echo ""
    
    # Check backend
    echo -e "${MAGENTA}Backend (Port $BACKEND_PORT):${NC}"
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        local backend_pid=$(lsof -ti :$BACKEND_PORT)
        print_success "Running (PID: $backend_pid)"
        echo "  URL: http://localhost:$BACKEND_PORT"
        echo "  Docs: http://localhost:$BACKEND_PORT/docs"
    else
        print_error "Not running"
    fi
    echo ""
    
    # Check frontend
    echo -e "${MAGENTA}Frontend (Port $FRONTEND_PORT):${NC}"
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        local frontend_pid=$(lsof -ti :$FRONTEND_PORT)
        print_success "Running (PID: $frontend_pid)"
        echo "  URL: http://localhost:$FRONTEND_PORT"
    else
        print_error "Not running"
    fi
    echo ""
    
    # Overall status
    echo -e "${MAGENTA}Overall Status:${NC}"
    if is_running; then
        print_success "Bot is running"
    else
        print_error "Bot is not running"
    fi
    echo ""
    
    # Show PID files if they exist
    if [ -f "$BACKEND_PID_FILE" ] || [ -f "$FRONTEND_PID_FILE" ]; then
        echo -e "${MAGENTA}PID Files:${NC}"
        if [ -f "$BACKEND_PID_FILE" ]; then
            echo "  Backend: $(cat $BACKEND_PID_FILE)"
        fi
        if [ -f "$FRONTEND_PID_FILE" ]; then
            echo "  Frontend: $(cat $FRONTEND_PID_FILE)"
        fi
        echo ""
    fi
    
    # Show log files
    echo -e "${MAGENTA}Log Files:${NC}"
    if [ -f "$BACKEND_LOG" ]; then
        local backend_size=$(du -h $BACKEND_LOG | cut -f1)
        echo "  Backend: $BACKEND_LOG ($backend_size)"
    fi
    if [ -f "$FRONTEND_LOG" ]; then
        local frontend_size=$(du -h $FRONTEND_LOG | cut -f1)
        echo "  Frontend: $FRONTEND_LOG ($frontend_size)"
    fi
}

# Function to show logs
show_logs() {
    local follow=$1
    
    if [ "$follow" = "follow" ]; then
        print_header "Following Bot Logs (Ctrl+C to stop)"
        echo ""
        if [ -f "$BACKEND_LOG" ] && [ -f "$FRONTEND_LOG" ]; then
            tail -f $BACKEND_LOG $FRONTEND_LOG
        elif [ -f "$BACKEND_LOG" ]; then
            tail -f $BACKEND_LOG
        elif [ -f "$FRONTEND_LOG" ]; then
            tail -f $FRONTEND_LOG
        else
            print_error "No log files found"
            print_info "Logs are only available when running in background mode"
        fi
    else
        print_header "Recent Bot Logs (Last 50 lines)"
        echo ""
        if [ -f "$BACKEND_LOG" ]; then
            echo -e "${CYAN}=== Backend Log ===${NC}"
            tail -n 50 $BACKEND_LOG
            echo ""
        fi
        if [ -f "$FRONTEND_LOG" ]; then
            echo -e "${CYAN}=== Frontend Log ===${NC}"
            tail -n 50 $FRONTEND_LOG
        fi
        if [ ! -f "$BACKEND_LOG" ] && [ ! -f "$FRONTEND_LOG" ]; then
            print_error "No log files found"
            print_info "Logs are only available when running in background mode"
        fi
    fi
}

# Function to show help
show_help() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}Ichimoku Cloud Trading Bot - Management Script${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  ./bot.sh [command] [options]"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo -e "  ${GREEN}start${NC}              Start bot (keeps existing positions/data)"
    echo -e "  ${GREEN}start --background${NC} Start bot in background (keeps data)"
    echo -e "  ${GREEN}stop${NC}               Stop bot and clean up (keeps trading data)"
    echo -e "  ${GREEN}restart${NC}            🔄 FRESH START - clears ALL data and restarts"
    echo -e "  ${GREEN}restart --background${NC} Fresh start in background"
    echo -e "  ${GREEN}status${NC}             Show bot status and info"
    echo -e "  ${GREEN}logs${NC}               Show recent logs"
    echo -e "  ${GREEN}logs --follow${NC}      Follow logs in real-time"
    echo -e "  ${GREEN}help${NC}               Show this help message"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  ./bot.sh start                    # Start (keeps existing data)"
    echo "  ./bot.sh start --background       # Start in background"
    echo "  ./bot.sh restart                  # Fresh start (clears everything)"
    echo "  ./bot.sh restart --background     # Fresh start in background"
    echo "  ./bot.sh stop                     # Stop (keeps trading data)"
    echo "  ./bot.sh status                   # Check status"
    echo "  ./bot.sh logs --follow            # Watch logs"
    echo ""
    echo -e "${YELLOW}Aliases:${NC}"
    echo "  start:   --start, -s"
    echo "  stop:    --stop, -x"
    echo "  restart: --restart, -r"
    echo "  status:  --status, -i"
    echo "  logs:    --logs, -l"
    echo "  help:    --help, -h"
    echo ""
    echo -e "${YELLOW}Tips:${NC}"
    echo "  • 'start' keeps your existing positions and continues trading"
    echo "  • 'restart' gives you a FRESH START (clears all positions/data)"
    echo "  • 'stop' stops the bot but preserves your trading data"
    echo "  • Use background mode for 24/7 operation"
    echo "  • Use './bot.sh restart' when you want to reset everything"
    echo ""
}

# Main script logic
main() {
    local command=$1
    local option=$2
    
    # Handle no arguments
    if [ -z "$command" ]; then
        show_help
        exit 0
    fi
    
    # Parse command
    case "$command" in
        start|--start|-s)
            if [ "$option" = "--background" ] || [ "$option" = "-b" ]; then
                start_background
            else
                start_foreground
            fi
            ;;
        stop|--stop|-x)
            stop_bot
            ;;
        restart|--restart|-r)
            if [ "$option" = "--background" ] || [ "$option" = "-b" ]; then
                restart_bot "background"
            else
                restart_bot "foreground"
            fi
            ;;
        status|--status|-i)
            show_status
            ;;
        logs|--logs|-l)
            if [ "$option" = "--follow" ] || [ "$option" = "-f" ]; then
                show_logs "follow"
            else
                show_logs
            fi
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"

