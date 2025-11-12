from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label, Button, Input, Select
from textual.screen import ModalScreen

from merchant_tycoon.engine import GameEngine


class SellLotModal(ModalScreen):
    """Modal for selling goods from a specific lot. Displays lots for a single product
    and lets the user choose a lot and quantity (default to lot size)."""

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
    ]

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
            title = "💵 Sell Goods (Lot)"
            parts = title.split(None, 1)
            if len(parts) == 2:
                title = f"{parts[0]} {parts[1].upper()}"
            else:
                title = title.upper()
            yield Label(title, id="modal-title")

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
        # Disable qty until a lot is selected
        self._set_qty_enabled(bool(getattr(lot_select, "value", None)))
        self._update_sell_enabled()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "lot-select":
            if event.value:
                max_qty = int(self.max_quantities.get(event.value, 0))
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
                selected = bool(getattr(self.query_one("#lot-select", Select), "value", None))
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
            lot_select = self.query_one("#lot-select", Select)
            qty_input = self.query_one("#quantity-input", Input)
            slots_label = self.query_one("#cargo-slots-info", Label)
        except Exception:
            return

        lot_ts = lot_select.value
        if not lot_ts:
            slots_label.update("")
            return

        try:
            qty_val = int((qty_input.value or "0").strip())
        except Exception:
            qty_val = 0

        if qty_val <= 0:
            slots_label.update("")
            return

        # Get product size
        try:
            good = self.engine.goods_repo.get_by_name(self.product)
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
            lot_select = self.query_one("#lot-select", Select)
            qty_input = self.query_one("#quantity-input", Input)
            btn = self.query_one("#confirm-btn", Button)
        except Exception:
            return
        has_lot = bool(lot_select.value)
        try:
            qty = int((qty_input.value or "0").strip())
        except Exception:
            qty = 0
        btn.disabled = not (has_lot and qty >= 1)

        # Update cargo slots info whenever sell button state changes
        self._update_cargo_slots_info()

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
                if qty >= 1:
                    self.callback(self.product, lot_ts, qty)
        else:
            self.dismiss()

    def action_dismiss_modal(self) -> None:
        self.dismiss()
