from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label, Button
from textual.screen import ModalScreen


class ConfirmModal(ModalScreen):
    """Simple confirmation modal with Yes/No buttons."""

    BINDINGS = [
        ("enter", "confirm", "Yes"),
        ("escape", "cancel", "No"),
    ]

    def __init__(self, title: str, message: str, on_confirm, on_cancel=None):
        super().__init__()
        self._title = title
        self._message = message
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel

    def compose(self) -> ComposeResult:
        with Container(id="confirm-modal"):
            yield Label(self._title, id="modal-title")
            yield Label(self._message)
            with Horizontal(id="modal-buttons"):
                yield Button("Yes", id="yes-btn", variant="primary")
                yield Button("No", id="no-btn", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes-btn":
            self.action_confirm()
        elif event.button.id == "no-btn":
            self.action_cancel()

    def action_confirm(self) -> None:
        try:
            if callable(self._on_confirm):
                self._on_confirm()
        finally:
            self.dismiss()

    def action_cancel(self) -> None:
        try:
            if callable(self._on_cancel):
                self._on_cancel()
        finally:
            self.dismiss()
