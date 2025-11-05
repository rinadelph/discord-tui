#!/usr/bin/env python3
"""Final comprehensive test before running the app."""

import sys
sys.path.insert(0, '/home/alejandro/discordo-python')

from discordo.cmd.application import CollapsibleOptionList, MessagesPanel, MessageItemWidget, parse_content_with_links
from textual.widgets import ListItem

def test_listview_insert_fix():
    """Verify that the ListView.insert() fix code is correct."""
    # The fix changed the code from:
    #   for i, item in enumerate(new_items):
    #       self.messages_list.insert(i, item)
    # To:
    #   if new_items:
    #       self.messages_list.insert(0, new_items)

    # Verify the signature is correct by checking the application source
    import inspect
    from discordo.cmd.application import MessagesPanel

    source = inspect.getsource(MessagesPanel.display_messages)

    # Check that the old problematic loop is NOT present
    assert 'for i, item in enumerate(new_items):' not in source, "Old problematic loop still present"

    # Check that the new correct code IS present
    assert 'self.messages_list.insert(0, new_items)' in source, "New fix code not found"

    print("✓ ListView.insert() fix is correctly implemented")
    return True

def test_url_detection():
    """Test URL detection in message content."""
    test_cases = [
        ("Check https://example.com here", [("Check ", None), ("https://example.com", "https://example.com"), (" here", None)]),
        ("Visit www.google.com now", [("Visit ", None), ("www.google.com", "https://www.google.com"), (" now", None)]),
        ("No links here", [("No links here", None)]),
        ("Multiple: https://github.com/user/repo and google.com", None),  # Just check it parses
    ]

    for content, expected in test_cases:
        result = parse_content_with_links(content)
        if expected:
            assert result == expected, f"URL parsing failed for: {content}"
        assert result is not None and len(result) > 0, f"Empty result for: {content}"

    print("✓ URL detection works correctly")
    return True

def test_message_widget_grouping():
    """Test message widget with grouping."""
    msg = {
        'timestamp': '03:19:06',
        'full_timestamp': '2025-11-05T03:19:06.119000+00:00',
        'date': '2025-11-05',
        'author': {'id': '123', 'global_name': 'TestUser', 'username': 'testuser'},
        'author_color': '#5865F2',
        'content': 'Hello world!',
        'embeds': [],
        'attachments': [],
        'reactions': []
    }

    # Test non-grouped message
    widget = MessageItemWidget(msg, container_width=80, is_grouped=False)
    assert widget.is_grouped == False
    assert widget.message == msg
    print("✓ Message widget non-grouped initialization works")

    # Test grouped message
    widget_grouped = MessageItemWidget(msg, container_width=80, is_grouped=True)
    assert widget_grouped.is_grouped == True
    print("✓ Message widget grouped initialization works")

    return True

def test_collapsible_option_list_creation():
    """Test that CollapsibleOptionList can be created without errors."""
    try:
        panel = CollapsibleOptionList()
        assert panel is not None
        assert hasattr(panel, 'dms_data')
        assert hasattr(panel, 'guilds_data')
        assert hasattr(panel, 'rebuild_list')
        print("✓ CollapsibleOptionList creates successfully")
        return True
    except Exception as e:
        print(f"✗ CollapsibleOptionList creation failed: {e}")
        return False

def test_prepend_message_logic():
    """Test that the prepend message logic is fixed (no cursor index errors)."""
    # Verify the problematic code has been removed
    import inspect
    from discordo.cmd.application import MessagesPanel

    source = inspect.getsource(MessagesPanel.display_messages)

    # Check that the old problematic cursor restoration is NOT present
    # The code that was causing: "IndexError: list index out of range"
    assert 'new_index = saved_index + len(new_items)' not in source, \
        "Old cursor restoration code still present - would cause IndexError"

    # Check that we're not setting cursor index right after insert (which is async)
    lines = source.split('\n')
    for i, line in enumerate(lines):
        if 'self.messages_list.insert(0, new_items)' in line:
            # Check that the next meaningful line is NOT trying to set index
            next_lines = '\n'.join(lines[i+1:i+5])
            assert 'self.messages_list.index' not in next_lines, \
                "Still setting index immediately after async insert()"

    print("✓ Prepend message logic is fixed - no cursor index errors")
    return True

if __name__ == '__main__':
    try:
        print("Running comprehensive tests...\n")

        # Run all tests
        results = []
        results.append(test_listview_insert_fix())
        results.append(test_url_detection())
        results.append(test_message_widget_grouping())
        results.append(test_collapsible_option_list_creation())
        results.append(test_prepend_message_logic())

        if all(results):
            print("\n✅ All tests passed!\n")
            print("Application is ready to run:")
            print("  cd /home/alejandro/discordo-python")
            print("  python main.py --token YOUR_TOKEN")
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)

    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
