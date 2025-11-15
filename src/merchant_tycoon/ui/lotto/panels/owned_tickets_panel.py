from textual.app import ComposeResult
from textual.widgets import Static, Label, DataTable

from merchant_tycoon.engine import GameEngine
from merchant_tycoon.ui.lotto.modals import TicketActionsModal


class OwnedTicketsPanel(Static):
    """Left-column panel listing owned lotto tickets with actions."""

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine
        self._row_to_index: dict[object, int] = {}

    def compose(self) -> ComposeResult:
        yield Label("🎟 OWNED TICKETS", classes="panel-title")
        yield DataTable(id="lotto-tickets-table")

    def update_tickets(self) -> None:
        table = self.query_one("#lotto-tickets-table", DataTable)
        # Setup columns once
        if not getattr(self, "_table_init", False):
            table.clear(columns=True)
            table.add_columns(
                "Day", "Status", "1", "2", "3", "4", "5", "6", "Cost", "Reward", "P/L"
            )
            try:
                table.cursor_type = "row"
                table.show_header = True
                table.zebra_stripes = True
            except Exception:
                pass
            self._table_init = True

        # Clear rows and mapping
        try:
            table.clear(rows=True)
        except Exception:
            table.clear()
        self._row_to_index.clear()

        # Work on a sorted view but keep mapping to original index in state
        tickets_view = list(self.engine.state.lotto_tickets or [])
        try:
            tickets_view.sort(key=lambda t: int(getattr(t, "purchase_day", 0) or 0), reverse=True)
        except Exception:
            pass
        for t in tickets_view:
            status = "Active" if getattr(t, "active", False) else "Inactive"
            nums = list(getattr(t, "numbers", [])) + ["-"] * 6
            nums = nums[:6]
            cost = int(getattr(t, "total_cost", 0) or 0)
            reward = int(getattr(t, "total_reward", 0) or 0)
            pl = reward - cost
            row_key = table.add_row(
                str(getattr(t, "purchase_day", "-")),
                status,
                *(str(n) for n in nums),
                f"${cost:,}",
                f"${reward:,}",
                f"${pl:,}",
            )
            # Map to original index in state.lotto_tickets
            try:
                orig_idx = (self.engine.state.lotto_tickets or []).index(t)
            except ValueError:
                orig_idx = None
            self._row_to_index[row_key] = orig_idx

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        try:
            table = event.data_table
        except Exception:
            return
        if getattr(table, "id", None) != "lotto-tickets-table":
            return
        idx = self._row_to_index.get(getattr(event, "row_key", None))
        if idx is None or idx < 0:
            return
        ticket = self.engine.state.lotto_tickets[idx]

        def _toggle():
            ok, msg = self.engine.lotto_service.toggle_ticket_active(idx)
            if not ok:
                self.engine.messenger.warn(msg, tag="lotto")
            self.app.refresh_all()

        def _remove():
            ok, msg = self.engine.lotto_service.remove_ticket(idx)
            if not ok:
                self.engine.messenger.warn(msg, tag="lotto")
            self.app.refresh_all()

        self.app.push_screen(
            TicketActionsModal(list(ticket.numbers), bool(ticket.active), _toggle, _remove)
        )
