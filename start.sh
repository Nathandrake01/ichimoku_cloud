#!/bin/bash

# Ichimoku Cloud Trading Bot - ALL-IN Strategy Startup Script

echo "Starting Ichimoku Cloud Trading Bot - ALL-IN Strategy..."

# Set environment variables
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Function to get server IP addresses
get_server_ip() {
    # Get private IP (for internal reference)
    PRIVATE_IP=$(hostname -I | awk '{print $1}')
    if [ -z "$PRIVATE_IP" ]; then
        PRIVATE_IP=$(ip route get 8.8.8.8 | awk 'NR==1 {print $7}')
    fi

    # Get public IP (for external access)
    PUBLIC_IP=$(curl -s --max-time 5 https://api.ipify.org 2>/dev/null)
    if [ -z "$PUBLIC_IP" ]; then
        PUBLIC_IP="Unable to detect"
    fi

    echo "$PRIVATE_IP|$PUBLIC_IP"
}

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "Port $1 is already in use. Please stop the service using that port or choose a different port."
        exit 1
    fi
}

# Check if ports are available
check_port 8001
check_port 3001

# Start backend in background
echo "Starting backend API server on port 8001..."
cd backend
python3 main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "Starting frontend server on port 3001..."
cd ../frontend
python3 -m http.server --bind 0.0.0.0 3001 &
FRONTEND_PID=$!

# Get server IPs
IP_INFO=$(get_server_ip)
PRIVATE_IP=$(echo $IP_INFO | cut -d'|' -f1)
PUBLIC_IP=$(echo $IP_INFO | cut -d'|' -f2)

echo ""
echo "🚀 Ichimoku Cloud Trading Bot - ALL-IN Strategy is running!"
echo ""
echo "📊 Frontend Dashboard:"
echo "   Local:     http://localhost:3001"
echo "   Private:   http://$PRIVATE_IP:3001"
echo "   Public:    http://$PUBLIC_IP:3001"
echo ""
echo "🔧 Backend API:"
echo "   Local:     http://localhost:8001"
echo "   Private:   http://$PRIVATE_IP:8001"
echo "   Public:    http://$PUBLIC_IP:8001"
echo ""
echo "📚 API Documentation:"
echo "   Local:     http://localhost:8001/docs"
echo "   Private:   http://$PRIVATE_IP:8001/docs"
echo "   Public:    http://$PUBLIC_IP:8001/docs"
echo ""
echo "⚠️  SECURITY WARNING: The bot is now accessible externally!"
echo "   Make sure to secure your server and consider using HTTPS."
echo ""
echo "Press Ctrl+C to stop all services"

# Function to kill both processes on exit
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Services stopped."
    exit 0
}

# Set trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Wait for processes
wait
