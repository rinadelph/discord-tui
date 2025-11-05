#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/alejandro/discordo-python')

# Quick syntax and import test
try:
    from discordo.cmd.application import DiscordoApp, MessagesPanel, CollapsibleOptionList
    from discordo.internal.config import Config
    print("✓ All imports successful")
    print("✓ DiscordoApp loaded")
    print("✓ MessagesPanel loaded")
    print("✓ CollapsibleOptionList loaded")
except Exception as e:
    print(f"✗ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test MessagesPanel
try:
    messages = [
        {
            'timestamp': '2025-11-05 00:22:32',
            'author': {'global_name': 'TestUser', 'username': 'testuser'},
            'content': 'Hello world!',
            'embeds': [],
            'attachments': [],
            'reactions': []
        }
    ]
    channel = {'id': '123456', 'display_name': 'test-channel', 'name': 'test-channel'}
    
    print("\n✓ Test data created")
    print(f"  - Message: {messages[0]['author']['global_name']}: {messages[0]['content']}")
    print(f"  - Channel: {channel['display_name']}")
    
except Exception as e:
    print(f"✗ Test error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*80)
print("READY TO TEST:")
print("="*80)
print("""
Run the app with:
  cd /home/alejandro/discordo-python
  uv run -m discordo.cmd.cmd

Expected behavior:
1. App starts with guild list on left
2. Select a channel with arrow keys + Enter
3. Messages should load in center panel
4. Each message shows: [timestamp] author: content
""")
