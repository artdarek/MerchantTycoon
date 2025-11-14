from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from merchant_tycoon.engine.game_state import GameState
    from merchant_tycoon.engine.services.clock_service import ClockService
    from merchant_tycoon.engine.services.messenger_service import MessengerService


class WalletService:
    """Service for managing player's cash/wallet operations.

    Centralizes all cash-related logic including:
    - Earning cash (income, refunds, dividends, etc.)
    - Spending cash (purchases, fees, travel, etc.)
    - Balance queries and validation

    This ensures consistent validation and balance updates across all gameplay systems.
    Services using WalletService handle their own business-specific messaging.
    """

    def __init__(
        self,
        state: "GameState",
        clock_service: "ClockService",
        messenger: Optional["MessengerService"] = None
    ):
        """Initialize WalletService.

        Args:
            state: Game state containing cash balance
            clock_service: Clock service for timestamps
            messenger: Optional messenger service for debug logging
        """
        self.state = state
        self.clock = clock_service
        self.messenger = messenger

    def get_balance(self) -> int:
        """Get current cash balance.

        Returns:
            Current cash amount
        """
        return self.state.cash

    def set_balance(self, value: int) -> None:
        """Set cash balance directly (use with caution).

        Args:
            value: New cash balance
        """
        self.state.cash = max(0, int(value))

    def can_afford(self, amount: int) -> bool:
        """Check if player can afford the given amount.

        Args:
            amount: Amount to check

        Returns:
            True if player has enough cash
        """
        return self.state.cash >= amount

    def earn(self, amount: int) -> None:
        """Add cash to wallet.

        Args:
            amount: Amount to add (must be positive)
        """
        if amount <= 0:
            return

        amount = int(amount)
        self.state.cash += amount

    def spend(self, amount: int) -> bool:
        """Deduct cash from wallet with validation.

        Args:
            amount: Amount to deduct (must be positive)

        Returns:
            True if successful, False if insufficient funds
        """
        if amount <= 0:
            return True

        amount = int(amount)

        # Validate sufficient funds
        if not self.can_afford(amount):
            return False

        # Deduct cash
        self.state.cash -= amount

        return True
