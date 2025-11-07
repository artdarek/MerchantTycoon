from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static, Label, Button

from ...engine import GameEngine


class LoanActionsPanel(Static):
    """Compact panel with Loan/Repay buttons for bank loans."""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("💳 LOAN ACTIONS", id="loan-actions-header", classes="panel-title")
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
