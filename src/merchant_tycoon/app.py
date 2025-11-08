#!/usr/bin/env python3
"""
Merchant Tycoon - A terminal-based trading game
Buy low, sell high, travel between cities, manage loans, survive random events!

This module hosts the main application class `MerchantTycoon` and the `main()`
entry point. It was extracted from `game.py` as part of refactoring Stage 4.
"""

from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Header, Footer, TabbedContent, TabPane, Static, Label, Button
from textual.binding import Binding
from .engine import GameEngine, GameState
from .model import CITIES
# UI modules extracted in Stage 3
from .ui.panels import (
    StatsPanel,
    MarketPanel,
    InventoryPanel,
    ExchangePricesPanel,
    InvestmentsPanel,
    MessageLog,
    TradeActionsPanel,
    GoodsTradeActionsPanel,
    AccountBalancePanel,
    AccountActionsPanel,
    AccountTransactionsPanel,
    LoanActionsPanel,
    LoanBalancePanel,
    YourLoansPanel,
)
from .ui.modals import (
    InputModal,
    CitySelectModal,
    BuyModal,
    SellModal,
    InventoryTransactionsModal,
    InvestmentsTransactionsModal,
    BuyAssetModal,
    SellAssetModal,
    HelpModal,
    AlertModal,
    ConfirmModal,
    LoanRepayModal,
    CargoExtendModal,
)


