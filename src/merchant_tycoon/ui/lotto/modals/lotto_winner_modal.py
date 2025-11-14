"""Lotto Winner modal for displaying daily lottery wins."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label, Button, Static
from textual.screen import ModalScreen


class LottoWinnerModal(ModalScreen):
    """Modal showing lotto winnings summary for the day."""

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
        ("enter", "dismiss_modal", "Close"),
    ]

    def __init__(self, wins: list, on_close=None):
        """Initialize lotto winner modal.

        Args:
            wins: List of win dicts with 'ticket', 'matched', 'payout' keys
        """
        super().__init__()
        self.wins = wins
        self._on_close = on_close

    def compose(self) -> ComposeResult:
        # Match EventModal (dividend) look-and-feel
        with Container(id="alert-modal-positive"):
            # Uppercase title with leading emoji preserved
            title = "🏆 Lotto Winner!"
            parts = title.split(None, 1)
            if len(parts) == 2:
                title = f"{parts[0]} {parts[1].upper()}"
            else:
                title = title.upper()
            yield Label(title, id="modal-title")

            # Build a rich message with summary and details
            total_payout = sum(int(w.get("payout", 0)) for w in self.wins)
            win_count = len(self.wins)
            if win_count == 1:
                summary = f"You had 1 winning ticket and received ${total_payout:,}.\n\n"
            else:
                summary = f"You had {win_count} winning tickets and received ${total_payout:,}.\n\n"

            lines = ["Winning Tickets:"]
            for i, win in enumerate(self.wins, 1):
                numbers_str = ", ".join(str(n) for n in win.get("ticket", []))
                matched = int(win.get("matched", 0))
                payout = int(win.get("payout", 0))
                lines.append(f"#{i}: [{numbers_str}] - {matched} matches → ${payout:,}")

            message = summary + "\n".join(lines)
            yield Static(message, id="alert-message")
            yield Button("OK (ENTER)", variant="success", id="ok-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok-btn":
            self.dismiss()
            if callable(self._on_close):
                try:
                    self._on_close()
                except Exception:
                    pass

    def action_dismiss_modal(self) -> None:
        self.dismiss()
        if callable(self._on_close):
            try:
                self._on_close()
            except Exception:
                pass
