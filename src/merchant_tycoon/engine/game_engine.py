from typing import Dict, Optional

from .game_state import GameState
from .bank_service import BankService
from .goods_service import GoodsService
from .investments_service import InvestmentsService
from .travel_service import TravelService


class GameEngine:
    """Core game logic - Facade over specialized services"""

    def __init__(self):
        # Initialize game state
        self.state = GameState()

        # Initialize price dictionaries - all prices are integers
        self.prices: Dict[str, int] = {}
        self.previous_prices: Dict[str, int] = {}
        self.asset_prices: Dict[str, int] = {}
        self.previous_asset_prices: Dict[str, int] = {}

        # Initialize services
        self.bank_service = BankService(self.state)
        self.goods_service = GoodsService(self.state, self.prices, self.previous_prices)
        self.investments_service = InvestmentsService(self.state, self.asset_prices, self.previous_asset_prices)
        self.travel_service = TravelService(
            self.state,
            self.bank_service,
            self.goods_service,
            self.investments_service,
        )

        # Generate initial prices
        self.generate_prices()
        self.generate_asset_prices()

        # Initialize bank last interest day to current day at start
        if self.state.bank.last_interest_day == 0:
            self.state.bank.last_interest_day = self.state.day

        # Sync legacy daily rate field from APR on startup for consistency
        try:
            _ = self.get_bank_daily_rate()
        except Exception:
            pass

        # Ensure aggregate debt synchronized with loans list
        self._sync_total_debt()

    # Legacy properties for backward compatibility
    @property
    def loan_apr_today(self) -> float:
        """Legacy property - delegates to bank_service"""
        return self.bank_service.loan_apr_today

    @loan_apr_today.setter
    def loan_apr_today(self, value: float):
        """Legacy property setter - delegates to bank_service"""
        self.bank_service.loan_apr_today = value

    @property
    def interest_rate(self) -> float:
        """Legacy property - delegates to bank_service"""
        return self.bank_service.interest_rate

    @interest_rate.setter
    def interest_rate(self, value: float):
        """Legacy property setter - delegates to bank_service"""
        self.bank_service.interest_rate = value

    # Bank operations - delegate to BankService
    def get_bank_daily_rate(self) -> float:
        """Return today's bank daily rate"""
        return self.bank_service.get_bank_daily_rate()

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

    def _sync_total_debt(self) -> int:
        """Sync aggregate debt from loans list"""
        return self.bank_service._sync_total_debt()

    # Goods operations - delegate to GoodsService
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

    # Investment operations - delegate to InvestmentsService
    def generate_asset_prices(self) -> None:
        """Generate random prices for stocks and commodities"""
        self.investments_service.generate_asset_prices()

    def buy_asset(self, symbol: str, quantity: int) -> tuple[bool, str]:
        """Buy stocks or commodities"""
        return self.investments_service.buy_asset(symbol, quantity)

    def sell_asset(self, symbol: str, quantity: int) -> tuple[bool, str]:
        """Sell stocks or commodities using FIFO"""
        return self.investments_service.sell_asset(symbol, quantity)

    # Travel operations - delegate to TravelService
    def travel(self, city_index: int) -> tuple[bool, str, Optional[tuple[str, bool]]]:
        """Travel to a new city"""
        return self.travel_service.travel(city_index)

    def _random_event(self) -> Optional[tuple[str, bool]]:
        """Generate a weighted random travel event"""
        return self.travel_service._random_event()
