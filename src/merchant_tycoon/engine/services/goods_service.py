import random
from typing import Dict, TYPE_CHECKING, Optional, List

from merchant_tycoon.domain.model.purchase_lot import PurchaseLot
from merchant_tycoon.domain.model.transaction import Transaction
from merchant_tycoon.domain.constants import GOODS, CITIES
from merchant_tycoon.config import SETTINGS

if TYPE_CHECKING:
    from merchant_tycoon.engine.game_state import GameState
    from merchant_tycoon.engine.services.clock_service import ClockService
    from merchant_tycoon.domain.model.good import Good


class GoodsService:
    """Service for handling goods trading operations"""

    def __init__(self, state: "GameState", prices: Dict[str, int], previous_prices: Dict[str, int], clock_service: Optional["ClockService"] = None, messenger: Optional["MessengerService"] = None):
        self.state = state
        self.prices = prices
        self.previous_prices = previous_prices
        self.clock = clock_service
        self.messenger = messenger

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
        # Pricing strategy
        mode = str(getattr(SETTINGS.cargo, "extend_pricing_mode", "linear")).lower()
        if mode == "exponential":
            factor = float(getattr(SETTINGS.cargo, "extend_cost_factor", 2.0))
            current_cost = int(int(SETTINGS.cargo.extend_base_cost) * (factor ** bundles_purchased))
        else:  # linear (default)
            base = int(SETTINGS.cargo.extend_base_cost)
            factor = float(getattr(SETTINGS.cargo, "extend_cost_factor", 1.0))
            increment = base * factor
            current_cost = int(base + increment * bundles_purchased)

        # Validate cash
        if self.state.cash < current_cost:
            return False, f"Not enough cash! Need ${current_cost:,}, have ${self.state.cash:,}", current_cost

        # Deduct and extend capacity
        self.state.cash -= current_cost
        self.state.max_inventory = current_capacity + step

        # Compute next cost after purchase
        if mode == "exponential":
            factor = float(getattr(SETTINGS.cargo, "extend_cost_factor", 2.0))
            next_cost = int(int(SETTINGS.cargo.extend_base_cost) * (factor ** (bundles_purchased + 1)))
        else:
            base = int(SETTINGS.cargo.extend_base_cost)
            factor = float(getattr(SETTINGS.cargo, "extend_cost_factor", 1.0))
            increment = base * factor
            next_cost = int(base + increment * (bundles_purchased + 1))
        return True, (
            f"Cargo extended by +{step} slots to {self.state.max_inventory} (-${current_cost:,})"
        ), self.state.max_inventory, next_cost

    def generate_prices(self) -> None:
        """Generate random prices for current city"""
        # Save previous prices before generating new ones
        self.previous_prices.clear()
        self.previous_prices.update(self.prices)

        city = CITIES[self.state.current_city]
        for good in self.get_goods():
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
        try:
            if self.messenger:
                self.messenger.info(f"Bought {quantity}x {good_name} for ${total_cost:,}", tag="goods")
        except Exception:
            pass

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
        try:
            if self.messenger:
                self.messenger.info(f"Sold {quantity}x {good_name} for ${total_value:,}", tag="goods")
        except Exception:
            pass
        
        return True, f"Sold {quantity}x {good_name} for ${total_value}"

    def sell_lot_by_ts(self, good_name: str, lot_ts: str) -> tuple[bool, str]:
        """Sell exactly the specified purchase lot identified by its ISO timestamp.
        This bypasses FIFO and removes that specific lot.
        """
        if not lot_ts:
            return False, "Invalid lot selection"
        # Find the lot
        lot_index = -1
        target: Optional[PurchaseLot] = None
        for i, lot in enumerate(self.state.purchase_lots):
            if lot.good_name == good_name and getattr(lot, "ts", "") == lot_ts:
                lot_index = i
                target = lot
                break
        if target is None or lot_index < 0:
            return False, "Lot not found"

        qty = int(getattr(target, "quantity", 0))
        if qty <= 0:
            return False, "Nothing to sell in this lot"

        have = int(self.state.inventory.get(good_name, 0))
        if have < qty:
            return False, f"Not enough {good_name} in inventory to sell this lot"

        price = int(self.prices.get(good_name, 0))
        total_value = price * qty

        # Remove the lot and update inventory/cash
        # Remove specific lot by index
        try:
            self.state.purchase_lots.pop(lot_index)
        except Exception:
            return False, "Failed to remove lot"

        self.state.inventory[good_name] = have - qty
        if self.state.inventory[good_name] <= 0:
            del self.state.inventory[good_name]

        self.state.cash += total_value

        # Record transaction
        city_name = CITIES[self.state.current_city].name
        tx = Transaction(
            transaction_type="sell",
            good_name=good_name,
            quantity=qty,
            price_per_unit=price,
            total_value=total_value,
            day=self.state.day,
            city=city_name,
            ts=(self.clock.now().isoformat(timespec="seconds") if self.clock else ""),
        )
        self.state.transaction_history.append(tx)
        try:
            if self.messenger:
                self.messenger.info(f"Sold lot: {qty}x {good_name} for ${total_value:,}", tag="goods")
        except Exception:
            pass

        return True, f"Sold lot: {qty}x {good_name} for ${total_value:,}"

    def sell_from_lot(self, good_name: str, lot_ts: str, quantity: int) -> tuple[bool, str]:
        """Sell a specific quantity from the selected lot. If quantity equals the lot's
        quantity, the lot is removed; otherwise it is reduced. Updates inventory/cash and
        records a sell transaction at current price.
        """
        if not lot_ts or quantity <= 0:
            return False, "Invalid lot or quantity"
        # Locate the lot
        lot_index = -1
        target: Optional[PurchaseLot] = None
        for i, lot in enumerate(self.state.purchase_lots):
            if lot.good_name == good_name and getattr(lot, "ts", "") == lot_ts:
                lot_index = i
                target = lot
                break
        if target is None:
            return False, "Lot not found"

        have = int(self.state.inventory.get(good_name, 0))
        if have < quantity:
            return False, f"Not enough {good_name} to sell"

        price = int(self.prices.get(good_name, 0))
        total_value = price * quantity

        # Reduce/remove lot
        if quantity > target.quantity:
            return False, "Quantity exceeds lot size"
        if quantity == target.quantity:
            try:
                self.state.purchase_lots.pop(lot_index)
            except Exception:
                return False, "Failed to remove lot"
        else:
            target.quantity -= quantity

        # Update inventory and cash
        self.state.inventory[good_name] = have - quantity
        if self.state.inventory[good_name] <= 0:
            del self.state.inventory[good_name]
        self.state.cash += total_value

        # Record transaction
        city_name = CITIES[self.state.current_city].name
        tx = Transaction(
            transaction_type="sell",
            good_name=good_name,
            quantity=quantity,
            price_per_unit=price,
            total_value=total_value,
            day=self.state.day,
            city=city_name,
            ts=(self.clock.now().isoformat(timespec="seconds") if self.clock else ""),
        )
        self.state.transaction_history.append(tx)
        try:
            if self.messenger:
                self.messenger.info(f"Sold {quantity}x {good_name} for ${total_value:,}", tag="goods")
        except Exception:
            pass
        
        return True, f"Sold {quantity}x {good_name} for ${total_value:,}"

    # --- Helpers to keep lots consistent when inventory changes outside sell() ---
    def _remove_from_lots_fifo(self, good_name: str, quantity: int) -> int:
        """Remove quantity from purchase_lots for given good using FIFO. Returns removed qty."""
        if quantity <= 0:
            return 0
        remaining = int(quantity)
        lots_to_remove = []
        for i, lot in enumerate(self.state.purchase_lots):
            if lot.good_name != good_name:
                continue
            if remaining <= 0:
                break
            if lot.quantity <= remaining:
                remaining -= lot.quantity
                lots_to_remove.append(i)
            else:
                lot.quantity -= remaining
                remaining = 0
                break
        for i in reversed(lots_to_remove):
            try:
                self.state.purchase_lots.pop(i)
            except Exception:
                pass
        return int(quantity) - int(remaining)

    def _remove_from_lots_from_last(self, good_name: str, quantity: int) -> int:
        """Remove quantity from purchase_lots for given good starting from the last lot.
        Returns removed qty.
        """
        if quantity <= 0:
            return 0
        remaining = int(quantity)
        for i in range(len(self.state.purchase_lots) - 1, -1, -1):
            lot = self.state.purchase_lots[i]
            if lot.good_name != good_name:
                continue
            if remaining <= 0:
                break
            if lot.quantity <= remaining:
                remaining -= lot.quantity
                try:
                    self.state.purchase_lots.pop(i)
                except Exception:
                    pass
            else:
                lot.quantity -= remaining
                remaining = 0
                break
        return int(quantity) - int(remaining)

    # ---- Public helper functions (filtering and lookup) ----
    def get_goods(self, *, type: Optional[str] = None, category: Optional[str] = None) -> List["Good"]:
        """Return goods filtered by optional type and/or category.

        Examples:
          get_goods() -> all goods
          get_goods(type="luxury") -> only luxury goods
          get_goods(category="jewelry") -> only jewelry goods
          get_goods(type="luxury", category="hardware") -> luxury hardware goods
        """
        items = GOODS
        if type is not None:
            t = str(type).lower()
            items = [g for g in items if str(getattr(g, "type", "standard")).lower() == t]
        if category is not None:
            c = str(category).lower()
            items = [g for g in items if str(getattr(g, "category", "")).lower() == c]
        return list(items)

    def get_good(self, name: str) -> Optional["Good"]:
        """Return Good by exact name, or None if not found."""
        for g in GOODS:
            if g.name == name:
                return g
        return None

    def is_luxury(self, name: str) -> bool:
        """True if the named good has type == 'luxury'."""
        g = self.get_good(name)
        return str(getattr(g, "type", "")).lower() == "luxury" if g else False
