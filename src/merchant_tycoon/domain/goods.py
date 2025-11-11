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
# Format: Good(name, base_price, price_variance, type, category, size)
GOODS: List[Good] = [
    # Standard Electronics - Medium size (3-5 slots)
    Good("TV", 800, 0.3, "standard", "electronics", 3),
    Good("Computer", 1200, 0.3, "standard", "electronics", 4),
    Good("Printer", 300, 0.3, "standard", "electronics", 3),
    Good("Phone", 600, 0.3, "standard", "electronics", 2),
    Good("Camera", 400, 0.3, "standard", "electronics", 3),
    Good("Laptop", 1500, 0.3, "standard", "electronics", 5),
    Good("Tablet", 500, 0.3, "standard", "electronics", 2),
    Good("Console", 450, 0.3, "standard", "electronics", 3),
    Good("Headphones", 150, 0.3, "standard", "electronics", 1),
    Good("Smartwatch", 400, 0.3, "standard", "electronics", 1),
    Good("VR Headset", 700, 0.3, "standard", "electronics", 3),
    Good("Coffee Machine", 450, 0.3, "standard", "electronics", 3),
    # Small Electronics - Minimal size (1 slot)
    Good("Powerbank", 40, 0.3, "standard", "electronics", 1),
    Good("USB Charger", 25, 0.3, "standard", "electronics", 1),
    Good("Pendrive", 15, 0.3, "standard", "electronics", 1),
    # Luxury products - Small jewelry (1 slot), larger electronics (3-5 slots)
    Good("Luxury Watch", 6000, 0.6, "luxury", "jewelry", 1),
    Good("Diamond Necklace", 8000, 0.7, "luxury", "jewelry", 1),
    Good("Gaming Laptop", 3000, 0.5, "luxury", "electronics", 5),
    Good("High-end Drone", 2500, 0.5, "luxury", "electronics", 4),
    Good("4K OLED TV", 2500, 0.4, "luxury", "electronics", 3),
    # Cars - Large size (15-30 slots)
    Good("Fiat", 20000, 0.3, "standard", "cars", 15),
    Good("Opel Astra", 40000, 0.3, "standard", "cars", 18),
    Good("Ford Focus", 50000, 0.3, "standard", "cars", 18),
    Good("Ferrari", 100000, 0.5, "luxury", "cars", 25),
    Good("Bentley", 200000, 0.5, "luxury", "cars", 28),
    Good("Bugatti", 300000, 0.6, "luxury", "cars", 30),
    # Contraband - Drugs (10-15 slots)
    Good("Weed", 500, 0.8, "contraband", "drugs", 10),
    Good("Cocaine", 2000, 1.0, "contraband", "drugs", 15),
    # Contraband - Weapons (10-15 slots)
    Good("Grenade", 100, 0.9, "contraband", "weapons", 12),
    Good("Pistol", 500, 0.8, "contraband", "weapons", 10),
    Good("Shotgun", 1000, 0.9, "contraband", "weapons", 15),
]
