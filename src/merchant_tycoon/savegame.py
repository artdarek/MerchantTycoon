from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

from .engine import GameEngine, GameState
from .models import PurchaseLot, Transaction, InvestmentLot, BankTransaction, BankAccount, Loan


SCHEMA_VERSION = 1


def get_save_dir() -> Path:
    home = Path(os.path.expanduser("~"))
    return home / ".merchant_tycoon"


def get_save_path() -> Path:
    return get_save_dir() / "savegame.json"


def is_save_present() -> bool:
    return get_save_path().exists()


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


# --- Loans converters ---

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
                    # Persist both APR and legacy daily for compatibility
                    "rate_annual": float(getattr(ln, "rate_annual", 0.0)),
                    "rate_daily": float(getattr(ln, "rate_daily", 0.0)),
                    "accrued_interest": float(getattr(ln, "accrued_interest", 0.0)),
                    "day_taken": int(getattr(ln, "day_taken", 0)),
                }
            )
        except Exception:
            # Skip malformed entries
            continue
    return items


def _dicts_to_loans(items: List[Dict[str, Any]]) -> List[Loan]:
    result: List[Loan] = []
    for d in items or []:
        try:
            # Prefer APR if present; otherwise derive from legacy daily
            try:
                rate_annual = float(d.get("rate_annual"))
            except Exception:
                rate_annual = None
            try:
                rate_daily_legacy = float(d.get("rate_daily", 0.0))
            except Exception:
                rate_daily_legacy = 0.0
            if rate_annual is None or rate_annual <= 0:
                if rate_daily_legacy > 0:
                    rate_annual = rate_daily_legacy * 365.0
                else:
                    rate_annual = 0.10  # sensible default APR for legacy saves
            # Clamp APR to agreed range 1%–20%
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
                    rate_daily=rate_daily_legacy if rate_daily_legacy > 0 else rate_annual / 365.0,
                    day_taken=int(d.get("day_taken", 0)),
                    rate_annual=rate_annual,
                    accrued_interest=accrued,
                )
            )
        except Exception:
            continue
    return result


