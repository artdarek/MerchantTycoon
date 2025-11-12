from __future__ import annotations

from datetime import datetime, date as _date, time as _time, timedelta as _timedelta
from typing import TYPE_CHECKING

from merchant_tycoon.config import SETTINGS

if TYPE_CHECKING:
    from merchant_tycoon.engine.game_state import GameState


class ClockService:
    """Provides game-consistent timestamps and day advancement.

    - Date comes from the in-game calendar (state.date)
    - Time comes from the system clock at the moment of the call
    """

    def __init__(self, state: "GameState"):
        self.state = state

    def now(self) -> datetime:
        d = (getattr(self.state, "date", "") or getattr(SETTINGS.game, "start_date", "2025-01-01"))
        try:
            dd = _date.fromisoformat(str(d))
        except Exception:
            dd = _date.fromisoformat("2025-01-01")
        tt = datetime.now().time().replace(microsecond=0)
        return datetime.combine(dd, tt)

    def date_str(self) -> str:
        return self.now().date().isoformat()

    def time_str(self) -> str:
        return self.now().strftime("%H:%M:%S")

    def advance_day(self) -> None:
        """Advance the game day counter and calendar date by one day."""
        self.state.day += 1

        # Advance calendar date
        try:
            current = getattr(self.state, "date", "") or getattr(SETTINGS.game, "start_date", "2025-01-01")
            d = _date.fromisoformat(str(current)) + _timedelta(days=1)
            self.state.date = d.isoformat()
        except Exception:
            # Keep going even if date parsing fails
            pass

