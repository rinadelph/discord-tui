"""Login form for Discordo."""

import asyncio
import logging
from typing import Callable, Optional

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Input, Button, Label
from textual.binding import Binding
from rich.console import Console
from rich.text import Text
import keyring

from discordo.internal.consts import DISCORDO_NAME

logger = logging.getLogger(__name__)


class LoginScreen(Container):
    """
    Login screen for Discord authentication.
    
    Allows user to enter their Discord token for the first time.
    """
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("enter", "login", "Login"),
    ]
    
    CSS = """
    LoginScreen {
        align: center middle;
        background: $surface;
    }
    
    #login-container {
        width: 50;
        height: 20;
        border: solid $accent;
        background: $boost;
    }
    
    #login-title {
        text-align: center;
        margin-bottom: 1;
    }
    
    #token-label {
        margin-top: 1;
    }
    
    #token-input {
        margin-bottom: 1;
        width: 100%;
    }
    
    #button-container {
        margin-top: 1;
        height: auto;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    def __init__(
        self,
        on_login: Optional[Callable[[str], None]] = None,
        *args,
        **kwargs
    ):
        """
        Initialize the login screen.
        
        Args:
            on_login: Callback when login is successful
        """
        super().__init__(*args, **kwargs)
        self.on_login = on_login
        self.token_input: Optional[Input] = None
    
    def compose(self) -> ComposeResult:
        """Compose the login screen."""
        with Vertical(id="login-container"):
            yield Label("🔐 Discordo - Discord TUI Client", id="login-title")
            yield Label("Enter your Discord user token to login:", id="token-label")
            yield Input(
                placeholder="Paste your token here...",
                password=True,
                id="token-input"
            )
            yield Label(
                "Your token is stored securely in your system keyring.",
                id="token-info"
            )
            with Horizontal(id="button-container"):
                yield Button("Login", id="login-btn", variant="primary")
                yield Button("Quit", id="quit-btn")
    
    def on_mount(self) -> None:
        """Handle mount."""
        self.token_input = self.query_one("#token-input", Input)
        self.token_input.focus()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "login-btn":
            asyncio.create_task(self.perform_login())
        elif event.button.id == "quit-btn":
            self.app.exit()
    
    async def perform_login(self) -> None:
        """Perform login with the entered token."""
        if not self.token_input:
            return
        
        token = self.token_input.value.strip()
        
        if not token:
            self.token_input.styles.border = ("solid", "red")
            return
        
        # Store token in keyring
        try:
            keyring.set_password(DISCORDO_NAME, 'token', token)
            logger.info("Token stored in keyring")
        except Exception as err:
            logger.error(f"Failed to store token: {err}")
            self.token_input.styles.border = ("solid", "red")
            return
        
        # Call callback
        if self.on_login:
            self.on_login(token)
