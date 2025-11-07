from textual.app import ComposeResult
from textual.widgets import Static, Label
from textual.containers import Horizontal

from ...engine import GameEngine


class LoanBalancePanel(Static):
    """Display player's loan (debt) summary."""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("💳 LOAN BALANCE", id="loan-header", classes="panel-title")
        with Horizontal(id="loan-summary"):
            yield Label("Debt: $0", id="loan-debt")
            yield Label("Current Daily Rate: 0.00%", id="loan-rate")

    def update_loan(self) -> None:
        state = self.engine.state
        # Update summary labels
        debt_lbl = self.query_one('#loan-debt', Label)
        rate_lbl = self.query_one('#loan-rate', Label)

        debt_lbl.update(f"Debt: ${state.debt:,}")
        # Engine interest_rate is decimal (e.g., 0.10 for 10%)
        try:
            rate = float(getattr(self.engine, 'interest_rate', 0.0))
        except Exception:
            rate = 0.0
        rate_lbl.update(f"Current daily rate: {rate * 100:.0f}%")
