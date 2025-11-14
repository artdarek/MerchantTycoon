"""
Merchant Tycoon — Textual TUI application.

This module defines the main UI class `MerchantTycoon` and supporting widgets
used by the game. It does not provide a top‑level `main()` function. To run the
app, use one of the configured entry points:

- Module: `python -m merchant_tycoon` (handled by `merchant_tycoon.__main__`)
- Console script: `merchant-tycoon` (configured in pyproject)
"""

import os
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Footer, TabbedContent, TabPane, Static, Label, Button
from textual.binding import Binding
from merchant_tycoon.engine import GameEngine, GameState
from merchant_tycoon.config import SETTINGS
from merchant_tycoon.domain.cities import CITIES
from merchant_tycoon.ui.general.panels import StatsPanel, MessangerPanel, GlobalActionsBar
from merchant_tycoon.ui.goods.panels import (
    GoodsPricesPanel,
    GoodsTradeActionsPanel,
    InventoryPanel,
    InventoryLotsPanel,
)
from merchant_tycoon.ui.investments.panels import (
    ExchangePricesPanel,
    InvestmentsPanel,
    TradeActionsPanel,
    InvestmentsLotsPanel,
)
from merchant_tycoon.ui.bank.panels import (
    AccountBalancePanel,
    AccountActionsPanel,
    AccountTransactionsPanel,
    LoanActionsPanel,
    LoanBalancePanel,
    YourLoansPanel,
)
from merchant_tycoon.ui.general.modals import (
    InputModal,
    TravelModal,
    HelpModal,
    AboutModal,
    SplashModal,
    AlertModal,
    ConfirmModal,
    CargoExtendModal,
    EventModal,
)
from merchant_tycoon.ui.goods.modals import (
    BuyModal,
    SellModal,
)
from merchant_tycoon.ui.investments.modals import (
    BuyAssetModal,
    SellAssetModal,
)
from merchant_tycoon.ui.bank.modals import LoanRepayModal


