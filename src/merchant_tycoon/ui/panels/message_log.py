from datetime import datetime
from typing import List

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Static, Label


class MessageLog(Static):
    """Display game messages"""

    def __init__(self):
        super().__init__()
        # Start with a welcome message tagged with time and the starting day
        ts = datetime.now().strftime("%H:%M:%S")
        self.messages: List[str] = [f"[{ts}] Day 1: Welcome to Merchant Tycoon!"]

    def compose(self) -> ComposeResult:
        yield Label("📜 MESSAGES", id="log-header", classes="panel-title")
        yield ScrollableContainer(id="log-content")

    def add_message(self, msg: str):
        self.messages.insert(0, msg)  # Add new messages at the beginning
        if len(self.messages) > 10:
            self.messages = self.messages[:10]  # Keep first 10 (newest)
        self._update_display()

    def set_messages(self, messages: List[str]):
        """Replace the log with provided messages (newest first)."""
        self.messages = list(messages[:10]) if messages else []
        self._update_display()

    def reset_messages(self):
        """Reset messages to the default welcome line for Day 1."""
        ts = datetime.now().strftime("%H:%M:%S")
        self.messages = [f"[{ts}] Day 1: Welcome to Merchant Tycoon!"]
        self._update_display()

    def _update_display(self):
        container = self.query_one("#log-content", ScrollableContainer)
        container.remove_children()
        for msg in self.messages:
            container.mount(Label(msg))
