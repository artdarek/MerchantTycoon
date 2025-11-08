from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static, Label, Button

from merchant_tycoon.engine import GameEngine


class AccountActionsPanel(Static):
    """Compact panel with Deposit/Withdraw buttons for the bank account."""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("🏦 ACCOUNT ACTIONS", id="bank-actions-header", classes="panel-title")
        with Horizontal(id="bank-actions-bar"):
            # Use consistent compact button styling as other action panels
            yield Button("Deposit [D]", id="bank-deposit-btn", variant="success")
            yield Button(
                "Withdraw [W]",
                id="bank-withdraw-btn",
                variant="warning",
                disabled=self.engine.state.bank.balance <= 0,
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Delegate to app actions that already open the proper modals/handlers
        if event.button.id == "bank-deposit-btn":
            try:
                self.app.action_bank_deposit()
            except Exception:
                pass
        elif event.button.id == "bank-withdraw-btn":
            try:
                self.app.action_bank_withdraw()
            except Exception:
                pass

    def update_actions(self) -> None:
        """Enable/disable buttons based on current state."""
        try:
            deposit_btn = self.query_one("#bank-deposit-btn", Button)
            withdraw_btn = self.query_one("#bank-withdraw-btn", Button)
            # Disable deposit if no cash on hand
            deposit_btn.disabled = self.engine.state.cash <= 0
            # Disable withdraw if no funds in bank
            withdraw_btn.disabled = self.engine.state.bank.balance <= 0
        except Exception:
            pass
