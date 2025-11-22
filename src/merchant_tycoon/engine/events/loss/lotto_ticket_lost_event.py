"""Lotto Ticket Lost event handler.

Removes one random active lotto ticket from the player's collection.
Loss-type travel event with small penalty interacting with the Lotto system.
"""

import random
from typing import Optional, Tuple

from merchant_tycoon.engine.events.base import BaseEventHandler, EventType
from merchant_tycoon.engine.events.context import EventContext


class LottoTicketLostEventHandler(BaseEventHandler):
    """Loss event: randomly lose one active lotto ticket (no refund)."""

    @property
    def event_type(self) -> EventType:
        return "loss"

    @property
    def default_weight(self) -> float:
        # Minor penalty, similar to other small loss events
        return 4.0

    def _get_active_tickets(self, context: EventContext):
        tickets = getattr(context.state, "lotto_tickets", []) or []
        return [t for t in tickets if getattr(t, "active", False)]

    def can_trigger(self, context: EventContext) -> bool:
        """Eligible when there is at least one active lotto ticket."""
        return len(self._get_active_tickets(context)) > 0

    def trigger(self, context: EventContext) -> Optional[Tuple[str, EventType]]:
        """Randomly remove one active lotto ticket and log the loss."""
        active = self._get_active_tickets(context)
        if not active:
            return None

        ticket = random.choice(active)
        numbers = list(getattr(ticket, "numbers", []) or [])
        bullets = " • ".join(str(n) for n in numbers)

        # Remove from the player's ticket list (by identity)
        try:
            context.state.lotto_tickets.remove(ticket)
        except Exception:
            # Fallback: mark inactive if removal fails unexpectedly
            try:
                ticket.active = False
            except Exception:
                pass

        # Messenger entry (separate from event modal log)
        try:
            # Messenger logging handled centrally in TravelService
            pass
        except Exception:
            pass

        message = (
            "🎟️ LOTTO TICKET LOST\n"
            "One of your lotto tickets was lost today.\n"
            f"The following ticket disappeared:\n{bullets}"
        )
        return message, "loss"
