from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static, Label, Button

from merchant_tycoon.engine import GameEngine


class GoodsTradeActionsPanel(Static):
    """Compact panel with Buy/Sell buttons for goods"""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("🛒 TRADE GOODS", id="goods-trade-actions-header", classes="panel-title")
        with Horizontal(id="goods-trade-actions-bar"):
            yield Button("Buy", id="goods-buy-btn", variant="success")
            yield Button(
                "Sell",
                id="goods-sell-btn",
                variant="error",
                disabled=not bool(self.engine.state.inventory),
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        from ..modals import BuyModal, SellModal
        if event.button.id == "goods-buy-btn":
            try:
                self.app.push_screen(BuyModal(self.engine, self.app._handle_buy))
            except Exception:
                pass
        elif event.button.id == "goods-sell-btn":
            try:
                if not self.engine.state.inventory:
                    self.app.game_log("No goods to sell!")
                else:
                    self.app.push_screen(SellModal(self.engine, self.app._handle_sell))
            except Exception:
                pass

    def update_trade_actions(self):
        # Disable Sell when there are no goods in inventory
        try:
            sell_btn = self.query_one("#goods-sell-btn", Button)
            sell_btn.disabled = not bool(self.engine.state.inventory)
        except Exception:
            pass
