# Discordo Python - Comprehensive Codebase Overview

## Project Summary

**Discordo** is a Python Discord client for the terminal using the Textual TUI framework and Rich for formatting. It's a port of the Go original with feature parity for message display, guild/channel navigation, and user authentication.

**Key Technologies:**
- **Discord API**: discord.py (user token authentication)
- **TUI Framework**: Textual
- **Text Formatting**: Rich
- **Configuration**: TOML files
- **Security**: System keyring for token storage

---

## Architecture Overview

### Application Flow

```
main.py (entry point)
    ↓
discordo/cmd/cmd.py (CLI argument parsing)
    ↓
discordo/cmd/application.py (Main TUI App - DiscordoApp)
    ├── CollapsibleOptionList (Guilds panel on left)
    ├── MessagesPanel (Messages display in center)
    └── InputPanel (Message composition)
    
Configuration Flow:
discordo/internal/config.py (TOML loading)
    ├── timestamps.format ("3:04PM" style)
    ├── theme configuration
    ├── keybindings
    └── various UI settings
```

### Core Components

#### 1. **Entry Point** (`main.py`)
- Simple entry point that imports and calls `discordo.cmd.cmd.run()`
- Sets up basic logging
- Error handling wrapper

#### 2. **Command-Line Interface** (`discordo/cmd/cmd.py`)
- Argument parsing for `--token`, `--config-path`, `--log-path`, `--log-level`
- Token management (stores in system keyring)
- Configuration loading
- App initialization

#### 3. **Main Application** (`discordo/cmd/application.py`)
- **DiscordoApp**: Main Textual App class
  - Layout: Horizontal split with guilds panel (width: 35) and messages/input panel
  - Status bar at bottom
  - Manages Discord connection and message loading
  - Keybinding handling (Up/Down/Enter/Ctrl+C/etc.)

#### 4. **Guilds Navigation** (`CollapsibleOptionList`)
- Left sidebar showing DMs, guilds, and channels
- Folder structure: Favorites, Direct Messages, Guilds
- Collapsible folders with toggle indicators (▼/▶)
- Item selection triggers message loading

#### 5. **Message Display** (`MessagesPanel` in `application.py`)
- **RichLog** widget displaying formatted messages
- Uses **Rich.Text** for styled output
- Message formatting includes:
  - Timestamp (time only, dim style)
  - Author name (bold colored based on member role)
  - Content with multiline support
  - Embeds, attachments, reactions

#### 6. **Discord State Management** (`discordo/cmd/state.py`)
- **DiscordState**: Manages Discord connection
- Event handlers for: ready, message, message_edit, message_delete
- Caches for guilds, channels, messages
- User token authentication (not bot token)

---

## Message Display Implementation

### Location & Flow

**Primary File**: `/home/alejandro/discordo-python/discordo/cmd/application.py`

#### Message Rendering Pipeline

1. **User selects a channel** from guilds tree
   - Triggers `on_collapsible_option_list_item_selected()` event
   - Calls `_load_channel_messages(channel_data)`

2. **API call to fetch messages**
   ```python
   url = f"https://discord.com/api/v10/channels/{channel_id}/messages?limit=50"
   ```
   - Loads last 50 messages for the channel
   - Fetches in reverse (oldest first for display)

3. **Message formatting** (`MessagesPanel._format_message()`)
   ```python
   - Timestamp extraction: ts.split(' ')[1] for HH:MM:SS
   - Author name: global_name or username
   - Author color: Default Discord blue (#5865F2) or member role color
   - Content: Split by newlines, handle multiline wrapping
   - First line: timestamp + author + content
   - Continuation lines: indented with 4 spaces
   ```

4. **Display to RichLog**
   - Uses `Rich.Text` objects with styles
   - Styles applied: dim, bold, colors
   - Each message written via `self.richlog.write(message)`

### Timestamp Formatting

**Configuration Location**: `discordo/internal/config.py`

```python
@dataclass
class Timestamps:
    enabled: bool = True
    format: str = "3:04PM"  # Default format
```

