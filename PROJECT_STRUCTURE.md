# Discordo Python Project Structure

This document outlines the Python equivalent structure of the Go Discordo implementation.

## File Mapping: Go → Python

### Core Application
| Go File | Python File | Purpose |
|---------|-------------|---------|
| main.go | main.py | Application entry point |
| cmd/root.go | discordo/cmd/cmd.py | CLI argument parsing and setup |
| cmd/application.go | discordo/cmd/application.py | Main TUI application |
| cmd/state.go | discordo/cmd/state.py | Discord state management |

### UI Components
| Go File | Python File | Purpose |
|---------|-------------|---------|
| cmd/guilds_tree.go | discordo/cmd/guilds_tree.py | Guild/channel navigation tree |
| cmd/messages_list.go | discordo/cmd/messages_list.py | Message display widget |
| cmd/message_input.go | discordo/cmd/message_input.py | Message composition widget |

### Configuration
| Go File | Python File | Purpose |
|---------|-------------|---------|
| internal/config/config.go | discordo/internal/config.py | Configuration loading |
| internal/config/keys.go | discordo/internal/keys.py | Keybinding definitions |
| internal/config/theme.go | discordo/internal/theme.py | Theme configuration |
| internal/config/border.go | (merged with theme.py) | Border styling |

### Utilities
| Go File | Python File | Purpose |
|---------|-------------|---------|
| internal/consts/consts.go | discordo/internal/consts.py | Application constants |
| internal/logger/logger.go | discordo/internal/logger.py | Logging configuration |
| internal/http/client.go | discordo/internal/http_client.py | HTTP client setup |
| internal/http/headers.go | discordo/internal/http_headers.py | HTTP headers |
| internal/http/props.go | (merged with http_headers.py) | Identify properties |
| internal/http/transport.go | discordo/internal/transport.py | HTTP transport |
| internal/cache/cache.go | discordo/internal/cache.py | Completion cache |

## Key Differences: Go vs Python

### Language Features
- **Error Handling**: Go's explicit error returns → Python's exceptions
- **Concurrency**: Go goroutines/channels → Python asyncio/threading
- **Type System**: Go's strict typing → Python's dataclasses with type hints
- **Memory Management**: Go's garbage collection → Python's automatic GC

### Framework Differences
- **TUI**: tview (Go) → Textual (Python)
- **Graphics**: rasterm (Go, Kitty protocol) → textual-image (Python, auto-handles protocols)
- **Discord API**: arikawa/v3 (Go) → discord.py (Python)
- **State Management**: ningen/v3 (Go) → discord.py built-in caches (Python)

### Architecture Alignments
1. **Application Structure**: Both use nested panels (Guilds Tree, Messages List, Message Input)
2. **Event Handling**: Both use event handlers for Discord gateway events
3. **Configuration**: Both load from TOML files with same structure
4. **Authentication**: Both use secure keyring storage for tokens
5. **Keybindings**: Both support customizable vim-style keybindings

## Implementation Status

### ✅ Completed
- Core application structure
- Configuration management
- Discord state management
- UI component scaffolding
- Keybinding system
- Theme configuration
- HTTP client setup
- Caching system

### 🔄 In Progress
- Textual widget integration
- Rich message rendering
- Image rendering with textual-image
- Event loop integration
- Async message operations

### 📋 Not Yet Implemented
- Login form UI
- Markdown rendering (discordmd equivalent)
- Notification system
- UI utility helpers
- Permission checking
- Member color resolution
- Auto-completion with fuzzy matching

## Running the Application

### Installation
```bash
pip install -r requirements.txt
```

### First Run
```bash
python main.py --token YOUR_DISCORD_TOKEN
```

### Configuration
Edit `~/.config/discordo/config.toml` after first run to customize keybindings and theme.

## Next Steps

1. **Complete Widget Integration**: Integrate Textual widgets fully
2. **Implement Message Rendering**: Use Rich for message formatting
3. **Add Image Support**: Configure textual-image for inline images
4. **Event Loop Integration**: Properly wire Discord events to UI updates
5. **User Authentication**: Implement login form
6. **Mention Completion**: Add fuzzy matching for user mentions
7. **Error Handling**: Comprehensive error handling and recovery
8. **Testing**: Add unit and integration tests

## Development Notes

### Architecture Philosophy
The Python version maintains the same architectural philosophy as the Go version:
- Clear separation of concerns (state, UI, config)
- Event-driven updates from Discord gateway
- Keyboard-driven navigation
- Configuration-driven behavior
- Secure credential storage

### Technology Choices
- **discord.py**: Mature, feature-complete Discord API library
- **Textual**: Modern TUI framework with native Python async support
- **Rich**: Beautiful terminal formatting and rendering
- **textual-image**: Native image support (solves the tcell/rasterm incompatibility)

### Key Improvements Over Go Version
- **Native image rendering**: Textual/Rich support images natively
- **Async/await**: More intuitive than Go's goroutines for TUI
- **Rich ecosystem**: More Python libraries for terminal apps
- **Easier development**: Python's dynamic typing for faster iteration

## File Organization

```
discordo-python/
├── main.py                          # Entry point
├── requirements.txt                 # Dependencies
├── pyproject.toml                   # Project metadata
├── README.md                        # User documentation
├── PROJECT_STRUCTURE.md             # This file
│
├── discordo/
│   ├── __init__.py                 # Package init
│   ├── cmd.py                      # (deprecated) moved to cmd/
│   │
│   ├── cmd/
│   │   ├── __init__.py
│   │   ├── cmd.py                  # CLI entry point
│   │   ├── application.py          # Main app
│   │   ├── state.py                # Discord state
│   │   ├── guilds_tree.py          # Guild/channel tree
│   │   ├── messages_list.py        # Message display
│   │   └── message_input.py        # Message input
│   │
│   └── internal/
│       ├── __init__.py
│       ├── consts.py               # Constants
│       ├── logger.py               # Logging
│       ├── config.py               # Configuration
│       ├── keys.py                 # Keybindings
│       ├── theme.py                # Theme/styling
│       ├── cache.py                # Completion cache
│       ├── http_client.py          # HTTP client
│       ├── http_headers.py         # HTTP headers
│       └── transport.py            # Transport layer
```
