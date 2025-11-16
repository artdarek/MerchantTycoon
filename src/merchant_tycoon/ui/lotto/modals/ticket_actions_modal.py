"""Ticket Actions modal for managing individual lottery tickets."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label, Button
from textual.screen import ModalScreen


class TicketActionsModal(ModalScreen):
    """Modal for managing a single lottery ticket (activate/deactivate/remove)."""

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
    ]

    def __init__(self, ticket_numbers: list, is_active: bool, on_toggle, on_remove):
        """Initialize ticket actions modal.

        Args:
            ticket_numbers: List of 6 numbers on this ticket
            is_active: Whether ticket is currently active
            on_toggle: Callback for toggle action
            on_remove: Callback for remove action
        """
        super().__init__()
        self.ticket_numbers = ticket_numbers
        # Avoid clashing with ModalScreen.read-only `is_active` property
        self.ticket_active = is_active
        self.on_toggle = on_toggle
        self.on_remove = on_remove

    def compose(self) -> ComposeResult:
        with Container(id="ticket-actions-modal"):
            # Match title formatting from BuyTicketModal/BuyModal
            title = "🎫 Ticket Actions"
            parts = title.split(None, 1)
            if len(parts) == 2:
                title = f"{parts[0]} {parts[1].upper()}"
            else:
                title = title.upper()
            yield Label(title, id="modal-title")

            # Show ticket numbers
            numbers_str = ", ".join(str(n) for n in self.ticket_numbers)
            yield Label(f"Numbers: {numbers_str}")

            # Show status
            status = "✅ Active" if self.ticket_active else "❌ Inactive"
            yield Label(f"Status: {status}")

            with Horizontal(id="modal-buttons"):
                # Toggle button (changes based on current state)
                if self.ticket_active:
                    yield Button("Deactivate", variant="warning", id="toggle-btn")
                else:
                    yield Button("Activate", variant="success", id="toggle-btn")

                yield Button("Remove", variant="error", id="remove-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "toggle-btn":
            self.dismiss()
            self.on_toggle()
        elif event.button.id == "remove-btn":
            self.dismiss()
            self.on_remove()
        else:
            # Unknown button id; just dismiss
            self.dismiss()

    def action_dismiss_modal(self) -> None:
        self.dismiss()
