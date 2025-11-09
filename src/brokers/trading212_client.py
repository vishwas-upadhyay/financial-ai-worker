"""
Trading 212 API Client
Handles all interactions with Trading 212 API
Official API docs: https://t212public-api-docs.redoc.ly/
"""
import asyncio
import httpx
import json
import base64
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from config.settings import settings

logger = logging.getLogger(__name__)


class Trading212Client:
    """Client for interacting with Trading 212 API"""

    def __init__(self, use_demo: bool = False, api_key: Optional[str] = None, api_secret: Optional[str] = None, account_name: str = "primary"):
        """
        Initialize Trading212 client

        Args:
            use_demo: If True, use demo/paper trading environment
            api_key: Optional API key (if not provided, will use from token manager or settings)
            api_secret: Optional API secret
            account_name: Account identifier (e.g., 'primary', 'spouse', 'child')
        """
        self.account_name = account_name

        # Try to get tokens from token manager first
        if not api_key:
            try:
                from src.services.token_manager import token_manager
                tokens = token_manager.get_trading212_token(account_name=account_name)
                if tokens:
                    self.api_key = tokens['api_key']
                    self.api_secret = tokens.get('api_secret')
                    logger.info(f"Using Trading212 tokens from token manager for account: {account_name}")
                else:
                    # Fall back to settings (only for primary account)
                    if account_name == "primary":
                        self.api_key = settings.trading212_api_key
                        self.api_secret = settings.trading212_api_secret
                        logger.info("Using Trading212 tokens from settings")
                    else:
                        raise ValueError(f"No tokens found for Trading212 account: {account_name}")
            except Exception as e:
                if account_name == "primary":
                    logger.warning(f"Could not load from token manager: {e}. Using settings.")
                    self.api_key = settings.trading212_api_key
                    self.api_secret = settings.trading212_api_secret
                else:
                    logger.error(f"Could not load tokens for account {account_name}: {e}")
                    raise
        else:
            self.api_key = api_key
            self.api_secret = api_secret

        # Choose base URL based on environment
        if use_demo:
            self.base_url = "https://demo.trading212.com/api/v0"
        else:
            self.base_url = "https://live.trading212.com/api/v0"

        self.session = None
        self._auth_header = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = httpx.AsyncClient(timeout=30.0)
        self._prepare_auth()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.aclose()

    def _prepare_auth(self):
        """Prepare HTTP Basic Authentication header"""
        if not self.api_key:
            raise ValueError("Trading212 API key is not configured. Please set TRADING212_API_KEY in .env file")

        # Trading212 uses API Key as username and Secret (if provided) as password
        # Format: API_KEY:API_SECRET (or just API_KEY: if no secret)
        if self.api_secret:
            credentials = f"{self.api_key}:{self.api_secret}"
        else:
            credentials = f"{self.api_key}:"

        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self._auth_header = f"Basic {encoded_credentials}"
        logger.info("Trading212 authentication prepared")

    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        return {
            "Authorization": self._auth_header,
            "Content-Type": "application/json"
        }
    
    async def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information
        Rate limit: 1 request per 30 seconds
        """
        try:
            response = await self.session.get(
                f"{self.base_url}/equity/account/info",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching account info: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error fetching account info: {e}")
            raise

    async def get_account_cash(self) -> Dict[str, Any]:
        """
        Get detailed cash balance and investment metrics
        Rate limit: 1 request per 2 seconds
        """
        try:
            response = await self.session.get(
                f"{self.base_url}/equity/account/cash",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching cash info: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error fetching cash info: {e}")
            raise

    async def get_portfolio(self) -> List[Dict[str, Any]]:
        """
        Get current portfolio holdings (all positions)
        Rate limit: 1 request per 5 seconds
        Returns: List of positions with quantity, average price, current price, etc.
        """
        try:
            response = await self.session.get(
                f"{self.base_url}/equity/portfolio",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching portfolio: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error fetching portfolio: {e}")
            raise

    async def get_positions(self) -> List[Dict[str, Any]]:
        """Alias for get_portfolio() for compatibility"""
        return await self.get_portfolio()

    async def get_position_by_ticker(self, ticker: str) -> Dict[str, Any]:
        """
        Get specific position by ticker symbol
        Rate limit: 1 request per second

        Args:
            ticker: Ticker symbol (e.g., "AAPL_US_EQ")
        """
        try:
            response = await self.session.get(
                f"{self.base_url}/equity/portfolio/{ticker}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching position for {ticker}: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error fetching position for {ticker}: {e}")
            raise
    
    async def get_orders(self) -> List[Dict[str, Any]]:
        """
        Get order history
        Rate limit: 1 request per 5 seconds
        """
        try:
            response = await self.session.get(
                f"{self.base_url}/equity/history/orders",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching orders: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            raise

    async def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "market",
        price: Optional[float] = None,
        stop_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Place a market order (live trading only)
        Rate limit: 1 request per 5 seconds

        Args:
            symbol: Ticker symbol
            side: "BUY" or "SELL"
            quantity: Number of shares
            order_type: Only "market" is supported for live trading
            price: Limit price (not supported for market orders)
            stop_price: Stop price (not supported for market orders)
        """
        try:
            data = {
                "quantity": quantity,
                "ticker": symbol
            }

            response = await self.session.post(
                f"{self.base_url}/equity/orders/{side.lower()}",
                headers=self._get_headers(),
                json=data
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error placing order: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise

    async def get_instruments(self) -> List[Dict[str, Any]]:
        """
        Get list of available instruments
        Rate limit: 1 request per 30 seconds
        """
        try:
            response = await self.session.get(
                f"{self.base_url}/equity/metadata/instruments",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching instruments: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error fetching instruments: {e}")
            raise