**How it works:**
- Configured in TOML via `timestamps.format`
- Uses Python's `strftime()` format strings
- Example formats:
  - `"3:04PM"` → "12:34PM"
  - `"%Y-%m-%d %H:%M:%S"` → "2024-11-05 14:30:45"
  - `"%H:%M"` → "14:30"

**Default Config**: `config.toml` sets `timestamps.format = "3:04PM"`

**Where used in code**:
1. `discordo/cmd/messages_list.py:113-123`:
   ```python
   def _format_timestamp(self, ts: datetime) -> str:
       return ts.strftime(self.cfg.timestamps.format)
   ```

2. `discordo/cmd/application.py:600-608`:
   ```python
   dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
   ny_tz = pytz.timezone('America/New_York')
   dt_ny = dt.astimezone(ny_tz)
   timestamp = dt_ny.strftime('%Y-%m-%d %H:%M:%S')
   ```
   - Converts UTC to New York timezone
   - Only shows time portion in display: `time_only = timestamp.split(' ')[1]`

---

## Configuration System

**Files Involved:**
1. `discordo/internal/config.py` - Configuration loading and dataclasses
2. `config.toml` - Default configuration (embedded as string)
3. `~/.config/discordo/config.toml` - User configuration (optional override)

### Configuration Structure

```toml
# Global settings
mouse = true
editor = "default"
status = "default"
markdown = true
hide_blocked_users = true
show_attachment_links = true
autocomplete_limit = 20
messages_limit = 50

# Timestamp configuration
[timestamps]
enabled = true
format = "3:04PM"

# Notification settings
[notifications]
enabled = true
duration = 0
[notifications.sound]
enabled = true
only_on_ping = true

# Keybindings
[keys]
focus_guilds_tree = "Ctrl+G"
focus_messages_list = "Ctrl+T"
... (many more bindings)

# Theme configuration
[theme.messages_list]
reply_indicator = ">"
forwarded_indicator = "<"
mention_style = { foreground = "blue" }
emoji_style = { foreground = "green" }
url_style = { foreground = "blue" }
attachment_style = { foreground = "yellow" }
```

### Configuration Loading

**Process**:
1. Load defaults from embedded `DEFAULT_CONFIG` string
2. Load user config from `~/.config/discordo/config.toml` (if exists)
3. Merge user config over defaults (user overrides)
4. Validate and set special values (editor, status, etc.)

**Access in code**:
```python
# In application.py
cfg = Config.load(config_path)
messages_panel.display_messages(messages, cfg)

# In messages_list.py
formatted_time = self.cfg.timestamps.format  # Access config
```

---

## UI Layout & Styling

### Layout Structure (CSS in Textual)

```
┌─────────────────────────────────────────────────────────┐
│ Discordo - Discord TUI Client                          │
├──────────────────┬──────────────────────────────────────┤
│                  │                                      │
│  Guilds Panel    │  Messages Panel                     │
│  (width: 35)     │  (width: 1fr - remaining)          │
│                  │  [RichLog widget]                   │
│                  │                                      │
│                  ├──────────────────────────────────────┤
│                  │  Input Panel (height: 8)            │
│                  │  [Placeholder for input]            │
├──────────────────┴──────────────────────────────────────┤
│ Status Panel (height: 1) - Keybinding hints           │
└──────────────────────────────────────────────────────────┘
```

### Message Display Width/Wrapping

**Key Property**: `RichLog(id="messages-richlog", wrap=True)`

- Textual RichLog widget with `wrap=True` enables word wrapping
- Wrapping adapts to terminal width automatically
- Messages split by newlines and rendered line-by-line
- Continuation lines indented for readability

**Implementation** (`application.py:203-262`):
```python
def display_messages(self, messages: List[dict], channel_data: dict):
    # Display messages (oldest first)
    for msg in reversed(messages):
        self._format_message(msg)

def _format_message(self, msg: dict):
    # Split content by newlines
    lines = content.split('\n')
    for line_idx, line in enumerate(lines):
        message = Text()
        
        # First line includes timestamp and author
        if line_idx == 0:
            message.append(time_only, style="dim")
            message.append(" ")
            message.append(author_name, style=f"bold {user_color}")
            message.append(": ")
        else:
            # Continuation lines indented
            message.append("    ")
        
        message.append(line)
        self.richlog.write(message)
```

