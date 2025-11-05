"""Main application for Discordo TUI client."""

import asyncio
import logging
from typing import Optional, List, Tuple, Set
from io import StringIO
from pathlib import Path

from textual.app import ComposeResult, App
from textual.containers import Vertical, Horizontal
from textual.widgets import OptionList, RichLog, Static
from textual.binding import Binding
from textual.message import Message
from rich.panel import Panel

from discordo.internal.config import Config
from discordo.internal.database import DiscordDatabase
from discordo.cmd.state import DiscordState
from discordo.cmd.guilds_tree import GuildsTree

logger = logging.getLogger(__name__)

# Create a buffer to capture logs
_log_buffer = StringIO()


class CollapsibleOptionList(OptionList):
    """OptionList with collapsible folders."""
    
    class ItemSelected(Message):
        """Posted when an item is selected."""
        def __init__(self, item_type: str, item_data: dict) -> None:
            super().__init__()
            self.item_type = item_type
            self.item_data = item_data
    
    DEFAULT_CSS = """
    CollapsibleOptionList {
        width: 35;
        height: 100%;
        background: $surface;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dms_data: List[dict] = []
        self.guilds_data: List[dict] = []
        self.favorites: Set[str] = set()
        
        # Folder states
        self.folders_open = {
            'favorites': True,
            'dms': True,
            'guilds': True,
        }
        
        self.all_items: List[Tuple[str, dict]] = []
    
    def rebuild_list(self) -> None:
