"""Persistent Discord Gateway connection with local state caching."""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
import aiohttp
import zlib

logger = logging.getLogger(__name__)


class DiscordCabinet:
    """In-memory cache for Discord state (Cabinet equivalent to Go implementation)."""

    def __init__(self):
        """Initialize the state cache."""
        self.guilds: Dict[str, dict] = {}  # guild_id -> guild_data
        self.channels: Dict[str, dict] = {}  # channel_id -> channel_data
        self.members: Dict[str, Dict[str, dict]] = {}  # guild_id -> {user_id -> member_data}
        self.roles: Dict[str, List[dict]] = {}  # guild_id -> [roles]
        self.users: Dict[str, dict] = {}  # user_id -> user_data
        self.ready = False

    def get_guild(self, guild_id: str) -> Optional[dict]:
        """Get guild by ID."""
        return self.guilds.get(guild_id)

    def get_channel(self, channel_id: str) -> Optional[dict]:
        """Get channel by ID."""
        return self.channels.get(channel_id)

    def get_member(self, guild_id: str, user_id: str) -> Optional[dict]:
        """Get member data from cache."""
        return self.members.get(guild_id, {}).get(user_id)

    def get_guild_members(self, guild_id: str) -> Dict[str, dict]:
        """Get all members for a guild."""
        return self.members.get(guild_id, {})

    def get_guild_roles(self, guild_id: str) -> List[dict]:
        """Get all roles for a guild (sorted by position)."""
        roles = self.roles.get(guild_id, [])
        return sorted(roles, key=lambda r: r.get('position', 0), reverse=True)

    def update_guild(self, guild_data: dict) -> None:
        """Update guild in cache."""
        guild_id = guild_data.get('id')
        if guild_id:
            self.guilds[guild_id] = guild_data

    def update_channel(self, channel_data: dict) -> None:
        """Update channel in cache."""
        channel_id = channel_data.get('id')
        if channel_id:
            self.channels[channel_id] = channel_data

    def update_member(self, guild_id: str, user_id: str, member_data: dict) -> None:
        """Update member in cache."""
        if guild_id not in self.members:
            self.members[guild_id] = {}
        self.members[guild_id][user_id] = member_data

    def update_roles(self, guild_id: str, roles: List[dict]) -> None:
        """Update guild roles in cache."""
        self.roles[guild_id] = roles

    def update_user(self, user_data: dict) -> None:
        """Update user in cache."""
        user_id = user_data.get('id')
        if user_id:
            self.users[user_id] = user_data


