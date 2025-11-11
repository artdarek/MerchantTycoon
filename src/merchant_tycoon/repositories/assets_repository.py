"""Repository for accessing and querying investment assets.

This repository provides a clean, read-only interface to the ASSETS domain constant,
encapsulating all lookup and filtering logic for tradable financial assets.
"""
from typing import List, Optional

from merchant_tycoon.domain.model.asset import Asset
from merchant_tycoon.domain.assets import ASSETS


class AssetsRepository:
    """Repository for querying investment assets.

    Provides methods for retrieving assets by various criteria without directly
    exposing the underlying ASSETS constant to services and UI components.

    Examples:
        >>> repo = AssetsRepository()
        >>> all_assets = repo.get_all()
        >>> aapl = repo.get_by_symbol("AAPL")
        >>> stocks = repo.get_by_type("stock")
        >>> cryptos = repo.get_by_type("crypto")
    """

    def __init__(self, assets: Optional[List[Asset]] = None):
        """Initialize repository with assets catalog.

        Args:
            assets: Optional custom assets list. Defaults to ASSETS constant.
        """
        self._assets = assets if assets is not None else ASSETS

    def get_all(self) -> List[Asset]:
        """Get all available assets.

        Returns:
            Complete list of all tradable assets in the game.
        """
        return list(self._assets)

    def get_by_symbol(self, symbol: str) -> Optional[Asset]:
        """Find an asset by its ticker symbol.

        Args:
            symbol: Ticker symbol (case-sensitive, e.g., "AAPL", "BTC").

        Returns:
            The Asset if found, None otherwise.

        Examples:
            >>> repo.get_by_symbol("AAPL")
            Asset(name="Apple Inc.", symbol="AAPL", ...)
            >>> repo.get_by_symbol("INVALID")
            None
        """
        for asset in self._assets:
            if asset.symbol == symbol:
                return asset
        return None

    def get_by_name(self, name: str) -> Optional[Asset]:
        """Find an asset by its full name.

        Args:
            name: Full name of the asset (case-sensitive).

        Returns:
            The Asset if found, None otherwise.

        Examples:
            >>> repo.get_by_name("Apple Inc.")
            Asset(name="Apple Inc.", symbol="AAPL", ...)
        """
        for asset in self._assets:
            if asset.name == name:
                return asset
        return None

    def get_by_type(self, asset_type: str) -> List[Asset]:
        """Get all assets of a specific type.

        Args:
            asset_type: Type filter - "stock", "commodity", or "crypto" (case-insensitive).

        Returns:
            List of assets matching the type.

        Examples:
            >>> repo.get_by_type("stock")
            [Asset(symbol="AAPL", ...), Asset(symbol="GOOGL", ...)]
            >>> repo.get_by_type("crypto")
            [Asset(symbol="BTC", ...), Asset(symbol="ETH", ...)]
        """
        type_lower = str(asset_type).lower()
        return [
            a for a in self._assets
            if str(getattr(a, "asset_type", "")).lower() == type_lower
        ]

    def filter(self, *, asset_type: Optional[str] = None) -> List[Asset]:
        """Filter assets by type.

        Args:
            asset_type: Optional type filter - "stock", "commodity", or "crypto".

        Returns:
            List of assets matching the filter, or all assets if no filter specified.

        Examples:
            >>> repo.filter(asset_type="stock")
            [Asset(symbol="AAPL", ...), ...]
            >>> repo.filter()
            [all assets]
        """
        if asset_type is None:
            return list(self._assets)
        return self.get_by_type(asset_type)

    def is_crypto(self, symbol: str) -> bool:
        """Check if an asset is a cryptocurrency.

        Args:
            symbol: Asset ticker symbol to check.

        Returns:
            True if the asset exists and has asset_type="crypto", False otherwise.

        Examples:
            >>> repo.is_crypto("BTC")
            True
            >>> repo.is_crypto("AAPL")
            False
        """
        asset = self.get_by_symbol(symbol)
        return str(getattr(asset, "asset_type", "")).lower() == "crypto" if asset else False

    def is_stock(self, symbol: str) -> bool:
        """Check if an asset is a stock.

        Args:
            symbol: Asset ticker symbol to check.

        Returns:
            True if the asset exists and has asset_type="stock", False otherwise.

        Examples:
            >>> repo.is_stock("AAPL")
            True
            >>> repo.is_stock("BTC")
            False
        """
        asset = self.get_by_symbol(symbol)
        return str(getattr(asset, "asset_type", "")).lower() == "stock" if asset else False

    def is_commodity(self, symbol: str) -> bool:
        """Check if an asset is a commodity.

        Args:
            symbol: Asset ticker symbol to check.

        Returns:
            True if the asset exists and has asset_type="commodity", False otherwise.

        Examples:
            >>> repo.is_commodity("GOLD")
            True
            >>> repo.is_commodity("AAPL")
            False
        """
        asset = self.get_by_symbol(symbol)
        return str(getattr(asset, "asset_type", "")).lower() == "commodity" if asset else False

    def get_stock_symbols(self) -> set[str]:
        """Get all stock ticker symbols.

        Returns:
            Set of all stock symbols.

        Examples:
            >>> repo.get_stock_symbols()
            {'AAPL', 'GOOGL', 'MSFT', ...}
        """
        return {a.symbol for a in self._assets if str(getattr(a, "asset_type", "")).lower() == "stock"}

    def count(self) -> int:
        """Get total number of assets.

        Returns:
            Total count of available assets.
        """
        return len(self._assets)
