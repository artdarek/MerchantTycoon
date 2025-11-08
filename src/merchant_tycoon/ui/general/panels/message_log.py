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
        # messages: newest-first list of entries {ts, text}
        self.messages: List[Dict[str, str]] = [
            {"ts": f"{start_date}T{start_time}", "text": "Welcome to Merchant Tycoon!"}
        ]

    def compose(self) -> ComposeResult:
        yield Label("📜 MESSAGES", id="log-header", classes="panel-title")
        yield ScrollableContainer(id="log-content")

    def on_mount(self) -> None:
        # Ensure initial render happens after the container exists
        try:
            self._update_display()
        except Exception:
            pass

    def add_entry(self, ts_iso: str, text: str):
        self.messages.insert(0, {"ts": str(ts_iso), "text": str(text)})
        limit = int(getattr(SETTINGS.saveui, "messages_save_limit", 10))
        if len(self.messages) > limit:
            self.messages = self.messages[:limit]
        self._update_display()

    def set_messages(self, messages: List[Dict[str, str]]):
        """Replace the log with provided messages (newest first).
        Expects list of dict entries: {"ts": ISO datetime, "text": str}.
        """
        limit = int(getattr(SETTINGS.saveui, "messages_save_limit", 10))
        self.messages = [
            {"ts": str(m.get("ts", "")), "text": str(m.get("text", ""))}
            for m in (messages or [])
        ][:limit]
        self._update_display()

    def reset_messages(self):
        """Reset messages to the default welcome line for start date."""
        start_date = getattr(SETTINGS.game, "start_date", "2025-01-01")
        start_time = datetime.now().strftime("%H:%M:%S")
        self.messages = [{"ts": f"{start_date}T{start_time}", "text": "Welcome to Merchant Tycoon!"}]
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
        # Render oldest first so newest is at the bottom
        for e in reversed(self.messages):
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
