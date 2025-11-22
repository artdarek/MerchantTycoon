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
    from merchant_tycoon.engine.services.lotto_service import LottoService
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

    def _calculate_travel_fee(self) -> int:
        """Calculate travel fee based on cargo space used."""
        cargo_units = self.cargo_service.get_used_slots()
        return int(SETTINGS.travel.base_fee) + int(SETTINGS.travel.fee_per_cargo_unit) * cargo_units

    def travel(self, city_index: int) -> tuple[bool, str, list, Optional[str], Optional[str]]:
        """Travel to a new city.

        Returns:
            tuple: (success, message, events_list, dividend_modal, investments_unlock_modal)
            - success: bool - whether travel succeeded
            - message: str - status message
            - events_list: list of (event_msg, event_type) tuples
            - dividend_modal: Optional[str] - dividend modal message if any
            - investments_unlock_modal: Optional[str] - investments unlock message if just unlocked
        """
        if city_index == self.state.current_city:
            return False, "Already in this city!", [], None, None

        origin_city = self.cities_repo.get_by_index(self.state.current_city)
        destination_city = self.cities_repo.get_by_index(city_index)

        # Calculate and validate travel fee
        travel_fee = self._calculate_travel_fee()
        if not self.wallet.can_afford(travel_fee):
            return False, (
                f"Not enough cash to travel! Travel fee from {origin_city.name} to {destination_city.name} is ${travel_fee:,}. "
                f"You have ${self.wallet.get_balance():,}."
            ), [], None, None

        # Deduct travel fee
        if not self.wallet.spend(travel_fee):
            return False, "Payment failed", [], None, None

        # Proceed with travel: change city
        self.state.current_city = city_index

        # Advance the day and apply daily effects (interest, prices, holdings)
        self.day_service.advance_day()

        # Check if player reached wealth threshold to unlock investments
        investments_unlock_modal = None
        try:
            from merchant_tycoon.config import SETTINGS
            # Calculate current wealth (cash + bank + portfolio)
            cash = int(getattr(self.state, "cash", 0))
            bank_balance = int(getattr(self.state.bank, "balance", 0))
            portfolio_value = 0
            try:
                portfolio = getattr(self.state, "portfolio", {}) or {}
                asset_prices = getattr(self.investments_service, "asset_prices", {})
                for symbol, qty in portfolio.items():
                    price = int(asset_prices.get(symbol, 0))
                    portfolio_value += qty * price
            except Exception:
                pass
            current_wealth = cash + bank_balance + portfolio_value

            # Get threshold and check unlock
            threshold = int(getattr(SETTINGS.investments, "min_wealth_to_unlock_trading", 0))
            just_unlocked = self.state.check_and_update_peak_wealth(current_wealth, threshold)

            # Prepare modal message if just unlocked
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

        # Return travel result with optional modals
        # dividend_modal is None if no dividend, or modal message string if dividend paid
        # investments_unlock_modal is None if not unlocked, or message string if just unlocked
        return True, msg, events_list, dividend_modal, investments_unlock_modal
