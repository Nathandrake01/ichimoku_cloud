#!/bin/bash

# Ichimoku Cloud Trading Bot - Status Check Script

echo "📊 Ichimoku Cloud Trading Bot Status"
echo "=================================="
echo ""

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

# Get server information
IP_INFO=$(get_server_ip)
PRIVATE_IP=$(echo $IP_INFO | cut -d'|' -f1)
PUBLIC_IP=$(echo $IP_INFO | cut -d'|' -f2)
HOSTNAME=$(hostname)

echo "🖥️  Server Information:"
echo "   Hostname: $HOSTNAME"
echo "   Private IP: $PRIVATE_IP"
echo "   Public IP: $PUBLIC_IP"
echo ""

# Check if services are running
echo "🔍 Service Status:"
echo ""

# Check backend (port 8000)
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null; then
    echo "   ✅ Backend API (port 8000): RUNNING"
    echo "      Local:     http://localhost:8000"
    echo "      Private:   http://$PRIVATE_IP:8000"
    echo "      Public:    http://$PUBLIC_IP:8000"
    echo "      API Docs:  http://$PUBLIC_IP:8000/docs"

    # Test backend health
    if curl -s http://localhost:8000/api/health > /dev/null; then
        echo "      Health:  ✅ OK"
    else
        echo "      Health:  ❌ FAILED"
    fi
else
    echo "   ❌ Backend API (port 8000): NOT RUNNING"
fi
echo ""

# Check frontend (port 3000)
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null; then
    echo "   ✅ Frontend Dashboard (port 3000): RUNNING"
    echo "      Local:   http://localhost:3000"
    echo "      Private: http://$PRIVATE_IP:3000"
    echo "      Public:  http://$PUBLIC_IP:3000"
else
    echo "   ❌ Frontend Dashboard (port 3000): NOT RUNNING"
fi
echo ""

# Check firewall status
echo "🔥 Firewall Status:"
if command -v ufw &> /dev/null; then
    echo "   UFW Status:"
    sudo ufw status | grep -E "(3000|8000|Status)" | sed 's/^/      /'
elif command -v iptables &> /dev/null; then
    echo "   iptables rules for ports 3000/8000:"
    sudo iptables -L INPUT -n | grep -E "(:3000|:8000)" | sed 's/^/      /' || echo "      No specific rules found"
else
    echo "   ❌ No firewall management tool detected"
fi
echo ""

# Network connectivity test
echo "🌐 Network Connectivity:"
echo "   Testing public access to port 3000..."
if curl -s --max-time 5 http://$PUBLIC_IP:3000 > /dev/null; then
    echo "   ✅ Port 3000: ACCESSIBLE from internet"
else
    echo "   ❌ Port 3000: NOT accessible from internet (firewall/cloud security group?)"
fi

echo "   Testing public access to port 8000..."
if curl -s --max-time 5 http://$PUBLIC_IP:8000 > /dev/null; then
    echo "   ✅ Port 8000: ACCESSIBLE from internet"
else
    echo "   ❌ Port 8000: NOT accessible from internet (firewall/cloud security group?)"
fi
echo ""

echo "💡 Quick Actions:"
echo "   Start bot:     ./start.sh"
echo "   Configure FW:  ./configure_firewall.sh"
echo "   Check status:  ./status.sh"
echo ""

echo "⚠️  Security Reminder:"
echo "   Your trading bot is accessible externally!"
echo "   Consider implementing authentication, HTTPS, and IP restrictions."
echo ""
