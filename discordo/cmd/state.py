"""Discord state management for Discordo."""

import asyncio
import logging
from typing import Optional, Callable, Any

import discord
from discord.ext import commands

from discordo.internal.config import Config
from discordo.internal.http_client import DiscordoHTTPClient

logger = logging.getLogger(__name__)


class DiscordState:
    """
    Manages Discord connection and state.
    
    Uses discord.py with USER TOKEN authentication (not bot token).
    """
    
    def __init__(self, token: str, cfg: Config):
        """
        Initialize Discord state.
        
        Args:
            token: Discord user token
            cfg: Configuration object
        """
        self.token = token
        self.cfg = cfg
        self.client: Optional[discord.Client] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        
        # Cache
        self._guilds_cache = {}
        self._channels_cache = {}
        self._messages_cache = {}
        
        # Event handlers
        self._handlers = {
            'ready': [],
            'message': [],
            'message_edit': [],
            'message_delete': [],
            'raw_message_edit': [],
            'raw_message_delete': [],
        }
    
    def add_handler(self, event_name: str, handler: Callable) -> None:
        """
        Add an event handler.
        
        Args:
            event_name: Name of the event ('ready', 'message', etc.)
            handler: Callable to handle the event
        """
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        self._handlers[event_name].append(handler)
    
    async def _on_ready(self) -> None:
        """Handle ready event."""
        logger.info(f"Connected as {self.client.user}")
        
        # Call registered handlers
        for handler in self._handlers['ready']:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(self.client.user)
                else:
                    handler(self.client.user)
            except Exception as err:
                logger.error(f"Error in ready handler: {err}", exc_info=err)
    
    async def _on_message(self, message: discord.Message) -> None:
        """
        Handle message event.
        
        Args:
            message: The message object
        """
        if message.author == self.client.user:
            return  # Ignore own messages
        
        # Call registered handlers
        for handler in self._handlers['message']:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            except Exception as err:
                logger.error(f"Error in message handler: {err}", exc_info=err)
    
    async def _on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        """
        Handle message edit event.
        
        Args:
            before: Message before edit
            after: Message after edit
        """
        # Call registered handlers
        for handler in self._handlers['message_edit']:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(before, after)
                else:
                    handler(before, after)
            except Exception as err:
                logger.error(f"Error in message_edit handler: {err}", exc_info=err)
    
    async def _on_message_delete(self, message: discord.Message) -> None:
        """
        Handle message delete event.
        
        Args:
            message: The deleted message
        """
        # Call registered handlers
        for handler in self._handlers['message_delete']:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            except Exception as err:
                logger.error(f"Error in message_delete handler: {err}", exc_info=err)
    
    async def _on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent) -> None:
        """
        Handle raw message edit event.
        
        Args:
            payload: The raw message update payload
        """
        # Call registered handlers
        for handler in self._handlers['raw_message_edit']:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(payload)
                else:
                    handler(payload)
            except Exception as err:
                logger.error(f"Error in raw_message_edit handler: {err}", exc_info=err)
    
    async def _on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent) -> None:
        """
        Handle raw message delete event.
        
        Args:
            payload: The raw message delete payload
        """
        # Call registered handlers
        for handler in self._handlers['raw_message_delete']:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(payload)
                else:
                    handler(payload)
            except Exception as err:
                logger.error(f"Error in raw_message_delete handler: {err}", exc_info=err)
    
    async def _setup_client(self) -> None:
        """Setup the Discord client with event handlers."""
        # Create a custom client with user token authentication
        intents = discord.Intents.default()
        intents.message_content = True
        
        self.client = discord.Client(intents=intents)
        
        # Register event handlers
        self.client.event(self._on_ready)
        self.client.event(self._on_message)
        self.client.event(self._on_message_edit)
        self.client.event(self._on_message_delete)
        self.client.event(self._on_raw_message_edit)
        self.client.event(self._on_raw_message_delete)
    
    def start(self) -> None:
        """
        Start the Discord connection.
        
        Note: This should be called in a separate thread or async context.
        """
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            # Setup client
            self.loop.run_until_complete(self._setup_client())
            
            # Start the client with user token
            # Note: discord.py sends "Bot" prefix for bot tokens and nothing for user tokens
            # We need to use a custom approach or modified discord.py
            logger.info("Starting Discord client...")
            self.loop.run_until_complete(self.client.start(self.token, bot=False))
        except Exception as err:
            logger.error(f"Failed to start Discord client: {err}", exc_info=err)
            raise
    
    def close(self) -> None:
        """Close the Discord connection."""
        if self.client and self.loop:
            try:
                self.loop.run_until_complete(self.client.close())
            except Exception as err:
                logger.error(f"Error closing client: {err}")
    
    def get_guilds(self) -> list:
        """
        Get list of guilds the user is in.
        
        Returns:
            List of Guild objects
        """
        if self.client:
            return list(self.client.guilds)
        return []
    
    def get_guild(self, guild_id: int) -> Optional[discord.Guild]:
        """
        Get a specific guild by ID.
        
        Args:
            guild_id: The guild ID
            
        Returns:
            Guild object or None if not found
        """
        if self.client:
            return self.client.get_guild(guild_id)
        return None
    
    def get_channels(self, guild_id: Optional[int] = None) -> list:
        """
        Get channels for a guild or all DM channels.
        
        Args:
            guild_id: Guild ID or None for DM channels
            
        Returns:
            List of Channel objects
        """
        if not self.client:
            return []
        
        if guild_id is None:
            # Return private channels (DMs)
            return self.client.private_channels
        else:
            guild = self.get_guild(guild_id)
            if guild:
                return list(guild.channels)
        
        return []
    
    def get_channel(self, channel_id: int) -> Optional[discord.abc.Messageable]:
        """
        Get a channel by ID.
        
        Args:
            channel_id: The channel ID
            
        Returns:
            Channel object or None if not found
        """
        if self.client:
            return self.client.get_channel(channel_id)
        return None
    
    async def get_messages(self, channel_id: int, limit: int = 50) -> list:
        """
        Get messages from a channel.
        
        Args:
            channel_id: The channel ID
            limit: Maximum number of messages to fetch
            
        Returns:
            List of Message objects
        """
        channel = self.get_channel(channel_id)
        if channel:
            try:
                messages = await channel.history(limit=limit).flatten()
                return list(reversed(messages))  # Oldest first
            except Exception as err:
                logger.error(f"Failed to get messages: {err}")
        
        return []
    
    async def send_message(self, channel_id: int, content: str) -> Optional[discord.Message]:
        """
        Send a message to a channel.
        
        Args:
            channel_id: The channel ID
            content: Message content
            
        Returns:
            Sent message or None if failed
        """
        channel = self.get_channel(channel_id)
        if channel:
            try:
                return await channel.send(content)
            except Exception as err:
                logger.error(f"Failed to send message: {err}")
        
        return None
    
    async def edit_message(
        self,
        channel_id: int,
        message_id: int,
        content: str
    ) -> Optional[discord.Message]:
        """
        Edit a message.
        
        Args:
            channel_id: The channel ID
            message_id: The message ID
            content: New message content
            
        Returns:
            Edited message or None if failed
        """
        channel = self.get_channel(channel_id)
        if channel:
            try:
                message = await channel.fetch_message(message_id)
                return await message.edit(content=content)
            except Exception as err:
                logger.error(f"Failed to edit message: {err}")
        
        return None
    
    async def delete_message(self, channel_id: int, message_id: int) -> bool:
        """
        Delete a message.
        
        Args:
            channel_id: The channel ID
            message_id: The message ID
            
        Returns:
            True if successful, False otherwise
        """
        channel = self.get_channel(channel_id)
        if channel:
            try:
                message = await channel.fetch_message(message_id)
                await message.delete()
                return True
            except Exception as err:
                logger.error(f"Failed to delete message: {err}")
        
        return False
