from textual.app import ComposeResult
from textual.widgets import Static, Label

from ...engine import GameEngine
from ...models import CITIES


class StatsPanel(Static):
    """Display player stats"""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("", id="stats-content")

    def update_stats(self):
        state = self.engine.state
        city = CITIES[state.current_city]
        inventory_count = state.get_inventory_count()

        # Calculate total portfolio value
        portfolio_value = 0
        for symbol, quantity in state.portfolio.items():
            if symbol in self.engine.asset_prices:
                portfolio_value += quantity * self.engine.asset_prices[symbol]

        # Bank balance (added to header after Cash)
        bank_balance = state.bank.balance if hasattr(state, "bank") and state.bank is not None else 0

        stats_text = f"""💰 Cash: ${state.cash:,}  |  🏦 Bank: ${bank_balance:,}  |  💼 Investments: ${portfolio_value:,}  |  🏦 Debt: ${state.debt:,}  |  📅 Day: {state.day}  |  📍 {city.name}, {city.country}  |  📦 Cargo: {inventory_count}/{state.max_inventory}"""

        label = self.query_one("#stats-content", Label)
        label.update(stats_text)
