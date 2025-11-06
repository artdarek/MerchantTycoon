from datetime import datetime
from typing import List

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Static, Label, DataTable
from rich.text import Text

from ..engine import GameEngine
from ..models import GOODS, STOCKS, COMMODITIES, CITIES


class StatsPanel(Static):
    """Display player stats"""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("", id="stats-content")

    def update_stats(self):
        state = self.engine.state
        city = CITIES[state.current_city]
        inventory_count = state.get_inventory_count()

        # Calculate total portfolio value
        portfolio_value = 0
        for symbol, quantity in state.portfolio.items():
            if symbol in self.engine.asset_prices:
                portfolio_value += quantity * self.engine.asset_prices[symbol]

        stats_text = f"""💰 Cash: ${state.cash:,}  |  💼 Investments: ${portfolio_value:,}  |  🏦 Debt: ${state.debt:,}  |  📅 Day: {state.day}  |  📍 {city.name}  |  📦 Cargo: {inventory_count}/{state.max_inventory}"""

        label = self.query_one("#stats-content", Label)
        label.update(stats_text)


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
            table.add_columns("Asset", "Price", "Change", "Have", "Type")
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

            table.add_row(
                f"{name} ({symbol})",
                f"${price:,}",
                change_cell,
                str(owned),
                "Stock" if asset_type == "stock" else "Commodity",
            )

        for stock in STOCKS:
            add_asset_row(stock.name, stock.symbol, stock.asset_type)
        for commodity in COMMODITIES:
            add_asset_row(commodity.name, commodity.symbol, commodity.asset_type)


class InvestmentsPanel(Static):
    """Display player investments (stocks and commodities)"""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("💼 YOUR INVESTMENTS", id="investments-header", classes="panel-title")
        yield DataTable(id="portfolio-table")

    def update_investments(self):
        table = self.query_one("#portfolio-table", DataTable)

        # Initialize columns once
        if not getattr(self, "_portfolio_table_initialized", False):
            table.clear(columns=True)
            table.add_columns("Symbol", "Name", "Qty", "Price", "Value", "Avg Cost", "P/L", "P/L%")
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

        if not self.engine.state.portfolio:
            table.add_row("(no investments)", "", "", "", "", "", "", "")
            return

        all_assets = STOCKS + COMMODITIES

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

            asset = next((a for a in all_assets if a.symbol == symbol), None)
            asset_name = asset.name if asset else symbol

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

            table.add_row(
                symbol,
                asset_name,
                str(quantity),
                f"${current_price:,}",
                f"${current_value:,}",
                f"${avg_purchase_price:,}",
                pl_cell,
                pl_pct_cell,
            )


class MessageLog(Static):
    """Display game messages"""

    def __init__(self):
        super().__init__()
        # Start with a welcome message tagged with time and the starting day
        ts = datetime.now().strftime("%H:%M:%S")
        self.messages: List[str] = [f"[{ts}] Day 1: Welcome to Merchant Tycoon!"]

    def compose(self) -> ComposeResult:
        yield Label("📜 MESSAGES", id="log-header", classes="panel-title")
        yield ScrollableContainer(id="log-content")

    def add_message(self, msg: str):
        self.messages.insert(0, msg)  # Add new messages at the beginning
        if len(self.messages) > 10:
            self.messages = self.messages[:10]  # Keep first 10 (newest)
        self._update_display()

    def _update_display(self):
        container = self.query_one("#log-content", ScrollableContainer)
        container.remove_children()
        for msg in self.messages:
            container.mount(Label(msg))
