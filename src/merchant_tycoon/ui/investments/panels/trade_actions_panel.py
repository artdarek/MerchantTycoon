from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static, Button

from merchant_tycoon.engine import GameEngine
from merchant_tycoon.config import SETTINGS

# Import modals lazily at runtime via self.app.push_screen to avoid circulars.
# Type hints avoided for self.app to prevent import cycles.


class TradeActionsPanel(Static):
    """Compact panel with Buy/Sell buttons for assets. Buy is blocked until wealth threshold reached."""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        # Always show normal trade actions (Buy button will be checked on click)
        with Horizontal(id="trade-actions-bar"):
            # Reuse existing IDs so compact button CSS applies
            yield Button("Buy [B]", id="exchange-buy-btn", variant="success")
            yield Button("Sell [S]", id="exchange-sell-btn", variant="error", disabled=not bool(self.engine.state.portfolio))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Import here to avoid top-level circular imports
        from merchant_tycoon.ui.investments.modals import BuyAssetModal, SellAssetModal
        from merchant_tycoon.ui.general.modals.alert_modal import AlertModal

        if event.button.id == "exchange-buy-btn":
            # Check if investments are unlocked (read-only, unlock happens during travel)
            threshold = int(getattr(SETTINGS.investments, "min_wealth_to_unlock_trading", 0))
            unlocked = getattr(self.engine.state, "investments_unlocked", False)

            # Auto-unlock if threshold is 0
            if threshold <= 0:
                unlocked = True

            if not unlocked:
                # Show locked alert modal
                current_wealth = self.engine.calculate_total_wealth()
                peak_wealth = int(getattr(self.engine.state, "peak_wealth", 0))
                progress_pct = (peak_wealth / threshold * 100) if threshold > 0 else 0

                message = (
                    f"Investment trading is currently locked.\n\n"
                    f"Required wealth: ${threshold:,}\n"
                    f"Current wealth: ${current_wealth:,}\n"
                    f"Peak wealth: ${peak_wealth:,}\n"
                    f"Progress: {progress_pct:.1f}%\n\n"
                    f"💡 Trade goods to build your wealth!\n"
                    f"Wealth = cash + bank + portfolio value"
                )

                try:
                    self.app.push_screen(AlertModal(
                        title="🔒 Investments Locked",
                        message=message,
                        is_positive=False
                    ))
                except Exception:
                    pass
                return

            # Unlocked - proceed with buy modal
            try:
                self.app.push_screen(BuyAssetModal(self.engine, self.app._handle_asset_trade))
            except Exception:
                pass
        elif event.button.id == "exchange-sell-btn":
            try:
                if not self.engine.state.portfolio:
                    self.app.game_log("No assets to sell!")
                else:
                    self.app.push_screen(SellAssetModal(self.engine, self.app._handle_asset_trade))
            except Exception:
                pass

    def update_trade_actions(self):
        """Update button states"""
        # Keep Sell disabled when no assets
        try:
            sell_btn = self.query_one("#exchange-sell-btn", Button)
            sell_btn.disabled = not bool(self.engine.state.portfolio)
        except Exception:
            pass
