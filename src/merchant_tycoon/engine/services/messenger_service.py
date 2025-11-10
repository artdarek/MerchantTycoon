from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

from merchant_tycoon.config import SETTINGS

if TYPE_CHECKING:
    from merchant_tycoon.engine.game_state import GameState
    from merchant_tycoon.engine.services.clock_service import ClockService


class MessengerService:
    """Centralized message log manager.

    Stores structured entries in state.messages. Each entry is a dict:
      {"ts": ISO datetime, "text": str, "level": str, "tag": str, "ctx": dict}
    Only "ts" and "text" are mandatory.
    """

    def __init__(self, state: "GameState", clock: "ClockService"):
        self.state = state
        self.clock = clock
        if not hasattr(self.state, "messages") or self.state.messages is None:
            self.state.messages = []

    # --- Public API ---
    def append(self, text: str, level: str = "info", tag: Optional[str] = None, ctx: Optional[Dict] = None) -> None:
        ts_iso = self.clock.now().isoformat(timespec="seconds")
        entry = {"ts": ts_iso, 
                 "text": str(text),
                 "level": str(level or "info"),
                 "tag": str(tag or ""),
                 "ctx": dict(ctx or {}),
                 }
        # Append as newest and enforce limit
        msgs: List[Dict] = getattr(self.state, "messages", []) or []
        msgs.append(entry)
        limit = int(getattr(SETTINGS.saveui, "messages_save_limit", 10))
        if len(msgs) > limit:
            # keep the last `limit` entries (oldest removed)
            msgs = msgs[-limit:]
        self.state.messages = msgs

    def info(self, text: str, tag: Optional[str] = None, ctx: Optional[Dict] = None) -> None:
        self.append(text, level="info", tag=tag, ctx=ctx)

    def debug(self, text: str, tag: Optional[str] = None, ctx: Optional[Dict] = None) -> None:
        """Log a debug-level message (system/technical, not core gameplay)."""
        self.append(text, level="debug", tag=tag, ctx=ctx)

    def warn(self, text: str, tag: Optional[str] = None, ctx: Optional[Dict] = None) -> None:
        self.append(text, level="warn", tag=tag, ctx=ctx)

    def error(self, text: str, tag: Optional[str] = None, ctx: Optional[Dict] = None) -> None:
        self.append(text, level="error", tag=tag, ctx=ctx)

    def get_entries(self, limit: Optional[int] = None) -> List[Dict]:
        msgs: List[Dict] = getattr(self.state, "messages", []) or []
        if limit is None:
            return list(msgs)
        return list(msgs[-int(limit):])

    def set_entries(self, entries: List[Dict]) -> None:
        limit = int(getattr(SETTINGS.saveui, "messages_save_limit", 10))
        # expect list of dicts {ts,text,...}
        msgs = [
            {"ts": str(e.get("ts", "")), "text": str(e.get("text", "")),
             "level": str(e.get("level", "info")), "tag": str(e.get("tag", "")),
             "ctx": dict(e.get("ctx", {}))}
            for e in (entries or [])
        ]
        self.state.messages = msgs[-limit:]

    def clear(self) -> None:
        self.state.messages = []
