"""Event context dataclass containing dependencies for event handlers."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from merchant_tycoon.engine.game_state import GameState
    from merchant_tycoon.domain.model.city import City
    from merchant_tycoon.engine.services.bank_service import BankService
    from merchant_tycoon.engine.services.goods_service import GoodsService
    from merchant_tycoon.engine.services.investments_service import InvestmentsService
    from merchant_tycoon.repositories import AssetsRepository, GoodsRepository


@dataclass
class EventContext:
    """Context object passed to event handlers containing all necessary dependencies.

    Attributes:
        state: Current game state with inventory, cash, portfolio, etc.
        initial_goods_prices: Snapshot of goods prices BEFORE event modifications.
                             Used for before/after price comparisons in event messages.
                             Format: {good_name: price}
        initial_asset_prices: Snapshot of asset prices BEFORE event modifications.
                             Used for before/after price comparisons in event messages.
                             Format: {symbol: price}
        city: Current destination city with travel event configuration
        bank_service: Service for bank operations (deposits, credits, transactions)
        goods_service: Service for goods operations (loss accounting, inventory management)
        investments_service: Service for investment operations (portfolio queries, asset info)
        assets_repo: Repository for asset data lookups (stocks, commodities, crypto)
        goods_repo: Repository for goods data lookups (all available goods)
    """

    state: "GameState"
    initial_goods_prices: dict[str, int]
    initial_asset_prices: dict[str, int]
    city: Optional["City"]
    bank_service: Optional["BankService"]
    goods_service: Optional["GoodsService"]
    investments_service: Optional["InvestmentsService"]
    assets_repo: "AssetsRepository"
    goods_repo: "GoodsRepository"
