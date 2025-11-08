from textual.app import ComposeResult
from textual.widgets import Static, Label, DataTable
from rich.text import Text

from merchant_tycoon.engine import GameEngine
from merchant_tycoon.model import GOODS


class MarketPanel(Static):
    """Display market prices and buy/sell options"""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("🏪 MARKET PRICES", id="market-header", classes="panel-title")
        # Use a DataTable to present goods in a tabular format
        yield DataTable(id="market-table")

    def update_market(self):
        table = self.query_one("#market-table", DataTable)

        # Configure columns once
        if not getattr(self, "_market_table_initialized", False):
            table.clear(columns=True)
            table.add_columns("Product", "Price", "Change", "Have")
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

        for good in GOODS:
            price = self.engine.prices.get(good.name, 0)
            inventory = self.engine.state.inventory.get(good.name, 0)

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

            table.add_row(
                good.name,
                f"${price:,}",
                change_cell,
                str(inventory),
            )
