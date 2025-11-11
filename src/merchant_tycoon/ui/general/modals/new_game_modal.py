from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Label, Button, Select
from textual.screen import ModalScreen
from textual.reactive import reactive

from merchant_tycoon.domain.game_difficulty_levels import GAME_DIFFICULTY_LEVELS


class NewGameModal(ModalScreen):
    """Modal for selecting difficulty level when starting a new game."""

    BINDINGS = [
        ("escape", "dismiss_only", "Close"),
    ]

    selected_difficulty = reactive("normal")

    def __init__(self, on_confirm, on_cancel=None):
        super().__init__()
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel

    def compose(self) -> ComposeResult:
        # Build select options from GAME_DIFFICULTY_LEVELS
        options = [(level.display_name, level.name) for level in GAME_DIFFICULTY_LEVELS]

        with Container(id="new-game-modal"):
            yield Label("🆕 NEW GAME — SELECT DIFFICULTY", id="modal-title")
            yield Label("Choose your starting challenge", classes="modal-subtitle")

            with Vertical(id="difficulty-selector"):
                yield Select(
                    options=options,
                    value="normal",
                    id="difficulty-select",
                    allow_blank=False,
                )
                yield Label("", id="difficulty-details", classes="difficulty-info")

            with Horizontal(id="modal-buttons"):
                yield Button("Start Game", id="start-btn", variant="success")
                yield Button("Cancel", id="cancel-btn", variant="error")

    def on_mount(self) -> None:
        """Update details when modal mounts."""
        self._update_difficulty_details("normal")

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle difficulty selection change."""
        if event.select.id == "difficulty-select":
            self.selected_difficulty = str(event.value)
            self._update_difficulty_details(str(event.value))

    def _update_difficulty_details(self, difficulty_name: str) -> None:
        """Update the difficulty details label."""
        # Find the difficulty level
        difficulty = None
        for level in GAME_DIFFICULTY_LEVELS:
            if level.name == difficulty_name:
                difficulty = level
                break

        if difficulty:
            details_text = f"{difficulty.description}\n"
            details_text += f"💵 ${difficulty.start_cash:,} • 📦 {difficulty.start_capacity} slots"

            details_label = self.query_one("#difficulty-details", Label)
            details_label.update(details_text)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start-btn":
            self.action_confirm()
        elif event.button.id == "cancel-btn":
            try:
                if callable(self._on_cancel):
                    self._on_cancel()
            finally:
                self.dismiss()

    def action_confirm(self) -> None:
        try:
            if callable(self._on_confirm):
                self._on_confirm(self.selected_difficulty)
        finally:
            self.dismiss()

    def action_dismiss_only(self) -> None:
        self.dismiss()