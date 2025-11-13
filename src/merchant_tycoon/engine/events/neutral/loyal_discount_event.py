"""Loyal customer discount event handler - special 95% discount."""

import random
from typing import Optional, Tuple

from merchant_tycoon.engine.events.base import BaseEventHandler, EventType
from merchant_tycoon.engine.events.context import EventContext
from merchant_tycoon.config import SETTINGS


class LoyalDiscountEventHandler(BaseEventHandler):
    """Loyal customer discount event - random good gets 95% discount.

    Event details:
    - Selects one random good from current city's offerings
    - Sets price modifier to 5% (95% discount)
    - Shows before/after prices using initial_goods_prices
    - No goods or cash cost to player
    """

    @property
    def event_type(self) -> EventType:
        return "neutral"

    @property
    def default_weight(self) -> float:
        return 2.0  # Lower weight - this is a very rare/good event

    def can_trigger(self, context: EventContext) -> bool:
        """Can trigger if city has any goods available."""
        return context.city is not None and bool(context.city.goods)

    def trigger(self, context: EventContext) -> Optional[Tuple[str, EventType]]:
        """Execute loyal customer discount event."""
        if context.city is None or not context.city.goods:
            return None

        goods = list(context.city.goods)
        if not goods:
            return None

        # Select random good and apply loyal customer discount
        good = random.choice(goods)
        mult = SETTINGS.events.loyal_discount_mult
        context.state.price_modifiers[good] = mult

        # Show price change
        old_price = context.initial_goods_prices.get(good, 0)
        new_price = int(old_price * mult) if old_price > 0 else 0
        discount_pct = int((1 - mult) * 100)

        if old_price > 0 and new_price > 0:
            return (
                f"⭐ LOYAL CUSTOMER! Special {discount_pct}% discount on {good}! "
                f"Price drops from ${old_price:,} to ${new_price:,}.",
                "neutral"
            )

        return (f"⭐ LOYAL CUSTOMER! Special discount on {good}!", "neutral")
