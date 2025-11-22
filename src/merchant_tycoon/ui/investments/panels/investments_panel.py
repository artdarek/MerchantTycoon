from textual.app import ComposeResult
from textual.widgets import Static, Label, DataTable
from rich.text import Text

from merchant_tycoon.engine import GameEngine


class InvestmentsPanel(Static):
    """Display player investments (stocks and commodities)"""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine
        self._row_to_symbol = {}

    def compose(self) -> ComposeResult:
        yield Label("💼 YOUR INVESTMENTS", id="investments-header", classes="panel-title")
        yield DataTable(id="portfolio-table")

    def update_investments(self):
        table = self.query_one("#portfolio-table", DataTable)

        # Initialize columns once
        if not getattr(self, "_portfolio_table_initialized", False):
            table.clear(columns=True)
            table.add_columns("Symbol", "Name", "Qty", "Price/C", "Value/C", "Price/B/A", "Value/B", "P/L", "P/L%", "Type")
            try:
                table.cursor_type = "row"
                table.show_header = True
                table.zebra_stripes = True
            except Exception:
                pass
            self._portfolio_table_initialized = True

        # Clear existing rows
        try:
            table.clear(rows=True)
        except Exception:
            table.clear()
        self._row_to_symbol = {}

        if not self.engine.state.portfolio:
            table.add_row("(no investments)", "", "", "", "", "", "", "")
            return

        for symbol in sorted(self.engine.state.portfolio.keys()):
            quantity = self.engine.state.portfolio.get(symbol, 0)
            current_price = self.engine.asset_prices.get(symbol, 0)
            current_value = current_price * quantity

            # Calculate profit/loss from investment lots (FIFO basis)
            lots = self.engine.state.get_investment_lots_for_asset(symbol)
            total_cost = sum(lot.quantity * lot.purchase_price for lot in lots)
            avg_purchase_price = (total_cost // quantity) if quantity > 0 else 0

            profit = current_value - total_cost
            profit_pct = (profit / total_cost * 100) if total_cost > 0 else 0

            try:
                asset = self.engine.assets_repo.get_by_symbol(symbol)
            except Exception:
                asset = None
            asset_name = asset.name if asset else symbol
            asset_type = getattr(asset, "asset_type", "") if asset else ""

            # Color profit cells
            if profit > 0:
                pl_cell = Text(f"${profit:+,}", style="green")
                pl_pct_cell = Text(f"{profit_pct:+.0f}%", style="green")
            elif profit < 0:
                pl_cell = Text(f"${profit:+,}", style="red")
                pl_pct_cell = Text(f"{profit_pct:+.0f}%", style="red")
            else:
                pl_cell = Text("$0", style="dim")
                pl_pct_cell = Text("0%", style="dim")

            row_key = table.add_row(
                symbol,
                asset_name,
                str(quantity),
                f"${current_price:,}",
                f"${current_value:,}",
                f"${avg_purchase_price:,}",
                f"${total_cost:,}",
                pl_cell,
                pl_pct_cell,
                asset_type,
            )
            try:
                self._row_to_symbol[row_key] = symbol
            except Exception:
                pass

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # Open SellAsset modal with default = owned quantity
        try:
            table = event.data_table
        except Exception:
            table = None
        if not table or getattr(table, "id", None) != "portfolio-table":
            return
        symbol = self._row_to_symbol.get(getattr(event, "row_key", None))
        if not symbol:
            return
        owned = int(self.engine.state.portfolio.get(symbol, 0))
        if owned <= 0:
            return
        try:
            from merchant_tycoon.ui.investments.modals import SellAssetModal
            self.app.push_screen(SellAssetModal(self.engine, self.app._handle_asset_trade, default_symbol=symbol, default_quantity=owned))
        except Exception:
            pass
