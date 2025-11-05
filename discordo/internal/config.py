"""Configuration management for Discordo."""

import logging
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

import tomllib

from discordo.internal.consts import DISCORDO_NAME

logger = logging.getLogger(__name__)

CONFIG_FILE_NAME = "config.toml"

# Default configuration as a string (embedded)
DEFAULT_CONFIG = """
mouse = true
editor = "default"
status = "default"
markdown = true
hide_blocked_users = true
show_attachment_links = true
autocomplete_limit = 20
messages_limit = 50

[timestamps]
enabled = true
format = "3:04PM"

[notifications]
enabled = true
duration = 0
[notifications.sound]
enabled = true
only_on_ping = true

[keys]
focus_guilds_tree = "Ctrl+G"
focus_messages_list = "Ctrl+T"
focus_message_input = "Ctrl+Space"
toggle_guilds_tree = "Ctrl+B"
focus_next = "Tab"
focus_previous = "Shift+Tab"
quit = "Ctrl+C"
logout = "Ctrl+D"

[keys.guilds_tree]
select_previous = "Rune[k]"
select_next = "Rune[j]"
select_first = "Rune[g]"
select_last = "Rune[G]"
select_current = "Enter"
yank_id = "Rune[i]"
collapse_parent_node = "Rune[-]"
move_to_parent_node = "Rune[p]"

[keys.messages_list]
select_previous = "Rune[k]"
select_next = "Rune[j]"
select_first = "Rune[g]"
select_last = "Rune[G]"
select_reply = "Rune[s]"
reply = "Rune[r]"
reply_mention = "Rune[R]"
cancel = "Esc"
edit = "Rune[e]"
delete = "Rune[D]"
delete_confirm = "Rune[d]"
open = "Rune[o]"
yank_content = "Rune[y]"
yank_url = "Rune[u]"
yank_id = "Rune[i]"

[keys.message_input]
paste = "Ctrl+V"
send = "Enter"
cancel = "Esc"
tab_complete = "Tab"
open_editor = "Ctrl+E"
open_file_picker = "Ctrl+\\\\"

[keys.mentions_list]
up = "Ctrl+P"
down = "Ctrl+N"

[theme.title]
alignment = "left"
normal_style = { attributes = "dim" }
active_style = { foreground = "green", attributes = "bold" }

[theme.border]
enabled = true
padding = [0, 0, 1, 1]
normal_style = { attributes = "dim" }
active_style = { foreground = "green", attributes = "bold" }
normal_set = "round"
active_set = "round"

[theme.guilds_tree]
auto_expand_folders = true
graphics = true
graphics_color = "default"

[theme.messages_list]
reply_indicator = ">"
forwarded_indicator = "<"
mention_style = { foreground = "blue" }
emoji_style = { foreground = "green" }
url_style = { foreground = "blue" }
attachment_style = { foreground = "yellow" }

[theme.mentions_list]
min_width = 20
max_height = 0
"""


@dataclass
class Timestamps:
    """Timestamps configuration."""
    enabled: bool = True
    format: str = "3:04PM"


@dataclass
class Sound:
    """Sound configuration."""
    enabled: bool = True
    only_on_ping: bool = True


@dataclass
class Notifications:
    """Notifications configuration."""
    enabled: bool = True
    duration: int = 0
    sound: Sound = field(default_factory=Sound)


