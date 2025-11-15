from textual.app import ComposeResult
from textual.widgets import Static, Label, DataTable

from merchant_tycoon.engine import GameEngine


class WinHistoryPanel(Static):
    """Right-column panel listing past wins."""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("🏆 WIN HISTORY", classes="panel-title")
        yield DataTable(id="lotto-win-table")

    def update_win_history(self) -> None:
        table = self.query_one("#lotto-win-table", DataTable)
        if not getattr(self, "_win_table_init", False):
            table.clear(columns=True)
            table.add_columns("Day", "Status", "1", "2", "3", "4", "5", "6", "Matched", "Payout")
            try:
                table.cursor_type = "row"
                table.show_header = True
                table.zebra_stripes = True
            except Exception:
                pass
            self._win_table_init = True

        try:
            table.clear(rows=True)
        except Exception:
            table.clear()

        wins = list(self.engine.state.lotto_win_history or [])
        try:
            wins.sort(key=lambda w: int(getattr(w, "day", 0) or 0), reverse=True)
        except Exception:
            pass
        for w in wins:
            nums = list(getattr(w, "ticket_numbers", [])) + ["-"] * 6
            nums = nums[:6]
            matched = getattr(w, "matched", 0)
            payout = getattr(w, "payout", 0)
            table.add_row(
                str(getattr(w, "day", "-")),
                "Win",
                *(str(n) for n in nums),
                str(matched),
                f"${int(payout):,}",
            )
        # No summary here; dedicated summary panel is used instead
