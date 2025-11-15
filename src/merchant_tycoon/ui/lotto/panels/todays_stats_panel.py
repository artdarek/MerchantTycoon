from textual.app import ComposeResult
from textual.widgets import Static, Label

from merchant_tycoon.engine import GameEngine


class TodaysStatsPanel(Static):
    """Right-column panel showing today's lottery stats and numbers."""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("🎲 TODAY'S LOTTERY STATS", classes="panel-title")
        yield Label("-", id="lotto-draw-line")

    def update_stats(self) -> None:
        label = self.query_one("#lotto-draw-line", Label)
        try:
            today_cost = int(getattr(self.engine.state, "lotto_today_cost", 0) or 0)
        except Exception:
            today_cost = 0
        try:
            today_payout = int(getattr(self.engine.state, "lotto_today_payout", 0) or 0)
        except Exception:
            today_payout = 0
        pl = today_payout - today_cost
        label.update(
            f"Cost: ${today_cost:,}  •  Payout: ${today_payout:,}  •  P/L: ${pl:,}"
        )
