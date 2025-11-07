from textual.app import ComposeResult
from textual.widgets import Static, Label, DataTable
from rich.text import Text

from ...engine import GameEngine


class AccountTransactionsPanel(Static):
    """Display the bank transactions table (last 100)."""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("📜 ACCOUNT TRANSACTIONS", id="bank-transactions-header", classes="panel-title")
        yield DataTable(id="bank-transactions")

    def update_transactions(self) -> None:
        bank = self.engine.state.bank
        table = self.query_one('#bank-transactions', DataTable)

        # Init columns once
        if not getattr(self, '_bank_table_initialized', False):
            table.clear(columns=True)
            table.add_columns("Day", "Type", "Amount", "Balance After", "Title")
            try:
                table.cursor_type = "row"
                table.show_header = True
                table.zebra_stripes = True
            except Exception:
                pass
            self._bank_table_initialized = True

        # Clear rows
        try:
            table.clear(rows=True)
        except Exception:
            table.clear()

        if not bank.transactions:
            table.add_row("-", "(no transactions)", "", "", "")
            return

        # Show last 100 transactions, newest to oldest
        txs = bank.transactions[-100:]
        # Sort by day descending; if equal day, preserve original relative order by reversing slice order
        try:
            txs = sorted(txs, key=lambda t: getattr(t, 'day', 0), reverse=True)
        except Exception:
            txs = list(reversed(txs))
        for tx in txs:
            # Color by type
            if tx.tx_type == "interest":
                ttype = Text("interest", style="green")
            elif tx.tx_type == "withdraw":
                ttype = Text("withdraw", style="yellow")
            else:
                ttype = Text("deposit", style="cyan")

            title = getattr(tx, "title", "") or ""

            table.add_row(
                str(tx.day),
                ttype,
                f"${tx.amount:,}",
                f"${tx.balance_after:,}",
                title,
            )
