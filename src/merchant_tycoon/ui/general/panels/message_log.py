from datetime import datetime
from merchant_tycoon.config import SETTINGS
from typing import List, Dict

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Static, Label


class MessageLog(Static):
    """Display game messages"""

    def __init__(self):
        super().__init__()
        # Start with a welcome message using game date and current system time
        start_date = getattr(SETTINGS.game, "start_date", "2025-01-01")
        start_time = datetime.now().strftime("%H:%M:%S")
        # No local buffer; messenger service holds the source of truth
        self.messages: List[Dict[str, str]] = []

    def compose(self) -> ComposeResult:
        yield Label("📜 MESSAGES", id="log-header", classes="panel-title")
        yield ScrollableContainer(id="log-content")

    def on_mount(self) -> None:
        # Ensure initial render happens after the container exists
        try:
            # If there are no messages yet (fresh game), add a welcome line
            try:
                entries = self.app.engine.messenger.get_entries()
            except Exception:
                entries = []
            if not entries:
                start_date = getattr(SETTINGS.game, "start_date", "2025-01-01")
                start_time = datetime.now().strftime("%H:%M:%S")
                self.app.engine.messenger.set_entries([
                    {"ts": f"{start_date}T{start_time}", "text": "Welcome to Merchant Tycoon!", "level": "info", "tag": "system", "ctx": {}}
                ])
            self._update_display()
        except Exception:
            pass

    def add_entry(self, ts_iso: str, text: str):
        # Delegate to messenger if available, then refresh UI
        try:
            self.app.engine.messenger.info(text)
        except Exception:
            pass
        self._update_display()

    def set_messages(self, messages: List[Dict[str, str]]):
        """Replace the log with provided messages (newest first).
        Expects list of dict entries: {"ts": ISO datetime, "text": str}.
        """
        # Set directly via messenger service, then refresh
        try:
            self.app.engine.messenger.set_entries(messages or [])
        except Exception:
            pass
        self._update_display()

    def reset_messages(self):
        """Reset messages to the default welcome line for start date."""
        start_date = getattr(SETTINGS.game, "start_date", "2025-01-01")
        start_time = datetime.now().strftime("%H:%M:%S")
        try:
            self.app.engine.messenger.set_entries([
                {"ts": f"{start_date}T{start_time}", "text": "Welcome to Merchant Tycoon!"}
            ])
        except Exception:
            pass
        self._update_display()

    def _update_display(self):
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
