from textual.app import ComposeResult
from textual.widgets import Static, Label
from textual.containers import Horizontal
from rich.text import Text

from merchant_tycoon.engine import GameEngine


class LoanBalancePanel(Static):
    """Display player's loan (debt) summary."""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("💳 LOAN BALANCE", id="loan-header", classes="panel-title")
        # First line: Debt, then credit capacity and max new loan
        with Horizontal(id="loan-summary"):
            yield Label("Debt: $0", id="loan-debt")
            yield Label("Credit Cap: $0", id="loan-credit-cap")
            yield Label("Max New Loan: $0", id="loan-credit-available")
        # Second line: today's offer (APR)
        with Horizontal(id="loan-rate-summary"):
            yield Label("Today's Loan Offer: APR 0.00% (Daily 0.0000%)", id="loan-rate")

    def update_loan(self) -> None:
        state = self.engine.state
        # Update summary labels
        debt_lbl = self.query_one('#loan-debt', Label)
        rate_lbl = self.query_one('#loan-rate', Label)

        debt_lbl.update(Text(f"Debt: ${state.debt:,}", no_wrap=True, overflow="crop"))
        # Display today's loan offer APR and derived daily rate
        try:
            apr = float(getattr(self.engine.bank_service, 'loan_apr_today', 0.10))
        except Exception:
            apr = 0.10
        daily = apr / 365.0
        rate_lbl.update(Text(f"Today's Loan Offer: APR {apr * 100:.2f}% (Daily {daily * 100:.4f}%)", no_wrap=True, overflow="crop"))
        # Credit capacity info
        try:
            _, max_total, max_new = self.engine.bank_service.compute_credit_limits()
            cap_lbl = self.query_one('#loan-credit-cap', Label)
            avail_lbl = self.query_one('#loan-credit-available', Label)
            cap_lbl.update(Text(f"Cap: ${max_total:,}", no_wrap=True, overflow="crop"))
            avail_lbl.update(Text(f"Max New: ${max_new:,}", no_wrap=True, overflow="crop"))
        except Exception:
            pass
