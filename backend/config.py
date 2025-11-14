from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class TradingConfig(BaseModel):
    # Long only coins (top 10-15 by market cap/volume)
    LONG_COINS: List[str] = [
        "BTC", "ETH", "BNB", "SOL", "XRP", 
        "ADA", "AVAX", "DOT", "MATIC", "LINK",
        "UNI", "ATOM", "LTC", "NEAR", "HYPE"
    ]

    # Risk management
    INITIAL_PORTFOLIO_VALUE: float = 10000.0  # USD
    CURRENT_PORTFOLIO_VALUE: float = 10000.0  # USD (can be reduced for risk management)

    # Position limits - ALL-IN STRATEGY
    MAX_TOTAL_POSITIONS: int = 10  # Maximum 10 positions total (can be all long, all short, or mix)
    POSITION_SIZE: float = 1000.0  # Fixed $1000 per position

    # Leverage settings
    LONG_LEVERAGE: float = 1.0  # Can be increased for long bias
    SHORT_LEVERAGE: float = 1.0  # Can be increased for short bias

    # Position allocation - ALL-IN STRATEGY (no 50/50 split)
    # Positions allocated based on signal strength ranking across all symbols

    # Ichimoku settings
    TENKAN_PERIOD: int = 9
    KIJUN_PERIOD: int = 26
    SENKOU_PERIOD: int = 52
    CHIKOU_PERIOD: int = 26

    # Trading settings
    TIMEFRAME: str = "1h"
    MIN_VOLUME_THRESHOLD: float = 1000000  # Minimum 24h volume in USD

    # API settings
    BINANCE_API_KEY: Optional[str] = os.getenv("BINANCE_API_KEY")
    BINANCE_SECRET_KEY: Optional[str] = os.getenv("BINANCE_SECRET_KEY")
    PAPER_TRADING: bool = True

    # Stop loss settings
    STOP_LOSS_BELOW_KIJUN: bool = True
    STOP_LOSS_TWO_CANDLES_IN_CLOUD: bool = True

    # Target settings
    TRAIL_BEHIND_CONVERSION: bool = True
    CONVERSION_KIJUN_CROSS_UNDER: bool = True

class Config:
    def __init__(self):
        self._config = TradingConfig()

    def get_config(self) -> TradingConfig:
        return self._config

    def update_portfolio_value(self, new_value: float):
        """Reduce portfolio value for risk management"""
        if new_value <= self._config.CURRENT_PORTFOLIO_VALUE:
            self._config.CURRENT_PORTFOLIO_VALUE = new_value
            print(f"Portfolio value updated to ${new_value}")

    def update_long_leverage(self, leverage: float):
        """Update long leverage"""
        if 1.0 <= leverage <= 10.0:  # Reasonable limits
            self._config.LONG_LEVERAGE = leverage
            print(f"Long leverage updated to {leverage}x")
        else:
            raise ValueError("Long leverage must be between 1.0 and 10.0")
    
    def update_short_leverage(self, leverage: float):
        """Update short leverage"""
        if 1.0 <= leverage <= 10.0:  # Reasonable limits
            self._config.SHORT_LEVERAGE = leverage
            print(f"Short leverage updated to {leverage}x")
        else:
            raise ValueError("Short leverage must be between 1.0 and 10.0")

# Global config instance
config = Config()
