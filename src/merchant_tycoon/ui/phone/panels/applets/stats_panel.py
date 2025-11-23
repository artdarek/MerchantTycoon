from textual.app import ComposeResult
from textual.widgets import Static, Label
from textual.containers import ScrollableContainer
from rich.text import Text


class StatsPanel(Static):
    """Displays daily wealth progress as a compact sparkline chart."""

    def compose(self) -> ComposeResult:
        yield Label("📊 STATS", classes="panel-title")
        with ScrollableContainer(id="stats-content"):
            # Net wealth
            yield Label("Net Wealth", id="stats-h-wealth")
            yield Label("", id="stats-chart-wealth")
            yield Label("", id="stats-legend-wealth", classes="dim")
            # Cash
            yield Label("Cash", id="stats-h-cash")
            yield Label("", id="stats-chart-cash")
            yield Label("", id="stats-legend-cash", classes="dim")
            # Bank
            yield Label("Bank", id="stats-h-bank")
            yield Label("", id="stats-chart-bank")
            yield Label("", id="stats-legend-bank", classes="dim")
            # Debt
            yield Label("Debt", id="stats-h-debt")
            yield Label("", id="stats-chart-debt")
            yield Label("", id="stats-legend-debt", classes="dim")
            # Goods value
            yield Label("Goods Value", id="stats-h-goods")
            yield Label("", id="stats-chart-goods")
            yield Label("", id="stats-legend-goods", classes="dim")
            # Investments / Assets value
            yield Label("Investments / Assets Value", id="stats-h-assets")
            yield Label("", id="stats-chart-assets")
            yield Label("", id="stats-legend-assets", classes="dim")

    def on_mount(self) -> None:
        self.refresh_chart()

    def _get_series(self, key: str, max_points: int = 30) -> tuple[list[int], list[int]]:
        """Return (days, values) for a given metric key from daily_metrics.
        Supports special key 'wealth_net' with fallback computation; for others,
        falls back to reading current value from state if history empty.
        """
        engine = getattr(self.app, "engine", None)
        if engine is None:
            return [], []
        state = engine.state
        dm = getattr(state, "daily_metrics", {}) or {}
        if dm:
            days = sorted(dm.keys())
            days = days[-max_points:]
            vals: list[int] = []
            for d in days:
                rec = dm.get(d) or {}
                if key in rec:
                    try:
                        vals.append(int(rec[key]))
                        continue
                    except Exception:
                        pass
                if key == "wealth_net":
                    try:
                        gross = int(rec.get("wealth_gross", 0))
                        debt = int(rec.get("debt", 0))
                        vals.append(gross - debt)
                    except Exception:
                        vals.append(0)
                else:
                    vals.append(int(rec.get(key, 0)))
            return days, vals
        # No history: compute single-point fallback
        try:
            day = int(getattr(state, "day", 0))
        except Exception:
            day = 0
        if key == "wealth_net":
            try:
                cur = int(state.calculate_total_wealth(getattr(engine, "asset_prices", {}), getattr(engine, "prices", {})))
            except Exception:
                cur = 0
        elif key == "cash":
            try:
                cur = int(getattr(state, "cash", 0))
            except Exception:
                cur = 0
        elif key == "bank":
            try:
                cur = int(getattr(getattr(state, "bank", object()), "balance", 0))
            except Exception:
                cur = 0
        elif key == "debt":
            try:
                cur = int(getattr(state, "debt", 0))
            except Exception:
                cur = 0
        elif key == "goods_value":
            try:
                inv = getattr(state, "inventory", {}) or {}
                prices = getattr(engine, "prices", {}) or {}
                cur = sum(int(q) * int(prices.get(n, 0)) for n, q in inv.items())
            except Exception:
                cur = 0
        elif key == "portfolio_value":
            try:
                port = getattr(state, "portfolio", {}) or {}
                prices = getattr(engine, "asset_prices", {}) or {}
                cur = sum(int(q) * int(prices.get(sym, 0)) for sym, q in port.items())
            except Exception:
                cur = 0
        else:
            cur = 0
        return [day], [cur]

    def _render_block_chart(self, values: list[int], width: int = 60, height: int = 10) -> Text:
        """Render a multi-row block chart with a baseline.

        Baseline: draws a horizontal axis at 0 if within range; otherwise at the
        minimum value level to give a visual baseline.
        """
        txt = Text()
        if not values or width <= 0 or height <= 0:
            txt.append("(no data)", style="dim")
            return txt

        vmin = min(values)
        vmax = max(values)

        # Resample to target width
        series = values
        if len(values) > width:
            step = len(values) / width
            series = []
            i = 0.0
            for _ in range(width):
                idx = int(i)
                if idx >= len(values):
                    idx = len(values) - 1
                series.append(values[idx])
                i += step
        elif len(values) < width:
            series = [values[0]] * (width - len(values)) + list(values)

        # Map values to level 0..height
        if vmax == vmin:
            levels = [height // 2] * len(series)
        else:
            rng = vmax - vmin
            levels = [max(0, min(height, int((v - vmin) / rng * height))) for v in series]

        # Baseline level (ensure within 1..height)
        if vmax == vmin:
            baseline_level = None  # Not meaningful; skip baseline overlay
        else:
            rng = vmax - vmin
            base_value = 0 if (vmin <= 0 <= vmax) else vmin
            # Use rounding and clamp to at least 1 so it shows on grid
            norm = (base_value - vmin) / rng * height
            baseline_level = max(1, min(height, int(round(norm))))

        # Build from top row to bottom
        for row in range(height, 0, -1):
            for col, lvl in enumerate(levels):
                # Draw baseline first (overlay to ensure visibility)
                if baseline_level is not None and row == baseline_level:
                    txt.append("─", style="#9aa3b2")
                elif lvl >= row:
                    # Draw bar cell
                    txt.append("█", style="#4ea59a")
                else:
                    txt.append(" ")
            txt.append("\n")
        return txt

    def _abbr(self, n: int) -> str:
        try:
            v = float(n)
        except Exception:
            return str(n)
        neg = v < 0
        v = abs(v)
        if v >= 1_000_000_000:
            s = f"{v/1_000_000_000:.1f}B"
        elif v >= 1_000_000:
            s = f"{v/1_000_000:.1f}M"
        elif v >= 1_000:
            s = f"{v/1_000:.1f}K"
        else:
            s = f"{int(v)}"
        return f"-{s}" if neg else s

    def _render_block_chart_with_axes(
        self,
        values: list[int],
        days: list[int] | None,
        width: int,
        height: int,
    ) -> Text:
        """Render chart with simple Y(top/bottom) and X(start/end) labels."""
        if not values:
            t = Text()
            t.append("(no data)", style="dim")
            return t

        # Build core chart first
        core = self._render_block_chart(values, width=width, height=height)

        # Split lines to insert left Y labels and bottom X labels
        lines = str(core).splitlines()
        if not lines:
            return core

        vmin = min(values)
        vmax = max(values)
        top_label = self._abbr(vmax)
        bot_label = self._abbr(vmin)
        label_w = max(len(top_label), len(bot_label)) + 1  # +1 space padding

        # Prefix Y-axis labels (only on top and bottom rows)
        for i, line in enumerate(lines):
            if i == 0:
                prefix = top_label.rjust(label_w)
            elif i == len(lines) - 1:
                prefix = bot_label.rjust(label_w)
            else:
                prefix = " " * label_w
            lines[i] = prefix + line

        # Bottom X labels
        if days and len(days) >= 1:
            left = f"D{days[0]}"
            right = f"D{days[-1]}"
            axis = " " * label_w
            axis_width = len(lines[-1]) - label_w
            if axis_width < 0:
                axis_width = 0
            # Place left at start, right at end
            left = left[:max(0, axis_width)]
            right = right[:max(0, axis_width)]
            # Build a line with left at col 0 and right right-aligned
            if len(right) > axis_width:
                right = right[:axis_width]
            pad_mid = max(0, axis_width - len(left) - len(right))
            axis += left + (" " * pad_mid) + right
            lines.append(axis)

        # Rebuild Text
        out = Text()
        out.append("\n".join(lines))
        return out

    def refresh_chart(self) -> None:
        # Render Net Wealth
        w_days, wealth_vals = self._get_series("wealth_net", max_points=30)
        try:
            w_chart_label = self.query_one("#stats-chart-wealth", Label)
            w_legend_label = self.query_one("#stats-legend-wealth", Label)
        except Exception:
            return
        w_chart_label.update(self._render_block_chart_with_axes(wealth_vals, w_days, width=60, height=10))
        w_legend_label.update(self._legend_text("Net wealth", wealth_vals))

        # Render Cash
        c_days, cash_vals = self._get_series("cash", max_points=30)
        try:
            c_chart_label = self.query_one("#stats-chart-cash", Label)
            c_legend_label = self.query_one("#stats-legend-cash", Label)
        except Exception:
            return
        c_chart_label.update(self._render_block_chart_with_axes(cash_vals, c_days, width=60, height=6))
        c_legend_label.update(self._legend_text("Cash", cash_vals))

        # Render Bank
        b_days, bank_vals = self._get_series("bank", max_points=30)
        try:
            b_chart_label = self.query_one("#stats-chart-bank", Label)
            b_legend_label = self.query_one("#stats-legend-bank", Label)
        except Exception:
            return
        b_chart_label.update(self._render_block_chart_with_axes(bank_vals, b_days, width=60, height=6))
        b_legend_label.update(self._legend_text("Bank", bank_vals))

        # Render Debt
        d_days, debt_vals = self._get_series("debt", max_points=30)
        try:
            d_chart_label = self.query_one("#stats-chart-debt", Label)
            d_legend_label = self.query_one("#stats-legend-debt", Label)
        except Exception:
            return
        d_chart_label.update(self._render_block_chart_with_axes(debt_vals, d_days, width=60, height=6))
        d_legend_label.update(self._legend_text("Debt", debt_vals))

        # Render Goods Value
        g_days, goods_vals = self._get_series("goods_value", max_points=30)
        try:
            g_chart_label = self.query_one("#stats-chart-goods", Label)
            g_legend_label = self.query_one("#stats-legend-goods", Label)
        except Exception:
            return
        g_chart_label.update(self._render_block_chart_with_axes(goods_vals, g_days, width=60, height=6))
        g_legend_label.update(self._legend_text("Goods", goods_vals))

        # Render Assets (Portfolio) Value
        a_days, asset_vals = self._get_series("portfolio_value", max_points=30)
        try:
            a_chart_label = self.query_one("#stats-chart-assets", Label)
            a_legend_label = self.query_one("#stats-legend-assets", Label)
        except Exception:
            return
        a_chart_label.update(self._render_block_chart_with_axes(asset_vals, a_days, width=60, height=6))
        a_legend_label.update(self._legend_text("Assets", asset_vals))

    def _legend_text(self, label: str, values: list[int]) -> Text:
        if not values:
            return Text("No data yet — travel to start days ticking.", style="dim")
        vmin = min(values)
        vmax = max(values)
        last = values[-1]
        prev = values[-2] if len(values) >= 2 else last
        delta = last - prev
        pct = (delta / prev * 100) if prev != 0 else 0.0
        sym = "▲" if delta > 0 else ("▼" if delta < 0 else "→")
        text = Text()
        text.append(f"{label}: ${last:,}  ")
        text.append(f"{sym} {delta:+,} ({pct:+.1f}%)  ", style=("green" if delta>0 else "red" if delta<0 else "#9aa3b2"))
        text.append(f"Range: ${vmin:,} → ${vmax:,}", style="#9aa3b2")
        return text
