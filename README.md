# Discordo - Discord TUI Client

A lightweight, feature-rich Discord client for the terminal with native image rendering support using Textual and Rich.

## Features

- **TUI Interface** - Full-featured terminal user interface using Textual
- **Message Display** - Rich message formatting with embeds, reactions, and attachments
- **Image Rendering** - Native support for displaying images inline using textual-image
- **User Authentication** - Secure token storage using system keyring
- **Message Composition** - Send messages with mentions, replies, and file attachments
- **Guild Navigation** - Browse servers, channels, and direct messages
- **User Status Indicators** - See online status of message authors
- **Keyboard-Driven** - Vim-style keybindings with customizable shortcuts

## Requirements

- Python 3.10+
- Kitty terminal emulator (or any terminal supporting modern graphics protocols)
- Discord account with valid user token

## Installation

### From Source

```bash
git clone https://github.com/ayn2op/discordo-python.git
cd discordo-python
pip install -r requirements.txt
pip install -e .
```

### Using pip

```bash
pip install discordo
```

## Configuration

Configuration is stored in `~/.config/discordo/config.toml`

### Getting Your Discord Token

**Warning**: Never share your Discord token! It gives full access to your account.

1. Open Discord in your web browser
2. Open Developer Tools (F12)
3. Go to Application > Cookies > discord.com
4. Copy the value of the `__Secure-LATEST_USER_TOKEN` cookie
5. Run `discord --token YOUR_TOKEN` (it will be saved to keyring for future use)

Or store the token in your system keyring:

```bash
keyring set discordo token YOUR_TOKEN
```

## Usage

```bash
# First time: provide token via flag
discord --token YOUR_TOKEN

# Subsequent runs: token is retrieved from keyring
discord
```

### Keybindings

**Global Navigation:**
- `Tab` - Cycle to next panel
- `Shift+Tab` - Cycle to previous panel
- `Ctrl+G` - Focus guilds tree
- `Ctrl+T` - Focus messages list
- `Ctrl+Space` - Focus message input
- `Ctrl+B` - Toggle guilds tree visibility
- `Ctrl+C` or `Ctrl+D` - Logout and quit

**Guilds Tree:**
- `j/Down` - Next guild/channel
- `k/Up` - Previous guild/channel
- `g` - First guild/channel
- `G` - Last guild/channel
- `Enter/Right` - Select/expand
- `Left` - Collapse parent
- `i` - Copy guild/channel ID

**Messages List:**
- `j/Down` - Next message
- `k/Up` - Previous message
- `g` - First message
- `G` - Last message
- `r` - Reply to message
- `R` - Reply with mention
- `e` - Edit message
- `d`/`D` - Delete message
- `o` - Open URLs/attachments
- `y` - Copy message content
- `u` - Copy message URL
- `i` - Copy message ID

**Message Input:**
- `Enter` - Send message
- `Ctrl+V` - Paste from clipboard
- `Ctrl+E` - Open external editor
- `Ctrl+\\` - Open file picker
- `Tab` - Complete mention
- `Esc` - Cancel composition/reply

## Configuration

Edit `~/.config/discordo/config.toml` to customize:

- Keybindings
- Theme and colors
- Message formatting options
- Notification settings
- Auto-completion behavior

## Themes

The default theme is configured in `config.toml` with support for:

- Custom foreground/background colors
- Text attributes (bold, italic, underline, etc.)
- Border styles (round, thick, double)
- Component-specific styling

## Troubleshooting

### Images not displaying

- Ensure you're using Kitty terminal or another terminal with graphics protocol support
- Check that textual-image is installed: `pip install textual-image`

### Token authentication failing

- Verify token is valid by checking Discord login
- Clear keyring and re-add token: `keyring delete discordo token`
- Try explicitly passing token: `discord --token YOUR_TOKEN`

### Missing dependencies

Install all dependencies:
```bash
pip install -r requirements.txt
```

## Architecture

### Directory Structure

```
discordo/
├── cmd/                    # Command-line and main application
│   ├── cmd.py             # Entry point and argument parsing
│   ├── application.py      # Main TUI application
│   ├── state.py           # Discord state management
│   ├── guilds_tree.py     # Guild/channel navigation
│   ├── messages_list.py   # Message display
│   └── message_input.py   # Message composition
├── internal/              # Internal utilities
│   ├── config.py          # Configuration management
│   ├── consts.py          # Constants
│   ├── logger.py          # Logging setup
│   ├── keys.py            # Keybindings
│   ├── theme.py           # Theme configuration
│   ├── http_client.py     # HTTP client
│   └── http_headers.py    # HTTP headers and properties
└── main.py               # Application entry point
```

### Key Components

- **Application**: Main TUI application managing focus and layout
- **DiscordState**: Manages Discord API connection and event handling
- **GuildsTree**: Tree widget for navigating guilds and channels
- **MessagesList**: Rich text widget for displaying messages
- **MessageInput**: Text area for composing messages

## Development

### Setting up development environment

```bash
pip install -e ".[dev]"
```

### Running tests

```bash
pytest
```

### Code formatting

```bash
black discordo/
ruff check --fix discordo/
isort discordo/
```

### Type checking

```bash
mypy discordo/
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [discord.py](https://github.com/Rapptz/discord.py) - Discord API library
- [Textual](https://github.com/Textualize/textual) - TUI framework
- [Rich](https://github.com/Textualize/rich) - Terminal formatting
- [textual-image](https://github.com/lnqs/textual-image) - Image rendering for Textual

## Legal Notice

This is an unofficial Discord client. Use at your own risk. Discord's Terms of Service prohibit self-bots and automated accounts. Use this responsibly.
