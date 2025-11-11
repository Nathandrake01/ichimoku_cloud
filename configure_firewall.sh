#!/bin/bash

# Ichimoku Cloud Trading Bot - Firewall Configuration Script

echo "🔥 Configuring firewall for Ichimoku Cloud Trading Bot..."
echo ""

# Check if ufw is available
if command -v ufw &> /dev/null; then
    echo "✅ UFW (Uncomplicated Firewall) is available"
    echo ""

    # Check current firewall status
    echo "Current firewall status:"
    sudo ufw status
    echo ""

    # Allow ports for the trading bot
    echo "Allowing ports 3000 (frontend) and 8000 (backend)..."
    sudo ufw allow 3000/tcp
    sudo ufw allow 8000/tcp

    echo ""
    echo "✅ Firewall configured successfully!"
    echo ""
    echo "Updated firewall status:"
    sudo ufw status

elif command -v iptables &> /dev/null; then
    echo "⚠️  UFW not available, using iptables directly..."
    echo ""

    # Check if ports are already open
    echo "Checking current iptables rules for ports 3000 and 8000..."

    # Allow ports using iptables
    sudo iptables -A INPUT -p tcp --dport 3000 -j ACCEPT
    sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT

    echo ""
    echo "✅ Ports 3000 and 8000 opened in iptables"
    echo ""

    # Save iptables rules (if iptables-persistent is available)
    if command -v iptables-save &> /dev/null && command -v iptables-persistent &> /dev/null; then
        echo "Saving iptables rules..."
        sudo iptables-save | sudo tee /etc/iptables/rules.v4 > /dev/null
        echo "✅ iptables rules saved"
    else
        echo "⚠️  iptables rules not saved permanently."
        echo "   Consider installing iptables-persistent:"
        echo "   sudo apt install iptables-persistent"
    fi

else
    echo "❌ Neither UFW nor iptables found!"
    echo "   You may need to manually configure your firewall to allow ports 3000 and 8000"
    exit 1
fi

echo ""
echo "🌐 Firewall configuration complete!"
echo ""
echo "Your trading bot should now be accessible from external IP addresses."
echo "Make sure your cloud provider's security group also allows these ports."
echo ""
