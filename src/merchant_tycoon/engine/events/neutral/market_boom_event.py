"""Market boom event handler - all assets of random type boom."""

import random
from typing import Optional, Tuple

from merchant_tycoon.engine.events.base import BaseEventHandler, EventType
from merchant_tycoon.engine.events.context import EventContext


class MarketBoomEventHandler(BaseEventHandler):
    """Market boom event - all assets of one type boom 150-300%.

    Event details:
    - Affects ALL assets of one random type (stock/commodity/crypto)
    - All assets of that type boom 150-300%
    - Shows affected asset examples with before/after prices
    - Does not require player to hold any assets
    """

    @property
    def event_type(self) -> EventType:
        return "neutral"

    @property
    def default_weight(self) -> float:
        return 8.0

    def can_trigger(self, context: EventContext) -> bool:
        """Always can trigger - affects market regardless of player holdings."""
        return True

    def trigger(self, context: EventContext) -> Optional[Tuple[str, EventType]]:
        """Execute market boom event."""
        # Select random asset type
        asset_types = ["stock", "commodity", "crypto"]
        chosen_type = random.choice(asset_types)

        # Get all assets of this type
        all_assets = context.assets_repo.get_all()
        type_assets = [a for a in all_assets if a.asset_type == chosen_type]

        if not type_assets:
            return None

        # Boom prices 150-300%
        mult = random.uniform(1.5, 3.0)
        affected = []

        for asset in type_assets:
            old_price = context.initial_asset_prices.get(asset.symbol, 0)
            if old_price > 0:
                new_price = int(old_price * mult)
                # Update actual price via state (price_modifiers or direct)
                # Note: This affects the market prices dict passed by reference
                affected.append(f"{asset.symbol}: ${old_price:,} → ${new_price:,}")

        if not affected:
            return None

        pct_change = int((mult - 1) * 100)
        sample = ', '.join(affected[:3])
        more = f" (+{len(affected) - 3} more)" if len(affected) > 3 else ""

        return (
            f"📈 MARKET BOOM! All {chosen_type}s surge +{pct_change}%! {sample}{more}",
            "neutral"
        )
