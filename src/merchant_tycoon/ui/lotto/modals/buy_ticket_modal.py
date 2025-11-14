"""Buy Ticket modal for lotto system."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.widgets import Label, Button, Input
from textual.screen import ModalScreen


class BuyTicketModal(ModalScreen):
    """Modal for buying a lottery ticket with 6 number inputs.

    Styled and structured to match the Buy goods modal.
    """

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
        ("enter", "submit_modal", "Confirm"),
    ]

    def __init__(self, callback, max_number: int = 45, preset_numbers: list[int] | None = None):
        """Initialize buy ticket modal.

        Args:
            callback: Function to call with list of 6 numbers
            max_number: Maximum valid number (default 45)
        """
        super().__init__()
        self.callback = callback
        self.max_number = max_number
        self.preset_numbers = list(preset_numbers) if preset_numbers else None

    def compose(self) -> ComposeResult:
        with Container(id="buy-ticket-modal"):
            # Uppercase title formatting like other modals
            title = "🎫 Buy Lotto Ticket"
            parts = title.split(None, 1)
            if len(parts) == 2:
                title = f"{parts[0]} {parts[1].upper()}"
            else:
                title = title.upper()
            yield Label(title, id="modal-title")

            yield Label(f"Select 6 unique numbers (1-{self.max_number}):")

            # Compact row with 6 columns; label above each input
            with Horizontal(id="number-inputs"):
                for i in range(1, 7):
                    with Vertical(classes="lotto-num-col"):
                        yield Label(f"#{i}", classes="lotto-num-label")
                        yield Input(placeholder="", id=f"number-{i}", type="integer", classes="lotto-num-input")

            yield Label("", id="error-message", classes="error")

            with Horizontal(id="modal-buttons"):
                # Match confirm/cancel styling and layout
                yield Button("Buy", variant="success", id="confirm-btn", disabled=True)
                yield Button("Cancel", variant="error", id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            self._validate_and_submit()
        else:
            self.dismiss()

    def _validate_and_submit(self) -> None:
        """Validate inputs and submit if valid."""
        error_label = self.query_one("#error-message", Label)
        error_label.update("")

        try:
            # Collect all numbers
            numbers = []
            for i in range(1, 7):
                input_widget = self.query_one(f"#number-{i}", Input)
                value_str = input_widget.value.strip()

                if not value_str:
                    error_label.update(f"❌ Number {i} is required")
                    self._update_confirm_enabled()
                    return

                try:
                    num = int(value_str)
                except ValueError:
                    error_label.update(f"❌ Number {i} must be an integer")
                    self._update_confirm_enabled()
                    return

                if num < 1 or num > self.max_number:
                    error_label.update(f"❌ Number {i} must be between 1 and {self.max_number}")
                    self._update_confirm_enabled()
                    return

                numbers.append(num)

            # Check for duplicates
            if len(set(numbers)) != 6:
                error_label.update("❌ All numbers must be unique")
                self._update_confirm_enabled()
                return

            # Valid! Call callback and close
            self.dismiss()
            self.callback(numbers)

        except Exception as e:
            error_label.update(f"❌ Error: {str(e)}")
        finally:
            self._update_confirm_enabled()

    def _update_confirm_enabled(self) -> None:
        """Enable confirm only when 6 valid unique numbers are provided."""
        try:
            btn = self.query_one("#confirm-btn", Button)
        except Exception:
            return
        try:
            values = []
            for i in range(1, 7):
                v = (self.query_one(f"#number-{i}", Input).value or "").strip()
                if not v:
                    btn.disabled = True
                    return
                try:
                    n = int(v)
                except Exception:
                    btn.disabled = True
                    return
                if n < 1 or n > self.max_number:
                    btn.disabled = True
                    return
                values.append(n)
            # Must be unique
            btn.disabled = len(set(values)) != 6
        except Exception:
            btn.disabled = False

    def on_mount(self) -> None:
        # Prefill numbers if provided (Lucky shot)
        if self.preset_numbers:
            try:
                nums = list(self.preset_numbers)[:6]
                for i, n in enumerate(nums, 1):
                    self.query_one(f"#number-{i}", Input).value = str(int(n))
            except Exception:
                pass
        # Initialize confirm state
        self._update_confirm_enabled()

    def on_input_changed(self, event: Input.Changed) -> None:
        # As user types, update confirm availability
        self._update_confirm_enabled()

    def action_dismiss_modal(self) -> None:
        self.dismiss()

    def action_submit_modal(self) -> None:
        # ENTER should act like confirm
        self._validate_and_submit()
