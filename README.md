# Ichimoku Cloud Trading Bot

A sophisticated cryptocurrency trading bot that uses Ichimoku Cloud analysis on 1-hour charts to trade cryptocurrencies with a long-biased strategy.

## Features

- **Ichimoku Cloud Strategy**: Advanced technical analysis using Tenkan-sen, Kijun-sen, Senkou Span A/B, and Chikou Span
- **Long-Biased Approach**: 2x leverage on longs, 1x on shorts with 50/50 capital allocation
- **Risk Management**: Configurable risk percentage and portfolio value reduction
- **Real-time Trading**: Live price data from Binance via CCXT
- **Paper Trading**: Test strategies without real money
- **Beautiful Dashboard**: Modern web interface with real-time P&L, equity curve, and trade history
- **Automated Trading**: Scan for signals and execute trades automatically

## Strategy Details

### Long Signals (2x Leverage)
- Price closes above Ichimoku cloud
- Conversion line (Tenkan-sen) above base line (Kijun-sen)
- Price above conversion line
- Chikou Span "clean" (price above local minima)

### Short Signals (1x Leverage)
- Opposite conditions of long signals
- Only available for coins with decent volume (>$1M 24h volume)

### Exit Conditions
- **Stop Loss**: Price below/above Kijun-sen OR 2 consecutive candles inside cloud
- **Target**: Price below/above conversion line OR conversion/base line crossover

### Eligible Coins
- **Long Only**: HYPE, BNB, SOL, LINK
- **Short Only**: Any coin with >$1M daily volume (except long-only coins)

## Installation

### Prerequisites
- Python 3.8+
- Node.js 18+
- pip (Python package manager)

### Setup

1. **Clone or download the project**
   ```bash
   cd /path/to/ichimoku_cloud
   ```

2. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (optional)
   Create a `.env` file in the backend directory:
   ```env
   BINANCE_API_KEY=your_api_key
   BINANCE_SECRET_KEY=your_secret_key
   ```

4. **Make startup script executable**
   ```bash
   chmod +x start.sh
   ```

## Usage

### Unified Management Script (Recommended)

The bot includes a unified management script `bot.sh` that handles all operations:

```bash
# Start bot in foreground (for development)
./bot.sh start

# Start bot in background (for production - keeps running after logout)
./bot.sh start --background

# Stop bot
./bot.sh stop

# Restart bot
./bot.sh restart

# Restart in background
./bot.sh restart --background

# Check status
./bot.sh status

# View logs
./bot.sh logs

# Follow logs in real-time
./bot.sh logs --follow

# Show help
./bot.sh help
```

**Key Features:**
- ✅ Single command interface for all operations
- ✅ Background mode for 24/7 operation
- ✅ Automatic port conflict resolution
- ✅ Built-in log management
- ✅ Status monitoring
- ✅ Color-coded output

### Legacy Scripts (Still Available)

Individual scripts are still available if preferred:

```bash
./start.sh      # Start the bot
./stop.sh       # Stop the bot
./restart.sh    # Restart (kills ports if needed)
./status.sh     # Check if running
```

### When to Use Each Mode

**Foreground Mode** (`./bot.sh start`):
- Development and debugging
- When you want to see real-time output
- When you'll keep the terminal open
- Stops when you close terminal/SSH

**Background Mode** (`./bot.sh start --background`):
- Production deployment
- 24/7 server operation
- When you need to close terminal/SSH
- Keeps running after logout
- Outputs to log files

### Making the Bot Accessible Externally

To allow others to access your bot via your server's IP address:

1. **Configure Firewall** (one-time setup):
   ```bash
   ./configure_firewall.sh
   ```

2. **Check Status**:
   ```bash
   ./status.sh
   ```

3. **Start the Bot**:
   ```bash
   ./start.sh
   ```

The startup script will display both local and external URLs. Anyone with your server's IP address can then access:
- **Dashboard**: `http://YOUR_SERVER_IP:3000`
- **API**: `http://YOUR_SERVER_IP:8000`

### Security Considerations

⚠️ **Important**: When making your bot accessible externally:

- **Firewall**: Use the `configure_firewall.sh` script to open ports 3000 and 8000
- **Cloud Security Groups**: If using AWS/GCP/Azure, ensure ports are open in security groups
- **HTTPS**: Consider adding SSL certificates for secure access
- **Authentication**: Implement user authentication if needed
- **IP Restrictions**: Consider restricting access to specific IP addresses
- **VPN**: For sensitive operations, consider requiring VPN access

### Dashboard Features

The web dashboard provides:

