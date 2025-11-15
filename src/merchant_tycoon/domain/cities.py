"""Domain constant: All trading cities in the game world.

This module defines the 11 European cities where trading occurs. Each city has unique
price multipliers for every good, creating arbitrage opportunities for players who
travel and exploit price differences between locations.

Constants:
    CITIES: List of all 11 trading cities with their price multipliers for each good.
        Used by GoodsService to calculate city-specific prices and by TravelService
        for navigation.

Cities Included:
    - Warsaw, Poland (base prices, central Europe)
    - Berlin, Germany (tech hub, high electronics demand)
    - Prague, Czech Republic (low contraband prices)
    - Vienna, Austria (wealthy city, high luxury prices)
    - Budapest, Hungary (economy city, low prices)
    - Paris, France (luxury capital, premium goods expensive)
    - London, United Kingdom (financial center, highest contraband prices)
    - Rome, Italy (mixed market, Ferrari discount)
    - Amsterdam, Netherlands (lowest contraband prices)
    - Barcelona, Spain (Mediterranean market)
    - Stockholm, Sweden (wealthy, highest overall prices)

Price Multipliers:
    Each city has a dictionary mapping good names to multipliers:
    - < 1.0: Good is cheaper (e.g., 0.5 = 50% discount)
    - = 1.0: Good is at base price
    - > 1.0: Good is more expensive (e.g., 1.5 = 50% markup)

Examples:
    >>> from merchant_tycoon.domain.cities import CITIES
    >>> warsaw = CITIES[0]  # First city
    >>> london = [c for c in CITIES if c.name == "London"][0]
    >>> # Find cheapest city for a product
    >>> cheapest = min(CITIES, key=lambda c: c.price_multiplier.get("TV", 1.0))

See Also:
    - City: Domain model representing a single city
    - TravelService: Business logic for traveling between cities
    - GoodsService: Uses city multipliers for price calculation
"""
from __future__ import annotations
from typing import List

from merchant_tycoon.domain.model.city import City, TravelEventsConfig

