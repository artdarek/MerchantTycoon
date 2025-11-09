from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label, Button, Input, Select
from textual.screen import ModalScreen

from merchant_tycoon.engine import GameEngine
from merchant_tycoon.domain.constants import STOCKS, COMMODITIES, CRYPTO


class SellAssetModal(ModalScreen):
    """Modal for selling stocks/commodities"""

    def __init__(self, engine: GameEngine, callback, default_symbol: str | None = None, default_quantity: int | None = None):
        super().__init__()
        self.engine = engine
        self.callback = callback
        self.max_quantities = {}  # Store max quantity for each asset
        self.default_symbol = default_symbol
        self.default_quantity = default_quantity
        self._suppress_autofill = False

    def compose(self) -> ComposeResult:
        with Container(id="sell-modal"):
            yield Label("💵 Sell Assets", id="modal-title")

            options = []
            for symbol, quantity in self.engine.state.portfolio.items():
                price = self.engine.asset_prices[symbol]
                total_value = quantity * price

                # Store max quantity for this asset
                self.max_quantities[symbol] = quantity

                # Find asset info
                all_assets = STOCKS + COMMODITIES + CRYPTO
                asset = next((a for a in all_assets if a.symbol == symbol), None)

                # Choose icon based on asset type
                if asset and asset.asset_type == "stock":
                    asset_type_icon = "📊"
                elif asset and asset.asset_type == "commodity":
                    asset_type_icon = "🌾"
                elif asset and asset.asset_type == "crypto":
                    asset_type_icon = "₿"
                else:
                    asset_type_icon = "❓"

                asset_name = asset.name if asset else symbol

                # Format price based on asset type
                if asset and asset.asset_type == "crypto" and price < 10:
                    price_str = f"${price:.2f}"
                    total_str = f"${total_value:.2f}"
                else:
                    price_str = f"${price:,}"
                    total_str = f"${total_value:,}"

                options.append((
                    f"{asset_type_icon} {symbol} - {asset_name} @ {price_str}/unit (have: {quantity}, worth {total_str})",
                    symbol
                ))

            yield Label("Select asset to sell:")
            yield Select(options, prompt="Choose an asset...", id="asset-select")
            yield Label("Enter quantity to sell:")
            yield Input(placeholder="Quantity...", type="integer", id="quantity-input")

            with Horizontal(id="modal-buttons"):
                yield Button("Sell", variant="primary", id="confirm-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_mount(self) -> None:
        # Preselect asset and quantity if provided
        try:
            select_widget = self.query_one("#asset-select", Select)
            input_widget = self.query_one("#quantity-input", Input)
        except Exception:
            return
        if self.default_symbol:
            try:
                self._suppress_autofill = True
                select_widget.value = self.default_symbol
            except Exception:
                pass
            finally:
                self._suppress_autofill = False
        if self.default_quantity is not None:
            try:
                input_widget.value = str(int(self.default_quantity))
            except Exception:
                pass

    def on_select_changed(self, event: Select.Changed) -> None:
        """Auto-fill quantity when asset is selected"""
        if getattr(self, "_suppress_autofill", False):
            return
        if event.select.id == "asset-select" and event.value:
            max_qty = self.max_quantities.get(event.value, 0)
            input_widget = self.query_one("#quantity-input", Input)
            input_widget.value = str(max_qty)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            select_widget = self.query_one("#asset-select", Select)
            input_widget = self.query_one("#quantity-input", Input)

            symbol = select_widget.value
            quantity_str = input_widget.value.strip()

            self.dismiss()

            if symbol and quantity_str:
                try:
                    quantity = int(quantity_str)
                    success, msg = self.engine.sell_asset(symbol, quantity)
                    # Service logs; no callback needed for logging
                    self.callback(msg)
                except ValueError:
                    pass
        else:
            self.dismiss()
