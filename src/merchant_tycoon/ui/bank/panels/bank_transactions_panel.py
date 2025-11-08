from textual.app import ComposeResult
from textual.widgets import Static, Label, DataTable
from rich.text import Text

from merchant_tycoon.engine import GameEngine
from merchant_tycoon.config import SETTINGS


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

        # Show last N transactions, newest to oldest (day desc, then insertion order desc)
        limit = int(SETTINGS.saveui.bank_transactions_limit)
        txs = bank.transactions[-limit:]
        # Use index within the sliced window to break ties for same day (later index = newer)
        indexed = [(i, tx) for i, tx in enumerate(txs)]
        try:
            indexed.sort(key=lambda pair: (getattr(pair[1], 'day', 0), pair[0]), reverse=True)
            txs = [tx for _, tx in indexed]
        except Exception:
            # Fallback: simple reverse if anything goes wrong
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
