from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label
from textual.screen import ModalScreen

import merchant_tycoon as pkg


# Primary ASCII Art (version 1)
ART1 = (
    """
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
)

# Alternate ASCII Art (version 2) — "T(ai)coon" effect
ART2 = (
    """
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
)

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
                yield Label("Buy low • Sell high • Travel and invest", classes="splash-note")
                # Big ASCII title provided by user
                yield Label(_pad_art(ART1), classes="splash-ascii", id="splash-ascii")

                # Version info and author
                try:
                    version = getattr(pkg, "__version__", "")
                except Exception:
                    version = ""
                if version:
                    yield Label(f"Version: {version}")
                # Author line under version
                yield Label("(C) Dariusz Przada", id="splash-author")

            # Bottom instruction
            yield Label("Press [Enter] or [Space] to continue", id="splash-instruction")

    def on_mount(self) -> None:
        # Auto-dismiss after 10 seconds
        self.set_timer(10.0, self.dismiss)
        # Start blinking with a constant 0.5s interval
        try:
            self._art_index = 0
            self._blink_timer = self.set_interval(0.5, self._blink_tick)
        except Exception:
            self._blink_timer = None

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
