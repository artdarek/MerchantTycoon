from datetime import datetime
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Static, Label
from rich.text import Text
from merchant_tycoon.engine.applets.whatsup_applet import WhatsUpApplet


class WhatsUpPanel(Static):
    """Displays messenger logs similarly to the Newspaper modal style."""

    def compose(self) -> ComposeResult:
        # Title with icon and full-height scrollable list (like Newspaper)
        yield Label("📨 WHATSUP", classes="panel-title")
        yield ScrollableContainer(id="whatsup-content")

    def on_mount(self) -> None:
        # Populate after mount to ensure children exist
        self.refresh_messages()

    def refresh_messages(self) -> None:
        try:
            container = self.query_one("#whatsup-content", ScrollableContainer)
        except Exception:
            return

        try:
            container.remove_children()
        except Exception:
            pass

        try:
            svc: WhatsUpApplet | None = getattr(self.app.engine, 'whatsup_applet', None)
            entries = list(svc.get_entries()) if svc else []
        except Exception:
            entries = []

        if not entries:
            container.mount(Label("No messages to display.", classes="no-messages"))
            return

        current_date = None
        for e in entries:
            ts = e.get("ts", "")
            body = e.get("text", "")
            level = str(e.get("level", "info")).lower()

            if ts:
                try:
                    dt = datetime.fromisoformat(ts)
                    msg_date = dt.date().isoformat()
                    if msg_date != current_date:
                        current_date = msg_date
                        separator = Text()
                        separator.append(f"\n── {msg_date} ──", style="bold #9aa3b2")
                        container.mount(Label(separator, classes="date-separator"))
                except Exception:
                    pass

            if level == "error":
                dot_color = "#d16a66"
            elif level in ("warn", "warning"):
                dot_color = "#e0b15a"
            elif level == "debug":
                dot_color = "#8a91a7"
            else:
                dot_color = "#4ea59a"

            render = Text()
            if ts:
                try:
                    dt = datetime.fromisoformat(ts)
                    date_str = dt.date().isoformat()
                    time_str = dt.strftime('%H:%M:%S')
                    render.append("→ ", style="white")
                    render.append(f"[{date_str}: {time_str}]", style="white")
                    render.append(" ●", style=dot_color)
                    render.append(" → ", style="white")
                except Exception:
                    if len(ts) >= 19 and ts[10] in ("T", " "):
                        render.append("→ ", style="white")
                        render.append(f"[{ts[:10]}: {ts[11:19]}]", style="white")
                        render.append(" ●", style=dot_color)
                        render.append(" → ", style="white")
                    else:
                        render.append(f"[{ts}]", style="white")
                        render.append(" ● ", style=dot_color)
            render.append(body, style="#c2c9d6")
            container.mount(Label(render, classes="newspaper-message"))

        try:
            container.scroll_end(animate=False)
        except Exception:
            pass
