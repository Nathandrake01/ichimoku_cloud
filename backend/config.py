from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class TradingConfig(BaseModel):
    # Long only coins
    LONG_COINS: List[str] = ["HYPE", "BNB", "SOL", "LINK"]

    # Risk management
    INITIAL_PORTFOLIO_VALUE: float = 10000.0  # USD
    CURRENT_PORTFOLIO_VALUE: float = 10000.0  # USD (can be reduced for risk management)

    # Position limits
    MAX_LONG_POSITIONS: int = 4  # Maximum 4 long positions
    MAX_SHORT_POSITIONS: int = 4  # Maximum 4 short positions

    # Leverage settings
    LONG_LEVERAGE: float = 2.0
    SHORT_LEVERAGE: float = 1.0

    # Position allocation
    LONG_ALLOCATION: float = 0.5  # 50% of capital for longs
    SHORT_ALLOCATION: float = 0.5  # 50% of capital for shorts

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

# Global config instance
config = Config()
