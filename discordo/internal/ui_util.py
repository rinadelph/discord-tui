"""UI utilities and helpers for Discordo."""

from typing import Optional
import discord
from discordo.internal.theme import Theme


def configure_box_styling(theme: Theme) -> dict:
    """
    Get box styling configuration from theme.
    
    Args:
        theme: Theme configuration
        
    Returns:
        Dictionary with styling configuration
    """
    border = theme.border
    title = theme.title
    
    return {
        "border_enabled": border.enabled,
        "border_style_normal": border.normal_style.to_rich_style(),
        "border_style_active": border.active_style.to_rich_style(),
        "border_set_normal": border.normal_set.value,
        "border_set_active": border.active_set.value,
        "border_padding": border.padding,
        "title_style_normal": title.normal_style.to_rich_style(),
        "title_style_active": title.active_style.to_rich_style(),
        "title_alignment": title.alignment,
    }


def channel_to_string(channel: discord.abc.GuildChannel) -> str:
    """
    Convert a Discord channel to a formatted string representation.
    
    Args:
        channel: The Discord channel
        
    Returns:
        Formatted channel name with prefix
    """
    if isinstance(channel, discord.DMChannel):
        return channel.recipient.name if channel.recipient else "DM"
    
    elif isinstance(channel, discord.GroupChannel):
        if channel.name:
            return channel.name
        # Get recipient names
        recipients = [r.display_name or r.name for r in channel.recipients]
        return ", ".join(recipients)
    
    elif isinstance(channel, discord.TextChannel):
        return f"# {channel.name}"
    
    elif isinstance(channel, discord.VoiceChannel):
        return f"🔊 {channel.name}"
    
    elif isinstance(channel, discord.StageChannel):
        return f"📻 {channel.name}"
    
    elif isinstance(channel, discord.CategoryChannel):
        return f"📁 {channel.name}"
    
    elif isinstance(channel, discord.ForumChannel):
        return f"💬 {channel.name}"
    
    else:
        # Fallback for unknown channel types
        return str(getattr(channel, 'name', 'Unknown'))


def centered_modal(width: int = 0, height: int = 0) -> dict:
    """
    Get layout configuration for a centered modal dialog.
    
    Args:
        width: Modal width (0 = auto)
        height: Modal height (0 = auto)
        
    Returns:
        Dictionary with modal layout configuration
    """
    return {
        "width": width,
        "height": height,
        "centered": True,
    }


def format_user_mention(user: discord.User, member: Optional[discord.Member] = None) -> str:
    """
    Format a user mention string.
    
    Args:
        user: The Discord user
        member: Optional guild member (for nickname)
        
    Returns:
        Formatted mention string
    """
    name = user.display_name or user.name
    
    if member and member.nick:
        name = member.nick
    
    return f"@{name}"


def format_role_color(role: discord.Role) -> Optional[str]:
    """
    Get the color string for a role.
    
    Args:
        role: The Discord role
        
    Returns:
        Color string or None if default
    """
    if role.color and role.color.value:
        return role.color.to_rgb()
    return None


def get_presence_indicator(status: discord.Status) -> tuple:
    """
    Get status indicator symbol and color.
    
    Args:
        status: User's Discord status
        
    Returns:
        Tuple of (symbol, color)
    """
    indicators = {
        discord.Status.online: ("●", "green"),
        discord.Status.idle: ("◐", "yellow"),
        discord.Status.dnd: ("⊘", "red"),
        discord.Status.offline: ("○", "gray"),
    }
    
    return indicators.get(status, ("?", "gray"))


def escape_markup(text: str) -> str:
    """
    Escape special characters for Rich markup.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text safe for Rich rendering
    """
    # Escape Rich markup characters
    text = text.replace("[", r"\[")
    text = text.replace("]", r"\]")
    return text
