from textual.app import ComposeResult
from textual.widgets import Static, Label

from merchant_tycoon.engine import GameEngine


class LottoTicketsSummaryPanel(Static):
    """Summary panel for owned tickets totals (cost, reward, P/L)."""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("📈 TICKETS SUMMARY", classes="panel-title")
        yield Label("", id="tickets-summary-line")

    def update_summary(self) -> None:
        try:
            tickets = list(self.engine.state.lotto_tickets or [])
            total_cost = sum(int(getattr(t, "total_cost", 0) or 0) for t in tickets)
            total_reward = sum(int(getattr(t, "total_reward", 0) or 0) for t in tickets)
            pl = total_reward - total_cost
            active = sum(1 for t in tickets if getattr(t, "active", False))
            total = len(tickets)
        except Exception:
            total_cost = total_reward = pl = 0
            active = total = 0

        line = f"Owned: {total} (Active: {active})  •  Cost: ${total_cost:,}  •  Reward: ${total_reward:,}  •  P/L: ${pl:,}"
        self.query_one("#tickets-summary-line", Label).update(line)

