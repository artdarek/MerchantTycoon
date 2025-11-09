from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Static, Label, DataTable
from rich.text import Text

from merchant_tycoon.engine import GameEngine
from merchant_tycoon.domain.constants import GOODS

GOODS_BY_NAME = {g.name: g for g in GOODS}


class InventoryLotsPanel(Static):
    """Per-good breakdown of purchase lots (like the Inventory details modal),
    shown inline as tables under YOUR INVENTORY. Only shows goods currently held.
    """

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine
        # Map table identity -> { 'good': str, 'rows': {row_key: qty} }
        self._tables: dict[int, dict] = {}

    def compose(self) -> ComposeResult:
        # Section header for purchased lots
        yield Label("🧾 PURCHASED LOTS", id="inventory-lots-header", classes="panel-title")
        yield ScrollableContainer(id="inventory-lots-content")

    def update_lots(self) -> None:
        container = self.query_one("#inventory-lots-content", ScrollableContainer)
        try:
            container.remove_children()
        except Exception:
            pass

        state = self.engine.state
        prices = self.engine.prices

        # Only display goods that are currently in inventory (>0)
        goods_owned = [g for g, qty in (state.inventory or {}).items() if qty > 0]
        goods_owned.sort()
        if not goods_owned:
            return

        # Single table for all goods' lots
        table = DataTable()
        try:
            table.cursor_type = "row"
            table.show_header = True
            table.zebra_stripes = True
        except Exception:
            pass
        table.add_columns("Product", "Category", "Date", "City", "Qty", "Price", "Total", "P/L", "P/L%", "Type")

        meta = {"rows": {}}
        self._tables[id(table)] = meta

        for good_name in goods_owned:
            current_price = prices.get(good_name, 0)
            lots = state.get_lots_for_good(good_name)
            if not lots:
                continue

            for lot in lots:
                qty = int(getattr(lot, "quantity", 0))
                pp = int(getattr(lot, "purchase_price", 0))
                city = str(getattr(lot, "city", ""))
                total = qty * pp
                profit_per_unit = current_price - pp
                lot_profit = profit_per_unit * qty
                lot_profit_pct = (profit_per_unit / pp * 100) if pp > 0 else 0

                # Color profit cells
                if lot_profit > 0:
                    pl_cell = Text(f"${lot_profit:+,}", style="green")
                    pl_pct_cell = Text(f"{lot_profit_pct:+.1f}%", style="green")
                elif lot_profit < 0:
                    pl_cell = Text(f"${lot_profit:+,}", style="red")
                    pl_pct_cell = Text(f"{lot_profit_pct:+.1f}%", style="red")
                else:
                    pl_cell = Text("$0", style="dim")
                    pl_pct_cell = Text("0.0%", style="dim")

                # Date only (YYYY-MM-DD) from ISO ts if present
                ts = str(getattr(lot, "ts", ""))
                date_only = ts[:10] if ts and len(ts) >= 10 else ""

                good_obj = GOODS_BY_NAME.get(good_name)
                g_type = getattr(good_obj, "type", "standard") if good_obj else "standard"
                g_cat = getattr(good_obj, "category", "hardware") if good_obj else "hardware"

                row_key = table.add_row(
                    good_name,
                    g_cat,
                    date_only,
                    city,
                    str(qty),
                    f"${pp:,}",
                    f"${total:,}",
                    pl_cell,
                    pl_pct_cell,
                    g_type,
                )
                try:
                    meta["rows"][row_key] = {"good": good_name, "qty": qty, "ts": ts}
                except Exception:
                    pass

        container.mount(table)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # Open Sell modal with product and lot quantity
        try:
            table = event.data_table
            meta = self._tables.get(id(table))
        except Exception:
            meta = None
        if not meta:
            return
        row_key = getattr(event, "row_key", None)
        if row_key is None:
            return
        entry = meta.get("rows", {}).get(row_key, {})
        good = entry.get("good")
        qty = int(entry.get("qty", 0))
        lot_ts = entry.get("ts", "")
        if not good or qty <= 0 or not lot_ts:
            return
        # Open modal to confirm/select quantity for this lot (default = lot qty)
        try:
            from merchant_tycoon.ui.goods.modals import SellLotModal
            self.app.push_screen(SellLotModal(self.engine, good, lot_ts, qty, self.app._handle_sell_from_lot))
        except Exception:
            pass
