"""Message input widget for Discordo."""

import asyncio
import logging
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Callable

import discord
from textual.widgets import TextArea
from textual.containers import Container

from discordo.internal.config import Config

logger = logging.getLogger(__name__)

# Regex patterns
MENTION_REGEX = re.compile(r'@[a-zA-Z0-9._]+')
FILE_PATH_REGEX = re.compile(r'(?:^|\s)(/[^\s]+|[a-zA-Z]:\\[^\s]+)(?:\s|$)')


class MessageInput(TextArea):
    """
    Text input widget for composing and sending messages.
    
    Supports:
    - Message composition with markdown
    - Mention autocompletion
    - File attachments
    - Image pasting
    - Message editing
    """
    
    def __init__(self, cfg: Config, discord_state, on_send=None):
        """
        Initialize the message input.
        
        Args:
            cfg: Configuration object
            discord_state: Discord state manager
            on_send: Callback when message is sent
        """
        super().__init__()
        self.cfg = cfg
        self.discord_state = discord_state
        self.on_send = on_send
        
        # Message composition state
        self.is_editing = False
        self.reply_to_id: Optional[int] = None
        self.mention_reply = False
        self.attached_files: List[Path] = []
        
        # Mention completion state
        self.mention_list_open = False
        self.completion_candidates: List[discord.Member] = []
        self.completion_index = 0
    
    def reset(self) -> None:
        """Reset the input for a new message."""
        self.is_editing = False
        self.reply_to_id = None
        self.mention_reply = False
        self.attached_files.clear()
        self.text = ""
        self.title = ""
    
    async def paste_from_clipboard(self) -> None:
        """Paste content from clipboard, handling both text and images."""
        try:
            import pyperclip
            
            # Try to get image from clipboard first
            # This is platform-specific and may require additional libraries
            text = pyperclip.paste()
            if text:
                self.text += text
        except ImportError:
            logger.warning("pyperclip not installed for clipboard access")
        except Exception as err:
            logger.error(f"Failed to paste from clipboard: {err}")
    
    def extract_and_attach_files(self, text: str) -> str:
        """
        Extract file paths from text and attach them.
        
        Args:
            text: The input text potentially containing file paths
            
        Returns:
            Text with file paths removed
        """
        matches = list(FILE_PATH_REGEX.finditer(text))
        
        # Process matches in reverse to maintain correct indices
        for match in reversed(matches):
            path_str = match.group(1)
            path = Path(path_str)
            
            # Check if file exists
            if path.exists() and path.is_file():
                self.attached_files.append(path)
                # Remove the path from text
                text = text[:match.start(1)] + text[match.end(1):]
        
        return text.strip()
    
    async def send(self) -> None:
        """Send the current message."""
        if not self.discord_state.selected_channel_id:
            logger.warning("No channel selected")
            return
        
        text = self.text.strip()
        
        # Extract file paths and attach them
        text = self.extract_and_attach_files(text)
        
        # Process text for mention expansion
        text = await self._process_text(text)
        
        # Check if we have content to send
        if not text and not self.attached_files:
            logger.warning("Nothing to send")
            return
        
        try:
            if self.is_editing:
                # Edit existing message
                await self._edit_message(text)
            else:
                # Send new message
                await self._send_message(text)
            
            self.reset()
            
            # Callback to parent
            if self.on_send:
                self.on_send()
        
        except Exception as err:
            logger.error(f"Failed to send message: {err}")
    
    async def _send_message(self, content: str) -> None:
        """
        Send a new message.
        
        Args:
            content: Message content
        """
        channel = self.discord_state.get_channel(self.discord_state.selected_channel_id)
        if not channel:
            logger.error("Channel not found")
            return
        
        # Prepare kwargs
        kwargs = {"content": content}
        
        # Add reply reference if set
        if self.reply_to_id:
            kwargs["reference"] = discord.MessageReference(message_id=self.reply_to_id)
            kwargs["mention_author"] = self.mention_reply
        
        # Add files
        for file_path in self.attached_files:
            try:
                with open(file_path, 'rb') as f:
                    kwargs.setdefault("file", []).append(discord.File(f, filename=file_path.name))
            except Exception as err:
                logger.error(f"Failed to attach file {file_path}: {err}")
        
        # Send message
        try:
            await channel.send(**kwargs)
            logger.info("Message sent")
        except Exception as err:
            logger.error(f"Failed to send message: {err}")
    
    async def _edit_message(self, content: str) -> None:
        """
        Edit an existing message.
        
        Args:
            content: New message content
        """
        if not self.reply_to_id:
            logger.error("No message selected for editing")
            return
        
        channel = self.discord_state.get_channel(self.discord_state.selected_channel_id)
        if not channel:
            logger.error("Channel not found")
            return
        
        try:
            message = await channel.fetch_message(self.reply_to_id)
            await message.edit(content=content)
            logger.info("Message edited")
        except Exception as err:
            logger.error(f"Failed to edit message: {err}")
    
    async def _process_text(self, text: str) -> str:
        """
        Process text for mention expansion.
        
        Args:
            text: The raw text
            
        Returns:
            Processed text with expanded mentions
        """
        # TODO: Implement proper mention expansion with markdown parsing
        return text
    
    async def tab_complete(self) -> None:
        """Handle tab completion for mentions."""
        # Find word under cursor (last @ mention)
        # This is a simplified version
        text = self.text
        
        # Find the last @ symbol
        last_at = text.rfind('@')
        if last_at == -1:
            return
        
        # Get the text after @
        start = last_at + 1
        # Find word boundary
        end = start
        while end < len(text) and (text[end].isalnum() or text[end] in '._'):
            end += 1
        
        search_term = text[start:end]
        
        # Get candidates from guild members
        await self._find_mention_candidates(search_term)
        
        if not self.completion_candidates:
            return
        
        # Replace with first candidate
        member = self.completion_candidates[0]
        name = member.display_name or member.user.name
        
        self.text = text[:last_at] + f"@{name} " + text[end:]
    
    async def _find_mention_candidates(self, search_term: str) -> None:
        """
        Find members matching the search term.
        
        Args:
            search_term: The search term
        """
        if not self.discord_state.selected_guild_id:
            return
        
        guild = self.discord_state.get_guild(self.discord_state.selected_guild_id)
        if not guild:
            return
        
        self.completion_candidates = []
        search_lower = search_term.lower()
        
        # Simple substring matching
        for member in guild.members:
            name = member.display_name or member.user.name
            if search_lower in name.lower():
                self.completion_candidates.append(member)
                
                if len(self.completion_candidates) >= self.cfg.autocomplete_limit:
                    break
    
    def add_title_suffix(self, suffix: str) -> None:
        """
        Add a suffix to the title.
        
        Args:
            suffix: Text to add to title
        """
        title = self.title or ""
        if title:
            title += " | "
        self.title = title + suffix
    
    async def open_editor(self) -> None:
        """Open external editor for message composition."""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp:
                tmp.write(self.text)
                tmp_path = tmp.name
            
            # Open editor
            editor = self.cfg.editor or os.getenv("EDITOR", "vim")
            subprocess.run([editor, tmp_path], check=True)
            
            # Read back the edited content
            with open(tmp_path, 'r') as f:
                self.text = f.read().strip()
            
            # Clean up
            os.unlink(tmp_path)
            
            logger.info("Editor closed, content updated")
        
        except Exception as err:
            logger.error(f"Failed to open editor: {err}")
    
    async def open_file_picker(self) -> None:
        """Open file picker dialog to attach files."""
        try:
            from tkinter import Tk
            from tkinter.filedialog import askopenfilenames
            
            # Hide the root window
            root = Tk()
            root.withdraw()
            root.update()
            
            # Open file picker
            files = askopenfilenames(title="Select files to attach")
            
            for file_path in files:
                path = Path(file_path)
                if path.exists() and path.is_file():
                    self.attached_files.append(path)
                    self.add_title_suffix(f"Attached {path.name}")
            
            root.destroy()
            logger.info(f"Attached {len(files)} file(s)")
        
        except ImportError:
            logger.error("tkinter not available for file picker")
        except Exception as err:
            logger.error(f"Failed to pick files: {err}")
    
    def set_reply_mode(self, message: discord.Message, mention: bool = False) -> None:
        """
        Set reply mode for the next message.
        
        Args:
            message: Message to reply to
            mention: Whether to mention the author
        """
        self.reply_to_id = message.id
        self.mention_reply = mention
        
        author_name = message.author.display_name or message.author.name
        prefix = "[@] " if mention else ""
        self.add_title_suffix(f"{prefix}Replying to {author_name}")
    
    def set_edit_mode(self, message: discord.Message) -> None:
        """
        Set edit mode for the selected message.
        
        Args:
            message: Message to edit
        """
        self.is_editing = True
        self.reply_to_id = message.id
        self.text = message.content
        self.title = "Editing"
    
    def clear_title(self) -> None:
        """Clear the input title."""
        self.title = ""
