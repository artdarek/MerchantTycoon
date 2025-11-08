from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label
from textual.screen import ModalScreen

import merchant_tycoon as pkg


class SplashModal(ModalScreen):
    """Simple splash screen shown on startup.

    Auto-closes after 10 seconds and can be dismissed with Enter or Escape.
    """

    BINDINGS = [
        ("enter", "dismiss", "Close"),
        ("escape", "dismiss", "Close"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="splash-modal"):
            # Center container for main content
            with Container(id="splash-center"):
                # Big ASCII title provided by user
                yield Label(
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
                    """.rstrip("\n"),
                    classes="splash-ascii",
                )

                # Version info and note
                try:
                    version = getattr(pkg, "__version__", "")
                except Exception:
                    version = ""
                if version:
                    yield Label(f"Version: {version}")
                yield Label("Buy low • Sell high • Travel and invest", classes="splash-note")

            # Bottom instruction
            yield Label("Press Enter to continue", id="splash-instruction")

    def on_mount(self) -> None:
        # Auto-dismiss after 10 seconds
        self.set_timer(10.0, self.dismiss)

    def action_dismiss(self) -> None:
        self.dismiss()
