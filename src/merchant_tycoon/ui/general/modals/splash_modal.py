from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label
from textual.screen import ModalScreen
from rich.text import Text

import merchant_tycoon as pkg


# Primary ASCII Art (version 1)
ART1 = r"""
 /$$      /$$                               /$$                             /$$
| $$$    /$$$                              | $$                            | $$
| $$$$  /$$$$  /$$$$$$   /$$$$$$   /$$$$$$$| $$$$$$$   /$$$$$$  /$$$$$$$  /$$$$$$
| $$ $$/$$ $$ /$$__  $$ /$$__  $$ /$$_____/| $$__  $$ |____  $$| $$__  $$|_  $$_/
| $$  $$$| $$| $$$$$$$$| $$  \__/| $$      | $$  \ $$  /$$$$$$$| $$  \ $$  | $$
| $$\  $ | $$| $$_____/| $$      | $$      | $$  | $$ /$$__  $$| $$  | $$  | $$ /$$
| $$ \/  | $$|  $$$$$$$| $$      |  $$$$$$$| $$  | $$|  $$$$$$$| $$  | $$  |  $$$$/
|__/     |__/ \_______/|__/       \_______/|__/  |__/ \_______/|__/  |__/   \___/

 /$$$$$$$$
|__  $$__/
   | $$ /$$   /$$  /$$$$$$$  /$$$$$$   /$$$$$$  /$$$$$$$
   | $$| $$  | $$ /$$_____/ /$$__  $$ /$$__  $$| $$__  $$
   | $$| $$  | $$| $$      | $$  \ $$| $$  \ $$| $$  \ $$
   | $$| $$  | $$| $$      | $$  | $$| $$  | $$| $$  | $$
   | $$|  $$$$$$$|  $$$$$$$|  $$$$$$/|  $$$$$$/| $$  | $$
   |__/ \____  $$ \_______/ \______/  \______/ |__/  |__/
        /$$  | $$
       |  $$$$$$/
        \______/
""".rstrip("\n")

# Alternate ASCII Art (version 2) — "T(ai)coon" effect
ART2 = r"""
 /$$      /$$                               /$$                             /$$
| $$$    /$$$                              | $$                            | $$
| $$$$  /$$$$  /$$$$$$   /$$$$$$   /$$$$$$$| $$$$$$$   /$$$$$$  /$$$$$$$  /$$$$$$
| $$ $$/$$ $$ /$$__  $$ /$$__  $$ /$$_____/| $$__  $$ |____  $$| $$__  $$|_  $$_/
| $$  $$$| $$| $$$$$$$$| $$  \__/| $$      | $$  \ $$  /$$$$$$$| $$  \ $$  | $$
| $$\  $ | $$| $$_____/| $$      | $$      | $$  | $$ /$$__  $$| $$  | $$  | $$ /$$
| $$ \/  | $$|  $$$$$$$| $$      |  $$$$$$$| $$  | $$|  $$$$$$$| $$  | $$  |  $$$$/
|__/     |__/ \_______/|__/       \_______/|__/  |__/ \_______/|__/  |__/   \___/

 /$$$$$$$$               /$$
|__  $$__/              |__/
   | $$         /$$$$$$  /$$          /$$$$$$$  /$$$$$$   /$$$$$$  /$$$$$$$        
   | $$ /$$$$$$|____  $$| $$ /$$$$$$ /$$_____/ /$$__  $$ /$$__  $$| $$__  $$
   | $$|______/ /$$$$$$$| $$|______/| $$      | $$  \ $$| $$  \ $$| $$  \ $$
   | $$        /$$__  $$| $$        | $$      | $$  | $$| $$  | $$| $$  | $$
   | $$       |  $$$$$$$| $$        |  $$$$$$$|  $$$$$$/|  $$$$$$/| $$  | $$
   |__/        \_______/|__/         \_______/ \______/  \______/ |__/  |__/
""".rstrip("\n")

