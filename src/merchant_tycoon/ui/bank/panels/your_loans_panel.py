from textual.app import ComposeResult
from textual.widgets import Static, Label, DataTable
from rich.text import Text

from merchant_tycoon.engine import GameEngine


class YourLoansPanel(Static):
    """Display a list of player's loans in a table."""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine
        self._row_to_loan_id: dict[object, int] = {}

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
            table.add_columns("Date", "Amount", "Paid", "Remain", "Rate (APR | Daily)", "Status")
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
        self._row_to_loan_id = {}

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

            # Date column from ISO ts if present, else fallback to "Day X"
            ts = getattr(ln, 'ts', '')
            if ts:
                try:
                    from datetime import datetime
                    date_only = datetime.fromisoformat(ts).date().isoformat()
                except Exception:
                    date_only = ts[:10]
            else:
                date_only = f"Day {day}"

            row_key = table.add_row(
                date_only,
                f"${int(principal):,}",
                f"${int(repaid):,}",
                f"${int(remaining):,}",
                rate_cell,
                status_cell,
            )
            try:
                self._row_to_loan_id[row_key] = int(getattr(ln, 'loan_id', -1))
            except Exception:
                pass

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # Open Repay modal with selected loan and default amount = min(remaining, cash)
        try:
            table = event.data_table
        except Exception:
            table = None
        if not table or getattr(table, "id", None) != "your-loans-table":
            return
        loan_id = self._row_to_loan_id.get(getattr(event, "row_key", None))
        if not loan_id or loan_id < 0:
            return
        # Find the loan to compute remaining
        ln = next((ln for ln in (self.engine.state.loans or []) if getattr(ln, 'loan_id', -1) == loan_id), None)
        if not ln:
            return
        remaining = int(getattr(ln, 'remaining', 0))
        if remaining <= 0:
            # Selected loan is already fully repaid – inform and do not open modal
            try:
                if self.engine.messenger:
                    self.engine.messenger.warn("This loan is already fully repaid.", tag="bank")
                    try:
                        self.app.refresh_all()
                    except Exception:
                        pass
            except Exception:
                pass
            return
        cash = int(getattr(self.engine.state, 'cash', 0))
        default_amount = min(remaining, cash)
        # No cash at all
        if cash <= 0:
            try:
                if self.engine.messenger:
                    self.engine.messenger.warn(
                        "Not enough cash to repay this loan.", tag="bank"
                    )
                # Ensure messenger panel updates immediately
                try:
                    self.app.refresh_all()
                except Exception:
                    pass
            except Exception:
                pass
            return
        # Inform if user cannot fully repay selected loan
        if cash < remaining:
            try:
                if self.engine.messenger:
                    self.engine.messenger.warn(
                        f"Insufficient funds to fully repay this loan. Required ${remaining:,}, you have ${cash:,}.",
                        tag="bank",
                    )
                try:
                    self.app.refresh_all()
                except Exception:
                    pass
            except Exception:
                pass
        try:
            from merchant_tycoon.ui.bank.modals import LoanRepayModal
            self.app.push_screen(LoanRepayModal(self.engine, self.app._handle_repay_selected, default_loan_id=loan_id, default_amount=default_amount))
        except Exception:
            pass
