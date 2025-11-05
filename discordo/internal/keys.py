"""Keybinding configuration for Discordo."""

from dataclasses import dataclass, field


@dataclass
class NavigationKeys:
    """Navigation keybindings."""
    select_previous: str = "Rune[k]"
    select_next: str = "Rune[j]"
    select_first: str = "Rune[g]"
    select_last: str = "Rune[G]"


@dataclass
class GuildsTreeKeys(NavigationKeys):
    """Guilds tree specific keybindings."""
    select_current: str = "Enter"
    yank_id: str = "Rune[i]"
    collapse_parent_node: str = "Rune[-]"
    move_to_parent_node: str = "Rune[p]"


@dataclass
class MessagesListKeys(NavigationKeys):
    """Messages list specific keybindings."""
    select_reply: str = "Rune[s]"
    reply: str = "Rune[r]"
    reply_mention: str = "Rune[R]"
    cancel: str = "Esc"
    edit: str = "Rune[e]"
    delete: str = "Rune[D]"
    delete_confirm: str = "Rune[d]"
    open: str = "Rune[o]"
    yank_content: str = "Rune[y]"
    yank_url: str = "Rune[u]"
    yank_id: str = "Rune[i]"


@dataclass
class MessageInputKeys:
    """Message input specific keybindings."""
    paste: str = "Ctrl+V"
    send: str = "Enter"
    cancel: str = "Esc"
    tab_complete: str = "Tab"
    open_editor: str = "Ctrl+E"
    open_file_picker: str = "Ctrl+\\"


@dataclass
class MentionsListKeys:
    """Mentions list specific keybindings."""
    up: str = "Ctrl+P"
    down: str = "Ctrl+N"


@dataclass
class Keys:
    """All keybindings for the application."""
    # Global shortcuts
    focus_guilds_tree: str = "Ctrl+G"
    focus_messages_list: str = "Ctrl+T"
    focus_message_input: str = "Ctrl+Space"
    focus_next: str = "Tab"
    focus_previous: str = "Shift+Tab"
    toggle_guilds_tree: str = "Ctrl+B"
    logout: str = "Ctrl+D"
    quit: str = "Ctrl+C"
    
    # Panel-specific keys
    guilds_tree: GuildsTreeKeys = field(default_factory=GuildsTreeKeys)
    messages_list: MessagesListKeys = field(default_factory=MessagesListKeys)
    message_input: MessageInputKeys = field(default_factory=MessageInputKeys)
    mentions_list: MentionsListKeys = field(default_factory=MentionsListKeys)
