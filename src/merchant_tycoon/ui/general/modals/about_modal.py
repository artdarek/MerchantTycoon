from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label, Button
from textual.screen import ModalScreen

import merchant_tycoon as pkg


class AboutModal(ModalScreen):
    """Modal showing application information (name, version, authors)."""

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="about-modal"):
            yield Label("ℹ️ ABOUT MERCHANT TYCOON", id="modal-title")

            name = "Merchant Tycoon"
            try:
                version = getattr(pkg, "__version__", "")
            except Exception:
                version = ""

            yield Label(f"Name: {name}")
            if version:
                yield Label(f"Version: {version}")
            yield Label("Main developer: Dariusz Przada")
            yield Label("Junior developers: Claude Code, Junie, Codex")

            yield Button("Close (ESC)", variant="success", id="close-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-btn":
            self.dismiss()

    def action_dismiss_modal(self) -> None:
        self.dismiss()
