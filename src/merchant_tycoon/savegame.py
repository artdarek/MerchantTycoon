from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

from .engine import GameEngine, GameState
from .engine.savegame_service import SavegameService
from .model import PurchaseLot, Transaction, InvestmentLot, BankTransaction, BankAccount, Loan


SCHEMA_VERSION = 1


def get_save_dir() -> Path:
    """[DEPRECATED] Use engine.SavegameService.get_save_dir()."""
    return SavegameService.get_save_dir()


def get_save_path() -> Path:
    """[DEPRECATED] Use engine.SavegameService.get_save_path()."""
    return SavegameService.get_save_path()


def is_save_present() -> bool:
    """[DEPRECATED] Use engine.SavegameService.is_save_present()."""
    return SavegameService.is_save_present()


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
    """[DEPRECATED] Use engine.SavegameService(engine).save(messages)."""
    try:
        # Prefer the service attached to engine if present
        service = getattr(engine, "savegame_service", None)
        if service is None:
            from .engine.savegame_service import SavegameService as _Svc
            service = _Svc(engine)
        return service.save(messages)
    except Exception as e:
        return False, f"Save failed: {e}"


def load_game() -> Optional[Dict[str, Any]]:
    """[DEPRECATED] Use engine.SavegameService.load()."""
    try:
        data = SavegameService.load()
        if not isinstance(data, dict):
            return None
        if int(data.get("schema_version", 0)) != SCHEMA_VERSION:
            # for MVP require exact match
            return None
        return data
    except Exception:
        return None


def apply_loaded_game(engine: GameEngine, data: Dict[str, Any]) -> bool:
    """[DEPRECATED] Use engine.SavegameService(engine).apply(data)."""
    try:
        service = getattr(engine, "savegame_service", None)
        if service is None:
            from .engine.savegame_service import SavegameService as _Svc
            service = _Svc(engine)
        return service.apply(data)
    except Exception:
        return False


def delete_save() -> Tuple[bool, str]:
    """[DEPRECATED] Use engine.SavegameService.delete_save()."""
    try:
        SavegameService.delete_save()
        return True, "Save deleted"
    except Exception as e:
        return False, f"Delete failed: {e}"
