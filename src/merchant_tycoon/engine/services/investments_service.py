import random
from typing import Dict, TYPE_CHECKING, Optional
import math

from merchant_tycoon.domain.model.investment_lot import InvestmentLot
from merchant_tycoon.config import SETTINGS

if TYPE_CHECKING:
    from merchant_tycoon.engine.game_state import GameState
    from merchant_tycoon.engine.services.clock_service import ClockService
    from merchant_tycoon.engine.services.bank_service import BankService
    from merchant_tycoon.domain.model.asset import Asset
    from merchant_tycoon.repositories import AssetsRepository


class InvestmentsService:
    """Service for handling investment operations (stocks, commodities, crypto)"""

    def __init__(
        self,
        state: "GameState",
        asset_prices: Dict[str, int],
        previous_asset_prices: Dict[str, int],
        assets_repository: "AssetsRepository",
        clock_service: Optional["ClockService"] = None,
        messenger: Optional["MessengerService"] = None,
        bank_service: Optional["BankService"] = None
    ):
        self.state = state
        self.asset_prices = asset_prices
        self.previous_asset_prices = previous_asset_prices
        self.assets_repo = assets_repository
        self.clock = clock_service
        self.messenger = messenger
        self.bank_service = bank_service

    def generate_asset_prices(self) -> None:
        """Generate random prices for stocks and commodities"""
        # Save previous prices
        self.previous_asset_prices.clear()
        self.previous_asset_prices.update(self.asset_prices)

        # Generate prices for all assets - always integers, minimum $1
        for asset in self.assets_repo.get_all():
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
        """Calculate maximum quantity affordable for given cash and price with fee.
        """
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

    # Helper functions for investment events
    def get_asset_types(self) -> list[str]:
        """Get all unique asset types (stock, commodity, crypto)."""
        types = set()
        for asset in self.assets_repo.get_all():
            types.add(asset.asset_type)
        return list(types)

    def get_assets_by_type(self, asset_type: str) -> list["Asset"]:
        """Get all assets of a specific type."""
        return [a for a in self.assets_repo.get_all() if a.asset_type == asset_type]

    def get_player_asset_types(self) -> list[str]:
        """Get asset types currently in player's portfolio."""
        types = set()
        for symbol in self.state.portfolio.keys():
            asset = self.assets_repo.get_by_symbol(symbol)
            if asset:
                types.add(asset.asset_type)
        return list(types)

    def get_player_assets_by_type(self, asset_type: str) -> list[str]:
        """Get symbols of player's held assets of a specific type."""
        held = []
        for symbol in self.state.portfolio.keys():
            asset = self.assets_repo.get_by_symbol(symbol)
            if asset and asset.asset_type == asset_type:
                held.append(symbol)
        return held

    # Dividend system methods
    def increment_lot_holding_days(self) -> None:
        """Increment days_held for all investment lots. Called daily during travel."""
        for lot in self.state.investment_lots:
            lot.days_held = getattr(lot, 'days_held', 0) + 1

    def calculate_and_pay_dividends(self) -> tuple[bool, str, int]:
        """Calculate and pay dividends for eligible lots.

        Returns:
            tuple[bool, str, int]: (has_dividends, message, total_payout)
        """
        interval = int(SETTINGS.investments.dividend_interval_days)
        min_holding = int(SETTINGS.investments.dividend_min_holding_days)

        # Check if dividends are enabled
        if interval <= 0:
            return False, "", 0

        # Check if it's dividend payout day
        if self.state.day % interval != 0:
            return False, "", 0

        total_payout = 0
        dividend_details = []  # List of (symbol, quantity, payout) tuples

        # Process each lot
        for lot in self.state.investment_lots:
            # Check if lot meets minimum holding period
            days_held = getattr(lot, 'days_held', 0)
            if days_held < min_holding:
                continue

            # Get asset and check for dividend rate
            asset = self.assets_repo.get_by_symbol(lot.asset_symbol)
            if not asset or asset.dividend_rate <= 0:
                continue

            # Calculate dividend for this lot
            current_price = self.asset_prices.get(lot.asset_symbol, 0)
            if current_price <= 0:
                continue

            # Payout = (current_price * dividend_rate) per share * quantity
            # Example: 100 shares of CDR at $200, dividend_rate=0.001
            # Per share dividend: $200 * 0.001 = $0.20
            # Total payout: $0.20 * 100 = $20
            per_share_dividend = current_price * asset.dividend_rate
            lot_payout = per_share_dividend * lot.quantity
            # Round up to at least $1 if payout > 0
            lot_payout = max(1, int(math.ceil(lot_payout)))

            total_payout += lot_payout

            # Update cumulative dividend paid for this lot
            lot.dividend_paid = getattr(lot, 'dividend_paid', 0) + lot_payout

            # Track for summary message
            existing = next((d for d in dividend_details if d[0] == lot.asset_symbol), None)
            if existing:
                idx = dividend_details.index(existing)
                dividend_details[idx] = (existing[0], existing[1] + lot.quantity, existing[2] + lot_payout)
            else:
                dividend_details.append((lot.asset_symbol, lot.quantity, lot_payout))

        # No dividends to pay
        if total_payout == 0:
            return False, "", 0

        # Pay dividends to bank account - separate transfer for each asset
        try:
            # Use BankService to credit account with separate transaction for each asset
            if self.bank_service and hasattr(self.state, 'bank') and self.state.bank:
                for symbol, qty, payout in dividend_details:
                    self.bank_service.credit(
                        amount=payout,
                        tx_type="dividend",
                        title=f"Dividend payout for {symbol}"
                    )
            else:
                # Fallback: add to cash if no bank service or account
                self.state.cash += total_payout
        except Exception:
            # Fallback: add to cash
            self.state.cash += total_payout

        # Build short message for messenger (will be logged in app.py)
        symbols_list = ", ".join([symbol for symbol, _, _ in dividend_details])
        short_message = f"💰 Dividend payout ${total_payout:,} for {symbols_list}"

        # Build detailed summary for modal
        summary_lines = []
        for symbol, qty, payout in dividend_details:
            summary_lines.append(f"{symbol}: {qty} shares → ${payout:,}")
        summary = "\n".join(summary_lines)
        modal_message = f"💰 Dividend Payout!\n\nYou received ${total_payout:,} in dividends:\n{summary}"

        # Return: (has_dividends, short_message, modal_message, total_payout, details)
        return True, short_message, modal_message, total_payout, dividend_details

