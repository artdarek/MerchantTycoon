from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static, Label, Button

from merchant_tycoon.engine import GameEngine


class LoanActionsPanel(Static):
    """Compact panel with Loan/Repay buttons for bank loans."""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        with Horizontal(id="loan-actions-bar"):
            yield Button("Loan [L]", id="loan-take-btn", variant="success")
            yield Button(
                "Repay [R]",
                id="loan-repay-btn",
                variant="warning",
                disabled=(self.engine.state.debt <= 0 or self.engine.state.cash <= 0),
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "loan-take-btn":
            try:
                self.app.action_loan()
            except Exception:
                pass
        elif event.button.id == "loan-repay-btn":
            try:
                self.app.action_repay()
            except Exception:
                pass

    def update_actions(self) -> None:
        """Enable/disable buttons based on current debt and cash."""
        try:
            repay_btn = self.query_one("#loan-repay-btn", Button)
            repay_btn.disabled = (self.engine.state.debt <= 0 or self.engine.state.cash <= 0)
        except Exception:
            pass
        # Disable Loan button when there is no credit capacity available
        try:
            loan_btn = self.query_one("#loan-take-btn", Button)
            _w, _cap, max_new = self.engine.bank_service.compute_credit_limits()
            loan_btn.disabled = (int(max_new) <= 0)
        except Exception:
            pass
