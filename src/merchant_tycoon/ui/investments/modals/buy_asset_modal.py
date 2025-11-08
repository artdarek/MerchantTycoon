from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label, Button, Input, Select
from textual.screen import ModalScreen

from merchant_tycoon.engine import GameEngine
from merchant_tycoon.model import STOCKS, COMMODITIES, CRYPTO


class BuyAssetModal(ModalScreen):
    """Modal for buying stocks/commodities"""

    def __init__(self, engine: GameEngine, callback, default_symbol: str | None = None, default_quantity: int | None = None):
        super().__init__()
        self.engine = engine
        self.callback = callback
        self.max_quantities = {}  # Store max quantity for each asset
        self.default_symbol = default_symbol
        self.default_quantity = default_quantity
        self._suppress_autofill = False

    def compose(self) -> ComposeResult:
        with Container(id="buy-modal"):
            yield Label("💰 Buy Assets", id="modal-title")

            options = []
            all_assets = STOCKS + COMMODITIES + CRYPTO
            for asset in all_assets:
                price = self.engine.asset_prices[asset.symbol]
                max_affordable = self.engine.state.cash // price if price > 0 else 0

                # Store max quantity for this asset
                self.max_quantities[asset.symbol] = max_affordable

                # Choose icon based on asset type
                if asset.asset_type == "stock":
                    asset_type_icon = "📊"
                elif asset.asset_type == "commodity":
                    asset_type_icon = "🌾"
                else:  # crypto
                    asset_type_icon = "₿"

                # Format price based on asset type
                if asset.asset_type == "crypto" and price < 10:
                    price_str = f"${price:.2f}"
                else:
                    price_str = f"${price:,}"

                options.append((
                    f"{asset_type_icon} {asset.symbol} - {asset.name} @ {price_str} (max: {max_affordable})",
                    asset.symbol
                ))

            yield Label("Select asset:")
            yield Select(options, prompt="Choose an asset...", id="asset-select")
            yield Label("Enter quantity:")
            yield Input(placeholder="Quantity...", type="integer", id="quantity-input")

            with Horizontal(id="modal-buttons"):
                yield Button("Buy", variant="primary", id="confirm-btn")
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
                    success, msg = self.engine.buy_asset(symbol, quantity)
                    # Service logs; no callback needed for logging
                    self.callback(msg)
                except ValueError:
                    pass
        else:
            self.dismiss()
