from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label, Button, Input, Select
from textual.screen import ModalScreen

from merchant_tycoon.engine import GameEngine
from merchant_tycoon.model import GOODS


class BuyModal(ModalScreen):
    """Modal for buying goods with product selector and quantity input"""

    def __init__(self, engine: GameEngine, callback):
        super().__init__()
        self.engine = engine
        self.callback = callback
        self.max_quantities = {}  # Store max quantity for each product

    def compose(self) -> ComposeResult:
        with Container(id="buy-modal"):
            yield Label("🛒 Buy Goods", id="modal-title")

            # Create select options with prices and max quantity
            options = []
            available_space = self.engine.state.max_inventory - self.engine.state.get_inventory_count()

            for good in GOODS:
                price = self.engine.prices[good.name]
                # Calculate max affordable based on cash
                max_affordable = self.engine.state.cash // price if price > 0 else 0
                # Calculate actual max (limited by inventory space)
                max_buyable = min(max_affordable, available_space)

                # Store max quantity for this product
                self.max_quantities[good.name] = max_buyable

                options.append((
                    f"{good.name} - ${price:,} (max: {max_buyable})",
                    good.name
                ))

            yield Label("Select product:")
            yield Select(options, prompt="Choose a product...", id="product-select")
            yield Label("Enter quantity:")
            yield Input(placeholder="Quantity...", type="integer", id="quantity-input")

            with Horizontal(id="modal-buttons"):
                yield Button("Buy", variant="primary", id="confirm-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_select_changed(self, event: Select.Changed) -> None:
        """Auto-fill quantity when product is selected"""
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
        # Trigger buy on Enter key
        select_widget = self.query_one("#product-select", Select)
        product = select_widget.value

        try:
            quantity = int(event.value.strip())
            self.dismiss()
            if product:
                self.callback(product, quantity)
        except ValueError:
            pass
