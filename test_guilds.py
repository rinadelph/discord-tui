#!/usr/bin/env python3
"""Test guilds loading."""

import asyncio
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_guilds_loading(token: str):
    """Test loading guilds from Discord."""
    import discord
    
    logger.info("Creating Discord client...")
    intents = discord.Intents.default()
    intents.message_content = True
    
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        logger.info(f"✓ Logged in as {client.user}")
        logger.info(f"✓ User ID: {client.user.id}")
        logger.info(f"✓ Guilds count: {len(client.guilds)}")
        
        # Display guilds and channels
        logger.info("\n" + "="*60)
        logger.info("GUILD STRUCTURE")
        logger.info("="*60)
        
        for guild in sorted(client.guilds, key=lambda g: g.name)[:5]:  # Show first 5
            logger.info(f"\n🏢 {guild.name} (ID: {guild.id})")
            logger.info(f"   Members: {len(guild.members)}")
            
            channels = list(guild.channels)
            categories = [ch for ch in channels if isinstance(ch, discord.CategoryChannel)]
            text_channels = [ch for ch in channels if isinstance(ch, discord.TextChannel)]
            voice_channels = [ch for ch in channels if isinstance(ch, discord.VoiceChannel)]
            
            logger.info(f"   Channels: {len(text_channels)} text, {len(voice_channels)} voice, {len(categories)} categories")
            
            # Show first few channels
            for channel in text_channels[:3]:
                logger.info(f"     # {channel.name}")
            
            for channel in voice_channels[:2]:
                logger.info(f"     🔊 {channel.name}")
            
            if len(text_channels) > 3 or len(voice_channels) > 2:
                logger.info(f"     ... and more")
        
        if len(client.guilds) > 5:
            logger.info(f"\n... and {len(client.guilds) - 5} more guilds")
        
        logger.info("\n" + "="*60)
        logger.info("✓ Guild loading test passed!")
        logger.info("="*60)
        
        await client.close()
    
    try:
        await asyncio.wait_for(client.start(token), timeout=15.0)
        return True
    except asyncio.TimeoutError:
        logger.error("✗ Connection timeout")
        return False
    except discord.LoginFailure:
        logger.error("✗ Login failed - invalid token")
        return False
    except Exception as e:
        logger.error(f"✗ Error: {e}", exc_info=e)
        return False

async def main():
    """Main test."""
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        # Try to get from keyring
        import keyring
        from discordo.internal.consts import DISCORDO_NAME
        
        try:
            token = keyring.get_password(DISCORDO_NAME, 'token')
            if not token:
                logger.error("No token provided and none in keyring")
                logger.info("Usage: python test_guilds.py YOUR_TOKEN")
                return False
        except Exception as e:
            logger.error(f"Failed to get token: {e}")
            return False
    
    logger.info("Testing guilds loading...")
    return await test_guilds_loading(token)

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
