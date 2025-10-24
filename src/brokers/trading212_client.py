"""
Trading 212 MCP Server Client
Handles all interactions with Trading 212 API
"""
import asyncio
import httpx
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from config.settings import settings

logger = logging.getLogger(__name__)


class Trading212Client:
    """Client for interacting with Trading 212 API"""
    
    def __init__(self):
        self.username = settings.trading212_username
        self.password = settings.trading212_password
        self.api_key = settings.trading212_api_key
        self.base_url = "https://live.trading212.com/api/v1"
        self.session = None
        self.auth_token = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = httpx.AsyncClient()
        await self._authenticate()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.aclose()
    
    async def _authenticate(self):
        """Authenticate with Trading 212 API"""
        try:
            auth_data = {
                "username": self.username,
                "password": self.password
            }
            async with self.session.post(
                f"{self.base_url}/auth/login",
                json=auth_data
            ) as response:
                response.raise_for_status()
                auth_response = await response.json()
                self.auth_token = auth_response.get("token")
        except Exception as e:
            logger.error(f"Error authenticating with Trading 212: {e}")
            raise
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        try:
            async with self.session.get(
                f"{self.base_url}/account",
                headers=self._get_headers()
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Error fetching account info: {e}")
            raise
    
    async def get_portfolio(self) -> Dict[str, Any]:
        """Get current portfolio holdings"""
        try:
            async with self.session.get(
                f"{self.base_url}/portfolio",
                headers=self._get_headers()
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Error fetching portfolio: {e}")
            raise
    
    async def get_positions(self) -> Dict[str, Any]:
        """Get current positions"""
        try:
            async with self.session.get(
                f"{self.base_url}/positions",
                headers=self._get_headers()
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            raise
    
    async def get_orders(self, status: str = "all") -> Dict[str, Any]:
        """Get order history"""
        try:
            params = {"status": status} if status != "all" else {}
            async with self.session.get(
                f"{self.base_url}/orders",
                headers=self._get_headers(),
                params=params
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            raise
    
    async def get_historical_data(
        self, 
        symbol: str, 
        from_date: str, 
        to_date: str, 
        interval: str = "1d"
    ) -> Dict[str, Any]:
        """Get historical data for a symbol"""
        try:
            params = {
                "symbol": symbol,
                "from": from_date,
                "to": to_date,
                "interval": interval
            }
            async with self.session.get(
                f"{self.base_url}/market/history",
                headers=self._get_headers(),
                params=params
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            raise
    
    async def get_quote(self, symbols: List[str]) -> Dict[str, Any]:
        """Get live quotes for symbols"""
        try:
            params = {"symbols": ",".join(symbols)}
            async with self.session.get(
                f"{self.base_url}/market/quote",
                headers=self._get_headers(),
                params=params
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Error fetching quotes: {e}")
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
        """Place a new order"""
        try:
            data = {
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "order_type": order_type
            }
            if price:
                data["price"] = price
            if stop_price:
                data["stop_price"] = stop_price
                
            async with self.session.post(
                f"{self.base_url}/orders",
                headers=self._get_headers(),
                json=data
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise
    
    async def modify_order(
        self,
        order_id: str,
        quantity: Optional[float] = None,
        price: Optional[float] = None,
        stop_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Modify an existing order"""
        try:
            data = {}
            if quantity:
                data["quantity"] = quantity
            if price:
                data["price"] = price
            if stop_price:
                data["stop_price"] = stop_price
                
            async with self.session.put(
                f"{self.base_url}/orders/{order_id}",
                headers=self._get_headers(),
                json=data
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Error modifying order: {e}")
            raise
    
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an existing order"""
        try:
            async with self.session.delete(
                f"{self.base_url}/orders/{order_id}",
                headers=self._get_headers()
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            raise
    
    async def get_market_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Get market data for symbols"""
        try:
            params = {"symbols": ",".join(symbols)}
            async with self.session.get(
                f"{self.base_url}/market/data",
                headers=self._get_headers(),
                params=params
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            raise
    
    async def get_instruments(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get list of available instruments"""
        try:
            params = {}
            if category:
                params["category"] = category
                
            async with self.session.get(
                f"{self.base_url}/instruments",
                headers=self._get_headers(),
                params=params
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Error fetching instruments: {e}")
            raise

