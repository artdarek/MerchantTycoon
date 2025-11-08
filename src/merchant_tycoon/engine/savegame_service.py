from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Tuple

from merchant_tycoon.model import (
    PurchaseLot,
    Transaction,
    InvestmentLot,
    BankTransaction,
    Loan,
)

if TYPE_CHECKING:
    from merchant_tycoon.engine.game_engine import GameEngine


SCHEMA_VERSION = 2


class SavegameService:
    """Service for persisting and restoring game state to/from disk.

    This mirrors the style of other services in the engine package and wraps
    the previous module-level functions from `merchant_tycoon.savegame`.
    """

    def __init__(self, engine: "GameEngine"):
        self.engine = engine

    # ---------- Public API (service methods) ----------
    @staticmethod
    def get_save_dir() -> Path:
        home = Path(os.path.expanduser("~"))
        return home / ".merchant_tycoon"

    @classmethod
    def get_save_path(cls) -> Path:
        return cls.get_save_dir() / "savegame.json"

    @classmethod
    def is_save_present(cls) -> bool:
        return cls.get_save_path().exists()

    def save(self, messages: List[str]) -> Tuple[bool, str]:
        """Persist the current game to JSON file. Returns (ok, message)."""
        try:
            save_dir = self.get_save_dir()
            save_dir.mkdir(parents=True, exist_ok=True)
            path = self.get_save_path()

            engine = self.engine
            state = engine.state
            bank = state.bank

            # Convert bank transactions to dicts
            bank_txs = [
                {
                    "type": tx.tx_type,
                    "amount": tx.amount,
                    "balance_after": tx.balance_after,
                    "day": tx.day,
                    "title": getattr(tx, "title", ""),
                }
                for tx in bank.transactions
            ]

            payload: Dict[str, Any] = {
                "schema_version": SCHEMA_VERSION,
                "state": {
                    "cash": state.cash,
                    "debt": state.debt,
                    "day": state.day,
                    "current_city": state.current_city,
                    "inventory": dict(state.inventory),
                    "max_inventory": state.max_inventory,
                    "purchase_lots": self._lots_to_dicts(state.purchase_lots),
                    "transaction_history": self._tx_to_dicts(state.transaction_history),
                    "portfolio": dict(state.portfolio),
                    "investment_lots": self._inv_lots_to_dicts(state.investment_lots),
                    # Loans list (multi-loan support).
                    "loans": self._loans_to_dicts(state.loans),
                    # Current global loan rate offer (APR)
                    "loan_rate_annual": float(getattr(engine, "loan_apr_today", 0.10)),
                    # Bank section (APR only)
                    "bank": {
                        "balance": bank.balance,
                        "rate_annual": getattr(bank, "interest_rate_annual", 0.02),
                        "accrued": bank.accrued_interest,
                        "last_day": bank.last_interest_day,
                        "transactions": bank_txs,
                    },
                },
                "prices": {
                    "goods": dict(engine.prices),
                    "goods_prev": dict(engine.previous_prices),
                    "assets": dict(engine.asset_prices),
                    "assets_prev": dict(engine.previous_asset_prices),
                },
                "messages": list(messages[:10]),
            }

            with path.open("w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            return True, f"Saved to {path}"
        except Exception as e:
            return False, f"Save failed: {e}"

    @classmethod
    def load(cls) -> Dict[str, Any]:
        """Read the save file and return the payload dict."""
        path = cls.get_save_path()
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def apply(self, data: Dict[str, Any]) -> bool:
        """Apply loaded payload to the current engine and state in-place."""
        try:
            engine = self.engine
            state = engine.state
            s = data.get("state") or {}

            # Restore basic fields
            try:
                state.cash = int(s.get("cash", state.cash))
            except Exception:
                pass
            try:
                state.debt = int(s.get("debt", state.debt))
            except Exception:
                pass
            try:
                state.day = int(s.get("day", state.day))
            except Exception:
                pass
            try:
                state.current_city = int(s.get("current_city", state.current_city))
            except Exception:
                pass
            # Inventory and capacities
            try:
                inv = s.get("inventory") or {}
                if isinstance(inv, dict):
                    state.inventory = {str(k): int(v) for k, v in inv.items()}
            except Exception:
                pass
            try:
                state.max_inventory = int(s.get("max_inventory", state.max_inventory))
            except Exception:
                pass

            # Lots and transactions
            try:
                state.purchase_lots = self._dicts_to_lots(s.get("purchase_lots") or [])
            except Exception:
                state.purchase_lots = []
            try:
                state.transaction_history = self._dicts_to_txs(s.get("transaction_history") or [])
            except Exception:
                state.transaction_history = []

            # Portfolio & investment lots
            try:
                port = s.get("portfolio") or {}
                if isinstance(port, dict):
                    state.portfolio = {str(k): int(v) for k, v in port.items()}
            except Exception:
                pass
            try:
                state.investment_lots = self._dicts_to_inv_lots(s.get("investment_lots") or [])
            except Exception:
                state.investment_lots = []

            # Loans (multi-loan support)
            try:
                state.loans = self._dicts_to_loans(s.get("loans") or [])
            except Exception:
                state.loans = []

            # Backward compatibility for debt (aggregate from loans)
            try:
                state.debt = engine._sync_total_debt()
            except Exception:
                pass

            # Restore prices (preserve dict object identities to keep service references valid)
            prices = data.get("prices") or {}
            try:
                goods = prices.get("goods") or {}
                if isinstance(goods, dict):
                    try:
                        engine.prices.clear()
                        engine.prices.update({str(k): int(v) for k, v in goods.items()})
                    except Exception:
                        engine.prices = {str(k): int(v) for k, v in goods.items()}
            except Exception:
                pass
            try:
                goods_prev = prices.get("goods_prev") or {}
                if isinstance(goods_prev, dict):
                    try:
                        engine.previous_prices.clear()
                        engine.previous_prices.update({str(k): int(v) for k, v in goods_prev.items()})
                    except Exception:
                        engine.previous_prices = {str(k): int(v) for k, v in goods_prev.items()}
            except Exception:
                pass
            try:
                assets = prices.get("assets") or {}
                if isinstance(assets, dict):
                    try:
                        engine.asset_prices.clear()
                        engine.asset_prices.update({str(k): int(v) for k, v in assets.items()})
                    except Exception:
                        engine.asset_prices = {str(k): int(v) for k, v in assets.items()}
            except Exception:
                pass
            try:
                assets_prev = prices.get("assets_prev") or {}
                if isinstance(assets_prev, dict):
                    try:
                        engine.previous_asset_prices.clear()
                        engine.previous_asset_prices.update({str(k): int(v) for k, v in assets_prev.items()})
                    except Exception:
                        engine.previous_asset_prices = {str(k): int(v) for k, v in assets_prev.items()}
            except Exception:
                pass

            # Restore bank account details
            bank_data = (s.get("bank") or {}) if isinstance(s, dict) else {}
            bank = state.bank
            try:
                bank.balance = int(bank_data.get("balance", bank.balance))
            except Exception:
                pass
            # Read APR (v2). Fallback: migrate from legacy daily (v1)
            rate_annual = bank_data.get("rate_annual")
            if rate_annual is None:
                try:
                    legacy_daily = float(bank_data.get("rate", 0.0))
                except Exception:
                    legacy_daily = 0.0
                bank.interest_rate_annual = legacy_daily * 365.0 if legacy_daily > 0 else getattr(bank, "interest_rate_annual", 0.02)
            else:
                try:
                    bank.interest_rate_annual = float(rate_annual)
                except Exception:
                    pass
            try:
                bank.accrued_interest = float(bank_data.get("accrued", bank.accrued_interest))
            except Exception:
                pass
            try:
                bank.last_interest_day = int(bank_data.get("last_day", bank.last_interest_day))
            except Exception:
                pass

            # Restore bank transactions
            txs = bank_data.get("transactions") or []
            new_txs: List[BankTransaction] = []
            for d in txs:
                try:
                    new_txs.append(
                        BankTransaction(
                            tx_type=str(d.get("type", "")),
                            amount=int(d.get("amount", 0)),
                            balance_after=int(d.get("balance_after", 0)),
                            day=int(d.get("day", 0)),
                            title=str(d.get("title", "")),
                        )
                    )
                except Exception:
                    continue
            try:
                bank.transactions = new_txs
            except Exception:
                pass

            # Restore today's loan offer (APR). For legacy saves, fallback handled via default.
            try:
                engine.loan_apr_today = float(s.get("loan_rate_annual", getattr(engine, "loan_apr_today", 0.10)))
            except Exception:
                pass

            return True
        except Exception:
            return False

    @classmethod
    def delete_save(cls) -> None:
        try:
            cls.get_save_path().unlink(missing_ok=True)
        except TypeError:
            # Python < 3.8 compatibility if needed
            path = cls.get_save_path()
            if path.exists():
                try:
                    path.unlink()
                except Exception:
                    pass

    # ---------- Private helpers (conversion) ----------
    @staticmethod
    def _lots_to_dicts(lots: List[PurchaseLot]) -> List[Dict[str, Any]]:
        return [
            {
                "good_name": lot.good_name,
                "quantity": lot.quantity,
                "purchase_price": lot.purchase_price,
                "day": lot.day,
                "city": lot.city,
            }
            for lot in lots
        ]

    @staticmethod
    def _dicts_to_lots(items: List[Dict[str, Any]]) -> List[PurchaseLot]:
        result: List[PurchaseLot] = []
        for d in items:
            try:
                result.append(
                    PurchaseLot(
                        good_name=d["good_name"],
                        quantity=int(d["quantity"]),
                        purchase_price=int(d["purchase_price"]),
                        day=int(d["day"]),
                        city=str(d["city"]),
                    )
                )
            except Exception:
                continue
        return result

    @staticmethod
    def _tx_to_dicts(txs: List[Transaction]) -> List[Dict[str, Any]]:
        return [
            {
                "transaction_type": tx.transaction_type,
                "good_name": tx.good_name,
                "quantity": tx.quantity,
                "price_per_unit": tx.price_per_unit,
                "total_value": tx.total_value,
                "day": tx.day,
                "city": tx.city,
            }
            for tx in txs
        ]

    @staticmethod
    def _dicts_to_txs(items: List[Dict[str, Any]]) -> List[Transaction]:
        result: List[Transaction] = []
        for d in items:
            try:
                result.append(
                    Transaction(
                        transaction_type=str(d["transaction_type"]),
                        good_name=str(d["good_name"]),
                        quantity=int(d["quantity"]),
                        price_per_unit=int(d["price_per_unit"]),
                        total_value=int(d["total_value"]),
                        day=int(d["day"]),
                        city=str(d["city"]),
                    )
                )
            except Exception:
                continue
        return result

    @staticmethod
    def _inv_lots_to_dicts(lots: List[InvestmentLot]) -> List[Dict[str, Any]]:
        return [
            {
                "asset_symbol": lot.asset_symbol,
                "quantity": lot.quantity,
                "purchase_price": lot.purchase_price,
                "day": lot.day,
            }
            for lot in lots
        ]

    @staticmethod
    def _dicts_to_inv_lots(items: List[Dict[str, Any]]) -> List[InvestmentLot]:
        result: List[InvestmentLot] = []
        for d in items:
            try:
                result.append(
                    InvestmentLot(
                        asset_symbol=str(d["asset_symbol"]),
                        quantity=int(d["quantity"]),
                        purchase_price=int(d["purchase_price"]),
                        day=int(d["day"]),
                    )
                )
            except Exception:
                continue
        return result

    @staticmethod
    def _loans_to_dicts(loans: List[Loan]) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        for ln in loans or []:
            try:
                items.append(
                    {
                        "loan_id": int(getattr(ln, "loan_id", 0)),
                        "principal": int(getattr(ln, "principal", 0)),
                        "remaining": int(getattr(ln, "remaining", 0)),
                        "repaid": int(getattr(ln, "repaid", 0)),
                        # Persist APR only in v2
                        "rate_annual": float(getattr(ln, "rate_annual", 0.0)),
                        "accrued_interest": float(getattr(ln, "accrued_interest", 0.0)),
                        "day_taken": int(getattr(ln, "day_taken", 0)),
                    }
                )
            except Exception:
                # Skip malformed entries
                continue
        return items

    @staticmethod
    def _dicts_to_loans(items: List[Dict[str, Any]]) -> List[Loan]:
        result: List[Loan] = []
        for d in items or []:
            try:
                # APR-first (v2). Migrate from legacy daily if needed (v1).
                rate_annual = d.get("rate_annual")
                if rate_annual is None or float(rate_annual) <= 0:
                    try:
                        rate_daily_legacy = float(d.get("rate_daily", 0.0))
                    except Exception:
                        rate_daily_legacy = 0.0
                    rate_annual = rate_daily_legacy * 365.0 if rate_daily_legacy > 0 else 0.10
                else:
                    rate_annual = float(rate_annual)
                # Clamp APR to range 1%–20%
                try:
                    rate_annual = max(0.01, min(0.20, rate_annual))
                except Exception:
                    rate_annual = 0.10
                # Accrued fractional interest carry-over (optional)
                try:
                    accrued = float(d.get("accrued_interest", 0.0))
                except Exception:
                    accrued = 0.0
                result.append(
                    Loan(
                        loan_id=int(d.get("loan_id", 0)),
                        principal=int(d.get("principal", 0)),
                        remaining=int(d.get("remaining", 0)),
                        repaid=int(d.get("repaid", 0)),
                        day_taken=int(d.get("day_taken", 0)),
                        rate_annual=rate_annual,
                        accrued_interest=accrued,
                    )
                )
            except Exception:
                continue
        return result
