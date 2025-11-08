"""
Zerodha MCP Server Client - Fixed Version
Handles all interactions with Zerodha's Kite API
"""
import asyncio
import httpx
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from config.settings import settings

logger = logging.getLogger(__name__)


class ZerodhaClient:
    """Client for interacting with Zerodha's Kite API"""

    def __init__(self):
        # Try to get tokens from token manager first
        try:
            from src.services.token_manager import token_manager
            tokens = token_manager.get_zerodha_token()
            if tokens:
                self.api_key = tokens['api_key']
                self.api_secret = tokens['api_secret']
                self.access_token = tokens['access_token']
                logger.info("Using Zerodha tokens from token manager")
            else:
                # Fall back to settings
                self.api_key = settings.zerodha_api_key
                self.api_secret = settings.zerodha_api_secret
                self.access_token = settings.zerodha_access_token
                logger.info("Using Zerodha tokens from settings")
        except Exception as e:
            logger.warning(f"Could not load from token manager: {e}. Using settings.")
            self.api_key = settings.zerodha_api_key
            self.api_secret = settings.zerodha_api_secret
            self.access_token = settings.zerodha_access_token

        self.base_url = "https://api.kite.trade"
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = httpx.AsyncClient()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.aclose()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        return {
            "X-Kite-Version": "3",
            "Authorization": f"token {self.api_key}:{self.access_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    
    async def get_profile(self) -> Dict[str, Any]:
        """Get user profile information"""
        try:
            response = await self.session.get(
                f"{self.base_url}/user/profile",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching profile: {e}")
            raise
    
    async def get_portfolio(self) -> Dict[str, Any]:
        """Get current portfolio holdings"""
        try:
            response = await self.session.get(
                f"{self.base_url}/portfolio/holdings",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching portfolio: {e}")
            raise
    
    async def get_positions(self) -> Dict[str, Any]:
        """Get current positions"""
        try:
            response = await self.session.get(
                f"{self.base_url}/portfolio/positions",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            raise
    
    async def get_margins(self) -> Dict[str, Any]:
        """Get account margins"""
        try:
            response = await self.session.get(
                f"{self.base_url}/user/margins",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching margins: {e}")
            raise
    
    async def get_orders(self, status: str = "all") -> Dict[str, Any]:
        """Get order history"""
        try:
            response = await self.session.get(
                f"{self.base_url}/orders",
                headers=self._get_headers(),
                params={"status": status}
            )
            response.raise_for_status()
            return await response.json()
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            raise
    
    async def get_historical_data(
        self, 
        instrument_token: str, 
        from_date: str, 
        to_date: str, 
        interval: str = "day"
    ) -> Dict[str, Any]:
        """Get historical data for a symbol"""
        try:
            params = {
                "instrument_token": instrument_token,
                "from": from_date,
                "to": to_date,
                "interval": interval
            }
            response = await self.session.get(
                f"{self.base_url}/instruments/historical/{instrument_token}/{interval}",
                headers=self._get_headers(),
                params=params
            )
            response.raise_for_status()
            return await response.json()
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            raise
    
    async def get_quote(self, instruments: List[str]) -> Dict[str, Any]:
        """Get live quotes for instruments"""
        try:
            instruments_str = ",".join(instruments)
            response = await self.session.get(
                f"{self.base_url}/quote",
                headers=self._get_headers(),
                params={"i": instruments_str}
            )
            response.raise_for_status()
            return await response.json()
        except Exception as e:
            logger.error(f"Error fetching quotes: {e}")
            raise
    
    async def place_order(
        self,
        variety: str,
        exchange: str,
        tradingsymbol: str,
        transaction_type: str,
        quantity: int,
        product: str,
        order_type: str,
        price: Optional[float] = None,
        validity: str = "DAY"
    ) -> Dict[str, Any]:
        """Place a new order"""
        try:
            data = {
                "variety": variety,
                "exchange": exchange,
                "tradingsymbol": tradingsymbol,
                "transaction_type": transaction_type,
                "quantity": quantity,
                "product": product,
                "order_type": order_type,
                "validity": validity
            }
            if price:
                data["price"] = price
                
            response = await self.session.post(
                f"{self.base_url}/orders/regular",
                headers=self._get_headers(),
                data=data
            )
            response.raise_for_status()
            return await response.json()
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise
    
    async def modify_order(
        self,
        order_id: str,
        variety: str,
        quantity: Optional[int] = None,
        price: Optional[float] = None,
        order_type: Optional[str] = None,
        validity: Optional[str] = None
    ) -> Dict[str, Any]:
        """Modify an existing order"""
        try:
            data = {
                "order_id": order_id,
                "variety": variety
            }
            if quantity:
                data["quantity"] = quantity
            if price:
                data["price"] = price
            if order_type:
                data["order_type"] = order_type
            if validity:
                data["validity"] = validity
                
            response = await self.session.put(
                f"{self.base_url}/orders/regular/{order_id}",
                headers=self._get_headers(),
                data=data
            )
            response.raise_for_status()
            return await response.json()
        except Exception as e:
            logger.error(f"Error modifying order: {e}")
            raise
    
    async def cancel_order(self, order_id: str, variety: str = "regular") -> Dict[str, Any]:
        """Cancel an existing order"""
        try:
            data = {
                "order_id": order_id,
                "variety": variety
            }
            response = await self.session.delete(
                f"{self.base_url}/orders/{variety}/{order_id}",
                headers=self._get_headers(),
                data=data
            )
            response.raise_for_status()
            return await response.json()
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            raise
    
    async def get_instruments(self, exchange: Optional[str] = None) -> Dict[str, Any]:
        """Get list of all instruments"""
        try:
            url = f"{self.base_url}/instruments"
            if exchange:
                url += f"/{exchange}"
                
            response = await self.session.get(
                url,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return await response.json()
        except Exception as e:
            logger.error(f"Error fetching instruments: {e}")
            raise
