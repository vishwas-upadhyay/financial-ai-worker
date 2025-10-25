"""
Technical Indicators Calculator
Calculates popular technical indicators for stock analysis
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class Signal(Enum):
    """Trading signal types"""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    NEUTRAL = "neutral"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


@dataclass
class IndicatorResult:
    """Result of technical indicator analysis"""
    signal: Signal
    value: float
    description: str
    confidence: float  # 0-100


class TechnicalIndicators:
    """Calculate and analyze technical indicators"""

    def __init__(self):
        pass

    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)

        Args:
            df: DataFrame with 'close' column
            period: RSI period (default 14)

        Returns:
            Series with RSI values
        """
        try:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            return rsi

        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return pd.Series()

    def calculate_macd(
        self,
        df: pd.DataFrame,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)

        Args:
            df: DataFrame with 'close' column
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period

        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        try:
            exp1 = df['close'].ewm(span=fast, adjust=False).mean()
            exp2 = df['close'].ewm(span=slow, adjust=False).mean()

            macd_line = exp1 - exp2
            signal_line = macd_line.ewm(span=signal, adjust=False).mean()
            histogram = macd_line - signal_line

            return macd_line, signal_line, histogram

        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return pd.Series(), pd.Series(), pd.Series()

    def calculate_bollinger_bands(
        self,
        df: pd.DataFrame,
        period: int = 20,
        std_dev: float = 2
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands

        Args:
            df: DataFrame with 'close' column
            period: Moving average period
            std_dev: Number of standard deviations

        Returns:
            Tuple of (Upper band, Middle band, Lower band)
        """
        try:
            middle_band = df['close'].rolling(window=period).mean()
            std = df['close'].rolling(window=period).std()

            upper_band = middle_band + (std * std_dev)
            lower_band = middle_band - (std * std_dev)

            return upper_band, middle_band, lower_band

        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return pd.Series(), pd.Series(), pd.Series()

    def calculate_sma(self, df: pd.DataFrame, period: int = 50) -> pd.Series:
        """
        Calculate Simple Moving Average (SMA)

        Args:
            df: DataFrame with 'close' column
            period: SMA period

        Returns:
            Series with SMA values
        """
        try:
            return df['close'].rolling(window=period).mean()
        except Exception as e:
            logger.error(f"Error calculating SMA: {e}")
            return pd.Series()

    def calculate_ema(self, df: pd.DataFrame, period: int = 50) -> pd.Series:
        """
        Calculate Exponential Moving Average (EMA)

        Args:
            df: DataFrame with 'close' column
            period: EMA period

        Returns:
            Series with EMA values
        """
        try:
            return df['close'].ewm(span=period, adjust=False).mean()
        except Exception as e:
            logger.error(f"Error calculating EMA: {e}")
            return pd.Series()

    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range (ATR) for volatility

        Args:
            df: DataFrame with 'high', 'low', 'close' columns
            period: ATR period

        Returns:
            Series with ATR values
        """
        try:
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())

            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)

            atr = true_range.rolling(window=period).mean()
            return atr

        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return pd.Series()

    def calculate_stochastic(
        self,
        df: pd.DataFrame,
        k_period: int = 14,
        d_period: int = 3
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Stochastic Oscillator

        Args:
            df: DataFrame with 'high', 'low', 'close' columns
            k_period: %K period
            d_period: %D period

        Returns:
            Tuple of (%K, %D)
        """
        try:
            lowest_low = df['low'].rolling(window=k_period).min()
            highest_high = df['high'].rolling(window=k_period).max()

            k_percent = 100 * ((df['close'] - lowest_low) / (highest_high - lowest_low))
            d_percent = k_percent.rolling(window=d_period).mean()

            return k_percent, d_percent

        except Exception as e:
            logger.error(f"Error calculating Stochastic: {e}")
            return pd.Series(), pd.Series()

    def analyze_rsi(self, rsi: pd.Series) -> IndicatorResult:
        """
        Analyze RSI signal

        Args:
            rsi: RSI series

        Returns:
            IndicatorResult with signal and confidence
        """
        try:
            current_rsi = rsi.iloc[-1]

            if current_rsi < 30:
                return IndicatorResult(
                    signal=Signal.STRONG_BUY if current_rsi < 20 else Signal.BUY,
                    value=current_rsi,
                    description=f"RSI at {current_rsi:.2f} - Oversold territory",
                    confidence=min(100, (30 - current_rsi) * 3)
                )
            elif current_rsi > 70:
                return IndicatorResult(
                    signal=Signal.STRONG_SELL if current_rsi > 80 else Signal.SELL,
                    value=current_rsi,
                    description=f"RSI at {current_rsi:.2f} - Overbought territory",
                    confidence=min(100, (current_rsi - 70) * 3)
                )
            else:
                return IndicatorResult(
                    signal=Signal.NEUTRAL,
                    value=current_rsi,
                    description=f"RSI at {current_rsi:.2f} - Neutral range",
                    confidence=50
                )

        except Exception as e:
            logger.error(f"Error analyzing RSI: {e}")
            return IndicatorResult(Signal.NEUTRAL, 50, "Error analyzing RSI", 0)

    def analyze_macd(
        self,
        macd_line: pd.Series,
        signal_line: pd.Series,
        histogram: pd.Series
    ) -> IndicatorResult:
        """
        Analyze MACD signal

        Args:
            macd_line: MACD line
            signal_line: Signal line
            histogram: MACD histogram

        Returns:
            IndicatorResult with signal and confidence
        """
        try:
            current_macd = macd_line.iloc[-1]
            current_signal = signal_line.iloc[-1]
            current_hist = histogram.iloc[-1]
            prev_hist = histogram.iloc[-2]

            # Bullish crossover
            if prev_hist < 0 and current_hist > 0:
                return IndicatorResult(
                    signal=Signal.BUY,
                    value=current_hist,
                    description="MACD bullish crossover detected",
                    confidence=75
                )

            # Bearish crossover
            elif prev_hist > 0 and current_hist < 0:
                return IndicatorResult(
                    signal=Signal.SELL,
                    value=current_hist,
                    description="MACD bearish crossover detected",
                    confidence=75
                )

            # Strong momentum
            elif current_hist > 0 and current_macd > current_signal:
                return IndicatorResult(
                    signal=Signal.BUY,
                    value=current_hist,
                    description="MACD shows bullish momentum",
                    confidence=60
                )

            elif current_hist < 0 and current_macd < current_signal:
                return IndicatorResult(
                    signal=Signal.SELL,
                    value=current_hist,
                    description="MACD shows bearish momentum",
                    confidence=60
                )

            else:
                return IndicatorResult(
                    signal=Signal.NEUTRAL,
                    value=current_hist,
                    description="MACD neutral",
                    confidence=50
                )

        except Exception as e:
            logger.error(f"Error analyzing MACD: {e}")
            return IndicatorResult(Signal.NEUTRAL, 0, "Error analyzing MACD", 0)

    def analyze_bollinger_bands(
        self,
        df: pd.DataFrame,
        upper: pd.Series,
        middle: pd.Series,
        lower: pd.Series
    ) -> IndicatorResult:
        """
        Analyze Bollinger Bands signal

        Args:
            df: DataFrame with price data
            upper: Upper band
            middle: Middle band
            lower: Lower band

        Returns:
            IndicatorResult with signal and confidence
        """
        try:
            current_price = df['close'].iloc[-1]
            current_upper = upper.iloc[-1]
            current_middle = middle.iloc[-1]
            current_lower = lower.iloc[-1]

            band_width = current_upper - current_lower
            price_position = (current_price - current_lower) / band_width

            # Price near lower band - potential buy
            if price_position < 0.2:
                return IndicatorResult(
                    signal=Signal.BUY,
                    value=price_position,
                    description=f"Price near lower Bollinger Band ({price_position*100:.1f}% position)",
                    confidence=70
                )

            # Price near upper band - potential sell
            elif price_position > 0.8:
                return IndicatorResult(
                    signal=Signal.SELL,
                    value=price_position,
                    description=f"Price near upper Bollinger Band ({price_position*100:.1f}% position)",
                    confidence=70
                )

            else:
                return IndicatorResult(
                    signal=Signal.NEUTRAL,
                    value=price_position,
                    description=f"Price in middle range ({price_position*100:.1f}% position)",
                    confidence=50
                )

        except Exception as e:
            logger.error(f"Error analyzing Bollinger Bands: {e}")
            return IndicatorResult(Signal.NEUTRAL, 0.5, "Error analyzing Bollinger Bands", 0)

    def analyze_moving_averages(
        self,
        df: pd.DataFrame,
        sma_50: pd.Series,
        sma_200: pd.Series
    ) -> IndicatorResult:
        """
        Analyze Moving Average signals (Golden Cross / Death Cross)

        Args:
            df: DataFrame with price data
            sma_50: 50-day SMA
            sma_200: 200-day SMA

        Returns:
            IndicatorResult with signal and confidence
        """
        try:
            current_price = df['close'].iloc[-1]
            current_sma50 = sma_50.iloc[-1]
            current_sma200 = sma_200.iloc[-1]
            prev_sma50 = sma_50.iloc[-2]
            prev_sma200 = sma_200.iloc[-2]

            # Golden Cross (bullish)
            if prev_sma50 < prev_sma200 and current_sma50 > current_sma200:
                return IndicatorResult(
                    signal=Signal.STRONG_BUY,
                    value=current_sma50 - current_sma200,
                    description="Golden Cross detected - Strong bullish signal",
                    confidence=85
                )

            # Death Cross (bearish)
            elif prev_sma50 > prev_sma200 and current_sma50 < current_sma200:
                return IndicatorResult(
                    signal=Signal.STRONG_SELL,
                    value=current_sma50 - current_sma200,
                    description="Death Cross detected - Strong bearish signal",
                    confidence=85
                )

            # Price above both MAs (bullish)
            elif current_price > current_sma50 > current_sma200:
                return IndicatorResult(
                    signal=Signal.BUY,
                    value=current_price - current_sma50,
                    description="Price above both moving averages - Bullish trend",
                    confidence=70
                )

            # Price below both MAs (bearish)
            elif current_price < current_sma50 < current_sma200:
                return IndicatorResult(
                    signal=Signal.SELL,
                    value=current_price - current_sma50,
                    description="Price below both moving averages - Bearish trend",
                    confidence=70
                )

            else:
                return IndicatorResult(
                    signal=Signal.NEUTRAL,
                    value=0,
                    description="Mixed moving average signals",
                    confidence=50
                )

        except Exception as e:
            logger.error(f"Error analyzing Moving Averages: {e}")
            return IndicatorResult(Signal.NEUTRAL, 0, "Error analyzing MAs", 0)

    def get_all_indicators(self, df: pd.DataFrame) -> Dict:
        """
        Calculate all technical indicators for a DataFrame

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary with all indicators
        """
        try:
            # Calculate all indicators
            rsi = self.calculate_rsi(df)
            macd_line, signal_line, histogram = self.calculate_macd(df)
            upper_bb, middle_bb, lower_bb = self.calculate_bollinger_bands(df)
            sma_50 = self.calculate_sma(df, 50)
            sma_200 = self.calculate_sma(df, 200)
            ema_20 = self.calculate_ema(df, 20)
            atr = self.calculate_atr(df)
            k_percent, d_percent = self.calculate_stochastic(df)

            # Analyze signals
            rsi_signal = self.analyze_rsi(rsi)
            macd_signal = self.analyze_macd(macd_line, signal_line, histogram)
            bb_signal = self.analyze_bollinger_bands(df, upper_bb, middle_bb, lower_bb)
            ma_signal = self.analyze_moving_averages(df, sma_50, sma_200)

            return {
                'indicators': {
                    'rsi': rsi.iloc[-1] if not rsi.empty else None,
                    'macd': macd_line.iloc[-1] if not macd_line.empty else None,
                    'macd_signal': signal_line.iloc[-1] if not signal_line.empty else None,
                    'macd_histogram': histogram.iloc[-1] if not histogram.empty else None,
                    'bb_upper': upper_bb.iloc[-1] if not upper_bb.empty else None,
                    'bb_middle': middle_bb.iloc[-1] if not middle_bb.empty else None,
                    'bb_lower': lower_bb.iloc[-1] if not lower_bb.empty else None,
                    'sma_50': sma_50.iloc[-1] if not sma_50.empty else None,
                    'sma_200': sma_200.iloc[-1] if not sma_200.empty else None,
                    'ema_20': ema_20.iloc[-1] if not ema_20.empty else None,
                    'atr': atr.iloc[-1] if not atr.empty else None,
                    'stochastic_k': k_percent.iloc[-1] if not k_percent.empty else None,
                    'stochastic_d': d_percent.iloc[-1] if not d_percent.empty else None,
                },
                'signals': {
                    'rsi': {
                        'signal': rsi_signal.signal.value,
                        'value': rsi_signal.value,
                        'description': rsi_signal.description,
                        'confidence': rsi_signal.confidence
                    },
                    'macd': {
                        'signal': macd_signal.signal.value,
                        'value': macd_signal.value,
                        'description': macd_signal.description,
                        'confidence': macd_signal.confidence
                    },
                    'bollinger_bands': {
                        'signal': bb_signal.signal.value,
                        'value': bb_signal.value,
                        'description': bb_signal.description,
                        'confidence': bb_signal.confidence
                    },
                    'moving_averages': {
                        'signal': ma_signal.signal.value,
                        'value': ma_signal.value,
                        'description': ma_signal.description,
                        'confidence': ma_signal.confidence
                    }
                }
            }

        except Exception as e:
            logger.error(f"Error getting all indicators: {e}")
            return {'indicators': {}, 'signals': {}}


# Global instance
technical_indicators = TechnicalIndicators()