class GlobalActionsBar(Static):
    """Top bar showing global actions available at all times"""

    def compose(self) -> ComposeResult:
        with Horizontal(id="global-actions-bar"):
            yield Button("🎮 [N] New Game", id="action-new", classes="action-item")
            yield Button("💾 [A] Save", id="action-save", classes="action-item")
            yield Button("📂 [O] Load", id="action-load", classes="action-item")
            yield Button("❓ [H] Help", id="action-help", classes="action-item")
            yield Button("🚪 [Q] Quit", id="action-quit", classes="action-item")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Dispatch top bar button clicks to the same actions as hotkeys."""
        bid = event.button.id or ""
        app = self.app
        if bid == "action-new":
            app.action_new_game()
        elif bid == "action-save":
            app.action_save()
        elif bid == "action-load":
            app.action_load()
        elif bid == "action-help":
            app.action_help()
        elif bid == "action-quit":
            try:
                app.action_quit()
            except Exception:
                app.exit()


class MerchantTycoon(App):
    """Main game application"""

    # Load styles from external file created in Stage 5
    CSS_PATH = "template/style.tcss"

    # All bindings are visible in footer - key actions depend on active tab
    BINDINGS = [
        # Global actions (hidden from footer, shown in top bar)
        Binding("q", "quit", "Quit", show=False),
        Binding("h", "help", "Help", show=False),
        Binding("a", "save", "Save", show=False),
        Binding("o", "load", "Load", show=False),
        Binding("n", "new_game", "New Game", show=False),
        # Context-sensitive actions (always visible, behavior depends on active tab)
        Binding("t", "travel", "Travel", show=True),
        Binding("b", "buy", "Buy", show=True),
        Binding("s", "sell", "Sell", show=True),
        Binding("i", "transactions", "Transactions", show=True),
        Binding("l", "loan", "Loan", show=True),
        Binding("r", "repay", "Repay", show=True),
        Binding("d", "bank_deposit", "Deposit", show=True),
        Binding("w", "bank_withdraw", "Withdraw", show=True),
        Binding("c", "cargo", "Cargo", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.engine = GameEngine()
        self.message_log = None
        self.stats_panel = None
        self.market_panel = None
        self.inventory_panel = None
        self.exchange_prices_panel = None
        self.trade_actions_panel = None
        self.investments_panel = None
        self.goods_trade_actions_panel = None
        self.bank_panel = None
        self.bank_actions_panel = None
        self.loan_actions_panel = None
        self.bank_transactions_panel = None
        self.loan_balance_panel = None
        self.your_loans_panel = None
        self.current_tab = "goods-tab"  # Track current tab

    def compose(self) -> ComposeResult:
        yield Header()
        yield GlobalActionsBar()
        yield StatsPanel(self.engine)
        with TabbedContent(initial="goods-tab"):
            with TabPane("📦 Goods", id="goods-tab"):
                yield MarketPanel(self.engine)
                with Vertical(id="goods-right-col"):
                    yield GoodsTradeActionsPanel(self.engine)
                    yield InventoryPanel(self.engine)
            with TabPane("💼 Investments", id="investments-tab"):
                yield ExchangePricesPanel(self.engine)
                with Vertical(id="investments-right-col"):
                    yield TradeActionsPanel(self.engine)
                    yield InvestmentsPanel(self.engine)
            with TabPane("🏦 Bank", id="bank-tab"):
                with Vertical(id="bank-left-col"):
                    yield AccountActionsPanel(self.engine)
                    yield AccountBalancePanel(self.engine)
                    yield AccountTransactionsPanel(self.engine)
                with Vertical(id="bank-right-col"):
                    yield LoanActionsPanel(self.engine)
                    yield LoanBalancePanel(self.engine)
                    yield YourLoansPanel(self.engine)
        yield MessageLog()
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Merchant Tycoon"
        self.message_log = self.query_one(MessageLog)
        self.stats_panel = self.query_one(StatsPanel)
        self.market_panel = self.query_one(MarketPanel)
        self.inventory_panel = self.query_one(InventoryPanel)
        self.exchange_prices_panel = self.query_one(ExchangePricesPanel)
        self.trade_actions_panel = self.query_one(TradeActionsPanel)
        self.investments_panel = self.query_one(InvestmentsPanel)
        # New: goods trade panel reference
        try:
            self.goods_trade_actions_panel = self.query_one(GoodsTradeActionsPanel)
        except Exception:
            self.goods_trade_actions_panel = None
        # Bank panel references (may be missing if layout changes)
        try:
            self.bank_panel = self.query_one(AccountBalancePanel)
        except Exception:
            self.bank_panel = None
        try:
            self.bank_actions_panel = self.query_one(AccountActionsPanel)
        except Exception:
            self.bank_actions_panel = None
        try:
            self.loan_actions_panel = self.query_one(LoanActionsPanel)
        except Exception:
            self.loan_actions_panel = None
        try:
            self.bank_transactions_panel = self.query_one(AccountTransactionsPanel)
        except Exception:
            self.bank_transactions_panel = None
        try:
            self.loan_balance_panel = self.query_one(LoanBalancePanel)
        except Exception:
            self.loan_balance_panel = None
        try:
            self.your_loans_panel = self.query_one(YourLoansPanel)
        except Exception:
            self.your_loans_panel = None

        # Initialize current_tab to default
        self.current_tab = "goods-tab"

        # Auto-load savegame if present
        try:
            if self.engine.savegame_service.is_save_present():
                data = self.engine.savegame_service.load()
                if data and self.engine.savegame_service.apply(data):
                    msgs = data.get("messages") or []
                    if self.message_log and msgs:
                        self.message_log.set_messages(msgs)
                    self.game_log("Loaded savegame.")
        except Exception:
            # Ignore autoload errors and start a fresh game
            pass

        self.refresh_all()

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        """Handle tab changes - track active tab for context-aware actions"""
        self.current_tab = event.pane.id

    def refresh_all(self):
        if self.stats_panel:
            self.stats_panel.update_stats()
        if self.market_panel:
            self.market_panel.update_market()
        if self.inventory_panel:
            self.inventory_panel.update_inventory()
        if self.exchange_prices_panel:
            self.exchange_prices_panel.update_exchange_prices()
        if self.trade_actions_panel:
            self.trade_actions_panel.update_trade_actions()
        if self.goods_trade_actions_panel:
            self.goods_trade_actions_panel.update_trade_actions()
        if self.investments_panel:
            self.investments_panel.update_investments()
        if self.bank_panel:
            self.bank_panel.update_bank()
        if self.bank_actions_panel:
            self.bank_actions_panel.update_actions()
        if self.loan_actions_panel:
            self.loan_actions_panel.update_actions()
        if self.loan_balance_panel:
            self.loan_balance_panel.update_loan()
        if self.your_loans_panel:
            self.your_loans_panel.update_loans()
        if self.bank_transactions_panel:
            self.bank_transactions_panel.update_transactions()

    def game_log(self, msg: str):
        # Prefix each log entry with timestamp and the in-game day number
        day = self.engine.state.day
        ts = datetime.now().strftime("%H:%M:%S")
        if self.message_log:
            self.message_log.add_message(f"[{ts}] Day {day}: {msg}")

    def action_buy(self):
        """Context-aware Buy: goods or assets depending on active tab.
        Disabled on Bank tab per UX requirements (no Buy/Sell in Bank).
        """
        try:
            tabbed = self.query_one(TabbedContent)
            active = getattr(tabbed, "active", None)
        except Exception:
            active = None

        # Do not allow Buy on the Bank tab
        if active == "bank-tab":
            return

        if active == "investments-tab":
            # Open assets buy modal when Investments tab is active
            self.push_screen(BuyAssetModal(self.engine, self._handle_asset_trade))
        else:
            # Default to goods
            modal = BuyModal(self.engine, self._handle_buy)
            self.push_screen(modal)

    def _handle_buy(self, product: str, quantity: int):
        """Handle buy transaction"""
        if quantity <= 0:
            self.game_log("Quantity must be positive!")
            return

        success, msg = self.engine.buy(product, quantity)
        self.game_log(msg)
        self.refresh_all()

    def action_sell(self):
        """Context-aware Sell: goods or assets depending on active tab.
        Disabled on Bank tab per UX requirements (no Buy/Sell in Bank).
        """
        try:
            tabbed = self.query_one(TabbedContent)
            active = getattr(tabbed, "active", None)
        except Exception:
            active = None

        # Do not allow Sell on the Bank tab
        if active == "bank-tab":
            return

        if active == "investments-tab":
            # Selling assets
            if not self.engine.state.portfolio:
                self.game_log("No assets to sell!")
                return
            self.push_screen(SellAssetModal(self.engine, self._handle_asset_trade))
        else:
            # Selling goods
            if not self.engine.state.inventory:
                self.game_log("No goods to sell!")
                return
            modal = SellModal(self.engine, self._handle_sell)
            self.push_screen(modal)

    def _handle_sell(self, product: str, quantity: int):
        """Handle sell transaction"""
        if quantity <= 0:
            self.game_log("Quantity must be positive!")
            return

        success, msg = self.engine.sell(product, quantity)
        self.game_log(msg)
        self.refresh_all()

    def _handle_asset_trade(self, msg: str):
        """Handle result message from asset buy/sell modals"""
        self.game_log(msg)
        self.refresh_all()

    def action_travel(self):
        """Travel to another city"""
        modal = CitySelectModal(CITIES, self.engine.state.current_city, self._handle_travel)
        self.push_screen(modal)

    def action_cargo(self):
        """Open modal to extend cargo capacity by purchasing an extra slot."""
        try:
            modal = CargoExtendModal(self.engine, self._handle_extend_cargo)
            self.push_screen(modal)
        except Exception as e:
            self.game_log(f"Error opening cargo modal: {e}")

    def _handle_extend_cargo(self) -> bool:
        """Callback used by CargoExtendModal when Extend is pressed.
        Returns True to close the modal on success, False to keep it open on failure.
        """
        try:
            result = self.engine.extend_cargo()
        except Exception as e:
            self.game_log(f"Error: {e}")
            return False

        # Interpret tuple shapes per service contract
        if not result:
            self.game_log("Unexpected response from engine.")
            return False

        ok = bool(result[0])
        if ok:
            # (True, msg, new_capacity, next_cost)
            msg = result[1] if len(result) > 1 else "Cargo extended."
            self.game_log(msg)
            self.refresh_all()
            return True
        else:
            # (False, msg, current_cost)
            msg = result[1] if len(result) > 1 else "Not enough cash to extend cargo."
            self.game_log(msg)
            return False

    def _handle_travel(self, city_index: int):
        """Handle travel to new city"""
        success, msg, event_data = self.engine.travel(city_index)
        if success:
            self.game_log(msg)
            if event_data:
                event_msg, is_positive = event_data
                self.game_log(event_msg)  # Log for history
                title = "✨ Good News!" if is_positive else "⚠️ Bad News!"
                modal = AlertModal(title, event_msg, is_positive)
                self.push_screen(modal)
            self.refresh_all()
        else:
            self.game_log(msg)

    def action_loan(self):
        """Take a loan"""
        # Show today's APR offer for new loans (existing loans keep their own APR)
        try:
            apr_offer = float(getattr(self.engine, "loan_apr_today", 0.10))
        except Exception:
            apr_offer = 0.10
        apr_pct = f"{apr_offer*100:.2f}"
        max_amount = 10000
        prompt = (
            "How much would you like to borrow?\n"
            f"(Max: ${max_amount:,} | Today's offer: {apr_pct}% APR, accrued daily)"
        )
        modal = InputModal(
            "🏦 Bank Loan",
            prompt,
            self._handle_loan,
            str(max_amount),
        )
        self.push_screen(modal)

    def _handle_loan(self, value: str):
        """Handle loan request"""
        try:
            amount = int(value.strip())
        except ValueError:
            self.game_log("Invalid amount!")
            return

        success, msg = self.engine.take_loan(amount)
        self.game_log(msg)
        self.refresh_all()

    def action_repay(self):
        """Repay loan. Opens a modal to select which loan to repay and amount."""
        # Filter active loans
        active_loans = [ln for ln in (self.engine.state.loans or []) if getattr(ln, "remaining", 0) > 0]
        if not active_loans or self.engine.state.cash <= 0:
            self.game_log("No repayable loans or no cash available!")
            return

        # Open new modal with loan selector and prefilled amount
        self.push_screen(LoanRepayModal(self.engine, self._handle_repay_selected))

    def _handle_repay_selected(self, loan_id: int, amount: int):
        """Handle loan repayment for a specific loan selected in modal."""
        try:
            amt = int(amount)
        except Exception:
            self.game_log("Invalid amount!")
            return
        ok, msg = self.engine.repay_loan_for(int(loan_id), amt)
        self.game_log(msg)
        self.refresh_all()

    def action_transactions(self):
        """Context-aware Transactions: show goods or investments depending on active tab"""
        try:
            tabbed = self.query_one(TabbedContent)
            active = getattr(tabbed, "active", None)
        except Exception:
            active = None

        if active == "investments-tab":
            self.action_investment_transactions()
        else:  # goods-tab (default)
            self.action_goods_transactions()

    def action_goods_transactions(self):
        """Show detailed inventory with purchase lots"""
        if not self.engine.state.inventory:
            self.game_log("No goods in inventory!")
            return

        modal = InventoryTransactionsModal(self.engine)
        self.push_screen(modal)

    def action_investment_transactions(self):
        """Show detailed investments with purchase lots"""
        if not self.engine.state.portfolio:
            self.game_log("No investments in portfolio!")
            return

        modal = InvestmentsTransactionsModal(self.engine)
        self.push_screen(modal)

    # --- Bank actions ---
    def action_bank_deposit(self):
        """Open modal to deposit cash to bank."""
        cash = self.engine.state.cash
        if cash <= 0:
            self.game_log("No cash to deposit!")
            return
        modal = InputModal(
            "🏦 Deposit to Bank",
            f"Cash available: ${cash:,}\nHow much to deposit?",
            self._handle_bank_deposit,
            default_value=str(cash),
        )
        self.push_screen(modal)

    def _handle_bank_deposit(self, value: str):
        try:
            amount = int(value.strip())
        except ValueError:
            self.game_log("Invalid amount!")
            return
        ok, msg = self.engine.deposit_to_bank(amount)
        self.game_log(msg)
        self.refresh_all()

    def action_bank_withdraw(self):
        """Open modal to withdraw cash from bank."""
        bal = self.engine.state.bank.balance
        if bal <= 0:
            self.game_log("No funds in bank to withdraw!")
            return
        modal = InputModal(
            "🏦 Withdraw from Bank",
            f"Bank balance: ${bal:,}\nHow much to withdraw?",
            self._handle_bank_withdraw,
            default_value=str(bal),
        )
        self.push_screen(modal)

    def _handle_bank_withdraw(self, value: str):
        try:
            amount = int(value.strip())
        except ValueError:
            self.game_log("Invalid amount!")
            return
        ok, msg = self.engine.withdraw_from_bank(amount)
        self.game_log(msg)
        self.refresh_all()

    def action_help(self):
        """Show game instructions"""
        modal = HelpModal()
        self.push_screen(modal)

    def action_save(self):
        """Save current game to disk (single slot)."""
        try:
            msgs = self.message_log.messages if self.message_log else []
            ok, msg = self.engine.savegame_service.save(msgs)
            if ok:
                self.game_log("Game saved.")
            else:
                self.game_log(msg)
        except Exception as e:
            self.game_log(f"Save failed: {e}")

    def action_load(self):
        """Load saved game from disk."""
        if not self.engine.savegame_service.is_save_present():
            self.game_log("No save file found!")
            return

        def _confirm_load():
            try:
                data = self.engine.savegame_service.load()
                if data and self.engine.savegame_service.apply(data):
                    msgs = data.get("messages") or []
                    if self.message_log and msgs:
                        self.message_log.set_messages(msgs)
                    self.game_log("Loaded savegame.")
                    self.refresh_all()
                else:
                    self.game_log("Failed to load save file.")
            except Exception as e:
                self.game_log(f"Load failed: {e}")

        confirm = ConfirmModal(
            "Load Game",
            "Load saved game? Current progress will be lost if not saved.",
            on_confirm=_confirm_load,
        )
        self.push_screen(confirm)

    def action_new_game(self):
        """Ask for confirmation, then delete save and reset state."""
        def _confirm_new():
            try:
                # Delete save file if exists
                self.engine.savegame_service.delete_save()
            except Exception:
                pass
            # Reset engine state safely via engine helper (rebinding services & prices)
            try:
                self.engine.new_game()
            except Exception:
                # Fallback to legacy behavior if helper not present
                self.engine.state = GameState()
                self.engine.generate_prices()
                self.engine.generate_asset_prices()
            # Reset messages to default welcome
            if self.message_log:
                self.message_log.reset_messages()
            self.game_log("New game started.")
            self.refresh_all()

        confirm = ConfirmModal(
            "Start New Game",
            "Start a new game? This will delete the current save.",
            on_confirm=_confirm_new,
        )
        self.push_screen(confirm)

    def action_quit(self):
        """Show quit modal with two explicit options: Save&Quit or Just quit!"""
        def _save_and_quit():
            # Save game, then exit regardless of save outcome
            try:
                msgs = self.message_log.messages if self.message_log else []
                ok, msg = self.engine.savegame_service.save(msgs)
                if ok:
                    self.game_log("Game saved.")
                else:
                    self.game_log(msg)
            except Exception as e:
                self.game_log(f"Save failed: {e}")
            finally:
                try:
                    self.exit()
                except Exception:
                    pass

        def _just_quit():
            # Exit immediately, do not write save file
            try:
                self.exit()
            except Exception:
                pass

        confirm = ConfirmModal(
            "Quit Game",
            "Do you want to save your progress before exit?",
            on_confirm=_save_and_quit,
            on_cancel=_just_quit,
            confirm_label="Save and exit",
            cancel_label="Exit",
        )
        self.push_screen(confirm)


def main():
    """Entry point for the game"""
    app = MerchantTycoon()
    app.run()


if __name__ == "__main__":
    main()
