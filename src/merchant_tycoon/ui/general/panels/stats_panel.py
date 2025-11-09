from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static, Label
from rich.text import Text

from merchant_tycoon.engine import GameEngine


class StatsPanel(Static):
    """Display player stats"""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        with Horizontal(id="stats-row"):
            yield Label("", id="stats-left")
            yield Label("", id="stats-spacer")
            yield Label("", id="stats-cargo")

    def update_stats(self):
        state = self.engine.state
        inventory_count = state.get_inventory_count()

        # Calculate total portfolio value
        portfolio_value = 0
        for symbol, quantity in state.portfolio.items():
            if symbol in self.engine.asset_prices:
                portfolio_value += quantity * self.engine.asset_prices[symbol]

        # Bank balance (added to header after Cash)
        bank_balance = state.bank.balance if hasattr(state, "bank") and state.bank is not None else 0

        left_text = (
            f"💰 Cash → ${state.cash:,}  •  "
            f"🏦 Bank → ${bank_balance:,}  •  "
            f"📈 Assets → ${portfolio_value:,}  •  "
            f"💳 Debt → ${state.debt:,}"
        )
        right_text = f"📦 Cargo → {inventory_count}/{state.max_inventory}"

        left_render = Text(left_text, no_wrap=True, overflow="ellipsis")
        right_render = Text(right_text, no_wrap=True, overflow="crop")
        self.query_one("#stats-left", Label).update(left_render)
        self.query_one("#stats-cargo", Label).update(right_render)
