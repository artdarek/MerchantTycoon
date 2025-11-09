from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Static, Label, DataTable
from rich.text import Text

from merchant_tycoon.engine import GameEngine


class InvestmentsLotsPanel(Static):
    """Per-asset breakdown of investment purchase lots, similar to PURCHASED LOTS.

    Shows lots for assets currently held in the portfolio with per-lot P/L.
    """

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine
        self._tables: dict[int, dict] = {}

    def compose(self) -> ComposeResult:
        yield Label("🧾 INVESTMETS LOTS", id="investments-lots-header", classes="panel-title")
        yield ScrollableContainer(id="investments-lots-content")

    def update_lots(self) -> None:
        container = self.query_one("#investments-lots-content", ScrollableContainer)
        try:
            container.remove_children()
        except Exception:
            pass

        state = self.engine.state
        prices = self.engine.asset_prices

        # Only display assets that are currently owned (>0)
        owned = [sym for sym, qty in (state.portfolio or {}).items() if qty > 0]
        owned.sort()
        if not owned:
            return

        for symbol in owned:
            current_price = int(prices.get(symbol, 0))
            lots = state.get_investment_lots_for_asset(symbol)
            if not lots:
                continue

            # Header for this asset
            container.mount(Label(f" {symbol} ", classes="section-header"))

            # Build a DataTable for this asset's lots
            table = DataTable()
            try:
                table.cursor_type = "row"
                table.show_header = True
                table.zebra_stripes = True
            except Exception:
                pass
            table.add_columns("Date", "Qty", "Price", "Total", "P/L", "P/L%")

            # Register table meta
            meta = {"symbol": symbol, "rows": {}}
            self._tables[id(table)] = meta

            for lot in lots:
                qty = int(getattr(lot, "quantity", 0))
                pp = int(getattr(lot, "purchase_price", 0))
                total = qty * pp
                profit_per_unit = current_price - pp
                lot_profit = profit_per_unit * qty
                lot_profit_pct = (profit_per_unit / pp * 100) if pp > 0 else 0

                # Color profit cells
                if lot_profit > 0:
                    pl_cell = Text(f"${lot_profit:+,}", style="green")
                    pl_pct_cell = Text(f"{lot_profit_pct:+.1f}%", style="green")
                elif lot_profit < 0:
                    pl_cell = Text(f"${lot_profit:+,}", style="red")
                    pl_pct_cell = Text(f"{lot_profit_pct:+.1f}%", style="red")
                else:
                    pl_cell = Text("$0", style="dim")
                    pl_pct_cell = Text("0.0%", style="dim")

                # Date only (YYYY-MM-DD) from ISO ts if present
                ts = str(getattr(lot, "ts", ""))
                date_only = ts[:10] if ts and len(ts) >= 10 else ""

                row_key = table.add_row(
                    date_only,
                    str(qty),
                    f"${pp:,}",
                    f"${total:,}",
                    pl_cell,
                    pl_pct_cell,
                )
                try:
                    meta["rows"][row_key] = {"qty": qty}
                except Exception:
                    pass

            container.mount(table)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # Open SellAssetModal with asset symbol and lot quantity prefilled
        try:
            table = event.data_table
            meta = self._tables.get(id(table))
        except Exception:
            meta = None
        if not meta:
            return
        row_key = getattr(event, "row_key", None)
        if row_key is None:
            return
        symbol = meta.get("symbol")
        entry = meta.get("rows", {}).get(row_key, {})
        qty = int(entry.get("qty", 0))
        if not symbol or qty <= 0:
            return
        # Launch SellAssetModal with defaults
        try:
            from merchant_tycoon.ui.investments.modals import SellAssetModal
            self.app.push_screen(SellAssetModal(self.engine, self.app._handle_asset_trade, default_symbol=symbol, default_quantity=qty))
        except Exception:
            pass
