"""Markdown rendering for Discord messages."""

import re
from typing import List, Tuple
from rich.text import Text
from rich.console import Console


class DiscordMarkdownRenderer:
    """
    Render Discord-flavored markdown to Rich text.
    
    Supports:
    - **bold**
    - *italic* or _italic_
    - __underline__
    - ~~strikethrough~~
    - `code`
    - ```code blocks```
    - Links [text](url)
    - User mentions @user
    - Channel mentions #channel
    - Emojis
    """
    
    # Markdown patterns
    PATTERNS = {
        'bold': (r'\*\*(.+?)\*\*', 'bold'),
        'italic': (r'[*_](.+?)[*_]', 'italic'),
        'underline': (r'__(.+?)__', 'underline'),
        'strikethrough': (r'~~(.+?)~~', 'strike'),
        'code': (r'`(.+?)`', 'cyan'),
        'mention': (r'<@!?(\d+)>', 'blue'),
        'channel': (r'<#(\d+)>', 'cyan'),
        'role': (r'<@&(\d+)>', 'magenta'),
        'emoji': (r'<:(\w+):(\d+)>', 'yellow'),
        'url': (r'https?://[^\s\)]+', 'blue underline'),
    }
    
    def __init__(self):
        """Initialize the markdown renderer."""
        self.compiled_patterns = {
            name: re.compile(pattern)
            for name, (pattern, _) in self.PATTERNS.items()
        }
    
    def render(self, text: str) -> Text:
        """
        Render markdown text to Rich Text.
        
        Args:
            text: Markdown text to render
            
        Returns:
            Rich Text object with styling
        """
        # Handle code blocks first (preserve content)
        code_blocks = []
        
        # Find code blocks
        code_block_pattern = re.compile(r'```(.+?)```', re.DOTALL)
        for match in code_block_pattern.finditer(text):
            code_blocks.append((match.start(), match.end(), match.group(1)))
        
        # Process text
        result = Text()
        last_pos = 0
        in_code_block = False
        
        for start, end, code in code_blocks:
            # Add text before code block
            if start > last_pos:
                chunk = text[last_pos:start]
                result.append_text(self._render_inline(chunk))
            
            # Add code block with monospace styling
            result.append(code, style="dim cyan")
            last_pos = end
        
        # Add remaining text
        if last_pos < len(text):
            chunk = text[last_pos:]
            result.append_text(self._render_inline(chunk))
        
        return result
    
    def _render_inline(self, text: str) -> Text:
        """
        Render inline markdown elements.
        
        Args:
            text: Text to render
            
        Returns:
            Rich Text with inline styling
        """
        result = Text()
        last_pos = 0
        matches = []
        
        # Find all markdown patterns
        for name, pattern in self.compiled_patterns.items():
            for match in pattern.finditer(text):
                matches.append((match.start(), match.end(), name, match.groups()))
        
        # Sort matches by position
        matches.sort(key=lambda x: x[0])
        
        # Process matches
        for start, end, match_type, groups in matches:
            # Add text before match
            if start > last_pos:
                result.append(text[last_pos:start])
            
            # Get styling
            pattern, style = self.PATTERNS[match_type]
            
            # Add matched text with styling
            if match_type in ('mention', 'channel', 'role', 'emoji'):
                # Special handling for Discord entities
                if match_type == 'mention':
                    result.append(f"@user{groups[0]}", style=style)
                elif match_type == 'channel':
                    result.append(f"#{groups[0]}", style=style)
                elif match_type == 'role':
                    result.append(f"@role{groups[0]}", style=style)
                elif match_type == 'emoji':
                    result.append(f":{groups[0]}:", style=style)
            else:
                # Regular markdown
                content = groups[0] if groups else text[start:end]
                result.append(content, style=style)
            
            last_pos = end
        
        # Add remaining text
        if last_pos < len(text):
            result.append(text[last_pos:])
        
        return result
    
    def render_embed_field(self, name: str, value: str) -> Tuple[Text, Text]:
        """
        Render an embed field with name and value.
        
        Args:
            name: Field name
            value: Field value
            
        Returns:
            Tuple of (name_text, value_text)
        """
        name_text = Text(name, style="bold yellow")
        value_text = self.render(value)
        return name_text, value_text
    
    def render_embed_description(self, description: str) -> Text:
        """
        Render embed description.
        
        Args:
            description: The description text
            
        Returns:
            Rendered Text
        """
        return self.render(description)


# Global renderer instance
default_renderer = DiscordMarkdownRenderer()


def render(text: str) -> Text:
    """
    Render markdown text using the default renderer.
    
    Args:
        text: Markdown text
        
    Returns:
        Rich Text object
    """
    return default_renderer.render(text)


def escape_markdown(text: str) -> str:
    """
    Escape markdown special characters.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text
    """
    special_chars = ['\\', '*', '_', '`', '~', '[', ']', '(', ')', '#', '+', '-', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text
