from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label, Button, Input, Select
from textual.screen import ModalScreen

from merchant_tycoon.engine import GameEngine


class SellModal(ModalScreen):
    """Modal for selling goods with product selector and quantity input"""

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
    ]

    def __init__(self, engine: GameEngine, callback, default_product: str | None = None, default_quantity: int | None = None):
        super().__init__()
        self.engine = engine
        self.callback = callback
        self.max_quantities = {}  # Store max quantity for each product
        self.default_product = default_product
        self.default_quantity = default_quantity
        self._suppress_autofill = False

    def compose(self) -> ComposeResult:
        with Container(id="sell-modal"):
            yield Label("💵 Sell Goods", id="modal-title")

            # Create select options with inventory and prices
            options = []
            for good_name, quantity in self.engine.state.inventory.items():
                price = self.engine.prices[good_name]
                total_value = quantity * price

                # Store max quantity for this product
                self.max_quantities[good_name] = quantity

                options.append((
                    f"{good_name} - ${price:,}/unit (have: {quantity}, worth ${total_value:,})",
                    good_name
                ))

            yield Label("Select product to sell:")
            yield Select(options, prompt="Choose a product...", id="product-select")
            yield Label("Enter quantity to sell:")
            yield Input(placeholder="Quantity...", type="integer", id="quantity-input")

            with Horizontal(id="modal-buttons"):
                yield Button("Sell", variant="primary", id="confirm-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_mount(self) -> None:
        # Preselect product and quantity if provided
        try:
            select_widget = self.query_one("#product-select", Select)
            input_widget = self.query_one("#quantity-input", Input)
        except Exception:
            return
        if self.default_product:
            try:
                self._suppress_autofill = True
                select_widget.value = self.default_product
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
        """Auto-fill quantity when product is selected"""
        if getattr(self, "_suppress_autofill", False):
            return
        if event.select.id == "product-select" and event.value:
            max_qty = self.max_quantities.get(event.value, 0)
            input_widget = self.query_one("#quantity-input", Input)
            input_widget.value = str(max_qty)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            select_widget = self.query_one("#product-select", Select)
            input_widget = self.query_one("#quantity-input", Input)

            product = select_widget.value
            quantity_str = input_widget.value.strip()

            self.dismiss()

            if product and quantity_str:
                try:
                    quantity = int(quantity_str)
                    self.callback(product, quantity)
                except ValueError:
                    pass
        else:
            self.dismiss()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # Trigger sell on Enter key
        select_widget = self.query_one("#product-select", Select)
        product = select_widget.value

        try:
            quantity = int(event.value.strip())
            self.dismiss()
            if product:
                self.callback(product, quantity)
        except ValueError:
            pass

    def action_dismiss_modal(self) -> None:
        self.dismiss()
