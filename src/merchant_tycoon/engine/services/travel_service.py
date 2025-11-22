from typing import Optional, TYPE_CHECKING

from merchant_tycoon.config import SETTINGS

if TYPE_CHECKING:
    from merchant_tycoon.engine.game_state import GameState
    from merchant_tycoon.engine.services.bank_service import BankService
    from merchant_tycoon.engine.services.goods_service import GoodsService
    from merchant_tycoon.engine.services.investments_service import InvestmentsService
    from merchant_tycoon.engine.services.travel_events_service import TravelEventsService
    from merchant_tycoon.engine.services.goods_cargo_service import GoodsCargoService
    from merchant_tycoon.engine.services.day_advance_service import DayAdvanceService
    from merchant_tycoon.engine.services.messenger_service import MessengerService
    from merchant_tycoon.engine.services.wallet_service import WalletService
    from merchant_tycoon.engine.modal_queue import ModalQueue
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
        day_advance_service: "DayAdvanceService",
        messenger_service: "MessengerService",
        cargo_service: "GoodsCargoService",
        wallet_service: "WalletService",
        modal_queue: "ModalQueue",
    ):
        self.state = state
        self.bank_service = bank_service
        self.goods_service = goods_service
        self.investments_service = investments_service
        self.events_service = events_service
        self.cities_repo = cities_repository
        self.day_service = day_advance_service
        self.messenger = messenger_service
        self.cargo_service = cargo_service
        self.wallet = wallet_service
        self.modal_queue = modal_queue

    def _calculate_travel_fee(self) -> int:
        """Calculate travel fee based on cargo space used."""
        cargo_units = self.cargo_service.get_used_slots()
        return int(SETTINGS.travel.base_fee) + int(SETTINGS.travel.fee_per_cargo_unit) * cargo_units

    def travel(self, city_index: int) -> tuple[bool, str]:
        """Travel to a new city.

        Modals are added directly to engine.modal_queue during travel.

        Returns:
            tuple: (success, message)
            - success: bool - whether travel succeeded
            - message: str - status message
        """
        if city_index == self.state.current_city:
            return False, "Already in this city!"

        origin_city = self.cities_repo.get_by_index(self.state.current_city)
        destination_city = self.cities_repo.get_by_index(city_index)

        # Calculate and validate travel fee
        travel_fee = self._calculate_travel_fee()
        if not self.wallet.can_afford(travel_fee):
            return False, (
                f"Not enough cash to travel! Travel fee from {origin_city.name} to {destination_city.name} is ${travel_fee:,}. "
                f"You have ${self.wallet.get_balance():,}."
            )

        # Deduct travel fee
        if not self.wallet.spend(travel_fee):
            return False, "Payment failed"

        # Proceed with travel: change city
        self.state.current_city = city_index

        # Advance the day and apply daily effects (interest, prices, holdings)
        self.day_service.advance_day()

        # Check if player reached wealth threshold to unlock investments
        investments_unlock_modal = None
        try:
            from merchant_tycoon.config import SETTINGS
            asset_prices = getattr(self.investments_service, "asset_prices", {})
            current_wealth = self.state.calculate_total_wealth(asset_prices)
            # Get threshold and check unlock
            threshold = int(getattr(SETTINGS.investments, "min_wealth_to_unlock_trading", 0))
            just_unlocked = self.state.check_and_update_peak_wealth(current_wealth, threshold)
            if just_unlocked:
                investments_unlock_modal = (
                    f"Congratulations! You've reached ${self.state.peak_wealth:,} total wealth.\n\n"
                    f"You can now trade stocks, commodities, and cryptocurrencies!\n\n"
                    f"Visit the INVESTMENTS tab to start trading."
                )
        except Exception:
            pass

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
                messenger=self.messenger,
            )
        except Exception as e:
            events_list = []
            # Log exception for debugging (can help catch event handler issues)
            try:
                self.messenger.error(f"EXCEPTION in travel events: {type(e).__name__}: {e}", tag="debug")
            except Exception:
                pass

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

        # Log each event to messenger as a concise line
        try:
            for ev_msg, ev_type in (events_list or []):
                summary = (ev_msg or "").splitlines()[0]
                if ev_type == "loss":
                    self.messenger.warn(summary, tag="event")
                elif ev_type == "gain":
                    self.messenger.info(summary, tag="event")
                else:
                    self.messenger.debug(summary, tag="event")
        except Exception:
            pass

        # Add modals to queue (modal_queue is required)
        try:
            if investments_unlock_modal:
                self.modal_queue.add(investments_unlock_modal, "gain")
            if dividend_modal:
                self.modal_queue.add(dividend_modal, "gain")
            if events_list:
                # events_list is a list of (message, type)
                self.modal_queue.add(events_list, "neutral")
        except Exception:
            pass

        return True, msg
