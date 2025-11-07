from textual.app import ComposeResult
from textual.widgets import Static, Label
from textual.containers import Horizontal

from ...engine import GameEngine


class AccountBalancePanel(Static):
    """Display player's bank account summary (no transactions)."""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("🏦 ACCOUNT BALANCE", id="bank-header", classes="panel-title")
        with Horizontal(id="bank-summary"):
            yield Label("Balance: $0", id="bank-balance")
            yield Label("Daily Rate: 0.00%", id="bank-rate")
            yield Label("Accrued: $0", id="bank-accrued")

    def update_bank(self) -> None:
        bank = self.engine.state.bank
        # Update summary labels
        bal_lbl = self.query_one('#bank-balance', Label)
        rate_lbl = self.query_one('#bank-rate', Label)
        acc_lbl = self.query_one('#bank-accrued', Label)

        bal_lbl.update(f"Balance: ${bank.balance:,}")
        rate_lbl.update(f"Daily Rate: {bank.interest_rate_daily * 100:.3f}%")
        acc_lbl.update(f"Accrued: ${int(bank.accrued_interest):,}" if bank.accrued_interest >= 1 else "Accrued: <$1")
