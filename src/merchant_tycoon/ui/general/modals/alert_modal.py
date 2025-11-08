from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label, Button
from textual.screen import ModalScreen


class AlertModal(ModalScreen):
    """Modal for displaying alerts/notifications"""

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
        ("enter", "dismiss_modal", "Close"),
    ]

    def __init__(self, title: str, message: str, is_positive: bool = False):
        super().__init__()
        self.alert_title = title
        self.alert_message = message
        self.is_positive = is_positive

    def compose(self) -> ComposeResult:
        modal_id = "alert-modal-positive" if self.is_positive else "alert-modal-negative"
        with Container(id=modal_id):
            yield Label(self.alert_title, id="modal-title")
            yield Label(self.alert_message, id="alert-message")
            yield Button("OK (ENTER)", variant="primary", id="ok-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok-btn":
            self.dismiss()

    def action_dismiss_modal(self) -> None:
        """Close the modal when ESC or ENTER is pressed"""
        self.dismiss()
