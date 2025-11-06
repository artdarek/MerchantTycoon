from datetime import datetime
from typing import List

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Static, Label

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
        yield Label("🏪 MARKET PRICES", id="market-header")
        yield ScrollableContainer(id="market-list")

    def update_market(self):
        container = self.query_one("#market-list", ScrollableContainer)
        container.remove_children()

        for good in GOODS:
            price = self.engine.prices[good.name]
            inventory = self.engine.state.inventory.get(good.name, 0)

            # Get price trend indicator
            trend = ""
            if good.name in self.engine.previous_prices:
                prev_price = self.engine.previous_prices[good.name]
                if price > prev_price:
                    change_pct = ((price - prev_price) / prev_price * 100) if prev_price > 0 else 0
                    trend = f" [green]▲+{change_pct:.0f}%[/green]"  # Price increased (good for selling)
                elif price < prev_price:
                    change_pct = ((prev_price - price) / prev_price * 100) if prev_price > 0 else 0
                    trend = f" [red]▼-{change_pct:.0f}%[/red]"  # Price decreased (good for buying)
                else:
                    trend = " [dim]─[/dim]"  # Price unchanged

            line = Label(f"{good.name:12} ${price:5}{trend:10}  (have: {inventory})", markup=True)
            container.mount(line)


class InventoryPanel(Static):
    """Display player inventory"""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("📦 YOUR INVENTORY", id="inventory-header")
        yield ScrollableContainer(id="inventory-list")

    def update_inventory(self):
        container = self.query_one("#inventory-list", ScrollableContainer)
        container.remove_children()

        if not self.engine.state.inventory:
            container.mount(Label("(empty)"))
        else:
            for good_name, quantity in sorted(self.engine.state.inventory.items()):
                current_price = self.engine.prices[good_name]
                current_value = current_price * quantity

                # Calculate profit/loss from purchase lots
                lots = self.engine.state.get_lots_for_good(good_name)
                total_cost = sum(lot.quantity * lot.purchase_price for lot in lots)

                profit = current_value - total_cost
                profit_pct = (profit / total_cost * 100) if total_cost > 0 else 0

                # Format profit indicator
                if profit > 0:
                    profit_str = f"[green]▲+${profit:,} (+{profit_pct:.0f}%)[/green]"
                elif profit < 0:
                    profit_str = f"[red]▼${profit:,} ({profit_pct:.0f}%)[/red]"
                else:
                    profit_str = "[dim]─$0[/dim]"

                line = Label(
                    f"{good_name:12} x{quantity:3}  ${current_value:,} {profit_str}",
                    markup=True
                )
                container.mount(line)


class ExchangePricesPanel(Static):
    """Display stock and commodity prices"""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("📈 EXCHANGE PRICES", id="exchange-prices-header")
        yield ScrollableContainer(id="exchange-prices-list")

    def update_exchange_prices(self):
        container = self.query_one("#exchange-prices-list", ScrollableContainer)
        container.remove_children()

        # Display stocks
        container.mount(Label("[bold]Stocks:[/bold]", markup=True))
        for stock in STOCKS:
            price = self.engine.asset_prices[stock.symbol]
            owned = self.engine.state.portfolio.get(stock.symbol, 0)

            # Get price trend indicator
            trend = ""
            if stock.symbol in self.engine.previous_asset_prices:
                prev_price = self.engine.previous_asset_prices[stock.symbol]
                if price > prev_price:
                    change_pct = ((price - prev_price) / prev_price * 100) if prev_price > 0 else 0
                    trend = f" [green]▲+{change_pct:.0f}%[/green]"
                elif price < prev_price:
                    change_pct = ((prev_price - price) / prev_price * 100) if prev_price > 0 else 0
                    trend = f" [red]▼-{change_pct:.0f}%[/red]"
                else:
                    trend = " [dim]─[/dim]"

            name_col = f"{stock.name} ({stock.symbol})"
            line = Label(f"{name_col:20} ${price:6,}{trend:20} own: {owned:3}", markup=True)
            container.mount(line)

        # Add spacing
        container.mount(Label(""))

        # Display commodities
        container.mount(Label("[bold]Commodities:[/bold]", markup=True))
        for commodity in COMMODITIES:
            price = self.engine.asset_prices[commodity.symbol]
            owned = self.engine.state.portfolio.get(commodity.symbol, 0)

            # Get price trend indicator
            trend = ""
            if commodity.symbol in self.engine.previous_asset_prices:
                prev_price = self.engine.previous_asset_prices[commodity.symbol]
                if price > prev_price:
                    change_pct = ((price - prev_price) / prev_price * 100) if prev_price > 0 else 0
                    trend = f" [green]▲+{change_pct:.0f}%[/green]"
                elif price < prev_price:
                    change_pct = ((prev_price - price) / prev_price * 100) if prev_price > 0 else 0
                    trend = f" [red]▼-{change_pct:.0f}%[/red]"
                else:
                    trend = " [dim]─[/dim]"

            name_col = f"{commodity.name} ({commodity.symbol})"
            line = Label(f"{name_col:20} ${price:6,}{trend:20} own: {owned:3}", markup=True)
            container.mount(line)


class InvestmentsPanel(Static):
    """Display player investments (stocks and commodities)"""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("💼 YOUR INVESTMENTS", id="investments-header")
        yield ScrollableContainer(id="investments-list")

    def update_investments(self):
        container = self.query_one("#investments-list", ScrollableContainer)
        container.remove_children()

        if not self.engine.state.portfolio:
            container.mount(Label("(no investments)"))
        else:
            for symbol in sorted(self.engine.state.portfolio.keys()):
                quantity = self.engine.state.portfolio[symbol]
                current_price = self.engine.asset_prices[symbol]
                current_value = current_price * quantity

                # Calculate profit/loss from investment lots
                lots = self.engine.state.get_investment_lots_for_asset(symbol)
                total_cost = sum(lot.quantity * lot.purchase_price for lot in lots)
                avg_purchase_price = total_cost // quantity if quantity > 0 else 0

                profit = current_value - total_cost
                profit_pct = (profit / total_cost * 100) if total_cost > 0 else 0

                # Find asset info
                all_assets = STOCKS + COMMODITIES
                asset = next((a for a in all_assets if a.symbol == symbol), None)
                asset_name = asset.name if asset else symbol
                asset_icon = "📊" if asset and asset.asset_type == "stock" else "🌾"

                # Format profit indicator
                if profit > 0:
                    profit_str = f"[green]▲+${profit:,} (+{profit_pct:.0f}%)[/green]"
                elif profit < 0:
                    profit_str = f"[red]▼${profit:,} ({profit_pct:.0f}%)[/red]"
                else:
                    profit_str = "[dim]─$0[/dim]"

                line = Label(
                    f"{asset_icon} {symbol:6} {asset_name:16} x{quantity:3}  ${current_value:,} {profit_str}",
                    markup=True
                )
                container.mount(line)


class MessageLog(Static):
    """Display game messages"""

    def __init__(self):
        super().__init__()
        # Start with a welcome message tagged with time and the starting day
        ts = datetime.now().strftime("%H:%M:%S")
        self.messages: List[str] = [f"[{ts}] Day 1: Welcome to Merchant Tycoon!"]

    def compose(self) -> ComposeResult:
        yield Label("📜 MESSAGES", id="log-header")
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