# Ensure both arts have identical number of lines to avoid layout jumping
_ART1_LINES = ART1.splitlines()
_ART2_LINES = ART2.splitlines()
_MAX_ART_LINES = max(len(_ART1_LINES), len(_ART2_LINES))

def _pad_art(text: str) -> str:
    lines = text.splitlines()
    if len(lines) < _MAX_ART_LINES:
        lines = lines + [""] * (_MAX_ART_LINES - len(lines))
    return "\n".join(lines)

class SplashModal(ModalScreen):
    """Simple splash screen shown on startup.

    Auto-closes after 10 seconds and can be dismissed with Enter, Space, or Escape.
    The ASCII title blinks every 3 seconds by alternating between two versions.
    """

    BINDINGS = [
        ("enter", "dismiss", "Close"),
        ("space", "dismiss", "Close"),
        ("escape", "dismiss", "Close"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="splash-modal"):
            # Center container for main content
            with Container(id="splash-center"):
                # Slogan above the ASCII logo
                yield Label(
                    "Buy low • Sell high • Travel and invest",
                    classes="splash-note",
                    id="splash-slogan",
                )
                # Big ASCII title provided by user
                yield Label(_pad_art(ART1), classes="splash-ascii", id="splash-ascii")

                # Version info and author
                try:
                    version = getattr(pkg, "__version__", "")
                except Exception:
                    version = ""
                if version:
                    yield Label(f"\nVersion: {version}")
                # Author line under version
                yield Label("(C) Dariusz Przada", id="splash-author")

            # Bottom instruction
            yield Label("Press [Enter] or [Space] to continue", id="splash-instruction")

    def on_mount(self) -> None:
        # Auto-dismiss after 10 seconds
        # Use a synchronous wrapper to avoid awaiting `dismiss` from a handler
        self.set_timer(10.0, self.action_dismiss)
        # Start blinking with a constant 0.5s interval
        try:
            self._art_index = 0
            self._blink_timer = self.set_interval(0.5, self._blink_tick)
        except Exception:
            self._blink_timer = None

        # Start shimmer effect on slogan
        try:
            self._shimmer_pos = 0
            # Slightly faster than the ASCII blink to look smooth
            self._shimmer_timer = self.set_interval(0.07, self._shimmer_tick)
        except Exception:
            self._shimmer_timer = None

    def action_dismiss(self) -> None:
        self.dismiss()

    def _blink_tick(self) -> None:
        """Toggle ASCII art then reschedule next blink with shorter delay."""
        try:
            label = self.query_one('#splash-ascii', Label)
        except Exception:
            return
        try:
            # Toggle art
            self._art_index = 1 - int(getattr(self, '_art_index', 0))
            label.update(_pad_art(ART2 if self._art_index else ART1))
        except Exception:
            pass

    def _shimmer_tick(self) -> None:
        """Animate a moving light across the slogan text using Rich styles."""
        try:
            label = self.query_one('#splash-slogan', Label)
        except Exception:
            return

        try:
            raw = "Buy low • Sell high • Travel and invest"
            n = len(raw)
            if n == 0:
                return

            # Move the highlight position
            self._shimmer_pos = (getattr(self, "_shimmer_pos", 0) + 1) % (n + 8)

            # Distance-based simple gradient (center brightest)
            # Use hex shades to simulate a sweeping light
            palette = ["#777777", "#999999", "#BBBBBB", "#DDDDDD", "#FFFFFF"]
            radius = 4  # controls gradient width

            t = Text()
            center = self._shimmer_pos - 4  # offset so the brightest is not at 0 immediately

            for i, ch in enumerate(raw):
                d = abs(i - center)
                if d <= 0:
                    style = "bold #FFFFFF"
                elif d <= radius - 1:
                    style = f"bold {palette[min(len(palette)-1, radius - 1 - int(d))]}"
                elif d == radius:
                    style = palette[0]
                else:
                    style = palette[0]
                t.append(ch, style=style)

            label.update(t)
        except Exception:
            pass
