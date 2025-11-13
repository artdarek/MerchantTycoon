"""Lottery event handler - player wins lottery with tiered rewards."""

import random
from typing import Optional, Tuple

from merchant_tycoon.engine.events.base import BaseEventHandler, EventType
from merchant_tycoon.engine.events.context import EventContext
from merchant_tycoon.config import SETTINGS


class LotteryEventHandler(BaseEventHandler):
    """Lottery win event - tiered rewards based on numbers matched.

    Event details:
    - Multiple tiers: 3, 4, 5, or 6 numbers matched
    - Weighted selection favors lower tiers (more 3s than 6s)
    - Rewards range from $200 (3 numbers) to $20,000 (6 numbers)
    - Cash added directly to player's cash balance
    """

    @property
    def event_type(self) -> EventType:
        return "gain"

    @property
    def default_weight(self) -> float:
        return 3.0

    def can_trigger(self, context: EventContext) -> bool:
        """Lottery can always trigger (no preconditions)."""
        return True

    def trigger(self, context: EventContext) -> Optional[Tuple[str, EventType]]:
        """Execute lottery win event."""
        # Select tier based on weighted probabilities
        tier = random.choices(
            SETTINGS.events.lottery_tiers,
            weights=SETTINGS.events.lottery_weights,
            k=1
        )[0]

        # Get reward range for this tier
        low, high = SETTINGS.events.lottery_reward_ranges.get(tier, (200, 600))
        win = random.randint(low, high)

        # Add cash to player
        context.state.cash += win

        return (f"🎟️ LOTTERY! You matched {tier} numbers and won ${win:,}!", "gain")
