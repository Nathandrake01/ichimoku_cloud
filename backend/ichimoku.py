import pandas as pd
import numpy as np
from typing import Tuple, Optional

class IchimokuCloud:
    def __init__(self, tenkan_period: int = 9, kijun_period: int = 26,
                 senkou_period: int = 52, chikou_period: int = 26):
        self.tenkan_period = tenkan_period
        self.kijun_period = kijun_period
        self.senkou_period = senkou_period
        self.chikou_period = chikou_period

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Ichimoku Cloud indicators

        Args:
            df: DataFrame with OHLC data (open, high, low, close, volume)

        Returns:
            DataFrame with Ichimoku indicators added
        """
        df = df.copy()

        # Tenkan-sen (Conversion Line): (highest high + lowest low) / 2 for the past 9 periods
        df['tenkan_high'] = df['high'].rolling(window=self.tenkan_period).max()
        df['tenkan_low'] = df['low'].rolling(window=self.tenkan_period).min()
        df['tenkan_sen'] = (df['tenkan_high'] + df['tenkan_low']) / 2

        # Kijun-sen (Base Line): (highest high + lowest low) / 2 for the past 26 periods
        df['kijun_high'] = df['high'].rolling(window=self.kijun_period).max()
        df['kijun_low'] = df['low'].rolling(window=self.kijun_period).min()
        df['kijun_sen'] = (df['kijun_high'] + df['kijun_low']) / 2

        # Senkou Span A (Leading Span A): (Tenkan-sen + Kijun-sen) / 2, plotted 26 periods ahead
        df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(self.kijun_period)

        # Senkou Span B (Leading Span B): (highest high + lowest low) / 2 for the past 52 periods, plotted 26 periods ahead
        df['senkou_high'] = df['high'].rolling(window=self.senkou_period).max()
        df['senkou_low'] = df['low'].rolling(window=self.senkou_period).min()
        df['senkou_span_b'] = ((df['senkou_high'] + df['senkou_low']) / 2).shift(self.kijun_period)

        # Chikou Span (Lagging Span): Current close plotted 26 periods back
        df['chikou_span'] = df['close'].shift(self.chikou_period)

        # Cloud boundaries
        df['cloud_top'] = df[['senkou_span_a', 'senkou_span_b']].max(axis=1)
        df['cloud_bottom'] = df[['senkou_span_a', 'senkou_span_b']].min(axis=1)

        return df

    def get_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on Ichimoku conditions

        Args:
            df: DataFrame with Ichimoku indicators calculated

        Returns:
            DataFrame with signal columns added
        """
        df = df.copy()

        # Long signals
        df['close_above_cloud'] = df['close'] > df['cloud_top']
        df['tenkan_above_kijun'] = df['tenkan_sen'] > df['kijun_sen']
        df['price_above_tenkan'] = df['close'] > df['tenkan_sen']
        df['chikou_clean'] = self._is_chikou_clean(df)

        # Long signal: basic Ichimoku conditions met
        df['long_signal'] = (df['close_above_cloud'] &
                           df['tenkan_above_kijun'] &
                           df['price_above_tenkan'])

        # Short signals (opposite conditions)
        df['close_below_cloud'] = df['close'] < df['cloud_bottom']
        df['tenkan_below_kijun'] = df['tenkan_sen'] < df['kijun_sen']
        df['price_below_tenkan'] = df['close'] < df['tenkan_sen']
        df['chikou_clean_short'] = self._is_chikou_clean_short(df)

        # Short signal: all opposite conditions met
        df['short_signal'] = (df['close_below_cloud'] &
                            df['tenkan_below_kijun'] &
                            df['price_below_tenkan'])

        return df

    def _is_chikou_clean(self, df: pd.DataFrame) -> pd.Series:
        """
        Check if Chikou Span is clean (price above local minima between current price and Chikou Span)
        """
        clean_signals = []

        for idx in df.index:
            current_price = df.loc[idx, 'close']
            chikou_price = df.loc[idx, 'chikou_span']

            if pd.isna(chikou_price):
                clean_signals.append(False)
                continue

            # Find data between current candle and Chikou Span position
            current_idx = df.index.get_loc(idx)
            chikou_shift = self.chikou_period

            if current_idx + chikou_shift >= len(df):
                clean_signals.append(False)
                continue

            # Get prices between current and Chikou Span position
            lookback_data = df.iloc[max(0, current_idx - chikou_shift):current_idx + 1]

            if len(lookback_data) == 0:
                clean_signals.append(False)
                continue

            # Check if current price is above all local minima
            local_minima = lookback_data['low'].min()
            clean_signals.append(current_price > local_minima)

        return pd.Series(clean_signals, index=df.index)

    def _is_chikou_clean_short(self, df: pd.DataFrame) -> pd.Series:
        """
        Check if Chikou Span is clean for short (price below local maxima between current price and Chikou Span)
        """
        clean_signals = []

        for idx in df.index:
            current_price = df.loc[idx, 'close']
            chikou_price = df.loc[idx, 'chikou_span']

            if pd.isna(chikou_price):
                clean_signals.append(False)
                continue

            # Find data between current candle and Chikou Span position
            current_idx = df.index.get_loc(idx)
            chikou_shift = self.chikou_period

            if current_idx + chikou_shift >= len(df):
                clean_signals.append(False)
                continue

            # Get prices between current and Chikou Span position
            lookback_data = df.iloc[max(0, current_idx - chikou_shift):current_idx + 1]

            if len(lookback_data) == 0:
                clean_signals.append(False)
                continue

            # Check if current price is below all local maxima
            local_maxima = lookback_data['high'].max()
            clean_signals.append(current_price < local_maxima)

        return pd.Series(clean_signals, index=df.index)

    def check_stop_loss(self, df: pd.DataFrame, position_type: str) -> pd.Series:
        """
        Check for stop loss conditions

        Args:
            df: DataFrame with indicators
            position_type: 'long' or 'short'

        Returns:
            Series of boolean values indicating stop loss triggers
        """
        if position_type == 'long':
            # Stop loss: price below Kijun-sen or two candles close inside cloud
            below_kijun = df['close'] < df['kijun_sen']
            inside_cloud = (df['close'] >= df['cloud_bottom']) & (df['close'] <= df['cloud_top'])
            two_candles_inside = inside_cloud & inside_cloud.shift(1).fillna(False)
            return below_kijun | two_candles_inside
        else:  # short
            # Stop loss: price above Kijun-sen or two candles close inside cloud
            above_kijun = df['close'] > df['kijun_sen']
            inside_cloud = (df['close'] >= df['cloud_bottom']) & (df['close'] <= df['cloud_top'])
            two_candles_inside = inside_cloud & inside_cloud.shift(1).fillna(False)
            return above_kijun | two_candles_inside

    def check_target(self, df: pd.DataFrame, position_type: str) -> pd.Series:
        """
        Check for target conditions (exit signals)

        Args:
            df: DataFrame with indicators
            position_type: 'long' or 'short'

        Returns:
            Series of boolean values indicating target reached
        """
        if position_type == 'long':
            # Target: close below conversion line or conversion crosses under base line
            below_conversion = df['close'] < df['tenkan_sen']
            conversion_cross_under = (df['tenkan_sen'] < df['kijun_sen']) & (df['tenkan_sen'].shift(1) >= df['kijun_sen'].shift(1))
            return below_conversion | conversion_cross_under
        else:  # short
            # Target: close above conversion line or conversion crosses above base line
            above_conversion = df['close'] > df['tenkan_sen']
            conversion_cross_above = (df['tenkan_sen'] > df['kijun_sen']) & (df['tenkan_sen'].shift(1) <= df['kijun_sen'].shift(1))
            return above_conversion | conversion_cross_above
