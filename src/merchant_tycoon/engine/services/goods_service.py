import random
from typing import Dict, TYPE_CHECKING, Optional

from merchant_tycoon.model import PurchaseLot, Transaction, GOODS, CITIES
from merchant_tycoon.config import SETTINGS

if TYPE_CHECKING:
    from merchant_tycoon.engine.game_state import GameState
    from merchant_tycoon.engine.services.clock_service import ClockService


class GoodsService:
    """Service for handling goods trading operations"""

    def __init__(self, state: "GameState", prices: Dict[str, int], previous_prices: Dict[str, int], clock_service: Optional["ClockService"] = None):
        self.state = state
        self.prices = prices
        self.previous_prices = previous_prices
        self.clock = clock_service

    # Cargo extension utility
    def extend_cargo(self) -> tuple:
        """Attempt to extend cargo capacity by a configurable step.
        Pricing is exponential per bundle: base_cost * (factor ** bundles_purchased),
        where a bundle = `SETTINGS.cargo.extend_step` slots beyond base capacity.
        Returns one of the following tuples:
          - (False, message, current_cost) when insufficient cash.
          - (True, message, new_capacity, next_cost) on success.
        """
        # Determine how many slots purchased beyond the base capacity
        try:
            current_capacity = int(getattr(self.state, "max_inventory", SETTINGS.cargo.base_capacity))
        except Exception:
            current_capacity = SETTINGS.cargo.base_capacity
        step = max(1, int(SETTINGS.cargo.extend_step))
        over_base = max(0, current_capacity - SETTINGS.cargo.base_capacity)
        bundles_purchased = over_base // step
        current_cost = int(SETTINGS.cargo.extend_base_cost) * (SETTINGS.cargo.extend_cost_factor ** bundles_purchased)

        # Validate cash
        if self.state.cash < current_cost:
            return False, f"Not enough cash! Need ${current_cost:,}, have ${self.state.cash:,}", current_cost

        # Deduct and extend capacity
        self.state.cash -= current_cost
        self.state.max_inventory = current_capacity + step

        # Compute next cost after purchase
        next_cost = int(SETTINGS.cargo.extend_base_cost) * (SETTINGS.cargo.extend_cost_factor ** (bundles_purchased + 1))
        return True, (
            f"Cargo extended by +{step} slots to {self.state.max_inventory} (-${current_cost:,})"
        ), self.state.max_inventory, next_cost

    def generate_prices(self) -> None:
        """Generate random prices for current city"""
        # Save previous prices before generating new ones
        self.previous_prices.clear()
        self.previous_prices.update(self.prices)

        city = CITIES[self.state.current_city]
        for good in GOODS:
            variance = random.uniform(1 - good.price_variance, 1 + good.price_variance)
            city_mult = city.price_multiplier.get(good.name, 1.0)
            base_price = good.base_price * city_mult * variance
            # Apply one-day modifier if present
            try:
                modifier = float(self.state.price_modifiers.get(good.name, 1.0))
            except Exception:
                modifier = 1.0
            price = int(max(SETTINGS.pricing.min_unit_price, base_price * modifier))
            self.prices[good.name] = price
        # Clear one-day modifiers after they take effect
        try:
            self.state.price_modifiers.clear()
        except Exception:
            self.state.price_modifiers = {}

        # Update rolling price history (keep last 10 per good)
        try:
            hist = getattr(self.state, "price_history", None)
            if hist is None:
                hist = {}
                self.state.price_history = hist
            for name, price in (self.prices or {}).items():
                seq = hist.get(name)
                if seq is None:
                    seq = []
                    hist[name] = seq
                seq.append(int(price))
                window = int(SETTINGS.pricing.history_window)
                if len(seq) > window:
                    del seq[:-window]
        except Exception:
            # Best-effort; ignore history errors
            pass

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
            ts=(self.clock.now().isoformat(timespec="seconds") if self.clock else ""),
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
            ts=(self.clock.now().isoformat(timespec="seconds") if self.clock else ""),
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
            ts=(self.clock.now().isoformat(timespec="seconds") if self.clock else ""),
        )
        self.state.transaction_history.append(transaction)

        return True, f"Sold {quantity}x {good_name} for ${total_value}"
