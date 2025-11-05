# Discordo Python - Architecture & Message Rendering Flow

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DISCORDO APPLICATION                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              TEXTUAL TUI APPLICATION (DiscordoApp)           │  │
│  │                                                               │  │
│  │  ┌─────────────────┐  ┌────────────────┐  ┌──────────────┐  │  │
│  │  │  Guilds Panel   │  │  Messages      │  │ Input Panel  │  │  │
│  │  │ CollapsibleOpt  │  │ Panel (RichLog)│  │ (Placeholder)│  │  │
│  │  │                 │  │                │  │              │  │  │
│  │  │ • DMs           │  │ • Timestamps   │  │ • Composition│  │  │
│  │  │ • Guilds        │  │ • Authors      │  │ • Sending    │  │  │
│  │  │ • Channels      │  │ • Content      │  │              │  │  │
│  │  │ • Favorites     │  │ • Embeds       │  └──────────────┘  │  │
│  │  └─────────────────┘  │ • Attachments  │                    │  │
│  │                       │ • Reactions    │                    │  │
│  │                       └────────────────┘                    │  │
│  │                                                               │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │          STATUS BAR (Keybinding hints)               │   │  │
│  │  └──────────────────────────────────────────────────────┘   │  │
│  │                                                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              ↕ (Events & Updates)                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              DISCORD STATE MANAGEMENT                         │  │
│  │                   (DiscordState)                              │  │
│  │                                                                │  │
│  │  • discord.py Client                                         │  │
│  │  • Event Handlers (ready, message, edit, delete)            │  │
│  │  • Caches (guilds, channels, messages)                      │  │
│  │  • User Token Authentication                                │  │
│  │                                                                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              ↕ (API Calls)                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              DISCORD REST API (aiohttp)                       │  │
│  │                                                                │  │
│  │  • https://discord.com/api/v10/users/@me                    │  │
│  │  • https://discord.com/api/v10/users/@me/guilds            │  │
│  │  • https://discord.com/api/v10/channels/{id}/messages      │  │
│  │  • https://discord.com/api/v10/guilds/{id}/members/{id}   │  │
│  │                                                                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              ↕ (HTTP Requests/Responses)           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              CONFIGURATION SYSTEM                             │  │
│  │                                                                │  │
│  │  ┌─────────────────────────┐   ┌──────────────────────┐     │  │
│  │  │  Default Config (Embedded) │  │ User Config (TOML)  │     │  │
│  │  │                            │  │ ~/.config/discordo/ │     │  │
│  │  │ • timestamps.format        │  │                    │     │  │
│  │  │ • theme config             │  │ (overrides defaults)│     │  │
│  │  │ • keybindings              │  │                    │     │  │
│  │  └─────────────────────────┘   └──────────────────────┘     │  │
│  │                   ↓ (merged)                                  │  │
│  │              Config object (dataclass)                       │  │
│  │                                                                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Message Rendering Pipeline

### Complete Flow from Channel Selection to Display

