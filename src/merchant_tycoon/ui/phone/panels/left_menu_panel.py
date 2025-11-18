from textual.app import ComposeResult
from textual.widgets import Static, Button, Label
from textual.containers import Vertical, Horizontal

from merchant_tycoon.engine import GameEngine


class LeftMenuPanel(Static):
    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("📱 APPS", classes="panel-title")
        # Grid: 3 boxes per row
        apps = list(self.engine.phone_service.get_available_apps())
        # Map simple emojis per app
        icons = {
            "home": "🏠",
            "whatsup": "📨",
            "closeai": "💬",
            "wordle": "🧩",
            "camera": "📷",
            "snake": "🐍",
        }
        rows = [apps[i:i+3] for i in range(0, len(apps), 3)]
        with Vertical(id="phone-menu-grid"):
            for row in rows:
                with Horizontal(classes="app-row"):
                    for key, label in row:
                        with Static(classes="app-card"):
                            icon = icons.get(key, "📱")
                            # Put icon and name inside the same button; icon clickable.
                            # Add one empty line between icon and name.
                            btn_label = f"{icon}\n\n{label}"
                            yield Button(btn_label, id=f"phone-menu-{key}", classes="app-btn")
                    # If fewer than 3, fill with empty cards for layout consistency
                    for _ in range(3 - len(row)):
                        yield Static(classes="app-card")

    def update_menu(self) -> None:
        active = self.engine.phone_service.get_active_app()
        for key, _ in self.engine.phone_service.get_available_apps():
            try:
                btn = self.query_one(f"#phone-menu-{key}", Button)
                # Use success variant to highlight active app
                btn.variant = "success" if key == active else "default"
            except Exception:
                pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Map button id back to app key
        btn_id = event.button.id or ""
        for key, _ in self.engine.phone_service.get_available_apps():
            if btn_id == f"phone-menu-{key}":
                self.engine.phone_service.set_active_app(key)
                # Notify ancestor PhonePanel to refresh screen
                refreshed = False
                try:
                    node = self.parent
                    # Walk up until we find a refresh_phone method
                    while node is not None and not hasattr(node, "refresh_phone"):
                        node = getattr(node, "parent", None)
                    if node is not None:
                        node.refresh_phone()
                        refreshed = True
                except Exception:
                    pass
                if not refreshed:
                    # Fallback: refresh whole app
                    try:
                        self.app.refresh_all()
                    except Exception:
                        pass
                break
