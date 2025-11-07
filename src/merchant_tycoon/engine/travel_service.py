from typing import Optional, TYPE_CHECKING

from ..model import CITIES
from ..events import TravelEventSystem

if TYPE_CHECKING:
    from .game_state import GameState
    from .bank_service import BankService
    from .goods_service import GoodsService
    from .investments_service import InvestmentsService


class TravelService:
    """Service for handling travel operations"""

    def __init__(
        self,
        state: "GameState",
        bank_service: "BankService",
        goods_service: "GoodsService",
        investments_service: "InvestmentsService",
    ):
        self.state = state
        self.bank_service = bank_service
        self.goods_service = goods_service
        self.investments_service = investments_service

    def travel(self, city_index: int) -> tuple[bool, str, Optional[tuple[str, bool]]]:
        """Travel to a new city. Returns (success, message, event_data) where event_data is (event_msg, is_positive)"""
        if city_index == self.state.current_city:
            return False, "Already in this city!", None

        # Calculate travel fee: $100 base + $1 per unit of cargo currently carried
        origin_city = CITIES[self.state.current_city]
        destination_city = CITIES[city_index]
        try:
            cargo_units = int(self.state.get_inventory_count())
        except Exception:
            cargo_units = sum(self.state.inventory.values()) if isinstance(self.state.inventory, dict) else 0
        travel_fee = 100 + cargo_units

        # Ensure player can afford the travel fee
        if self.state.cash < travel_fee:
            return False, (
                f"Not enough cash to travel! Travel fee from {origin_city.name} to {destination_city.name} is ${travel_fee}. "
                f"You have ${self.state.cash}."
            ), None

        # Deduct travel fee
        self.state.cash -= travel_fee

        # Proceed with travel: advance day and change city
        self.state.current_city = city_index
        self.state.day += 1

        # Randomize daily interest rates for this new day (1%–20%)
        try:
            self.bank_service.randomize_daily_rates()
        except Exception:
            pass

        # Apply per-loan interest using each loan's APR/365 with fractional carry
        self.bank_service.accrue_loan_interest()

        # Accrue bank interest for the day advance (daily compounding)
        self.bank_service.accrue_bank_interest()

        # Random event (only affects goods, not investments!)
        event_data = self._random_event()

        # Generate new prices for goods and assets
        self.goods_service.generate_prices()
        self.investments_service.generate_asset_prices()

        city = destination_city
        msg = (
            f"Traveled to {city.name}, {city.country}. "
            f"Travel fee charged: ${travel_fee} for route {origin_city.name} → {destination_city.name}"
        )
        return True, msg, event_data

    def _random_event(self) -> Optional[tuple[str, bool]]:
        """Generate a weighted random travel event. Returns (message, is_positive) or None.
        Delegates to TravelEventSystem to keep engine slim.

        Note: This method needs access to GameEngine-like interface for event system.
        We'll need to pass a wrapper or the actual GameEngine reference.
        """
        try:
            # TravelEventSystem expects an engine-like object with state and prices
            # For now, we create a minimal wrapper
            class EngineWrapper:
                def __init__(self, state, goods_service):
                    self.state = state
                    self.prices = goods_service.prices
                    self.asset_prices = {}  # Events don't affect investments

            wrapper = EngineWrapper(self.state, self.goods_service)
            return TravelEventSystem().trigger(wrapper)
        except Exception:
            # Fail-safe: no event if anything goes wrong
            return None
