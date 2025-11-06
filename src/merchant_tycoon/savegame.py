from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

from .engine import GameEngine, GameState
from .models import PurchaseLot, Transaction, InvestmentLot


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


def save_game(engine: GameEngine, messages: List[str]) -> Tuple[bool, str]:
    """Persist the current game to JSON file.

    Returns (ok, message).
    """
    try:
        save_dir = get_save_dir()
        save_dir.mkdir(parents=True, exist_ok=True)
        path = get_save_path()

        state = engine.state
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

        engine.state = new_state

        # Prices
        engine.prices = dict(p.get("goods", {}))
        engine.previous_prices = dict(p.get("goods_prev", {}))
        engine.asset_prices = dict(p.get("assets", {}))
        engine.previous_asset_prices = dict(p.get("assets_prev", {}))
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