# All trading cities in the game (11 European cities)
CITIES: List[City] = [
    # Warsaw - Balanced, central European city
    City("Warsaw", "Poland", {"TV": 1.0, "Computer": 1.0, "Printer": 1.0, "Phone": 1.0,
          "Camera": 1.0, "Laptop": 1.0, "Tablet": 1.0, "Console": 1.0,
          "Headphones": 1.0, "Smartwatch": 1.0, "VR Headset": 1.0, "Coffee Machine": 1.0,
          "Powerbank": 1.0, "USB Charger": 1.0, "Pendrive": 1.0,
          "Luxury Watch": 1.0, "Diamond Necklace": 1.0, "Gaming Laptop": 1.0, "High-end Drone": 1.0, "4K OLED TV": 1.0,
          "Fiat": 1.0, "Opel Astra": 1.0, "Ford Focus": 1.0, "Ferrari": 1.0, "Bentley": 1.0, "Bugatti": 1.0,
          "Weed": 0.9, "Cocaine": 0.95, "Grenade": 0.9, "Pistol": 0.9, "Shotgun": 0.95},
         TravelEventsConfig(probability=0.30, loss_min=0, loss_max=1, gain_min=0, gain_max=2, neutral_min=1, neutral_max=1)),

    # Berlin - Stable tech hub, slightly safer
    City("Berlin", "Germany", {"TV": 0.8, "Computer": 1.2, "Printer": 0.9, "Phone": 1.1,
          "Camera": 0.85, "Laptop": 1.15, "Tablet": 0.95, "Console": 1.05,
          "Headphones": 0.85, "Smartwatch": 1.1, "VR Headset": 0.9, "Coffee Machine": 1.05,
          "Powerbank": 0.85, "USB Charger": 0.85, "Pendrive": 0.85,
          "Luxury Watch": 1.1, "Diamond Necklace": 1.15, "Gaming Laptop": 0.9, "High-end Drone": 0.95, "4K OLED TV": 0.9,
          "Fiat": 0.95, "Opel Astra": 0.85, "Ford Focus": 0.9, "Ferrari": 1.15, "Bentley": 1.1, "Bugatti": 1.15,
          "Weed": 0.85, "Cocaine": 1.0, "Grenade": 0.9, "Pistol": 0.95, "Shotgun": 1.0},
         TravelEventsConfig(probability=0.30, loss_min=0, loss_max=1, gain_min=0, gain_max=2, neutral_min=0, neutral_max=2)),

    # Prague - Cheap contraband hub, risky for traders
    City("Prague", "Czech Republic", {"TV": 1.1, "Computer": 0.9, "Printer": 1.2, "Phone": 0.95,
          "Camera": 1.1, "Laptop": 0.85, "Tablet": 1.05, "Console": 0.9,
          "Headphones": 1.15, "Smartwatch": 0.95, "VR Headset": 1.2, "Coffee Machine": 0.9,
          "Powerbank": 1.15, "USB Charger": 1.15, "Pendrive": 1.15,
          "Luxury Watch": 0.9, "Diamond Necklace": 0.9, "Gaming Laptop": 0.95, "High-end Drone": 0.95, "4K OLED TV": 1.0,
          "Fiat": 0.9, "Opel Astra": 0.95, "Ford Focus": 0.95, "Ferrari": 0.85, "Bentley": 0.85, "Bugatti": 0.9,
          "Weed": 0.6, "Cocaine": 0.7, "Grenade": 0.65, "Pistol": 0.7, "Shotgun": 0.75},
         TravelEventsConfig(probability=0.30, loss_min=0, loss_max=2, gain_min=0, gain_max=2, neutral_min=0, neutral_max=1)),

    # Vienna - Wealthy, safe city
    City("Vienna", "Austria", {"TV": 0.95, "Computer": 1.1, "Printer": 0.85, "Phone": 1.2,
          "Camera": 1.0, "Laptop": 1.05, "Tablet": 1.1, "Console": 0.95,
          "Headphones": 0.9, "Smartwatch": 1.15, "VR Headset": 1.05, "Coffee Machine": 0.8,
          "Powerbank": 0.9, "USB Charger": 0.9, "Pendrive": 0.9,
          "Luxury Watch": 1.1, "Diamond Necklace": 1.15, "Gaming Laptop": 1.05, "High-end Drone": 1.0, "4K OLED TV": 1.1,
          "Fiat": 1.0, "Opel Astra": 0.95, "Ford Focus": 1.0, "Ferrari": 1.1, "Bentley": 1.1, "Bugatti": 1.15,
          "Weed": 1.1, "Cocaine": 1.15, "Grenade": 1.05, "Pistol": 1.1, "Shotgun": 1.15},
         TravelEventsConfig(probability=0.18, loss_min=0, loss_max=1, gain_min=1, gain_max=3, neutral_min=0, neutral_max=2)),

    # Budapest - Economy city, moderate risk
    City("Budapest", "Hungary", {"TV": 1.2, "Computer": 0.85, "Printer": 1.1, "Phone": 0.9,
          "Camera": 1.15, "Laptop": 0.9, "Tablet": 0.85, "Console": 1.1,
          "Headphones": 1.2, "Smartwatch": 0.85, "VR Headset": 1.1, "Coffee Machine": 1.15,
          "Powerbank": 1.2, "USB Charger": 1.2, "Pendrive": 1.2,
          "Luxury Watch": 0.85, "Diamond Necklace": 0.85, "Gaming Laptop": 0.9, "High-end Drone": 0.9, "4K OLED TV": 0.9,
          "Fiat": 0.85, "Opel Astra": 0.9, "Ford Focus": 0.9, "Ferrari": 0.8, "Bentley": 0.8, "Bugatti": 0.85,
          "Weed": 0.65, "Cocaine": 0.75, "Grenade": 0.7, "Pistol": 0.75, "Shotgun": 0.8},
         TravelEventsConfig(probability=0.28, loss_min=0, loss_max=2, gain_min=0, gain_max=2, neutral_min=0, neutral_max=1)),

    # Paris - Luxury capital, stable and safe
    City("Paris", "France", {"TV": 0.9, "Computer": 1.15, "Printer": 0.95, "Phone": 1.05,
          "Camera": 1.2, "Laptop": 1.1, "Tablet": 1.0, "Console": 0.85,
          "Headphones": 0.95, "Smartwatch": 1.2, "VR Headset": 0.85, "Coffee Machine": 0.75,
          "Powerbank": 1.05, "USB Charger": 1.05, "Pendrive": 1.05,
          "Luxury Watch": 1.3, "Diamond Necklace": 1.35, "Gaming Laptop": 1.1, "High-end Drone": 1.05, "4K OLED TV": 1.2,
          "Fiat": 1.05, "Opel Astra": 1.0, "Ford Focus": 1.05, "Ferrari": 1.2, "Bentley": 1.15, "Bugatti": 0.9,
          "Weed": 1.15, "Cocaine": 1.25, "Grenade": 1.2, "Pistol": 1.2, "Shotgun": 1.25},
         TravelEventsConfig(probability=0.20, loss_min=0, loss_max=1, gain_min=1, gain_max=2, neutral_min=1, neutral_max=2)),

    # London - Financial center, very stable
    City("London", "United Kingdom", {"TV": 0.85, "Computer": 1.25, "Printer": 1.0, "Phone": 1.15,
          "Camera": 0.9, "Laptop": 1.2, "Tablet": 1.05, "Console": 0.95,
          "Headphones": 1.0, "Smartwatch": 1.1, "VR Headset": 1.15, "Coffee Machine": 1.1,
          "Powerbank": 1.05, "USB Charger": 1.05, "Pendrive": 1.05,
          "Luxury Watch": 1.25, "Diamond Necklace": 1.3, "Gaming Laptop": 1.15, "High-end Drone": 1.1, "4K OLED TV": 1.2,
          "Fiat": 1.1, "Opel Astra": 1.05, "Ford Focus": 0.95, "Ferrari": 1.25, "Bentley": 0.85, "Bugatti": 1.2,
          "Weed": 1.35, "Cocaine": 1.45, "Grenade": 1.4, "Pistol": 1.4, "Shotgun": 1.45},
         TravelEventsConfig(probability=0.20, loss_min=0, loss_max=1, gain_min=1, gain_max=2, neutral_min=1, neutral_max=2)),

    # Rome - Mixed market, balanced
    City("Rome", "Italy", {"TV": 1.05, "Computer": 0.95, "Printer": 1.15, "Phone": 0.9,
          "Camera": 1.15, "Laptop": 0.9, "Tablet": 0.95, "Console": 1.0,
          "Headphones": 1.1, "Smartwatch": 0.9, "VR Headset": 1.0, "Coffee Machine": 0.7,
          "Powerbank": 1.1, "USB Charger": 1.1, "Pendrive": 1.1,
          "Luxury Watch": 1.1, "Diamond Necklace": 1.1, "Gaming Laptop": 0.95, "High-end Drone": 1.0, "4K OLED TV": 1.0,
          "Fiat": 0.8, "Opel Astra": 1.0, "Ford Focus": 1.05, "Ferrari": 0.85, "Bentley": 1.15, "Bugatti": 1.1,
          "Weed": 1.0, "Cocaine": 1.2, "Grenade": 1.1, "Pistol": 1.15, "Shotgun": 1.2},
         TravelEventsConfig(probability=0.25, loss_min=0, loss_max=2, gain_min=0, gain_max=2, neutral_min=0, neutral_max=1)),

    # Amsterdam - Cheapest contraband, high risk/reward
    City("Amsterdam", "Netherlands", {"TV": 0.95, "Computer": 1.1, "Printer": 0.9, "Phone": 1.05,
          "Camera": 0.95, "Laptop": 1.15, "Tablet": 1.1, "Console": 1.05,
          "Headphones": 0.85, "Smartwatch": 1.05, "VR Headset": 1.1, "Coffee Machine": 0.85,
          "Powerbank": 0.9, "USB Charger": 0.9, "Pendrive": 0.9,
          "Luxury Watch": 0.95, "Diamond Necklace": 1.0, "Gaming Laptop": 1.1, "High-end Drone": 1.0, "4K OLED TV": 1.05,
          "Fiat": 0.95, "Opel Astra": 0.95, "Ford Focus": 1.0, "Ferrari": 1.05, "Bentley": 1.0, "Bugatti": 1.05,
          "Weed": 0.5, "Cocaine": 0.65, "Grenade": 0.8, "Pistol": 0.85, "Shotgun": 0.9},
         TravelEventsConfig(probability=0.32, loss_min=1, loss_max=3, gain_min=1, gain_max=3, neutral_min=1, neutral_max=2)),

    # Barcelona - Mediterranean, relaxed atmosphere
    City("Barcelona", "Spain", {"TV": 1.15, "Computer": 0.85, "Printer": 1.05, "Phone": 0.95,
          "Camera": 1.05, "Laptop": 0.95, "Tablet": 0.9, "Console": 1.15,
          "Headphones": 1.05, "Smartwatch": 0.95, "VR Headset": 0.9, "Coffee Machine": 0.9,
          "Powerbank": 1.05, "USB Charger": 1.05, "Pendrive": 1.05,
          "Luxury Watch": 1.05, "Diamond Necklace": 1.1, "Gaming Laptop": 0.95, "High-end Drone": 0.95, "4K OLED TV": 0.9,
          "Fiat": 0.9, "Opel Astra": 0.95, "Ford Focus": 1.0, "Ferrari": 0.95, "Bentley": 1.05, "Bugatti": 1.0,
          "Weed": 0.95, "Cocaine": 1.1, "Grenade": 1.05, "Pistol": 1.05, "Shotgun": 1.1},
         TravelEventsConfig(probability=0.22, loss_min=0, loss_max=2, gain_min=1, gain_max=2, neutral_min=0, neutral_max=1)),

    # Stockholm - Wealthiest, safest city
    City("Stockholm", "Sweden", {"TV": 0.75, "Computer": 1.3, "Printer": 0.85, "Phone": 1.2,
          "Camera": 0.8, "Laptop": 1.25, "Tablet": 1.15, "Console": 0.9,
          "Headphones": 0.8, "Smartwatch": 1.25, "VR Headset": 1.05, "Coffee Machine": 1.05,
          "Powerbank": 0.8, "USB Charger": 0.8, "Pendrive": 0.8,
          "Luxury Watch": 1.25, "Diamond Necklace": 1.3, "Gaming Laptop": 1.2, "High-end Drone": 1.15, "4K OLED TV": 1.2,
          "Fiat": 1.05, "Opel Astra": 1.1, "Ford Focus": 1.1, "Ferrari": 1.3, "Bentley": 1.2, "Bugatti": 1.25,
          "Weed": 1.5, "Cocaine": 1.65, "Grenade": 1.6, "Pistol": 1.6, "Shotgun": 1.65},
         TravelEventsConfig(probability=0.15, loss_min=0, loss_max=1, gain_min=1, gain_max=3, neutral_min=1, neutral_max=2)),
]