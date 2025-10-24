"""
Currency Conversion Service
Provides real-time currency conversion using exchangerate-api.com (free tier)
"""
import httpx
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class CurrencyConverter:
    """
    Currency converter with caching for exchange rates
    Uses exchangerate-api.com free API (1500 requests/month)
    """

    def __init__(self):
        self.base_url = "https://api.exchangerate-api.com/v4/latest"
        self.cache: Dict[str, Dict] = {}
        self.cache_duration = timedelta(hours=1)  # Cache rates for 1 hour
        self.cache_file = Path("data/currency_cache.json")
        self._load_cache()

    def _load_cache(self):
        """Load cached rates from file"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    # Convert timestamp strings back to datetime
                    for currency, data in cache_data.items():
                        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                    self.cache = cache_data
                logger.info("Loaded currency cache from file")
        except Exception as e:
            logger.warning(f"Could not load currency cache: {e}")
            self.cache = {}

    def _save_cache(self):
        """Save cached rates to file"""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            # Convert datetime to string for JSON serialization
            cache_data = {}
            for currency, data in self.cache.items():
                cache_data[currency] = {
                    'rates': data['rates'],
                    'timestamp': data['timestamp'].isoformat()
                }

            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)
            logger.debug("Saved currency cache to file")
        except Exception as e:
            logger.warning(f"Could not save currency cache: {e}")

    async def get_exchange_rates(self, base_currency: str = "USD") -> Optional[Dict[str, float]]:
        """
        Get exchange rates for a base currency

        Args:
            base_currency: Base currency code (e.g., "USD", "EUR", "INR")

        Returns:
            Dictionary of exchange rates or None if failed
        """
        base_currency = base_currency.upper()

        # Check cache
        if base_currency in self.cache:
            cached_data = self.cache[base_currency]
            if datetime.now() - cached_data['timestamp'] < self.cache_duration:
                logger.debug(f"Using cached rates for {base_currency}")
                return cached_data['rates']

        # Fetch new rates
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/{base_currency}")
                response.raise_for_status()
                data = response.json()

                rates = data.get('rates', {})

                # Cache the rates
                self.cache[base_currency] = {
                    'rates': rates,
                    'timestamp': datetime.now()
                }
                self._save_cache()

                logger.info(f"Fetched exchange rates for {base_currency}")
                return rates

        except Exception as e:
            logger.error(f"Error fetching exchange rates for {base_currency}: {e}")

            # Try to use expired cache as fallback
            if base_currency in self.cache:
                logger.warning(f"Using expired cache for {base_currency}")
                return self.cache[base_currency]['rates']

            return None

    async def convert(
        self,
        amount: float,
        from_currency: str,
        to_currency: str
    ) -> Optional[float]:
        """
        Convert amount from one currency to another

        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code

        Returns:
            Converted amount or None if conversion failed
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        # Same currency, no conversion needed
        if from_currency == to_currency:
            return amount

        # Get rates based on from_currency
        rates = await self.get_exchange_rates(from_currency)

        if not rates:
            logger.error(f"Could not get rates for {from_currency}")
            return None

        if to_currency not in rates:
            logger.error(f"Currency {to_currency} not found in rates")
            return None

        conversion_rate = rates[to_currency]
        converted_amount = amount * conversion_rate

        logger.debug(f"Converted {amount} {from_currency} to {converted_amount} {to_currency} (rate: {conversion_rate})")

        return converted_amount

    async def convert_portfolio(
        self,
        holdings: list,
        from_currency: str,
        to_currency: str
    ) -> tuple[list, float, float, float]:
        """
        Convert entire portfolio to target currency

        Args:
            holdings: List of holdings with values
            from_currency: Source currency
            to_currency: Target currency

        Returns:
            Tuple of (converted_holdings, total_value, total_investment, total_pnl)
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        # Get conversion rate
        rates = await self.get_exchange_rates(from_currency)
        if not rates or to_currency not in rates:
            logger.error(f"Could not convert portfolio from {from_currency} to {to_currency}")
            return holdings, 0, 0, 0

        conversion_rate = rates[to_currency]

        # Convert each holding
        converted_holdings = []
        total_value = 0
        total_investment = 0
        total_pnl = 0

        for holding in holdings:
            converted_holding = holding.copy()

            # Convert monetary values
            if 'average_price' in converted_holding:
                converted_holding['average_price'] *= conversion_rate
            if 'current_price' in converted_holding:
                converted_holding['current_price'] *= conversion_rate
            if 'current_value' in converted_holding:
                converted_holding['current_value'] *= conversion_rate
                total_value += converted_holding['current_value']
            if 'invested_value' in converted_holding:
                converted_holding['invested_value'] *= conversion_rate
                total_investment += converted_holding['invested_value']
            if 'pnl' in converted_holding:
                converted_holding['pnl'] *= conversion_rate
                total_pnl += converted_holding['pnl']
            if 'day_pnl' in converted_holding:
                converted_holding['day_pnl'] *= conversion_rate

            # Add currency info
            converted_holding['original_currency'] = from_currency
            converted_holding['display_currency'] = to_currency
            converted_holding['conversion_rate'] = conversion_rate

            converted_holdings.append(converted_holding)

        return converted_holdings, total_value, total_investment, total_pnl

    def get_supported_currencies(self) -> list[str]:
        """Get list of supported currencies"""
        return [
            'INR',  # Indian Rupee
            'EUR',  # Euro
        ]


# Global instance
currency_converter = CurrencyConverter()
