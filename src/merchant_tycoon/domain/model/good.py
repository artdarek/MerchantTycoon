from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Good:
    """Represents a tradable product in the game economy.

    Goods are the primary items that players buy and sell across different cities
    to generate profit through arbitrage. Each good has a base price that fluctuates
    based on variance and city-specific multipliers.

    Attributes:
        name: Display name of the product (e.g., "TV", "Ferrari", "Cocaine").
        base_price: Default market price in dollars before city multipliers and variance.
            This is the baseline price used for calculations. Example: 800 for a TV.
        price_variance: Price volatility factor (0.0-1.0) controlling random fluctuations.
            Higher values mean more price swings. Standard: 0.3 (±30%),
            Luxury: 0.4-0.7 (±40-70%), Contraband: 0.8-1.0 (±80-100%).
        type: Product tier classification determining risk/reward profile.
            Valid values:
            - "standard": Stable prices, lower volatility, consistent profits
            - "luxury": Higher prices, more volatility, premium city margins
            - "contraband": Extreme volatility, high risk/reward, event exposure
        category: Product category for grouping and filtering.
            Valid values:
            - "electronics": Tech products (TVs, laptops, phones, etc.)
            - "jewelry": Luxury accessories (watches, necklaces)
            - "cars": Vehicles from economy to luxury (Fiat to Bugatti)
            - "drugs": Contraband narcotics (weed, cocaine)
            - "weapons": Contraband armaments (grenades, pistols, shotguns)

    Examples:
        >>> tv = Good("TV", 800, 0.3, "standard", "electronics")
        >>> ferrari = Good("Ferrari", 100000, 0.5, "luxury", "cars")
        >>> cocaine = Good("Cocaine", 2000, 1.0, "contraband", "drugs")
    """
    name: str
    base_price: int
    price_variance: float = 0.3  # 30% variance (±30% price fluctuation)
    # Classification
    type: str = "standard"   # "standard" | "luxury" | "contraband"
    category: str = "electronics"  # "electronics" | "jewelry" | "cars" | "drugs" | "weapons"