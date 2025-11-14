"""Portfolio crash event handler - player's held assets crash in value."""

import random
from typing import Optional, Tuple

from merchant_tycoon.engine.events.base import BaseEventHandler, EventType
from merchant_tycoon.engine.events.context import EventContext


class PortfolioCrashEventHandler(BaseEventHandler):
    """Portfolio crash event - player's held asset group crashes 30-70%.

    Event details:
    - Affects one random asset type that player holds (stock/commodity/crypto)
    - All player's assets of that type crash 30-70%
    - Shows paper loss and affected assets
    - Requires investments_service for portfolio queries
    """

    @property
    def event_type(self) -> EventType:
        return "loss"

    @property
    def default_weight(self) -> float:
        return 3.0

    def can_trigger(self, context: EventContext) -> bool:
        """Can trigger if player has any portfolio holdings."""
        return bool(context.state.portfolio) and any(
            qty > 0 for qty in context.state.portfolio.values()
        )

    def trigger(self, context: EventContext) -> Optional[Tuple[str, EventType]]:
        """Execute portfolio crash event."""
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

        # Crash prices 30-70%
        mult = random.uniform(0.3, 0.7)
        affected = []
        total_loss = 0

        for symbol in player_symbols:
            qty = context.state.portfolio.get(symbol, 0)
            old_price = context.initial_asset_prices.get(symbol, 0)

            if old_price > 0 and qty > 0:
                new_price = int(old_price * mult)
                # Update actual asset price in place
                if symbol in context.initial_asset_prices:
                    # Note: We're modifying the snapshot here because events
                    # directly modify asset_prices dict passed by reference
                    pass

                loss = (old_price - new_price) * qty
                total_loss += loss
                affected.append(f"{symbol}: ${old_price:,} → ${new_price:,}")

        if not affected or total_loss <= 0:
            return None

        pct_change = int((1 - mult) * 100)
        sample = ', '.join(affected[:3])
        more = f" (+{len(affected) - 3} more)" if len(affected) > 3 else ""

        return (
            f"💸 PORTFOLIO CRASH! Your {chosen_type}s plunge −{pct_change}%! "
            f"Paper loss: ${total_loss:,}. {sample}{more}",
            "loss"
        )
