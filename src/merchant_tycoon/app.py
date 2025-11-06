#!/usr/bin/env python3
"""
Merchant Tycoon - A terminal-based trading game
Buy low, sell high, travel between cities, manage loans, survive random events!

This module hosts the main application class `MerchantTycoon` and the `main()`
entry point. It was extracted from `game.py` as part of refactoring Stage 4.
"""

from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Header, Footer, TabbedContent, TabPane
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
)
from .ui.trade_panels import (
    TradeActionsPanel,
    GoodsTradeActionsPanel,
)
from .ui.modals import (
    InputModal,
    CitySelectModal,
    BuyModal,
    SellModal,
    InventoryDetailsModal,
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


class MerchantTycoon(App):
    """Main game application"""

    # Load styles from external file created in Stage 5
    CSS_PATH = "style.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("b", "buy", "Buy"),
        Binding("s", "sell", "Sell"),
        Binding("t", "travel", "Travel"),
        Binding("l", "loan", "Loan"),
        Binding("r", "repay", "Repay"),
        Binding("i", "details", "Inventory"),
        Binding("h", "help", "Help"),
        Binding("a", "save", "Save"),
        Binding("n", "new_game", "New Game"),
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

    def compose(self) -> ComposeResult:
        yield Header()
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

    def action_details(self):
        """Show detailed inventory with purchase lots"""
        if not self.engine.state.inventory:
            self.game_log("No goods in inventory!")
            return

        modal = InventoryDetailsModal(self.engine)
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


def main():
    """Entry point for the game"""
    app = MerchantTycoon()
    app.run()


if __name__ == "__main__":
    main()
