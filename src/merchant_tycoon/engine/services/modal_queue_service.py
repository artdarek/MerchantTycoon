"""Modal queue manager for showing sequential modals after travel and other events.

Renamed from ModalQueue to ModalQueueService and moved under engine/services
to better reflect its role as engine-side presentation orchestration used by
multiple services (travel/day advance, lotto, unlocks).
"""

from typing import Any


class ModalQueueService:
    """Manages a queue of modals to be shown sequentially.

    Usage:
        queue = ModalQueueService()
        queue.add("Congratulations! Unlocked!", "gain")
        queue.add([("Good news!", "gain"), ("Bad news!", "loss")], "neutral")
        queue.add("You had 1 winning ticket...", "gain")
        queue.process(app)  # Start showing modals
    """

    def __init__(self):
        self._queue: list[tuple[str, Any]] = []

    # --- Unified API ---
    def add(self, message: str, modal_type: str = "neutral", title: str | None = None) -> "ModalQueueService":
        """Add a single item to the modal queue.

        Args:
            message: Single message string to display (str only)
            modal_type: Visual type for this message. Accepts synonyms:
                - success/gain, error/loss, info/neutral
            title: Optional explicit title for the message. If None, the UI uses a default based on modal_type.

        Returns:
            Self for chaining
        """
        # Expect proper type passed: "gain", "loss", or "neutral"
        modal_type = (modal_type or "neutral").lower()

        # Default: simple event modal
        self._queue.append(("simple", {"message": message, "event_type": modal_type, "title": title}))
        return self

    def add_bulk(self, items: list[tuple[str, str]]) -> "ModalQueueService":
        """Add multiple items to the queue.

        Args:
            items: List of (message, event_type) tuples

        Returns:
            Self for chaining
        """
        for item in items or []:
            msg, et = item
            self._queue.append(("simple", {"message": msg, "event_type": et}))
        return self

    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._queue) == 0

    def process(self) -> list[tuple[str, Any]]:
        """Return the current queue for the UI to consume and clear internal state.

        The UI should call its own sequencing method with the returned list,
        e.g., `app._show_next_modal_in_queue(queue)`.
        """
        if not self._queue:
            return []
        queue = self._queue
        self._queue = []
        return queue

    def clear(self) -> None:
        """Clear the queue."""
        self._queue.clear()
        # no callbacks kept anymore
