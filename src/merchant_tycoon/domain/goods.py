"""Domain constant: All tradable goods in the game economy.

This module defines the complete catalog of products that players can buy and sell
across cities. Goods are organized into categories (electronics, jewelry, cars, drugs, weapons)
and types (standard, luxury, contraband) with varying price volatility and risk profiles.

Constants:
    GOODS: List of all 31 tradable products with their base prices, volatility,
        and classification. Used by GoodsService for price generation and trading.

Categories:
    - electronics: Tech products (TVs, laptops, phones, etc.) - 18 products
    - jewelry: Luxury accessories (watches, necklaces) - 2 products
    - cars: Vehicles from economy to luxury (Fiat to Bugatti) - 6 products
    - drugs: Contraband narcotics (weed, cocaine) - 2 products
    - weapons: Contraband armaments (grenades, pistols, shotguns) - 3 products

Product Types:
    - standard: ±30% volatility, stable profits, lower risk
    - luxury: ±40-70% volatility, premium city margins, medium risk
    - contraband: ±80-100% volatility, extreme profits, high event risk

Examples:
    >>> from merchant_tycoon.domain.goods import GOODS
    >>> standard_goods = [g for g in GOODS if g.type == "standard"]
    >>> contraband = [g for g in GOODS if g.type == "contraband"]
    >>> cars = [g for g in GOODS if g.category == "cars"]

See Also:
    - Good: Domain model representing a single product
    - GoodsService: Business logic for pricing and trading
"""
from __future__ import annotations
from typing import List

from merchant_tycoon.domain.model.good import Good

# All tradable goods in the game (31 products total)
GOODS: List[Good] = [
    Good("TV", 800, 0.3, "standard", "electronics"),
    Good("Computer", 1200, 0.3, "standard", "electronics"),
    Good("Printer", 300, 0.3, "standard", "electronics"),
    Good("Phone", 600, 0.3, "standard", "electronics"),
    Good("Camera", 400, 0.3, "standard", "electronics"),
    Good("Laptop", 1500, 0.3, "standard", "electronics"),
    Good("Tablet", 500, 0.3, "standard", "electronics"),
    Good("Console", 450, 0.3, "standard", "electronics"),
    Good("Headphones", 150, 0.3, "standard", "electronics"),
    Good("Smartwatch", 400, 0.3, "standard", "electronics"),
    Good("VR Headset", 700, 0.3, "standard", "electronics"),
    Good("Coffee Machine", 450, 0.3, "standard", "electronics"),
    # New low-priced electronics
    Good("Powerbank", 40, 0.3, "standard", "electronics"),
    Good("USB Charger", 25, 0.3, "standard", "electronics"),
    Good("Pendrive", 15, 0.3, "standard", "electronics"),
    # Luxury products (higher prices and volatility)
    Good("Luxury Watch", 6000, 0.6, "luxury", "jewelry"),
    Good("Diamond Necklace", 8000, 0.7, "luxury", "jewelry"),
    Good("Gaming Laptop", 3000, 0.5, "luxury", "electronics"),
    Good("High-end Drone", 2500, 0.5, "luxury", "electronics"),
    Good("4K OLED TV", 2500, 0.4, "luxury", "electronics"),
    # Cars
    Good("Fiat", 20000, 0.3, "standard", "cars"),
    Good("Opel Astra", 40000, 0.3, "standard", "cars"),
    Good("Ford Focus", 50000, 0.3, "standard", "cars"),
    Good("Ferrari", 100000, 0.5, "luxury", "cars"),
    Good("Bentley", 200000, 0.5, "luxury", "cars"),
    Good("Bugatti", 300000, 0.6, "luxury", "cars"),
    # Contraband - Drugs (high risk, high reward)
    Good("Weed", 500, 0.8, "contraband", "drugs"),
    Good("Cocaine", 2000, 1.0, "contraband", "drugs"),
    # Contraband - Weapons (high risk, high reward)
    Good("Grenade", 100, 0.9, "contraband", "weapons"),
    Good("Pistol", 500, 0.8, "contraband", "weapons"),
    Good("Shotgun", 1000, 0.9, "contraband", "weapons"),
]
