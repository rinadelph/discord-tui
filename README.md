# Discord TUI

A lightweight, keyboard-driven Discord client for the terminal with message sending, guild navigation, and comprehensive logging.

## Features

- **TUI Interface** - Full terminal user interface using Textual
- **Send Messages** - Compose and send messages to Discord channels
- **Guild Navigation** - Browse servers and channels
- **Message History** - View and scroll through message history
- **Comprehensive Logging** - Detailed debug logs for troubleshooting
- **Secure Auth** - Token stored securely in system keyring

## Requirements

- Python 3.10+
- Discord account with valid token
- System keyring support

## Quick Start

```bash
# Clone repository
git clone https://github.com/rinadelph/discord-tui.git
cd discord-tui

# Install dependencies
uv install  # or: pip install -r requirements.txt

# Run with token
uv run -m discordo.cmd.cmd --token YOUR_DISCORD_TOKEN

# Or store token in keyring first
python -c "import keyring; keyring.set_password('DiscordoApp', 'token', 'YOUR_TOKEN')"
uv run -m discordo.cmd.cmd
```

## Usage

### Navigation
- **↑/↓** - Navigate guilds/channels/messages
- **Enter** - Select/expand guild or load channel
- **Ctrl+C** - Quit

### Message Input
- **Click input field** or **Tab** to focus
- **Type message** and **press Enter** to send
- Message appears at bottom of chat

## Getting Your Token

1. Open Discord app (or web version at discord.com)
2. Press **F12** to open Developer Tools
3. Go to **Application** tab
4. Expand **Local Storage** in left sidebar
5. Select **https://discord.com**
6. Search (Ctrl+F) for **token** in the values
7. Copy the token value (long string starting with your user ID)
8. **Never share this token!** - It gives full access to your account

## Logs

Detailed logs are written to `~/.cache/discordo/logs.txt` for debugging message sending and other issues.

View logs in real-time:
```bash
tail -f ~/.cache/discordo/logs.txt
```

## Troubleshooting

### Messages not sending
- Check `~/.cache/discordo/logs.txt` for error details
- Verify token is valid
- Ensure channel is selected
- Check Discord permissions for the channel

### Token issues
- Verify token format (should be long string)
- Check token hasn't expired
- Re-add token to keyring if needed

## Project Structure

```
discordo/
├── cmd/
│   ├── application.py      # Main TUI app, message sending
│   ├── cmd.py             # Entry point
│   └── ...
├── internal/
│   ├── logger.py          # Logging setup
│   ├── gateway.py         # Discord connection
│   ├── database.py        # Message caching
│   └── ...
└── main.py               # App launcher
```

## Contributing

Feel free to fork and submit pull requests!

## License

MIT License