@dataclass
class Keys:
    """Keybindings configuration."""
    # Global shortcuts
    focus_guilds_tree: str = "Ctrl+G"
    focus_messages_list: str = "Ctrl+T"
    focus_message_input: str = "Ctrl+Space"
    toggle_guilds_tree: str = "Ctrl+B"
    focus_next: str = "Tab"
    focus_previous: str = "Shift+Tab"
    quit: str = "Ctrl+C"
    logout: str = "Ctrl+D"
    
    # Guilds tree keys
    guilds_tree: dict = field(default_factory=lambda: {
        "select_previous": "Rune[k]",
        "select_next": "Rune[j]",
        "select_first": "Rune[g]",
        "select_last": "Rune[G]",
        "select_current": "Enter",
        "yank_id": "Rune[i]",
        "collapse_parent_node": "Rune[-]",
        "move_to_parent_node": "Rune[p]",
    })
    
    # Messages list keys
    messages_list: dict = field(default_factory=lambda: {
        "select_previous": "Rune[k]",
        "select_next": "Rune[j]",
        "select_first": "Rune[g]",
        "select_last": "Rune[G]",
        "select_reply": "Rune[s]",
        "reply": "Rune[r]",
        "reply_mention": "Rune[R]",
        "cancel": "Esc",
        "edit": "Rune[e]",
        "delete": "Rune[D]",
        "delete_confirm": "Rune[d]",
        "open": "Rune[o]",
        "yank_content": "Rune[y]",
        "yank_url": "Rune[u]",
        "yank_id": "Rune[i]",
    })
    
    # Message input keys
    message_input: dict = field(default_factory=lambda: {
        "paste": "Ctrl+V",
        "send": "Enter",
        "cancel": "Esc",
        "tab_complete": "Tab",
        "open_editor": "Ctrl+E",
        "open_file_picker": "Ctrl+\\",
    })
    
    # Mentions list keys
    mentions_list: dict = field(default_factory=lambda: {
        "up": "Ctrl+P",
        "down": "Ctrl+N",
    })


@dataclass
class Theme:
    """Theme configuration."""
    title: dict = field(default_factory=dict)
    border: dict = field(default_factory=dict)
    guilds_tree: dict = field(default_factory=dict)
    messages_list: dict = field(default_factory=dict)
    mentions_list: dict = field(default_factory=dict)


@dataclass
class Config:
    """Main configuration structure."""
    mouse: bool = True
    editor: str = "default"
    status: str = "default"
    markdown: bool = True
    hide_blocked_users: bool = True
    show_attachment_links: bool = True
    autocomplete_limit: int = 20
    messages_limit: int = 50
    
    timestamps: Timestamps = field(default_factory=Timestamps)
    notifications: Notifications = field(default_factory=Notifications)
    keys: Keys = field(default_factory=Keys)
    theme: Theme = field(default_factory=Theme)
    
    @staticmethod
    def default_path() -> Path:
        """Return the default configuration file path."""
        try:
            config_dir = Path(os.path.expanduser("~/.config"))
        except Exception as err:
            logger.info(
                f"user config dir cannot be determined; falling back to current dir: {err}"
            )
            config_dir = Path(".")
        
        return config_dir / DISCORDO_NAME / CONFIG_FILE_NAME
    
    @staticmethod
    def load(path: str) -> "Config":
        """
        Load configuration from file, merging with defaults.
        
        Args:
            path: Path to the configuration file
            
        Returns:
            Config instance with merged settings
        """
        # Load default config
        default_data = tomllib.loads(DEFAULT_CONFIG)
        cfg = Config(**default_data)
        
        # Load user config if it exists
        config_path = Path(path)
        if not config_path.exists():
            logger.info(
                f"config file does not exist, falling back to the default config: {config_path}"
            )
        else:
            try:
                with open(config_path, 'rb') as f:
                    user_data = tomllib.load(f)
                    
                # Merge user config with defaults
                for key, value in user_data.items():
                    if key == "timestamps" and isinstance(value, dict):
                        cfg.timestamps = Timestamps(**value)
                    elif key == "notifications" and isinstance(value, dict):
                        sound_data = value.pop("sound", {})
                        cfg.notifications = Notifications(
                            sound=Sound(**sound_data),
                            **value
                        )
                    elif key == "keys" and isinstance(value, dict):
                        cfg.keys = Keys(**value)
                    elif key == "theme" and isinstance(value, dict):
                        cfg.theme = Theme(**value)
                    elif hasattr(cfg, key):
                        setattr(cfg, key, value)
            except Exception as err:
                logger.error(f"failed to load config: {err}")
                raise
        
        # Set defaults for special values
        if cfg.editor == "default":
            cfg.editor = os.getenv("EDITOR", "vim")
        
        if cfg.status == "default":
            cfg.status = ""
        
        return cfg
