from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label, Button, Input, Select
from textual.screen import ModalScreen

from merchant_tycoon.engine import GameEngine


class SellLotModal(ModalScreen):
    """Modal for selling goods from a specific lot. Displays lots for a single product
    and lets the user choose a lot and quantity (default to lot size)."""

    def __init__(self, engine: GameEngine, product: str, default_lot_ts: str, default_quantity: int, callback):
        super().__init__()
        self.engine = engine
        self.product = product
        self.default_lot_ts = default_lot_ts
        self.default_quantity = int(default_quantity)
        self.callback = callback  # expects (product, lot_ts, qty)
        self.max_quantities: dict[str, int] = {}

    def compose(self) -> ComposeResult:
        with Container(id="sell-modal"):
            yield Label("💵 Sell Goods (Lot)", id="modal-title")

            # Build options from lots for the product
            options = []
            lots = self.engine.state.get_lots_for_good(self.product)
            current_price = int(self.engine.prices.get(self.product, 0))
            for lot in lots:
                qty = int(getattr(lot, "quantity", 0))
                pp = int(getattr(lot, "purchase_price", 0))
                total_value = qty * current_price
                ts = str(getattr(lot, "ts", ""))
                city = str(getattr(lot, "city", ""))
                self.max_quantities[ts] = qty
                date_only = ts[:10] if ts else ""
                options.append(
                    (
                        f"{self.product} — {qty}x @ ${pp:,}  (date: {date_only}, city: {city}, worth now ${total_value:,})",
                        ts,
                    )
                )

            yield Label("Select lot to sell:")
            yield Select(options, prompt="Choose a lot...", id="lot-select")
            yield Label("Enter quantity to sell:")
            yield Input(placeholder="Quantity...", type="integer", id="quantity-input")

            with Horizontal(id="modal-buttons"):
                yield Button("Sell", variant="primary", id="confirm-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_mount(self) -> None:
        # Preselect lot and quantity
        try:
            lot_select = self.query_one("#lot-select", Select)
            qty_input = self.query_one("#quantity-input", Input)
        except Exception:
            return
        try:
            lot_select.value = self.default_lot_ts
        except Exception:
            pass
        try:
            qty_input.value = str(self.default_quantity)
        except Exception:
            pass

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "lot-select" and event.value:
            max_qty = int(self.max_quantities.get(event.value, 0))
            input_widget = self.query_one("#quantity-input", Input)
            input_widget.value = str(max_qty)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            lot_select = self.query_one("#lot-select", Select)
            qty_input = self.query_one("#quantity-input", Input)
            lot_ts = lot_select.value
            qty_str = qty_input.value.strip()
            self.dismiss()
            if lot_ts and qty_str:
                try:
                    qty = int(qty_str)
                except ValueError:
                    qty = 0
                self.callback(self.product, lot_ts, qty)
        else:
            self.dismiss()

