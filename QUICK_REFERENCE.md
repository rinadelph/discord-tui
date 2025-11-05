# Discordo Python - Quick Reference Guide

## Project at a Glance

- **Type**: Discord Terminal UI Client (TUI)
- **Framework**: Textual + Rich
- **API**: Discord REST API (aiohttp)
- **Language**: Python 3.10+
- **Entry Point**: `main.py` → `discordo/cmd/cmd.py:run()`

---

## File Map: Where to Find Things

### Message Display Logic
- **Main Implementation**: `/discordo/cmd/application.py`
  - `MessagesPanel` class (lines 163-262)
  - `_format_message()` method (lines 215-262)
  - `_load_channel_messages()` method (lines 568-666)

- **Alternative Implementation**: `/discordo/cmd/messages_list.py`
  - `MessagesList` class (RichLog subclass)
  - `draw_message()` and related methods

### Timestamp Formatting
- **Configuration**: `/discordo/internal/config.py` (lines 120-124)
  - `Timestamps` dataclass
  - Default format: `"3:04PM"` (not currently used)

- **Usage in Code**: 
  - `application.py:600-606` - Hardcoded `'%Y-%m-%d %H:%M:%S'`
  - `messages_list.py:113-123` - Correct `_format_timestamp()` method

### UI Layout & Styling
- **Layout**: `/discordo/cmd/application.py` (lines 295-320)
  - CSS styling with widget dimensions
  - Panel layout: Guilds (35px) + Messages (1fr) + Input (8px)

- **Theme**: `/discordo/internal/theme.py`
  - Style dataclasses (Style, Theme, etc.)
  - Color and attribute definitions

### Configuration
- **Config Loading**: `/discordo/internal/config.py` (lines 240-296)
- **Default Config**: Embedded `DEFAULT_CONFIG` string (lines 18-117)
- **User Config**: `~/.config/discordo/config.toml` (optional)

---

## Key Code Locations

### Message Loading Pipeline
```
User selects channel
    ↓ (application.py:370-372)
on_collapsible_option_list_item_selected()
    ↓ (application.py:568-666)
_load_channel_messages()
    ├─ API fetch: /channels/{id}/messages?limit=50
    ├─ Process each message: timestamp, author, color
    ├─ Create message dict
    └─ Call messages_panel.display_messages()
         ↓ (application.py:203-214)
    display_messages()
         ├─ Clear previous
         ├─ Iterate messages
         └─ Call _format_message() for each
              ↓ (application.py:215-262)
         _format_message()
              ├─ Extract timestamp
              ├─ Extract author
              ├─ Split content by lines
              ├─ Create Rich.Text objects
              └─ Write to RichLog
```

### Timestamp Processing
```
API Response: "2024-11-05T14:30:45.123456+00:00"
    ↓
Parse: datetime.fromisoformat(...)
    ↓
Timezone: pytz.timezone('America/New_York')
    ↓
Format: strftime('%Y-%m-%d %H:%M:%S')
    ↓
Result: "2024-11-05 14:30:45"
    ↓
Display: Split by space, take [1] → "14:30:45"
```

---

## Configuration Reference

### Timestamp Config (config.py)
```python
@dataclass
class Timestamps:
    enabled: bool = True
    format: str = "3:04PM"  # Go format string (not currently used)
```

### TOML Format
```toml
[timestamps]
enabled = true
format = "3:04PM"
```

### Common Formats
- `"3:04PM"` → Go format (12-hour with AM/PM)
- `"%H:%M"` → Python format (24-hour HH:MM)
- `"%H:%M:%S"` → Python format (24-hour HH:MM:SS)
- `"%Y-%m-%d %H:%M:%S"` → Full datetime

---

## UI Layout Structure

```css
Screen {
    layout: horizontal;
}

#guilds-panel {
    width: 35;  /* Fixed 35 characters */
    height: 100%;
}

#messages-panel {
    width: 1fr;  /* Flexible - fill remaining */
    height: 1fr;
}

#messages-richlog {
    width: 1fr;
    height: 1fr;
    wrap: true;  /* Enable word wrapping */
}

#input-panel {
    width: 1fr;
    height: 8;  /* Fixed 8 lines */
}

#status-panel {
    dock: bottom;
    height: 1;  /* Status bar */
}
```

---

## Rich/Textual Styling

### Text Styling in Code
```python
from rich.text import Text

# Create styled text
message = Text()
message.append(time_only, style="dim")  # Dimmed timestamp
message.append(" ")
message.append(author_name, style=f"bold {hex_color}")  # Bold colored author
message.append(": ")
message.append(content)  # Default styling

# Write to RichLog
richlog.write(message)
```

### Style Strings
- `"dim"` - Dimmed text
- `"bold"` - Bold text
- `"bold blue"` - Bold + blue
- `"#FF5733"` - Hex color
- `"on yellow"` - Background color

---

## API Endpoints Used

### User/Auth
```
GET /api/v10/users/@me
GET /api/v10/users/@me/guilds
GET /api/v10/users/@me/channels
```

### Messages
```
GET /api/v10/channels/{channel_id}/messages?limit=50
```

### Guild/Member Info
```
GET /api/v10/guilds/{guild_id}/members/{user_id}
GET /api/v10/guilds/{guild_id}/roles
```

---

## Data Structures

