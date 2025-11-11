from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label, Button
from textual.screen import ModalScreen


class ConfirmModal(ModalScreen):
    """Simple confirmation modal with configurable button labels (defaults Yes/No)."""

    BINDINGS = [
        ("enter", "confirm", "Yes"),
        # ESC only dismisses the modal; it does NOT trigger cancel callback.
        ("escape", "dismiss_only", "Close"),
    ]

    def __init__(self, title: str, message: str, on_confirm, on_cancel=None, *, confirm_label: str = "Yes", cancel_label: str = "No"):
        super().__init__()
        self._title = title
        self._message = message
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel
        self._confirm_label = confirm_label
        self._cancel_label = cancel_label

    def compose(self) -> ComposeResult:
        with Container(id="confirm-modal"):
            # Add emoji by title context and uppercase the rest
            title = self._title or ""
            lower = title.lower()
            emoji = "❓"
            if "quit" in lower:
                emoji = "🚪"
            elif "save" in lower:
                emoji = "💾"
            elif "load" in lower:
                emoji = "📂"
            elif "new game" in lower or "start" in lower:
                emoji = "🆕"
            elif "delete" in lower:
                emoji = "🗑️"
            # Always render as "EMOJI {FULL TITLE UPPERCASE}"
            final = f"{emoji} {title.upper()}"
            yield Label(final, id="modal-title")
            yield Label(self._message)
            with Horizontal(id="modal-buttons"):
                yield Button(self._confirm_label, id="yes-btn", variant="success")
                yield Button(self._cancel_label, id="no-btn", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes-btn":
            self.action_confirm()
        elif event.button.id == "no-btn":
            # Clicking the explicit NO/EXIT button invokes cancel callback
            # Dismiss first, then call callback to allow opening other modals
            callback = self._on_cancel
            self.dismiss()
            if callable(callback):
                callback()

    def action_confirm(self) -> None:
        # Dismiss first, then call callback
        # This allows callback to open another modal without stack conflicts
        callback = self._on_confirm
        self.dismiss()
        if callable(callback):
            callback()

    def action_cancel(self) -> None:  # kept for backward compatibility
        self.dismiss()

    def action_dismiss_only(self) -> None:
        self.dismiss()
