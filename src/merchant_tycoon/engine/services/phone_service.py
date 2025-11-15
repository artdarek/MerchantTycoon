from __future__ import annotations

from typing import Optional


class PhoneService:
    """Lightweight service to track active phone app and related logic.

    For now, keeps active app in-memory; default is 'whatsup'.
    """

    def __init__(self):
        self._active_app: str = "whatsup"

    def get_active_app(self) -> str:
        return self._active_app or "whatsup"

    def set_active_app(self, app_key: str) -> None:
        self._active_app = str(app_key or "whatsup").lower()

    def get_available_apps(self) -> list[tuple[str, str]]:
        """Return list of available (key, label) pairs in menu order."""
        return [
            ("whatsup", "WhatsUp"),
            ("wordle", "Wordle"),
        ]

