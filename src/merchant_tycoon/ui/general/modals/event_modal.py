from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label, Button, Static
from textual.screen import ModalScreen
from typing import Literal


EventType = Literal["loss", "gain", "neutral"]


class EventModal(ModalScreen):
    """Modal for displaying travel events with callback support

    Supports three event types:
    - loss: Red theme for negative events (robbery, fire, etc.)
    - gain: Green theme for positive events (dividend, lottery, etc.)
    - neutral: Gray theme for informational events (price changes)
    """

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
        ("enter", "dismiss_modal", "Close"),
    ]

    def __init__(self, title: str, message: str, event_type: EventType, callback):
        super().__init__()
        self.alert_title = title
        self.alert_message = message
        self.event_type = event_type
        self.callback = callback

    def compose(self) -> ComposeResult:
        # Map event type to modal ID and button variant
        if self.event_type == "gain":
            modal_id = "alert-modal-positive"
            button_variant = "success"
        elif self.event_type == "loss":
            modal_id = "alert-modal-negative"
            button_variant = "error"
        else:  # neutral
            modal_id = "alert-modal-neutral"
            button_variant = "default"

        with Container(id=modal_id):
            # Uppercase the title while preserving leading emoji + single space
            t = self.alert_title or ""
            parts = t.split(None, 1)
            if len(parts) == 2:
                t = f"{parts[0]} {parts[1].upper()}"
            else:
                t = t.upper()
            yield Label(t, id="modal-title")
            yield Static(self.alert_message, id="alert-message")
            yield Button("OK (ENTER)", variant=button_variant, id="ok-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok-btn":
            self.dismiss()
            if self.callback:
                self.callback()

    def action_dismiss_modal(self) -> None:
        """Close the modal when ESC or ENTER is pressed"""
        self.dismiss()
        if self.callback:
            self.callback()
