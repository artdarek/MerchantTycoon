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
    def add(self, message: Any, modal_type: str = "neutral", title: str | None = None) -> "ModalQueueService":
        """Add an item to the modal queue using a unified API.

        Args:
            message: Content to display. Can be:
                - str: a simple message shown via EventModal
                - list[tuple[str, str]]: events sequence as (message, type)
              Note: other list types are not handled here; build a summary string in the service and pass it as str.
            modal_type: Visual type for simple messages. Accepts synonyms:
                - success/gain, error/loss, info/neutral
            title: Optional explicit title for simple messages. If None, the UI uses a default based on modal_type.

        Returns:
            Self for chaining
        """
        # Normalize type synonyms
        t = (modal_type or "neutral").lower()
        if t in ("success", "ok", "positive"):
            t = "gain"
        elif t in ("error", "fail", "negative"):
            t = "loss"
        elif t in ("info", "information"):
            t = "neutral"

        # Auto-detect structured payloads
        if isinstance(message, list):
            # Events list: list of (msg, type) tuples → expand into simple items
            if message and isinstance(message[0], (tuple, list)) and len(message[0]) == 2:
                for (msg, etype) in message:
                    self._queue.append(("simple", {"message": msg, "event_type": (etype or t), "title": title}))
                return self

        # Default: simple event modal
        self._queue.append(("simple", {"message": message, "event_type": t, "title": title}))
        return self

    # Legacy add_* methods removed; use add(message, modal_type) only.

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
