from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
import uvicorn
from datetime import datetime
import json
import io
import csv

from config import config
from trading_strategy import trading_strategy
from data_provider import data_provider
from equity_tracker import equity_tracker

app = FastAPI(title="Ichimoku Cloud Trading Bot", version="1.0.0")

# Global flag to control the trading loop
trading_loop_running = False
trading_loop_task = None

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConfigUpdate(BaseModel):
    portfolio_value: Optional[float] = None
    long_leverage: Optional[float] = None

class TradeSignal(BaseModel):
    symbol: str
    signal_type: str  # 'long' or 'short'

@app.get("/")
async def root():
    return {"message": "Ichimoku Cloud Trading Bot API", "version": "1.0.0"}

@app.get("/api/portfolio")
async def get_portfolio():
    """Get portfolio summary"""
    return await trading_strategy.get_portfolio_summary()

@app.get("/api/positions")
async def get_positions():
    """Get all positions"""
    positions = await trading_strategy.get_positions()
    return {"positions": positions}

@app.get("/api/config")
async def get_config():
    """Get current configuration"""
    config_data = config.get_config()
    return {
        "long_coins": config_data.LONG_COINS,
        "initial_portfolio_value": config_data.INITIAL_PORTFOLIO_VALUE,
        "current_portfolio_value": config_data.CURRENT_PORTFOLIO_VALUE,
        "long_leverage": config_data.LONG_LEVERAGE,
        "short_leverage": config_data.SHORT_LEVERAGE,
        "max_long_positions": config_data.MAX_LONG_POSITIONS,
        "max_short_positions": config_data.MAX_SHORT_POSITIONS,
        "paper_trading": config_data.PAPER_TRADING
    }

@app.put("/api/config")
async def update_config(config_update: ConfigUpdate):
    """Update configuration"""
    try:
        if config_update.portfolio_value is not None:
            config.update_portfolio_value(config_update.portfolio_value)

        if config_update.long_leverage is not None:
            config.update_long_leverage(config_update.long_leverage)

        return {"message": "Configuration updated successfully"}
    except ValueError as e:
        return {"error": str(e)}

@app.get("/api/signals")
async def get_signals():
    """Scan for trading signals"""
    signals = await trading_strategy.scan_for_signals()
    return {"signals": signals}

@app.post("/api/trade")
async def execute_trade(signal: TradeSignal, background_tasks: BackgroundTasks):
    """Execute a trade based on signal"""
    success = await trading_strategy.open_position(signal.symbol, signal.signal_type)
    if success:
        return {"message": f"Successfully opened {signal.signal_type} position in {signal.symbol}"}
    else:
        return {"error": f"Failed to open {signal.signal_type} position in {signal.symbol}"}

@app.post("/api/check-exits")
async def check_exits():
    """Check and close positions that meet exit conditions"""
    closed_positions = []

    for symbol in list(trading_strategy.portfolio.positions.keys()):
        should_exit = await trading_strategy.check_exit_conditions(symbol)
        if should_exit:
            success = await trading_strategy.close_position(symbol)
            if success:
                closed_positions.append(symbol)

    return {"closed_positions": closed_positions, "count": len(closed_positions)}

@app.get("/api/symbols")
async def get_symbols():
    """Get available symbols for trading"""
    config_data = config.get_config()
    long_symbols = [coin + '/USDT' for coin in config_data.LONG_COINS]
    short_symbols = await data_provider.get_shortable_symbols()

    return {
        "long_symbols": long_symbols,
        "short_symbols": short_symbols[:50]  # Limit to top 50 for performance
    }

@app.get("/api/prices")
async def get_prices():
    """Get current prices for relevant symbols"""
    config_data = config.get_config()
    all_symbols = [coin + '/USDT' for coin in config_data.LONG_COINS]

    try:
        short_symbols = await data_provider.get_shortable_symbols()
        all_symbols.extend(short_symbols[:20])  # Get prices for top 20 shortable symbols
    except:
        pass

    prices = await data_provider.get_multiple_prices(all_symbols)

    return {"prices": prices}