```
1. USER INTERACTION
   ├─ Selects channel in Guilds Tree
   │  └─ CollapsibleOptionList.on_option_list_option_selected()
   │
   └─ Event: CollapsibleOptionList.ItemSelected

2. APPLICATION EVENT HANDLER
   ├─ DiscordoApp.on_collapsible_option_list_item_selected()
   │
   ├─ Extracts channel_data from event
   │
   └─ Creates async task: _load_channel_messages(channel_data)

3. API LOAD PHASE
   ├─ _load_channel_messages()
   │  │
   │  ├─ Get token from keyring
   │  │
   │  ├─ Create aiohttp session with headers
   │  │  ├─ Authorization: token
   │  │  ├─ User-Agent: Browser-like user agent
   │  │  ├─ Accept: */*
   │  │  └─ Other HTTP headers
   │  │
   │  ├─ Fetch messages:
   │  │  └─ GET /api/v10/channels/{channel_id}/messages?limit=50
   │  │
   │  └─ Receive JSON response: List[MessageObject]

4. MESSAGE PROCESSING PHASE
   ├─ For each message in messages_raw:
   │  │
   │  ├─ Parse timestamp ISO format
   │  │  └─ datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
   │  │
   │  ├─ Convert to timezone (hardcoded: America/New_York)
   │  │  └─ pytz.timezone('America/New_York').localize(dt)
   │  │
   │  ├─ Format timestamp string
   │  │  └─ dt_ny.strftime('%Y-%m-%d %H:%M:%S')
   │  │  └─ Result: "2024-11-05 14:30:45"
   │  │
   │  ├─ Extract author information
   │  │  ├─ global_name or username
   │  │  └─ author.id
   │  │
   │  ├─ Get author color (async subcalls):
   │  │  ├─ Default: Discord blue (#5865F2)
   │  │  ├─ For guild messages:
   │  │  │  ├─ Fetch member: /api/v10/guilds/{id}/members/{user_id}
   │  │  │  ├─ Get member.roles[]
   │  │  │  ├─ Fetch roles: /api/v10/guilds/{id}/roles
   │  │  │  └─ Find highest role with color value
   │  │  │     └─ Format as hex: f"#{role['color']:06x}"
   │  │  │
   │  │  └─ Result: Hex color string like "#FF5733"
   │  │
   │  └─ Create message dict:
   │     {
   │         'id': message_id,
   │         'timestamp': "2024-11-05 14:30:45",
   │         'author': {
   │             'id': author_id,
   │             'global_name': display_name,
   │             'username': username,
   │         },
   │         'author_color': "#5865F2",
   │         'content': message_content,
   │         'embeds': [...],
   │         'attachments': [...],
   │         'reactions': [...],
   │     }
   │
   └─ Result: List[Dict] with formatted messages

5. PANEL UPDATE
   ├─ messages_panel = query_one("#messages-panel", MessagesPanel)
   │
   ├─ messages_panel.display_messages(messages, channel_data)
   │
   └─ MessagesPanel updates internal state

6. MESSAGE RENDERING PHASE (MessagesPanel)
   ├─ display_messages():
   │  ├─ Clear previous messages
   │  ├─ Set current_channel
   │  ├─ Store messages in internal list
   │  │
   │  └─ For each message (reversed - oldest first):
   │     └─ _format_message(msg)
   │
   ├─ _format_message(msg):
   │  │
   │  ├─ Extract timestamp portion:
   │  │  ├─ Split timestamp by space: "2024-11-05 14:30:45".split(' ')
   │  │  └─ time_only = timestamp[1]  # "14:30:45"
   │  │
   │  ├─ Extract author info:
   │  │  └─ author_name = author['global_name'] or author['username']
   │  │  └─ user_color = msg['author_color']
   │  │
   │  ├─ Get message content:
   │  │  └─ content = msg['content']
   │  │
   │  ├─ Split content by newlines:
   │  │  └─ lines = content.split('\n')
   │  │
   │  ├─ For each line (line_idx, line):
   │  │  │
   │  │  ├─ Create Rich.Text object: message = Text()
   │  │  │
   │  │  ├─ If first line (line_idx == 0):
   │  │  │  ├─ message.append(time_only, style="dim")
   │  │  │  ├─ message.append(" ")
   │  │  │  ├─ message.append(author_name, style=f"bold {user_color}")
   │  │  │  ├─ message.append(": ")
   │  │  │  │
   │  │  │  └─ Result on screen:
   │  │  │     "14:30:45 JohnDoe#5865F2: This is the first line"
   │  │  │      ^dim    ^author_color  ^default
   │  │  │
   │  │  ├─ Else (continuation lines):
   │  │  │  ├─ message.append("    ")  # 4-space indent
   │  │  │  │
   │  │  │  └─ Result on screen:
   │  │  │     "    and this is the second line"
   │  │  │
   │  │  └─ message.append(line)  # Add actual content
   │  │
   │  └─ Write to RichLog:
   │     └─ self.richlog.write(message)

7. TEXTUAL RENDERING
   ├─ RichLog widget with wrap=True
   │  ├─ Automatically wraps long lines to terminal width
   │  ├─ Preserves styles and colors
   │  └─ Scrollable content
   │
   └─ Display on screen with all formatting preserved

---

## Key Configuration Points

### Timestamp Configuration

**File**: `discordo/internal/config.py`

```python
@dataclass
class Timestamps:
    enabled: bool = True
    format: str = "3:04PM"