class MerchantTycoon(App):
    """Main game application"""

    # Load styles from external file created in Stage 5
    CSS_PATH = "template/style.tcss"

    # Explicitly disable Textual's command palette if present
    ENABLE_COMMAND_PALETTE = False

    # All bindings are visible in footer - key actions depend on active tab
    BINDINGS = [
        # Global actions (hidden from footer, shown in top bar)
        Binding("q", "quit", "Quit", show=False),
        Binding("escape", "quit", "Quit", show=False),
        Binding("f4", "help", "Help", show=False),
        Binding("f2", "save", "Save", show=False),
        Binding("f3", "load", "Load", show=False),
        Binding("f1", "new_game", "New Game", show=False),
        Binding("f5", "about", "About", show=False),
        Binding("f9", "splash", "Splash", show=False),
        # Tab shortcuts
        Binding("1", "go_goods_tab", "Goods", show=True),
        Binding("2", "go_investments_tab", "Investments", show=True),
        Binding("3", "go_bank_tab", "Bank", show=True),
        # Override common command-palette shortcuts with no-ops
        Binding("ctrl+k", "noop", show=False),
        Binding("ctrl+p", "noop", show=False),
        # Context-sensitive actions (always visible, behavior depends on active tab)
        Binding("t", "travel", "Travel", show=True),
        Binding("b", "buy", "Buy", show=True),
        Binding("s", "sell", "Sell", show=True),
        Binding("l", "loan", "Loan", show=True),
        Binding("r", "repay", "Repay", show=True),
        Binding("d", "bank_deposit", "Deposit", show=True),
        Binding("w", "bank_withdraw", "Withdraw", show=True),
        Binding("c", "cargo", "Cargo", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.engine = GameEngine()
        self.messanger_panel = None
        self.stats_panel = None
        self.market_panel = None
        self.inventory_panel = None
        self.inventory_lots_panel = None
        self.exchange_prices_panel = None
        self.trade_actions_panel = None
        self.investments_panel = None
        self.investments_lots_panel = None
        self.goods_trade_actions_panel = None
        self.bank_panel = None
        self.bank_actions_panel = None
        self.loan_actions_panel = None
        self.bank_transactions_panel = None
        self.loan_balance_panel = None
        self.your_loans_panel = None
        self.current_tab = "goods-tab"  # Track current tab

    def compose(self) -> ComposeResult:
        yield GlobalActionsBar()
        yield StatsPanel(self.engine)
        with TabbedContent(initial="goods-tab"):
            with TabPane("📦 Goods", id="goods-tab"):
                yield GoodsPricesPanel(self.engine)
                with Vertical(id="goods-right-col"):
                    yield GoodsTradeActionsPanel(self.engine)
                    yield InventoryPanel(self.engine)
                    yield InventoryLotsPanel(self.engine)
            with TabPane("💼 Investments", id="investments-tab"):
                yield ExchangePricesPanel(self.engine)
                with Vertical(id="investments-right-col"):
                    yield TradeActionsPanel(self.engine)
                    yield InvestmentsPanel(self.engine)
                    yield InvestmentsLotsPanel(self.engine)
            with TabPane("🏦 Bank", id="bank-tab"):
                with Vertical(id="bank-left-col"):
                    yield AccountBalancePanel(self.engine)
                    yield AccountActionsPanel(self.engine)
                    yield AccountTransactionsPanel(self.engine)
                with Vertical(id="bank-right-col"):
                    yield LoanBalancePanel(self.engine)
                    yield LoanActionsPanel(self.engine)
                    yield YourLoansPanel(self.engine)
        yield MessangerPanel()
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Merchant Tycoon"
        self.messanger_panel = self.query_one(MessangerPanel)
        try:
            self.global_actions_bar = self.query_one(GlobalActionsBar)
        except Exception:
            self.global_actions_bar = None
        self.stats_panel = self.query_one(StatsPanel)
        self.market_panel = self.query_one(GoodsPricesPanel)
        self.inventory_panel = self.query_one(InventoryPanel)
        try:
            self.inventory_lots_panel = self.query_one(InventoryLotsPanel)
        except Exception:
            self.inventory_lots_panel = None
        self.exchange_prices_panel = self.query_one(ExchangePricesPanel)
        self.trade_actions_panel = self.query_one(TradeActionsPanel)
        self.investments_panel = self.query_one(InvestmentsPanel)
        try:
            self.investments_lots_panel = self.query_one(InvestmentsLotsPanel)
        except Exception:
            self.investments_lots_panel = None
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

        # Splash screen (configurable via SETTINGS.game.show_splash)
        try:
            if SETTINGS.game.show_splash:
                self.push_screen(SplashModal())
        except Exception:
            pass

        # Auto-load savegame if present (may occur while splash is visible)
        try:
            if self.engine.savegame_service.is_save_present():
                data = self.engine.savegame_service.load()
                if data and self.engine.savegame_service.apply(data):
                    # Messages handled inside savegame apply via messenger
                    try:
                        self.messanger_panel.update_messages()
                    except Exception:
                        pass
                    # Optional: add operational note
                    self.engine.messenger.debug("Loaded savegame.", tag="system")
        except Exception:
            # Ignore autoload errors and start a fresh game
            pass

        self.refresh_all()

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        """Handle tab changes - track active tab for context-aware actions"""
        self.current_tab = event.pane.id

    # --- Tab shortcuts ---
    def action_go_goods_tab(self) -> None:
        try:
            self.query_one(TabbedContent).active = "goods-tab"
            self.current_tab = "goods-tab"
        except Exception:
            pass

    def action_go_investments_tab(self) -> None:
        try:
            self.query_one(TabbedContent).active = "investments-tab"
            self.current_tab = "investments-tab"
        except Exception:
            pass

    def action_go_bank_tab(self) -> None:
        try:
            self.query_one(TabbedContent).active = "bank-tab"
            self.current_tab = "bank-tab"
        except Exception:
            pass

    def refresh_all(self):

        if self.stats_panel:
            self.stats_panel.update_stats()
        if self.market_panel:
            self.market_panel.update_goods_prices()
        if self.inventory_panel:
            self.inventory_panel.update_inventory()
        if self.inventory_lots_panel:
            self.inventory_lots_panel.update_lots()
        if self.exchange_prices_panel:
            self.exchange_prices_panel.update_exchange_prices()
        if self.trade_actions_panel:
            self.trade_actions_panel.update_trade_actions()
        if self.goods_trade_actions_panel:
            self.goods_trade_actions_panel.update_trade_actions()
        if self.investments_panel:
            self.investments_panel.update_investments()
        if self.investments_lots_panel:
            self.investments_lots_panel.update_lots()
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
        # Refresh message log to reflect any new messenger entries
        try:
            if self.messanger_panel:
                self.messanger_panel.update_messages()
        except Exception:
            pass
        # Update top bar info (date/city)
        try:
            if getattr(self, "global_actions_bar", None):
                self.global_actions_bar.update_info()
        except Exception:
            pass

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
            self.engine.messenger.warn("Quantity must be positive!", tag="goods")
            return

        success, msg = self.engine.goods_service.buy(product, quantity)

        if not success:
            self.engine.messenger.warn(msg, tag="goods")
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
                self.engine.messenger.warn("No assets to sell!", tag="investments")
                return
            self.push_screen(SellAssetModal(self.engine, self._handle_asset_trade))
        else:
            # Selling goods
            if not self.engine.state.inventory:
                self.engine.messenger.warn("No goods to sell!", tag="goods")
                return
            modal = SellModal(self.engine, self._handle_sell)
            self.push_screen(modal)

    def _handle_sell(self, product: str, quantity: int):
        """Handle sell transaction"""
        if quantity <= 0:
            self.engine.messenger.warn("Quantity must be positive!", tag="goods")
            return

        success, msg = self.engine.goods_service.sell(product, quantity)
        if not success:
            self.engine.messenger.warn(msg, tag="goods")
        self.refresh_all()

    def _handle_sell_from_lot(self, product: str, lot_ts: str, quantity: int):
        """Handle sell from a specific lot (partial or full)."""
        if quantity <= 0:
            self.engine.messenger.warn("Quantity must be positive!", tag="goods")
            return
        ok, msg = self.engine.goods_service.sell_from_lot(product, lot_ts, quantity)
        if not ok:
            self.engine.messenger.warn(msg, tag="goods")
        self.refresh_all()

    def _handle_asset_trade(self, msg: str):
        """Handle result message from asset buy/sell modals (refresh only)."""
        self.refresh_all()


    def action_cargo(self):
        """Open modal to extend cargo capacity by purchasing an extra slot."""
        try:
            modal = CargoExtendModal(self.engine, self._handle_extend_cargo)
            self.push_screen(modal)
        except Exception as e:
            self.engine.messenger.error(f"Error opening cargo modal: {e}", tag="system")

    def _handle_extend_cargo(self) -> bool:
        """Callback used by CargoExtendModal when Extend is pressed.
        Returns True to close the modal on success, False to keep it open on failure.
        """
        try:
            result = self.engine.cargo_service.extend_capacity()
        except Exception as e:
            self.engine.messenger.error(f"Error: {e}", tag="system")
            return False

        # Interpret tuple shapes per service contract
        if not result:
            self.engine.messenger.error("Unexpected response from engine.", tag="system")
            return False

        ok = bool(result[0])
        if ok:
            # (True, msg, new_capacity, next_cost)
            msg = result[1] if len(result) > 1 else "Cargo extended."
            self.engine.messenger.info(msg, tag="goods")
            self.refresh_all()
            return True
        else:
            # (False, msg, current_cost)
            msg = result[1] if len(result) > 1 else "Not enough cash to extend cargo."
            self.engine.messenger.warn(msg, tag="goods")
            self.refresh_all()
            return False

    def action_travel(self):
        """Travel to another city"""
        modal = TravelModal(CITIES, self.engine.state.current_city, self._handle_travel)
        self.push_screen(modal)

    def _handle_travel(self, city_index: int):
        """Handle travel to new city"""
        success, msg, events_list, dividend_modal = self.engine.travel_service.travel(city_index)

        if not success:
            self.engine.messenger.warn(msg, tag="travel")
            self.refresh_all()
            return

        # Log travel events to messenger
        for event_msg, event_type in events_list:
            if event_type == "gain":
                self.engine.messenger.warn(event_msg, tag="events")
            elif event_type == "loss":
                self.engine.messenger.error(event_msg, tag="events")
            else:  # neutral
                self.engine.messenger.info(event_msg, tag="events")

        # Refresh messenger panel to show all messages
        self.refresh_all()

        # Show dividend modal first (if any), then travel events
        if dividend_modal:
            self._show_dividend_modal(dividend_modal, events_list)
        elif events_list:
            self._show_travel_events(events_list)
        # If neither dividend nor events, refresh is already done above

    def _show_travel_events(self, events_list: list) -> None:
        """Show multiple travel events sequentially with blocking modals."""
        if not events_list:
            return

        self._pending_events = list(events_list)
        self._show_next_event()

    def _show_next_event(self) -> None:
        """Show the next event from pending events queue."""
        if not hasattr(self, '_pending_events') or not self._pending_events:
            self.refresh_all()
            return

        event_msg, event_type = self._pending_events.pop(0)

        # Map event type to title
        if event_type == "gain":
            title = "✨ Good News!"
        elif event_type == "loss":
            title = "⚠️ Bad News!"
        else:  # neutral
            title = "ℹ️ Market Update"

        modal = EventModal(title, event_msg, event_type, self._show_next_event)
        self.push_screen(modal)

    def _show_dividend_modal(self, dividend_msg: str, events_list: list = None) -> None:
        """Show dividend modal, then travel events if any."""
        def after_dividend():
            if events_list:
                self._show_travel_events(events_list)
            else:
                self.refresh_all()

        modal = EventModal("💰 Dividend Payout!", dividend_msg, "gain", after_dividend)
        self.push_screen(modal)

    def action_loan(self):
        """Take a loan"""
        # Show today's APR offer for new loans (existing loans keep their own APR)
        try:
            apr_offer = float(getattr(self.engine.bank_service, "loan_apr_today", 0.10))
        except Exception:
            apr_offer = 0.10
        apr_pct = f"{apr_offer*100:.2f}"
        try:
            _, _, max_new = self.engine.bank_service.compute_credit_limits()
        except Exception:
            max_new = 0
        if int(max_new) <= 0:
            # No capacity left: inform user and return
            self.engine.messenger.warn(
                "No credit capacity available. Repay loans or increase wealth to borrow more.",
                tag="bank",
            )
            self.refresh_all()
            return
        suggested = max(0, int(max_new))
        prompt = (
            "How much would you like to borrow?\n"
            f"(Max new loan by capacity: ${max_new:,} | Today's offer: {apr_pct}% APR)"
        )
        modal = InputModal(
            "🏦 Bank Loan",
            prompt,
            self._handle_loan,
            str(suggested),
        )
        self.push_screen(modal)

    def _handle_loan(self, value: str):
        """Handle loan request"""
        try:
            amount = int(value.strip())
        except ValueError:
            self.engine.messenger.warn("Invalid amount!", tag="bank")
            return

        success, msg = self.engine.bank_service.take_loan(amount)
        if not success:
            self.engine.messenger.warn(msg, tag="bank")
        self.refresh_all()

    def action_repay(self):
        """Repay loan. Opens a modal to select which loan to repay and amount."""
        # Filter active loans
        active_loans = [ln for ln in (self.engine.state.loans or []) if getattr(ln, "remaining", 0) > 0]
        if not active_loans or self.engine.state.cash <= 0:
            self.engine.messenger.warn("No repayable loans or no cash available!", tag="bank")
            return

        # Open new modal with loan selector and prefilled amount
        self.push_screen(LoanRepayModal(self.engine, self._handle_repay_selected))

    def _handle_repay_selected(self, loan_id: int, amount: int):
        """Handle loan repayment for a specific loan selected in modal."""
        try:
            amt = int(amount)
        except Exception:
            self.engine.messenger.warn("Invalid amount!", tag="bank")
            return
        ok, msg = self.engine.bank_service.repay_loan_for(int(loan_id), amt)
        if not ok:
            self.engine.messenger.warn(msg, tag="bank")
        self.refresh_all()

    # --- Bank actions ---
    def action_bank_deposit(self):
        """Open modal to deposit cash to bank."""
        cash = self.engine.state.cash
        if cash <= 0:
            self.engine.messenger.warn("No cash to deposit!", tag="bank")
            return
        modal = InputModal(
            "🏦 Deposit to Bank",
            f"Cash available: ${cash:,}\nHow much to deposit?",
            self._handle_bank_deposit,
            default_value=str(cash),
            confirm_variant="success",
            cancel_variant="error",
        )
        self.push_screen(modal)

    def _handle_bank_deposit(self, value: str):
        try:
            amount = int(value.strip())
        except ValueError:
            self.engine.messenger.warn("Invalid amount!", tag="bank")
            return
        ok, msg = self.engine.bank_service.deposit_to_bank(amount)
        if not ok:
            self.engine.messenger.warn(msg, tag="bank")
        self.refresh_all()

    def action_bank_withdraw(self):
        """Open modal to withdraw cash from bank."""
        bal = self.engine.state.bank.balance
        if bal <= 0:
            self.engine.messenger.warn("No funds in bank to withdraw!", tag="bank")
            return
        modal = InputModal(
            "🏦 Withdraw from Bank",
            f"Bank balance: ${bal:,}\nHow much to withdraw?",
            self._handle_bank_withdraw,
            default_value=str(bal),
            confirm_variant="success",
            cancel_variant="error",
        )
        self.push_screen(modal)

    def _handle_bank_withdraw(self, value: str):
        try:
            amount = int(value.strip())
        except ValueError:
            self.engine.messenger.warn("Invalid amount!", tag="bank")
            return
        ok, msg = self.engine.bank_service.withdraw_from_bank(amount)
        if not ok:
            self.engine.messenger.warn(msg, tag="bank")
        self.refresh_all()

    def action_help(self):
        """Show game instructions"""
        modal = HelpModal()
        self.push_screen(modal)

    def action_about(self):
        """Show About modal with app info"""
        self.push_screen(AboutModal())

    def action_splash(self):
        """Show Splash modal on demand (F9)."""
        try:
            self.push_screen(SplashModal())
        except Exception as e:
            try:
                self.engine.messenger.error(f"Failed to open splash: {e}", tag="system")
                self.refresh_all()
            except Exception:
                pass

    def action_save(self):
        """Ask for confirmation, then save current game to disk."""
        def _confirm_save():
            try:
                msgs = self.engine.messenger.get_entries()
                ok, msg = self.engine.savegame_service.save(msgs)
                if ok:
                    self.engine.messenger.debug("Game saved.", tag="system")
                else:
                    self.engine.messenger.warn(msg, tag="system")
            except Exception as e:
                self.engine.messenger.error(f"Save failed: {e}", tag="system")
            finally:
                self.refresh_all()

        confirm = ConfirmModal(
            "Save Game",
            "Do you want to save your progress?",
            on_confirm=_confirm_save,
            confirm_label="Yes",
            cancel_label="No",
        )
        self.push_screen(confirm)

    def action_load(self):
        """Load saved game from disk."""
        if not self.engine.savegame_service.is_save_present():
            self.engine.messenger.warn("No save file found!", tag="system")
            return

        def _confirm_load():
            try:
                data = self.engine.savegame_service.load()
                if data and self.engine.savegame_service.apply(data):
                    self.engine.messenger.debug("Loaded savegame.", tag="system")
                    self.refresh_all()
                else:
                    self.engine.messenger.warn("Failed to load save file.", tag="system")
            except Exception as e:
                self.engine.messenger.error(f"Load failed: {e}", tag="system")

        confirm = ConfirmModal(
            "Load Game",
            "Load saved game? Current progress will be lost if not saved.",
            on_confirm=_confirm_load,
        )
        self.push_screen(confirm)

    def action_new_game(self):
        """Ask for confirmation, then show difficulty selection, then start new game."""
        def _show_difficulty_modal():
            """Show difficulty selection modal after confirmation."""
            def _start_new_game(difficulty_name: str):
                """Start new game with selected difficulty."""
                try:
                    # Delete save file if exists
                    self.engine.savegame_service.delete_save()
                except Exception:
                    pass
                # Reset engine state safely via engine helper with selected difficulty
                try:
                    self.engine.reset_state(difficulty_name)
                    self.engine.goods_service.generate_prices()
                    self.engine.investments_service.generate_asset_prices()
                except Exception:
                    # Fallback to legacy behavior if helper not present
                    self.engine.state = GameState()
                    self.engine.goods_service.generate_prices()
                    self.engine.investments_service.generate_asset_prices()
                # Reset messages
                self.engine.messenger.clear()
                self.engine.messenger.debug(f"New game started with {difficulty_name} difficulty.", tag="system")
                self.refresh_all()

            from merchant_tycoon.ui.general.modals import NewGameModal
            modal = NewGameModal(self.engine.difficulty_repo, on_confirm=_start_new_game)
            self.push_screen(modal)

        confirm = ConfirmModal(
            "Start New Game",
            "Start a new game? This will delete the current save.",
            on_confirm=_show_difficulty_modal,
        )
        self.push_screen(confirm)

    def action_quit(self):
        """Show quit modal with two explicit options: Save&Quit or Just quit!"""
        def _save_and_quit():
            # Save game, then exit regardless of save outcome
            try:
                msgs = self.engine.messenger.get_entries()
                ok, msg = self.engine.savegame_service.save(msgs)
                if ok:
                    self.engine.messenger.debug("Game saved.", tag="system")
                else:
                    self.engine.messenger.warn(msg, tag="system")
            except Exception as e:
                self.engine.messenger.error(f"Save failed: {e}", tag="system")
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

    def action_noop(self):
        """No-op action used to swallow global shortcuts like Ctrl+K/Ctrl+P."""
        pass