@app.get("/api/chart-data/{symbol}")
async def get_chart_data(symbol: str, timeframe: str = "1h", limit: int = 100):
    """Get chart data for a symbol"""
    df = await data_provider.get_ohlcv(symbol, timeframe=timeframe, limit=limit)

    if df.empty:
        return {"error": f"No data available for {symbol}"}

    # Convert to list of dicts for JSON serialization
    data = []
    for idx, row in df.iterrows():
        data.append({
            "timestamp": idx.isoformat(),
            "open": float(row['open']),
            "high": float(row['high']),
            "low": float(row['low']),
            "close": float(row['close']),
            "volume": float(row['volume'])
        })

    return {"symbol": symbol, "data": data}

@app.post("/api/scan-and-trade")
async def scan_and_trade(background_tasks: BackgroundTasks):
    """Scan for signals and execute trades automatically"""
    signals = await trading_strategy.scan_for_signals()

    executed_trades = []
    for symbol, signal_type in signals.items():
        # Check if we already have a position in this symbol
        if symbol not in trading_strategy.portfolio.positions:
            success = await trading_strategy.open_position(symbol, signal_type)
            if success:
                executed_trades.append({"symbol": symbol, "type": signal_type})

    return {
        "signals_found": len(signals),
        "trades_executed": executed_trades,
        "count": len(executed_trades)
    }

@app.get("/api/equity-curve")
async def get_equity_curve(limit: int = 100):
    """Get equity curve data"""
    history = equity_tracker.get_history(limit=limit)
    statistics = equity_tracker.get_statistics()
    return {
        "history": history,
        "statistics": statistics
    }

@app.get("/api/trades/download")
async def download_trades():
    """Download all closed trades as CSV"""
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Symbol',
        'Type',
        'Entry Price',
        'Exit Price',
        'Quantity',
        'Leverage',
        'Entry Time',
        'Exit Time',
        'Duration (hours)',
        'P&L ($)',
        'P&L (%)',
        'Position Value',
        'Margin Used'
    ])
    
    # Write trade data
    for trade in trading_strategy.trades_history:
        # Calculate duration in hours
        duration_hours = 0
        if trade.exit_time and trade.entry_time:
            duration = trade.exit_time - trade.entry_time
            duration_hours = round(duration.total_seconds() / 3600, 2)
        
        # Calculate position value and margin
        position_value = trade.entry_price * trade.quantity
        margin_used = position_value / trade.leverage
        
        writer.writerow([
            trade.symbol,
            trade.position_type.value,
            round(trade.entry_price, 6),
            round(trade.exit_price, 6) if trade.exit_price else 'N/A',
            round(trade.quantity, 6),
            trade.leverage,
            trade.entry_time.strftime('%Y-%m-%d %H:%M:%S'),
            trade.exit_time.strftime('%Y-%m-%d %H:%M:%S') if trade.exit_time else 'N/A',
            duration_hours,
            round(trade.pnl, 2),
            round(trade.pnl_percentage, 2),
            round(position_value, 2),
            round(margin_used, 2)
        ])
    
    # Prepare the response
    output.seek(0)
    
    # Generate filename with current timestamp
    filename = f"trades_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "paper_trading": config.get_config().PAPER_TRADING,
        "trading_loop_running": trading_loop_running
    }

