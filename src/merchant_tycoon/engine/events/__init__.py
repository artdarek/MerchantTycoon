"""Travel events system with modular event handlers."""

from merchant_tycoon.engine.events.base import BaseEventHandler, EventType
from merchant_tycoon.engine.events.context import EventContext

__all__ = [
    "BaseEventHandler",
    "EventContext",
    "EventType",
]
