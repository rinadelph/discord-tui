"""Messages list view for Discordo."""

import asyncio
import logging
import re
from datetime import datetime
from typing import Optional, List, Dict, Callable

import discord
from textual.widgets import RichLog
from rich.text import Text
from rich.console import Console
# from textual_image.widget import Image  # TODO: enable when using image rendering

from discordo.internal.config import Config

logger = logging.getLogger(__name__)


class MessagesList(RichLog):
    """
    Display messages in a rich log widget.
    
    Handles rendering messages with formatting, embeds, reactions, and images.
    """
    
    def __init__(self, cfg: Config, discord_state, on_message_selected=None):
        """
        Initialize the messages list.
        
        Args:
            cfg: Configuration object
            discord_state: Discord state manager
            on_message_selected: Callback when a message is selected
        """
        super().__init__()
        self.cfg = cfg
        self.discord_state = discord_state
        self.on_message_selected = on_message_selected
        
        self.selected_message_id: Optional[int] = None
        self.selected_channel_id: Optional[int] = None
        self.selected_guild_id: Optional[int] = None
        
        # Message cache
        self._messages: Dict[int, discord.Message] = {}
        self._rendered_messages: List[int] = []
    
    def reset(self) -> None:
        """Clear the messages list."""
        self.selected_message_id = None
        self.selected_channel_id = None
        self.selected_guild_id = None
        self._messages.clear()
        self._rendered_messages.clear()
        self.clear()
    
    def set_title(self, channel: discord.abc.GuildChannel) -> None:
        """
        Set the title based on channel info.
        
        Args:
            channel: The Discord channel
        """
        title = f"#{channel.name}" if hasattr(channel, 'name') else str(channel)
        if hasattr(channel, 'topic') and channel.topic:
            title += f" - {channel.topic}"
        # TODO: Update widget title when implemented
    
    async def draw_messages(self, messages: List[discord.Message]) -> None:
        """
        Draw multiple messages.
        
        Args:
            messages: List of messages to display
        """
        for message in reversed(messages):
            await self.draw_message(message)
    
    async def draw_message(self, message: discord.Message) -> None:
        """
        Draw a single message with all formatting.
        
        Args:
            message: The message to display
        """
        # Cache the message
        self._messages[message.id] = message
        self._rendered_messages.append(message.id)
        
        # Check if user is blocked
        if self.cfg.hide_blocked_users:
            # TODO: Check if user is blocked
            pass
        
        # Render based on message type
        if message.type == discord.MessageType.default:
            if message.reference and getattr(message.reference, 'type', None) == 'forward':
                await self._draw_forwarded_message(message)
            else:
                await self._draw_default_message(message)
        elif message.type == discord.MessageType.user_join:
            await self._draw_user_joined(message)
        elif message.type == discord.MessageType.reply:
            await self._draw_reply_message(message)
        elif message.type == discord.MessageType.channel_pinned_message:
            await self._draw_pinned_message(message)
        else:
            await self._draw_default_message(message)
        
        self.write(Text())  # New line
    
    def _format_timestamp(self, ts: datetime) -> str:
        """
        Format a timestamp according to config.
        
        Args:
            ts: The timestamp to format
            
        Returns:
            Formatted timestamp string
        """
        return ts.strftime(self.cfg.timestamps.format)
    
    async def _draw_timestamp(self, ts: datetime) -> None:
        """
        Draw a timestamp.
        
        Args:
            ts: The timestamp to display
        """
        if not self.cfg.timestamps.enabled:
            return
        
        formatted = self._format_timestamp(ts)
        self.write(Text(f"{formatted} ", style="dim"))
    
    async def _draw_author(self, message: discord.Message) -> None:
        """
        Draw the message author.
        
        Args:
            message: The message containing author info
        """
        name = message.author.display_name or message.author.name
        
        # Check if this is our message
        try:
            current_user = self.discord_state.client.user
            is_own_message = message.author.id == current_user.id
        except Exception:
            is_own_message = False
        
        # Color for our messages is blue
        if is_own_message:
            style = "bold blue"
        else:
            # TODO: Get member color from guild
            style = "bold"
        
        self.write(Text(name, style=style))
        self.write(Text(" ", style=style))
        
        # Draw status indicator for non-self messages
        if not is_own_message:
            await self._draw_user_status(message.author.id)
    
    async def _draw_user_status(self, user_id: int) -> None:
        """
        Draw user online status indicator.
        
        Args:
            user_id: The user ID to check status for
        """
        # TODO: Get presence from Discord state
        status_map = {
            discord.Status.online: ("●", "green"),
            discord.Status.idle: ("◐", "yellow"),
            discord.Status.dnd: ("⊘", "red"),
            discord.Status.offline: ("○", "gray"),
        }
        
        # Default to offline
        indicator, color = "○", "gray"
        
        self.write(Text(indicator, style=color))
        self.write(Text(" ", style=color))
    
    async def _draw_content(self, message: discord.Message) -> None:
        """
        Draw message content with markdown rendering.
        
        Args:
            message: The message containing content
        """
        if not message.content:
            return
        
        if self.cfg.markdown:
            # TODO: Render markdown using discordmd equivalent
            self.write(Text(message.content))
        else:
            self.write(Text(message.content))
        
        # Show edit indicator
        if message.edited_at:
            self.write(Text(" (edited)", style="dim"))
    
    async def _draw_attachment(self, attachment: discord.Attachment) -> None:
        """
        Draw an attachment link.
        
        Args:
            attachment: The attachment to display
        """
        if self.cfg.show_attachment_links:
            text = f"{attachment.filename}: {attachment.url}"
        else:
            text = attachment.filename
        
        self.write(Text(text, style="yellow"))
        self.write(Text("\n"))
    
    async def _draw_reactions(self, reactions: List[discord.Reaction]) -> None:
        """
        Draw message reactions.
        
        Args:
            reactions: List of reactions on the message
        """
        if not reactions:
            return
        
        self.write(Text("\n"))
        reaction_texts = []
        for reaction in reactions:
            emoji_name = reaction.emoji.name if hasattr(reaction.emoji, 'name') else str(reaction.emoji)
            reaction_texts.append(f"{emoji_name} {reaction.count}")
        
        self.write(Text(" ".join(reaction_texts), style="dim"))
    
    async def _draw_embeds(self, embeds: List[discord.Embed]) -> None:
        """
        Draw embed content.
        
        Args:
            embeds: List of embeds to display
        """
        for embed in embeds:
            self.write(Text("\n"))
            
            # Title
            if embed.title:
                self.write(Text(f"┃ ", style="yellow"))
                self.write(Text(embed.title, style="bold yellow"))
                self.write(Text("\n"))
            
            # Author
            if embed.author and embed.author.name:
                self.write(Text(f"┃ ", style="yellow"))
                self.write(Text(embed.author.name, style="dim"))
                self.write(Text("\n"))
            
            # Description
            if embed.description:
                for line in embed.description.split("\n"):
                    self.write(Text(f"┃ ", style="yellow"))
                    self.write(Text(line))
                    self.write(Text("\n"))
            
            # Fields
            if embed.fields:
                for field in embed.fields:
                    self.write(Text(f"┃ ", style="yellow"))
                    self.write(Text(field.name, style="bold yellow"))
                    self.write(Text(f": {field.value}\n"))
            
            # Image
            if embed.image:
                self.write(Text(f"┃ ", style="yellow"))
                if self.cfg.show_attachment_links:
                    self.write(Text(f"Image: {embed.image.url}\n", style="underline"))
                else:
                    self.write(Text("[Image]\n", style="dim"))
            
            # Thumbnail
            if embed.thumbnail:
                self.write(Text(f"┃ ", style="yellow"))
                if self.cfg.show_attachment_links:
                    self.write(Text(f"Thumbnail: {embed.thumbnail.url}\n", style="underline"))
                else:
                    self.write(Text("[Thumbnail]\n", style="dim"))
            
            # URL
            if embed.url:
                self.write(Text(f"┃ ", style="yellow"))
                self.write(Text(f"{embed.url}\n", style="underline"))
            
            # Footer
            if embed.footer and embed.footer.text:
                self.write(Text(f"┃ ", style="yellow"))
                self.write(Text(embed.footer.text, style="dim"))
                self.write(Text("\n"))
    
    async def _draw_default_message(self, message: discord.Message) -> None:
        """
        Draw a standard message.
        
        Args:
            message: The message to display
        """
        await self._draw_timestamp(message.created_at)
        await self._draw_author(message)
        await self._draw_content(message)
        
        # Draw embeds
        if message.embeds:
            await self._draw_embeds(message.embeds)
        
        # Draw attachments
        for attachment in message.attachments:
            self.write(Text("\n"))
            await self._draw_attachment(attachment)
        
        # Draw reactions
        if message.reactions:
            await self._draw_reactions(message.reactions)
    
    async def _draw_forwarded_message(self, message: discord.Message) -> None:
        """
        Draw a forwarded/snapshot message.
        
        Args:
            message: The forwarded message
        """
        await self._draw_timestamp(message.created_at)
        await self._draw_author(message)
        self.write(Text(f"{self.cfg.theme['messages_list'].get('forwarded_indicator', '<')} "))
        
        # Show snapshot content if available
        if hasattr(message, 'message_snapshots') and message.message_snapshots:
            snapshot = message.message_snapshots[0]
            self.write(Text(snapshot.message.content))
            self.write(Text(f" ({self._format_timestamp(snapshot.message.timestamp)})", style="dim"))
    
    async def _draw_reply_message(self, message: discord.Message) -> None:
        """
        Draw a message that's a reply.
        
        Args:
            message: The reply message
        """
        self.write(Text(f"{self.cfg.theme['messages_list'].get('reply_indicator', '>')} "))
        
        if message.reference and message.reference.resolved:
            ref_msg = message.reference.resolved
            await self._draw_author(ref_msg)
            self.write(Text(ref_msg.content))
        else:
            self.write(Text("Original message was deleted", style="dim"))
        
        self.write(Text("\n"))
        await self._draw_default_message(message)
    
    async def _draw_user_joined(self, message: discord.Message) -> None:
        """
        Draw a user join message.
        
        Args:
            message: The join message
        """
        await self._draw_timestamp(message.created_at)
        await self._draw_author(message)
        self.write(Text("joined the server."))
    
    async def _draw_pinned_message(self, message: discord.Message) -> None:
        """
        Draw a pinned message indicator.
        
        Args:
            message: The pinned message
        """
        self.write(Text(f"{message.author.name} pinned a message"))
    
    async def select_previous(self) -> None:
        """Select the previous message."""
        messages = list(self._messages.values())
        if not messages:
            return
        
        if self.selected_message_id is None:
            self.selected_message_id = messages[0].id
        else:
            idx = next((i for i, m in enumerate(messages) if m.id == self.selected_message_id), -1)
            if idx > 0:
                self.selected_message_id = messages[idx - 1].id
    
    async def select_next(self) -> None:
        """Select the next message."""
        messages = list(self._messages.values())
        if not messages:
            return
        
        if self.selected_message_id is None:
            self.selected_message_id = messages[-1].id
        else:
            idx = next((i for i, m in enumerate(messages) if m.id == self.selected_message_id), -1)
            if idx < len(messages) - 1:
                self.selected_message_id = messages[idx + 1].id
    
    async def select_first(self) -> None:
        """Select the first message."""
        messages = list(self._messages.values())
        if messages:
            self.selected_message_id = messages[-1].id
    
    async def select_last(self) -> None:
        """Select the last message."""
        messages = list(self._messages.values())
        if messages:
            self.selected_message_id = messages[0].id
    
    def yank_id(self) -> None:
        """Copy selected message ID to clipboard."""
        if self.selected_message_id and self.selected_message_id in self._messages:
            msg = self._messages[self.selected_message_id]
            try:
                import pyperclip
                pyperclip.copy(str(msg.id))
                logger.info(f"Copied message ID to clipboard: {msg.id}")
            except ImportError:
                logger.warning("pyperclip not installed")
            except Exception as err:
                logger.error(f"Failed to copy to clipboard: {err}")
    
    def yank_content(self) -> None:
        """Copy selected message content to clipboard."""
        if self.selected_message_id and self.selected_message_id in self._messages:
            msg = self._messages[self.selected_message_id]
            try:
                import pyperclip
                pyperclip.copy(msg.content)
                logger.info("Copied message content to clipboard")
            except ImportError:
                logger.warning("pyperclip not installed")
            except Exception as err:
                logger.error(f"Failed to copy to clipboard: {err}")
    
    def yank_url(self) -> None:
        """Copy selected message URL to clipboard."""
        if self.selected_message_id and self.selected_message_id in self._messages:
            msg = self._messages[self.selected_message_id]
            url = msg.jump_url
            try:
                import pyperclip
                pyperclip.copy(url)
                logger.info(f"Copied message URL to clipboard: {url}")
            except ImportError:
                logger.warning("pyperclip not installed")
            except Exception as err:
                logger.error(f"Failed to copy to clipboard: {err}")
    
    async def reply(self, mention: bool = False) -> None:
        """
        Set up reply to selected message.
        
        Args:
            mention: Whether to mention the user
        """
        if self.selected_message_id and self.selected_message_id in self._messages:
            msg = self._messages[self.selected_message_id]
            
            # Callback to parent to set reply mode
            if self.on_message_selected:
                self.on_message_selected('reply', msg, mention)
    
    async def edit(self) -> None:
        """Edit the selected message."""
        if self.selected_message_id and self.selected_message_id in self._messages:
            msg = self._messages[self.selected_message_id]
            
            # Check if we're the author
            try:
                if msg.author.id != self.discord_state.client.user.id:
                    logger.error("Cannot edit: not the author")
                    return
            except Exception as err:
                logger.error(f"Failed to check author: {err}")
                return
            
            # Callback to parent to set edit mode
            if self.on_message_selected:
                self.on_message_selected('edit', msg, False)
    
    async def delete(self) -> None:
        """Delete the selected message."""
        if self.selected_message_id and self.selected_message_id in self._messages:
            msg = self._messages[self.selected_message_id]
            
            try:
                await msg.delete()
                logger.info(f"Deleted message {msg.id}")
            except Exception as err:
                logger.error(f"Failed to delete message: {err}")
    
    async def open_selected(self) -> None:
        """Open URLs or attachments from the selected message."""
        if self.selected_message_id and self.selected_message_id in self._messages:
            msg = self._messages[self.selected_message_id]
            
            # Extract URLs from content
            urls = self._extract_urls(msg.content)
            
            # Get attachment URLs
            attachment_urls = [a.url for a in msg.attachments]
            
            # Open first one if only one exists
            if len(urls) + len(attachment_urls) == 1:
                url = urls[0] if urls else attachment_urls[0]
                await self._open_url(url)
    
    def _extract_urls(self, content: str) -> List[str]:
        """
        Extract URLs from text.
        
        Args:
            content: The text to extract URLs from
            
        Returns:
            List of URLs found
        """
        url_pattern = r'https?://[^\s]+'
        return re.findall(url_pattern, content)
    
    async def _open_url(self, url: str) -> None:
        """
        Open a URL in the default browser.
        
        Args:
            url: The URL to open
        """
        try:
            import subprocess
            import platform
            
            if platform.system() == "Darwin":
                subprocess.Popen(["open", url])
            elif platform.system() == "Windows":
                subprocess.Popen(["start", url])
            else:
                subprocess.Popen(["xdg-open", url])
            
            logger.info(f"Opened URL: {url}")
        except Exception as err:
            logger.error(f"Failed to open URL: {err}")
