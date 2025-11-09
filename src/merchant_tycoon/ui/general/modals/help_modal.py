from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.widgets import Label, Button
from textual.screen import ModalScreen


class HelpModal(ModalScreen):
    """Modal showing game instructions"""

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="help-modal"):
            yield Label("📖 HOW TO PLAY MERCHANT TYCOON", id="modal-title")

            with ScrollableContainer(id="help-content"):
                yield Label("")
                yield Label(" 🎯 GAME OBJECTIVE ", classes="section-header")
                yield Label("  Buy low, sell high, and become a wealthy merchant!")
                yield Label("  Main strategy: TRAVEL → BUY → SELL → INVEST INCOME")
                yield Label("")

                yield Label(" 💰 BASIC TRADING ", classes="section-header")
                yield Label("  • Travel (T) between cities to find the best prices")
                yield Label("  • Buy (B) goods when prices are low")
                yield Label("  • Sell (S) goods when prices are high")
                yield Label("  • Each city has different prices for different goods")
                yield Label("")

                yield Label(" 📈 STOCK EXCHANGE ", classes="section-header")
                yield Label("  • Use Buy/Sell in the TRADE box (above YOUR INVESTMENTS) or press B/S on the Investments tab")
                yield Label("  • Investments are SAFE from random events!")
                yield Label("  • Watch price trends: ▲ up, ▼ down, ─ stable")
                yield Label("  • Diversify your portfolio for better returns")
                yield Label("")

                yield Label(" 🏦 LOANS & DEBT ", classes="section-header")
                yield Label("  • Loan (L) to borrow money when you need capital")
                yield Label("  • Interest is shown as APR; it accrues daily on each loan")
                yield Label("  • Repay (R) debt as soon as possible")
                yield Label("")

                yield Label(" 📦 INVENTORY ", classes="section-header")
                yield Label("  • Inventory (I) to see detailed purchase history")
                yield Label("  • Limited space: starts at 50; press C to extend (cost doubles per slot)")
                yield Label("  • Goods sold using FIFO (First In, First Out)")
                yield Label("  • Track profit/loss for each purchase lot")
                yield Label("")

                yield Label(" ⚠️ RANDOM EVENTS ", classes="section-header")
                yield Label("  • Random events can affect your goods inventory")
                yield Label("  • Stock market investments are protected!")
                yield Label("  • Stay alert and adapt your strategy")
                yield Label("")

                yield Label(" 💡 WINNING STRATEGY ", classes="section-header")
                yield Label("  1. Start by trading goods between cities")
                yield Label("  2. Learn which cities have best prices for each good")
                yield Label("  3. Once profitable, invest excess cash in stocks")
                yield Label("  4. Build a diversified investment portfolio")
                yield Label("  5. Balance trading and investing for maximum wealth")
                yield Label("")

            yield Button("Close (ESC)", variant="success", id="close-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-btn":
            self.dismiss()

    def action_dismiss_modal(self) -> None:
        """Close the modal when ESC is pressed"""
        self.dismiss()