```

**Default TOML**:
```toml
[timestamps]
enabled = true
format = "3:04PM"
```

**Current Implementation**:
- Default format is defined but NOT used in application.py
- Code hardcodes format: `strftime('%Y-%m-%d %H:%M:%S')`
- Only time portion displayed: `timestamp.split(' ')[1]`
- Result: Shows "HH:MM:SS" format (e.g., "14:30:45")

**To Use Config Format**:
- Modify application.py line 606 to:
  ```python
  formatted_ts = dt_ny.strftime(self.cfg.timestamps.format)
  ```
- Then extract time portion or full timestamp based on config

### Message Display Width & Wrapping

**File**: `discordo/cmd/application.py`

**CSS Configuration**:
```python
CSS = """
#messages-panel {
    width: 1fr;  # Flexible width - fills remaining space
    height: 1fr; # Flexible height
}
```

**RichLog Widget**:
```python
yield RichLog(id="messages-richlog", wrap=True)
```

**Properties**:
- `wrap=True`: Enables word wrapping at terminal width
- Auto-adapts to terminal resizing
- Line breaks in content are preserved

### Author Color Resolution

**Process**:
1. Default: Discord's default blue (#5865F2)
2. For guild messages: Fetch member's highest colored role
3. Format as Rich color string: f"bold {hex_color}"

**Code Location**: `application.py:613-641`

---

## File Organization & Key Components

### Core Application Files

```
discordo/cmd/
├── application.py (770+ lines)
│   ├── DiscordoApp (Main Textual App)
│   │   ├── compose() - Layout definition
│   │   ├── on_mount() - Initialization
│   │   ├── connect_discord() - API login
│   │   └── _load_channel_messages() - Message loading
│   │
│   ├── CollapsibleOptionList (Guilds sidebar)
│   │   ├── rebuild_list() - UI updates
│   │   ├── on_option_list_option_selected() - Item selection
│   │   └── toggle_favorite() - Favorite management
│   │
│   ├── MessagesPanel (Message display)
│   │   ├── display_messages() - Update display
│   │   ├── _format_message() - Format single message
│   │   ├── clear_messages() - Clear display
│   │   └── on_mount() - Initialize RichLog
│   │
│   ├── InputPanel (Message input)
│   │
│   └── StatusPanel (Status bar)
│
├── messages_list.py (MessagesList class - partial/alternative implementation)
│   ├── draw_message() - Message rendering
│   ├── _draw_timestamp() - Timestamp formatting
│   ├── _draw_author() - Author name rendering
│   ├── _draw_content() - Content rendering
│   └── Various message selection methods
│
├── state.py (DiscordState class)
│   ├── Event handler registration
│   ├── Message caching
│   └── Discord connection management
│
├── cmd.py (CLI entry point)
│   ├── Argument parsing
│   ├── Config loading
│   ├── Token management
│   └── App initialization
│
└── guilds_tree.py (Guild navigation - not fully reviewed)
```

### Configuration Files

```
discordo/internal/
├── config.py (Configuration system)
│   ├── DEFAULT_CONFIG (Embedded TOML)
│   ├── Config (Main dataclass)
│   ├── Timestamps (Timestamp config)
│   ├── Keys (Keybindings config)
│   └── Theme (Theme config)
│
├── theme.py (Theme dataclasses)
│   ├── Style (Text styling)
│   ├── Theme (Complete theme)
│   ├── MessagesListTheme (Message list colors/styles)
│   └── Various theme components
│
├── ui_util.py (UI helper functions)
│   ├── Format functions
│   ├── Style utilities
│   └── UI layout helpers
│
└── Other utilities (consts, logger, keys, database, http_client, etc.)
```

---

## Important Implementation Notes

### Timestamp Handling Issue

**Current Behavior**:
- Config defines format: "3:04PM" (Go format)
- Application hardcodes: '%Y-%m-%d %H:%M:%S'
- Only time portion displayed: Split by space, take index [1]
- Result: "HH:MM:SS" format

**To Fix**:
1. Use config.timestamps.format in application.py
2. Handle Go format strings (3:04PM → Python %I:%M%p)
3. Decide on full timestamp vs. time-only display

### Message Ordering

**Current**: Messages displayed oldest-first (reversed)
```python
for msg in reversed(messages):
    self._format_message(msg)
```

- API returns newest first
- Reversed to show chronological order in display

### Author Color Fetching

**Performance Note**: Fetches member info and roles for EVERY message
- Multiple async API calls per message
- Could be optimized with bulk fetching or caching

### Configuration Not Fully Applied

**Not Used**:
- timestamps.format (hardcoded in application)
- Many theme settings (no custom theme loading)
- Some keybindings (basic set only)

**Partially Used**:
- Configuration structure is defined
- Loading mechanism works
- Not integrated into UI rendering

---

## Data Flow Diagram

```
Input: User selects channel
  │
  ↓
Event: on_collapsible_option_list_item_selected
  │
  ↓
Async Task: _load_channel_messages
  │
  ├─ API Call: GET /channels/{id}/messages?limit=50
  │  └─ Returns: List[MessageJSON]
  │
  ├─ For Each Message:
  │  ├─ Parse timestamp (ISO → datetime)
  │  ├─ Convert timezone (UTC → NY)
  │  ├─ Get author info
  │  ├─ Get author color (async API calls)
  │  └─ Create message dict
  │
  ├─ Call: messages_panel.display_messages(messages)
  │
  └─ MessagesPanel:
     ├─ For Each Message:
     │  ├─ Extract time portion
     │  ├─ Split content by lines
     │  └─ Create Rich.Text objects
     │
     ├─ Write to RichLog
     │  └─ Widget renders with wrapping/styling
     │
     └─ Display on screen
```

---

## Summary

The Discordo application follows a clear MVC-like architecture:

- **Model**: DiscordState (manages Discord connection and data)
- **View**: Textual widgets (Guilds tree, Messages panel, Input area)
- **Controller**: DiscordoApp (handles events and coordinates updates)

**Message rendering** is a multi-stage process:
1. User selects channel
2. API fetches messages (async)
3. Messages formatted with colors, timestamps, author info
4. Rich.Text objects created with proper styling
5. RichLog widget renders with automatic wrapping

**Configuration** system is in place but not fully integrated:
- TOML loading works
- Dataclasses defined for all settings
- UI rendering doesn't use all config options yet

This architecture provides good separation of concerns and is ready for further feature development.
