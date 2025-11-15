from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static, Button

from merchant_tycoon.engine import GameEngine
from merchant_tycoon.config import SETTINGS
from merchant_tycoon.ui.lotto.modals import BuyTicketModal
import random


class TicketsActionPanel(Static):
    """Compact actions panel with Buy Ticket and Lucky Shot buttons.

    Styled to mirror AccountActionsPanel (bank actions bar).
    """

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        with Horizontal(id="lotto-actions-bar"):
            yield Button("Buy ticket", id="lotto-buy-btn", variant="success")
            # Match Bank actions styling: second button uses error variant (like Withdraw)
            yield Button("Lucky shot!", id="lotto-lucky-btn", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "lotto-buy-btn":
            # Open empty BuyTicket modal as before
            max_n = int(getattr(SETTINGS.lotto, "number_range_max", 45))

            def _after_choose(numbers: list[int]):
                ok, msg = self.engine.lotto_service.buy_ticket(numbers)
                if not ok:
                    self.engine.messenger.warn(msg, tag="lotto")
                self.app.refresh_all()

            self.app.push_screen(BuyTicketModal(_after_choose, max_number=max_n))

        elif event.button.id == "lotto-lucky-btn":
            # Prefill modal with random unique numbers in range
            max_n = int(getattr(SETTINGS.lotto, "number_range_max", 45))
            picks = sorted(random.sample(range(1, max_n + 1), 6))

            def _after_choose(numbers: list[int]):
                ok, msg = self.engine.lotto_service.buy_ticket(numbers)
                if not ok:
                    self.engine.messenger.warn(msg, tag="lotto")
                self.app.refresh_all()

            self.app.push_screen(BuyTicketModal(_after_choose, max_number=max_n, preset_numbers=picks))

    def update_actions(self) -> None:
        """Enable/disable based on cash for ticket price."""
        try:
            buy_btn = self.query_one("#lotto-buy-btn", Button)
            lucky_btn = self.query_one("#lotto-lucky-btn", Button)
            price = int(getattr(SETTINGS.lotto, "ticket_price", 10))
            can = int(self.engine.state.cash) >= price
            buy_btn.disabled = not can
            lucky_btn.disabled = not can
        except Exception:
            pass
