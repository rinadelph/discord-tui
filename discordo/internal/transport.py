"""HTTP transport with compression support."""

import logging
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)


class CompressedTransport:
    """
    HTTP transport with automatic compression handling.
    
    Supports gzip, deflate, and brotli compression automatically.
    """
    
    def __init__(self, connector: Optional[aiohttp.BaseConnector] = None):
        """
        Initialize the compressed transport.
        
        Args:
            connector: Optional custom connector
        """
        self.connector = connector or aiohttp.TCPConnector()
    
    async def create_session(self) -> aiohttp.ClientSession:
        """
        Create a new client session with compression support.
        
        Returns:
            Configured ClientSession
        """
        # Modern aiohttp versions automatically handle:
        # - gzip compression (via Content-Encoding: gzip)
        # - deflate compression (via Content-Encoding: deflate)
        # - brotli compression (if brotli package is installed)
        
        # Create session with proper decompression
        session = aiohttp.ClientSession(
            connector=self.connector,
            # Use default decompression (handles gzip, deflate, br)
            auto_decompress=True
        )
        
        return session
    
    @staticmethod
    async def decompress_response(response: aiohttp.ClientResponse) -> bytes:
        """
        Read and decompress response body.
        
        Args:
            response: The aiohttp response
            
        Returns:
            Decompressed response body
        """
        # aiohttp automatically handles decompression
        # based on Content-Encoding header
        return await response.read()


def create_connector() -> aiohttp.BaseConnector:
    """
    Create a properly configured TCP connector for Discord API.
    
    Returns:
        Configured TCPConnector
    """
    return aiohttp.TCPConnector(
        # Connection pooling settings
        limit=100,
        limit_per_host=30,
        # SSL settings
        ssl=True,
        # Keep-alive
        keepalive_timeout=30,
        # Force close connections after use
        force_close=False,
    )
