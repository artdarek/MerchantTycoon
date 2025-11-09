from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label, Button, Input
from textual.screen import ModalScreen


class InputModal(ModalScreen):
    """Generic input modal"""

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
    ]

    def __init__(self, title: str, prompt: str, callback, default_value: str = "", *, confirm_variant: str = "success", cancel_variant: str = "error"):
        super().__init__()
        self.modal_title = title
        self.modal_prompt = prompt
        self.callback = callback
        self.default_value = default_value
        self._confirm_variant = confirm_variant
        self._cancel_variant = cancel_variant

    def compose(self) -> ComposeResult:
        with Container(id="input-modal"):
            # Ensure uppercase title with leading emoji and a single space
            t = self.modal_title or ""
            parts = t.split(None, 1)
            if len(parts) == 2:
                t = f"{parts[0]} {parts[1].upper()}"
            else:
                t = t.upper()
            yield Label(t, id="modal-title")
            yield Label(self.modal_prompt)
            yield Input(placeholder="Enter value...", value=self.default_value, id="modal-input")
            with Horizontal(id="modal-buttons"):
                yield Button("Confirm", variant=self._confirm_variant, id="confirm-btn")
                yield Button("Cancel", variant=self._cancel_variant, id="cancel-btn")

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

    def action_dismiss_modal(self) -> None:
        self.dismiss()
