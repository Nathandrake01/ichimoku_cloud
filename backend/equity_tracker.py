import json
import os
from datetime import datetime
from typing import List, Dict

class EquityTracker:
    def __init__(self, filename: str = "equity_history.json"):
        self.filename = filename
        self.equity_history: List[Dict] = []
        self.load_history()

    def load_history(self):
        """Load equity history from file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    self.equity_history = json.load(f)
            except Exception as e:
                print(f"Error loading equity history: {e}")
                self.equity_history = []

    def save_history(self):
        """Save equity history to file"""
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.equity_history, f, indent=2)
        except Exception as e:
            print(f"Error saving equity history: {e}")

    def add_snapshot(self, total_value: float, realized_pnl: float, unrealized_pnl: float, 
                     open_positions: int, drawdown: float,
                     long_pnl: float = 0.0, short_pnl: float = 0.0,
                     long_realized_pnl: float = 0.0, short_realized_pnl: float = 0.0,
                     long_unrealized_pnl: float = 0.0, short_unrealized_pnl: float = 0.0,
                     long_drawdown: float = 0.0, short_drawdown: float = 0.0,
                     long_positions: int = 0, short_positions: int = 0):
        """Add a new equity snapshot"""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'total_value': round(total_value, 2),
            'realized_pnl': round(realized_pnl, 2),
            'unrealized_pnl': round(unrealized_pnl, 2),
            'total_pnl': round(realized_pnl + unrealized_pnl, 2),
            'open_positions': open_positions,
            'drawdown': round(drawdown, 2),
            # Long position metrics
            'long_pnl': round(long_pnl, 2),
            'long_realized_pnl': round(long_realized_pnl, 2),
            'long_unrealized_pnl': round(long_unrealized_pnl, 2),
            'long_drawdown': round(long_drawdown, 2),
            'long_positions': long_positions,
            # Short position metrics
            'short_pnl': round(short_pnl, 2),
            'short_realized_pnl': round(short_realized_pnl, 2),
            'short_unrealized_pnl': round(short_unrealized_pnl, 2),
            'short_drawdown': round(short_drawdown, 2),
            'short_positions': short_positions
        }
        
        self.equity_history.append(snapshot)
        
        # Keep only last 1000 snapshots to avoid file getting too large
        if len(self.equity_history) > 1000:
            self.equity_history = self.equity_history[-1000:]
        
        self.save_history()

    def get_history(self, limit: int = 100) -> List[Dict]:
        """Get recent equity history"""
        return self.equity_history[-limit:]

    def get_statistics(self) -> Dict:
        """Calculate statistics from equity history"""
        if not self.equity_history:
            return {
                'total_snapshots': 0,
                'max_value': 0,
                'min_value': 0,
                'current_value': 0,
                'max_drawdown': 0,
                'total_return': 0,
                'total_return_pct': 0
            }

        values = [s['total_value'] for s in self.equity_history]
        initial_value = self.equity_history[0]['total_value']
        current_value = self.equity_history[-1]['total_value']
        
        return {
            'total_snapshots': len(self.equity_history),
            'max_value': round(max(values), 2),
            'min_value': round(min(values), 2),
            'current_value': round(current_value, 2),
            'max_drawdown': round(max([s['drawdown'] for s in self.equity_history]), 2),
            'total_return': round(current_value - initial_value, 2),
            'total_return_pct': round(((current_value - initial_value) / initial_value) * 100, 2) if initial_value > 0 else 0
        }

# Global equity tracker instance
equity_tracker = EquityTracker()

