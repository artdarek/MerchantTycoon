from datetime import datetime
from merchant_tycoon.config import SETTINGS
from typing import List, Dict

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Static, Label


class MessangerPanel(Static):
    """Read-only view over MessengerService entries."""

    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label("📜 MESSAGES", id="log-header", classes="panel-title")
        yield ScrollableContainer(id="log-content")

    def on_mount(self) -> None:
        # Initial render after container exists
        self.render_messages()

    def render_messages(self) -> None:
        try:
            container = self.query_one("#log-content", ScrollableContainer)
        except Exception:
            return
        try:
            container.remove_children()
        except Exception:
            pass
        # Get entries from messenger; render oldest first so newest at bottom
        try:
            entries = self.app.engine.messenger.get_entries()
        except Exception:
            entries = []
        for e in entries:
            ts = e.get("ts", "")
            text = e.get("text", "")
            display = text
            if ts:
                try:
                    dt = datetime.fromisoformat(ts)
                    display = f"[{dt.date().isoformat()}: {dt.strftime('%H:%M:%S')}] {text}"
                except Exception:
                    # Fallback: attempt simple slicing if ISO-like
                    if len(ts) >= 19 and ts[10] in ("T", " "):
                        display = f"[{ts[:10]}: {ts[11:19]}] {text}"
                    else:
                        display = f"[{ts}] {text}"
            container.mount(Label(display))
        # Ensure view is scrolled to the end (newest entries are last)
        try:
            container.scroll_end(animate=False)
        except Exception:
            pass