class DiscordGateway:
    """Persistent Discord Gateway connection with event handling."""

    GATEWAY_URL = "wss://gateway.discord.gg/?v=10&encoding=json&compress=zlib-stream"
    HEARTBEAT_INTERVAL = 45  # seconds

    def __init__(self, token: str):
        """Initialize the gateway client."""
        self.token = token
        self.state = DiscordCabinet()
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.sequence = 0
        self.session_id = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._decompress_buffer = zlib.decompressobj()
        self.ready = False

    async def connect(self) -> bool:
        """Connect to Discord gateway."""
        try:
            self.session = aiohttp.ClientSession()

            async with self.session.ws_connect(
                self.GATEWAY_URL,
                compress=0,
                heartbeat=30,
            ) as ws:
                self.ws = ws
                logger.info("Connected to Discord gateway")

                # Start receiving events
                await self._listen()

        except Exception as e:
            logger.error(f"Failed to connect to gateway: {e}")
            return False
        finally:
            if self.session:
                await self.session.close()

        return True

    async def _listen(self) -> None:
        """Listen for gateway events."""
        try:
            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.BINARY:
                    # Decompress zlib stream
                    data = self._decompress_buffer.decompress(msg.data)
                    if data:
                        await self._handle_event(json.loads(data))

                elif msg.type == aiohttp.WSMsgType.TEXT:
                    await self._handle_event(json.loads(msg.data))

                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {self.ws.exception()}")
                    break

                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    logger.warning("WebSocket connection closed")
                    break

        except Exception as e:
            logger.error(f"Error in gateway listener: {e}")

    async def _handle_event(self, payload: dict) -> None:
        """Handle incoming gateway event."""
        op = payload.get("op")
        d = payload.get("d")
        t = payload.get("t")
        s = payload.get("s")

        # Update sequence number
        if s:
            self.sequence = s

        # Handle different opcodes
        if op == 10:  # HELLO
            heartbeat_interval = d.get("heartbeat_interval", 45000) / 1000
            self._heartbeat_task = asyncio.create_task(
                self._heartbeat_loop(heartbeat_interval)
            )
            # Send IDENTIFY
            await self._identify()

        elif op == 11:  # HEARTBEAT ACK
            logger.debug("Heartbeat ACK received")

        elif op == 0:  # DISPATCH
            if t == "READY":
                await self._handle_ready(d)
            elif t == "GUILD_CREATE":
                self._handle_guild_create(d)
            elif t == "GUILD_UPDATE":
                self._handle_guild_update(d)
            elif t == "GUILD_DELETE":
                self._handle_guild_delete(d)
            elif t == "CHANNEL_CREATE":
                self._handle_channel_create(d)
            elif t == "CHANNEL_UPDATE":
                self._handle_channel_update(d)
            elif t == "CHANNEL_DELETE":
                self._handle_channel_delete(d)
            elif t == "GUILD_MEMBER_ADD":
                self._handle_member_add(d)
            elif t == "GUILD_MEMBER_UPDATE":
                self._handle_member_update(d)
            elif t == "GUILD_MEMBER_REMOVE":
                self._handle_member_remove(d)
            elif t == "GUILD_MEMBERS_CHUNK":
                self._handle_members_chunk(d)
            elif t == "GUILD_ROLE_CREATE":
                self._handle_role_create(d)
            elif t == "GUILD_ROLE_UPDATE":
                self._handle_role_update(d)
            elif t == "GUILD_ROLE_DELETE":
                self._handle_role_delete(d)

    async def _identify(self) -> None:
        """Send IDENTIFY to gateway."""
        # Calculate intents: we need GUILDS and GUILD_MEMBERS to get role/member data
        intents = (
            (1 << 0)   # GUILDS - guild create/update/delete
            | (1 << 1) # GUILD_MEMBERS - member join/update/remove
            | (1 << 2) # GUILD_BANS
            | (1 << 3) # GUILD_EMOJIS_AND_STICKERS
            | (1 << 4) # GUILD_INTEGRATIONS
            | (1 << 5) # GUILD_WEBHOOKS
            | (1 << 6) # GUILD_INVITES
            | (1 << 7) # GUILD_VOICE_STATES
            | (1 << 8) # GUILD_PRESENCES
            | (1 << 9) # GUILD_MESSAGES
            | (1 << 10) # GUILD_MESSAGE_REACTIONS
        )

        payload = {
            "op": 2,
            "d": {
                "token": self.token,
                "intents": intents,
                "properties": {
                    "os": "Linux",
                    "browser": "Discordo",
                    "device": "Discordo",
                },
            },
        }
        await self.ws.send_json(payload)
        logger.info("IDENTIFY sent with intents")

    async def _heartbeat_loop(self, interval: float) -> None:
        """Send periodic heartbeats."""
        try:
            while self.ws and not self.ws.closed:
                await asyncio.sleep(interval)
                await self.ws.send_json({"op": 1, "d": self.sequence})
                logger.debug(f"Heartbeat sent (sequence: {self.sequence})")
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")

    async def _handle_ready(self, data: dict) -> None:
        """Handle READY event."""
        logger.info(f"READY received for user {data.get('user', {}).get('username')}")
        self.session_id = data.get("session_id")

        # Cache user
        user = data.get("user", {})
        self.state.update_user(user)

        # Cache guilds
        for guild in data.get("guilds", []):
            self.state.update_guild(guild)
            # Cache guild data on ready
            guild_id = guild.get('id')
            if guild_id:
                # Cache channels
                for channel in guild.get('channels', []):
                    self.state.update_channel(channel)
                # Cache roles
                roles = guild.get('roles', [])
                self.state.update_roles(guild_id, roles)
                # Cache members
                for member in guild.get('members', []):
                    user_id = member.get('user', {}).get('id')
                    if user_id:
                        self.state.update_member(guild_id, user_id, member)

        # Request guild members for all guilds to ensure we have full member list
        logger.info(f"READY: Requesting members for {len(self.state.guilds)} guilds...")
        await self._request_all_guild_members()
        logger.info(f"READY: Member requests sent, waiting for GUILD_MEMBERS_CHUNK events...")

        self.state.ready = True
        logger.info(f"✓ Gateway ready: {len(self.state.guilds)} guilds cached")
        logger.info(f"  Initial members synced: {len(self.state.members)}")
        logger.info(f"  Total roles synced: {sum(len(r) for r in self.state.roles.values())}")
        logger.info(f"  Member chunks will arrive async (may take a moment for large guilds)")

    async def _request_all_guild_members(self) -> None:
        """Request member chunks for all guilds."""
        for guild_id in self.state.guilds:
            await self._request_guild_members(guild_id)

    async def _request_guild_members(self, guild_id: str) -> None:
        """Request members for a specific guild."""
        payload = {
            "op": 8,  # REQUEST_GUILD_MEMBERS
            "d": {
                "guild_id": guild_id,
                "query": "",  # Empty query returns all members
                "limit": 0,   # 0 means all members
            }
        }
        try:
            await self.ws.send_json(payload)
            logger.info(f"Requested members for guild {guild_id}")
        except Exception as e:
            logger.error(f"Failed to request members: {e}")

    def _handle_guild_create(self, guild_data: dict) -> None:
        """Handle GUILD_CREATE event."""
        guild_id = guild_data.get("id")
        self.state.update_guild(guild_data)

        # Cache channels
        for channel in guild_data.get("channels", []):
            self.state.update_channel(channel)

        # Cache roles
        roles = guild_data.get("roles", [])
        self.state.update_roles(guild_id, roles)

        # Cache members
        for member in guild_data.get("members", []):
            user_id = member.get("user", {}).get("id")
            if user_id:
                self.state.update_member(guild_id, user_id, member)

        logger.debug(f"GUILD_CREATE: {guild_data.get('name')} ({guild_id})")

    def _handle_guild_update(self, guild_data: dict) -> None:
        """Handle GUILD_UPDATE event."""
        self.state.update_guild(guild_data)

    def _handle_guild_delete(self, guild_data: dict) -> None:
        """Handle GUILD_DELETE event."""
        guild_id = guild_data.get("id")
        if guild_id in self.state.guilds:
            del self.state.guilds[guild_id]
        if guild_id in self.state.members:
            del self.state.members[guild_id]
        if guild_id in self.state.roles:
            del self.state.roles[guild_id]

    def _handle_channel_create(self, channel_data: dict) -> None:
        """Handle CHANNEL_CREATE event."""
        self.state.update_channel(channel_data)

    def _handle_channel_update(self, channel_data: dict) -> None:
        """Handle CHANNEL_UPDATE event."""
        self.state.update_channel(channel_data)

    def _handle_channel_delete(self, channel_data: dict) -> None:
        """Handle CHANNEL_DELETE event."""
        channel_id = channel_data.get("id")
        if channel_id in self.state.channels:
            del self.state.channels[channel_id]

    def _handle_member_add(self, data: dict) -> None:
        """Handle GUILD_MEMBER_ADD event."""
        guild_id = data.get("guild_id")
        member = data
        user_id = member.get("user", {}).get("id")
        if user_id:
            self.state.update_member(guild_id, user_id, member)

    def _handle_member_update(self, data: dict) -> None:
        """Handle GUILD_MEMBER_UPDATE event."""
        guild_id = data.get("guild_id")
        member = data
        user_id = member.get("user", {}).get("id")
        if user_id:
            self.state.update_member(guild_id, user_id, member)

    def _handle_member_remove(self, data: dict) -> None:
        """Handle GUILD_MEMBER_REMOVE event."""
        guild_id = data.get("guild_id")
        user_id = data.get("user", {}).get("id")
        if guild_id in self.state.members and user_id in self.state.members[guild_id]:
            del self.state.members[guild_id][user_id]

    def _handle_members_chunk(self, data: dict) -> None:
        """Handle GUILD_MEMBERS_CHUNK event."""
        guild_id = data.get("guild_id")
        members = data.get("members", [])
        logger.info(f"GUILD_MEMBERS_CHUNK: guild {guild_id}, received {len(members)} members")
        for member in members:
            user_id = member.get("user", {}).get("id")
            if user_id:
                member_roles = member.get("roles", [])
                logger.debug(f"  Member: {member.get('user', {}).get('username', 'unknown')} (roles: {len(member_roles)})")
                self.state.update_member(guild_id, user_id, member)

    def _handle_role_create(self, data: dict) -> None:
        """Handle GUILD_ROLE_CREATE event."""
        guild_id = data.get("guild_id")
        role = data.get("role")
        if role:
            roles = self.state.get_guild_roles(guild_id)
            roles.append(role)
            self.state.update_roles(guild_id, roles)

    def _handle_role_update(self, data: dict) -> None:
        """Handle GUILD_ROLE_UPDATE event."""
        guild_id = data.get("guild_id")
        role = data.get("role")
        if role:
            roles = self.state.get_guild_roles(guild_id)
            # Update role in list
            role_id = role.get("id")
            for i, r in enumerate(roles):
                if r.get("id") == role_id:
                    roles[i] = role
                    break
            self.state.update_roles(guild_id, roles)

    def _handle_role_delete(self, data: dict) -> None:
        """Handle GUILD_ROLE_DELETE event."""
        guild_id = data.get("guild_id")
        role_id = data.get("role_id")
        roles = self.state.get_guild_roles(guild_id)
        self.state.update_roles(guild_id, [r for r in roles if r.get("id") != role_id])

    async def close(self) -> None:
        """Close the gateway connection."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self.ws:
            await self.ws.close()
        if self.session:
            await self.session.close()
