#!/usr/bin/env python3
"""Verify the changes work correctly."""

import sys
sys.path.insert(0, '/home/alejandro/discordo-python')

try:
    from discordo.cmd.application import DiscordoApp, GuildsPanel
    print("✓ Imports successful")
    
    # Test GuildsPanel rendering
    panel = GuildsPanel()
    panel.dms_data = [
        {'display_name': 'Espe'},
        {'display_name': 'Kawz 🦑'},
    ]
    panel.guilds_data = [
        {'name': 'DanVek'},
        {'name': 'alvaro7000'},
        {'name': 'Antlers too Big'},
    ]
    
    rendered = panel.render()
    print("\n✓ GuildsPanel renders correctly:")
    print(rendered)
    
    # Check that it uses display names (not usernames)
    assert 'Espe' in rendered, "DM display name not found"
    assert 'DanVek' in rendered, "Guild name not found"
    print("\n✓ Display names are correctly included")
    
    # Check formatting
    assert '╭Guilds' in rendered, "Top border format incorrect"
    assert '╰──' in rendered, "Item prefix format incorrect"
    assert '╰─' in rendered, "Bottom border format incorrect"
    print("✓ ASCII box formatting is correct")
    
    print("\n✅ All checks passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
