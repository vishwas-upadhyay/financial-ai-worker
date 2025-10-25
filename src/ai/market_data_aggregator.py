"""
Market Data Aggregator
Collects real-time and historical market data from multiple sources
"""
import asyncio
import httpx
import pandas as pd
import yfinance as yf
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Available data sources"""
    YAHOO_FINANCE = "yahoo"
    ALPHA_VANTAGE = "alphavantage"
    BROKER = "broker"


class MarketDataAggregator:
    """Aggregates market data from multiple sources"""

    def __init__(self, alpha_vantage_key: Optional[str] = None):
        """
        Initialize market data aggregator

        Args:
            alpha_vantage_key: Alpha Vantage API key (optional)
        """
        self.alpha_vantage_key = alpha_vantage_key
        self.cache = {}
        self.cache_duration = timedelta(minutes=5)

    async def get_current_price(self, symbol: str, exchange: str = "NSE") -> Optional[float]:
        """
        Get current price for a symbol

        Args:
            symbol: Stock symbol
            exchange: Exchange (NSE, BSE, NYSE, NASDAQ)

        Returns:
            Current price or None if not available
        """
        try:
            # Format symbol based on exchange
            ticker_symbol = self._format_symbol(symbol, exchange)

            # Check cache first
            cache_key = f"price_{ticker_symbol}"
            if cache_key in self.cache:
                cached_time, cached_price = self.cache[cache_key]
                if datetime.now() - cached_time < self.cache_duration:
                    return cached_price

            # Fetch from Yahoo Finance
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            price = info.get('currentPrice') or info.get('regularMarketPrice')

            if price:
                self.cache[cache_key] = (datetime.now(), price)
                return float(price)

            return None

        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None

    async def get_historical_data(
        self,
        symbol: str,
        exchange: str = "NSE",
        period: str = "1mo",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Get historical data for a symbol

        Args:
            symbol: Stock symbol
            exchange: Exchange (NSE, BSE, NYSE, NASDAQ)
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker_symbol = self._format_symbol(symbol, exchange)

            # Fetch historical data
            ticker = yf.Ticker(ticker_symbol)
            df = ticker.history(period=period, interval=interval)

            if df.empty:
                logger.warning(f"No historical data found for {symbol}")
                return None

            # Standardize column names
            df.columns = [col.lower() for col in df.columns]

            return df

        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None

    async def get_multiple_prices(
        self,
        symbols: List[Tuple[str, str]]
    ) -> Dict[str, float]:
        """
        Get current prices for multiple symbols

        Args:
            symbols: List of (symbol, exchange) tuples

        Returns:
            Dictionary mapping symbols to prices
        """
        tasks = [self.get_current_price(symbol, exchange) for symbol, exchange in symbols]
        prices = await asyncio.gather(*tasks, return_exceptions=True)

        result = {}
        for (symbol, exchange), price in zip(symbols, prices):
            if isinstance(price, Exception):
                logger.error(f"Error fetching price for {symbol}: {price}")
                continue
            if price is not None:
                result[symbol] = price

        return result

    async def get_market_info(self, symbol: str, exchange: str = "NSE") -> Dict:
        """
        Get detailed market information for a symbol

        Args:
            symbol: Stock symbol
            exchange: Exchange

        Returns:
            Dictionary with market information
        """
        try:
            ticker_symbol = self._format_symbol(symbol, exchange)
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info

            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'eps': info.get('trailingEps'),
                'dividend_yield': info.get('dividendYield'),
                'beta': info.get('beta'),
                '52_week_high': info.get('fiftyTwoWeekHigh'),
                '52_week_low': info.get('fiftyTwoWeekLow'),
                'avg_volume': info.get('averageVolume'),
                'current_price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'previous_close': info.get('previousClose'),
                'day_change': self._calculate_day_change(
                    info.get('currentPrice') or info.get('regularMarketPrice'),
                    info.get('previousClose')
                )
            }

        except Exception as e:
            logger.error(f"Error fetching market info for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

    async def get_news_sentiment(self, symbol: str, exchange: str = "NSE") -> List[Dict]:
        """
        Get recent news and sentiment for a symbol

        Args:
            symbol: Stock symbol
            exchange: Exchange

        Returns:
            List of news articles with sentiment
        """
        try:
            ticker_symbol = self._format_symbol(symbol, exchange)
            ticker = yf.Ticker(ticker_symbol)
            news = ticker.news

            # Extract relevant information
            articles = []
            for article in news[:5]:  # Get top 5 news
                articles.append({
                    'title': article.get('title', ''),
                    'publisher': article.get('publisher', ''),
                    'link': article.get('link', ''),
                    'published': article.get('providerPublishTime'),
                    'type': article.get('type', '')
                })

            return articles

        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []

    async def get_market_indices(self) -> Dict[str, Dict]:
        """
        Get major market indices data

        Returns:
            Dictionary with index data
        """
        indices = {
            'NIFTY50': '^NSEI',
            'SENSEX': '^BSESN',
            'NASDAQ': '^IXIC',
            'S&P500': '^GSPC',
            'DOW': '^DJI'
        }

        result = {}
        for name, symbol in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info

                current_price = info.get('regularMarketPrice')
                previous_close = info.get('previousClose')

                result[name] = {
                    'price': current_price,
                    'previous_close': previous_close,
                    'change': current_price - previous_close if current_price and previous_close else 0,
                    'change_percent': ((current_price - previous_close) / previous_close * 100)
                                     if current_price and previous_close else 0
                }
            except Exception as e:
                logger.error(f"Error fetching index {name}: {e}")

        return result

    def _format_symbol(self, symbol: str, exchange: str) -> str:
        """
        Format symbol for Yahoo Finance based on exchange

        Args:
            symbol: Stock symbol
            exchange: Exchange code

        Returns:
            Formatted symbol
        """
        exchange = exchange.upper()

        # Indian exchanges
        if exchange == "NSE":
            return f"{symbol}.NS"
        elif exchange == "BSE":
            return f"{symbol}.BO"

        # US exchanges (no suffix needed)
        elif exchange in ["NYSE", "NASDAQ", "US"]:
            return symbol

        # Default: return as is
        return symbol

    def _calculate_day_change(
        self,
        current_price: Optional[float],
        previous_close: Optional[float]
    ) -> Dict:
        """Calculate day change"""
        if not current_price or not previous_close:
            return {'amount': 0, 'percent': 0}

        change = current_price - previous_close
        change_percent = (change / previous_close) * 100

        return {
            'amount': round(change, 2),
            'percent': round(change_percent, 2)
        }

    def clear_cache(self):
        """Clear price cache"""
        self.cache.clear()


# Global instance
market_data = MarketDataAggregator()
