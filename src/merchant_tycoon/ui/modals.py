from typing import List

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Label, Button, Input, Select, OptionList
from textual.widgets.option_list import Option
from textual.screen import ModalScreen

from ..engine import GameEngine
from ..models import City, GOODS, STOCKS, COMMODITIES


class InputModal(ModalScreen):
    """Generic input modal"""

    def __init__(self, title: str, prompt: str, callback):
        super().__init__()
        self.modal_title = title
        self.modal_prompt = prompt
        self.callback = callback

    def compose(self) -> ComposeResult:
        with Container(id="input-modal"):
            yield Label(self.modal_title, id="modal-title")
            yield Label(self.modal_prompt)
            yield Input(placeholder="Enter value...", id="modal-input")
            with Horizontal(id="modal-buttons"):
                yield Button("Confirm", variant="primary", id="confirm-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            input_widget = self.query_one("#modal-input", Input)
            value = input_widget.value.strip()
            self.dismiss()
            if value:
                self.callback(value)
        else:
            self.dismiss()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        self.dismiss()
        if value:
            self.callback(value)


class CitySelectModal(ModalScreen):
    """City selection modal"""

    def __init__(self, cities: List[City], current_city: int, callback):
        super().__init__()
        self.cities = cities
        self.current_city = current_city
        self.callback = callback

    def compose(self) -> ComposeResult:
        with Container(id="city-modal"):
            yield Label("🗺️  Select Destination", id="modal-title")
            options = []
            for i, city in enumerate(self.cities):
                if i == self.current_city:
                    options.append(Option(f"{city.name} (current)", id=str(i), disabled=True))
                else:
                    options.append(Option(city.name, id=str(i)))
            yield OptionList(*options, id="city-list")
            yield Button("Cancel", variant="default", id="cancel-btn")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        city_index = int(event.option.id)
        self.dismiss()
        self.callback(city_index)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()


class BuyModal(ModalScreen):
    """Modal for buying goods with product selector and quantity input"""

    def __init__(self, engine: GameEngine, callback):
        super().__init__()
        self.engine = engine
        self.callback = callback

    def compose(self) -> ComposeResult:
        with Container(id="buy-modal"):
            yield Label("🛒 Buy Goods", id="modal-title")

            # Create select options with prices and max quantity
            options = []
            available_space = self.engine.state.max_inventory - self.engine.state.get_inventory_count()

            for good in GOODS:
                price = self.engine.prices[good.name]
                # Calculate max affordable based on cash
                max_affordable = self.engine.state.cash // price if price > 0 else 0
                # Calculate actual max (limited by inventory space)
                max_buyable = min(max_affordable, available_space)

                options.append((
                    f"{good.name} - ${price:,} (max: {max_buyable})",
                    good.name
                ))

            yield Label("Select product:")
            yield Select(options, prompt="Choose a product...", id="product-select")
            yield Label("Enter quantity:")
            yield Input(placeholder="Quantity...", type="integer", id="quantity-input")

            with Horizontal(id="modal-buttons"):
                yield Button("Buy", variant="primary", id="confirm-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            select_widget = self.query_one("#product-select", Select)
            input_widget = self.query_one("#quantity-input", Input)

            product = select_widget.value
            quantity_str = input_widget.value.strip()

            self.dismiss()

            if product and quantity_str:
                try:
                    quantity = int(quantity_str)
                    self.callback(product, quantity)
                except ValueError:
                    pass
        else:
            self.dismiss()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # Trigger buy on Enter key
        select_widget = self.query_one("#product-select", Select)
        product = select_widget.value

        try:
            quantity = int(event.value.strip())
            self.dismiss()
            if product:
                self.callback(product, quantity)
        except ValueError:
            pass


class SellModal(ModalScreen):
    """Modal for selling goods with product selector and quantity input"""

    def __init__(self, engine: GameEngine, callback):
        super().__init__()
        self.engine = engine
        self.callback = callback

    def compose(self) -> ComposeResult:
        with Container(id="sell-modal"):
            yield Label("💵 Sell Goods", id="modal-title")

            # Create select options with inventory and prices
            options = []
            for good_name, quantity in self.engine.state.inventory.items():
                price = self.engine.prices[good_name]
                total_value = quantity * price
                options.append((
                    f"{good_name} - ${price:,}/unit (have: {quantity}, worth ${total_value:,})",
                    good_name
                ))

            yield Label("Select product to sell:")
            yield Select(options, prompt="Choose a product...", id="product-select")
            yield Label("Enter quantity to sell:")
            yield Input(placeholder="Quantity...", type="integer", id="quantity-input")

            with Horizontal(id="modal-buttons"):
                yield Button("Sell", variant="primary", id="confirm-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            select_widget = self.query_one("#product-select", Select)
            input_widget = self.query_one("#quantity-input", Input)

            product = select_widget.value
            quantity_str = input_widget.value.strip()

            self.dismiss()

            if product and quantity_str:
                try:
                    quantity = int(quantity_str)
                    self.callback(product, quantity)
                except ValueError:
                    pass
        else:
            self.dismiss()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # Trigger sell on Enter key
        select_widget = self.query_one("#product-select", Select)
        product = select_widget.value

        try:
            quantity = int(event.value.strip())
            self.dismiss()
            if product:
                self.callback(product, quantity)
        except ValueError:
            pass


class InventoryDetailsModal(ModalScreen):
    """Modal showing detailed inventory with purchase lots and profit/loss"""

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
    ]

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        with Vertical(id="inventory-details-modal"):
            yield Label("📊 INVENTORY DETAILS", id="modal-title")
            yield Label("Use ↑↓ or mouse wheel to scroll", id="details-instructions")
            yield ScrollableContainer(id="details-content")
            yield Button("Close (ESC)", variant="primary", id="close-btn")

    def on_mount(self) -> None:
        self._update_details()

    def _update_details(self):
        try:
            container = self.query_one("#details-content", ScrollableContainer)
            container.remove_children()

            if not self.engine.state.inventory:
                container.mount(Label("No goods in inventory"))
                return

            for good_name in sorted(self.engine.state.inventory.keys()):
                total_qty = self.engine.state.inventory.get(good_name, 0)
                current_price = self.engine.prices.get(good_name, 0)
                lots = self.engine.state.get_lots_for_good(good_name)

                # Header for this good
                container.mount(Label(""))  # Empty line
                container.mount(Label(f" {good_name} ", classes="section-header"))
                container.mount(Label(""))
                container.mount(Label(f"  Total owned: {total_qty} units"))
                container.mount(Label(f"  Market price: ${current_price:,}"))
                container.mount(Label(""))

                if not lots:
                    container.mount(Label("  (No purchase history available)"))
                    container.mount(Label(""))
                else:
                    # Calculate total profit/loss
                    total_invested = sum(lot.quantity * lot.purchase_price for lot in lots)
                    total_current_value = total_qty * current_price
                    total_profit = total_current_value - total_invested
                    total_profit_pct = (total_profit / total_invested * 100) if total_invested > 0 else 0

                    profit_symbol = "📈" if total_profit > 0 else "📉" if total_profit < 0 else "➖"
                    container.mount(Label(
                        f"  {profit_symbol} Total P/L: ${total_profit:+,} ({total_profit_pct:+.1f}%)"
                    ))
                    container.mount(Label(""))
                    container.mount(Label("  Purchase History (FIFO order):"))

                    for i, lot in enumerate(lots, 1):
                        profit_per_unit = current_price - lot.purchase_price
                        lot_profit = profit_per_unit * lot.quantity
                        lot_profit_pct = (profit_per_unit / lot.purchase_price * 100) if lot.purchase_price > 0 else 0

                        profit_symbol = "📈" if profit_per_unit > 0 else "📉" if profit_per_unit < 0 else "➖"

                        container.mount(Label(""))
                        container.mount(Label(
                            f"    [{i}] {lot.quantity}x @ ${lot.purchase_price:,}/unit = ${lot.quantity * lot.purchase_price:,}",
                            classes="lot-info"
                        ))
                        container.mount(Label(
                            f"        Bought: Day {lot.day} in {lot.city}",
                            classes="lot-info"
                        ))
                        container.mount(Label(
                            f"        {profit_symbol} If sold now: ${profit_per_unit:+,}/unit "
                            f"({lot_profit_pct:+.1f}%) = ${lot_profit:+,}",
                            classes="profit-info"
                        ))
                    container.mount(Label(""))
        except Exception as e:
            # If there's any error, show a simple error message
            try:
                container = self.query_one("#details-content", ScrollableContainer)
                container.remove_children()
                container.mount(Label(f"Error loading details: {str(e)}"))
            except:  # noqa: E722
                pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-btn":
            self.dismiss()

    def action_dismiss_modal(self) -> None:
        """Close the modal when ESC is pressed"""
        self.dismiss()


class BuyAssetModal(ModalScreen):
    """Modal for buying stocks/commodities"""

    def __init__(self, engine: GameEngine, callback):
        super().__init__()
        self.engine = engine
        self.callback = callback

    def compose(self) -> ComposeResult:
        with Container(id="buy-modal"):
            yield Label("💰 Buy Assets", id="modal-title")

            options = []
            all_assets = STOCKS + COMMODITIES
            for asset in all_assets:
                price = self.engine.asset_prices[asset.symbol]
                max_affordable = self.engine.state.cash // price if price > 0 else 0
                asset_type_icon = "📊" if asset.asset_type == "stock" else "🌾"

                options.append((
                    f"{asset_type_icon} {asset.symbol} - {asset.name} @ ${price:,} (max: {max_affordable})",
                    asset.symbol
                ))

            yield Label("Select asset:")
            yield Select(options, prompt="Choose an asset...", id="asset-select")
            yield Label("Enter quantity:")
            yield Input(placeholder="Quantity...", type="integer", id="quantity-input")

            with Horizontal(id="modal-buttons"):
                yield Button("Buy", variant="primary", id="confirm-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            select_widget = self.query_one("#asset-select", Select)
            input_widget = self.query_one("#quantity-input", Input)

            symbol = select_widget.value
            quantity_str = input_widget.value.strip()

            self.dismiss()

            if symbol and quantity_str:
                try:
                    quantity = int(quantity_str)
                    success, msg = self.engine.buy_asset(symbol, quantity)
                    self.callback(msg)
                except ValueError:
                    pass
        else:
            self.dismiss()


class SellAssetModal(ModalScreen):
    """Modal for selling stocks/commodities"""

    def __init__(self, engine: GameEngine, callback):
        super().__init__()
        self.engine = engine
        self.callback = callback

    def compose(self) -> ComposeResult:
        with Container(id="sell-modal"):
            yield Label("💵 Sell Assets", id="modal-title")

            options = []
            for symbol, quantity in self.engine.state.portfolio.items():
                price = self.engine.asset_prices[symbol]
                total_value = quantity * price

                # Find asset info
                all_assets = STOCKS + COMMODITIES
                asset = next((a for a in all_assets if a.symbol == symbol), None)
                asset_type_icon = "📊" if asset and asset.asset_type == "stock" else "🌾"
                asset_name = asset.name if asset else symbol

                options.append((
                    f"{asset_type_icon} {symbol} - {asset_name} @ ${price:,}/unit (have: {quantity}, worth ${total_value:,})",
                    symbol
                ))

            yield Label("Select asset to sell:")
            yield Select(options, prompt="Choose an asset...", id="asset-select")
            yield Label("Enter quantity to sell:")
            yield Input(placeholder="Quantity...", type="integer", id="quantity-input")

            with Horizontal(id="modal-buttons"):
                yield Button("Sell", variant="primary", id="confirm-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            select_widget = self.query_one("#asset-select", Select)
            input_widget = self.query_one("#quantity-input", Input)

            symbol = select_widget.value
            quantity_str = input_widget.value.strip()

            self.dismiss()

            if symbol and quantity_str:
                try:
                    quantity = int(quantity_str)
                    success, msg = self.engine.sell_asset(symbol, quantity)
                    self.callback(msg)
                except ValueError:
                    pass
        else:
            self.dismiss()


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
                yield Label("  • 10% interest charged each day")
                yield Label("  • Repay (R) debt as soon as possible")
                yield Label("")

                yield Label(" 📦 INVENTORY ", classes="section-header")
                yield Label("  • Inventory (I) to see detailed purchase history")
                yield Label("  • Limited space: 50 units maximum")
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

            yield Button("Close (ESC)", variant="primary", id="close-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-btn":
            self.dismiss()

    def action_dismiss_modal(self) -> None:
        """Close the modal when ESC is pressed"""
        self.dismiss()


class AlertModal(ModalScreen):
    """Modal for displaying alerts/notifications"""

    BINDINGS = [
        ("escape", "dismiss_modal", "Close"),
        ("enter", "dismiss_modal", "Close"),
    ]

    def __init__(self, title: str, message: str, is_positive: bool = False):
        super().__init__()
        self.alert_title = title
        self.alert_message = message
        self.is_positive = is_positive

    def compose(self) -> ComposeResult:
        modal_id = "alert-modal-positive" if self.is_positive else "alert-modal-negative"
        with Container(id=modal_id):
            yield Label(self.alert_title, id="modal-title")
            yield Label(self.alert_message, id="alert-message")
            yield Button("OK (ENTER)", variant="primary", id="ok-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok-btn":
            self.dismiss()

    def action_dismiss_modal(self) -> None:
        """Close the modal when ESC or ENTER is pressed"""
        self.dismiss()


class ConfirmModal(ModalScreen):
    """Simple confirmation modal with Yes/No buttons."""

    BINDINGS = [
        ("enter", "confirm", "Yes"),
        ("escape", "cancel", "No"),
    ]

    def __init__(self, title: str, message: str, on_confirm, on_cancel=None):
        super().__init__()
        self._title = title
        self._message = message
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel

    def compose(self) -> ComposeResult:
        with Container(id="confirm-modal"):
            yield Label(self._title, id="modal-title")
            yield Label(self._message)
            with Horizontal(id="modal-buttons"):
                yield Button("Yes", id="yes-btn", variant="primary")
                yield Button("No", id="no-btn", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes-btn":
            self.action_confirm()
        elif event.button.id == "no-btn":
            self.action_cancel()

    def action_confirm(self) -> None:
        try:
            if callable(self._on_confirm):
                self._on_confirm()
        finally:
            self.dismiss()

    def action_cancel(self) -> None:
        try:
            if callable(self._on_cancel):
                self._on_cancel()
        finally:
            self.dismiss()
