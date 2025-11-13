"""Base event handler abstract class for all travel events."""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, Literal

from merchant_tycoon.engine.events.context import EventContext

# Event type literals
EventType = Literal["loss", "gain", "neutral"]


class BaseEventHandler(ABC):
    """Abstract base class for all travel event handlers.

    Each event handler encapsulates:
    - Event type classification (loss/gain/neutral)
    - Weight for random selection
    - Precondition check (can this event occur?)
    - Event execution logic (what happens when triggered?)

    Subclasses must implement all abstract methods and properties.
    """

    @property
    @abstractmethod
    def event_type(self) -> EventType:
        """Return the event category: 'loss', 'gain', or 'neutral'.

        Returns:
            EventType: The category this event belongs to
        """
        pass

    @property
    @abstractmethod
    def default_weight(self) -> float:
        """Default weight for weighted random selection.

        Higher weights make the event more likely to be selected.
        Weight of 0.0 disables the event.

        Returns:
            float: Default weight (typically 1.0 - 10.0)
        """
        pass

    @abstractmethod
    def can_trigger(self, context: EventContext) -> bool:
        """Check if this event can occur given current game state.

        This method should be side-effect free (no state modifications).
        Used to filter eligible events before weighted selection.

        Args:
            context: Event context with game state and services

        Returns:
            bool: True if event is applicable, False otherwise

        Examples:
            - Robbery requires non-empty inventory
            - Dividend requires holding stocks
            - Price events can always trigger
        """
        pass

    @abstractmethod
    def trigger(self, context: EventContext) -> Optional[Tuple[str, EventType]]:
        """Execute the event and return result message.

        This method performs the actual event logic:
        - Modifies game state (inventory, cash, prices, etc.)
        - Calls services for complex operations
        - Generates user-facing message

        Args:
            context: Event context with game state and services

        Returns:
            Optional[Tuple[str, EventType]]: Tuple of (message, event_type) if successful,
                                            None if event cannot be applied

        Note:
            Even if can_trigger() returns True, trigger() may still return None
            if runtime conditions prevent execution (e.g., random selection
            results in zero quantity).
        """
        pass

    def get_weight(self) -> float:
        """Get the effective weight for this event.

        Override this method to implement dynamic weights based on game state.
        By default, returns the static default_weight.

        Returns:
            float: Effective weight for random selection
        """
        return self.default_weight
