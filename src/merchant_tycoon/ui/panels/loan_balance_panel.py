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
            yield Label("Today's Loan Offer: APR 0.00% (Daily 0.0000%)", id="loan-rate")

    def update_loan(self) -> None:
        state = self.engine.state
        # Update summary labels
        debt_lbl = self.query_one('#loan-debt', Label)
        rate_lbl = self.query_one('#loan-rate', Label)

        debt_lbl.update(f"Debt: ${state.debt:,}")
        # Display today's loan offer APR and derived daily rate
        try:
            apr = float(getattr(self.engine, 'loan_apr_today', 0.10))
        except Exception:
            apr = 0.10
        daily = apr / 365.0
        rate_lbl.update(f"Today's Loan Offer: APR {apr * 100:.2f}% (Daily {daily * 100:.4f}%)")