async def trading_loop():
    """Main trading loop that runs continuously"""
    global trading_loop_running
    trading_loop_running = True
    
    print("🤖 Trading loop started")
    print("📊 Priority-based trading: Entries based on signal freshness, exits on hourly candles")
    
    # Track last scan time to avoid too frequent scanning
    last_scan_time = None
    scan_interval = 300  # Scan every 5 minutes
    
    while trading_loop_running:
        try:
            current_time = datetime.now()
            
            # Should we scan for entries? (every 5 minutes)
            time_since_last_scan = None
            if last_scan_time:
                time_since_last_scan = (current_time - last_scan_time).total_seconds()
            
            should_scan = (last_scan_time is None or time_since_last_scan >= scan_interval)
            
            if should_scan:
                print(f"\n⏰ [{current_time.strftime('%Y-%m-%d %H:%M:%S')}] Running trading cycle...")
                
                # Step 1: Check exit conditions for open positions (only on hourly boundaries)
                current_hour = current_time.replace(minute=0, second=0, microsecond=0)
                is_hourly_boundary = current_time.minute >= 2 and current_time.minute <= 7  # 2-7 minutes past the hour
                
                if is_hourly_boundary and len(trading_strategy.portfolio.positions) > 0:
                    print("📊 Checking exit conditions for open positions (hourly check)...")
                    closed_count = 0
                    for symbol in list(trading_strategy.portfolio.positions.keys()):
                        should_exit = await trading_strategy.check_exit_conditions(symbol)
                        if should_exit:
                            success = await trading_strategy.close_position(symbol)
                            if success:
                                closed_count += 1
                                print(f"✅ Closed position: {symbol}")
                    
                    if closed_count > 0:
                        print(f"📉 Closed {closed_count} position(s)")
                    else:
                        print("✓ No positions to close")
                
                # Step 2: Scan for new signals and open positions (priority-based, anytime)
                print("🔍 Scanning for new trading signals...")
                signals = await trading_strategy.scan_for_signals()
                
                if signals:
                    print(f"📡 Found {len(signals)} signal(s)")
                    
                    opened_count = 0
                    for symbol, signal_type in signals.items():
                        if symbol not in trading_strategy.portfolio.positions:
                            success = await trading_strategy.open_position(symbol, signal_type)
                            if success:
                                opened_count += 1
                                print(f"✅ Opened {signal_type} position: {symbol}")
                    
                    if opened_count > 0:
                        print(f"📈 Opened {opened_count} new position(s)")
                else:
                    print("✓ No new signals found")
                
                # Step 3: Update portfolio metrics
                await trading_strategy.update_portfolio_value()
                print(f"💰 Portfolio value: ${trading_strategy.portfolio.total_value:.2f}")
                print(f"📊 Open positions: {len(trading_strategy.portfolio.positions)}")
                
                last_scan_time = current_time
                print(f"✓ Trading cycle complete. Next scan in {scan_interval/60:.0f} minutes")
            else:
                # Just update portfolio value
                await trading_strategy.update_portfolio_value()
                minutes_until_next = int((scan_interval - time_since_last_scan) / 60)
                if minutes_until_next > 0:
                    print(f"⏳ [{current_time.strftime('%H:%M:%S')}] Next scan in ~{minutes_until_next} minutes")
            
            # Check every minute
            await asyncio.sleep(60)
            
        except Exception as e:
            print(f"❌ Error in trading loop: {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(60)  # Wait 1 minute before retrying on error
    
    print("🛑 Trading loop stopped")

@app.on_event("startup")
async def startup_event():
    """Start the trading loop when the application starts"""
    global trading_loop_task
    trading_loop_task = asyncio.create_task(trading_loop())
    print("✅ Application started - Trading loop initiated")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the trading loop when the application shuts down"""
    global trading_loop_running, trading_loop_task
    trading_loop_running = False
    if trading_loop_task:
        trading_loop_task.cancel()
        try:
            await trading_loop_task
        except asyncio.CancelledError:
            pass
    print("✅ Application shutdown - Trading loop stopped")

@app.post("/api/start-trading")
async def start_trading():
    """Manually start the trading loop"""
    global trading_loop_running, trading_loop_task
    if not trading_loop_running:
        trading_loop_task = asyncio.create_task(trading_loop())
        return {"message": "Trading loop started"}
    return {"message": "Trading loop already running"}

@app.post("/api/stop-trading")
async def stop_trading():
    """Manually stop the trading loop"""
    global trading_loop_running
    if trading_loop_running:
        trading_loop_running = False
        return {"message": "Trading loop stopped"}
    return {"message": "Trading loop not running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
