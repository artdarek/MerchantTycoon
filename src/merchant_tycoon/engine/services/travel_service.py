from typing import Optional, TYPE_CHECKING

from merchant_tycoon.config import SETTINGS

if TYPE_CHECKING:
    from merchant_tycoon.engine.game_state import GameState
    from merchant_tycoon.engine.services.bank_service import BankService
    from merchant_tycoon.engine.services.goods_service import GoodsService
    from merchant_tycoon.engine.services.investments_service import InvestmentsService
    from merchant_tycoon.engine.services.travel_events_service import TravelEventsService
    from merchant_tycoon.engine.services.goods_cargo_service import GoodsCargoService
    from merchant_tycoon.engine.services.clock_service import ClockService
    from merchant_tycoon.engine.services.messenger_service import MessengerService
    from merchant_tycoon.repositories import CitiesRepository


class TravelService:
    """Service for handling travel operations"""

    def __init__(
        self,
        state: "GameState",
        bank_service: "BankService",
        goods_service: "GoodsService",
        investments_service: "InvestmentsService",
        events_service: "TravelEventsService",
        cities_repository: "CitiesRepository",
        clock_service: "ClockService",
        messenger_service: "MessengerService",
        cargo_service: "GoodsCargoService",
    ):
        self.state = state
        self.bank_service = bank_service
        self.goods_service = goods_service
        self.investments_service = investments_service
        self.events_service = events_service
        self.cities_repo = cities_repository
        self.clock_service = clock_service
        self.messenger = messenger_service
        self.cargo_service = cargo_service

    def _calculate_travel_fee(self) -> int:
        """Calculate travel fee based on cargo space used."""
        cargo_units = self.cargo_service.get_used_slots()
        return int(SETTINGS.travel.base_fee) + int(SETTINGS.travel.fee_per_cargo_unit) * cargo_units

    def travel(self, city_index: int) -> tuple[bool, str, list, Optional[str]]:
        """Travel to a new city.

        Returns:
            tuple: (success, message, events_list, dividend_modal)
            - success: bool - whether travel succeeded
            - message: str - status message
            - events_list: list of (event_msg, event_type) tuples
            - dividend_modal: Optional[str] - dividend modal message if any
        """
        if city_index == self.state.current_city:
            return False, "Already in this city!", [], None

        origin_city = self.cities_repo.get_by_index(self.state.current_city)
        destination_city = self.cities_repo.get_by_index(city_index)

        # Calculate and validate travel fee
        travel_fee = self._calculate_travel_fee()
        if self.state.cash < travel_fee:
            return False, (
                f"Not enough cash to travel! Travel fee from {origin_city.name} to {destination_city.name} is ${travel_fee}. "
                f"You have ${self.state.cash}."
            ), [], None

        # Deduct travel fee
        self.state.cash -= travel_fee

        # Proceed with travel: change city and advance day
        self.state.current_city = city_index
        self.clock_service.advance_day()

        # Randomize daily interest rates for this new day (1%–20%)
        try:
            self.bank_service.randomize_daily_rates()
        except Exception:
            pass

        # Apply per-loan interest using each loan's APR/365 with fractional carry
        self.bank_service.accrue_loan_interest()

        # Accrue bank interest for the day advance (daily compounding)
        self.bank_service.accrue_bank_interest()

        # Increment holding days for investment lots (for dividend eligibility)
        try:
            self.investments_service.increment_lot_holding_days()
        except Exception:
            pass

        # Generate new prices for goods and assets FIRST
        # (so events can show accurate before/after prices)
        self.goods_service.generate_prices()
        self.investments_service.generate_asset_prices()

        # Random events (can set price modifiers and show current prices)
        try:
            events_list = self.events_service.trigger(
                self.state,
                self.goods_service.prices,
                getattr(self.investments_service, "asset_prices", {}),
                city=destination_city,
                bank_service=self.bank_service,
                goods_service=self.goods_service,
                investments_service=self.investments_service,
            )
        except Exception:
            events_list = []

        # If events set price modifiers, regenerate prices with those modifiers applied
        if self.state.price_modifiers:
            self.goods_service.generate_prices()

        # Check for dividend payouts (happens after price generation)
        # Returns None if no dividends, or (has_dividend, modal_message) if paid
        # Messenger logging happens inside calculate_and_pay_dividends
        dividend_modal = None
        try:
            result = self.investments_service.calculate_and_pay_dividends()
            if result:  # Has dividend
                has_dividend, modal_msg = result
                dividend_modal = modal_msg
        except Exception:
            pass

        city = destination_city
        msg = (
            f"Traveled to {city.name}, {city.country}. "
            f"Travel fee charged: ${travel_fee} for route {origin_city.name} → {destination_city.name}"
        )
        self.messenger.info(msg, tag="travel")

        # Return travel result with optional dividend modal
        # dividend_modal is None if no dividend, or modal message string if dividend paid
        return True, msg, events_list, dividend_modal
