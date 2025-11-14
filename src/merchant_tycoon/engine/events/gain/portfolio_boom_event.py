"""Portfolio boom event handler - player's held assets boom in value."""

import random
from typing import Optional, Tuple

from merchant_tycoon.engine.events.base import BaseEventHandler, EventType
from merchant_tycoon.engine.events.context import EventContext


class PortfolioBoomEventHandler(BaseEventHandler):
    """Portfolio boom event - player's held asset group booms 150-300%.

    Event details:
    - Affects one random asset type that player holds (stock/commodity/crypto)
    - All player's assets of that type boom 150-300%
    - Shows paper gain and affected assets
    - Requires investments_service for portfolio queries
    """

    @property
    def event_type(self) -> EventType:
        return "gain"

    @property
    def default_weight(self) -> float:
        return 3.0

    def can_trigger(self, context: EventContext) -> bool:
        """Can trigger if player has any portfolio holdings."""
        return bool(context.state.portfolio) and any(
            qty > 0 for qty in context.state.portfolio.values()
        )

    def trigger(self, context: EventContext) -> Optional[Tuple[str, EventType]]:
        """Execute portfolio boom event."""
        if not context.investments_service:
            return None

        # Get asset types player currently holds
        try:
            player_types = context.investments_service.get_player_asset_types()
        except Exception:
            return None

        if not player_types:
            return None

        # Select random asset type from player's holdings
        chosen_type = random.choice(player_types)

        # Get player's assets of this type
        try:
            player_symbols = context.investments_service.get_player_assets_by_type(chosen_type)
        except Exception:
            return None

        if not player_symbols:
            return None

        # Boom prices 150-300%
        mult = random.uniform(1.5, 3.0)
        affected = []
        total_gain = 0

        for symbol in player_symbols:
            qty = context.state.portfolio.get(symbol, 0)
            old_price = context.initial_asset_prices.get(symbol, 0)

            if old_price > 0 and qty > 0:
                new_price = int(old_price * mult)
                gain = (new_price - old_price) * qty
                total_gain += gain
                affected.append(f"{symbol}: ${old_price:,} → ${new_price:,}")

        if not affected or total_gain <= 0:
            return None

        pct_change = int((mult - 1) * 100)
        sample = ', '.join(affected[:3])
        more = f" (+{len(affected) - 3} more)" if len(affected) > 3 else ""

        return (
            f"💰 PORTFOLIO BOOM! Your {chosen_type}s surge +{pct_change}%! "
            f"Paper gain: ${total_gain:,}. {sample}{more}",
            "gain"
        )
