"""Cash damage event handler - accident costs money."""

import random
from typing import Optional, Tuple

from merchant_tycoon.engine.events.base import BaseEventHandler, EventType
from merchant_tycoon.engine.events.context import EventContext
from merchant_tycoon.config import SETTINGS


class CashDamageEventHandler(BaseEventHandler):
    """Cash damage event - generic accident costs cash.

    Event details:
    - Damage scaled by current cash (1-5%)
    - Minimum damage: configured in settings (default $50)
    - Maximum damage: configured in settings (default $5000)
    - Deducted from cash (can go negative)
    """

    @property
    def event_type(self) -> EventType:
        return "loss"

    @property
    def default_weight(self) -> float:
        return 4.0

    def can_trigger(self, context: EventContext) -> bool:
        """Can trigger if player has cash."""
        return int(context.state.cash) > 0

    def trigger(self, context: EventContext) -> Optional[Tuple[str, EventType]]:
        """Execute cash damage event."""
        # Calculate damage as percentage of current cash
        lo, hi = SETTINGS.events.cash_damage_pct
        base = int(context.state.cash * random.uniform(lo, hi))

        # Clamp to min/max configured values
        damage = max(
            SETTINGS.events.cash_damage_min,
            min(SETTINGS.events.cash_damage_max, base)
        )

        if damage <= 0:
            return None

        # Deduct from cash
        context.state.cash -= damage

        return (f"💥 ACCIDENT! Paid ${damage:,} in damages.", "loss")
