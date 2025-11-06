#!/usr/bin/env python3
"""
Merchant Tycoon - A terminal-based trading game
Buy low, sell high, travel between cities, manage loans, survive random events!
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static, Label, Button, Input, Select, OptionList
from textual.widgets.option_list import Option
from textual.binding import Binding
from textual.screen import ModalScreen
from textual import events


# Game Data Models
@dataclass
class Good:
    """Represents a tradeable good"""
    name: str
    base_price: int
    price_variance: float = 0.3  # 30% variance


@dataclass
class PurchaseLot:
    """Represents a batch of goods purchased at a specific price"""
    good_name: str
    quantity: int
    purchase_price: int  # Price per unit
    day: int
    city: str


@dataclass
class Transaction:
    """Represents a transaction (buy or sell)"""
    transaction_type: str  # "buy" or "sell"
    good_name: str
    quantity: int
    price_per_unit: int
    total_value: int
    day: int
    city: str


GOODS = [
    Good("TV", 800),
    Good("Computer", 1200),
    Good("Printer", 300),
    Good("Phone", 600),
    Good("Camera", 400),
    Good("Laptop", 1500),
    Good("Tablet", 500),
    Good("Console", 450),
]


@dataclass
class Asset:
    """Represents a stock or commodity"""
    name: str
    symbol: str
    base_price: int
    price_variance: float = 0.5  # 50% variance (more volatile than goods)
    asset_type: str = "stock"  # "stock" or "commodity"


STOCKS = [
    Asset("Google", "GOOGL", 150, 0.6, "stock"),
    Asset("Meta", "META", 80, 0.5, "stock"),
    Asset("Apple", "AAPL", 120, 0.7, "stock"),
    Asset("Microsoft", "MSFT", 200, 0.4, "stock"),
]

COMMODITIES = [
    Asset("Gold", "GOLD", 1800, 0.3, "commodity"),
    Asset("Oil", "OIL", 75, 0.8, "commodity"),
    Asset("Silver", "SILV", 25, 0.4, "commodity"),
    Asset("Copper", "COPP", 8, 0.5, "commodity"),
]


@dataclass
class InvestmentLot:
    """Represents a batch of stocks/commodities purchased at a specific price"""
    asset_symbol: str
    quantity: int
    purchase_price: int
    day: int


@dataclass
class City:
    """Represents a city/location"""
    name: str
    price_multiplier: Dict[str, float]  # Per-good multipliers


CITIES = [
    City("Warsaw", {"TV": 1.0, "Computer": 1.0, "Printer": 1.0, "Phone": 1.0,
          "Camera": 1.0, "Laptop": 1.0, "Tablet": 1.0, "Console": 1.0}),
    City("Berlin", {"TV": 0.8, "Computer": 1.2, "Printer": 0.9, "Phone": 1.1,
          "Camera": 0.85, "Laptop": 1.15, "Tablet": 0.95, "Console": 1.05}),
    City("Prague", {"TV": 1.1, "Computer": 0.9, "Printer": 1.2, "Phone": 0.95,
          "Camera": 1.1, "Laptop": 0.85, "Tablet": 1.05, "Console": 0.9}),
    City("Vienna", {"TV": 0.95, "Computer": 1.1, "Printer": 0.85, "Phone": 1.2,
          "Camera": 1.0, "Laptop": 1.05, "Tablet": 1.1, "Console": 0.95}),
    City("Budapest", {"TV": 1.2, "Computer": 0.85, "Printer": 1.1, "Phone": 0.9,
          "Camera": 1.15, "Laptop": 0.9, "Tablet": 0.85, "Console": 1.1}),
]


@dataclass
class GameState:
    """Player's game state"""
    cash: int = 5000
    debt: int = 0
    day: int = 1
    current_city: int = 0
    inventory: Dict[str, int] = field(default_factory=dict)
    max_inventory: int = 50
    purchase_lots: List[PurchaseLot] = field(default_factory=list)
    transaction_history: List[Transaction] = field(default_factory=list)
    # Investment portfolio
    portfolio: Dict[str, int] = field(default_factory=dict)  # {symbol: quantity}
    investment_lots: List[InvestmentLot] = field(default_factory=list)

    def get_inventory_count(self) -> int:
        return sum(self.inventory.values())

    def can_carry(self, amount: int = 1) -> bool:
        return self.get_inventory_count() + amount <= self.max_inventory

    def get_lots_for_good(self, good_name: str) -> List[PurchaseLot]:
        """Get all purchase lots for a specific good"""
        return [lot for lot in self.purchase_lots if lot.good_name == good_name]

    def get_investment_lots_for_asset(self, symbol: str) -> List[InvestmentLot]:
        """Get all investment lots for a specific asset"""
        return [lot for lot in self.investment_lots if lot.asset_symbol == symbol]


