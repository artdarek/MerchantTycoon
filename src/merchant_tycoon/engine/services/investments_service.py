import random
from typing import Dict, TYPE_CHECKING, Optional
import math

from merchant_tycoon.domain.model.investment_lot import InvestmentLot
from merchant_tycoon.domain.constants import ASSETS
from merchant_tycoon.config import SETTINGS

if TYPE_CHECKING:
    from merchant_tycoon.engine.game_state import GameState
    from merchant_tycoon.engine.services.clock_service import ClockService
    from merchant_tycoon.domain.model.asset import Asset


class InvestmentsService:
    """Service for handling investment operations (stocks, commodities, crypto)"""

    def __init__(self, state: "GameState", asset_prices: Dict[str, int], previous_asset_prices: Dict[str, int], clock_service: Optional["ClockService"] = None, messenger: Optional["MessengerService"] = None):
        self.state = state
        self.asset_prices = asset_prices
        self.previous_asset_prices = previous_asset_prices
        self.clock = clock_service
        self.messenger = messenger

    def generate_asset_prices(self) -> None:
        """Generate random prices for stocks and commodities"""
        # Save previous prices
        self.previous_asset_prices.clear()
        self.previous_asset_prices.update(self.asset_prices)

        # Generate prices for all assets - always integers, minimum $1
        for asset in ASSETS:
            variance = random.uniform(1 - asset.price_variance, 1 + asset.price_variance) * float(SETTINGS.investments.variance_scale)
            price = asset.base_price * variance
            # Always convert to int and ensure minimum $1
            p = max(int(SETTINGS.pricing.min_unit_price), int(price))
            self.asset_prices[asset.symbol] = p

        # Update rolling price history for assets (reuse state's price_history)
        try:
            hist = getattr(self.state, "price_history", None)
            if hist is None:
                hist = {}
                self.state.price_history = hist
            for symbol, price in (self.asset_prices or {}).items():
                seq = hist.get(symbol)
                if seq is None:
                    seq = []
                    hist[symbol] = seq
                seq.append(int(price))
                window = int(SETTINGS.pricing.history_window)
                if len(seq) > window:
                    del seq[:-window]
        except Exception:
            pass

    def buy_asset(self, symbol: str, quantity: int) -> tuple[bool, str]:
        """Buy stocks or commodities"""
        if symbol not in self.asset_prices:
            return False, "Invalid asset"

        if quantity <= 0:
            return False, "Quantity must be positive"

        price = self.asset_prices[symbol]
        base_cost = price * quantity
        # Commission on buy: rate with minimum fee
        rate = float(getattr(SETTINGS.investments, "buy_fee_rate", 0.02))
        min_fee = int(getattr(SETTINGS.investments, "buy_fee_min", 1))
        fee = max(min_fee, int(math.ceil(base_cost * rate)))
        total_cost = base_cost + fee

        if total_cost > self.state.cash:
            return False, f"Not enough cash! Need ${total_cost:,} (incl. fee ${fee:,}), have ${self.state.cash:,}"

        self.state.cash -= total_cost
        self.state.portfolio[symbol] = self.state.portfolio.get(symbol, 0) + quantity

        # Record investment lot
        lot = InvestmentLot(
            asset_symbol=symbol,
            quantity=quantity,
            purchase_price=price,
            day=self.state.day,
            ts=(self.clock.now().isoformat(timespec="seconds") if getattr(self, 'clock', None) else ""),
        )
        self.state.investment_lots.append(lot)

        try:
            if self.messenger:
                self.messenger.info(
                    f"Bought {quantity}x {symbol} for ${base_cost:,} (fee ${fee:,}, total ${total_cost:,})",
                    tag="investments",
                )
        except Exception:
            pass
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
        # Commission on sell: rate with minimum fee, deducted from proceeds
        rate = float(getattr(SETTINGS.investments, "sell_fee_rate", 0.005))
        min_fee = int(getattr(SETTINGS.investments, "sell_fee_min", 1))
        fee = max(min_fee, int(math.ceil(total_value * rate)))
        proceeds = max(0, total_value - fee)

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

        self.state.cash += proceeds
        self.state.portfolio[symbol] -= quantity
        if self.state.portfolio[symbol] == 0:
            del self.state.portfolio[symbol]

        try:
            if self.messenger:
                self.messenger.info(
                    f"Sold {quantity}x {symbol} for ${total_value:,} (fee ${fee:,}, received ${proceeds:,})",
                    tag="investments",
                )
        except Exception:
            pass
        return True, f"Sold {quantity}x {symbol} for ${proceeds:,} (after fee)"

    def sell_asset_from_lot(self, symbol: str, lot_ts: str, quantity: int) -> tuple[bool, str]:
        """Sell a specific quantity from a selected investment lot (identified by ts).

        Applies the same sell commission rules as sell_asset and updates lots/portfolio
        without enforcing FIFO. If quantity equals lot size the lot is removed.
        """
        if not lot_ts or quantity <= 0:
            return False, "Invalid lot or quantity"
        # Find the lot
        lot_index = -1
        target: Optional[InvestmentLot] = None
        for i, lot in enumerate(self.state.investment_lots):
            if lot.asset_symbol == symbol and getattr(lot, "ts", "") == lot_ts:
                lot_index = i
                target = lot
                break
        if target is None:
            return False, "Lot not found"

        have = int(self.state.portfolio.get(symbol, 0))
        if have < quantity:
            return False, f"Don't have enough! Have {have}x {symbol}"
        if quantity > int(getattr(target, "quantity", 0)):
            return False, "Quantity exceeds lot size"

        price = int(self.asset_prices.get(symbol, 0))
        total_value = price * quantity
        rate = float(getattr(SETTINGS.investments, "sell_fee_rate", 0.005))
        min_fee = int(getattr(SETTINGS.investments, "sell_fee_min", 1))
        fee = max(min_fee, int(math.ceil(total_value * rate)))
        proceeds = max(0, total_value - fee)

        # Reduce/remove selected lot
        if quantity == target.quantity:
            try:
                self.state.investment_lots.pop(lot_index)
            except Exception:
                return False, "Failed to remove lot"
        else:
            target.quantity -= quantity

        # Update portfolio and cash
        self.state.portfolio[symbol] = have - quantity
        if self.state.portfolio[symbol] <= 0:
            del self.state.portfolio[symbol]
        self.state.cash += proceeds

        try:
            if self.messenger:
                self.messenger.info(
                    f"Sold {quantity}x {symbol} (selected lot) for ${total_value:,} (fee ${fee:,}, received ${proceeds:,})",
                    tag="investments",
                )
        except Exception:
            pass
        return True, f"Sold {quantity}x {symbol} for ${proceeds:,} (after fee)"

    # Utility to compute max affordable quantity including buy commission
    def max_affordable(self, cash: int, price: int) -> int:
        if price <= 0 or cash <= 0:
            return 0
        rate = float(getattr(SETTINGS.investments, "buy_fee_rate", 0.02))
        min_fee = int(getattr(SETTINGS.investments, "buy_fee_min", 1))
        # Upper bound ignoring fee
        hi = cash // price
        if hi <= 0:
            return 0
        lo = 0
        while lo < hi:
            mid = (lo + hi + 1) // 2
            base = price * mid
            fee = max(min_fee, int(math.ceil(base * rate)))
            total = base + fee
            if total <= cash:
                lo = mid
            else:
                hi = mid - 1
        return lo

    # ---- Public helper functions (filtering and lookup) ----
    def get_assets(self, *, type: Optional[str] = None) -> list["Asset"]:
        """Return assets filtered by optional type ('stock'|'commodity'|'crypto').

        Examples:
          get_assets() -> all assets
          get_assets(type='stock') -> only stocks
        """
        items = ASSETS
        if type is not None:
            t = str(type).lower()
            items = [a for a in items if str(getattr(a, "asset_type", "")).lower() == t]
        return list(items)

    def get_asset(self, symbol: str) -> Optional["Asset"]:
        """Return Asset by ticker symbol (exact match) or None if not found."""
        for a in ASSETS:
            if a.symbol == symbol:
                return a
        return None

    def is_crypto(self, symbol: str) -> bool:
        a = self.get_asset(symbol)
        return str(getattr(a, "asset_type", "")).lower() == "crypto" if a else False
