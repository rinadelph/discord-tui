"""SQLite database for caching Discord data."""

import sqlite3
import json
import logging
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DiscordDatabase:
    """SQLite database for caching Discord guilds, channels, users, and messages."""
    
    def __init__(self, cache_dir: Path = None):
        """Initialize database connection."""
        if cache_dir is None:
            cache_dir = Path.home() / '.cache' / 'discordo'
        
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = cache_dir / 'discordo.db'
        self.conn = None
        self.init_db()
    
    def init_db(self):
        """Initialize database schema."""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            cursor = self.conn.cursor()
            
            # Guilds table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS guilds (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    icon TEXT,
                    owner BOOLEAN,
                    data TEXT,
                    updated_at TIMESTAMP
                )
            ''')
            
            # Channels table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS channels (
                    id TEXT PRIMARY KEY,
                    guild_id TEXT,
                    name TEXT NOT NULL,
                    type INTEGER,
                    position INTEGER,
                    parent_id TEXT,
                    data TEXT,
                    updated_at TIMESTAMP,
                    FOREIGN KEY(guild_id) REFERENCES guilds(id)
                )
            ''')
            
            # Direct messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dms (
                    id TEXT PRIMARY KEY,
                    recipient_id TEXT,
                    recipient_name TEXT,
                    recipient_global_name TEXT,
                    type INTEGER,
                    last_message_id TEXT,
                    data TEXT,
                    updated_at TIMESTAMP
                )
            ''')
            
            # Users table (for display names)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    global_name TEXT,
                    avatar TEXT,
                    data TEXT,
                    updated_at TIMESTAMP
                )
            ''')
            
            # Messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    channel_id TEXT NOT NULL,
                    author_id TEXT,
                    author_name TEXT,
                    content TEXT,
                    timestamp TIMESTAMP,
                    data TEXT,
                    updated_at TIMESTAMP,
                    FOREIGN KEY(channel_id) REFERENCES channels(id)
                )
            ''')
            
            # Cache metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP
                )
            ''')

            # Favorites table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS favorites (
                    item_id TEXT PRIMARY KEY,
                    item_type TEXT NOT NULL,
                    item_name TEXT,
                    added_at TIMESTAMP
                )
            ''')

            self.conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    # === GUILDS ===
    
    def save_guilds(self, guilds: List[Dict[str, Any]]):
        """Cache guilds in database."""
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()
            
            for guild in guilds:
                cursor.execute('''
                    INSERT OR REPLACE INTO guilds (id, name, icon, owner, data, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    guild.get('id'),
                    guild.get('name'),
                    guild.get('icon'),
                    guild.get('owner', False),
                    json.dumps(guild),
                    now
                ))
            
            self.conn.commit()
            logger.debug(f"Cached {len(guilds)} guilds")
        except Exception as e:
            logger.error(f"Failed to save guilds: {e}")
    
    def get_guilds(self) -> List[Dict[str, Any]]:
        """Load guilds from cache."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT data FROM guilds ORDER BY name')
            rows = cursor.fetchall()
            
            guilds = [json.loads(row[0]) for row in rows if row[0]]
            logger.debug(f"Loaded {len(guilds)} guilds from cache")
            return guilds
        except Exception as e:
            logger.error(f"Failed to load guilds: {e}")
            return []
    
    # === CHANNELS ===
    
    def save_channels(self, guild_id: str, channels: List[Dict[str, Any]]):
        """Cache channels for a guild."""
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()
            
            for channel in channels:
                cursor.execute('''
                    INSERT OR REPLACE INTO channels (id, guild_id, name, type, position, parent_id, data, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    channel.get('id'),
                    guild_id,
                    channel.get('name'),
                    channel.get('type'),
                    channel.get('position'),
                    channel.get('parent_id'),
                    json.dumps(channel),
                    now
                ))
            
            self.conn.commit()
            logger.debug(f"Cached {len(channels)} channels for guild {guild_id}")
        except Exception as e:
            logger.error(f"Failed to save channels: {e}")
    
    def get_channels(self, guild_id: str) -> List[Dict[str, Any]]:
        """Load channels for a guild from cache."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT data FROM channels WHERE guild_id = ? ORDER BY position', (guild_id,))
            rows = cursor.fetchall()
            
            channels = [json.loads(row[0]) for row in rows if row[0]]
            logger.debug(f"Loaded {len(channels)} channels from cache for guild {guild_id}")
            return channels
        except Exception as e:
            logger.error(f"Failed to load channels: {e}")
            return []
    
    # === DIRECT MESSAGES ===
    
    def save_dms(self, dms: List[Dict[str, Any]]):
        """Cache DMs in database."""
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()
            
            for dm in dms:
                # Extract recipient info
                recipients = dm.get('recipients', [])
                recipient_id = recipients[0].get('id') if recipients else None
                recipient_name = recipients[0].get('username') if recipients else None
                recipient_global_name = recipients[0].get('global_name') if recipients else None
                
                cursor.execute('''
                    INSERT OR REPLACE INTO dms (id, recipient_id, recipient_name, recipient_global_name, type, last_message_id, data, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    dm.get('id'),
                    recipient_id,
                    recipient_name,
                    recipient_global_name,
                    dm.get('type'),
                    dm.get('last_message_id'),
                    json.dumps(dm),
                    now
                ))
            
            self.conn.commit()
            logger.debug(f"Cached {len(dms)} DMs")
        except Exception as e:
            logger.error(f"Failed to save DMs: {e}")
    
    def get_dms(self) -> List[Dict[str, Any]]:
        """Load DMs from cache."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT data FROM dms ORDER BY last_message_id DESC')
            rows = cursor.fetchall()
            
            dms = [json.loads(row[0]) for row in rows if row[0]]
            logger.debug(f"Loaded {len(dms)} DMs from cache")
            return dms
        except Exception as e:
            logger.error(f"Failed to load DMs: {e}")
            return []
    
    # === USERS ===
    
    def save_user(self, user_id: str, user_data: Dict[str, Any]):
        """Cache user info."""
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO users (id, username, global_name, avatar, data, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                user_data.get('username'),
                user_data.get('global_name'),
                user_data.get('avatar'),
                json.dumps(user_data),
                now
            ))
            
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to save user: {e}")
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load user from cache."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT data FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            
            if row and row[0]:
                return json.loads(row[0])
            return None
        except Exception as e:
            logger.error(f"Failed to load user: {e}")
            return None
    
    # === MESSAGES ===
    
    def save_messages(self, channel_id: str, messages: List[Dict[str, Any]]):
        """Cache messages for a channel."""
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()
            
            for msg in messages:
                author = msg.get('author', {})
                cursor.execute('''
                    INSERT OR REPLACE INTO messages (id, channel_id, author_id, author_name, content, timestamp, data, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    msg.get('id'),
                    channel_id,
                    author.get('id'),
                    author.get('username'),
                    msg.get('content'),
                    msg.get('timestamp'),
                    json.dumps(msg),
                    now
                ))
            
            self.conn.commit()
            logger.debug(f"Cached {len(messages)} messages for channel {channel_id}")
        except Exception as e:
            logger.error(f"Failed to save messages: {e}")
    
    def get_messages(self, channel_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Load messages for a channel from cache."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'SELECT data FROM messages WHERE channel_id = ? ORDER BY timestamp DESC LIMIT ?',
                (channel_id, limit)
            )
            rows = cursor.fetchall()
            
            messages = [json.loads(row[0]) for row in rows if row[0]]
            messages.reverse()  # Chronological order
            return messages
        except Exception as e:
            logger.error(f"Failed to load messages: {e}")
            return []
    
    # === CACHE METADATA ===
    
    def set_cache_meta(self, key: str, value: str):
        """Store cache metadata."""
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO cache_meta (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', (key, value, now))
            
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to set cache meta: {e}")
    
    def get_cache_meta(self, key: str) -> Optional[str]:
        """Get cache metadata."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT value FROM cache_meta WHERE key = ?', (key,))
            row = cursor.fetchone()
            
            return row[0] if row else None
        except Exception as e:
            logger.error(f"Failed to get cache meta: {e}")
            return None
    
    def is_cache_fresh(self, key: str, max_age_minutes: int = 60) -> bool:
        """Check if cache is still fresh."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT updated_at FROM cache_meta WHERE key = ?', (key,))
            row = cursor.fetchone()
            
            if not row:
                return False
            
            updated_at = datetime.fromisoformat(row[0])
            age = datetime.now() - updated_at
            
            return age < timedelta(minutes=max_age_minutes)
        except Exception as e:
            logger.error(f"Failed to check cache freshness: {e}")
            return False

    # === FAVORITES ===

    def add_favorite(self, item_id: str, item_type: str, item_name: str = None) -> bool:
        """Add an item to favorites.

        Args:
            item_id: The ID of the guild or DM
            item_type: Either 'guild' or 'dm'
            item_name: Optional name of the item for reference

        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO favorites (item_id, item_type, item_name, added_at)
                VALUES (?, ?, ?, ?)
            ''', (item_id, item_type, item_name, datetime.now().isoformat()))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to add favorite: {e}")
            return False

    def remove_favorite(self, item_id: str) -> bool:
        """Remove an item from favorites.

        Args:
            item_id: The ID of the guild or DM

        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM favorites WHERE item_id = ?', (item_id,))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to remove favorite: {e}")
            return False

    def load_favorites(self) -> set:
        """Load all favorite item IDs from database.

        Returns:
            Set of favorite item IDs
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT item_id FROM favorites')
            rows = cursor.fetchall()
            return set(row[0] for row in rows)
        except Exception as e:
            logger.error(f"Failed to load favorites: {e}")
            return set()

    def is_favorite(self, item_id: str) -> bool:
        """Check if an item is favorited.

        Args:
            item_id: The ID of the guild or DM

        Returns:
            True if favorited, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM favorites WHERE item_id = ?', (item_id,))
            count = cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            logger.error(f"Failed to check favorite status: {e}")
            return False
