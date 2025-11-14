"""Contest Win event handler - player wins a random contest with tiered prizes."""

import random
from math import ceil
from typing import Optional, Tuple

from merchant_tycoon.engine.events.base import BaseEventHandler, EventType
from merchant_tycoon.engine.events.context import EventContext
from merchant_tycoon.config import SETTINGS


class ContestWinEventHandler(BaseEventHandler):
    """Contest Win event - player wins 1st/2nd/3rd place in a random contest.

    Event details:
    - Contest selected randomly from configurable list
    - Place (1st/2nd/3rd) selected with weighted probabilities (favors 3rd)
    - Prize calculation:
      * 1st place: base prize amount
      * 2nd place: ceil(base / 2)
      * 3rd place: ceil(base / 4)
    - Cash added directly to player's cash balance
    - Always eligible (no preconditions)
    """

    @property
    def event_type(self) -> EventType:
        return "gain"

    @property
    def default_weight(self) -> float:
        return 3.0

    def can_trigger(self, context: EventContext) -> bool:
        """Contest win can always trigger (no preconditions)."""
        return True

    def trigger(self, context: EventContext) -> Optional[Tuple[str, EventType]]:
        """Execute contest win event."""
        # Select random contest from configured list
        if not SETTINGS.events.contest_names:
            return None

        contest_name, base_prize = random.choice(SETTINGS.events.contest_names)

        # Select place based on weighted probabilities [1st, 2nd, 3rd]
        # Weights favor lower places (more 3rd place wins than 1st)
        places = ["1st", "2nd", "3rd"]
        place = random.choices(
            places,
            weights=SETTINGS.events.contest_place_weights,
            k=1
        )[0]

        # Calculate prize based on place
        if place == "1st":
            prize = base_prize
        elif place == "2nd":
            prize = ceil(base_prize / 2)
        else:  # 3rd
            prize = ceil(base_prize / 4)

        # Add cash to player
        context.state.cash += prize

        # Log to messenger if available
        if context.messenger:
            context.messenger.info(
                f"You won {place} place in {contest_name}! Prize: ${prize:,}.",
                tag="event"
            )

        return (
            f"🏆 CONTEST WIN! You won {place} place in {contest_name}! Prize: ${prize:,}",
            "gain"
        )