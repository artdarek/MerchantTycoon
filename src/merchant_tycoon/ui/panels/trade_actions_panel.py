from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static, Label, Button

from ...engine import GameEngine

# Import modals lazily at runtime via self.app.push_screen to avoid circulars.
# Type hints avoided for self.app to prevent import cycles.


class TradeActionsPanel(Static):
    """Compact panel with Buy/Sell buttons for assets"""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("🛒 TRADE STOCKS", id="trade-actions-header", classes="panel-title")
        with Horizontal(id="trade-actions-bar"):
            # Reuse existing IDs so compact button CSS applies
            yield Button("Buy", id="exchange-buy-btn", variant="success")
            yield Button("Sell", id="exchange-sell-btn", variant="error", disabled=not bool(self.engine.state.portfolio))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Import here to avoid top-level circular imports
        from ..modals import BuyAssetModal, SellAssetModal
        if event.button.id == "exchange-buy-btn":
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
        # Keep Sell disabled when no assets
        try:
            sell_btn = self.query_one("#exchange-sell-btn", Button)
            sell_btn.disabled = not bool(self.engine.state.portfolio)
        except Exception:
            pass
