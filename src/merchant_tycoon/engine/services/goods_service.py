import random
from typing import Dict, TYPE_CHECKING, Optional, List

from merchant_tycoon.domain.model.purchase_lot import PurchaseLot
from merchant_tycoon.domain.model.transaction import Transaction
from merchant_tycoon.domain.goods import GOODS
from merchant_tycoon.domain.cities import CITIES
from merchant_tycoon.config import SETTINGS

if TYPE_CHECKING:
    from merchant_tycoon.engine.game_state import GameState
    from merchant_tycoon.engine.services.clock_service import ClockService
    from merchant_tycoon.engine.services.goods_cargo_service import GoodsCargoService
    from merchant_tycoon.domain.model.good import Good


class GoodsService:
    """Service for handling goods trading operations.

    This service is responsible for:
    - Price generation and management
    - Buying and selling goods
    - Transaction recording
    - Lot management (FIFO accounting)
    - Loss recording from random events

    Note: Cargo capacity management is handled by GoodsCargoService.
    """

    def __init__(
        self,
        state: "GameState",
        prices: Dict[str, int],
        previous_prices: Dict[str, int],
        clock_service: Optional["ClockService"] = None,
        messenger: Optional["MessengerService"] = None,
        cargo_service: Optional["GoodsCargoService"] = None
    ):
        self.state = state
        self.prices = prices
        self.previous_prices = previous_prices
        self.clock = clock_service
        self.messenger = messenger
        self.cargo_service = cargo_service

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

        # Check cargo capacity (size-aware)
        if self.cargo_service:
            # Get product info to calculate required space
            good = self.get_good(good_name)
            product_size = getattr(good, "size", 1) if good else 1
            required_space = quantity * product_size

            if not self.cargo_service.has_space_for_good(good_name, quantity):
                available = self.cargo_service.get_free_slots()
                return False, f"Not enough cargo space! Need {required_space} slots ({quantity}x {good_name} @ {product_size} slots each), only {available} available"
        elif not self.state.can_carry(quantity):
            # Fallback if cargo_service not available (legacy - uses simple counting)
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
            initial_quantity=quantity,
            lost_quantity=0,
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

    # --- Loss accounting (Option A): recognize loss immediately ---
    def _record_loss_tx(self, good_name: str, qty: int, price_per_unit: int) -> None:
        """Record a 'loss' transaction for bookkeeping (one lot slice)."""
        try:
            from merchant_tycoon.domain.model.transaction import Transaction
            from merchant_tycoon.domain.cities import CITIES
            city_name = CITIES[self.state.current_city].name
            ts = (self.clock.now().isoformat(timespec="seconds") if self.clock else "")
            tx = Transaction(
                transaction_type="loss",
                good_name=good_name,
                quantity=int(qty),
                price_per_unit=int(price_per_unit),
                total_value=int(qty) * int(price_per_unit),
                day=self.state.day,
                city=city_name,
                ts=ts,
            )
            self.state.transaction_history.append(tx)
        except Exception:
            pass

    def record_loss_fifo(self, good_name: str, quantity: int) -> int:
        """Remove quantity from inventory and lots using FIFO and mark as lost.
        Returns actually lost quantity (may be lower if insufficient stock).
        """
        if quantity <= 0:
            return 0
        have = int(self.state.inventory.get(good_name, 0))
        if have <= 0:
            return 0
        to_remove = min(int(quantity), have)
        remaining = to_remove
        to_remove_indices = []
        for idx, lot in enumerate(self.state.purchase_lots):
            if remaining <= 0:
                break
            if lot.good_name != good_name:
                continue
            take = min(int(getattr(lot, "quantity", 0)), remaining)
            if take <= 0:
                continue
            # Reduce available qty and mark as lost
            lot.quantity -= take
            try:
                lot.lost_quantity = int(getattr(lot, "lost_quantity", 0)) + take
            except Exception:
                lot.lost_quantity = take
            remaining -= take
            # Recognize loss immediately at purchase price
            self._record_loss_tx(good_name, take, int(getattr(lot, "purchase_price", 0)))
            # Remove empty lots
            if int(getattr(lot, "quantity", 0)) <= 0:
                to_remove_indices.append(idx)
        for i in reversed(to_remove_indices):
            try:
                self.state.purchase_lots.pop(i)
            except Exception:
                pass
        # Update inventory
        new_have = have - (to_remove - remaining)
        if new_have > 0:
            self.state.inventory[good_name] = new_have
        else:
            self.state.inventory.pop(good_name, None)
        return to_remove - remaining

    def record_loss_from_last(self, good_name: str, quantity: int) -> int:
        """Remove quantity starting from the last lot (LIFO-ish for event semantics)
        and mark as lost. Returns actually lost quantity.
        """
        if quantity <= 0:
            return 0
        have = int(self.state.inventory.get(good_name, 0))
        if have <= 0:
            return 0
        to_remove = min(int(quantity), have)
        remaining = to_remove
        for i in range(len(self.state.purchase_lots) - 1, -1, -1):
            if remaining <= 0:
                break
            lot = self.state.purchase_lots[i]
            if lot.good_name != good_name:
                continue
            take = min(int(getattr(lot, "quantity", 0)), remaining)
            if take <= 0:
                continue
            lot.quantity -= take
            try:
                lot.lost_quantity = int(getattr(lot, "lost_quantity", 0)) + take
            except Exception:
                lot.lost_quantity = take
            remaining -= take
            self._record_loss_tx(good_name, take, int(getattr(lot, "purchase_price", 0)))
            if int(getattr(lot, "quantity", 0)) <= 0:
                try:
                    self.state.purchase_lots.pop(i)
                except Exception:
                    pass
        # Update inventory
        new_have = have - (to_remove - remaining)
        if new_have > 0:
            self.state.inventory[good_name] = new_have
        else:
            self.state.inventory.pop(good_name, None)
        return to_remove - remaining

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
          get_goods(type="luxury", category="electronics") -> luxury electronics goods
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
