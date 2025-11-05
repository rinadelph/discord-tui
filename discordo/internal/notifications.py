"""Desktop notifications for Discordo."""

import asyncio
import logging
from pathlib import Path
from typing import Optional
import aiohttp

import discord

from discordo.internal.config import Config
from discordo.internal.consts import cache_dir

logger = logging.getLogger(__name__)


async def notify(
    message: discord.Message,
    cfg: Config,
    is_mention: bool = False,
) -> None:
    """
    Send a desktop notification for a message.
    
    Args:
        message: The message that triggered the notification
        cfg: Configuration
        is_mention: Whether the user was mentioned
    """
    # Check if notifications are enabled
    if not cfg.notifications.enabled:
        return
    
    # Don't notify if user is in DND status
    if cfg.status == "dnd":
        return
    
    # Only notify on mentions
    if not is_mention:
        return
    
    # Get message content
    content = message.content
    if not content and message.attachments:
        content = f"Uploaded {message.attachments[0].filename}"
    
    if not content:
        return
    
    # Build notification title
    title = message.author.display_name or message.author.name
    
    # Add channel and guild info if applicable
    if isinstance(message.channel, discord.TextChannel):
        guild = message.guild
        title += f" (#{message.channel.name}, {guild.name})"
    elif isinstance(message.channel, discord.DMChannel):
        title = f"DM from {title}"
    
    # Get avatar image
    avatar_path = await _get_cached_avatar(message.author)
    
    # Determine if should play sound
    should_sound = (
        cfg.notifications.sound.enabled
        and (
            not cfg.notifications.sound.only_on_ping
            or is_mention
        )
    )
    
    # Send notification
    await _send_desktop_notification(
        title,
        content,
        avatar_path,
        should_sound,
        cfg.notifications.duration,
    )


async def _get_cached_avatar(user: discord.User) -> Optional[str]:
    """
    Get user avatar, caching it locally.
    
    Args:
        user: The Discord user
        
    Returns:
        Path to cached avatar image or None
    """
    if not user.avatar:
        return None
    
    avatar_hash = str(user.avatar)
    avatar_dir = cache_dir() / "avatars"
    avatar_path = avatar_dir / f"{avatar_hash}.png"
    
    # Return if already cached
    if avatar_path.exists():
        return str(avatar_path)
    
    # Create directory
    try:
        avatar_dir.mkdir(parents=True, exist_ok=True)
    except Exception as err:
        logger.error(f"Failed to create avatar cache dir: {err}")
        return None
    
    # Download and cache avatar
    try:
        avatar_url = user.avatar.url
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as resp:
                if resp.status == 200:
                    with open(avatar_path, 'wb') as f:
                        f.write(await resp.read())
                    return str(avatar_path)
    except Exception as err:
        logger.warning(f"Failed to download avatar: {err}")
    
    return None


async def _send_desktop_notification(
    title: str,
    content: str,
    image_path: Optional[str] = None,
    play_sound: bool = False,
    duration: int = 0,
) -> None:
    """
    Send a desktop notification using the system notification daemon.
    
    Args:
        title: Notification title
        content: Notification body
        image_path: Path to image to display
        play_sound: Whether to play a sound
        duration: Duration in milliseconds (0 = default)
    """
    try:
        # Try using dbus/freedesktop notifications (Linux)
        await _notify_freedesktop(title, content, image_path, duration)
    except Exception as err:
        logger.debug(f"Freedesktop notification failed: {err}")
        
        try:
            # Fallback to platform-specific notifications
            await _notify_native(title, content)
        except Exception as err2:
            logger.warning(f"Failed to send notification: {err2}")
    
    # Play sound if requested
    if play_sound:
        await _play_notification_sound()


async def _notify_freedesktop(
    title: str,
    body: str,
    icon: Optional[str] = None,
    timeout: int = 0,
) -> None:
    """
    Send notification using freedesktop.org DBus interface (Linux).
    
    Args:
        title: Notification title
        body: Notification body
        icon: Icon path
        timeout: Timeout in milliseconds
    """
    try:
        import dbus
        
        bus = dbus.SessionBus()
        notifications = bus.get_object(
            "org.freedesktop.Notifications",
            "/org/freedesktop/Notifications"
        )
        notify_interface = dbus.Interface(notifications, "org.freedesktop.Notifications")
        
        notify_interface.Notify(
            "discordo",  # app name
            0,  # replaces id
            icon or "",  # icon
            title,  # summary
            body,  # body
            [],  # actions
            {},  # hints
            timeout,  # timeout (0 = default)
        )
    except ImportError:
        raise ImportError("dbus-python not available for notifications")


async def _notify_native(title: str, message: str) -> None:
    """
    Send notification using platform-specific method.
    
    Args:
        title: Notification title
        message: Notification message
    """
    import platform
    import subprocess
    
    system = platform.system()
    
    try:
        if system == "Darwin":
            # macOS
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(
                ["osascript", "-e", script],
                check=True,
                capture_output=True,
            )
        elif system == "Windows":
            # Windows - use toast notifications
            from win10toast import ToastNotifier
            ToastNotifier().show_toast(title, message)
        elif system == "Linux":
            # Linux - try notify-send as fallback
            subprocess.run(
                ["notify-send", title, message],
                check=True,
                capture_output=True,
            )
    except Exception as err:
        raise RuntimeError(f"Failed to send native notification: {err}")


async def _play_notification_sound() -> None:
    """Play a notification sound."""
    try:
        import winsound
        winsound.Beep(1000, 200)
    except ImportError:
        # Not on Windows, try other methods
        try:
            import subprocess
            import platform
            
            if platform.system() == "Darwin":
                subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"], check=False)
            elif platform.system() == "Linux":
                subprocess.run(
                    ["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"],
                    check=False,
                )
        except Exception as err:
            logger.debug(f"Failed to play notification sound: {err}")
