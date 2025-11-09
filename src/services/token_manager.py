"""
Token Manager Service
Securely stores and manages broker authentication tokens
"""
import json
import base64
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging
from cryptography.fernet import Fernet
import os

logger = logging.getLogger(__name__)


class TokenManager:
    """
    Manages broker authentication tokens with encryption
    """

    def __init__(self):
        self.tokens_dir = Path("data/tokens")
        self.tokens_file = self.tokens_dir / "broker_tokens.enc"
        self.tokens_dir.mkdir(parents=True, exist_ok=True)

        # Get or create encryption key
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)

        # Load existing tokens
        self.tokens = self._load_tokens()

    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = self.tokens_dir / ".key"

        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            logger.info("Created new encryption key")
            return key

    def _load_tokens(self) -> Dict:
        """Load tokens from encrypted file"""
        if not self.tokens_file.exists():
            return {}

        try:
            with open(self.tokens_file, 'rb') as f:
                encrypted_data = f.read()

            decrypted_data = self.cipher.decrypt(encrypted_data)
            tokens = json.loads(decrypted_data.decode())
            logger.info("Loaded encrypted tokens")
            return tokens
        except Exception as e:
            logger.error(f"Error loading tokens: {e}")
            return {}

    def _save_tokens(self):
        """Save tokens to encrypted file"""
        try:
            # Convert to JSON
            data = json.dumps(self.tokens, indent=2)

            # Encrypt
            encrypted_data = self.cipher.encrypt(data.encode())

            # Save
            with open(self.tokens_file, 'wb') as f:
                f.write(encrypted_data)

            logger.info("Saved encrypted tokens")
        except Exception as e:
            logger.error(f"Error saving tokens: {e}")
            raise

    def save_zerodha_token(
        self,
        api_key: str,
        api_secret: str,
        access_token: str,
        request_token: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        account_name: str = "primary"
    ):
        """
        Save Zerodha authentication tokens for a specific account

        Args:
            api_key: Zerodha API key
            api_secret: Zerodha API secret
            access_token: Zerodha access token
            request_token: Optional request token
            expires_at: Token expiration time (default: end of day)
            account_name: Account identifier (e.g., 'primary', 'spouse', 'parent')
        """
        if expires_at is None:
            # Zerodha tokens expire at end of day
            expires_at = datetime.now().replace(hour=23, minute=59, second=59)

        # Initialize zerodha dict if it doesn't exist or isn't a dict
        if 'zerodha' not in self.tokens or not isinstance(self.tokens.get('zerodha'), dict):
            self.tokens['zerodha'] = {}

        # For backward compatibility, migrate old format
        if 'api_key' in self.tokens.get('zerodha', {}):
            old_data = self.tokens['zerodha'].copy()
            self.tokens['zerodha'] = {'primary': old_data}

        self.tokens['zerodha'][account_name] = {
            'api_key': api_key,
            'api_secret': api_secret,
            'access_token': access_token,
            'request_token': request_token,
            'expires_at': expires_at.isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        self._save_tokens()
        logger.info(f"Saved Zerodha tokens for account: {account_name}")

    def save_trading212_token(
        self,
        api_key: str,
        api_secret: Optional[str] = None,
        account_name: str = "primary"
    ):
        """
        Save Trading212 API credentials for a specific account

        Args:
            api_key: Trading212 API key
            api_secret: Trading212 API secret (optional)
            account_name: Account identifier (e.g., 'primary', 'spouse', 'child')
        """
        # Initialize trading212 dict if it doesn't exist or isn't a dict
        if 'trading212' not in self.tokens or not isinstance(self.tokens.get('trading212'), dict):
            self.tokens['trading212'] = {}

        # For backward compatibility, migrate old format
        if 'api_key' in self.tokens.get('trading212', {}):
            old_data = self.tokens['trading212'].copy()
            self.tokens['trading212'] = {'primary': old_data}

        self.tokens['trading212'][account_name] = {
            'api_key': api_key,
            'api_secret': api_secret,
            'updated_at': datetime.now().isoformat()
        }

        self._save_tokens()
        logger.info(f"Saved Trading212 tokens for account: {account_name}")

    def get_zerodha_token(self, account_name: str = "primary") -> Optional[Dict]:
        """
        Get Zerodha authentication tokens for a specific account

        Args:
            account_name: Account identifier (default: 'primary')

        Returns:
            Dictionary with tokens or None if not found/expired
        """
        zerodha_data = self.tokens.get('zerodha', {})

        # Handle backward compatibility - if old format, migrate and return
        if 'api_key' in zerodha_data:
            old_data = zerodha_data.copy()
            self.tokens['zerodha'] = {'primary': old_data}
            self._save_tokens()
            zerodha_data = self.tokens['zerodha']

        zerodha_tokens = zerodha_data.get(account_name)

        if not zerodha_tokens:
            logger.warning(f"No Zerodha tokens found for account: {account_name}")
            return None

        # Check expiration
        expires_at = datetime.fromisoformat(zerodha_tokens['expires_at'])
        if datetime.now() > expires_at:
            logger.warning(f"Zerodha tokens expired for account: {account_name}")
            return None

        return zerodha_tokens

    def get_trading212_token(self, account_name: str = "primary") -> Optional[Dict]:
        """
        Get Trading212 API credentials for a specific account

        Args:
            account_name: Account identifier (default: 'primary')

        Returns:
            Dictionary with credentials or None if not found
        """
        trading212_data = self.tokens.get('trading212', {})

        # Handle backward compatibility - if old format, migrate and return
        if 'api_key' in trading212_data:
            old_data = trading212_data.copy()
            self.tokens['trading212'] = {'primary': old_data}
            self._save_tokens()
            trading212_data = self.tokens['trading212']

        trading212_tokens = trading212_data.get(account_name)

        if not trading212_tokens:
            logger.warning(f"No Trading212 tokens found for account: {account_name}")
            return None

        return trading212_tokens

    def delete_zerodha_token(self, account_name: Optional[str] = None):
        """
        Delete Zerodha tokens for a specific account or all accounts

        Args:
            account_name: Specific account to delete, or None to delete all
        """
        if 'zerodha' in self.tokens:
            if account_name:
                if account_name in self.tokens['zerodha']:
                    del self.tokens['zerodha'][account_name]
                    logger.info(f"Deleted Zerodha tokens for account: {account_name}")
            else:
                del self.tokens['zerodha']
                logger.info("Deleted all Zerodha tokens")
            self._save_tokens()

    def delete_trading212_token(self, account_name: Optional[str] = None):
        """
        Delete Trading212 tokens for a specific account or all accounts

        Args:
            account_name: Specific account to delete, or None to delete all
        """
        if 'trading212' in self.tokens:
            if account_name:
                if account_name in self.tokens['trading212']:
                    del self.tokens['trading212'][account_name]
                    logger.info(f"Deleted Trading212 tokens for account: {account_name}")
            else:
                del self.tokens['trading212']
                logger.info("Deleted all Trading212 tokens")
            self._save_tokens()

    def list_zerodha_accounts(self) -> list:
        """List all Zerodha account names"""
        zerodha_data = self.tokens.get('zerodha', {})
        if 'api_key' in zerodha_data:  # Old format
            return ['primary']
        return list(zerodha_data.keys())

    def list_trading212_accounts(self) -> list:
        """List all Trading212 account names"""
        trading212_data = self.tokens.get('trading212', {})
        if 'api_key' in trading212_data:  # Old format
            return ['primary']
        return list(trading212_data.keys())

    def get_all_tokens_status(self) -> Dict:
        """
        Get status of all broker tokens

        Returns:
            Dictionary with broker status
        """
        status = {}

        # Zerodha status
        zerodha = self.get_zerodha_token()
        if zerodha:
            expires_at = datetime.fromisoformat(zerodha['expires_at'])
            status['zerodha'] = {
                'connected': True,
                'expires_at': zerodha['expires_at'],
                'expires_in_hours': (expires_at - datetime.now()).total_seconds() / 3600,
                'api_key': zerodha['api_key'][:8] + '...'
            }
        else:
            status['zerodha'] = {
                'connected': False
            }

        # Trading212 status
        trading212 = self.get_trading212_token()
        if trading212:
            status['trading212'] = {
                'connected': True,
                'api_key': trading212['api_key'][:8] + '...',
                'updated_at': trading212['updated_at']
            }
        else:
            status['trading212'] = {
                'connected': False
            }

        return status

    def is_zerodha_connected(self) -> bool:
        """Check if Zerodha is connected"""
        return self.get_zerodha_token() is not None

    def is_trading212_connected(self) -> bool:
        """Check if Trading212 is connected"""
        return self.get_trading212_token() is not None


# Global instance
token_manager = TokenManager()
