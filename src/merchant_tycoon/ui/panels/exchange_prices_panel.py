from textual.app import ComposeResult
from textual.widgets import Static, Label, DataTable
from rich.text import Text

from ...engine import GameEngine
from ...models import STOCKS, COMMODITIES, CRYPTO


class ExchangePricesPanel(Static):
    """Display stock and commodity prices"""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("📈 EXCHANGE PRICES", id="exchange-prices-header", classes="panel-title")
        yield DataTable(id="exchange-table")

    def update_exchange_prices(self):
        table = self.query_one("#exchange-table", DataTable)

        # Initialize columns once
        if not getattr(self, "_exchange_table_initialized", False):
            table.clear(columns=True)
            table.add_columns("Symbol", "Name", "Price", "Change", "Have", "Type")
            try:
                table.cursor_type = "row"
                table.show_header = True
                table.zebra_stripes = True
            except Exception:
                pass
            self._exchange_table_initialized = True

        # Clear rows
        try:
            table.clear(rows=True)
        except Exception:
            table.clear()

        # Helper to add asset rows
        def add_asset_row(name: str, symbol: str, asset_type: str):
            price = self.engine.asset_prices.get(symbol, 0)
            owned = self.engine.state.portfolio.get(symbol, 0)

            change_cell = Text("─", style="dim")
            if symbol in self.engine.previous_asset_prices:
                prev_price = self.engine.previous_asset_prices[symbol]
                if prev_price > 0:
                    if price > prev_price:
                        pct = (price - prev_price) / prev_price * 100
                        change_cell = Text(f"▲ +{pct:.0f}%", style="green")
                    elif price < prev_price:
                        pct = (prev_price - price) / prev_price * 100
                        change_cell = Text(f"▼ -{pct:.0f}%", style="red")
                    else:
                        change_cell = Text("─", style="dim")

            # Format price based on asset type
            if asset_type == "crypto" and price < 10:
                price_str = f"${price:.2f}"
            else:
                price_str = f"${price:,}"

            # Display asset type
            type_display = "Stock" if asset_type == "stock" else "Commodity" if asset_type == "commodity" else "Crypto"

            table.add_row(
                symbol,
                name,
                price_str,
                change_cell,
                str(owned),
                type_display,
            )

        for stock in STOCKS:
            add_asset_row(stock.name, stock.symbol, stock.asset_type)
        for commodity in COMMODITIES:
            add_asset_row(commodity.name, commodity.symbol, commodity.asset_type)
        for crypto in CRYPTO:
            add_asset_row(crypto.name, crypto.symbol, crypto.asset_type)
