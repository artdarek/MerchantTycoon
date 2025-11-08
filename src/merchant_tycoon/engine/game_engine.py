from typing import Dict, Optional

from merchant_tycoon.engine.game_state import GameState
from merchant_tycoon.config import SETTINGS
from merchant_tycoon.engine.services.bank_service import BankService
from merchant_tycoon.engine.services.goods_service import GoodsService
from merchant_tycoon.engine.services.investments_service import InvestmentsService
from merchant_tycoon.engine.services.travel_service import TravelService
from merchant_tycoon.engine.services.travel_events_service import TravelEventsService
from merchant_tycoon.engine.services.savegame_service import SavegameService
from merchant_tycoon.engine.services.clock_service import ClockService


class GameEngine:
    """Core game logic - Facade over specialized services"""

    def __init__(self):
        # Initialize game state
        self.state = GameState()
        try:
            self.state.cash = int(SETTINGS.game.start_cash)
        except Exception:
            pass
        # Initialize in-game calendar date
        try:
            if not getattr(self.state, "date", ""):
                start_date = getattr(SETTINGS.game, "start_date", "") or "2025-01-01"
                self.state.date = str(start_date)
        except Exception:
            pass

        # Initialize price dictionaries - all prices are integers
        self.prices: Dict[str, int] = {}
        self.previous_prices: Dict[str, int] = {}
        self.asset_prices: Dict[str, int] = {}
        self.previous_asset_prices: Dict[str, int] = {}

        # Initialize services
        self.clock_service = ClockService(self.state)
        self.bank_service = BankService(self.state, self.clock_service)
        self.goods_service = GoodsService(self.state, self.prices, self.previous_prices, self.clock_service)
        self.investments_service = InvestmentsService(self.state, self.asset_prices, self.previous_asset_prices, self.clock_service)
        # Event service for travel random encounters
        self.travel_events_service = TravelEventsService()
        self.travel_service = TravelService(
            self.state,
            self.bank_service,
            self.goods_service,
            self.investments_service,
            self.travel_events_service,
        )
        # Savegame service (persistence)
        self.savegame_service = SavegameService(self)

        # Generate initial prices
        self.generate_prices()
        self.generate_asset_prices()

        # Initialize bank last interest day to current day at start
        if self.state.bank.last_interest_day == 0:
            self.state.bank.last_interest_day = self.state.day


        # Ensure aggregate debt synchronized with loans list
        self.bank_service._sync_total_debt()

    # ---------- Lifecycle helpers ----------

    def reset_state(self) -> None:
        """Reset the engine to a fresh GameState and rebind all services.
        Keeps the same engine instance so UI references remain valid.
        """
        # Replace state object
        self.state = GameState()
        try:
            self.state.cash = int(SETTINGS.game.start_cash)
        except Exception:
            pass
        try:
            if not getattr(self.state, "date", ""):
                start_date = getattr(SETTINGS.game, "start_date", "") or "2025-01-01"
                self.state.date = str(start_date)
        except Exception:
            pass
        try:
            if not getattr(self.state, "date", ""):
                start_date = getattr(SETTINGS.game, "start_date", "") or "2025-01-01"
                self.state.date = str(start_date)
        except Exception:
            pass

        # Rebind service state references
        try:
            self.bank_service.state = self.state
        except Exception:
            pass
        try:
            self.goods_service.state = self.state
        except Exception:
            pass
        try:
            self.investments_service.state = self.state
        except Exception:
            pass
        try:
            self.travel_service.state = self.state
        except Exception:
            pass

        # Clear price dicts; services keep references to the same dict objects
        try:
            self.prices.clear()
            self.previous_prices.clear()
            self.asset_prices.clear()
            self.previous_asset_prices.clear()
        except Exception:
            self.prices = {}
            self.previous_prices = {}
            self.asset_prices = {}
            self.previous_asset_prices = {}

        # Initialize bank last interest day to current day
        if getattr(self.state.bank, "last_interest_day", 0) == 0:
            self.state.bank.last_interest_day = self.state.day

        # Ensure aggregate debt synchronized with loans list
        try:
            self.bank_service._sync_total_debt()
        except Exception:
            pass
        # Clear price history on reset
        try:
            self.state.price_history.clear()
        except Exception:
            self.state.price_history = {}

    # ---------- Global operations ----------

    def new_game(self) -> None:
        """Start a new game using a fresh GameState and regenerated prices."""
        self.reset_state()
        # Generate fresh prices
        try:
            self.generate_prices()
        except Exception:
            pass
        try:
            self.generate_asset_prices()
        except Exception:
            pass

    # ---------- Travel operations ----------

    def travel(self, city_index: int) -> tuple[bool, str, Optional[tuple[str, bool]]]:
        """Travel to a new city"""
        return self.travel_service.travel(city_index)

    # ---------- Bank operations ----------

    def randomize_daily_rates(self) -> None:
        """Randomize bank APR and loan APR offer"""
        self.bank_service.randomize_daily_rates()

    def deposit_to_bank(self, amount: int) -> tuple[bool, str]:
        """Deposit cash to bank account"""
        return self.bank_service.deposit_to_bank(amount)

    def withdraw_from_bank(self, amount: int) -> tuple[bool, str]:
        """Withdraw cash from bank account"""
        return self.bank_service.withdraw_from_bank(amount)

    def accrue_bank_interest(self) -> None:
        """Accrue and credit daily compounding bank interest"""
        self.bank_service.accrue_bank_interest()

    def take_loan(self, amount: int) -> tuple[bool, str]:
        """Take a loan from the bank"""
        return self.bank_service.take_loan(amount)

    def repay_loan_for(self, loan_id: int, amount: int) -> tuple[bool, str]:
        """Repay a specific loan by ID"""
        return self.bank_service.repay_loan_for(loan_id, amount)

    def repay_loan(self, amount: int) -> tuple[bool, str]:
        """Repay loan (legacy - oldest active loan)"""
        return self.bank_service.repay_loan(amount)

    # ---------- Goods operations ----------

    def generate_prices(self) -> None:
        """Generate random prices for current city"""
        self.goods_service.generate_prices()

    def buy(self, good_name: str, quantity: int) -> tuple[bool, str]:
        """Buy goods"""
        return self.goods_service.buy(good_name, quantity)

    def sell(self, good_name: str, quantity: int) -> tuple[bool, str]:
        """Sell goods using FIFO"""
        return self.goods_service.sell(good_name, quantity)

    # Cargo operations - delegate to GoodsService
    def extend_cargo(self) -> tuple:
        """Attempt to extend cargo capacity by 1 slot.
        Delegates to GoodsService.extend_cargo().
        Returns tuple as defined by the service.
        """
        return self.goods_service.extend_cargo()

    # ---------- Investment operation ----------

    def generate_asset_prices(self) -> None:
        """Generate random prices for stocks and commodities"""
        self.investments_service.generate_asset_prices()

    def buy_asset(self, symbol: str, quantity: int) -> tuple[bool, str]:
        """Buy stocks or commodities"""
        return self.investments_service.buy_asset(symbol, quantity)

    def sell_asset(self, symbol: str, quantity: int) -> tuple[bool, str]:
        """Sell stocks or commodities using FIFO"""
        return self.investments_service.sell_asset(symbol, quantity)
