from textual.app import ComposeResult
from textual.widgets import Static, Label, DataTable
from rich.text import Text

from merchant_tycoon.engine import GameEngine


class YourLoansPanel(Static):
    """Display a list of player's loans in a table."""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("📋 YOUR LOANS", id="your-loans-header", classes="panel-title")
        yield DataTable(id="your-loans-table")

    def update_loans(self) -> None:
        table = self.query_one('#your-loans-table', DataTable)

        # Initialize columns once
        if not getattr(self, "_your_loans_table_initialized", False):
            try:
                table.clear(columns=True)
            except Exception:
                try:
                    table.clear()
                except Exception:
                    pass
            table.add_columns("Day", "Amount", "Paid", "Remain", "Rate (APR | Daily)", "Status")
            try:
                table.cursor_type = "row"
                table.show_header = True
                table.zebra_stripes = True
            except Exception:
                pass
            self._your_loans_table_initialized = True

        # Clear existing rows
        try:
            table.clear(rows=True)
        except Exception:
            try:
                table.clear()
            except Exception:
                pass

        loans = list(self.engine.state.loans or [])
        if not loans:
            table.add_row("-", "(no loans)", "", "", "", "")
            return

        # Newest first by day; for same day, keep newer insertions first
        indexed = [(i, ln) for i, ln in enumerate(loans)]
        try:
            indexed.sort(key=lambda pair: (getattr(pair[1], 'day_taken', 0), pair[0]), reverse=True)
            loans = [ln for _, ln in indexed]
        except Exception:
            loans.sort(key=lambda ln: getattr(ln, 'day_taken', 0), reverse=True)
        for ln in loans:
            day = getattr(ln, 'day_taken', 0)
            principal = getattr(ln, 'principal', 0)
            repaid = getattr(ln, 'repaid', 0)
            remaining = getattr(ln, 'remaining', 0)

            if remaining <= 0:
                status_cell = Text("Fully Paid", style="green")
            else:
                status_cell = Text("Not Paid", style="yellow")

            # Display per-loan APR and derived daily rate
            try:
                apr = float(getattr(ln, 'rate_annual', 0.10))
            except Exception:
                apr = 0.10
            daily = apr / 365.0
            rate_cell = f"{apr*100:.2f}% | {daily*100:.4f}%"

            table.add_row(
                str(day),
                f"${int(principal):,}",
                f"${int(repaid):,}",
                f"${int(remaining):,}",
                rate_cell,
                status_cell,
            )
