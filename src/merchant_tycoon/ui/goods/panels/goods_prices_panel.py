from textual.app import ComposeResult
from textual.widgets import Static, Label, DataTable
from rich.text import Text

from merchant_tycoon.engine import GameEngine
from merchant_tycoon.config import SETTINGS


class GoodsPricesPanel(Static):
    """Display market prices and buy/sell options"""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine
        self._row_to_product = {}

    def compose(self) -> ComposeResult:
        yield Label("🏪 MARKET PRICES", id="market-header", classes="panel-title")
        # Use a DataTable to present goods in a tabular format
        yield DataTable(id="market-table")

    def update_goods_prices(self):
        table = self.query_one("#market-table", DataTable)

        # Configure columns once
        if not getattr(self, "_market_table_initialized", False):
            table.clear(columns=True)
            window = int(SETTINGS.pricing.history_window)
            table.add_columns(
                "Product",
                "Category",
                "Size",
                "Price",
                "Prev",
                "Change",
                f"Min ({window}d)",
                f"Max ({window}d)",
                "Type",
            )
            # Optional: make table non-selectable for now (purely informational)
            try:
                table.cursor_type = "row"
                table.show_header = True
                table.zebra_stripes = True
            except Exception:
                pass
            self._market_table_initialized = True

        # Clear existing rows
        try:
            table.clear(rows=True)
        except Exception:
            # Fallback if signature differs
            table.clear()
        # Rebuild row->product mapping
        self._row_to_product = {}

        try:
            goods = self.engine.goods_service.get_goods()
        except Exception:
            goods = []
        for good in goods:
            price = self.engine.prices.get(good.name, 0)
            prev_price_val = self.engine.previous_prices.get(good.name, None)
            hist = (self.engine.state.price_history or {}).get(good.name, [])[-10:]

            # Compute price change indicator with color
            change_cell = Text("─", style="dim")
            if good.name in self.engine.previous_prices:
                prev_price = self.engine.previous_prices[good.name]
                if prev_price > 0:
                    if price > prev_price:
                        change_pct = (price - prev_price) / prev_price * 100
                        change_cell = Text(f"▲ +{change_pct:.0f}%", style="green")
                    elif price < prev_price:
                        change_pct = (prev_price - price) / prev_price * 100
                        change_cell = Text(f"▼ -{change_pct:.0f}%", style="red")
                    else:
                        change_cell = Text("─", style="dim")

            if hist:
                try:
                    minp = f"${min(hist):,}"
                    maxp = f"${max(hist):,}"
                except Exception:
                    minp = maxp = "-"
            else:
                minp = maxp = "-"

            prev_cell = f"${prev_price_val:,}" if prev_price_val is not None else "-"

            # Get product size for display
            product_size = getattr(good, "size", 1)
            size_cell = f"{product_size}"

            row_key = table.add_row(
                good.name,
                getattr(good, "category", "electronics"),
                size_cell,
                f"${price:,}",
                prev_cell,
                change_cell,
                minp,
                maxp,
                getattr(good, "type", "standard"),
            )
            try:
                self._row_to_product[row_key] = good.name
            except Exception:
                pass

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # Open Buy modal for the clicked product with default = max buyable now
        try:
            table = event.data_table
        except Exception:
            table = None
        if not table or getattr(table, "id", None) != "market-table":
            return
        product = self._row_to_product.get(getattr(event, "row_key", None))
        if not product:
            return
        # Compute max quantity we can buy now (cash and cargo space constraints)
        price = int(self.engine.prices.get(product, 0))
        cash = int(self.engine.state.cash)

        # Get available cargo space (accounting for product sizes)
        if hasattr(self.engine, 'cargo_service') and self.engine.cargo_service:
            available_space = self.engine.cargo_service.get_free_slots()
        else:
            # Fallback to old method
            available_space = int(self.engine.state.max_inventory - self.engine.state.get_inventory_count())

        # Get product size to calculate how many units fit
        good = self.engine.goods_service.get_good(product)
        product_size = getattr(good, "size", 1) if good else 1

        max_affordable = (cash // price) if price > 0 else 0
        max_that_fits = (available_space // product_size) if product_size > 0 else available_space
        max_buyable = min(max_affordable, max_that_fits)

        try:
            from merchant_tycoon.ui.goods.modals import BuyModal
            self.app.push_screen(BuyModal(self.engine, self.app._handle_buy, default_product=product, default_quantity=max_buyable))
        except Exception:
            pass
