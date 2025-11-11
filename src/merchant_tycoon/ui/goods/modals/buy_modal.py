from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label, Button, Input, Select
from textual.screen import ModalScreen

from merchant_tycoon.engine import GameEngine


class BuyModal(ModalScreen):
    """Modal for buying goods with product selector and quantity input"""

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
        with Container(id="buy-modal"):
            title = "🛒 Buy Goods"
            parts = title.split(None, 1)
            if len(parts) == 2:
                title = f"{parts[0]} {parts[1].upper()}"
            else:
                title = title.upper()
            yield Label(title, id="modal-title")

            # Create select options with prices and max quantity
            options = []

            # Get available cargo space (accounting for product sizes)
            if hasattr(self.engine, 'cargo_service') and self.engine.cargo_service:
                available_space = self.engine.cargo_service.get_free_slots()
            else:
                # Fallback to old method
                available_space = self.engine.state.max_inventory - self.engine.state.get_inventory_count()

            try:
                goods = self.engine.goods_repo.get_all()
            except Exception:
                goods = []
            for good in goods:
                price = self.engine.prices[good.name]
                # Calculate max affordable based on cash
                max_affordable = self.engine.state.cash // price if price > 0 else 0

                # Calculate how many units fit based on product size
                product_size = getattr(good, "size", 1)
                max_that_fits = (available_space // product_size) if product_size > 0 else available_space

                # Calculate actual max (limited by both cash and space)
                max_buyable = min(max_affordable, max_that_fits)

                # Store max quantity for this product
                self.max_quantities[good.name] = max_buyable

                options.append((
                    f"{good.name} - ${price:,} (max: {max_buyable})",
                    good.name
                ))

            yield Label("Select product:")
            yield Select(options, prompt="Choose a product...", id="product-select")
            yield Label("Enter quantity:")
            qty = Input(placeholder="Quantity...", type="integer", id="quantity-input")
            try:
                qty.disabled = True
                qty.can_focus = False
            except Exception:
                pass
            yield qty

            with Horizontal(id="modal-buttons"):
                # Disabled until valid selection and quantity >= 1
                yield Button("Buy", variant="success", id="confirm-btn", disabled=True)
                yield Button("Cancel", variant="error", id="cancel-btn")

    # --- helpers ---
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
        # Disable quantity field until a product is selected
        self._set_qty_enabled(bool(getattr(select_widget, "value", None)))
        # Initialize Buy button enabled state
        self._update_buy_enabled()

    def on_select_changed(self, event: Select.Changed) -> None:
        """Auto-fill quantity when product is selected"""
        if getattr(self, "_suppress_autofill", False):
            return
        if event.select.id == "product-select":
            if event.value:
                max_qty = self.max_quantities.get(event.value, 0)
                try:
                    self.query_one("#quantity-input", Input).value = str(max_qty)
                except Exception:
                    pass
                self._set_qty_enabled(True)
            else:
                self._set_qty_enabled(False)
            self._update_buy_enabled()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "quantity-input":
            try:
                selected = bool(getattr(self.query_one("#product-select", Select), "value", None))
                if not selected:
                    event.input.value = ""
                    self._set_qty_enabled(False)
                    self._update_buy_enabled()
                    return
            except Exception:
                pass
            self._update_buy_enabled()

    def _update_buy_enabled(self) -> None:
        """Enable Buy only when a product is selected and quantity >= 1."""
        try:
            select_widget = self.query_one("#product-select", Select)
            input_widget = self.query_one("#quantity-input", Input)
            buy_btn = self.query_one("#confirm-btn", Button)
        except Exception:
            return
        has_product = bool(select_widget.value)
        try:
            qty_val = int((input_widget.value or "0").strip())
        except Exception:
            qty_val = 0
        buy_btn.disabled = not (has_product and qty_val >= 1)

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
                    if quantity >= 1:
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

    def action_dismiss_modal(self) -> None:
        self.dismiss()
