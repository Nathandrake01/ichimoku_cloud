#!/bin/bash

# Ichimoku Cloud Trading Bot Installation Script

echo "🚀 Installing Ichimoku Cloud Trading Bot..."
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the ichimoku_cloud directory"
    exit 1
fi

# Install Node.js if not present
echo "📦 Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    echo "✅ Node.js is already installed"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    echo "✅ Python dependencies installed"
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Make scripts executable
cd ..
chmod +x start.sh
echo "✅ Scripts are now executable"

echo ""
echo "🎉 Installation complete!"
echo ""
echo "To start the trading bot:"
echo "  ./start.sh"
echo ""
echo "Then open your browser to:"
echo "  http://localhost:3000"
echo ""
echo "Happy trading! 📈"
