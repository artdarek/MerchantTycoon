"""Event handler registry for managing and selecting travel events."""

import random
from typing import List, Tuple, Optional, Set, Callable

from merchant_tycoon.engine.events.base import BaseEventHandler, EventType
from merchant_tycoon.engine.events.context import EventContext


class EventHandlerRegistry:
    """Registry for managing event handlers with weighted random selection.

    Responsibilities:
    - Register event handlers by category (loss/gain/neutral)
    - Select multiple events based on city configuration
    - Ensure no duplicate events in single trigger
    - Apply weighted random selection within each category
    """

    def __init__(self):
        """Initialize empty registry."""
        self.loss_handlers: List[BaseEventHandler] = []
        self.gain_handlers: List[BaseEventHandler] = []
        self.neutral_handlers: List[BaseEventHandler] = []

    def register(self, handler: BaseEventHandler) -> None:
        """Register an event handler in the appropriate category.

        Args:
            handler: Event handler instance to register
        """
        if handler.event_type == "loss":
            self.loss_handlers.append(handler)
        elif handler.event_type == "gain":
            self.gain_handlers.append(handler)
        elif handler.event_type == "neutral":
            self.neutral_handlers.append(handler)
        else:
            raise ValueError(f"Unknown event type: {handler.event_type}")

    def select_and_trigger_events(
        self,
        context: EventContext,
        loss_range: Tuple[int, int],
        gain_range: Tuple[int, int],
        neutral_range: Tuple[int, int],
    ) -> List[Tuple[str, EventType]]:
        """Select and trigger multiple events based on ranges.

        Args:
            context: Event context with game state and services
            loss_range: (min, max) number of loss events to trigger
            gain_range: (min, max) number of gain events to trigger
            neutral_range: (min, max) number of neutral events to trigger

        Returns:
            List of (message, event_type) tuples for triggered events.
            Events are shuffled for variety.
        """
        selected_events: List[Tuple[str, EventType]] = []
        used_handlers: Set[BaseEventHandler] = set()

        # Select loss events
        loss_count = random.randint(loss_range[0], loss_range[1])
        for _ in range(loss_count):
            result = self._select_and_trigger_one(
                self.loss_handlers,
                context,
                used_handlers
            )
            if result:
                selected_events.append(result)

        # Select gain events
        gain_count = random.randint(gain_range[0], gain_range[1])
        for _ in range(gain_count):
            result = self._select_and_trigger_one(
                self.gain_handlers,
                context,
                used_handlers
            )
            if result:
                selected_events.append(result)

        # Select neutral events
        neutral_count = random.randint(neutral_range[0], neutral_range[1])
        for _ in range(neutral_count):
            result = self._select_and_trigger_one(
                self.neutral_handlers,
                context,
                used_handlers
            )
            if result:
                selected_events.append(result)

        # Shuffle all events for variety
        random.shuffle(selected_events)
        return selected_events

    def _select_and_trigger_one(
        self,
        handler_pool: List[BaseEventHandler],
        context: EventContext,
        used_handlers: Set[BaseEventHandler]
    ) -> Optional[Tuple[str, EventType]]:
        """Select and trigger one event from handler pool.

        Uses weighted random selection among eligible handlers.
        Ensures no duplicate handlers in a single trigger session.

        Args:
            handler_pool: List of handlers to select from
            context: Event context
            used_handlers: Set of already-used handlers (mutated)

        Returns:
            (message, event_type) tuple if successful, None otherwise
        """
        # Filter eligible handlers:
        # - Not already used
        # - Weight > 0
        # - Preconditions satisfied (can_trigger)
        eligible = [
            h for h in handler_pool
            if h not in used_handlers
            and h.get_weight() > 0
            and h.can_trigger(context)
        ]

        if not eligible:
            return None

        # Calculate total weight for weighted selection
        total_weight = sum(h.get_weight() for h in eligible)
        if total_weight <= 0:
            return None

        # Weighted random selection
        pick = random.uniform(0, total_weight)
        cumulative = 0.0
        chosen = eligible[-1]  # Fallback to last

        for handler in eligible:
            cumulative += handler.get_weight()
            if pick <= cumulative:
                chosen = handler
                break

        # Trigger the chosen handler
        result = chosen.trigger(context)

        # Mark as used if successfully triggered
        if result:
            used_handlers.add(chosen)

        return result

    def get_all_handlers(self) -> List[BaseEventHandler]:
        """Get all registered handlers.

        Returns:
            List of all registered handlers (loss + gain + neutral)
        """
        return self.loss_handlers + self.gain_handlers + self.neutral_handlers

    def get_handlers_by_type(self, event_type: EventType) -> List[BaseEventHandler]:
        """Get all handlers of a specific type.

        Args:
            event_type: "loss", "gain", or "neutral"

        Returns:
            List of handlers of the specified type
        """
        if event_type == "loss":
            return self.loss_handlers.copy()
        elif event_type == "gain":
            return self.gain_handlers.copy()
        elif event_type == "neutral":
            return self.neutral_handlers.copy()
        else:
            return []
