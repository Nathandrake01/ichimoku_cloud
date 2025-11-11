import ccxt
import pandas as pd
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
from config import config

class DataProvider:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': config.get_config().BINANCE_API_KEY,
            'secret': config.get_config().BINANCE_SECRET_KEY,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
            }
        })

        # Cache for price data
        self.price_cache = {}
        self.cache_timestamp = {}

    async def get_ohlcv(self, symbol: str, timeframe: str = '1h',
                        limit: int = 100) -> pd.DataFrame:
        """
        Get OHLCV data for a symbol

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Timeframe (e.g., '1h', '4h', '1d')
            limit: Number of candles to fetch

        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Check cache first
            cache_key = f"{symbol}_{timeframe}_{limit}"
            if cache_key in self.price_cache:
                cache_time = self.cache_timestamp.get(cache_key, 0)
                if time.time() - cache_time < 60:  # Cache for 1 minute
                    return self.price_cache[cache_key].copy()

            # Fetch data from exchange
            ohlcv = await asyncio.get_event_loop().run_in_executor(
                None, self.exchange.fetch_ohlcv, symbol, timeframe, None, limit
            )

            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            # Convert to numeric
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Cache the data
            self.price_cache[cache_key] = df.copy()
            self.cache_timestamp[cache_key] = time.time()

            return df

        except Exception as e:
            print(f"Error fetching OHLCV for {symbol}: {e}")
            return pd.DataFrame()

    async def get_24h_volume(self, symbol: str) -> float:
        """
        Get 24h volume for a symbol in USD

        Args:
            symbol: Trading pair

        Returns:
            24h volume in USD
        """
        try:
            ticker = await asyncio.get_event_loop().run_in_executor(
                None, self.exchange.fetch_ticker, symbol
            )

            if 'quoteVolume' in ticker:
                return float(ticker['quoteVolume'])
            else:
                return 0.0

        except Exception as e:
            print(f"Error fetching volume for {symbol}: {e}")
            return 0.0

    async def get_available_symbols(self) -> List[str]:
        """
        Get list of available trading symbols with decent volume

        Returns:
            List of symbols with USDT pairs
        """
        try:
            markets = await asyncio.get_event_loop().run_in_executor(
                None, self.exchange.load_markets
            )

            symbols = []
            for symbol, market in markets.items():
                if (market['active'] and
                    market['type'] == 'spot' and
                    symbol.endswith('/USDT') and
                    not symbol.startswith(('BUSD/', 'USDC/', 'TUSD/', 'USDP/'))):

                    # Filter out leveraged tokens and stable coins
                    base = symbol.split('/')[0]
                    if not any(stable in base for stable in ['USD', 'BUSD', 'USDC', 'TUSD', 'USDP', 'DAI']):
                        symbols.append(symbol)

            return symbols

        except Exception as e:
            print(f"Error fetching symbols: {e}")
            return []

    async def get_shortable_symbols(self, min_volume: float = 1000000, limit: int = 100) -> List[str]:
        """
        Get symbols that can be shorted (not in long-only list) with decent volume,
        sorted by volume (highest first)

        Args:
            min_volume: Minimum 24h volume in USD
            limit: Maximum number of symbols to return

        Returns:
            List of shortable symbols sorted by volume
        """
        config_data = config.get_config()
        long_coins = [coin + '/USDT' for coin in config_data.LONG_COINS]

        all_symbols = await self.get_available_symbols()
        symbol_volumes = []

        # Get volumes for all symbols (this might be slow, but necessary for sorting)
        for symbol in all_symbols[:200]:  # Limit to first 200 to avoid too many API calls
            if symbol not in long_coins:
                try:
                    volume = await self.get_24h_volume(symbol)
                    if volume >= min_volume:
                        symbol_volumes.append((symbol, volume))
                except:
                    continue  # Skip symbols that fail

        # Sort by volume (highest first) and return top symbols
        symbol_volumes.sort(key=lambda x: x[1], reverse=True)
        shortable_symbols = [symbol for symbol, volume in symbol_volumes[:limit]]

        return shortable_symbols

    async def get_current_price(self, symbol: str) -> float:
        """
        Get current price for a symbol

        Args:
            symbol: Trading pair

        Returns:
            Current price
        """
        try:
            ticker = await asyncio.get_event_loop().run_in_executor(
                None, self.exchange.fetch_ticker, symbol
            )
            return float(ticker['last'])
        except Exception as e:
            print(f"Error fetching current price for {symbol}: {e}")
            return 0.0

    async def get_multiple_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Get current prices for multiple symbols

        Args:
            symbols: List of trading pairs

        Returns:
            Dictionary of symbol -> price
        """
        prices = {}
        for symbol in symbols:
            price = await self.get_current_price(symbol)
            if price > 0:
                prices[symbol] = price
        return prices

# Global data provider instance
data_provider = DataProvider()
