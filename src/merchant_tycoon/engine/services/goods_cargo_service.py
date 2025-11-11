"""Service for handling cargo capacity management and extensions.

This service is responsible for all cargo-related operations including:
- Tracking used/free cargo slots (accounting for product sizes)
- Validating cargo capacity before purchases
- Extending cargo capacity (with configurable pricing strategies)
- Calculating extension costs

Separating cargo logic from goods trading logic improves modularity and
prepares for future extensions like multiple cargo vehicles or dynamic capacity.
"""
from typing import TYPE_CHECKING, Optional

from merchant_tycoon.config import SETTINGS

if TYPE_CHECKING:
    from merchant_tycoon.engine.game_state import GameState
    from merchant_tycoon.repositories import GoodsRepository


class GoodsCargoService:
    """Service for managing cargo capacity, usage, and extensions.

    This service handles all operations related to inventory space management,
    including capacity calculations (accounting for product sizes), extension
    purchases, and space validation.

    Responsibilities:
        - Calculate used/free cargo slots based on product sizes
        - Validate space availability before purchases
        - Handle cargo capacity extensions with configurable pricing
        - Provide cargo-related state queries

    Attributes:
        state: Reference to the game state for accessing inventory and capacity
        goods_repo: Repository for product lookups

    Examples:
        >>> cargo_service = GoodsCargoService(game_state, goods_repo)
        >>> used = cargo_service.get_used_slots()
        >>> free = cargo_service.get_free_slots()
        >>> if cargo_service.has_space_for_good("TV", 10):
        ...     # Purchase 10 TVs (30 slots)
        ...     pass
        >>> success, msg = cargo_service.extend_capacity()
    """

    def __init__(self, state: "GameState", goods_repository: "GoodsRepository"):
        """Initialize cargo service with game state reference.

        Args:
            state: Game state containing inventory and capacity information
            goods_repository: Repository for product lookups
        """
        self.state = state
        self.goods_repo = goods_repository

    def _get_product_size(self, good_name: str) -> int:
        """Get the cargo size of a product by name.

        Args:
            good_name: Name of the product to look up

        Returns:
            Size in cargo slots (defaults to 1 if product not found)
        """
        good = self.goods_repo.get_by_name(good_name)
        if good:
            return getattr(good, "size", 1)
        return 1  # Default size if product not found

    def get_used_slots(self) -> int:
        """Get the number of cargo slots currently in use (accounting for product sizes).

        Calculates total space used by multiplying each product's quantity by its size.

        Returns:
            Total cargo slots occupied by all inventory items

        Examples:
            >>> cargo_service.get_used_slots()
            45  # e.g., 10x TV (3 slots each) + 5x Phone (2 slots each) + 5x Pendrive (1 slot each) = 30 + 10 + 5 = 45
        """
        total_space = 0
        for good_name, quantity in self.state.inventory.items():
            size = self._get_product_size(good_name)
            total_space += quantity * size
        return total_space

    def get_max_slots(self) -> int:
        """Get the maximum cargo capacity (total slots available).

        Returns:
            Maximum number of items that can be carried

        Examples:
            >>> cargo_service.get_max_slots()
            50  # 50 total slots
        """
        return int(getattr(self.state, "max_inventory", SETTINGS.cargo.base_capacity))

    def get_free_slots(self) -> int:
        """Get the number of free cargo slots available.

        Returns:
            Number of empty slots (max_slots - used_slots)

        Examples:
            >>> cargo_service.get_free_slots()
            25  # 25 slots free (50 max - 25 used)
        """
        return self.get_max_slots() - self.get_used_slots()

    def has_space_for_good(self, good_name: str, quantity: int) -> bool:
        """Check if cargo has space for the specified quantity of a product.

        Accounts for the product's size when calculating required space.

        Args:
            good_name: Name of the product to check
            quantity: Number of units to check space for

        Returns:
            True if there's enough free space, False otherwise

        Examples:
            >>> cargo_service.has_space_for_good("TV", 10)
            True  # Can carry 10 TVs (30 slots total)
            >>> cargo_service.has_space_for_good("Ferrari", 3)
            False  # Cannot carry 3 Ferraris (75 slots needed, not enough space)
        """
        product_size = self._get_product_size(good_name)
        required_space = quantity * product_size
        return self.get_free_slots() >= required_space

    def has_space_for(self, quantity: int) -> bool:
        """Check if cargo has space for the specified number of slots.

        Note: This method assumes each item takes 1 slot. For accurate
        size-based checks, use has_space_for_good() instead.

        Args:
            quantity: Number of slots to check space for

        Returns:
            True if there's enough free space, False otherwise

        Examples:
            >>> cargo_service.has_space_for(10)
            True  # Can fit 10 more slots
            >>> cargo_service.has_space_for(50)
            False  # Not enough space
        """
        return self.get_free_slots() >= quantity

    def get_extend_cost(self) -> int:
        """Calculate the cost to extend cargo capacity by one bundle.

        The cost is calculated based on the configured pricing mode:
        - Exponential: base_cost × (factor ** bundles_purchased)
        - Linear: base_cost + (increment × bundles_purchased)

        Returns:
            Cost in dollars to purchase the next cargo extension

        Examples:
            >>> cargo_service.get_extend_cost()
            50  # $50 for next extension

        Notes:
            - A "bundle" is a group of slots defined by extend_step setting
            - Bundles purchased = (current_capacity - base_capacity) / extend_step
            - Pricing strategy configured via SETTINGS.cargo.extend_pricing_mode
        """
        return self._calculate_extend_cost()

    def extend_capacity(self) -> tuple:
        """Attempt to extend cargo capacity by purchasing additional slots.

        Extends capacity by the configured step size (default 1 slot) and deducts
        the current extension cost from player's cash. Pricing follows the
        configured strategy (linear or exponential).

        Returns:
            Tuple with one of the following formats:
            - On insufficient cash: (False, error_message, current_cost)
            - On success: (True, success_message, new_capacity, next_cost)

        Examples:
            >>> success, msg, *args = cargo_service.extend_capacity()
            >>> if success:
            ...     new_capacity, next_cost = args
            ...     print(f"Extended to {new_capacity}, next costs ${next_cost}")
            ... else:
            ...     current_cost = args[0]
            ...     print(f"Failed: {msg} (need ${current_cost})")

        Notes:
            - Deducts cost from state.cash on success
            - Increases state.max_inventory by extend_step
            - Returns updated capacity and next extension cost
            - Pricing strategy: exponential or linear (configurable)
        """
        # Get current capacity and configuration
        current_capacity = self.get_max_slots()
        step = max(1, int(SETTINGS.cargo.extend_step))
        current_cost = self.get_extend_cost()

        # Validate player has enough cash
        if self.state.cash < current_cost:
            return (
                False,
                f"Not enough cash! Need ${current_cost:,}, have ${self.state.cash:,}",
                current_cost
            )

        # Deduct cost and extend capacity
        self.state.cash -= current_cost
        self.state.max_inventory = current_capacity + step

        # Calculate next extension cost
        over_base = max(0, self.state.max_inventory - SETTINGS.cargo.base_capacity)
        bundles_purchased = over_base // step
        next_cost = self._calculate_cost_for_bundle(bundles_purchased)

        return (
            True,
            f"Cargo extended by +{step} slots to {self.state.max_inventory} (-${current_cost:,})",
            self.state.max_inventory,
            next_cost
        )

    def _calculate_extend_cost(self) -> int:
        """Internal method to calculate current extension cost.

        Returns:
            Cost in dollars for the next cargo extension
        """
        current_capacity = self.get_max_slots()
        step = max(1, int(SETTINGS.cargo.extend_step))
        over_base = max(0, current_capacity - SETTINGS.cargo.base_capacity)
        bundles_purchased = over_base // step

        return self._calculate_cost_for_bundle(bundles_purchased)

    def _calculate_cost_for_bundle(self, bundle_number: int) -> int:
        """Calculate cost for a specific bundle number.

        Args:
            bundle_number: The bundle index to calculate cost for (0-indexed)

        Returns:
            Cost in dollars for the specified bundle
        """
        mode = str(getattr(SETTINGS.cargo, "extend_pricing_mode", "linear")).lower()
        base_cost = int(SETTINGS.cargo.extend_base_cost)

        if mode == "exponential":
            # Exponential pricing: base_cost × (factor ** bundle_number)
            factor = float(getattr(SETTINGS.cargo, "extend_cost_factor", 2.0))
            return int(base_cost * (factor ** bundle_number))
        else:
            # Linear pricing: base_cost + (increment × bundle_number)
            factor = float(getattr(SETTINGS.cargo, "extend_cost_factor", 1.0))
            increment = base_cost * factor
            return int(base_cost + increment * bundle_number)
