"""Modal queue manager for showing sequential modals after travel and other events."""

from typing import Optional, Callable, Any


class ModalQueue:
    """Manages a queue of modals to be shown sequentially.

    Usage:
        queue = ModalQueue()
        queue.add("Congratulations! Unlocked!", "gain")
        queue.add("Received $500 dividend", "gain")
        queue.add([("Good news!", "gain"), ("Bad news!", "loss")], "neutral")
        queue.add("You had 1 winning ticket...", "gain")
        queue.process(app)  # Start showing modals
    """

    def __init__(self):
        self._queue: list[tuple[str, Any]] = []

    # --- Unified API ---
    def add(self, message: Any, modal_type: str = "neutral", title: str | None = None) -> "ModalQueue":
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
            # Events list: list of (msg, type) tuples
            if message and isinstance(message[0], (tuple, list)) and len(message[0]) == 2:
                if message:
                    self._queue.append(("events", message))
                return self

            # (no other list types handled here; callers should format message text)

        # Default: simple event modal
        self._queue.append(("simple", {"message": message, "event_type": t, "title": title}))
        return self

    # Legacy add_* methods removed; use add(message, modal_type) only.

    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._queue) == 0

    def process(self, app) -> None:
        """Start processing the modal queue.

        Args:
            app: MerchantTycoon app instance with _show_next_modal_in_queue method
        """
        if self._queue:
            app._show_next_modal_in_queue(self._queue)

    def clear(self) -> None:
        """Clear the queue."""
        self._queue.clear()
        # no callbacks kept anymore
