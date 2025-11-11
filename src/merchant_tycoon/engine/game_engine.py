from typing import Dict, Optional

from merchant_tycoon.engine.game_state import GameState
from merchant_tycoon.config import SETTINGS
from merchant_tycoon.domain.game_difficulty_levels import GAME_DIFFICULTY_LEVELS
from merchant_tycoon.engine.services.bank_service import BankService
from merchant_tycoon.engine.services.goods_service import GoodsService
from merchant_tycoon.engine.services.goods_cargo_service import GoodsCargoService
from merchant_tycoon.engine.services.investments_service import InvestmentsService
from merchant_tycoon.engine.services.travel_service import TravelService
from merchant_tycoon.engine.services.travel_events_service import TravelEventsService
from merchant_tycoon.engine.services.savegame_service import SavegameService
from merchant_tycoon.engine.services.clock_service import ClockService
from merchant_tycoon.engine.services.messenger_service import MessengerService


class GameEngine:
    """Core game logic - Facade over specialized services"""

    def __init__(self):
        # Initialize game state with default difficulty
        self.state = GameState()
        self._apply_difficulty(SETTINGS.game.default_difficulty)
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
        self.messenger = MessengerService(self.state, self.clock_service)
        self.bank_service = BankService(self.state, self.clock_service, self.messenger)
        # Initialize cargo service before goods service (goods service depends on it)
        self.cargo_service = GoodsCargoService(self.state)
        self.goods_service = GoodsService(
            self.state,
            self.prices,
            self.previous_prices,
            self.clock_service,
            self.messenger,
            self.cargo_service
        )
        self.investments_service = InvestmentsService(self.state, self.asset_prices, self.previous_asset_prices, self.clock_service, self.messenger)
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

        # Provide references for cross-service credit capacity computation
        try:
            self.bank_service.investments_service = self.investments_service
            self.bank_service.asset_prices = self.asset_prices
        except Exception:
            pass

        # Generate initial prices
        self.goods_service.generate_prices()
        self.investments_service.generate_asset_prices()

        # Initialize bank last interest day to current day at start
        if self.state.bank.last_interest_day == 0:
            self.state.bank.last_interest_day = self.state.day

        # Ensure aggregate debt synchronized with loans list
        self.bank_service._sync_total_debt()

    # ---------- Lifecycle helpers ----------

    def _apply_difficulty(self, difficulty_name: str) -> None:
        """Apply difficulty level settings to the current game state."""
        # Find the difficulty level
        difficulty = None
        for level in GAME_DIFFICULTY_LEVELS:
            if level.name == difficulty_name:
                difficulty = level
                break

        # If not found, use normal as fallback
        if not difficulty:
            for level in GAME_DIFFICULTY_LEVELS:
                if level.name == "normal":
                    difficulty = level
                    break

        # Apply difficulty settings
        if difficulty:
            self.state.cash = difficulty.start_cash
            self.state.max_inventory = difficulty.start_capacity

    def reset_state(self, difficulty_name: Optional[str] = None) -> None:
        """Reset the engine to a fresh GameState and rebind all services.
        Keeps the same engine instance so UI references remain valid.

        Args:
            difficulty_name: Name of difficulty level to use. If None, uses default from settings.
        """
        # Replace state object
        self.state = GameState()

        # Apply difficulty level
        if difficulty_name is None:
            difficulty_name = SETTINGS.game.default_difficulty
        self._apply_difficulty(difficulty_name)

        # Initialize in-game calendar date
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
            self.cargo_service.state = self.state
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
            self.goods_service.generate_prices()
        except Exception:
            pass
        try:
            self.investments_service.generate_asset_prices()
        except Exception:
            pass