class GameEngine:
    """Core game logic"""

    def __init__(self):
        self.state = GameState()
        self.prices: Dict[str, int] = {}
        self.previous_prices: Dict[str, int] = {}
        self.asset_prices: Dict[str, int] = {}
        self.previous_asset_prices: Dict[str, int] = {}
        self.generate_prices()
        self.generate_asset_prices()
        self.interest_rate = 0.10  # 10% per day

    def generate_prices(self):
        """Generate random prices for current city"""
        # Save previous prices before generating new ones
        self.previous_prices = self.prices.copy()

        city = CITIES[self.state.current_city]
        for good in GOODS:
            variance = random.uniform(1 - good.price_variance, 1 + good.price_variance)
            city_mult = city.price_multiplier[good.name]
            self.prices[good.name] = int(good.base_price * city_mult * variance)

    def generate_asset_prices(self):
        """Generate random prices for stocks and commodities"""
        # Save previous prices
        self.previous_asset_prices = self.asset_prices.copy()

        # Generate prices for all assets
        all_assets = STOCKS + COMMODITIES
        for asset in all_assets:
            variance = random.uniform(1 - asset.price_variance, 1 + asset.price_variance)
            self.asset_prices[asset.symbol] = int(asset.base_price * variance)

    def buy(self, good_name: str, quantity: int) -> tuple[bool, str]:
        """Buy goods"""
        if good_name not in self.prices:
            return False, "Invalid item"

        price = self.prices[good_name]
        total_cost = price * quantity

        if total_cost > self.state.cash:
            return False, f"Not enough cash! Need ${total_cost}, have ${self.state.cash}"

        if not self.state.can_carry(quantity):
            available = self.state.max_inventory - self.state.get_inventory_count()
            return False, f"Not enough space! Only {available} slots available"

        self.state.cash -= total_cost
        self.state.inventory[good_name] = self.state.inventory.get(good_name, 0) + quantity

        # Record purchase lot
        city_name = CITIES[self.state.current_city].name
        lot = PurchaseLot(
            good_name=good_name,
            quantity=quantity,
            purchase_price=price,
            day=self.state.day,
            city=city_name
        )
        self.state.purchase_lots.append(lot)

        # Record transaction
        transaction = Transaction(
            transaction_type="buy",
            good_name=good_name,
            quantity=quantity,
            price_per_unit=price,
            total_value=total_cost,
            day=self.state.day,
            city=city_name
        )
        self.state.transaction_history.append(transaction)

        return True, f"Bought {quantity}x {good_name} for ${total_cost}"

    def sell(self, good_name: str, quantity: int) -> tuple[bool, str]:
        """Sell goods using FIFO (First In, First Out) strategy"""
        if good_name not in self.state.inventory or self.state.inventory[good_name] < quantity:
            have = self.state.inventory.get(good_name, 0)
            return False, f"Don't have enough! Have {have}x {good_name}"

        price = self.prices[good_name]
        total_value = price * quantity

        # Deduct from purchase lots using FIFO
        remaining_to_sell = quantity
        lots_to_remove = []
        for i, lot in enumerate(self.state.purchase_lots):
            if lot.good_name == good_name and remaining_to_sell > 0:
                if lot.quantity <= remaining_to_sell:
                    # Sell entire lot
                    remaining_to_sell -= lot.quantity
                    lots_to_remove.append(i)
                else:
                    # Partial sell from this lot
                    lot.quantity -= remaining_to_sell
                    remaining_to_sell = 0
                    break

        # Remove fully sold lots (in reverse order to maintain indices)
        for i in reversed(lots_to_remove):
            self.state.purchase_lots.pop(i)

        self.state.cash += total_value
        self.state.inventory[good_name] -= quantity
        if self.state.inventory[good_name] == 0:
            del self.state.inventory[good_name]

        # Record transaction
        city_name = CITIES[self.state.current_city].name
        transaction = Transaction(
            transaction_type="sell",
            good_name=good_name,
            quantity=quantity,
            price_per_unit=price,
            total_value=total_value,
            day=self.state.day,
            city=city_name
        )
        self.state.transaction_history.append(transaction)

        return True, f"Sold {quantity}x {good_name} for ${total_value}"

    def travel(self, city_index: int) -> tuple[bool, str, Optional[str]]:
        """Travel to a new city"""
        if city_index == self.state.current_city:
            return False, "Already in this city!", None

        self.state.current_city = city_index
        self.state.day += 1

        # Apply interest if there's debt
        if self.state.debt > 0:
            interest = int(self.state.debt * self.interest_rate)
            self.state.debt += interest

        # Random event (only affects goods, not investments!)
        event_msg = self._random_event()

        # Generate new prices for goods and assets
        self.generate_prices()
        self.generate_asset_prices()

        return True, f"Traveled to {CITIES[city_index].name}", event_msg

    def _random_event(self) -> Optional[str]:
        """Generate random travel events"""
        event_chance = random.random()

        if event_chance < 0.15:  # 15% chance of bad event
            event_type = random.choice(['robbery', 'confiscation', 'damage'])

            if event_type == 'robbery' and self.state.inventory:
                # Lose random goods
                good = random.choice(list(self.state.inventory.keys()))
                lost = random.randint(1, max(1, self.state.inventory[good] // 2))
                self.state.inventory[good] -= lost
                if self.state.inventory[good] <= 0:
                    del self.state.inventory[good]
                return f"🚨 ROBBED! Lost {lost}x {good}!"

            elif event_type == 'confiscation' and self.state.inventory:
                # Lose all of one type
                good = random.choice(list(self.state.inventory.keys()))
                lost = self.state.inventory[good]
                del self.state.inventory[good]
                return f"🚔 CONFISCATED! Lost all {lost}x {good}!"

            elif event_type == 'damage':
                damage = random.randint(100, 500)
                self.state.cash -= damage
                return f"💥 ACCIDENT! Paid ${damage} in damages!"

        elif event_chance < 0.20:  # 5% chance of good event
            bonus = random.randint(200, 800)
            self.state.cash += bonus
            return f"✨ LUCKY FIND! Found ${bonus}!"

        return None

    def take_loan(self, amount: int) -> tuple[bool, str]:
        """Take a loan from the bank"""
        if amount <= 0:
            return False, "Invalid loan amount"
        if amount > 10000:
            return False, "Maximum loan is $10,000"

        self.state.cash += amount
        self.state.debt += amount
        return True, f"Loan approved! Received ${amount} (10% daily interest)"

    def repay_loan(self, amount: int) -> tuple[bool, str]:
        """Repay loan"""
        if amount <= 0:
            return False, "Invalid amount"
        if amount > self.state.cash:
            return False, f"Not enough cash! Have ${self.state.cash}"
        if amount > self.state.debt:
            return False, f"Debt is only ${self.state.debt}"

        self.state.cash -= amount
        self.state.debt -= amount
        return True, f"Paid ${amount} towards debt. Remaining: ${self.state.debt}"

    def buy_asset(self, symbol: str, quantity: int) -> tuple[bool, str]:
        """Buy stocks or commodities"""
        if symbol not in self.asset_prices:
            return False, "Invalid asset"

        price = self.asset_prices[symbol]
        total_cost = price * quantity

        if total_cost > self.state.cash:
            return False, f"Not enough cash! Need ${total_cost:,}, have ${self.state.cash:,}"

        if quantity <= 0:
            return False, "Quantity must be positive"

        self.state.cash -= total_cost
        self.state.portfolio[symbol] = self.state.portfolio.get(symbol, 0) + quantity

        # Record investment lot
        lot = InvestmentLot(
            asset_symbol=symbol,
            quantity=quantity,
            purchase_price=price,
            day=self.state.day
        )
        self.state.investment_lots.append(lot)

        return True, f"Bought {quantity}x {symbol} for ${total_cost:,}"

    def sell_asset(self, symbol: str, quantity: int) -> tuple[bool, str]:
        """Sell stocks or commodities using FIFO"""
        if symbol not in self.state.portfolio or self.state.portfolio[symbol] < quantity:
            have = self.state.portfolio.get(symbol, 0)
            return False, f"Don't have enough! Have {have}x {symbol}"

        if quantity <= 0:
            return False, "Quantity must be positive"

        price = self.asset_prices[symbol]
        total_value = price * quantity

        # Deduct from investment lots using FIFO
        remaining_to_sell = quantity
        lots_to_remove = []
        for i, lot in enumerate(self.state.investment_lots):
            if lot.asset_symbol == symbol and remaining_to_sell > 0:
                if lot.quantity <= remaining_to_sell:
                    remaining_to_sell -= lot.quantity
                    lots_to_remove.append(i)
                else:
                    lot.quantity -= remaining_to_sell
                    remaining_to_sell = 0
                    break

        # Remove fully sold lots
        for i in reversed(lots_to_remove):
            self.state.investment_lots.pop(i)

        self.state.cash += total_value
        self.state.portfolio[symbol] -= quantity
        if self.state.portfolio[symbol] == 0:
            del self.state.portfolio[symbol]

        return True, f"Sold {quantity}x {symbol} for ${total_value:,}"


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
        self.messages: List[str] = ["Welcome to Merchant Tycoon!"]

    def compose(self) -> ComposeResult:
        yield Label("📜 LOG", id="log-header")
        yield ScrollableContainer(id="log-content")

    def add_message(self, msg: str):
        self.messages.append(msg)
        if len(self.messages) > 10:
            self.messages = self.messages[-10:]
        self._update_display()

    def _update_display(self):
        container = self.query_one("#log-content", ScrollableContainer)
        container.remove_children()
        for msg in self.messages:
            container.mount(Label(msg))


class InputModal(ModalScreen):
    """Generic input modal"""

    def __init__(self, title: str, prompt: str, callback):
        super().__init__()
        self.modal_title = title
        self.modal_prompt = prompt
        self.callback = callback

    def compose(self) -> ComposeResult:
        with Container(id="input-modal"):
            yield Label(self.modal_title, id="modal-title")
            yield Label(self.modal_prompt)
            yield Input(placeholder="Enter value...", id="modal-input")
            with Horizontal(id="modal-buttons"):
                yield Button("Confirm", variant="primary", id="confirm-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            input_widget = self.query_one("#modal-input", Input)
            value = input_widget.value.strip()
            self.dismiss()
            if value:
                self.callback(value)
        else:
            self.dismiss()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        self.dismiss()
        if value:
            self.callback(value)


class CitySelectModal(ModalScreen):
    """City selection modal"""

    def __init__(self, cities: List[City], current_city: int, callback):
        super().__init__()
        self.cities = cities
        self.current_city = current_city
        self.callback = callback

    def compose(self) -> ComposeResult:
        with Container(id="city-modal"):
            yield Label("🗺️  Select Destination", id="modal-title")
            options = []
            for i, city in enumerate(self.cities):
                if i == self.current_city:
                    options.append(Option(f"{city.name} (current)", id=str(i), disabled=True))
                else:
                    options.append(Option(city.name, id=str(i)))
            yield OptionList(*options, id="city-list")
            yield Button("Cancel", variant="default", id="cancel-btn")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        city_index = int(event.option.id)
        self.dismiss()
        self.callback(city_index)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()


class BuyModal(ModalScreen):
    """Modal for buying goods with product selector and quantity input"""

    def __init__(self, engine: GameEngine, callback):
        super().__init__()
        self.engine = engine
        self.callback = callback

    def compose(self) -> ComposeResult:
        with Container(id="buy-modal"):
            yield Label("🛒 Buy Goods", id="modal-title")

            # Create select options with prices and max quantity
            options = []
            available_space = self.engine.state.max_inventory - self.engine.state.get_inventory_count()

            for good in GOODS:
                price = self.engine.prices[good.name]
                # Calculate max affordable based on cash
                max_affordable = self.engine.state.cash // price if price > 0 else 0
                # Calculate actual max (limited by inventory space)
                max_buyable = min(max_affordable, available_space)

                options.append((
                    f"{good.name} - ${price:,} (max: {max_buyable})",
                    good.name
                ))

            yield Label("Select product:")
            yield Select(options, prompt="Choose a product...", id="product-select")
            yield Label("Enter quantity:")
            yield Input(placeholder="Quantity...", type="integer", id="quantity-input")

            with Horizontal(id="modal-buttons"):
                yield Button("Buy", variant="primary", id="confirm-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            select_widget = self.query_one("#product-select", Select)
            input_widget = self.query_one("#quantity-input", Input)

            product = select_widget.value
            quantity_str = input_widget.value.strip()

            self.dismiss()

            if product and quantity_str:
                try:
                    quantity = int(quantity_str)
                    self.callback(product, quantity)
                except ValueError:
                    pass
        else:
            self.dismiss()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # Trigger buy on Enter key
        select_widget = self.query_one("#product-select", Select)
        product = select_widget.value

        try:
            quantity = int(event.value.strip())
            self.dismiss()
            if product:
                self.callback(product, quantity)
        except ValueError:
            pass


class SellModal(ModalScreen):
    """Modal for selling goods with product selector and quantity input"""

    def __init__(self, engine: GameEngine, callback):
        super().__init__()
        self.engine = engine
        self.callback = callback

    def compose(self) -> ComposeResult:
        with Container(id="sell-modal"):
            yield Label("💵 Sell Goods", id="modal-title")

            # Create select options with inventory and prices
            options = []
            for good_name, quantity in self.engine.state.inventory.items():
                price = self.engine.prices[good_name]
                total_value = quantity * price
                options.append((
                    f"{good_name} - ${price:,}/unit (have: {quantity}, worth ${total_value:,})",
                    good_name
                ))

            yield Label("Select product to sell:")
            yield Select(options, prompt="Choose a product...", id="product-select")
            yield Label("Enter quantity to sell:")
            yield Input(placeholder="Quantity...", type="integer", id="quantity-input")

            with Horizontal(id="modal-buttons"):
                yield Button("Sell", variant="primary", id="confirm-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            select_widget = self.query_one("#product-select", Select)
            input_widget = self.query_one("#quantity-input", Input)

            product = select_widget.value
            quantity_str = input_widget.value.strip()

            self.dismiss()

            if product and quantity_str:
                try:
                    quantity = int(quantity_str)
                    self.callback(product, quantity)
                except ValueError:
                    pass
        else:
            self.dismiss()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # Trigger sell on Enter key
        select_widget = self.query_one("#product-select", Select)
        product = select_widget.value

        try:
            quantity = int(event.value.strip())
            self.dismiss()
            if product:
                self.callback(product, quantity)
        except ValueError:
            pass


class InventoryDetailsModal(ModalScreen):
    """Modal showing detailed inventory with purchase lots and profit/loss"""

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
    ]

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        with Vertical(id="inventory-details-modal"):
            yield Label("📊 INVENTORY DETAILS", id="modal-title")
            yield Label("Use ↑↓ or mouse wheel to scroll", id="details-instructions")
            yield ScrollableContainer(id="details-content")
            yield Button("Close (ESC)", variant="primary", id="close-btn")

    def on_mount(self) -> None:
        self._update_details()

    def _update_details(self):
        try:
            container = self.query_one("#details-content", ScrollableContainer)
            container.remove_children()

            if not self.engine.state.inventory:
                container.mount(Label("No goods in inventory"))
                return

            for good_name in sorted(self.engine.state.inventory.keys()):
                total_qty = self.engine.state.inventory.get(good_name, 0)
                current_price = self.engine.prices.get(good_name, 0)
                lots = self.engine.state.get_lots_for_good(good_name)

                # Header for this good
                container.mount(Label(""))  # Empty line
                container.mount(Label(f" {good_name} ", classes="section-header"))
                container.mount(Label(""))
                container.mount(Label(f"  Total owned: {total_qty} units"))
                container.mount(Label(f"  Market price: ${current_price:,}"))
                container.mount(Label(""))

                if not lots:
                    container.mount(Label("  (No purchase history available)"))
                    container.mount(Label(""))
                else:
                    # Calculate total profit/loss
                    total_invested = sum(lot.quantity * lot.purchase_price for lot in lots)
                    total_current_value = total_qty * current_price
                    total_profit = total_current_value - total_invested
                    total_profit_pct = (total_profit / total_invested * 100) if total_invested > 0 else 0

                    profit_symbol = "📈" if total_profit > 0 else "📉" if total_profit < 0 else "➖"
                    container.mount(Label(
                        f"  {profit_symbol} Total P/L: ${total_profit:+,} ({total_profit_pct:+.1f}%)"
                    ))
                    container.mount(Label(""))
                    container.mount(Label("  Purchase History (FIFO order):"))

                    for i, lot in enumerate(lots, 1):
                        profit_per_unit = current_price - lot.purchase_price
                        lot_profit = profit_per_unit * lot.quantity
                        lot_profit_pct = (profit_per_unit / lot.purchase_price * 100) if lot.purchase_price > 0 else 0

                        profit_symbol = "📈" if profit_per_unit > 0 else "📉" if profit_per_unit < 0 else "➖"

                        container.mount(Label(""))
                        container.mount(Label(
                            f"    [{i}] {lot.quantity}x @ ${lot.purchase_price:,}/unit = ${lot.quantity * lot.purchase_price:,}",
                            classes="lot-info"
                        ))
                        container.mount(Label(
                            f"        Bought: Day {lot.day} in {lot.city}",
                            classes="lot-info"
                        ))
                        container.mount(Label(
                            f"        {profit_symbol} If sold now: ${profit_per_unit:+,}/unit "
                            f"({lot_profit_pct:+.1f}%) = ${lot_profit:+,}",
                            classes="profit-info"
                        ))
                    container.mount(Label(""))
        except Exception as e:
            # If there's any error, show a simple error message
            try:
                container = self.query_one("#details-content", ScrollableContainer)
                container.remove_children()
                container.mount(Label(f"Error loading details: {str(e)}"))
            except:
                pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-btn":
            self.dismiss()

    def action_dismiss_modal(self) -> None:
        """Close the modal when ESC is pressed"""
        self.dismiss()


class ExchangeModal(ModalScreen):
    """Modal for trading stocks and commodities"""

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
    ]

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        with Vertical(id="exchange-modal"):
            yield Label("📈 STOCK EXCHANGE", id="modal-title")
            yield Label("Trade stocks & commodities (safe from random events!)", id="exchange-subtitle")

            with Horizontal(id="exchange-actions"):
                yield Button("Buy", variant="success", id="buy-asset-btn")
                yield Button("Sell", variant="error", id="sell-asset-btn")

            yield ScrollableContainer(id="exchange-content")
            yield Button("Close (ESC)", variant="primary", id="close-btn")

    def on_mount(self) -> None:
        self._update_exchange()

    def _update_exchange(self):
        container = self.query_one("#exchange-content", ScrollableContainer)
        container.remove_children()

        # Stocks section
        container.mount(Label(""))
        container.mount(Label(" 📊 STOCKS ", classes="section-header"))
        container.mount(Label(""))

        for stock in STOCKS:
            price = self.engine.asset_prices[stock.symbol]
            owned = self.engine.state.portfolio.get(stock.symbol, 0)

            # Price trend
            trend = ""
            if stock.symbol in self.engine.previous_asset_prices:
                prev = self.engine.previous_asset_prices[stock.symbol]
                if price > prev:
                    change = ((price - prev) / prev * 100)
                    trend = f" [green]▲+{change:.0f}%[/green]"
                elif price < prev:
                    change = ((prev - price) / prev * 100)
                    trend = f" [red]▼-{change:.0f}%[/red]"
                else:
                    trend = " [dim]─[/dim]"

            # Profit/loss if owned
            profit_str = ""
            if owned > 0:
                lots = self.engine.state.get_investment_lots_for_asset(stock.symbol)
                cost = sum(lot.quantity * lot.purchase_price for lot in lots)
                value = owned * price
                profit = value - cost
                profit_pct = (profit / cost * 100) if cost > 0 else 0

                if profit > 0:
                    profit_str = f" [green]▲+${profit:,} (+{profit_pct:.0f}%)[/green]"
                elif profit < 0:
                    profit_str = f" [red]▼${profit:,} ({profit_pct:.0f}%)[/red]"

            container.mount(Label(
                f"{stock.symbol:6} {stock.name:16} ${price:6,}{trend:12}  own: {owned:4}{profit_str}",
                markup=True
            ))

        # Commodities section
        container.mount(Label(""))
        container.mount(Label(""))
        container.mount(Label(" 🌾 COMMODITIES ", classes="section-header"))
        container.mount(Label(""))

        for commodity in COMMODITIES:
            price = self.engine.asset_prices[commodity.symbol]
            owned = self.engine.state.portfolio.get(commodity.symbol, 0)

            # Price trend
            trend = ""
            if commodity.symbol in self.engine.previous_asset_prices:
                prev = self.engine.previous_asset_prices[commodity.symbol]
                if price > prev:
                    change = ((price - prev) / prev * 100)
                    trend = f" [green]▲+{change:.0f}%[/green]"
                elif price < prev:
                    change = ((prev - price) / prev * 100)
                    trend = f" [red]▼-{change:.0f}%[/red]"
                else:
                    trend = " [dim]─[/dim]"

            # Profit/loss if owned
            profit_str = ""
            if owned > 0:
                lots = self.engine.state.get_investment_lots_for_asset(commodity.symbol)
                cost = sum(lot.quantity * lot.purchase_price for lot in lots)
                value = owned * price
                profit = value - cost
                profit_pct = (profit / cost * 100) if cost > 0 else 0

                if profit > 0:
                    profit_str = f" [green]▲+${profit:,} (+{profit_pct:.0f}%)[/green]"
                elif profit < 0:
                    profit_str = f" [red]▼${profit:,} ({profit_pct:.0f}%)[/red]"

            container.mount(Label(
                f"{commodity.symbol:6} {commodity.name:16} ${price:6,}{trend:12}  own: {owned:4}{profit_str}",
                markup=True
            ))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-btn":
            self.dismiss()
        elif event.button.id == "buy-asset-btn":
            self.app.push_screen(BuyAssetModal(self.engine, self._handle_trade))
        elif event.button.id == "sell-asset-btn":
            if not self.engine.state.portfolio:
                self.app.game_log("No assets to sell!")
            else:
                self.app.push_screen(SellAssetModal(self.engine, self._handle_trade))

    def _handle_trade(self, msg: str):
        """Refresh exchange after trade and display message"""
        self._update_exchange()
        self.app.game_log(msg)
        self.app.refresh_all()

    def action_dismiss_modal(self) -> None:
        self.dismiss()


class BuyAssetModal(ModalScreen):
    """Modal for buying stocks/commodities"""

    def __init__(self, engine: GameEngine, callback):
        super().__init__()
        self.engine = engine
        self.callback = callback

    def compose(self) -> ComposeResult:
        with Container(id="buy-modal"):
            yield Label("💰 Buy Assets", id="modal-title")

            options = []
            all_assets = STOCKS + COMMODITIES
            for asset in all_assets:
                price = self.engine.asset_prices[asset.symbol]
                max_affordable = self.engine.state.cash // price if price > 0 else 0
                asset_type_icon = "📊" if asset.asset_type == "stock" else "🌾"

                options.append((
                    f"{asset_type_icon} {asset.symbol} - {asset.name} @ ${price:,} (max: {max_affordable})",
                    asset.symbol
                ))

            yield Label("Select asset:")
            yield Select(options, prompt="Choose an asset...", id="asset-select")
            yield Label("Enter quantity:")
            yield Input(placeholder="Quantity...", type="integer", id="quantity-input")

            with Horizontal(id="modal-buttons"):
                yield Button("Buy", variant="primary", id="confirm-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            select_widget = self.query_one("#asset-select", Select)
            input_widget = self.query_one("#quantity-input", Input)

            symbol = select_widget.value
            quantity_str = input_widget.value.strip()

            self.dismiss()

            if symbol and quantity_str:
                try:
                    quantity = int(quantity_str)
                    success, msg = self.engine.buy_asset(symbol, quantity)
                    self.callback(msg)
                except ValueError:
                    pass
        else:
            self.dismiss()


class SellAssetModal(ModalScreen):
    """Modal for selling stocks/commodities"""

    def __init__(self, engine: GameEngine, callback):
        super().__init__()
        self.engine = engine
        self.callback = callback

    def compose(self) -> ComposeResult:
        with Container(id="sell-modal"):
            yield Label("💵 Sell Assets", id="modal-title")

            options = []
            for symbol, quantity in self.engine.state.portfolio.items():
                price = self.engine.asset_prices[symbol]
                total_value = quantity * price

                # Find asset info
                all_assets = STOCKS + COMMODITIES
                asset = next((a for a in all_assets if a.symbol == symbol), None)
                asset_type_icon = "📊" if asset and asset.asset_type == "stock" else "🌾"
                asset_name = asset.name if asset else symbol

                options.append((
                    f"{asset_type_icon} {symbol} - {asset_name} @ ${price:,}/unit (have: {quantity}, worth ${total_value:,})",
                    symbol
                ))

            yield Label("Select asset to sell:")
            yield Select(options, prompt="Choose an asset...", id="asset-select")
            yield Label("Enter quantity to sell:")
            yield Input(placeholder="Quantity...", type="integer", id="quantity-input")

            with Horizontal(id="modal-buttons"):
                yield Button("Sell", variant="primary", id="confirm-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            select_widget = self.query_one("#asset-select", Select)
            input_widget = self.query_one("#quantity-input", Input)

            symbol = select_widget.value
            quantity_str = input_widget.value.strip()

            self.dismiss()

            if symbol and quantity_str:
                try:
                    quantity = int(quantity_str)
                    success, msg = self.engine.sell_asset(symbol, quantity)
                    self.callback(msg)
                except ValueError:
                    pass
        else:
            self.dismiss()


class HelpModal(ModalScreen):
    """Modal showing game instructions"""

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="help-modal"):
            yield Label("📖 HOW TO PLAY MERCHANT TYCOON", id="modal-title")

            with ScrollableContainer(id="help-content"):
                yield Label("")
                yield Label(" 🎯 GAME OBJECTIVE ", classes="section-header")
                yield Label("  Buy low, sell high, and become a wealthy merchant!")
                yield Label("  Main strategy: TRAVEL → BUY → SELL → INVEST INCOME")
                yield Label("")

                yield Label(" 💰 BASIC TRADING ", classes="section-header")
                yield Label("  • Travel (T) between cities to find the best prices")
                yield Label("  • Buy (B) goods when prices are low")
                yield Label("  • Sell (S) goods when prices are high")
                yield Label("  • Each city has different prices for different goods")
                yield Label("")

                yield Label(" 📈 STOCK EXCHANGE ", classes="section-header")
                yield Label("  • Exchange (E) to trade stocks & commodities")
                yield Label("  • Investments are SAFE from random events!")
                yield Label("  • Watch price trends: ▲ up, ▼ down, ─ stable")
                yield Label("  • Diversify your portfolio for better returns")
                yield Label("")

                yield Label(" 🏦 LOANS & DEBT ", classes="section-header")
                yield Label("  • Loan (L) to borrow money when you need capital")
                yield Label("  • 10% interest charged each day")
                yield Label("  • Repay (R) debt as soon as possible")
                yield Label("")

                yield Label(" 📦 INVENTORY ", classes="section-header")
                yield Label("  • Inventory (I) to see detailed purchase history")
                yield Label("  • Limited space: 50 units maximum")
                yield Label("  • Goods sold using FIFO (First In, First Out)")
                yield Label("  • Track profit/loss for each purchase lot")
                yield Label("")

                yield Label(" ⚠️ RANDOM EVENTS ", classes="section-header")
                yield Label("  • Random events can affect your goods inventory")
                yield Label("  • Stock market investments are protected!")
                yield Label("  • Stay alert and adapt your strategy")
                yield Label("")

                yield Label(" 💡 WINNING STRATEGY ", classes="section-header")
                yield Label("  1. Start by trading goods between cities")
                yield Label("  2. Learn which cities have best prices for each good")
                yield Label("  3. Once profitable, invest excess cash in stocks")
                yield Label("  4. Build a diversified investment portfolio")
                yield Label("  5. Balance trading and investing for maximum wealth")
                yield Label("")

            yield Button("Close (ESC)", variant="primary", id="close-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-btn":
            self.dismiss()

    def action_dismiss_modal(self) -> None:
        """Close the modal when ESC is pressed"""
        self.dismiss()


class MerchantTycoon(App):
    """Main game application"""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 4;
        grid-rows: auto 1fr 1fr auto;
    }

    StatsPanel {
        column-span: 2;
        background: $primary;
        color: $text;
        padding: 1;
        text-style: bold;
    }

    MarketPanel {
        border: solid $accent;
        padding: 1;
    }

    InventoryPanel {
        border: solid $accent;
        padding: 1;
    }

    ExchangePricesPanel {
        border: solid $accent;
        padding: 1;
    }

    InvestmentsPanel {
        border: solid $accent;
        padding: 1;
    }

    MessageLog {
        column-span: 2;
        border: solid $accent;
        padding: 1;
        max-height: 12;
    }

    #market-header, #inventory-header, #exchange-prices-header, #investments-header, #log-header {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    #market-list, #inventory-list, #exchange-prices-list, #investments-list, #log-content {
        height: auto;
    }

    /* Modal styles */
    #input-modal, #city-modal, #buy-modal, #sell-modal {
        width: 60;
        height: auto;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }

    #inventory-details-modal {
        width: 90;
        height: 35;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
        layout: vertical;
    }

    #details-content {
        width: 100%;
        height: 28;
        border: solid $primary;
        margin: 1 0;
        padding: 1;
        background: $panel;
    }

    #details-instructions {
        text-style: italic;
        color: $text-muted;
    }

    .section-header {
        text-style: bold;
        color: $accent;
        background: $primary-darken-2;
        padding: 0 1;
    }

    .lot-info {
        padding-left: 2;
        color: $text;
    }

    .profit-info {
        padding-left: 4;
        color: $success;
    }

    #modal-title {
        text-style: bold;
        color: $accent;
        text-align: center;
        margin-bottom: 1;
    }

    #modal-buttons {
        height: auto;
        margin-top: 1;
    }

    #modal-buttons Button {
        width: 1fr;
        margin: 0 1;
    }

    #city-list {
        height: auto;
        max-height: 10;
        margin: 1 0;
    }

    /* Exchange modal styles */
    #exchange-modal {
        width: 90;
        height: 40;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
        layout: vertical;
    }

    #exchange-subtitle {
        text-style: italic;
        color: $text-muted;
        text-align: center;
        margin-bottom: 1;
    }

    #exchange-actions {
        height: auto;
        margin: 1 0;
    }

    #exchange-actions Button {
        width: 1fr;
        margin: 0 1;
    }

    #exchange-content {
        width: 100%;
        height: 1fr;
        margin: 1 0;
        padding: 1;
    }

    /* Help modal styles */
    #help-modal {
        width: 90;
        height: 40;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
        layout: vertical;
    }

    #help-content {
        width: 100%;
        height: 30;
        margin: 1 0;
        padding: 1;
        border: solid $primary;
        background: $panel;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("b", "buy", "Buy"),
        Binding("s", "sell", "Sell"),
        Binding("t", "travel", "Travel"),
        Binding("l", "loan", "Loan"),
        Binding("r", "repay", "Repay"),
        Binding("i", "details", "Inventory"),
        Binding("e", "exchange", "Exchange"),
        Binding("h", "help", "Help"),
    ]

    def __init__(self):
        super().__init__()
        self.engine = GameEngine()
        self.message_log = None
        self.stats_panel = None
        self.market_panel = None
        self.inventory_panel = None
        self.exchange_prices_panel = None
        self.investments_panel = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield StatsPanel(self.engine)
        yield MarketPanel(self.engine)
        yield InventoryPanel(self.engine)
        yield ExchangePricesPanel(self.engine)
        yield InvestmentsPanel(self.engine)
        yield MessageLog()
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Merchant Tycoon"
        self.message_log = self.query_one(MessageLog)
        self.stats_panel = self.query_one(StatsPanel)
        self.market_panel = self.query_one(MarketPanel)
        self.inventory_panel = self.query_one(InventoryPanel)
        self.exchange_prices_panel = self.query_one(ExchangePricesPanel)
        self.investments_panel = self.query_one(InvestmentsPanel)
        self.refresh_all()

    def refresh_all(self):
        if self.stats_panel:
            self.stats_panel.update_stats()
        if self.market_panel:
            self.market_panel.update_market()
        if self.inventory_panel:
            self.inventory_panel.update_inventory()
        if self.exchange_prices_panel:
            self.exchange_prices_panel.update_exchange_prices()
        if self.investments_panel:
            self.investments_panel.update_investments()

    def game_log(self, msg: str):
        if self.message_log:
            self.message_log.add_message(msg)

    def action_buy(self):
        """Buy goods"""
        modal = BuyModal(self.engine, self._handle_buy)
        self.push_screen(modal)

    def _handle_buy(self, product: str, quantity: int):
        """Handle buy transaction"""
        if quantity <= 0:
            self.game_log("Quantity must be positive!")
            return

        success, msg = self.engine.buy(product, quantity)
        self.game_log(msg)
        self.refresh_all()

    def action_sell(self):
        """Sell goods"""
        if not self.engine.state.inventory:
            self.game_log("No goods to sell!")
            return

        modal = SellModal(self.engine, self._handle_sell)
        self.push_screen(modal)

    def _handle_sell(self, product: str, quantity: int):
        """Handle sell transaction"""
        if quantity <= 0:
            self.game_log("Quantity must be positive!")
            return

        success, msg = self.engine.sell(product, quantity)
        self.game_log(msg)
        self.refresh_all()

    def action_travel(self):
        """Travel to another city"""
        modal = CitySelectModal(CITIES, self.engine.state.current_city, self._handle_travel)
        self.push_screen(modal)

    def _handle_travel(self, city_index: int):
        """Handle travel to new city"""
        success, msg, event_msg = self.engine.travel(city_index)
        if success:
            self.game_log(msg)
            if event_msg:
                self.game_log(event_msg)
            self.refresh_all()
        else:
            self.game_log(msg)

    def action_loan(self):
        """Take a loan"""
        modal = InputModal(
            "🏦 Bank Loan",
            "How much would you like to borrow?\n(Max: $10,000 | Interest: 10% per day)",
            self._handle_loan
        )
        self.push_screen(modal)

    def _handle_loan(self, value: str):
        """Handle loan request"""
        try:
            amount = int(value.strip())
        except ValueError:
            self.game_log("Invalid amount!")
            return

        success, msg = self.engine.take_loan(amount)
        self.game_log(msg)
        self.refresh_all()

    def action_repay(self):
        """Repay loan"""
        if self.engine.state.debt <= 0:
            self.game_log("No debt to repay!")
            return

        modal = InputModal(
            "💳 Repay Loan",
            f"Current debt: ${self.engine.state.debt:,}\nCash available: ${self.engine.state.cash:,}\nHow much to repay?",
            self._handle_repay
        )
        self.push_screen(modal)

    def _handle_repay(self, value: str):
        """Handle loan repayment"""
        try:
            amount = int(value.strip())
        except ValueError:
            self.game_log("Invalid amount!")
            return

        success, msg = self.engine.repay_loan(amount)
        self.game_log(msg)
        self.refresh_all()

    def action_details(self):
        """Show detailed inventory with purchase lots"""
        if not self.engine.state.inventory:
            self.game_log("No goods in inventory!")
            return

        modal = InventoryDetailsModal(self.engine)
        self.push_screen(modal)

    def action_exchange(self):
        """Open the stock exchange"""
        modal = ExchangeModal(self.engine)
        self.push_screen(modal)

    def action_help(self):
        """Show game instructions"""
        modal = HelpModal()
        self.push_screen(modal)


if __name__ == "__main__":
    app = MerchantTycoon()
    app.run()
