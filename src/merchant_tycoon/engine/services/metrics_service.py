from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from merchant_tycoon.engine.game_state import GameState


class MetricsService:
    """Service responsible for capturing per-day metrics snapshots.

    Keeps computation outside GameState to avoid coupling state to pricing logic.
    """

    def snapshot_daily(
        self,
        state: "GameState",
        goods_prices: Optional[Dict[str, int]] = None,
        asset_prices: Optional[Dict[str, int]] = None,
        extra: Optional[Dict[str, int]] = None,
    ) -> None:
        """Compute and store a daily snapshot under state.daily_metrics[state.day].

        Captures:
          - cash, bank, goods_value, portfolio_value, debt
          - wealth_gross (cash + bank + goods + portfolio)
          - wealth_net (wealth_gross − debt)
        Optionally merges additional metrics from `extra`.
        """
        # Components
        try:
            cash = int(getattr(state, "cash", 0))
        except Exception:
            cash = 0
        try:
            bank_balance = int(getattr(state.bank, "balance", 0))
        except Exception:
            bank_balance = 0

        # Portfolio value
        port_val = 0
        try:
            portfolio = getattr(state, "portfolio", {}) or {}
            prices = asset_prices or {}
            for sym, qty in portfolio.items():
                port_val += int(qty) * int(prices.get(sym, 0))
        except Exception:
            pass

        # Goods value
        goods_val = 0
        try:
            inv = getattr(state, "inventory", {}) or {}
            gprices = goods_prices or {}
            for name, qty in inv.items():
                goods_val += int(qty) * int(gprices.get(name, 0))
        except Exception:
            pass

        # Debt
        try:
            debt = int(getattr(state, "debt", 0))
        except Exception:
            debt = 0

        wealth_gross = cash + bank_balance + goods_val + port_val
        wealth_net = wealth_gross - debt

        metrics: Dict[str, int] = {
            "cash": cash,
            "bank": bank_balance,
            "goods_value": goods_val,
            "portfolio_value": port_val,
            "debt": debt,
            "wealth_gross": wealth_gross,
            "wealth_net": wealth_net,
        }
        if extra:
            for k, v in (extra or {}).items():
                try:
                    metrics[str(k)] = int(v)
                except Exception:
                    continue

        # Store under current day
        try:
            d = int(getattr(state, "day", 0))
        except Exception:
            d = 0
        state.daily_metrics[d] = metrics

