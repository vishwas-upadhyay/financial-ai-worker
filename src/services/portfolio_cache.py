"""
Portfolio Cache Manager
Implements file-based caching for portfolio data to ensure data availability
even when broker APIs are down or disconnected.
"""
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from filelock import FileLock

logger = logging.getLogger(__name__)


class PortfolioCache:
    """File-based cache manager for portfolio data"""

    def __init__(self, cache_dir: str = "data/cache"):
        """
        Initialize portfolio cache

        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = timedelta(hours=24)  # Cache valid for 24 hours

    def _get_cache_path(self, broker: str, currency: str = "INR", account_name: str = "primary") -> Path:
        """Get cache file path for a specific broker, currency, and account"""
        filename = f"portfolio_{broker}_{account_name}_{currency.lower()}.json"
        return self.cache_dir / filename

    def _get_lock_path(self, cache_path: Path) -> Path:
        """Get lock file path for a cache file"""
        return cache_path.with_suffix('.lock')

    def save(self, broker: str, data: Dict[str, Any], currency: str = "INR", account_name: str = "primary") -> bool:
        """
        Save portfolio data to cache

        Args:
            broker: Broker name (zerodha, trading212, combined)
            data: Portfolio data dictionary
            currency: Currency code
            account_name: Account identifier

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            cache_path = self._get_cache_path(broker, currency, account_name)
            lock_path = self._get_lock_path(cache_path)

            # Add metadata
            cache_data = {
                'broker': broker,
                'currency': currency,
                'account_name': account_name,
                'cached_at': datetime.now().isoformat(),
                'data': data
            }

            # Use file lock to prevent concurrent writes
            with FileLock(str(lock_path), timeout=5):
                with open(cache_path, 'w') as f:
                    json.dump(cache_data, f, indent=2, default=str)

            logger.info(f"Cached portfolio data for {broker}:{account_name} ({currency})")
            return True

        except Exception as e:
            logger.error(f"Error saving cache for {broker}:{account_name}: {e}")
            return False

    def load(self, broker: str, currency: str = "INR", account_name: str = "primary") -> Optional[Dict[str, Any]]:
        """
        Load portfolio data from cache

        Args:
            broker: Broker name (zerodha, trading212, combined)
            currency: Currency code
            account_name: Account identifier

        Returns:
            Cached data dictionary or None if not found/expired
        """
        try:
            cache_path = self._get_cache_path(broker, currency, account_name)

            if not cache_path.exists():
                logger.debug(f"No cache file found for {broker}:{account_name} ({currency})")
                return None

            lock_path = self._get_lock_path(cache_path)

            # Use file lock to prevent reading while writing
            with FileLock(str(lock_path), timeout=5):
                with open(cache_path, 'r') as f:
                    cache_data = json.load(f)

            # Check if cache is still valid
            cached_at = datetime.fromisoformat(cache_data['cached_at'])
            age = datetime.now() - cached_at

            logger.info(f"Loaded cached data for {broker}:{account_name} ({currency}), age: {age}")

            return cache_data

        except Exception as e:
            logger.error(f"Error loading cache for {broker}:{account_name}: {e}")
            return None

    def is_valid(self, cache_data: Optional[Dict[str, Any]]) -> bool:
        """
        Check if cached data is still valid (not expired)

        Args:
            cache_data: Cache data dictionary

        Returns:
            True if cache is valid, False otherwise
        """
        if not cache_data:
            return False

        try:
            cached_at = datetime.fromisoformat(cache_data['cached_at'])
            age = datetime.now() - cached_at
            return age < self.cache_ttl
        except Exception:
            return False

    def get_age(self, cache_data: Optional[Dict[str, Any]]) -> Optional[timedelta]:
        """
        Get age of cached data

        Args:
            cache_data: Cache data dictionary

        Returns:
            Age as timedelta or None if invalid
        """
        if not cache_data:
            return None

        try:
            cached_at = datetime.fromisoformat(cache_data['cached_at'])
            return datetime.now() - cached_at
        except Exception:
            return None

    def clear(self, broker: Optional[str] = None) -> bool:
        """
        Clear cache files

        Args:
            broker: Specific broker to clear, or None to clear all

        Returns:
            True if cleared successfully
        """
        try:
            if broker:
                # Clear specific broker cache
                for cache_file in self.cache_dir.glob(f"portfolio_{broker}_*.json"):
                    cache_file.unlink()
                    lock_file = cache_file.with_suffix('.lock')
                    if lock_file.exists():
                        lock_file.unlink()
                logger.info(f"Cleared cache for {broker}")
            else:
                # Clear all cache files
                for cache_file in self.cache_dir.glob("portfolio_*.json"):
                    cache_file.unlink()
                for lock_file in self.cache_dir.glob("portfolio_*.lock"):
                    lock_file.unlink()
                logger.info("Cleared all portfolio cache")

            return True

        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

    def list_cached(self) -> list:
        """
        List all cached portfolio data

        Returns:
            List of cache file info
        """
        cached_files = []

        try:
            for cache_file in self.cache_dir.glob("portfolio_*.json"):
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    cached_files.append({
                        'file': cache_file.name,
                        'broker': data.get('broker'),
                        'account_name': data.get('account_name', 'primary'),
                        'currency': data.get('currency'),
                        'cached_at': data.get('cached_at'),
                        'age': str(self.get_age(data))
                    })
        except Exception as e:
            logger.error(f"Error listing cached files: {e}")

        return cached_files


# Global cache instance
portfolio_cache = PortfolioCache()
