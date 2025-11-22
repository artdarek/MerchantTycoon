from typing import Dict, Optional

from merchant_tycoon.engine.game_state import GameState
from merchant_tycoon.config import SETTINGS
from merchant_tycoon.engine.services.bank_service import BankService
from merchant_tycoon.engine.services.goods_service import GoodsService
from merchant_tycoon.engine.services.goods_cargo_service import GoodsCargoService
from merchant_tycoon.engine.services.investments_service import InvestmentsService
from merchant_tycoon.engine.services.travel_service import TravelService
from merchant_tycoon.engine.services.day_advance_service import DayAdvanceService
from merchant_tycoon.engine.services.travel_events_service import TravelEventsService
from merchant_tycoon.engine.services.savegame_service import SavegameService
from merchant_tycoon.engine.services.clock_service import ClockService
from merchant_tycoon.engine.services.messenger_service import MessengerService
from merchant_tycoon.engine.services.lotto_service import LottoService
from merchant_tycoon.engine.services.phone_service import PhoneService
from merchant_tycoon.engine.applets.wordle_applet import WordleApplet
from merchant_tycoon.engine.applets.snake_applet import SnakeApplet
from merchant_tycoon.engine.applets.close_ai_applet import CloseAIApplet
from merchant_tycoon.engine.applets.home_applet import HomeApplet
from merchant_tycoon.engine.applets.camera_applet import CameraApplet
from merchant_tycoon.engine.applets.whatsup_applet import WhatsUpApplet
from merchant_tycoon.repositories import (
    GoodsRepository,
    CitiesRepository,
    AssetsRepository,
    DifficultyRepository,
    WordleRepository,
)
from merchant_tycoon.engine.services.modal_queue_service import ModalQueueService


