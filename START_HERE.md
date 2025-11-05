# Starting Discordo Python

## Quick Start

### 1. Test if Textual renders at all:

```bash
cd /home/alejandro/discordo-python
python3 simple_test.py
```

This is a minimal Textual app. If you see anything, Textual is working.

### 2. Run the full app:

```bash
# Method 1: Direct with uv (recommended)
uv run -m discordo.cmd.cmd --token YOUR_TOKEN_HERE

# Method 2: Direct with python
PYTHONPATH=/home/alejandro/discordo-python:$PYTHONPATH python3 main.py --token YOUR_TOKEN_HERE

# Method 3: Using the run script
./run.sh --token YOUR_TOKEN_HERE
```

### 3. In TMux for debugging:

```bash
tmux new-session -s discordo

# Inside tmux:
cd /home/alejandro/discordo-python

# Test simple app first
python3 simple_test.py

# Exit (Ctrl+C) and try the full app
python3 main.py --token YOUR_TOKEN_HERE
```

## Expected Output

When you run the app, you should see:

```
┌─ Guilds ─────┬─ Messages ───────┐
│              │                  │
│ Loading...   │ Waiting for...   │
│              │                  │
├──────────────┼──────────────────┤
│                                 │
│ Type your message here...       │
│                                 │
└─────────────────────────────────┘
[Ready] | Press Ctrl+C to quit
```

## Troubleshooting

### Blank screen / Nothing rendering

1. **Check terminal support:**
   ```bash
   echo $TERM
   # Should output: xterm-kitty or similar
   ```

2. **Test Textual directly:**
   ```bash
   python3 simple_test.py
   ```

3. **Check Python version:**
   ```bash
   python3 --version
   # Should be 3.10+
   ```

4. **Run with debug logging:**
   ```bash
   PYTHONPATH=/home/alejandro/discordo-python:$PYTHONPATH python3 main.py --log-level debug --token YOUR_TOKEN
   ```

### Token not working

1. **Verify token is valid:**
   ```bash
   PYTHONPATH=/home/alejandro/discordo-python:$PYTHONPATH python3 test_auth.py YOUR_TOKEN
   ```

2. **Check keyring:**
   ```bash
   python3 -c "import keyring; print(keyring.get_password('discordo', 'token')[:20] + '...')"
   ```

### Import errors

```bash
# Make sure all dependencies are installed
pip install discord.py textual rich keyring

# Check versions
pip list | grep -E "(discord|textual|rich|keyring)"
```

## What to Look For

After running the app:

1. ✓ Should see 3 panels (Guilds, Messages, Input)
2. ✓ Should see status bar at bottom
3. ✓ Should be able to press Ctrl+C to quit
4. ✓ Status should change when connecting to Discord

## Next Steps

Once the UI renders:
1. Implement guild/channel loading
2. Add message display
3. Add message input
4. Add navigation between panels
5. Add image rendering with textual-image

## Development Tips

- Run with `--log-level debug` to see what's happening
- Check `~/.cache/discordo/logs.txt` for detailed logs
- Use tmux to see both logs and app at same time
- Press Ctrl+C to exit at any time

## File Structure

```
discordo-python/
├── main.py                 # Entry point
├── simple_test.py         # Minimal test app
├── quick_test.py          # Quick test with config
├── test_auth.py           # Token auth test
├── config.toml            # Default config
├── requirements.txt       # Dependencies
└── discordo/
    ├── cmd/
    │   ├── cmd.py         # CLI entry
    │   ├── application.py  # Main app
    │   └── ...
    └── internal/
        ├── config.py
        ├── consts.py
        └── ...
```

## Token Information

To get your Discord token, visit https://discord.com/developers/applications

Use it like:
```bash
python3 main.py --token YOUR_DISCORD_TOKEN_HERE
```

Or store it in keyring:
```bash
python3 -c "import keyring; keyring.set_password('discordo', 'token', 'YOUR_DISCORD_TOKEN_HERE')"
```

Then just run:
```bash
python3 main.py
```
