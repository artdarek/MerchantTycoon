from textual.app import ComposeResult
from textual.widgets import Static, Button, Label
from textual.containers import Vertical

from merchant_tycoon.engine import GameEngine


class LeftMenuPanel(Static):
    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        yield Label("📱 APPS", classes="panel-title")
        with Vertical(id="phone-menu"):
            for key, label in self.engine.phone_service.get_available_apps():
                btn = Button(label, id=f"phone-menu-{key}")
                yield btn

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
