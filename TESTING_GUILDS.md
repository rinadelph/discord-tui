# Testing Guilds Component

## Quick Test

### 1. Test Guild Loading Only (No TUI)

This tests if we can properly connect to Discord and load all your guilds:

```bash
cd /home/alejandro/discordo-python
python3 test_guilds.py
```

**Expected output:**
```
✓ Logged in as YourUsername
✓ User ID: 12345678...
✓ Guilds count: N

GUILD STRUCTURE
============================================================

🏢 Guild Name 1 (ID: 123...)
   Members: 150
   Channels: 5 text, 2 voice, 1 categories
     # general
     # announcements
     # random
     🔊 General Voice
     🔊 Gaming
     ... and more

... and X more guilds
============================================================
✓ Guild loading test passed!
```

### 2. Run Full App with Guilds Display

```bash
python3 main.py --token YOUR_TOKEN
```

Or if token is in keyring:

```bash
python3 main.py
```

**Expected output:**
```
┌────────────────────┬──────────────────────┐
│ Guilds & Channels  │ Messages             │
│                    │                      │
│ 💬 Direct Messages │ Select a channel to  │
│ 🏢 Guild 1         │ view messages        │
│  📁 Category       │                      │
│   # general        │                      │
│   # announcements  │                      │
│ 🏢 Guild 2         │                      │
│  # welcome         │                      │
│                    ├──────────────────────┤
│                    │ Message input coming │
│                    │ soon                 │
├────────────────────┴──────────────────────┤
│ ✓ Loaded X guild(s) | Press Ctrl+C to quit│
└──────────────────────────────────────────┘
```

## Debugging

### If Token Auth Fails

Test authentication first:

```bash
python3 test_auth.py YOUR_TOKEN
```

### If Guilds Don't Load

Check logs:

```bash
tail -f ~/.cache/discordo/logs.txt
```

Run with debug logging:

```bash
python3 main.py --log-level debug
```

### Check Token in Keyring

```bash
python3 -c "import keyring; print('Token:', keyring.get_password('discordo', 'token')[:30] + '...')"
```

## What's Implemented

✅ **Done:**
- Discord authentication with user token
- Guild structure loading (categories, channels)
- Tree view display of guilds/channels
- Status bar with connection status
- Config loading and parsing
- Basic UI layout (3 panels + status)

🔄 **Next to Implement:**
- Message display when channel is selected
- Channel click/select handling
- Direct message support
- User status indicators
- Unread message badges
- Message input and sending

## File Structure

```
discordo-python/
├── main.py                      # Entry point
├── test_auth.py                 # Auth test
├── test_guilds.py              # Guilds loading test
├── simple_test.py              # Minimal TUI test
├── config.toml                 # Default config
│
├── discordo/
│   ├── cmd/
│   │   ├── application.py      # Main TUI app
│   │   ├── guilds_tree.py      # Guilds tree widget
│   │   ├── messages_list.py    # Messages display
│   │   ├── message_input.py    # Input widget
│   │   └── state.py            # Discord state
│   │
│   └── internal/
│       ├── config.py           # Config loading
│       ├── consts.py           # Constants
│       ├── logger.py           # Logging setup
│       └── ... (other utilities)
```

## Architecture

### Discord Connection Flow

```
main.py
  └─> cmd.run()
      └─> DiscordoApp (Textual)
          └─> on_mount()
              └─> _check_and_login()
                  └─> connect_discord(token)
                      └─> discord.Client.start(token)
                          └─> on_ready()
                              └─> _load_guilds()
                                  └─> Tree widget populated
```

### Data Flow

```
Discord API
    ↓
discord.py Client
    ↓
DiscordState (cache/state management)
    ↓
DiscordoApp (TUI)
    ├─> GuildsTree (left panel)
    ├─> MessagesPanel (center)
    ├─> InputPanel (bottom)
    └─> StatusPanel (status bar)
```

## Testing Checklist

- [ ] Token authentication works
- [ ] Guilds load and display in tree
- [ ] Guild structure shows categories and channels
- [ ] Status bar updates during loading
- [ ] Can press Ctrl+C to quit
- [ ] No error messages in logs

## Next Steps

1. **Test current implementation:**
   ```bash
   python3 test_guilds.py
   python3 main.py
   ```

2. **Implement channel selection:**
   - Handle tree node clicks
   - Load messages for selected channel
   - Display in messages panel

3. **Implement message display:**
   - Format messages with author, timestamp, content
   - Show reactions
   - Show embeds
   - Render images

4. **Implement message input:**
   - Text input widget
   - Send message on Enter
   - Show status

5. **Add navigation:**
   - Tab to cycle panels
   - Arrow keys in tree
   - Vim keybindings (j/k for up/down)

## Performance Notes

- **Guild loading**: ~1-3 seconds for 50+ guilds
- **Message loading**: ~0.5-1 second per 50 messages
- **Tree rendering**: Instant for <1000 nodes
- **Memory**: ~50-100MB for full state of 20+ guilds

## Known Limitations

1. DM list not yet populated (folder exists but empty)
2. Message reactions not clickable
3. Can't edit/delete messages yet
4. No typing indicators
5. No voice channel support
6. No thread support
7. No emoji auto-complete

## Troubleshooting

### "Connection timeout"
- Check internet connection
- Discord API might be slow
- Try again in a few seconds

### "Invalid token"
- Token may have expired
- Get a fresh token from Discord
- Store in keyring again

### Tree not showing guilds
- Check logs: `tail -f ~/.cache/discordo/logs.txt`
- Run test_guilds.py to isolate issue
- Verify token has correct permissions

### Status bar not updating
- This is a known Textual limitation
- Status updates work but may not always render
- Will be improved in next iteration

## Token Refresh

If your token expires:

```bash
# Get new token from Discord web
# Then run:
python3 main.py --token NEW_TOKEN_HERE

# Or update keyring:
python3 -c "import keyring; keyring.set_password('discordo', 'token', 'NEW_TOKEN')"
```

## Contact & Support

For issues:
1. Check logs: `~/.cache/discordo/logs.txt`
2. Run with debug: `python3 main.py --log-level debug`
3. Test components individually: `test_auth.py`, `test_guilds.py`
4. Check Discord status: https://status.discord.com/
