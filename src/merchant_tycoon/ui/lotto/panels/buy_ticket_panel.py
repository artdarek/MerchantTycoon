from textual.app import ComposeResult
from textual.widgets import Static, Label, Button

from merchant_tycoon.engine import GameEngine
from merchant_tycoon.config import SETTINGS
from merchant_tycoon.ui.lotto.modals import BuyTicketModal


class BuyTicketPanel(Static):
    """Left-column panel with Buy Ticket button and brief info."""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("🎫 BUY TICKET", classes="panel-title")
        # Show quick hint with price and rules (no buttons here; moved to actions panel)
        price = int(getattr(SETTINGS.lotto, "ticket_price", 10))
        renewal = int(getattr(SETTINGS.lotto, "ticket_renewal_cost", 10))
        rng = int(getattr(SETTINGS.lotto, "number_range_max", 45))
        yield Label(f"Price: ${price:,}  •  Renewal: ${renewal:,}/day  •  Pick 6 (1-{rng})")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        pass
