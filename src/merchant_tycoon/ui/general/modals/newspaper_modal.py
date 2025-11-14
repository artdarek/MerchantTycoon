from datetime import datetime
from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.widgets import Label, Button
from textual.screen import ModalScreen
from rich.text import Text


class NewspaperModal(ModalScreen):
    """Modal displaying all messenger logs in a large, scrollable newspaper format"""

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
        ("n", "dismiss_modal", "Close"),  # Toggle: N closes if already open
    ]

    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container(id="newspaper-modal"):
            yield Label("📰 NEWSPAPER", id="modal-title")
            yield Label("Tycoons Daily", id="newspaper-subtitle")

            with ScrollableContainer(id="newspaper-content"):
                # Content will be populated in on_mount
                pass

            yield Button("Close (ESC / N)", variant="success", id="close-btn")

    def on_mount(self) -> None:
        """Populate newspaper content after mount"""
        self.refresh_content()

    def refresh_content(self) -> None:
        """Refresh the newspaper content with latest messenger logs"""
        try:
            container = self.query_one("#newspaper-content", ScrollableContainer)
        except Exception:
            return

        # Clear existing content
        try:
            container.remove_children()
        except Exception:
            pass

        # Get all messenger entries
        try:
            entries = self.app.engine.messenger.get_entries()
        except Exception:
            entries = []

        if not entries:
            container.mount(Label("No messages to display.", classes="no-messages"))
            return

        # Render messages with same styling as messenger panel
        current_date = None
        for e in entries:
            ts = e.get("ts", "")
            body = e.get("text", "")
            level = str(e.get("level", "info")).lower()

            # Add date separator if day changed
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

            # Color mapping for the filled dot by level (same as messenger panel)
            if level == "error":
                dot_color = "#d16a66"  # salmon/red
            elif level == "warn" or level == "warning":
                dot_color = "#e0b15a"  # amber
            elif level == "debug":
                dot_color = "#8a91a7"  # muted gray/blue for debug
            else:
                dot_color = "#4ea59a"  # teal for info/default

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
                    # Fallback formatting
                    if len(ts) >= 19 and ts[10] in ("T", " "):
                        render.append("→ ", style="white")
                        render.append(f"[{ts[:10]}: {ts[11:19]}]", style="white")
                        render.append(" ●", style=dot_color)
                        render.append(" → ", style="white")
                    else:
                        render.append(f"[{ts}]", style="white")
                        render.append(" ● ", style=dot_color)

            # Message body in slightly dimmer color (same as messenger panel)
            render.append(body, style="#c2c9d6")
            container.mount(Label(render, classes="newspaper-message"))

        # Auto-scroll to bottom to show latest entries
        try:
            container.scroll_end(animate=False)
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-btn":
            self.dismiss()

    def action_dismiss_modal(self) -> None:
        """Close the modal when ESC or N is pressed"""
        self.dismiss()