from textual.app import ComposeResult
from textual.widgets import Static, Label
from textual.containers import Horizontal

from merchant_tycoon.engine import GameEngine


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
        # Put credit capacity info on a new line for readability
        with Horizontal(id="loan-credit-summary"):
            yield Label("Credit Cap: $0", id="loan-credit-cap")
            yield Label("Max New Loan: $0", id="loan-credit-available")

    def update_loan(self) -> None:
        state = self.engine.state
        # Update summary labels
        debt_lbl = self.query_one('#loan-debt', Label)
        rate_lbl = self.query_one('#loan-rate', Label)

        debt_lbl.update(f"Debt: ${state.debt:,}")
        # Display today's loan offer APR and derived daily rate
        try:
            apr = float(getattr(self.engine.bank_service, 'loan_apr_today', 0.10))
        except Exception:
            apr = 0.10
        daily = apr / 365.0
        rate_lbl.update(f"Today's Loan Offer: APR {apr * 100:.2f}% (Daily {daily * 100:.4f}%)")
        # Credit capacity info
        try:
            _, max_total, max_new = self.engine.bank_service.compute_credit_limits()
            cap_lbl = self.query_one('#loan-credit-cap', Label)
            avail_lbl = self.query_one('#loan-credit-available', Label)
            cap_lbl.update(f"Credit Cap: ${max_total:,}")
            avail_lbl.update(f"Max New Loan: ${max_new:,}")
        except Exception:
            pass