### Theme & Styling

**Theme Configuration** (`discordo/internal/theme.py`):
- `Style` class: foreground, background, attributes (bold, italic, etc.)
- `Theme` class: Complete theme with title, border, guilds_tree, messages_list, mentions_list
- Rich style strings: `"bold blue"`, `"dim"`, `"on yellow"`, etc.

**Message Styling** (in `application.py`):
```python
# Timestamp styling
message.append(time_only, style="dim")

# Author styling
message.append(author_name, style=f"bold {user_color}")
# user_color from message metadata, e.g., "#5865F2"

# Content styling
message.append(line)  # Default (no special styling)
```

---

## File Locations Reference

### Core Application Files

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `main.py` | Entry point | `main()` |
| `discordo/cmd/cmd.py` | CLI parsing | `run()`, argument parser |
| `discordo/cmd/application.py` | Main TUI app | `DiscordoApp`, `MessagesPanel`, `CollapsibleOptionList` |
| `discordo/cmd/state.py` | Discord connection | `DiscordState` |
| `discordo/cmd/messages_list.py` | Message rendering | `MessagesList` class (RichLog subclass) |
| `discordo/cmd/guilds_tree.py` | Guild navigation | (Not fully reviewed, tree widget) |
| `discordo/cmd/message_input.py` | Message composition | (Placeholder) |

### Configuration & Utilities

| File | Purpose |
|------|---------|
| `discordo/internal/config.py` | Configuration loading (TOML), dataclasses for config |
| `discordo/internal/theme.py` | Theme dataclasses and styling |
| `discordo/internal/ui_util.py` | UI helper functions (formatting, styling) |
| `discordo/internal/consts.py` | Application constants |
| `discordo/internal/logger.py` | Logging setup |
| `discordo/internal/keys.py` | Keybinding definitions |
| `discordo/internal/database.py` | Local cache for guilds/DMs |
| `discordo/internal/http_client.py` | HTTP client setup |
| `discordo/internal/http_headers.py` | HTTP headers for requests |
| `discordo/internal/transport.py` | Transport layer |
| `discordo/internal/cache.py` | Completion cache |

---

## How Messages Are Displayed

### Step-by-Step Flow

1. **User selects channel** in guilds tree
   - Event: `CollapsibleOptionList.ItemSelected`
   - Handler: `DiscordoApp.on_collapsible_option_list_item_selected()`

2. **Load messages from API**
   ```python
   # application.py:_load_channel_messages()
   url = f"https://discord.com/api/v10/channels/{channel_id}/messages?limit=50"
   messages_raw = await session.get(url)
   ```

3. **Format messages for display**
   ```python
   # For each message in API response:
   # - Parse timestamp to local timezone
   # - Get author display name and role color
   # - Create message dict with: timestamp, author, content, etc.
   ```

4. **Render to MessagesPanel**
   ```python
   # application.py:_load_channel_messages()
   self.messages_panel.display_messages(messages, channel_data)
   ```

5. **MessagesPanel renders each message**
   ```python
   # application.py:MessagesPanel._format_message()
   # For each line in message content:
   # - Create Rich.Text object
   # - Add timestamp (first line only)
   # - Add author name with color
   # - Add message content
   # - Write to RichLog widget
   ```

### Message Data Structure

```python
message = {
    'id': int,
    'timestamp': str,  # "2024-11-05 14:30:45"
    'author': {
        'id': int,
        'global_name': str,
        'username': str,
    },
    'author_color': str,  # Hex color like "#5865F2"
    'content': str,  # Message text
    'embeds': list,  # Embed objects
    'attachments': list,  # Attachment objects
    'reactions': list,  # Reaction objects
}
```

---

## Timestamp Handling

