"""HTTP client for Discord API requests."""

import logging
from typing import Optional

import aiohttp
import discord

logger = logging.getLogger(__name__)


class DiscordoHTTPClient:
    """
    Custom HTTP client for Discord API.
    
    Wraps the Discord API client with custom headers and transport settings.
    """
    
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    
    def __init__(self, token: str):
        """
        Initialize the HTTP client.
        
        Args:
            token: Discord user token
        """
        self.token = token
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def start(self) -> None:
        """Start the HTTP session."""
        if self.session:
            return
        
        headers = {
            "User-Agent": self.USER_AGENT,
        }
        
        self.session = aiohttp.ClientSession(headers=headers)
    
    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def request(self, method: str, url: str, **kwargs) -> dict:
        """
        Make an HTTP request to the Discord API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to request
            **kwargs: Additional arguments for aiohttp
            
        Returns:
            JSON response data
        """
        if not self.session:
            await self.start()
        
        # Add authorization header
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        
        kwargs["headers"]["Authorization"] = f"Bot {self.token}"
        
        try:
            async with self.session.request(method, url, **kwargs) as resp:
                if resp.status >= 400:
                    logger.error(f"HTTP {resp.status}: {resp.reason}")
                    return {}
                
                return await resp.json() if resp.status != 204 else None
        
        except Exception as err:
            logger.error(f"HTTP request failed: {err}")
            raise
    
    async def get(self, url: str, **kwargs) -> dict:
        """GET request."""
        return await self.request("GET", url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> dict:
        """POST request."""
        return await self.request("POST", url, **kwargs)
    
    async def patch(self, url: str, **kwargs) -> dict:
        """PATCH request."""
        return await self.request("PATCH", url, **kwargs)
    
    async def put(self, url: str, **kwargs) -> dict:
        """PUT request."""
        return await self.request("PUT", url, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> dict:
        """DELETE request."""
        return await self.request("DELETE", url, **kwargs)
