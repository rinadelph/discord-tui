"""Theme and styling configuration for Discordo."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Style:
    """Represents a text style with foreground, background, and attributes."""
    foreground: Optional[str] = None
    background: Optional[str] = None
    attributes: List[str] = field(default_factory=list)
    
    def to_rich_style(self) -> str:
        """
        Convert to Rich library style string.
        
        Returns:
            Rich style string
        """
        parts = []
        
        if self.foreground:
            parts.append(self.foreground)
        
        if self.background:
            parts.append(f"on {self.background}")
        
        if self.attributes:
            parts.extend(self.attributes)
        
        return " ".join(parts)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Style":
        """
        Create Style from dictionary (TOML data).
        
        Args:
            data: Dictionary with style configuration
            
        Returns:
            Style instance
        """
        style = Style()
        
        if "foreground" in data:
            style.foreground = data["foreground"]
        
        if "background" in data:
            style.background = data["background"]
        
        if "attributes" in data:
            attrs = data["attributes"]
            if isinstance(attrs, str):
                style.attributes = [attrs]
            elif isinstance(attrs, list):
                style.attributes = attrs
        
        return style


@dataclass
class Alignment:
    """Text alignment configuration."""
    value: str = "left"  # left, center, right
    
    @staticmethod
    def from_string(s: str) -> "Alignment":
        """Create Alignment from string."""
        alignment = Alignment()
        if s in ("left", "center", "right"):
            alignment.value = s
        return alignment


@dataclass
class ThemeStyle:
    """Theme styling for UI elements."""
    normal_style: Style = field(default_factory=Style)
    active_style: Style = field(default_factory=Style)


@dataclass
class TitleTheme(ThemeStyle):
    """Theme for title bars."""
    alignment: str = "left"


@dataclass
class BorderSet:
    """Border style set."""
    value: str = "round"  # hidden, plain, round, thick, double


@dataclass
class BorderTheme(ThemeStyle):
    """Theme for borders."""
    enabled: bool = True
    padding: tuple = field(default_factory=lambda: (0, 0, 1, 1))  # top, bottom, left, right
    normal_set: BorderSet = field(default_factory=BorderSet)
    active_set: BorderSet = field(default_factory=BorderSet)


@dataclass
class GuildsTreeTheme:
    """Theme for guilds tree."""
    auto_expand_folders: bool = True
    graphics: bool = True
    graphics_color: str = "default"


@dataclass
class MessagesListTheme:
    """Theme for messages list."""
    reply_indicator: str = ">"
    forwarded_indicator: str = "<"
    author_style: Style = field(default_factory=Style)
    mention_style: Style = field(default_factory=lambda: Style(foreground="blue"))
    emoji_style: Style = field(default_factory=lambda: Style(foreground="green"))
    url_style: Style = field(default_factory=lambda: Style(foreground="blue"))
    attachment_style: Style = field(default_factory=lambda: Style(foreground="yellow"))


@dataclass
class MentionsListTheme:
    """Theme for mentions list."""
    min_width: int = 20
    max_height: int = 0


@dataclass
class Theme:
    """Complete theme configuration."""
    title: TitleTheme = field(default_factory=TitleTheme)
    border: BorderTheme = field(default_factory=BorderTheme)
    guilds_tree: GuildsTreeTheme = field(default_factory=GuildsTreeTheme)
    messages_list: MessagesListTheme = field(default_factory=MessagesListTheme)
    mentions_list: MentionsListTheme = field(default_factory=MentionsListTheme)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Theme":
        """
        Create Theme from dictionary (TOML data).
        
        Args:
            data: Dictionary with theme configuration
            
        Returns:
            Theme instance
        """
        theme = Theme()
        
        if "title" in data and isinstance(data["title"], dict):
            title_data = data["title"]
            theme.title.alignment = title_data.get("alignment", "left")
            if "normal_style" in title_data:
                theme.title.normal_style = Style.from_dict(title_data["normal_style"])
            if "active_style" in title_data:
                theme.title.active_style = Style.from_dict(title_data["active_style"])
        
        if "border" in data and isinstance(data["border"], dict):
            border_data = data["border"]
            theme.border.enabled = border_data.get("enabled", True)
            theme.border.padding = tuple(border_data.get("padding", (0, 0, 1, 1)))
            if "normal_style" in border_data:
                theme.border.normal_style = Style.from_dict(border_data["normal_style"])
            if "active_style" in border_data:
                theme.border.active_style = Style.from_dict(border_data["active_style"])
            if "normal_set" in border_data:
                theme.border.normal_set.value = border_data["normal_set"]
            if "active_set" in border_data:
                theme.border.active_set.value = border_data["active_set"]
        
        if "guilds_tree" in data and isinstance(data["guilds_tree"], dict):
            gt_data = data["guilds_tree"]
            theme.guilds_tree.auto_expand_folders = gt_data.get("auto_expand_folders", True)
            theme.guilds_tree.graphics = gt_data.get("graphics", True)
            theme.guilds_tree.graphics_color = gt_data.get("graphics_color", "default")
        
        if "messages_list" in data and isinstance(data["messages_list"], dict):
            ml_data = data["messages_list"]
            theme.messages_list.reply_indicator = ml_data.get("reply_indicator", ">")
            theme.messages_list.forwarded_indicator = ml_data.get("forwarded_indicator", "<")
            if "mention_style" in ml_data:
                theme.messages_list.mention_style = Style.from_dict(ml_data["mention_style"])
            if "emoji_style" in ml_data:
                theme.messages_list.emoji_style = Style.from_dict(ml_data["emoji_style"])
            if "url_style" in ml_data:
                theme.messages_list.url_style = Style.from_dict(ml_data["url_style"])
            if "attachment_style" in ml_data:
                theme.messages_list.attachment_style = Style.from_dict(ml_data["attachment_style"])
        
        if "mentions_list" in data and isinstance(data["mentions_list"], dict):
            ml_data = data["mentions_list"]
            theme.mentions_list.min_width = ml_data.get("min_width", 20)
            theme.mentions_list.max_height = ml_data.get("max_height", 0)
        
        return theme