### Default Configuration
- Format: `"3:04PM"` (Go style format string)
- Enabled by default
- Converted to 12-hour time with AM/PM

### Conversion Process in Code

**File**: `discordo/cmd/application.py:600-606`

```python
# Parse ISO format timestamp from API
timestamp = msg.get('timestamp', '')  # "2024-11-05T14:30:45.123456+00:00"

# Convert to datetime
dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

# Convert to New York timezone (hardcoded)
ny_tz = pytz.timezone('America/New_York')
dt_ny = dt.astimezone(ny_tz)

# Format as string
timestamp = dt_ny.strftime('%Y-%m-%d %H:%M:%S')

# Extract time portion for display
time_only = timestamp.split(' ')[1]  # "14:30:45"
```

### Config Integration

**File**: `discordo/internal/config.py:113-123`

```python
@dataclass
class Timestamps:
    enabled: bool = True
    format: str = "3:04PM"

def _format_timestamp(self, ts: datetime) -> str:
    return ts.strftime(self.cfg.timestamps.format)
```

**Note**: The config format is currently not used in `application.py` - timestamps are hardcoded as `'%Y-%m-%d %H:%M:%S'` and only the time portion is displayed.

---

## Key Features & Implementation Status

### Implemented
- ✅ Application startup and configuration loading
- ✅ Token authentication via keyring
- ✅ Guild and DM list display (collapsible)
- ✅ Message loading from API (last 50 messages)
- ✅ Message formatting with author, timestamp, content
- ✅ Timezone conversion (UTC to NY)
- ✅ Author color based on member roles
- ✅ Multiline message support with wrapping
- ✅ Status bar with keybinding hints
- ✅ Keyboard navigation (Up/Down/Enter)

### Partially Implemented
- ⚠️ Embeds, attachments, reactions (structure exists, not full rendering)
- ⚠️ Message composition (placeholder)
- ⚠️ Markdown rendering (config exists, not implemented)
- ⚠️ Image display (textual-image ready, not integrated)

### Not Yet Implemented
- ❌ Message editing/deletion UI
- ❌ Reply functionality with quoted text
- ❌ Mention autocomplete
- ❌ Custom theme loading from config
- ❌ Notification system
- ❌ Reaction interaction

---

## Customization Points

### Timestamp Format
**File**: `~/.config/discordo/config.toml`
```toml
[timestamps]
enabled = true
format = "%Y-%m-%d %H:%M:%S"  # Python strftime format
```

### Message Display Width
**File**: `discordo/cmd/application.py`
- Line 186: `wrap=True` enables wrapping
- Line 303: `#messages-panel { width: 1fr; }` (flexible width)
- Line 40: `#guilds-panel { width: 35; }` (fixed width guilds)

### Colors & Styling
**File**: `config.toml` (theme section)
```toml
[theme.messages_list]
mention_style = { foreground = "blue" }
emoji_style = { foreground = "green" }
url_style = { foreground = "blue" }
attachment_style = { foreground = "yellow" }
```

### Keybindings
**File**: `config.toml` (keys section)
```toml
[keys.messages_list]
select_previous = "Rune[k]"
select_next = "Rune[j]"
reply = "Rune[r]"
...
```

---

## Dependencies

**Key Libraries**:
- `discord.py` - Discord API
- `textual` - TUI framework
- `rich` - Terminal text formatting
- `keyring` - Secure credential storage
- `aiohttp` - HTTP client
- `pytz` - Timezone handling
- `tomllib` - TOML configuration parsing

---

## Summary

This Python Discord TUI client uses a clean architecture with separated concerns:

1. **UI Layer**: Textual widgets (OptionList, RichLog, Static)
2. **Logic Layer**: DiscordoApp managing state and events
3. **Config Layer**: TOML-based configuration with dataclasses
4. **API Layer**: Direct aiohttp calls to Discord REST API

**Message display** is handled by the `MessagesPanel` widget which uses Rich's `Text` objects to render formatted messages with timestamps, author names, colors, and content. The system supports multiline messages, timezone conversion, and configurable timestamp formats.
