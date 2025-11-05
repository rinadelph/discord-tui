#!/usr/bin/env python3
"""Test authentication and basic Discord connection."""

import asyncio
import logging
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_discord_connection(token: str) -> bool:
    """
    Test Discord connection with the provided token.
    
    Args:
        token: Discord user token
        
    Returns:
        True if connection successful, False otherwise
    """
    try:
        import discord
        
        logger.info("Creating Discord client...")
        client = discord.Client(intents=discord.Intents.default())
        
        @client.event
        async def on_ready():
            logger.info(f"✓ Logged in as {client.user}")
            logger.info(f"✓ User ID: {client.user.id}")
            logger.info(f"✓ Connected to Discord")
            await client.close()
        
        logger.info("Attempting to connect to Discord...")
        await asyncio.wait_for(
            client.start(token),
            timeout=10.0
        )
        return True
        
    except asyncio.TimeoutError:
        logger.error("✗ Connection timeout - check your internet")
        return False
    except discord.LoginFailure:
        logger.error("✗ Login failed - token is invalid or expired")
        return False
    except Exception as e:
        logger.error(f"✗ Connection error: {e}")
        return False

async def main():
    """Main test function."""
    import keyring
    from discordo.internal.consts import DISCORDO_NAME
    from discordo.internal.config import Config
    
    logger.info("="*60)
    logger.info("Discordo Authentication Test")
    logger.info("="*60)
    
    # Load config
    try:
        cfg = Config.load("/home/alejandro/.config/discordo/config.toml")
        logger.info(f"✓ Config loaded")
    except Exception as e:
        logger.error(f"✗ Failed to load config: {e}")
        return False
    
    # Get token from command line or keyring
    token = None
    
    if len(sys.argv) > 1:
        token = sys.argv[1]
        logger.info(f"✓ Token provided via command line")
        # Store it in keyring
        try:
            keyring.set_password(DISCORDO_NAME, 'token', token)
            logger.info(f"✓ Token stored in keyring")
        except Exception as e:
            logger.warning(f"Could not store token in keyring: {e}")
    else:
        # Try to get from keyring
        try:
            token = keyring.get_password(DISCORDO_NAME, 'token')
            if token:
                logger.info(f"✓ Token retrieved from keyring")
            else:
                logger.error("✗ No token in keyring and none provided")
                logger.info("Usage: python test_auth.py YOUR_TOKEN_HERE")
                return False
        except Exception as e:
            logger.error(f"✗ Failed to get token from keyring: {e}")
            return False
    
    # Test connection
    logger.info("\nAttempting to connect to Discord...")
    success = await test_discord_connection(token)
    
    logger.info("="*60)
    if success:
        logger.info("✓ All tests passed! You're ready to run Discordo")
        return True
    else:
        logger.error("✗ Tests failed. Check your token and internet connection")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
