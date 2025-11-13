"""Promotion event handler - random good gets 30-60% price discount."""

import random
from typing import Optional, Tuple

from merchant_tycoon.engine.events.base import BaseEventHandler, EventType
from merchant_tycoon.engine.events.context import EventContext
from merchant_tycoon.config import SETTINGS


class PromoEventHandler(BaseEventHandler):
    """Promotion event - one random good gets temporary price discount.

    Event details:
    - Random good selected from all available goods
    - Price reduced by 30-60% (multiplier 0.4-0.7)
    - Sets price_modifier in game state (affects next price generation)
    - Shows before/after prices using initial_goods_prices snapshot
    """

    @property
    def event_type(self) -> EventType:
        return "neutral"

    @property
    def default_weight(self) -> float:
        return 5.0

    def can_trigger(self, context: EventContext) -> bool:
        """Can always trigger (no preconditions)."""
        return True

    def trigger(self, context: EventContext) -> Optional[Tuple[str, EventType]]:
        """Execute promotion event."""
        # Get all available goods
        try:
            goods = [g.name for g in context.goods_repo.get_all()]
        except Exception:
            return None

        if not goods:
            return None

        # Select random good for promotion
        good = random.choice(goods)

        # Calculate discount multiplier (0.4 - 0.7 = 30-60% off)
        lo, hi = SETTINGS.events.promo_multiplier
        mult = random.uniform(lo, hi)

        # Set price modifier for next price generation
        context.state.price_modifiers[good] = mult

        # Show price before and after promotion using initial snapshot
        old_price = context.initial_goods_prices.get(good, 0)
        new_price = int(old_price * mult) if old_price > 0 else 0
        discount_pct = int((1 - mult) * 100)

        if old_price > 0 and new_price > 0:
            return (
                f"🏷️ PROMOTION! {good} price drops from ${old_price:,} to ${new_price:,} (−{discount_pct}%).",
                "neutral"
            )
        else:
            return (
                f"🏷️ PROMOTION! {good} will be cheaper today (−{discount_pct}%).",
                "neutral"
            )
