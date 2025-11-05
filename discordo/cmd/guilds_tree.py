"""Guilds tree view for Discordo."""

import asyncio
import logging
from typing import Optional, List, Dict, Callable

import discord
from textual.widgets import Tree
from textual.widgets.tree import TreeNode

from discordo.internal.config import Config

logger = logging.getLogger(__name__)


class GuildsTree(Tree):
    """
    Tree view for guilds, channels, and direct messages.
    
    Shows a hierarchical view of:
    - Direct Messages
    - Guilds (Servers)
      - Channels
        - Sub-channels
    """
    
    def __init__(
        self,
        cfg: Config,
        discord_state,
        on_channel_selected: Optional[Callable] = None,
        **kwargs
    ):
        """
        Initialize the guilds tree.
        
        Args:
            cfg: Configuration
            discord_state: Discord state manager
            on_channel_selected: Callback when channel is selected
        """
        super().__init__("Root", **kwargs)
        self.cfg = cfg
        self.discord_state = discord_state
        self.on_channel_selected = on_channel_selected
        
        self.selected_channel_id: Optional[int] = None
        self.selected_guild_id: Optional[int] = None
        
        # Hide root node
        self.root.display = False
        self.root.expand()
    
    async def load_guilds(self, user: discord.User, guilds: List[discord.Guild]) -> None:
        """
        Load and display guilds and DMs.
        
        Args:
            user: Current user
            guilds: List of guilds
        """
        try:
            # Clear existing
            self.root.children.clear()
            
            # Add Direct Messages
            await self._add_dms(user)
            
            # Add Guilds
            for guild in sorted(guilds, key=lambda g: g.name):
                await self._add_guild(guild)
            
            logger.info(f"Loaded {len(guilds)} guilds and DMs")
            
        except Exception as e:
            logger.error(f"Error loading guilds: {e}", exc_info=e)
    
    async def _add_dms(self, user: discord.User) -> None:
        """Add direct messages section."""
        try:
            # Get all private channels (DMs and group DMs)
            private_channels = []
            
            # Find DM channels from guilds and direct messages
            if hasattr(user, '_connection') and user._connection:
                # Try to get from client's private channels
                try:
                    # Collect DM channels
                    dm_channels = []
                    
                    # Iterate through all Discord objects to find DMs
                    # This is a bit hacky but works with discord.py
                    if hasattr(user, 'dm_channel'):
                        dm_channels.append(user.dm_channel)
                    
                    private_channels = dm_channels
                except Exception as e:
                    logger.debug(f"Could not get DM channels: {e}")
            
            # Create DM folder
            dm_node = self.root.add("💬 Direct Messages")
            dm_node.data = {"type": "dm_folder", "id": None}
            
            # For now, just show the section
            # In a full implementation, we'd enumerate actual DMs
            
            logger.debug("Added Direct Messages section")
            
        except Exception as e:
            logger.error(f"Error adding DMs: {e}")
    
    async def _add_guild(self, guild: discord.Guild) -> None:
        """
        Add a guild and its channels to the tree.
        
        Args:
            guild: The guild to add
        """
        try:
            # Create guild node
            guild_node = self.root.add(f"🏢 {guild.name}")
            guild_node.data = {"type": "guild", "id": guild.id}
            
            # Get and sort channels
            try:
                channels = list(guild.channels)
                
                # Separate by type
                categories = [ch for ch in channels if isinstance(ch, discord.CategoryChannel)]
                text_channels = [ch for ch in channels if isinstance(ch, discord.TextChannel)]
                voice_channels = [ch for ch in channels if isinstance(ch, discord.VoiceChannel)]
                
                # Add uncategorized channels
                for channel in text_channels:
                    if channel.category is None:
                        await self._add_channel(guild_node, channel)
                
                for channel in voice_channels:
                    if channel.category is None:
                        await self._add_channel(guild_node, channel)
                
                # Add categorized channels
                for category in sorted(categories, key=lambda c: c.position):
                    cat_node = guild_node.add(f"📁 {category.name}")
                    cat_node.data = {"type": "category", "id": category.id}
                    
                    # Add channels in this category
                    for channel in sorted(
                        [ch for ch in channels if ch.category == category],
                        key=lambda c: c.position
                    ):
                        await self._add_channel(cat_node, channel)
                
                logger.debug(f"Added guild {guild.name} with {len(channels)} channels")
                
            except Exception as e:
                logger.error(f"Error loading channels for {guild.name}: {e}")
        
        except Exception as e:
            logger.error(f"Error adding guild {guild.name}: {e}")
    
    async def _add_channel(self, parent_node: TreeNode, channel: discord.abc.GuildChannel) -> None:
        """
        Add a channel to the tree.
        
        Args:
            parent_node: Parent tree node
            channel: The channel to add
        """
        try:
            if isinstance(channel, discord.TextChannel):
                icon = "#"
                label = channel.name
            elif isinstance(channel, discord.VoiceChannel):
                icon = "🔊"
                label = channel.name
            elif isinstance(channel, discord.StageChannel):
                icon = "📻"
                label = channel.name
            else:
                icon = "•"
                label = channel.name
            
            # Check permissions
            can_view = True
            try:
                if hasattr(channel, 'permissions_for'):
                    # Would need current member context
                    pass
            except Exception:
                pass
            
            if can_view:
                node = parent_node.add(f"{icon} {label}")
                node.data = {"type": "channel", "id": channel.id}
        
        except Exception as e:
            logger.error(f"Error adding channel: {e}")
    
    async def select_channel(self, channel_id: int) -> Optional[discord.abc.GuildChannel]:
        """
        Select a channel and load its messages.
        
        Args:
            channel_id: ID of channel to select
            
        Returns:
            The selected channel or None
        """
        try:
            channel = self.discord_state.get_channel(channel_id)
            
            if channel:
                self.selected_channel_id = channel_id
                
                if isinstance(channel, discord.TextChannel):
                    self.selected_guild_id = channel.guild.id
                
                # Callback to load messages
                if self.on_channel_selected:
                    messages = await self.discord_state.get_messages(channel_id, self.cfg.messages_limit)
                    self.on_channel_selected(channel, messages)
                
                return channel
            
        except Exception as e:
            logger.error(f"Error selecting channel: {e}")
        
        return None
    
    def action_select_channel(self, node: TreeNode) -> None:
        """Handle channel selection."""
        if not node.data:
            return
        
        node_type = node.data.get("type")
        node_id = node.data.get("id")
        
        if node_type == "channel":
            asyncio.create_task(self.select_channel(node_id))
