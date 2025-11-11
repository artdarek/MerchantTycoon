"""Repository for accessing and querying goods (tradable products).

This repository provides a clean, read-only interface to the GOODS domain constant,
encapsulating all lookup and filtering logic for tradable products in the game.
"""
from typing import List, Optional

from merchant_tycoon.domain.model.good import Good
from merchant_tycoon.domain.goods import GOODS


class GoodsRepository:
    """Repository for querying tradable goods/products.

    Provides methods for retrieving goods by various criteria without directly
    exposing the underlying GOODS constant to services and UI components.

    Examples:
        >>> repo = GoodsRepository()
        >>> all_goods = repo.get_all()
        >>> tv = repo.get_by_name("TV")
        >>> electronics = repo.get_by_category("electronics")
        >>> luxury_items = repo.get_by_type("luxury")
    """

    def __init__(self, goods: Optional[List[Good]] = None):
        """Initialize repository with goods catalog.

        Args:
            goods: Optional custom goods list. Defaults to GOODS constant.
        """
        self._goods = goods if goods is not None else GOODS

    def get_all(self) -> List[Good]:
        """Get all available goods.

        Returns:
            Complete list of all tradable goods in the game.
        """
        return list(self._goods)

    def get_by_name(self, name: str) -> Optional[Good]:
        """Find a good by exact name match.

        Args:
            name: Exact name of the product (case-sensitive).

        Returns:
            The Good if found, None otherwise.

        Examples:
            >>> repo.get_by_name("TV")
            Good(name="TV", base_price=800, ...)
            >>> repo.get_by_name("NonExistent")
            None
        """
        for good in self._goods:
            if good.name == name:
                return good
        return None

    def get_by_type(self, good_type: str) -> List[Good]:
        """Get all goods of a specific type.

        Args:
            good_type: Type filter - "standard", "luxury", or "contraband" (case-insensitive).

        Returns:
            List of goods matching the type.

        Examples:
            >>> repo.get_by_type("luxury")
            [Good(name="Luxury Watch", ...), Good(name="Ferrari", ...)]
        """
        type_lower = str(good_type).lower()
        return [
            g for g in self._goods
            if str(getattr(g, "type", "standard")).lower() == type_lower
        ]

    def get_by_category(self, category: str) -> List[Good]:
        """Get all goods in a specific category.

        Args:
            category: Category filter - "electronics", "jewelry", "cars", "drugs", or "weapons"
                     (case-insensitive).

        Returns:
            List of goods in the category.

        Examples:
            >>> repo.get_by_category("electronics")
            [Good(name="TV", ...), Good(name="Computer", ...), ...]
        """
        category_lower = str(category).lower()
        return [
            g for g in self._goods
            if str(getattr(g, "category", "")).lower() == category_lower
        ]

    def filter(
        self,
        *,
        good_type: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Good]:
        """Filter goods by type and/or category.

        Args:
            good_type: Optional type filter - "standard", "luxury", or "contraband".
            category: Optional category filter - "electronics", "jewelry", "cars", etc.

        Returns:
            List of goods matching all specified filters.

        Examples:
            >>> repo.filter(good_type="luxury", category="cars")
            [Good(name="Ferrari", ...), Good(name="Bentley", ...), ...]
            >>> repo.filter(category="electronics")
            [Good(name="TV", ...), Good(name="Computer", ...), ...]
        """
        results = list(self._goods)

        if good_type is not None:
            type_lower = str(good_type).lower()
            results = [
                g for g in results
                if str(getattr(g, "type", "standard")).lower() == type_lower
            ]

        if category is not None:
            category_lower = str(category).lower()
            results = [
                g for g in results
                if str(getattr(g, "category", "")).lower() == category_lower
            ]

        return results

    def is_luxury(self, name: str) -> bool:
        """Check if a good is a luxury item.

        Args:
            name: Name of the product to check.

        Returns:
            True if the good exists and has type="luxury", False otherwise.

        Examples:
            >>> repo.is_luxury("Ferrari")
            True
            >>> repo.is_luxury("TV")
            False
        """
        good = self.get_by_name(name)
        return str(getattr(good, "type", "")).lower() == "luxury" if good else False

    def is_contraband(self, name: str) -> bool:
        """Check if a good is contraband.

        Args:
            name: Name of the product to check.

        Returns:
            True if the good exists and has type="contraband", False otherwise.

        Examples:
            >>> repo.is_contraband("Cocaine")
            True
            >>> repo.is_contraband("TV")
            False
        """
        good = self.get_by_name(name)
        return str(getattr(good, "type", "")).lower() == "contraband" if good else False

    def count(self) -> int:
        """Get total number of goods.

        Returns:
            Total count of available goods.
        """
        return len(self._goods)
