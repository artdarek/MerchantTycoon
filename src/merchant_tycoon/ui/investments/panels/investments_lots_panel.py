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

        # Build lookup for asset names/type by symbol
        try:
            assets = self.engine.assets_repo.get_all()
        except Exception:
            assets = []
        symbol_to_name = {a.symbol: a.name for a in assets}

        # Only display assets that are currently owned (>0)
        owned = [sym for sym, qty in (state.portfolio or {}).items() if qty > 0]
        owned.sort()
        if not owned:
            return

        # Build a single DataTable for all assets' lots
        table = DataTable()
        try:
            table.cursor_type = "row"
            table.show_header = True
            table.zebra_stripes = True
        except Exception:
            pass
        table.add_columns("Symbol", "Name", "Qty", "Price/B", "Value/B", "Price/C", "Value/C", "P/L", "P/L%", "Type", "Dividend", "Date")

        meta = {"rows": {}}
        self._tables[id(table)] = meta

        for symbol in owned:
            current_price = int(prices.get(symbol, 0))
            lots = state.get_investment_lots_for_asset(symbol)
            if not lots:
                continue

            asset_name = symbol_to_name.get(symbol, symbol)
            try:
                asset = self.engine.assets_repo.get_by_symbol(symbol)
            except Exception:
                asset = None
            asset_type = getattr(asset, "asset_type", "") if asset else ""

            for lot in lots:
                qty = int(getattr(lot, "quantity", 0))
                pp = int(getattr(lot, "purchase_price", 0))
                total_cost = qty * pp
                total_value = qty * current_price
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

                # Get dividend paid for this lot
                dividend_paid = int(getattr(lot, "dividend_paid", 0))
                dividend_cell = f"${dividend_paid:,}" if dividend_paid > 0 else "-"

                row_key = table.add_row(
                    symbol,
                    asset_name,
                    str(qty),
                    f"${pp:,}",
                    f"${total_cost:,}",
                    f"${current_price:,}",
                    f"${total_value:,}",
                    pl_cell,
                    pl_pct_cell,
                    asset_type,
                    dividend_cell,
                    date_only,
                )
                try:
                    meta["rows"][row_key] = {"symbol": symbol, "qty": qty, "ts": ts}
                except Exception:
                    pass

        container.mount(table)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # Open SellAssetLotModal with selected lot and prefilled quantity
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
        entry = meta.get("rows", {}).get(row_key, {})
        symbol = entry.get("symbol")
        qty = int(entry.get("qty", 0))
        ts = entry.get("ts", "")
        if not symbol or qty <= 0 or not ts:
            return
        # Launch SellAssetLotModal with defaults
        try:
            from merchant_tycoon.ui.investments.modals import SellAssetLotModal
            self.app.push_screen(SellAssetLotModal(self.engine, symbol, ts, qty, self.app._handle_asset_trade))
        except Exception:
            pass
