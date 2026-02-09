"""Cisco CircuIT LLM provider with automatic token refresh for litellm."""

import base64
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import requests


class CiscoTokenManager:
    """Token manager for Cisco CircuIT with automatic refresh and caching."""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        app_key: Optional[str] = None,
        cache_file: str = "/tmp/.cisco_token.json",
    ) -> None:
        self.client_id = client_id or os.getenv("CISCO_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("CISCO_CLIENT_SECRET")
        self.app_key = app_key or os.getenv("CISCO_APP_KEY")
        self.cache_file = cache_file
        self.token_url = "https://id.cisco.com/oauth2/default/v1/token"

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "CISCO_CLIENT_ID and CISCO_CLIENT_SECRET environment variables must be set"
            )

    def _get_cached_token(self) -> Optional[str]:
        """Retrieve a valid token from cache if it exists and hasn't expired."""
        if not os.path.exists(self.cache_file):
            return None

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            expires_at = datetime.fromisoformat(cache_data["expires_at"])
            # Refresh 5 minutes before expiry
            if datetime.now() < expires_at - timedelta(minutes=5):
                return cache_data["access_token"]
        except (json.JSONDecodeError, KeyError, ValueError, OSError):
            pass

        return None

    def _fetch_new_token(self) -> str:
        """Fetch a new token from Cisco OAuth2 endpoint."""
        auth_value = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode("utf-8")
        ).decode("utf-8")

        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth_value}",
        }

        response = requests.post(
            self.token_url,
            headers=headers,
            data="grant_type=client_credentials",
            timeout=30,
        )
        response.raise_for_status()

        token_data = response.json()
        expires_in = token_data.get("expires_in", 3600)
        expires_at = datetime.now() + timedelta(seconds=expires_in)

        # Cache the new token
        cache_data = {
            "access_token": token_data["access_token"],
            "expires_at": expires_at.isoformat(),
        }

        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2)
            os.chmod(self.cache_file, 0o600)
        except OSError:
            pass  # Continue even if caching fails

        return token_data["access_token"]

    def get_token(self) -> str:
        """Get a valid token, using cache or fetching a new one."""
        token = self._get_cached_token()
        if token:
            return token
        return self._fetch_new_token()

    def cleanup_token_cache(self) -> None:
        """Securely delete the token cache file."""
        if not os.path.exists(self.cache_file):
            return
        try:
            with open(self.cache_file, "r+b") as f:
                length = f.seek(0, 2)
                f.seek(0)
                f.write(b"\0" * length)
            os.remove(self.cache_file)
        except OSError:
            pass


# Global token manager instance
_token_manager: Optional[CiscoTokenManager] = None


def get_token_manager() -> CiscoTokenManager:
    """Get or create the global token manager instance."""
    global _token_manager
    if _token_manager is None:
        _token_manager = CiscoTokenManager()
    return _token_manager


def get_cisco_token() -> str:
    """Convenience function to get a fresh Cisco token with automatic refresh."""
    return get_token_manager().get_token()
