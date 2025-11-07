import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .models import (
    PurchaseLot,
    Transaction,
    InvestmentLot,
    GOODS,
    STOCKS,
    COMMODITIES,
    CRYPTO,
    CITIES,
)


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
        all_assets = STOCKS + COMMODITIES + CRYPTO
        for asset in all_assets:
            variance = random.uniform(1 - asset.price_variance, 1 + asset.price_variance)
            # For crypto with very low prices (like DOGE), use float precision
            price = asset.base_price * variance
            self.asset_prices[asset.symbol] = round(price, 2) if asset.asset_type == "crypto" and price < 10 else int(price)

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
            city=city_name,
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
            city=city_name,
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
            city=city_name,
        )
        self.state.transaction_history.append(transaction)

        return True, f"Sold {quantity}x {good_name} for ${total_value}"

    def travel(self, city_index: int) -> tuple[bool, str, Optional[tuple[str, bool]]]:
        """Travel to a new city. Returns (success, message, event_data) where event_data is (event_msg, is_positive)"""
        if city_index == self.state.current_city:
            return False, "Already in this city!", None

        self.state.current_city = city_index
        self.state.day += 1

        # Apply interest if there's debt
        if self.state.debt > 0:
            interest = int(self.state.debt * self.interest_rate)
            self.state.debt += interest

        # Random event (only affects goods, not investments!)
        event_data = self._random_event()

        # Generate new prices for goods and assets
        self.generate_prices()
        self.generate_asset_prices()

        city = CITIES[city_index]
        return True, f"Traveled to {city.name}, {city.country}", event_data

    def _random_event(self) -> Optional[tuple[str, bool]]:
        """Generate random travel events. Returns (message, is_positive) or None"""
        event_chance = random.random()

        if event_chance < 0.15:  # 15% chance of bad event
            event_type = random.choice(["robbery", "confiscation", "damage"])

            if event_type == "robbery" and self.state.inventory:
                # Lose random goods
                good = random.choice(list(self.state.inventory.keys()))
                lost = random.randint(1, max(1, self.state.inventory[good] // 2))
                self.state.inventory[good] -= lost
                if self.state.inventory[good] <= 0:
                    del self.state.inventory[good]
                return (f"🚨 ROBBED! Lost {lost}x {good}!", False)

            elif event_type == "confiscation" and self.state.inventory:
                # Lose all of one type
                good = random.choice(list(self.state.inventory.keys()))
                lost = self.state.inventory[good]
                del self.state.inventory[good]
                return (f"🚔 CONFISCATED! Lost all {lost}x {good}!", False)

            elif event_type == "damage":
                damage = random.randint(100, 500)
                self.state.cash -= damage
                return (f"💥 ACCIDENT! Paid ${damage} in damages!", False)

        elif event_chance < 0.20:  # 5% chance of good event
            bonus = random.randint(200, 800)
            self.state.cash += bonus
            return (f"✨ LUCKY FIND! Found ${bonus}!", True)

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
            day=self.state.day,
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
