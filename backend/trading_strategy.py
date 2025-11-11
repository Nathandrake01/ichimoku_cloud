import pandas as pd
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import os

from config import config
from ichimoku import IchimokuCloud
from data_provider import data_provider
from equity_tracker import equity_tracker

class PositionType(Enum):
    LONG = "long"
    SHORT = "short"

class PositionStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"

@dataclass
class Position:
    symbol: str
    position_type: PositionType
    entry_price: float
    quantity: float
    leverage: float
    entry_time: datetime
    status: PositionStatus = PositionStatus.OPEN
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    pnl: float = 0.0
    pnl_percentage: float = 0.0

@dataclass
class Portfolio:
    total_value: float
    available_cash: float
    positions: Dict[str, Position]
    total_pnl: float
    total_pnl_percentage: float
    peak_value: float
    drawdown: float

class TradingStrategy:
    def __init__(self):
        self.ichimoku = IchimokuCloud()
        self.portfolio = Portfolio(
            total_value=config.get_config().CURRENT_PORTFOLIO_VALUE,
            available_cash=config.get_config().CURRENT_PORTFOLIO_VALUE,
            positions={},
            total_pnl=0.0,
            total_pnl_percentage=0.0,
            peak_value=config.get_config().CURRENT_PORTFOLIO_VALUE,
            drawdown=0.0
        )
        self.trades_history: List[Position] = []
        self.positions_file = "positions.json"
        # Track last action timestamp per symbol to prevent duplicate trades on same candle
        self.last_action_timestamp: Dict[str, datetime] = {}
        # Track startup time for warm-up period
        self.startup_time = datetime.now()
        print(f"🚀 Trading strategy initialized at {self.startup_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("⏳ Warm-up period: 1 hour (no trades until bot observes one complete cycle)")
        self.load_positions()

    def load_positions(self):
        """Load positions from file"""
        if os.path.exists(self.positions_file):
            try:
                with open(self.positions_file, 'r') as f:
                    data = json.load(f)
                    for pos_data in data.get('positions', []):
                        pos = Position(
                            symbol=pos_data['symbol'],
                            position_type=PositionType(pos_data['position_type']),
                            entry_price=pos_data['entry_price'],
                            quantity=pos_data['quantity'],
                            leverage=pos_data['leverage'],
                            entry_time=datetime.fromisoformat(pos_data['entry_time']),
                            status=PositionStatus(pos_data['status']),
                            exit_price=pos_data.get('exit_price'),
                            exit_time=datetime.fromisoformat(pos_data['exit_time']) if pos_data.get('exit_time') else None,
                            pnl=pos_data.get('pnl', 0.0),
                            pnl_percentage=pos_data.get('pnl_percentage', 0.0)
                        )
                        if pos.status == PositionStatus.OPEN:
                            self.portfolio.positions[pos.symbol] = pos
                        else:
                            self.trades_history.append(pos)
                
                # Recalculate available cash based on loaded positions and trades
                # Start with initial portfolio value
                self.portfolio.available_cash = config.get_config().CURRENT_PORTFOLIO_VALUE
                
                # Subtract margin used by open positions
                for pos in self.portfolio.positions.values():
                    margin_used = (pos.entry_price * pos.quantity) / pos.leverage
                    self.portfolio.available_cash -= margin_used
                
                # Add/subtract realized P&L from closed trades
                realized_pnl = sum(trade.pnl for trade in self.trades_history)
                self.portfolio.total_pnl = realized_pnl
                self.portfolio.available_cash += realized_pnl
                
                print(f"Loaded {len(self.portfolio.positions)} open positions and {len(self.trades_history)} closed trades")
                print(f"Realized P&L: ${realized_pnl:.2f}")
                print(f"Available Cash: ${self.portfolio.available_cash:.2f}")
                
            except Exception as e:
                print(f"Error loading positions: {e}")

    def save_positions(self):
        """Save positions to file"""
        try:
            positions_data = []
            for pos in list(self.portfolio.positions.values()) + self.trades_history:
                pos_dict = {
                    'symbol': pos.symbol,
                    'position_type': pos.position_type.value,
                    'entry_price': pos.entry_price,
                    'quantity': pos.quantity,
                    'leverage': pos.leverage,
                    'entry_time': pos.entry_time.isoformat(),
                    'status': pos.status.value,
                    'pnl': pos.pnl,
                    'pnl_percentage': pos.pnl_percentage
                }
                if pos.exit_price:
                    pos_dict['exit_price'] = pos.exit_price
                if pos.exit_time:
                    pos_dict['exit_time'] = pos.exit_time.isoformat()
                positions_data.append(pos_dict)

            with open(self.positions_file, 'w') as f:
                json.dump({'positions': positions_data}, f, indent=2)
        except Exception as e:
            print(f"Error saving positions: {e}")

    async def scan_for_signals(self) -> Dict[str, str]:
        """
        Scan all eligible symbols for trading signals with priority system
        
        Priority:
        1. Fresh signals (transition from False to True) - Best entries
        2. Recent signals (appeared in last few hours) - Good entries
        3. Older signals (if slots need filling) - Acceptable entries

        Returns:
            Dictionary of symbol -> signal_type ('long', 'short', or None)
        """
        config_data = config.get_config()

        # Get long-eligible symbols
        long_symbols = [coin + '/USDT' for coin in config_data.LONG_COINS]

        # Get short-eligible symbols (limit to top 50 for performance)
        short_symbols = await data_provider.get_shortable_symbols(limit=50)

        all_symbols = long_symbols + short_symbols

        # Collect all signals with their "freshness" score
        signal_candidates = []
        
        for symbol in all_symbols:
            signal_info = await self.check_signal_with_priority(symbol)
            if signal_info:
                signal_candidates.append(signal_info)

        # Sort by priority: fresh signals first, then by recency
        signal_candidates.sort(key=lambda x: (x['priority'], -x['hours_since_signal']))
        
        # Log signal priorities
        if signal_candidates:
            print(f"\n📊 Signal Priority Ranking:")
            for i, candidate in enumerate(signal_candidates[:10], 1):  # Show top 10
                priority_label = {0: "🆕 FRESH", 1: "⏰ RECENT", 2: "⏳ OLDER"}[candidate['priority']]
                print(f"  {i}. {candidate['symbol']}: {priority_label} ({candidate['hours_since_signal']}h ago) - {candidate['signal_type'].upper()}")
        
        # Convert to simple dict for compatibility
        signals = {}
        for candidate in signal_candidates:
            signals[candidate['symbol']] = candidate['signal_type']

        return signals

    async def check_signal_with_priority(self, symbol: str) -> Optional[Dict]:
        """
        Check for trading signal with priority scoring
        
        Returns dict with:
        - symbol: str
        - signal_type: 'long' or 'short'
        - priority: int (0=fresh, 1=recent, 2=older)
        - hours_since_signal: float
        - signal_first_appeared: int (candle index where signal first appeared)
        """
        try:
            # Warm-up period check
            time_since_startup = (datetime.now() - self.startup_time).total_seconds()
            if time_since_startup < 3600:
                return None

            # Get OHLCV data
            df = await data_provider.get_ohlcv(symbol, timeframe='1h', limit=100)

            if df.empty or len(df) < 52:
                return None

            # Filter out forming candle
            last_timestamp = df.index[-1]
            current_time = datetime.now()
            
            if last_timestamp.hour == current_time.hour and last_timestamp.date() == current_time.date():
                df = df.iloc[:-1]
            
            if df.empty or len(df) < 52:
                return None

            # Calculate Ichimoku indicators
            df = self.ichimoku.calculate(df)
            df = self.ichimoku.get_signals(df)

            # Check current signal status
            current_long = df['long_signal'].iloc[-1]
            current_short = df['short_signal'].iloc[-1]

            # Determine which signal type to check
            signal_type = None
            current_signal = False
            
            if current_long and symbol.endswith('/USDT'):
                base_coin = symbol.replace('/USDT', '')
                if base_coin in config.get_config().LONG_COINS:
                    signal_type = 'long'
                    current_signal = True
            elif current_short:
                signal_type = 'short'
                current_signal = True

            if not current_signal:
                return None

            # Find when signal first appeared (look back through candles)
            signal_column = 'long_signal' if signal_type == 'long' else 'short_signal'
            hours_since_signal = 0
            
            # Look back to find where signal first appeared
            for i in range(len(df) - 1, -1, -1):
                if df[signal_column].iloc[i]:
                    hours_since_signal += 1
                else:
                    break  # Found where signal first appeared

            # Determine priority
            # 0 = Fresh (just appeared, 1 hour old)
            # 1 = Recent (2-4 hours old)
            # 2 = Older (5+ hours old)
            if hours_since_signal == 1:
                priority = 0  # Fresh signal
            elif hours_since_signal <= 4:
                priority = 1  # Recent signal
            else:
                priority = 2  # Older signal

            return {
                'symbol': symbol,
                'signal_type': signal_type,
                'priority': priority,
                'hours_since_signal': hours_since_signal,
                'signal_first_appeared': hours_since_signal
            }

        except Exception as e:
            print(f"Error checking signal for {symbol}: {e}")
            return None

    async def check_signal(self, symbol: str) -> Optional[str]:
        """
        Check for trading signal on a specific symbol
        Only returns a signal if it JUST APPEARED (transition detection)
        This ensures we catch fresh breakouts, not late moves

        Args:
            symbol: Trading pair

        Returns:
            'long', 'short', or None
        """
        try:
            # Warm-up period: Don't trade in first hour after startup
            # This ensures we have proper historical context
            time_since_startup = (datetime.now() - self.startup_time).total_seconds()
            if time_since_startup < 3600:  # 1 hour = 3600 seconds
                minutes_remaining = int((3600 - time_since_startup) / 60)
                if minutes_remaining % 10 == 0:  # Log every 10 minutes
                    print(f"⏳ Warm-up period: {minutes_remaining} minutes remaining")
                return None

            # Get OHLCV data
            df = await data_provider.get_ohlcv(symbol, timeframe='1h', limit=100)

            if df.empty or len(df) < 52:  # Need enough data for Ichimoku
                return None

            # Only use completed candles - exclude the last candle which may still be forming
            # Check if the last candle is aligned to clock hour
            last_timestamp = df.index[-1]
            current_time = datetime.now()
            
            # If last candle's timestamp is within the current hour, it's still forming - exclude it
            if last_timestamp.hour == current_time.hour and last_timestamp.date() == current_time.date():
                df = df.iloc[:-1]  # Exclude the forming candle
            
            if df.empty or len(df) < 52:
                return None

            # Need at least 2 candles to detect signal transition
            if len(df) < 2:
                return None

            # Calculate Ichimoku indicators
            df = self.ichimoku.calculate(df)
            df = self.ichimoku.get_signals(df)

            # TRANSITION DETECTION: Only enter if signal JUST APPEARED
            # This catches fresh breakouts and avoids late entries
            
            # Check for LONG signal transition (False → True)
            current_long_signal = df['long_signal'].iloc[-1]
            previous_long_signal = df['long_signal'].iloc[-2]
            long_signal_just_appeared = current_long_signal and not previous_long_signal
            
            if long_signal_just_appeared and symbol.endswith('/USDT'):
                base_coin = symbol.replace('/USDT', '')
                if base_coin in config.get_config().LONG_COINS:
                    print(f"🆕 Fresh LONG signal detected for {symbol}")
                    print(f"   Previous candle: signal=False, Current candle: signal=True")
                    return 'long'

            # Check for SHORT signal transition (False → True)
            current_short_signal = df['short_signal'].iloc[-1]
            previous_short_signal = df['short_signal'].iloc[-2]
            short_signal_just_appeared = current_short_signal and not previous_short_signal
            
            if short_signal_just_appeared:
                print(f"🆕 Fresh SHORT signal detected for {symbol}")
                print(f"   Previous candle: signal=False, Current candle: signal=True")
                return 'short'

            return None

        except Exception as e:
            print(f"Error checking signal for {symbol}: {e}")
            return None

    def calculate_position_size(self, symbol: str, signal_type: str, entry_price: float) -> Tuple[float, float]:
        """
        Calculate position size based on fixed allocation per position

        Logic:
        - Split capital 50/50 between long and short
        - Long: $50 total ÷ 4 positions = $12.5 per position × 2x leverage = $25
        - Short: $50 total ÷ 4 positions = $12.5 per position × 1x leverage = $12.5

        Args:
            symbol: Trading pair
            signal_type: 'long' or 'short'
            entry_price: Entry price

        Returns:
            Tuple of (quantity, leverage)
        """
        config_data = config.get_config()

        # Split capital 50/50 between long and short
        long_allocation = self.portfolio.available_cash * 0.5
        short_allocation = self.portfolio.available_cash * 0.5

        if signal_type == 'long':
            leverage = config_data.LONG_LEVERAGE
            # Long: $50 total ÷ 4 positions = $12.5 per position
            position_amount = long_allocation / config_data.MAX_LONG_POSITIONS
        else:
            leverage = config_data.SHORT_LEVERAGE
            # Short: $50 total ÷ 4 positions = $12.5 per position
            position_amount = short_allocation / config_data.MAX_SHORT_POSITIONS

        # Calculate quantity based on position amount and leverage
        quantity = (position_amount * leverage) / entry_price

        return quantity, leverage

    async def open_position(self, symbol: str, signal_type: str) -> bool:
        """
        Open a new position

        Args:
            symbol: Trading pair
            signal_type: 'long' or 'short'

        Returns:
            True if position opened successfully
        """
        if symbol in self.portfolio.positions:
            return False  # Already have position in this symbol

        # Check if we already acted on this symbol in the current hour
        try:
            df = await data_provider.get_ohlcv(symbol, timeframe='1h', limit=2)
            if not df.empty:
                last_completed_candle = df.index[-2] if len(df) >= 2 else df.index[-1]
                
                # Check if we already acted on this candle
                if symbol in self.last_action_timestamp:
                    last_action = self.last_action_timestamp[symbol]
                    # Normalize both to hour precision for comparison
                    if last_action.replace(minute=0, second=0, microsecond=0) == last_completed_candle.replace(minute=0, second=0, microsecond=0):
                        print(f"Already acted on {symbol} for candle {last_completed_candle}, skipping duplicate entry")
                        return False
        except:
            pass  # If we can't check, proceed anyway

        # Check position limits
        config_data = config.get_config()
        current_long_positions = sum(1 for pos in self.portfolio.positions.values()
                                   if pos.position_type == PositionType.LONG)
        current_short_positions = sum(1 for pos in self.portfolio.positions.values()
                                    if pos.position_type == PositionType.SHORT)

        if signal_type == 'long' and current_long_positions >= config_data.MAX_LONG_POSITIONS:
            return False  # Already at max long positions

        if signal_type == 'short' and current_short_positions >= config_data.MAX_SHORT_POSITIONS:
            return False  # Already at max short positions

        try:
            entry_price = await data_provider.get_current_price(symbol)
            if entry_price <= 0:
                return False

            quantity, leverage = self.calculate_position_size(symbol, signal_type, entry_price)

            if quantity <= 0:
                return False

            position = Position(
                symbol=symbol,
                position_type=PositionType(signal_type),
                entry_price=entry_price,
                quantity=quantity,
                leverage=leverage,
                entry_time=datetime.now()
            )

            self.portfolio.positions[symbol] = position

            # Update available cash
            position_value = (quantity * entry_price) / leverage
            self.portfolio.available_cash -= position_value

            # Record the action timestamp
            self.last_action_timestamp[symbol] = datetime.now()

            self.save_positions()
            print(f"Opened {signal_type} position in {symbol} at ${entry_price:.4f}")
            return True

        except Exception as e:
            print(f"Error opening position for {symbol}: {e}")
            return False

    async def check_exit_conditions(self, symbol: str) -> bool:
        """
        Check if position should be exited based on stop loss or target conditions

        Args:
            symbol: Trading pair

        Returns:
            True if position should be closed
        """
        if symbol not in self.portfolio.positions:
            return False

        position = self.portfolio.positions[symbol]

        try:
            # Get recent OHLCV data
            df = await data_provider.get_ohlcv(symbol, timeframe='1h', limit=50)

            if df.empty:
                return False

            # Only use completed candles - exclude the last candle which may still be forming
            last_timestamp = df.index[-1]
            current_time = datetime.now()
            
            # If last candle's timestamp is within the current hour, it's still forming - exclude it
            if last_timestamp.hour == current_time.hour and last_timestamp.date() == current_time.date():
                df = df.iloc[:-1]  # Exclude the forming candle
            
            if df.empty:
                return False

            # Calculate Ichimoku indicators
            df = self.ichimoku.calculate(df)

            # Check stop loss on the last COMPLETED candle
            stop_loss_triggered = self.ichimoku.check_stop_loss(df, position.position_type.value).iloc[-1]

            # Check target on the last COMPLETED candle
            target_reached = self.ichimoku.check_target(df, position.position_type.value).iloc[-1]

            return stop_loss_triggered or target_reached

        except Exception as e:
            print(f"Error checking exit conditions for {symbol}: {e}")
            return False

    async def close_position(self, symbol: str) -> bool:
        """
        Close an existing position

        Args:
            symbol: Trading pair

        Returns:
            True if position closed successfully
        """
        if symbol not in self.portfolio.positions:
            return False

        position = self.portfolio.positions[symbol]

        try:
            exit_price = await data_provider.get_current_price(symbol)
            if exit_price <= 0:
                return False

            position.exit_price = exit_price
            position.exit_time = datetime.now()

            # Calculate P&L
            if position.position_type == PositionType.LONG:
                position.pnl = (exit_price - position.entry_price) * position.quantity * position.leverage
            else:  # SHORT
                position.pnl = (position.entry_price - exit_price) * position.quantity * position.leverage

            position.pnl_percentage = (position.pnl / (position.entry_price * position.quantity)) * 100

            # Update portfolio
            position_value = (position.quantity * position.entry_price) / position.leverage
            self.portfolio.available_cash += position_value + position.pnl
            self.portfolio.total_pnl += position.pnl

            position.status = PositionStatus.CLOSED
            self.trades_history.append(position)
            del self.portfolio.positions[symbol]

            # Record the action timestamp to prevent re-entry on same candle
            self.last_action_timestamp[symbol] = datetime.now()

            self.save_positions()
            print(f"Closed {position.position_type.value} position in {symbol} at ${exit_price:.4f}, P&L: ${position.pnl:.2f}")
            return True

        except Exception as e:
            print(f"Error closing position for {symbol}: {e}")
            return False

    async def update_portfolio_value(self):
        """Update total portfolio value and calculate metrics with current prices"""
        unrealized_pnl = 0.0
        locked_capital = 0.0

        # Calculate unrealized P&L and locked capital from open positions using current prices
        for symbol, position in self.portfolio.positions.items():
            try:
                current_price = await data_provider.get_current_price(symbol)
                
                # Locked capital = entry price * quantity / leverage (the actual capital we used)
                locked_capital += (position.entry_price * position.quantity) / position.leverage
                
                if position.position_type == PositionType.LONG:
                    # Long: profit when price goes up
                    price_diff = current_price - position.entry_price
                    unrealized_pnl += price_diff * position.quantity
                else:
                    # Short: profit when price goes down
                    price_diff = position.entry_price - current_price
                    unrealized_pnl += price_diff * position.quantity
            except:
                continue  # Skip if can't get price

        # Total value = available cash + locked capital + unrealized P&L
        # This ensures that opening a position doesn't change total value (except for P&L)
        self.portfolio.total_value = self.portfolio.available_cash + locked_capital + unrealized_pnl
        
        # Total P&L = realized P&L + unrealized P&L
        total_pnl = self.portfolio.total_pnl + unrealized_pnl
        self.portfolio.total_pnl_percentage = (total_pnl / config.get_config().INITIAL_PORTFOLIO_VALUE) * 100

        # Update peak value and drawdown
        if self.portfolio.total_value > self.portfolio.peak_value:
            self.portfolio.peak_value = self.portfolio.total_value
            self.portfolio.drawdown = 0.0
        else:
            self.portfolio.drawdown = ((self.portfolio.peak_value - self.portfolio.total_value) / self.portfolio.peak_value) * 100

    async def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary for API"""
        await self.update_portfolio_value()

        # Calculate realized and unrealized P&L
        unrealized_pnl = 0.0
        for symbol, position in self.portfolio.positions.items():
            try:
                current_price = await data_provider.get_current_price(symbol)
                if position.position_type == PositionType.LONG:
                    price_diff = current_price - position.entry_price
                    unrealized_pnl += price_diff * position.quantity
                else:
                    price_diff = position.entry_price - current_price
                    unrealized_pnl += price_diff * position.quantity
            except:
                continue

        # Add snapshot to equity tracker
        equity_tracker.add_snapshot(
            total_value=self.portfolio.total_value,
            realized_pnl=self.portfolio.total_pnl,
            unrealized_pnl=unrealized_pnl,
            open_positions=len(self.portfolio.positions),
            drawdown=self.portfolio.drawdown
        )

        return {
            'total_value': round(self.portfolio.total_value, 2),
            'available_cash': round(self.portfolio.available_cash, 2),
            'total_pnl': round(self.portfolio.total_pnl + unrealized_pnl, 2),
            'realized_pnl': round(self.portfolio.total_pnl, 2),
            'unrealized_pnl': round(unrealized_pnl, 2),
            'total_pnl_percentage': round(self.portfolio.total_pnl_percentage, 2),
            'peak_value': round(self.portfolio.peak_value, 2),
            'drawdown': round(self.portfolio.drawdown, 2),
            'open_positions': len(self.portfolio.positions),
            'total_trades': len(self.trades_history)
        }

    async def get_positions(self) -> List[Dict]:
        """Get all positions for API with current prices and unrealized P&L"""
        positions = []
        
        # Add open positions with current unrealized P&L
        for pos in self.portfolio.positions.values():
            try:
                current_price = await data_provider.get_current_price(pos.symbol)
                
                # Calculate unrealized P&L
                if pos.position_type == PositionType.LONG:
                    price_diff = current_price - pos.entry_price
                    unrealized_pnl = price_diff * pos.quantity
                else:
                    price_diff = pos.entry_price - current_price
                    unrealized_pnl = price_diff * pos.quantity
                
                unrealized_pnl_pct = (unrealized_pnl / (pos.entry_price * pos.quantity)) * 100
                
                pos_dict = {
                    'symbol': pos.symbol,
                    'type': pos.position_type.value,
                    'entry_price': round(pos.entry_price, 4),
                    'current_price': round(current_price, 4),
                    'quantity': round(pos.quantity, 6),
                    'leverage': pos.leverage,
                    'entry_time': pos.entry_time.isoformat(),
                    'status': pos.status.value,
                    'pnl': round(unrealized_pnl, 2),
                    'pnl_percentage': round(unrealized_pnl_pct, 2)
                }
                positions.append(pos_dict)
            except:
                continue
        
        # Add closed trades (last 20)
        for pos in self.trades_history[-20:]:
            pos_dict = {
                'symbol': pos.symbol,
                'type': pos.position_type.value,
                'entry_price': round(pos.entry_price, 4),
                'quantity': round(pos.quantity, 6),
                'leverage': pos.leverage,
                'entry_time': pos.entry_time.isoformat(),
                'status': pos.status.value,
                'pnl': round(pos.pnl, 2),
                'pnl_percentage': round(pos.pnl_percentage, 2)
            }
            if pos.exit_price:
                pos_dict['exit_price'] = round(pos.exit_price, 4)
                pos_dict['current_price'] = round(pos.exit_price, 4)
            if pos.exit_time:
                pos_dict['exit_time'] = pos.exit_time.isoformat()
            positions.append(pos_dict)
            
        return positions

# Global strategy instance
trading_strategy = TradingStrategy()
