from textual.app import ComposeResult
from textual.widgets import Static, Label, DataTable

from ...engine import GameEngine


class InventoryPanel(Static):
    """Display player inventory"""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("📦 YOUR INVENTORY", id="inventory-header", classes="panel-title")
        yield DataTable(id="inventory-table")

    def update_inventory(self):
        table = self.query_one("#inventory-table", DataTable)

        # Configure columns once
        if not getattr(self, "_inventory_table_initialized", False):
            table.clear(columns=True)
            table.add_columns("Product", "Qty", "Price", "Value", "Avg Cost", "P/L", "P/L%")
            try:
                table.cursor_type = "row"
                table.show_header = True
                table.zebra_stripes = True
            except Exception:
                pass
            self._inventory_table_initialized = True

        # Clear existing rows
        try:
            table.clear(rows=True)
        except Exception:
            table.clear()

        if not self.engine.state.inventory:
            # Show a single informative row
            table.add_row("(empty)", "", "", "", "", "", "")
            return

        for good_name, quantity in sorted(self.engine.state.inventory.items()):
            current_price = self.engine.prices.get(good_name, 0)
            current_value = current_price * quantity

            # Calculate total cost and average cost from FIFO lots
            lots = self.engine.state.get_lots_for_good(good_name)
            total_cost = sum(lot.quantity * lot.purchase_price for lot in lots)
            avg_cost = (total_cost // quantity) if quantity > 0 else 0

            profit = current_value - total_cost
            profit_pct = (profit / total_cost * 100) if total_cost > 0 else 0

            table.add_row(
                good_name,
                str(quantity),
                f"${current_price:,}",
                f"${current_value:,}",
                f"${avg_cost:,}",
                f"${profit:+,}",
                f"{profit_pct:+.0f}%",
            )