### Message Dict (Internal)
```python
{
    'id': int,
    'timestamp': "2024-11-05 14:30:45",
    'author': {
        'id': int,
        'global_name': str,
        'username': str,
    },
    'author_color': "#5865F2",
    'content': str,
    'embeds': list,
    'attachments': list,
    'reactions': list,
}
```

### Config Object (After Loading)
```python
Config(
    mouse=True,
    editor="vim",
    status="",
    markdown=True,
    hide_blocked_users=True,
    timestamps=Timestamps(enabled=True, format="3:04PM"),
    theme=Theme(...),
    keys=Keys(...),
    # ... more fields
)
```

---

## Key Classes & Methods

### DiscordoApp (Main Application)
```python
class DiscordoApp(App):
    compose()  # Define layout
    on_mount()  # Initialize
    on_collapsible_option_list_item_selected()  # Handle channel selection
    _load_channel_messages()  # Fetch and display messages
    connect_discord()  # Login to Discord
    _load_from_cache()  # Load cached data
```

### MessagesPanel (Message Display)
```python
class MessagesPanel(Static):
    display_messages()  # Update display with new messages
    _format_message()  # Format single message for display
    clear_messages()  # Clear display
```

### CollapsibleOptionList (Guilds/Channels)
```python
class CollapsibleOptionList(OptionList):
    rebuild_list()  # Refresh UI
    populate_from_data()  # Update with new data
    toggle_favorite()  # Mark/unmark favorite
```

---

## Important Implementation Details

### Message Ordering
- API returns newest first
- Code reverses for display: `for msg in reversed(messages)`
- Result: Chronological order (oldest at top)

### Timezone Handling
- Hardcoded to New York timezone: `pytz.timezone('America/New_York')`
- API provides UTC timestamps
- Converted before display

### Author Color
- Default: Discord blue `#5865F2`
- For guild messages: Fetches highest colored role
- Applied as Rich style: `f"bold {hex_color}"`

### Text Wrapping
- Enabled by `wrap=True` on RichLog
- Automatic wrapping at terminal width
- Newlines in content preserved

---

## Configuration Not Yet Implemented

- ❌ `timestamps.format` - Hardcoded in application.py
- ❌ Custom theme colors - Structure exists, not applied
- ❌ Keybinding customization - Basic set only
- ❌ Notification settings - Config exists, not implemented

---

## Quick Debugging Tips

### Check timestamp formatting
- **File**: `application.py:600-606`
- **Look for**: `strftime('%Y-%m-%d %H:%M:%S')`
- **Issue**: Hardcoded format, not using config

### Check message color assignment
- **File**: `application.py:613-641`
- **Look for**: Member color fetching logic
- **Issue**: May make too many API calls (performance)

### Check display width/wrapping
- **File**: `application.py:186`
- **Look for**: `RichLog(id="messages-richlog", wrap=True)`
- **Issue**: Width determined by terminal size

### Check config loading
- **File**: `config.py:244-296`
- **Look for**: `Config.load()` method
- **Issue**: User config must be valid TOML

---

## Common Tasks

### Add a new timestamp format
1. Update `config.toml` `[timestamps]` section
2. Modify `application.py:606` to use `self.cfg.timestamps.format`
3. Handle format string conversion (Go → Python)

### Change message display width
1. Modify CSS in `application.py` (lines 300-308)
2. Change `#messages-panel { width: 1fr; }`
3. Or adjust `#guilds-panel { width: 35; }`

### Add custom colors
1. Update theme in `config.toml`
2. Modify `_format_message()` to use theme colors
3. Apply styles when creating Rich.Text objects

### Optimize author color fetching
1. Add caching in `DiscordState`
2. Bulk fetch roles instead of per-message
3. Use cached member info for subsequent messages

---

## Testing Message Display

### Test with sample data
```python
# In application.py _format_message() for debugging:
test_msg = {
    'timestamp': '2024-11-05 14:30:45',
    'author': {'global_name': 'TestUser', 'username': 'test'},
    'author_color': '#5865F2',
    'content': 'Test message\nWith multiple lines',
}
# Add logging: logger.debug(f"Formatting: {test_msg}")
```

### Check Rich.Text rendering
```python
# Add to _format_message() for debugging:
from rich.console import Console
console = Console()
console.print(message)  # See what Rich renders
```

---

## Performance Considerations

1. **Message Pagination**: Only loads 50 messages at a time
2. **Color Fetching**: Makes async API calls for each message (could cache)
3. **Timezone Conversion**: Per-message conversion (could batch)
4. **RichLog Rendering**: Auto-wrapping may be slow for very long messages

---

## File Size Reference

| File | Lines | Purpose |
|------|-------|---------|
| application.py | ~770 | Main TUI app + message display |
| messages_list.py | ~556 | Alternative message rendering |
| config.py | ~296 | Configuration loading |
| theme.py | ~200 | Theme definitions |
| state.py | ~150+ | Discord connection management |
| cmd.py | ~96 | CLI entry point |

---

## Documentation Files in Project

- `README.md` - User-facing documentation
- `PROJECT_STRUCTURE.md` - High-level architecture
- `CODEBASE_ANALYSIS.md` - Detailed code analysis
- `ARCHITECTURE.md` - Message flow and diagrams
- `QUICK_REFERENCE.md` - This file

