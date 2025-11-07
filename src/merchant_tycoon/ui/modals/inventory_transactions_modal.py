from textual.app import ComposeResult
from textual.containers import Vertical, ScrollableContainer
from textual.widgets import Label, Button
from textual.screen import ModalScreen
from rich.text import Text

from ...engine import GameEngine


class InventoryTransactionsModal(ModalScreen):
    """Modal showing detailed inventory with purchase lots and profit/loss"""

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
    ]

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        with Vertical(id="transactions-modal"):
            yield Label("📊 INVENTORY DETAILS", id="modal-title")
            yield Label("Use ↑↓ or mouse wheel to scroll", id="transactions-instructions")
            yield ScrollableContainer(id="transactions-content")
            yield Button("Close (ESC)", variant="primary", id="close-btn")

    def on_mount(self) -> None:
        self._update_details()

    def _update_details(self):
        try:
            container = self.query_one("#transactions-content", ScrollableContainer)
            container.remove_children()

            if not self.engine.state.inventory:
                container.mount(Label("No goods in inventory"))
                return

            for good_name in sorted(self.engine.state.inventory.keys()):
                total_qty = self.engine.state.inventory.get(good_name, 0)
                current_price = self.engine.prices.get(good_name, 0)
                lots = self.engine.state.get_lots_for_good(good_name)

                # Header for this good
                container.mount(Label(""))  # Empty line
                container.mount(Label(f" {good_name} ", classes="section-header"))
                container.mount(Label(""))
                container.mount(Label(f"  Total owned: {total_qty} units"))
                container.mount(Label(f"  Market price: ${current_price:,}"))
                container.mount(Label(""))

                if not lots:
                    container.mount(Label("  (No purchase history available)"))
                    container.mount(Label(""))
                else:
                    # Calculate total profit/loss
                    total_invested = sum(lot.quantity * lot.purchase_price for lot in lots)
                    total_current_value = total_qty * current_price
                    total_profit = total_current_value - total_invested
                    total_profit_pct = (total_profit / total_invested * 100) if total_invested > 0 else 0

                    profit_symbol = "📈" if total_profit > 0 else "📉" if total_profit < 0 else "➖"
                    container.mount(Label(
                        f"  {profit_symbol} Total P/L: ${total_profit:+,} ({total_profit_pct:+.1f}%)"
                    ))
                    container.mount(Label(""))
                    container.mount(Label("  Purchase History (FIFO order):"))

                    for i, lot in enumerate(lots, 1):
                        profit_per_unit = current_price - lot.purchase_price
                        lot_profit = profit_per_unit * lot.quantity
                        lot_profit_pct = (profit_per_unit / lot.purchase_price * 100) if lot.purchase_price > 0 else 0

                        profit_symbol = "📈" if profit_per_unit > 0 else "📉" if profit_per_unit < 0 else "➖"
                        profit_color = "green" if profit_per_unit > 0 else "red" if profit_per_unit < 0 else "dim"

                        container.mount(Label(""))
                        container.mount(Label(
                            f"    [{i}] {lot.quantity}x @ ${lot.purchase_price:,}/unit = ${lot.quantity * lot.purchase_price:,}",
                            classes="lot-info"
                        ))
                        container.mount(Label(
                            f"        Bought: Day {lot.day} in {lot.city}",
                            classes="lot-info"
                        ))

                        profit_text = Text(
                            f"        {profit_symbol} If sold now: ${profit_per_unit:+,}/unit "
                            f"({lot_profit_pct:+.1f}%) = ${lot_profit:+,}",
                            style=profit_color
                        )
                        profit_text.stylize(profit_color, 8)  # Apply color from after spaces
                        container.mount(Label(profit_text))
                    container.mount(Label(""))
        except Exception as e:
            # If there's any error, show a simple error message
            try:
                container = self.query_one("#transactions-content", ScrollableContainer)
                container.remove_children()
                container.mount(Label(f"Error loading details: {str(e)}"))
            except:  # noqa: E722
                pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-btn":
            self.dismiss()

    def action_dismiss_modal(self) -> None:
        """Close the modal when ESC is pressed"""
        self.dismiss()