def save_game(engine: GameEngine, messages: List[str]) -> Tuple[bool, str]:
    """Persist the current game to JSON file.

    Returns (ok, message).
    """
    try:
        save_dir = get_save_dir()
        save_dir.mkdir(parents=True, exist_ok=True)
        path = get_save_path()

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

        payload = {
            "schema_version": SCHEMA_VERSION,
            "state": {
                "cash": state.cash,
                "debt": state.debt,
                "day": state.day,
                "current_city": state.current_city,
                "inventory": dict(state.inventory),
                "max_inventory": state.max_inventory,
                "purchase_lots": _lots_to_dicts(state.purchase_lots),
                "transaction_history": _tx_to_dicts(state.transaction_history),
                "portfolio": dict(state.portfolio),
                "investment_lots": _inv_lots_to_dicts(state.investment_lots),
                # Loans list (multi-loan support). Optional for backward compatibility.
                "loans": _loans_to_dicts(state.loans),
                # Current global loan rates offer (optional; defaults on load if missing)
                "loan_rate_annual": float(getattr(engine, "loan_apr_today", 0.10)),
                "loan_rate_daily": float(getattr(engine, "interest_rate", 0.10)),  # legacy
                # New optional bank section (backward compatible)
                "bank": {
                    "balance": bank.balance,
                    # Persist both annual APR and legacy daily rate for backward compatibility
                    "rate_annual": getattr(bank, "interest_rate_annual", 0.02),
                    "rate": getattr(bank, "interest_rate_daily", 0.0005),
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


def load_game() -> Optional[Dict[str, Any]]:
    """Load and parse the save file. Returns dict or None if missing/invalid."""
    path = get_save_path()
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return None
        if int(data.get("schema_version", 0)) != SCHEMA_VERSION:
            # for MVP require exact match
            return None
        return data
    except Exception:
        return None


def apply_loaded_game(engine: GameEngine, data: Dict[str, Any]) -> bool:
    """Apply loaded payload to the existing engine/state. Returns success flag."""
    try:
        s = data.get("state", {})
        p = data.get("prices", {})

        # Replace state in-place
        new_state = GameState()
        new_state.cash = int(s.get("cash", new_state.cash))
        new_state.debt = int(s.get("debt", new_state.debt))
        new_state.day = int(s.get("day", new_state.day))
        new_state.current_city = int(s.get("current_city", new_state.current_city))
        new_state.inventory = dict(s.get("inventory", {}))
        new_state.max_inventory = int(s.get("max_inventory", new_state.max_inventory))
        new_state.purchase_lots = _dicts_to_lots(list(s.get("purchase_lots", [])))
        new_state.transaction_history = _dicts_to_txs(list(s.get("transaction_history", [])))
        new_state.portfolio = dict(s.get("portfolio", {}))
        new_state.investment_lots = _dicts_to_inv_lots(list(s.get("investment_lots", [])))
        
        # Loans (explicit multi-loan support). Legacy single-loan synthesis removed.
        has_loans_key = "loans" in s
        try:
            loans_list = _dicts_to_loans(list(s.get("loans", [])))
        except Exception:
            loans_list = []
        new_state.loans = loans_list

        # Bank (optional for backward compatibility)
        bank_data = s.get("bank")
        if bank_data:
            txs: List[BankTransaction] = []
            for d in bank_data.get("transactions", []):
                try:
                    txs.append(
                        BankTransaction(
                            tx_type=str(d.get("type", "")),
                            amount=int(d.get("amount", 0)),
                            balance_after=int(d.get("balance_after", 0)),
                            day=int(d.get("day", new_state.day)),
                            title=str(d.get("title", "")),
                        )
                    )
                except Exception:
                    continue
            # Prefer annual rate if present; keep legacy daily for backward compatibility
            try:
                rate_annual = float(bank_data.get("rate_annual"))
            except Exception:
                rate_annual = None
            if rate_annual is None or rate_annual <= 0:
                # If only legacy daily provided, we will not upscale *365; per user we use a sensible default APR
                rate_annual = 0.02
            # Set daily from provided legacy if any; otherwise derive from APR
            try:
                rate_daily = float(bank_data.get("rate", 0.0005))
            except Exception:
                rate_daily = rate_annual / 365.0
            new_state.bank = BankAccount(
                balance=int(bank_data.get("balance", 0)),
                interest_rate_daily=rate_daily,
                interest_rate_annual=rate_annual,
                accrued_interest=float(bank_data.get("accrued", 0.0)),
                last_interest_day=int(bank_data.get("last_day", new_state.day)),
                transactions=txs,
            )
        else:
            # Defaults if not present
            new_state.bank = BankAccount(
                balance=0,
                interest_rate_daily=0.0005,
                interest_rate_annual=0.02,
                accrued_interest=0.0,
                last_interest_day=new_state.day,
                transactions=[],
            )

        engine.state = new_state

        # Prices
        engine.prices = dict(p.get("goods", {}))
        engine.previous_prices = dict(p.get("goods_prev", {}))
        engine.asset_prices = dict(p.get("assets", {}))
        engine.previous_asset_prices = dict(p.get("assets_prev", {}))

        # Restore current global loan rates if present (optional fields)
        try:
            engine.loan_apr_today = float(s.get("loan_rate_annual", getattr(engine, "loan_apr_today", 0.10)))
        except Exception:
            # fallback if only daily provided
            try:
                engine.loan_apr_today = float(s.get("loan_rate_daily", 0.10)) * 365.0
            except Exception:
                engine.loan_apr_today = getattr(engine, "loan_apr_today", 0.10)
        # Keep legacy daily rate synchronized for compatibility
        try:
            engine.interest_rate = float(s.get("loan_rate_daily", engine.loan_apr_today / 365.0))
        except Exception:
            engine.interest_rate = engine.loan_apr_today / 365.0

        # Ensure aggregate debt is consistent when loans are present
        if getattr(engine.state, "loans", None):
            try:
                engine._sync_total_debt()
            except Exception:
                pass

        # Accrue any missed interest up to the loaded current day (idempotent)
        try:
            engine.accrue_bank_interest()
        except Exception:
            pass

        return True
    except Exception:
        return False


def delete_save() -> Tuple[bool, str]:
    try:
        path = get_save_path()
        if path.exists():
            path.unlink()
            return True, "Save deleted"
        return True, "No save to delete"
    except Exception as e:
        return False, f"Delete failed: {e}"
