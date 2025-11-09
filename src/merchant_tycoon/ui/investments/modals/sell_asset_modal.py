from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label, Button, Input, Select
from textual.screen import ModalScreen

from merchant_tycoon.engine import GameEngine


class SellAssetModal(ModalScreen):
    """Modal for selling stocks/commodities"""

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
    ]

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
            title = "💵 Sell Assets"
            parts = title.split(None, 1)
            if len(parts) == 2:
                title = f"{parts[0]} {parts[1].upper()}"
            else:
                title = title.upper()
            yield Label(title, id="modal-title")

            options = []
            for symbol, quantity in self.engine.state.portfolio.items():
                price = self.engine.asset_prices[symbol]
                total_value = quantity * price

                # Store max quantity for this asset
                self.max_quantities[symbol] = quantity

                # Find asset info
                try:
                    asset = self.engine.investments_service.get_asset(symbol)
                except Exception:
                    asset = None

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
            qty = Input(placeholder="Quantity...", type="integer", id="quantity-input")
            try:
                qty.disabled = True
                qty.can_focus = False
            except Exception:
                pass
            yield qty

            with Horizontal(id="modal-buttons"):
                yield Button("Sell", variant="success", id="confirm-btn", disabled=True)
                yield Button("Cancel", variant="error", id="cancel-btn")

    def _set_qty_enabled(self, enabled: bool) -> None:
        try:
            qty = self.query_one("#quantity-input", Input)
            qty.disabled = not enabled
            try:
                qty.can_focus = enabled
            except Exception:
                pass
        except Exception:
            pass

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
        # Disable quantity until an asset is selected
        self._set_qty_enabled(bool(getattr(select_widget, "value", None)))
        self._update_sell_enabled()

    def on_select_changed(self, event: Select.Changed) -> None:
        """Auto-fill quantity when asset is selected"""
        if getattr(self, "_suppress_autofill", False):
            return
        if event.select.id == "asset-select":
            if event.value:
                max_qty = self.max_quantities.get(event.value, 0)
                try:
                    self.query_one("#quantity-input", Input).value = str(max_qty)
                except Exception:
                    pass
                self._set_qty_enabled(True)
            else:
                self._set_qty_enabled(False)
            self._update_sell_enabled()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "quantity-input":
            try:
                selected = bool(getattr(self.query_one("#asset-select", Select), "value", None))
                if not selected:
                    event.input.value = ""
                    self._set_qty_enabled(False)
                    self._update_sell_enabled()
                    return
            except Exception:
                pass
            self._update_sell_enabled()

    def _update_sell_enabled(self) -> None:
        try:
            select_widget = self.query_one("#asset-select", Select)
            input_widget = self.query_one("#quantity-input", Input)
            btn = self.query_one("#confirm-btn", Button)
        except Exception:
            return
        has_symbol = bool(select_widget.value)
        try:
            qty = int((input_widget.value or "0").strip())
        except Exception:
            qty = 0
        btn.disabled = not (has_symbol and qty >= 1)

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
                    if quantity >= 1:
                        success, msg = self.engine.sell_asset(symbol, quantity)
                        # Service logs; no callback needed for logging
                        self.callback(msg)
                except ValueError:
                    pass
        else:
            self.dismiss()

    def action_dismiss_modal(self) -> None:
        """Close the modal when ESC is pressed"""
        self.dismiss()
