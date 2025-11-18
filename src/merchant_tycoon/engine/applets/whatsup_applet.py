from __future__ import annotations

from typing import List, Dict, Any, Sequence


class WhatsUpApplet:
    """Adaptor over Messenger to serve the WhatsUp applet.

    Keeps UI decoupled from the messenger internals.
    """

    def __init__(self, messenger: object):
        self._messenger = messenger

    def get_entries(self) -> Sequence[Dict[str, Any]]:
        try:
            entries = self._messenger.get_entries()
            # Return as-is; UI formats presentation
            return entries
        except Exception:
            return []
