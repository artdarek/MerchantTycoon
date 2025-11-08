from typing import Optional, TYPE_CHECKING

from merchant_tycoon.model import CITIES

if TYPE_CHECKING:
    from merchant_tycoon.engine.game_state import GameState
    from merchant_tycoon.engine.services.bank_service import BankService
    from merchant_tycoon.engine.services.goods_service import GoodsService
    from merchant_tycoon.engine.services.investments_service import InvestmentsService
    from merchant_tycoon.engine.services.travel_events_service import TravelEventsService


class TravelService:
    """Service for handling travel operations"""

    def __init__(
        self,
        state: "GameState",
        bank_service: "BankService",
        goods_service: "GoodsService",
        investments_service: "InvestmentsService",
        events_service: "TravelEventsService",
    ):
        self.state = state
        self.bank_service = bank_service
        self.goods_service = goods_service
        self.investments_service = investments_service
        self.events_service = events_service

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
        try:
            event_data = self.events_service.trigger(
                self.state,
                self.goods_service.prices,
                getattr(self.investments_service, "asset_prices", {}),
            )
        except Exception:
            event_data = None

        # Generate new prices for goods and assets
        self.goods_service.generate_prices()
        self.investments_service.generate_asset_prices()

        city = destination_city
        msg = (
            f"Traveled to {city.name}, {city.country}. "
            f"Travel fee charged: ${travel_fee} for route {origin_city.name} → {destination_city.name}"
        )
        return True, msg, event_data