class GameEngine:
    """Core game logic - Facade over specialized services"""

    def __init__(self):
        # Initialize repositories first (encapsulate domain constants)
        self.goods_repo = GoodsRepository()
        self.cities_repo = CitiesRepository()
        self.assets_repo = AssetsRepository()
        self.difficulty_repo = DifficultyRepository()
        self.wordle_repo = WordleRepository()

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

        # Initialize modal queue for coordinating UI modals
        self.modal_queue = ModalQueueService()

        # Initialize services
        self.clock_service = ClockService(self.state)
        self.messenger = MessengerService(self.state, self.clock_service)

        # Wallet service for centralized cash operations
        from merchant_tycoon.engine.services.wallet_service import WalletService
        self.wallet_service = WalletService(self.state, self.clock_service, self.messenger)

        self.bank_service = BankService(self.state, self.clock_service, self.messenger, self.wallet_service)
        # Initialize cargo service before goods service (goods service depends on it)
        self.cargo_service = GoodsCargoService(self.state, self.goods_repo)
        self.goods_service = GoodsService(
            self.state,
            self.prices,
            self.previous_prices,
            self.goods_repo,
            self.cities_repo,
            self.clock_service,
            self.messenger,
            self.cargo_service,
            self.wallet_service
        )
        self.investments_service = InvestmentsService(
            self.state,
            self.asset_prices,
            self.previous_asset_prices,
            self.assets_repo,
            self.clock_service,
            self.messenger,
            self.bank_service,
            self.wallet_service
        )
        # Lotto service for daily lottery
        self.lotto_service = LottoService(
            self.state,
            self.messenger,
            self.wallet_service,
            modal_queue_service=self.modal_queue
        )
        # Phone service
        self.phone_service = PhoneService()
        # Mini-app services
        try:
            from merchant_tycoon.config import SETTINGS as _S
            _max = int(getattr(_S.phone, 'wordle_max_tries', 10))
            _val = bool(getattr(_S.phone, 'wordle_validate_in_dictionary', True))
        except Exception:
            _max, _val = 10, True
        self.wordle_applet = WordleApplet(self.wordle_repo, max_tries=_max, validate_in_dictionary=_val)
        self.wordle_applet.reset()

        # Snake service
        try:
            from merchant_tycoon.config import SETTINGS as _S
            _bonus_amt = int(getattr(_S.phone, 'snake_bonus_amount', 100))
            _bonus_growth = int(getattr(_S.phone, 'snake_bonus_growth', 2))
            _super_amt = int(getattr(_S.phone, 'snake_super_bonus_amount', 1000))
            _super_growth = int(getattr(_S.phone, 'snake_super_bonus_growth', 3))
            _speed_step = float(getattr(_S.phone, 'snake_super_bonus_speed_step', 0.2))
        except Exception:
            _bonus_amt, _bonus_growth, _super_amt, _super_growth, _speed_step = 100, 2, 1000, 3, 0.2
        self.snake_applet = SnakeApplet(
            width=24,
            height=14,
            wallet_service=self.wallet_service,
            messenger=self.messenger,
            bonus_amount=_bonus_amt,
            bonus_growth=_bonus_growth,
            super_bonus_amount=_super_amt,
            super_bonus_growth=_super_growth,
            super_bonus_speed_step=_speed_step,
        )

        # CloseAI service (share history list with PhoneService)
        try:
            from merchant_tycoon.config import SETTINGS as _S
            _settings = _S
        except Exception:  # pragma: no cover
            _settings = object()
        self.closeai_applet = CloseAIApplet(
            settings=_settings,
            history=self.phone_service.closeai_history,
            bank_service=self.bank_service,
            wallet_service=self.wallet_service,
            goods_service=self.goods_service,
            investments_service=self.investments_service,
            messenger=self.messenger,
            assets_repo=self.assets_repo,
            goods_repo=self.goods_repo,
        )
        # Non-game applets
        self.home_applet = HomeApplet()
        self.camera_applet = CameraApplet()
        self.whatsup_applet = WhatsUpApplet(self.messenger)
        # Event service for travel random encounters
        self.travel_events_service = TravelEventsService(self.assets_repo, self.goods_repo)
        # Day-advance service (daily tick independent of travel details)
        self.day_advance_service = DayAdvanceService(
            self.clock_service,
            self.bank_service,
            self.investments_service,
            self.goods_service,
        )
        self.travel_service = TravelService(
            self.state,
            self.bank_service,
            self.goods_service,
            self.investments_service,
            self.travel_events_service,
            self.cities_repo,
            self.day_advance_service,
            self.messenger,
            self.cargo_service,
            self.wallet_service,
            modal_queue_service=self.modal_queue,
        )
        # Savegame service (persistence) – inject exact dependencies
        self.savegame_service = SavegameService(
            self.state,
            self.prices,
            self.previous_prices,
            self.asset_prices,
            self.previous_asset_prices,
            self.bank_service,
            self.messenger,
        )

        # Provide references for cross-service credit capacity computation
        try:
            self.bank_service.investments_service = self.investments_service
            self.bank_service.asset_prices = self.asset_prices
            self.bank_service.assets_repo = self.assets_repo
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
        # Find the difficulty level using repository
        difficulty = self.difficulty_repo.get_by_name(difficulty_name)

        # If not found, use normal as fallback
        if not difficulty:
            difficulty = self.difficulty_repo.get_default()

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
            self.messenger.state = self.state
        except Exception:
            pass
        try:
            self.wallet_service.state = self.state
        except Exception:
            pass
        try:
            self.clock_service.state = self.state
        except Exception:
            pass
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
        try:
            self.lotto_service.state = self.state
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

        # Clear modal queue on reset
        try:
            self.modal_queue.clear()
        except Exception:
            self.modal_queue = ModalQueueService()

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

        # Rebind savegame service dependencies to the new state/dicts
        try:
            self.savegame_service.state = self.state
            self.savegame_service.prices = self.prices
            self.savegame_service.previous_prices = self.previous_prices
            self.savegame_service.asset_prices = self.asset_prices
            self.savegame_service.previous_asset_prices = self.previous_asset_prices
            self.savegame_service.bank_service = self.bank_service
            self.savegame_service.messenger = self.messenger
        except Exception:
            pass

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

    # ---------- Investments helpers ----------
