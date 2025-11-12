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
            title = "💵 Sell Goods"
            parts = title.split(None, 1)
            if len(parts) == 2:
                title = f"{parts[0]} {parts[1].upper()}"
            else:
                title = title.upper()
            yield Label(title, id="modal-title")

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
            qty = Input(placeholder="Quantity...", type="integer", id="quantity-input")
            try:
                qty.disabled = True
                qty.can_focus = False
            except Exception:
                pass
            yield qty

            # Cargo slots information
            yield Label("", id="cargo-slots-info", classes="cargo-info")

            with Horizontal(id="modal-buttons"):
                yield Button("Sell", variant="success", id="confirm-btn", disabled=True)
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
        self._update_sell_enabled()

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
            self._update_sell_enabled()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "quantity-input":
            try:
                selected = bool(getattr(self.query_one("#product-select", Select), "value", None))
                if not selected:
                    event.input.value = ""
                    self._set_qty_enabled(False)
                    self._update_sell_enabled()
                    return
            except Exception:
                pass
            self._update_sell_enabled()

    def _update_cargo_slots_info(self) -> None:
        """Update the cargo slots information label."""
        try:
            select_widget = self.query_one("#product-select", Select)
            input_widget = self.query_one("#quantity-input", Input)
            slots_label = self.query_one("#cargo-slots-info", Label)
        except Exception:
            return

        product_name = select_widget.value
        if not product_name:
            slots_label.update("")
            return

        try:
            qty_val = int((input_widget.value or "0").strip())
        except Exception:
            qty_val = 0

        if qty_val <= 0:
            slots_label.update("")
            return

        # Get product size
        try:
            good = self.engine.goods_repo.get_by_name(product_name)
            product_size = getattr(good, "size", 1) if good else 1
        except Exception:
            product_size = 1

        # Calculate total slots to be freed
        slots_freed = qty_val * product_size

        # Get current cargo status
        if hasattr(self.engine, 'cargo_service') and self.engine.cargo_service:
            cargo_used = self.engine.cargo_service.get_used_slots()
            cargo_max = self.engine.cargo_service.get_max_slots()
        else:
            cargo_used = self.engine.state.get_inventory_count()
            cargo_max = self.engine.state.max_inventory

        cargo_after = cargo_used - slots_freed

        # Format message
        slots_label.update(f"Will free {slots_freed} cargo slot{'s' if slots_freed != 1 else ''} ({cargo_after}/{cargo_max} after)")

    def _update_sell_enabled(self) -> None:
        try:
            select_widget = self.query_one("#product-select", Select)
            input_widget = self.query_one("#quantity-input", Input)
            btn = self.query_one("#confirm-btn", Button)
        except Exception:
            return
        has_product = bool(select_widget.value)
        try:
            qty = int((input_widget.value or "0").strip())
        except Exception:
            qty = 0
        btn.disabled = not (has_product and qty >= 1)

        # Update cargo slots info whenever sell button state changes
        self._update_cargo_slots_info()

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
