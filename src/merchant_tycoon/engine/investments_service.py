import random
from typing import Dict, TYPE_CHECKING

from merchant_tycoon.model import InvestmentLot, STOCKS, COMMODITIES, CRYPTO

if TYPE_CHECKING:
    from merchant_tycoon.engine.game_state import GameState


class InvestmentsService:
    """Service for handling investment operations (stocks, commodities, crypto)"""

    def __init__(self, state: "GameState", asset_prices: Dict[str, int], previous_asset_prices: Dict[str, int]):
        self.state = state
        self.asset_prices = asset_prices
        self.previous_asset_prices = previous_asset_prices

    def generate_asset_prices(self) -> None:
        """Generate random prices for stocks and commodities"""
        # Save previous prices
        self.previous_asset_prices.clear()
        self.previous_asset_prices.update(self.asset_prices)

        # Generate prices for all assets - always integers, minimum $1
        all_assets = STOCKS + COMMODITIES + CRYPTO
        for asset in all_assets:
            variance = random.uniform(1 - asset.price_variance, 1 + asset.price_variance)
            price = asset.base_price * variance
            # Always convert to int and ensure minimum $1
            self.asset_prices[asset.symbol] = max(1, int(price))

    def buy_asset(self, symbol: str, quantity: int) -> tuple[bool, str]:
        """Buy stocks or commodities"""
        if symbol not in self.asset_prices:
            return False, "Invalid asset"

        if quantity <= 0:
            return False, "Quantity must be positive"

        price = self.asset_prices[symbol]
        total_cost = price * quantity

        if total_cost > self.state.cash:
            return False, f"Not enough cash! Need ${total_cost:,}, have ${self.state.cash:,}"

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
