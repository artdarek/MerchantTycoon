"""Travel events service - refactored to use modular event handlers.

This is the new implementation using EventHandlerRegistry and individual event handlers.
Once complete, this will replace travel_events_service.py
"""

import random
from typing import TYPE_CHECKING, List, Tuple, Optional, Literal

from merchant_tycoon.domain.model.city import City
from merchant_tycoon.engine.events.registry import EventHandlerRegistry
from merchant_tycoon.engine.events.context import EventContext

# Import all event handlers
from merchant_tycoon.engine.events.loss import (
    RobberyEventHandler,
    FireEventHandler,
    FloodEventHandler,
    DefectiveBatchEventHandler,
    CustomsDutyEventHandler,
    StolenGoodsEventHandler,
    CashDamageEventHandler,
    PortfolioCrashEventHandler,
    LottoTicketLostEventHandler,
)
from merchant_tycoon.engine.events.gain import (
    ContestWinEventHandler,
    DividendEventHandler,
    BankCorrectionEventHandler,
    PortfolioBoomEventHandler,
)
from merchant_tycoon.engine.events.neutral import (
    PromoEventHandler,
    OversupplyEventHandler,
    ShortageEventHandler,
    LoyalDiscountEventHandler,
    MarketBoomEventHandler,
    MarketCrashEventHandler,
)

if TYPE_CHECKING:
    from merchant_tycoon.repositories import AssetsRepository, GoodsRepository
    from merchant_tycoon.engine.game_state import GameState
    from merchant_tycoon.engine.services.bank_service import BankService
    from merchant_tycoon.engine.services.goods_service import GoodsService
    from merchant_tycoon.engine.services.investments_service import InvestmentsService
    from merchant_tycoon.engine.services.messenger_service import MessengerService

# Event type literals
EventType = Literal["loss", "gain", "neutral"]


class TravelEventsService:
    """Weighted random travel events service.

    Orchestrates event triggering using registered event handlers.
    Delegates event logic to individual handler classes for better modularity.

    Architecture:
    - EventHandlerRegistry: Manages all event handlers by category
    - BaseEventHandler: Abstract base for individual events
    - EventContext: Dependency container passed to handlers
    """

    def __init__(
        self,
        assets_repository: "AssetsRepository",
        goods_repository: "GoodsRepository"
    ):
        """Initialize TravelEventsService with required repositories.

        Args:
            assets_repository: Repository for asset lookups.
            goods_repository: Repository for goods lookups.
        """
        self.assets_repo = assets_repository
        self.goods_repo = goods_repository

        # Initialize event registry and register all handlers
        self.registry = EventHandlerRegistry()
        self._register_all_handlers()

    def _register_all_handlers(self):
        """Register all 18 event handlers with the registry.

        Loss events (8): robbery, fire, flood, defective_batch, customs_duty,
                        stolen_goods, cash_damage, portfolio_crash
        Gain events (4): contest_win, dividend, bank_correction, portfolio_boom
        Neutral events (6): promo, oversupply, shortage, loyal_discount,
                           market_boom, market_crash
        """
        # Register all loss handlers (8)
        self.registry.register(RobberyEventHandler())
        self.registry.register(FireEventHandler())
        self.registry.register(FloodEventHandler())
        self.registry.register(DefectiveBatchEventHandler())
        self.registry.register(CustomsDutyEventHandler())
        self.registry.register(StolenGoodsEventHandler())
        self.registry.register(CashDamageEventHandler())
        self.registry.register(PortfolioCrashEventHandler())
        # New minor loss event: lose one lotto ticket if any active
        self.registry.register(LottoTicketLostEventHandler())

        # Register all gain handlers (4)
        self.registry.register(ContestWinEventHandler())
        self.registry.register(DividendEventHandler())
        self.registry.register(BankCorrectionEventHandler())
        self.registry.register(PortfolioBoomEventHandler())

        # Register all neutral handlers (6)
        self.registry.register(PromoEventHandler())
        self.registry.register(OversupplyEventHandler())
        self.registry.register(ShortageEventHandler())
        self.registry.register(LoyalDiscountEventHandler())
        self.registry.register(MarketBoomEventHandler())
        self.registry.register(MarketCrashEventHandler())

    def trigger(
        self,
        state: "GameState",
        prices: dict,
        asset_prices: dict,
        city: Optional[City] = None,
        bank_service: Optional["BankService"] = None,
        goods_service: Optional["GoodsService"] = None,
        investments_service: Optional["InvestmentsService"] = None,
        messenger: Optional["MessengerService"] = None
    ) -> List[Tuple[str, EventType]]:
        """Trigger multiple weighted random travel events based on city configuration.

        Parameters:
            state: Game state object with inventory, cash, bank, etc.
            prices: dict of current goods prices {good_name: price} - snapshot before events
            asset_prices: dict of asset prices {symbol: price} - snapshot before events
            city: Optional City object with travel_events config
            bank_service: optional bank service to credit amounts
            goods_service: optional goods service for loss accounting
            investments_service: optional investments service for portfolio events
            messenger:  optional messanger service

        Returns:
            List of event tuples (message, event_type). Empty list if no events occur.
            event_type can be: "loss", "gain", or "neutral"

        Raises:
            ValueError: If city is None or missing travel_events config
        """
        # Validate city config (required)
        if not city or not hasattr(city, 'travel_events'):
            raise ValueError("City with travel_events config is required for trigger()")

        probability = float(city.travel_events.probability)

        # Overall chance that any event occurs this travel
        if random.random() > probability:
            return []

        # Create event context with clear parameter names
        context = EventContext(
            state=state,
            initial_goods_prices=prices or {},  # Snapshot for before/after comparison
            initial_asset_prices=asset_prices or {},  # Snapshot for before/after comparison
            city=city,
            bank_service=bank_service,
            goods_service=goods_service,
            investments_service=investments_service,
            messenger=messenger,
            assets_repo=self.assets_repo,
            goods_repo=self.goods_repo,
        )

        # Get city event configuration
        cfg = city.travel_events
        loss_min, loss_max = cfg.loss_min, cfg.loss_max
        gain_min, gain_max = cfg.gain_min, cfg.gain_max
        neutral_min = getattr(cfg, 'neutral_min', 0)
        neutral_max = getattr(cfg, 'neutral_max', 2)

        # Delegate to registry for event selection and triggering
        return self.registry.select_and_trigger_events(
            context=context,
            loss_range=(loss_min, loss_max),
            gain_range=(gain_min, gain_max),
            neutral_range=(neutral_min, neutral_max),
        )
