"""Shortage event handler - random good has very high prices."""

import random
from typing import Optional, Tuple

from merchant_tycoon.engine.events.base import BaseEventHandler, EventType
from merchant_tycoon.engine.events.context import EventContext
from merchant_tycoon.config import SETTINGS


class ShortageEventHandler(BaseEventHandler):
    """Shortage event - random good spikes to 150-250% of base price.

    Event details:
    - Selects one random good from current city's offerings
    - Sets price modifier to 150-250% (shortage)
    - Shows before/after prices using initial_goods_prices
    - No goods or cash cost to player
    """

    @property
    def event_type(self) -> EventType:
        return "neutral"

    @property
    def default_weight(self) -> float:
        return 10.0

    def can_trigger(self, context: EventContext) -> bool:
        """Can trigger if city has any goods available."""
        return context.city is not None and bool(context.city.goods)

    def trigger(self, context: EventContext) -> Optional[Tuple[str, EventType]]:
        """Execute shortage event."""
        if context.city is None or not context.city.goods:
            return None

        goods = list(context.city.goods)
        if not goods:
            return None

        # Select random good and apply shortage multiplier
        good = random.choice(goods)
        lo, hi = SETTINGS.events.shortage_mult
        mult = random.uniform(lo, hi)
        context.state.price_modifiers[good] = mult

        # Show price change
        old_price = context.initial_goods_prices.get(good, 0)
        new_price = int(old_price * mult) if old_price > 0 else 0
        increase_pct = int((mult - 1) * 100)

        if old_price > 0 and new_price > 0:
            return (
                f"⚠️ SHORTAGE! {good} supply critically low! "
                f"Price surges from ${old_price:,} to ${new_price:,} (+{increase_pct}%).",
                "neutral"
            )

        return (f"⚠️ SHORTAGE! {good} prices spike due to supply crisis.", "neutral")
