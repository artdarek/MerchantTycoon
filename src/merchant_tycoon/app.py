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
from .models import CITIES
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
)
from .savegame import (
    is_save_present,
    load_game,
    apply_loaded_game,
    save_game as save_game_to_disk,
    delete_save as delete_save_from_disk,
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
    CSS_PATH = "style.tcss"

    # Global bindings (always active, shown in top bar)
    BINDINGS = [
        Binding("q", "quit", "Quit", show=False),
        Binding("h", "help", "Help", show=False),
        Binding("a", "save", "Save", show=False),
        Binding("o", "load", "Load", show=False),
        Binding("n", "new_game", "New Game", show=False),
    ]

    # Contextual bindings for Goods tab
    GOODS_BINDINGS = [
        Binding("t", "travel", "Travel"),
        Binding("b", "buy", "Buy"),
        Binding("s", "sell", "Sell"),
        Binding("i", "goods_transactions", "Transactions"),
        Binding("l", "loan", "Loan"),
        Binding("r", "repay", "Repay"),
    ]

    # Contextual bindings for Investments tab
    INVESTMENTS_BINDINGS = [
        Binding("b", "buy", "Buy"),
        Binding("s", "sell", "Sell"),
        Binding("i", "investment_transactions", "Transactions"),
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

        # Set initial contextual bindings for Goods tab
        self._update_contextual_bindings("goods-tab")

        # Auto-load savegame if present
        try:
            if is_save_present():
                data = load_game()
                if data and apply_loaded_game(self.engine, data):
                    msgs = data.get("messages") or []
                    if self.message_log and msgs:
                        self.message_log.set_messages(msgs)
                    self.game_log("Loaded savegame.")
        except Exception:
            # Ignore autoload errors and start a fresh game
            pass

        self.refresh_all()

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        """Handle tab changes to update contextual bindings"""
        self._update_contextual_bindings(event.pane.id)

    def _update_contextual_bindings(self, tab_id: str) -> None:
        """Update footer bindings based on active tab"""
        self.current_tab = tab_id

        # Remove all contextual bindings first
        contextual_keys = ["b", "s", "t", "l", "r", "i"]
        for key in contextual_keys:
            try:
                self.unbind(key)
            except Exception:
                pass

        # Add new contextual bindings based on tab
        if tab_id == "investments-tab":
            bindings_to_add = self.INVESTMENTS_BINDINGS
        else:  # goods-tab
            bindings_to_add = self.GOODS_BINDINGS

        # Add each binding by extracting properties from Binding object
        for binding in bindings_to_add:
            self.bind(
                keys=binding.key,
                action=binding.action,
                description=binding.description,
                show=binding.show
            )

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

    def game_log(self, msg: str):
        # Prefix each log entry with timestamp and the in-game day number
        day = self.engine.state.day
        ts = datetime.now().strftime("%H:%M:%S")
        if self.message_log:
            self.message_log.add_message(f"[{ts}] Day {day}: {msg}")

    def action_buy(self):
        """Context-aware Buy: goods or assets depending on active tab"""
        try:
            tabbed = self.query_one(TabbedContent)
            active = getattr(tabbed, "active", None)
        except Exception:
            active = None

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
        """Context-aware Sell: goods or assets depending on active tab"""
        try:
            tabbed = self.query_one(TabbedContent)
            active = getattr(tabbed, "active", None)
        except Exception:
            active = None

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
        modal = InputModal(
            "🏦 Bank Loan",
            "How much would you like to borrow?\n(Max: $10,000 | Interest: 10% per day)",
            self._handle_loan
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
        """Repay loan"""
        if self.engine.state.debt <= 0:
            self.game_log("No debt to repay!")
            return

        modal = InputModal(
            "💳 Repay Loan",
            f"Current debt: ${self.engine.state.debt:,}\nCash available: ${self.engine.state.cash:,}\nHow much to repay?",
            self._handle_repay
        )
        self.push_screen(modal)

    def _handle_repay(self, value: str):
        """Handle loan repayment"""
        try:
            amount = int(value.strip())
        except ValueError:
            self.game_log("Invalid amount!")
            return

        success, msg = self.engine.repay_loan(amount)
        self.game_log(msg)
        self.refresh_all()

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

    def action_help(self):
        """Show game instructions"""
        modal = HelpModal()
        self.push_screen(modal)

    def action_save(self):
        """Save current game to disk (single slot)."""
        try:
            msgs = self.message_log.messages if self.message_log else []
            ok, msg = save_game_to_disk(self.engine, msgs)
            if ok:
                self.game_log("Game saved.")
            else:
                self.game_log(msg)
        except Exception as e:
            self.game_log(f"Save failed: {e}")

    def action_load(self):
        """Load saved game from disk."""
        if not is_save_present():
            self.game_log("No save file found!")
            return

        def _confirm_load():
            try:
                data = load_game()
                if data and apply_loaded_game(self.engine, data):
                    msgs = data.get("messages") or []
                    if self.message_log and msgs:
                        self.message_log.set_messages(msgs)
                    self.game_log("Game loaded successfully.")
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
                delete_save_from_disk()
            except Exception:
                pass
            # Reset engine state in-place (keep object for UI references)
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
        """Quit the game application."""
        self.exit()


def main():
    """Entry point for the game"""
    app = MerchantTycoon()
    app.run()


if __name__ == "__main__":
    main()
