from datetime import datetime
from merchant_tycoon.config import SETTINGS
from typing import List, Dict

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Static, Label
from rich.text import Text


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
            body = e.get("text", "")
            render = Text()
            if ts:
                try:
                    dt = datetime.fromisoformat(ts)
                    date_str = dt.date().isoformat()
                    time_str = dt.strftime('%H:%M:%S')
                    render.append("→ ", style="white")
                    render.append(f"[{date_str}: {time_str}]", style="white")
                    render.append(" → ", style="white")
                except Exception:
                    # Fallback formatting
                    if len(ts) >= 19 and ts[10] in ("T", " "):
                        render.append("→ ", style="white")
                        render.append(f"[{ts[:10]}: {ts[11:19]}]", style="white")
                        render.append(" → ", style="white")
                    else:
                        render.append(f"[{ts}] ", style="white")
            # Message body in slightly dimmer color
            render.append(body, style="#c2c9d6")
            container.mount(Label(render))
        # Ensure view is scrolled to the end (newest entries are last)
        try:
            container.scroll_end(animate=False)
        except Exception:
            pass
