from textual.app import ComposeResult
from textual.widgets import Static, Label, DataTable
from rich.text import Text

from merchant_tycoon.engine import GameEngine


class InventoryPanel(Static):
    """Display player inventory"""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine
        self._row_to_product = {}

    def compose(self) -> ComposeResult:
        yield Label("📦 YOUR INVENTORY", id="inventory-header", classes="panel-title")
        yield DataTable(id="inventory-table")

    def update_inventory(self):
        table = self.query_one("#inventory-table", DataTable)

        # Configure columns once
        if not getattr(self, "_inventory_table_initialized", False):
            table.clear(columns=True)
            table.add_columns(
                "Product",
                "Category",
                "Qty",
                "Qty/L",
                "Cost/L",
                "Price",
                "Value",
                "Avg Cost",
                "P/L",
                "P/L%",
                "Type",
            )
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
        self._row_to_product = {}

        if not self.engine.state.inventory:
            # Show a single informative row (11 columns)
            table.add_row("(empty)", "", "", "", "", "", "", "", "", "", "")
            return

        for good_name, quantity in sorted(self.engine.state.inventory.items()):
            current_price = self.engine.prices.get(good_name, 0)
            current_value = current_price * quantity

            # Calculate total cost and average cost from FIFO lots (only remaining qty)
            lots = self.engine.state.get_lots_for_good(good_name)
            total_cost = sum(lot.quantity * lot.purchase_price for lot in lots)
            avg_cost = (total_cost // quantity) if quantity > 0 else 0
            # Sum lost across lots
            try:
                lost_total = sum(int(getattr(lot, "lost_quantity", 0)) for lot in lots)
            except Exception:
                lost_total = 0
            # Sum lost cost across lots at each lot's purchase price
            try:
                lost_cost_total = sum(int(getattr(lot, "lost_quantity", 0)) * int(getattr(lot, "purchase_price", 0)) for lot in lots)
            except Exception:
                lost_cost_total = 0

            # Sum lot-level P/L for robustness (equals current_value - total_cost)
            profit = sum((current_price - lot.purchase_price) * lot.quantity for lot in lots)
            profit_pct = (profit / total_cost * 100) if total_cost > 0 else 0

            # Colored cells for clarity
            if profit > 0:
                pl_cell = Text(f"${profit:+,}", style="green")
                pl_pct_cell = Text(f"{profit_pct:+.1f}%", style="green")
            elif profit < 0:
                pl_cell = Text(f"${profit:+,}", style="red")
                pl_pct_cell = Text(f"{profit_pct:+.1f}%", style="red")
            else:
                pl_cell = Text("$0", style="dim")
                pl_pct_cell = Text("0.0%", style="dim")

            try:
                good_obj = self.engine.goods_service.get_good(good_name)
            except Exception:
                good_obj = None
            g_type = getattr(good_obj, "type", "standard") if good_obj else "standard"
            g_cat = getattr(good_obj, "category", "hardware") if good_obj else "hardware"

            row_key = table.add_row(
                good_name,
                g_cat,
                str(quantity),
                str(int(lost_total)),
                f"${int(lost_cost_total):,}",
                f"${current_price:,}",
                f"${current_value:,}",
                f"${avg_cost:,}",
                pl_cell,
                pl_pct_cell,
                g_type,
            )
            try:
                self._row_to_product[row_key] = good_name
            except Exception:
                pass

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # Open Sell modal for the clicked product with default = owned quantity
        try:
            table = event.data_table
        except Exception:
            table = None
        if not table or getattr(table, "id", None) != "inventory-table":
            return
        product = self._row_to_product.get(getattr(event, "row_key", None))
        if not product:
            return
        owned = int(self.engine.state.inventory.get(product, 0))
        if owned <= 0:
            return
        try:
            from merchant_tycoon.ui.goods.modals import SellModal
            self.app.push_screen(SellModal(self.engine, self.app._handle_sell, default_product=product, default_quantity=owned))
        except Exception:
            pass
