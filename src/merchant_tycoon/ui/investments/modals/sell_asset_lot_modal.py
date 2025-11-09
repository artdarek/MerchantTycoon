from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label, Button, Input, Select
from textual.screen import ModalScreen

from merchant_tycoon.engine import GameEngine


class SellAssetLotModal(ModalScreen):
    """Sell a specific quantity from a selected investment lot (by timestamp)."""

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
    ]

    def __init__(self, engine: GameEngine, symbol: str, lot_ts: str, default_quantity: int, callback):
        super().__init__()
        self.engine = engine
        self.symbol = symbol
        self.lot_ts = lot_ts
        self.default_quantity = int(max(0, int(default_quantity)))
        self.callback = callback  # expects (msg: str)

    def compose(self) -> ComposeResult:
        with Container(id="sell-modal"):
            title = "💵 Sell Assets (Lot)"
            parts = title.split(None, 1)
            if len(parts) == 2:
                title = f"{parts[0]} {parts[1].upper()}"
            else:
                title = title.upper()
            yield Label(title, id="modal-title")

        
            # Build select options from lots for this symbol
            options: list[tuple[str, str]] = []
            lots = [lot for lot in (self.engine.state.investment_lots or []) if getattr(lot, "asset_symbol", "") == self.symbol]
            current_price = int(self.engine.asset_prices.get(self.symbol, 0))
            # Enrich display with asset name/type like in SellAssetModal
            try:
                asset = self.engine.investments_service.get_asset(self.symbol)
            except Exception:
                asset = None
            asset_name = getattr(asset, "name", self.symbol)
            if asset and asset.asset_type == "stock":
                icon = "📊"
            elif asset and asset.asset_type == "commodity":
                icon = "🌾"
            elif asset and asset.asset_type == "crypto":
                icon = "₿"
            else:
                icon = "❓"
            price_str = f"${current_price:.2f}" if (asset and asset.asset_type == "crypto" and current_price < 10) else f"${current_price:,}"
            self._max_for_ts: dict[str, int] = {}
            for lot in lots:
                qty = int(getattr(lot, "quantity", 0))
                pp = int(getattr(lot, "purchase_price", 0))
                total_now = qty * current_price
                total_buy = qty * pp
                pl = total_now - total_buy
                ts = str(getattr(lot, "ts", ""))
                self._max_for_ts[ts] = qty
                date_only = ts[:10] if ts and len(ts) >= 10 else ""
                # Build rich option text similar to SellAssetModal
                text = (
                    f"{icon} {self.symbol} - {asset_name} | "
                    f"{qty}x @ ${pp:,}/unit (bought ${total_buy:,}) | "
                    f"now @ {price_str}/unit (worth ${total_now:,}, P/L {pl:+,}) • {date_only}"
                )
                options.append((text, ts))

            yield Label("Select lot to sell:")
            yield Select(options, prompt="Choose a lot...", id="lot-select")

            # Quantity field (enabled; validated against lot size on submit)
            yield Label("Enter quantity to sell:")
            qty = Input(placeholder="Quantity...", type="integer", id="quantity-input")
            try:
                qty.value = str(self.default_quantity)
                qty.disabled = True
                qty.can_focus = False
            except Exception:
                pass
            yield qty

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
        # Preselect provided lot if present
        try:
            lot_select = self.query_one("#lot-select", Select)
            if self.lot_ts:
                lot_select.value = self.lot_ts
        except Exception:
            pass
        # Enable qty if a lot is selected
        try:
            self._set_qty_enabled(bool(getattr(self.query_one("#lot-select", Select), "value", None)))
        except Exception:
            self._set_qty_enabled(False)
        # Initialize button state
        self._update_enabled()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "quantity-input":
            try:
                qty = int((event.value or "0").strip())
            except Exception:
                qty = 0
            try:
                self.query_one("#confirm-btn", Button).disabled = qty <= 0
            except Exception:
                pass

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "lot-select":
            if event.value:
                max_qty = int(self._max_for_ts.get(event.value, 0))
                try:
                    self.query_one("#quantity-input", Input).value = str(max_qty)
                except Exception:
                    pass
                self._set_qty_enabled(True)
                self._update_enabled()
            else:
                self._set_qty_enabled(False)
                self._update_enabled()

    def _update_enabled(self) -> None:
        try:
            lot_selected = bool(getattr(self.query_one("#lot-select", Select), "value", None))
            qty_val = int((getattr(self.query_one("#quantity-input", Input), "value", "0") or "0").strip())
        except Exception:
            lot_selected = False
            qty_val = 0
        try:
            self.query_one("#confirm-btn", Button).disabled = not (lot_selected and qty_val > 0)
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            try:
                lot_select = self.query_one("#lot-select", Select)
                ts = lot_select.value
            except Exception:
                ts = None
            qty_input = self.query_one("#quantity-input", Input)
            try:
                qty = int((qty_input.value or "0").strip())
            except Exception:
                qty = 0
            # Validate against selected lot size; warn and keep modal open if exceeded
            try:
                max_allowed = int(self._max_for_ts.get(ts, 0)) if ts else 0
            except Exception:
                max_allowed = 0
            if not ts or qty <= 0:
                return
            if qty > max_allowed:
                try:
                    self.engine.messenger.warn("Selected lot does not contain that many units.", tag="investments")
                    self.app.refresh_all()
                except Exception:
                    pass
                return
            ok, msg = self.engine.investments_service.sell_asset_from_lot(self.symbol, ts, qty)
            # Emit feedback
            if not ok:
                try:
                    self.engine.messenger.warn(msg or "Unable to sell from the selected lot.", tag="investments")
                    self.app.refresh_all()
                except Exception:
                    pass
            else:
                try:
                    self.callback(msg)
                except Exception:
                    pass
            self.dismiss()
        else:
            self.dismiss()

    def action_dismiss_modal(self) -> None:
        self.dismiss()
