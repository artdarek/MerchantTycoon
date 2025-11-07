from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label, Button, Input
from textual.screen import ModalScreen


class InputModal(ModalScreen):
    """Generic input modal"""

    def __init__(self, title: str, prompt: str, callback):
        super().__init__()
        self.modal_title = title
        self.modal_prompt = prompt
        self.callback = callback

    def compose(self) -> ComposeResult:
        with Container(id="input-modal"):
            yield Label(self.modal_title, id="modal-title")
            yield Label(self.modal_prompt)
            yield Input(placeholder="Enter value...", id="modal-input")
            with Horizontal(id="modal-buttons"):
                yield Button("Confirm", variant="primary", id="confirm-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            input_widget = self.query_one("#modal-input", Input)
            value = input_widget.value.strip()
            self.dismiss()
            if value:
                self.callback(value)
        else:
            self.dismiss()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        self.dismiss()
        if value:
            self.callback(value)
