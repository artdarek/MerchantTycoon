from textual.app import ComposeResult
from textual.widgets import Static, Label
from textual.containers import Horizontal

from merchant_tycoon.engine import GameEngine


class AccountBalancePanel(Static):
    """Display player's bank account summary (no transactions)."""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("🏦 ACCOUNT BALANCE", id="bank-header", classes="panel-title")
        # First line: balance only (better readability)
        with Horizontal(id="bank-summary"):
            yield Label("Balance → $0", id="bank-balance")
        # Second line: APR and accrued
        with Horizontal(id="bank-rate-summary"):
            yield Label("APR (Today) → 0.00% • Daily → 0.0000%", id="bank-rate")
            yield Label("• Accrued → $0", id="bank-accrued")

    def update_bank(self) -> None:
        bank = self.engine.state.bank
        # Update summary labels
        bal_lbl = self.query_one('#bank-balance', Label)
        rate_lbl = self.query_one('#bank-rate', Label)
        acc_lbl = self.query_one('#bank-accrued', Label)

        bal_lbl.update(f"Balance → ${bank.balance:,}")
        try:
            apr = float(getattr(bank, 'interest_rate_annual', 0.02))
        except Exception:
            apr = 0.02
        daily = self.engine.bank_service.get_bank_daily_rate()
        rate_lbl.update(f"APR (Today) → {apr * 100:.2f}% • Daily → {daily * 100:.4f}%")
        acc_lbl.update(
            f"• Accrued → ${int(bank.accrued_interest):,}" if bank.accrued_interest >= 1 else "• Accrued → <$1"
        )
