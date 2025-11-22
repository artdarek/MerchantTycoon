from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label, Button
from textual.screen import ModalScreen


class InvestmentsLockedModal(ModalScreen):
    """Modal shown when investments are locked due to insufficient wealth."""

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
        ("enter", "dismiss_modal", "Close"),
    ]

    def __init__(self, title: str, message: str):
        super().__init__()
        self.alert_title = title
        self.alert_message = message

    def compose(self) -> ComposeResult:
        # Use the negative alert style for locked state
        with Container(id="alert-modal-negative"):
            # Uppercase the title while preserving leading emoji + single space
            t = self.alert_title or ""
            parts = t.split(None, 1)
            if len(parts) == 2:
                t = f"{parts[0]} {parts[1].upper()}"
            else:
                t = t.upper()
            yield Label(t, id="modal-title")
            yield Label(self.alert_message, id="alert-message")
            yield Button("OK (ENTER)", variant="error", id="ok-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok-btn":
            self.dismiss()

    def action_dismiss_modal(self) -> None:
        """Close the modal when ESC or ENTER is pressed"""
        self.dismiss()

