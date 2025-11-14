from textual.app import ComposeResult
from textual.widgets import Static, Label

from merchant_tycoon.engine import GameEngine


class LottoTodayDrawPanel(Static):
    """Right-column panel showing today's draw numbers."""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("🎲 TODAY'S DRAW", classes="panel-title")
        yield Label("-", id="lotto-draw-line")

    def update_draw(self) -> None:
        label = self.query_one("#lotto-draw-line", Label)
        draw = getattr(self.engine.state, "lotto_today_draw", None)
        try:
            today_cost = int(getattr(self.engine.state, "lotto_today_cost", 0) or 0)
        except Exception:
            today_cost = 0
        try:
            today_payout = int(getattr(self.engine.state, "lotto_today_payout", 0) or 0)
        except Exception:
            today_payout = 0
        pl = today_payout - today_cost
        if not draw or not getattr(draw, "numbers", None):
            label.update(
                f"Numbers: - - - - - -  •  Today's cost: ${today_cost:,}  •  Today's payout: ${today_payout:,}  •  P/L: ${pl:,}"
            )
            return
        try:
            nums = ", ".join(str(n) for n in sorted(list(draw.numbers)))
        except Exception:
            nums = ", ".join(str(n) for n in list(draw.numbers))
        label.update(
            f"Numbers: {nums}  •  Today's cost: ${today_cost:,}  •  Today's payout: ${today_payout:,}  •  P/L: ${pl:,}"
        )
