from textual.app import ComposeResult
from textual.widgets import Static, Label, DataTable
from rich.text import Text

from merchant_tycoon.engine import GameEngine
from merchant_tycoon.config import SETTINGS


class ExchangePricesPanel(Static):
    """Display stock and commodity prices"""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine
        self._row_to_symbol = {}

    def compose(self) -> ComposeResult:
        yield Label("📈 EXCHANGE PRICES", id="exchange-prices-header", classes="panel-title")
        yield DataTable(id="exchange-table")

    def update_exchange_prices(self):
        table = self.query_one("#exchange-table", DataTable)

        # Initialize columns once
        if not getattr(self, "_exchange_table_initialized", False):
            table.clear(columns=True)
            window = int(SETTINGS.pricing.history_window)
            table.add_columns(
                "Symbol",
                "Name",
                "Price",
                "Prev",
                "Change",
                f"Min ({window}d)",
                f"Max ({window}d)",
                "Type",
            )
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
        self._row_to_symbol = {}

        # Helper to add asset rows
        def add_asset_row(name: str, symbol: str, asset_type: str):
            price = self.engine.asset_prices.get(symbol, 0)
            hist = (self.engine.state.price_history or {}).get(symbol, [])[-10:]

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

            # Format previous price
            if symbol in self.engine.previous_asset_prices:
                prev_price = self.engine.previous_asset_prices[symbol]
                if asset_type == "crypto" and prev_price < 10:
                    prev_str = f"${prev_price:.2f}"
                else:
                    prev_str = f"${prev_price:,}"
            else:
                prev_str = "─"

            # Format min/max over last 10 entries
            if hist:
                try:
                    min_val = min(hist)
                    max_val = max(hist)
                    minp = f"${min_val:.2f}" if asset_type == "crypto" and min_val < 10 else f"${min_val:,}"
                    maxp = f"${max_val:.2f}" if asset_type == "crypto" and max_val < 10 else f"${max_val:,}"
                except Exception:
                    minp = maxp = "-"
            else:
                minp = maxp = "-"

            # Display asset type
            type_display = "Stock" if asset_type == "stock" else "Commodity" if asset_type == "commodity" else "Crypto"

            row_key = table.add_row(
                symbol,
                name,
                price_str,
                prev_str,
                change_cell,
                minp,
                maxp,
                type_display,
            )
            try:
                self._row_to_symbol[row_key] = symbol
            except Exception:
                pass

        # Show stocks
        try:
            stocks = self.engine.assets_repo.get_by_type("stock")
        except Exception:
            stocks = []
        for stock in stocks:
            add_asset_row(stock.name, stock.symbol, stock.asset_type)
        # Show commodities
        try:
            commodities = self.engine.assets_repo.get_by_type("commodity")
        except Exception:
            commodities = []
        for commodity in commodities:
            add_asset_row(commodity.name, commodity.symbol, commodity.asset_type)
        # Show crypto
        try:
            cryptos = self.engine.assets_repo.get_by_type("crypto")
        except Exception:
            cryptos = []
        for crypto in cryptos:
            add_asset_row(crypto.name, crypto.symbol, crypto.asset_type)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # Open BuyAsset modal with default = max affordable quantity (if unlocked)
        try:
            table = event.data_table
        except Exception:
            table = None
        if not table or getattr(table, "id", None) != "exchange-table":
            return
        symbol = self._row_to_symbol.get(getattr(event, "row_key", None))
        if not symbol:
            return

        # Check if investments are unlocked before allowing buy (read-only, unlock happens during travel)
        from merchant_tycoon.config import SETTINGS
        threshold = int(getattr(SETTINGS.investments, "min_wealth_to_unlock_trading", 0))
        unlocked = getattr(self.engine.state, "investments_unlocked", False)

        # Auto-unlock if threshold is 0
        if threshold <= 0:
            unlocked = True

        if not unlocked:
            # Show locked alert modal (modal computes its own content)
            try:
                from merchant_tycoon.ui.investments.modals import InvestmentsLockedModal
                self.app.push_screen(InvestmentsLockedModal(self.engine))
            except Exception:
                pass
            return

        # Unlocked - proceed with buy modal
        price = int(self.engine.asset_prices.get(symbol, 0))
        cash = int(self.engine.state.cash)
        try:
            max_affordable = int(self.engine.investments_service.max_affordable(cash, price))
        except Exception:
            max_affordable = int(cash // price) if price > 0 else 0
        try:
            from merchant_tycoon.ui.investments.modals import BuyAssetModal
            self.app.push_screen(BuyAssetModal(self.engine, self.app._handle_asset_trade, default_symbol=symbol, default_quantity=max_affordable))
        except Exception:
            pass