- **Portfolio Overview**: Total value, P&L, drawdown, open positions
- **Real-time Updates**: Auto-refreshes every 30 seconds
- **Position Management**: View open positions and trade history (max 4 long + 4 short)
- **Configuration**: Adjust portfolio value and long leverage from frontend
- **Quick Actions**: Scan for signals, check exits, manual trading

### API Endpoints

- `GET /api/portfolio` - Get portfolio summary
- `GET /api/positions` - Get all positions and trades
- `GET /api/config` - Get current configuration
- `PUT /api/config` - Update configuration
- `POST /api/scan-and-trade` - Scan for signals and execute trades
- `POST /api/check-exits` - Check and close positions meeting exit conditions

### Configuration

#### Position Sizing
- **Capital Allocation**: 50/50 split between long and short positions
- **Long Positions**: Maximum 4 positions, $12.5 each at 2x leverage = $25 per position
- **Short Positions**: Maximum 4 positions, $12.5 each at 1x leverage = $12.5 per position
- **Long Leverage**: Configurable from frontend (default: 2x)

#### Trading Parameters
- **Short Leverage**: 1x (fixed)
- **Position Limits**: Max 4 long + 4 short positions

### Trading Workflow

1. **Configure Risk**: Set your risk tolerance in the dashboard
2. **Monitor Signals**: Use "Scan & Trade" to automatically find and execute trades
3. **Manage Positions**: System automatically checks for exits every scan
4. **Manual Override**: Use "Check Exits" to force position closure checks

## File Structure

```
ichimoku_cloud/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── config.py            # Configuration management
│   ├── ichimoku.py          # Ichimoku Cloud calculations
│   ├── trading_strategy.py  # Trading logic and position management
│   ├── data_provider.py     # CCXT integration for price data
│   ├── equity_tracker.py    # Track equity curve over time
│   ├── requirements.txt     # Python dependencies
│   └── positions.json       # Position storage (auto-generated)
├── frontend/
│   ├── index.html           # Main dashboard
│   └── package.json         # Frontend dependencies
├── bot.sh                   # 🌟 Unified management script (RECOMMENDED)
├── start.sh                 # Legacy: Startup script
├── stop.sh                  # Legacy: Stop all services
├── restart.sh               # Legacy: Restart script
├── status.sh                # Legacy: Server status checker
├── install.sh               # Installation script
├── configure_firewall.sh    # Firewall configuration
├── QUICK_START.md           # Quick reference guide
├── UNIFIED_SCRIPT_GUIDE.md  # Complete bot.sh documentation
├── SCRIPTS_GUIDE.md         # Legacy scripts documentation
├── TRADING_LOGIC_FIX.md     # Trading logic documentation
└── README.md                # This file
```

## Safety & Risk Management

### Paper Trading First
- Always test with `PAPER_TRADING: true` before going live
- Monitor performance and adjust risk settings

### Risk Controls
- Maximum risk per trade (configurable)
- Automatic stop losses
- Position size calculation based on risk tolerance

### Live Trading
- Set `PAPER_TRADING: false` in config.py
- Ensure sufficient API permissions on Binance
- Start with small position sizes

## Technical Details

### Ichimoku Cloud Components
- **Tenkan-sen**: (9-period high + low) / 2
- **Kijun-sen**: (26-period high + low) / 2
- **Senkou Span A**: (Tenkan + Kijun) / 2, plotted 26 periods ahead
- **Senkou Span B**: (52-period high + low) / 2, plotted 26 periods ahead
- **Chikou Span**: Current close plotted 26 periods back

### Signal Generation
- Uses 1-hour candles for analysis
- Requires sufficient historical data (52+ candles)
- Filters by volume for short opportunities

### Position Sizing
- Risk-based sizing: (portfolio_value × risk_percentage) × leverage
- 50/50 allocation between long and short positions
- Ensures adequate cash reserves

## Troubleshooting

### Backend Won't Start
- Check Python version: `python3 --version`
- Install dependencies: `pip install -r requirements.txt`
- Check port 8000 availability

### Frontend Not Loading
- Ensure backend is running first
- Check port 3000 availability
- Try accessing directly: http://localhost:3000

### No Trading Signals
- Verify internet connection for price data
- Check Binance API access
- Ensure sufficient historical data available

### API Errors
- Verify Binance API keys (if using live trading)
- Check API rate limits
- Review error logs in terminal

## Disclaimer

This trading bot is for educational and research purposes. Cryptocurrency trading involves substantial risk of loss and is not suitable for every investor. Past performance does not guarantee future results. Always test thoroughly and never risk more than you can afford to lose.

## License

MIT License - see LICENSE file for details
