# Discordo Python - Setup Guide

This guide will help you set up and run the Python version of Discordo.

## Prerequisites

- **Python 3.10+** (3.11+ recommended)
- **pip** (Python package manager)
- **Kitty Terminal** (or any terminal with modern graphics protocol support)
- **Discord Account** with a valid user token

## Installation Steps

### 1. Clone and Navigate

```bash
cd /home/alejandro/discordo-python
```

### 2. Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or for development with additional tools:

```bash
pip install -e ".[dev]"
```

### 4. Get Your Discord Token

**⚠️ WARNING:** Never share your Discord token publicly. It gives full access to your account.

#### Option A: From Web Browser
1. Open Discord in your web browser (discord.com)
2. Press F12 to open Developer Tools
3. Go to **Application** tab
4. In left sidebar, click **Cookies** → **discord.com**
5. Find `__Secure-LATEST_USER_TOKEN` cookie
6. Copy the token value

#### Option B: Using the CLI
```bash
# First run with token flag (will be saved to keyring automatically)
python main.py --token YOUR_TOKEN_HERE

# Or run in interactive mode (will prompt for token on first run)
python main.py
```

### 5. Running Discordo

#### First Time (with token)
```bash
python main.py --token YOUR_DISCORD_TOKEN
```

The token will be saved securely in your system keyring.

#### Subsequent Runs (token retrieved from keyring)
```bash
python main.py
```

#### With Custom Configuration Path
```bash
python main.py --config-path ~/.config/discordo/config.toml
```

#### With Debug Logging
```bash
python main.py --log-level debug
```

## System Keyring Setup

Discordo uses your system's secure credential storage:

- **Linux**: Uses `secretservice` (via dbus) or `pass` password manager
- **macOS**: Uses Keychain
- **Windows**: Uses Windows Credential Manager

### Verifying Keyring Access

```bash
python -c "import keyring; print(keyring.get_keyring())"
```

This should print your system's keyring backend.

## Initial Configuration

On first run, Discordo creates a configuration file at:
```
~/.config/discordo/config.toml
```

### Editing Configuration

Edit the config file to customize:
- **Keybindings** - Vim-style navigation keys
- **Theme** - Colors and styling
- **Notifications** - Sound and desktop notifications
- **Behavior** - Markdown rendering, auto-complete, etc.

See `README.md` for available options.

## Directory Structure

After setup, you'll have:

```
~/.cache/discordo/
├── logs.txt              # Application logs
├── avatars/              # Cached user avatars
└── attachments/          # Downloaded attachments

~/.config/discordo/
└── config.toml           # Your configuration
```

## Troubleshooting

### Issue: "No module named 'discord'"

**Solution**: Make sure dependencies are installed
```bash
pip install -r requirements.txt
```

### Issue: Keyring not working

**Solution**: Install backend for your system
```bash
# Linux
sudo apt-get install python3-secretservice

# macOS (usually built-in, but try)
pip install keyring

# Windows
pip install keyring windows-curses
```

### Issue: Textual not rendering properly

**Solution**: Update Textual
```bash
pip install --upgrade textual
```

### Issue: Discord connection fails

**Possible causes:**
1. Token is invalid or expired
2. Network connectivity issue
3. Discord API is down

**Solution:**
- Verify token is correct
- Check internet connection
- Try again later
- Check Discord status page

### Issue: Images not displaying

**Solution:**
1. Ensure you're using Kitty terminal (or compatible)
2. Check textual-image is installed: `pip show textual-image`
3. Verify terminal supports graphics protocol
4. Try updating: `pip install --upgrade textual-image`

## Development Setup

### Install Dev Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Quality

Format code:
```bash
black discordo/
isort discordo/
```

Check code:
```bash
ruff check discordo/
mypy discordo/
```

## Performance Tips

- Use a modern terminal emulator (Kitty, WezTerm, iTerm2)
- Reduce notification frequency in config.toml
- Disable markdown rendering if experiencing lag: `markdown = false`
- Limit message history: `messages_limit = 30` (default is 50)

## Getting Help

- Check logs at `~/.cache/discordo/logs.txt`
- Enable debug logging: `--log-level debug`
- Review README.md for features and keybindings
- Check PROJECT_STRUCTURE.md for architecture details

## Next Steps After Installation

1. **Explore the Interface**
   - Use Tab/Shift+Tab to navigate between panels
   - Use vim-style keys (j/k) to move around
   - Press Ctrl+H for help (when implemented)

2. **Customize Configuration**
   - Edit `~/.config/discordo/config.toml`
   - Adjust keybindings to your preference
   - Set theme colors you like

3. **Set Notifications** (Optional)
   - Enable desktop notifications in config
   - Configure sound alerts

## Uninstalling

To remove Discordo:

```bash
# Remove package
pip uninstall discordo

# Remove configuration
rm -rf ~/.config/discordo/

# Remove cache
rm -rf ~/.cache/discordo/

# Remove token from keyring
keyring delete discordo token
```

## Important Notes

⚠️ **Security & Legality:**
- This is an unofficial Discord client
- Using self-bots may violate Discord's Terms of Service
- Use responsibly and at your own risk
- Never share your token with anyone
- Discord can disable your account for using unauthorized clients

✅ **What's Safe:**
- Reading messages
- Viewing your servers and DMs
- Standard user interactions
- Using a personal token for your own account

## Support

For issues specific to the Python implementation:
1. Check the logs: `~/.cache/discordo/logs.txt`
2. Run with debug logging: `--log-level debug`
3. Review source code in `discordo/` directory
4. Check GitHub issues (if available)

For Discord API issues:
- See Discord Developer Documentation: https://discord.com/developers/docs
- Check discord.py documentation: https://discordpy.readthedocs.io

## Next Phase Development

The following features are planned:
- [ ] Full message rendering with Rich formatting
- [ ] Image display with textual-image integration
- [ ] Guild member list view
- [ ] Message search functionality
- [ ] Message threading support
- [ ] Voice channel display
- [ ] Typing indicators
- [ ] Presence synchronization
- [ ] Better error recovery
- [ ] Unit and integration tests

See PROJECT_STRUCTURE.md for architecture details.
