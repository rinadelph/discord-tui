#!/usr/bin/env python3
"""Simple Textual app test."""

from textual.app import ComposeResult, App
from textual.widgets import Static, Label
from rich.panel import Panel

class SimpleApp(App):
    """A simple test app."""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    Label {
        border: solid green;
        width: 100%;
        height: 100%;
        content-align: center middle;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Label("[bold cyan]Discordo v0.1.0[/bold cyan]\n\nSimple Test App\n\nPress Ctrl+C to quit", id="main")

if __name__ == "__main__":
    app = SimpleApp()
    app.run()
