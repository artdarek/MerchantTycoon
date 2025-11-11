from __future__ import annotations
from typing import List

from merchant_tycoon.domain.model.good import Good
from merchant_tycoon.domain.model.asset import Asset
from merchant_tycoon.domain.model.city import City
from merchant_tycoon.domain.model.difficulty_level import DifficultyLevel

# Goods
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

# Financial assets (unified list). Filter by asset_type: 'stock' | 'commodity' | 'crypto'.
ASSETS: List[Asset] = [
    # Stocks
    Asset("Google", "GOOGL", 150, 0.6, "stock"),
    Asset("Meta", "META", 80, 0.5, "stock"),
    Asset("Apple", "AAPL", 120, 0.7, "stock"),
    Asset("Microsoft", "MSFT", 200, 0.4, "stock"),
    Asset("Amazon", "AMZN", 180, 0.6, "stock"),
    Asset("Netflix", "NFLX", 90, 0.8, "stock"),
    Asset("NVIDIA", "NVDA", 250, 0.9, "stock"),
    Asset("Tesla", "TSLA", 160, 0.8, "stock"),
    Asset("AMD", "AMD", 110, 0.7, "stock"),
    Asset("Oracle", "ORCL", 95, 0.5, "stock"),
    Asset("Adobe", "ADBE", 140, 0.6, "stock"),
    Asset("Intel", "INTC", 85, 0.6, "stock"),
    # Commodities
    Asset("Gold", "GOLD", 1800, 0.3, "commodity"),
    Asset("Oil", "OIL", 75, 0.8, "commodity"),
    Asset("Silver", "SILV", 25, 0.4, "commodity"),
    Asset("Copper", "COPP", 8, 0.5, "commodity"),
    # Crypto
    Asset("Bitcoin", "BTC", 35000, 0.7, "crypto"),
    Asset("Ethereum", "ETH", 2000, 0.8, "crypto"),
    Asset("Solana", "SOL", 80, 0.9, "crypto"),
    Asset("Dogecoin", "DOGE", 5, 1.0, "crypto"),  # Price range $1-$10 (base 5, variance 1.0)
]

# Cities
CITIES: List[City] = [
    City("Warsaw", "Poland", {"TV": 1.0, "Computer": 1.0, "Printer": 1.0, "Phone": 1.0,
          "Camera": 1.0, "Laptop": 1.0, "Tablet": 1.0, "Console": 1.0,
          "Headphones": 1.0, "Smartwatch": 1.0, "VR Headset": 1.0, "Coffee Machine": 1.0,
          "Powerbank": 1.0, "USB Charger": 1.0, "Pendrive": 1.0,
          "Luxury Watch": 1.0, "Diamond Necklace": 1.0, "Gaming Laptop": 1.0, "High-end Drone": 1.0, "4K OLED TV": 1.0,
          "Fiat": 1.0, "Opel Astra": 1.0, "Ford Focus": 1.0, "Ferrari": 1.0, "Bentley": 1.0, "Bugatti": 1.0,
          "Weed": 0.9, "Cocaine": 0.95, "Grenade": 0.9, "Pistol": 0.9, "Shotgun": 0.95}),
    City("Berlin", "Germany", {"TV": 0.8, "Computer": 1.2, "Printer": 0.9, "Phone": 1.1,
          "Camera": 0.85, "Laptop": 1.15, "Tablet": 0.95, "Console": 1.05,
          "Headphones": 0.85, "Smartwatch": 1.1, "VR Headset": 0.9, "Coffee Machine": 1.05,
          "Powerbank": 0.85, "USB Charger": 0.85, "Pendrive": 0.85,
          "Luxury Watch": 1.1, "Diamond Necklace": 1.15, "Gaming Laptop": 0.9, "High-end Drone": 0.95, "4K OLED TV": 0.9,
          "Fiat": 0.95, "Opel Astra": 0.85, "Ford Focus": 0.9, "Ferrari": 1.15, "Bentley": 1.1, "Bugatti": 1.15,
          "Weed": 0.85, "Cocaine": 1.0, "Grenade": 0.9, "Pistol": 0.95, "Shotgun": 1.0}),
    City("Prague", "Czech Republic", {"TV": 1.1, "Computer": 0.9, "Printer": 1.2, "Phone": 0.95,
          "Camera": 1.1, "Laptop": 0.85, "Tablet": 1.05, "Console": 0.9,
          "Headphones": 1.15, "Smartwatch": 0.95, "VR Headset": 1.2, "Coffee Machine": 0.9,
          "Powerbank": 1.15, "USB Charger": 1.15, "Pendrive": 1.15,
          "Luxury Watch": 0.9, "Diamond Necklace": 0.9, "Gaming Laptop": 0.95, "High-end Drone": 0.95, "4K OLED TV": 1.0,
          "Fiat": 0.9, "Opel Astra": 0.95, "Ford Focus": 0.95, "Ferrari": 0.85, "Bentley": 0.85, "Bugatti": 0.9,
          "Weed": 0.6, "Cocaine": 0.7, "Grenade": 0.65, "Pistol": 0.7, "Shotgun": 0.75}),
    City("Vienna", "Austria", {"TV": 0.95, "Computer": 1.1, "Printer": 0.85, "Phone": 1.2,
          "Camera": 1.0, "Laptop": 1.05, "Tablet": 1.1, "Console": 0.95,
          "Headphones": 0.9, "Smartwatch": 1.15, "VR Headset": 1.05, "Coffee Machine": 0.8,
          "Powerbank": 0.9, "USB Charger": 0.9, "Pendrive": 0.9,
          "Luxury Watch": 1.1, "Diamond Necklace": 1.15, "Gaming Laptop": 1.05, "High-end Drone": 1.0, "4K OLED TV": 1.1,
          "Fiat": 1.0, "Opel Astra": 0.95, "Ford Focus": 1.0, "Ferrari": 1.1, "Bentley": 1.1, "Bugatti": 1.15,
          "Weed": 1.1, "Cocaine": 1.15, "Grenade": 1.05, "Pistol": 1.1, "Shotgun": 1.15}),
    City("Budapest", "Hungary", {"TV": 1.2, "Computer": 0.85, "Printer": 1.1, "Phone": 0.9,
          "Camera": 1.15, "Laptop": 0.9, "Tablet": 0.85, "Console": 1.1,
          "Headphones": 1.2, "Smartwatch": 0.85, "VR Headset": 1.1, "Coffee Machine": 1.15,
          "Powerbank": 1.2, "USB Charger": 1.2, "Pendrive": 1.2,
          "Luxury Watch": 0.85, "Diamond Necklace": 0.85, "Gaming Laptop": 0.9, "High-end Drone": 0.9, "4K OLED TV": 0.9,
          "Fiat": 0.85, "Opel Astra": 0.9, "Ford Focus": 0.9, "Ferrari": 0.8, "Bentley": 0.8, "Bugatti": 0.85,
          "Weed": 0.65, "Cocaine": 0.75, "Grenade": 0.7, "Pistol": 0.75, "Shotgun": 0.8}),
    City("Paris", "France", {"TV": 0.9, "Computer": 1.15, "Printer": 0.95, "Phone": 1.05,
          "Camera": 1.2, "Laptop": 1.1, "Tablet": 1.0, "Console": 0.85,
          "Headphones": 0.95, "Smartwatch": 1.2, "VR Headset": 0.85, "Coffee Machine": 0.75,
          "Powerbank": 1.05, "USB Charger": 1.05, "Pendrive": 1.05,
          "Luxury Watch": 1.3, "Diamond Necklace": 1.35, "Gaming Laptop": 1.1, "High-end Drone": 1.05, "4K OLED TV": 1.2,
          "Fiat": 1.05, "Opel Astra": 1.0, "Ford Focus": 1.05, "Ferrari": 1.2, "Bentley": 1.15, "Bugatti": 0.9,
          "Weed": 1.15, "Cocaine": 1.25, "Grenade": 1.2, "Pistol": 1.2, "Shotgun": 1.25}),
    City("London", "United Kingdom", {"TV": 0.85, "Computer": 1.25, "Printer": 1.0, "Phone": 1.15,
          "Camera": 0.9, "Laptop": 1.2, "Tablet": 1.05, "Console": 0.95,
          "Headphones": 1.0, "Smartwatch": 1.1, "VR Headset": 1.15, "Coffee Machine": 1.1,
          "Powerbank": 1.05, "USB Charger": 1.05, "Pendrive": 1.05,
          "Luxury Watch": 1.25, "Diamond Necklace": 1.3, "Gaming Laptop": 1.15, "High-end Drone": 1.1, "4K OLED TV": 1.2,
          "Fiat": 1.1, "Opel Astra": 1.05, "Ford Focus": 0.95, "Ferrari": 1.25, "Bentley": 0.85, "Bugatti": 1.2,
          "Weed": 1.35, "Cocaine": 1.45, "Grenade": 1.4, "Pistol": 1.4, "Shotgun": 1.45}),
    City("Rome", "Italy", {"TV": 1.05, "Computer": 0.95, "Printer": 1.15, "Phone": 0.9,
          "Camera": 1.15, "Laptop": 0.9, "Tablet": 0.95, "Console": 1.0,
          "Headphones": 1.1, "Smartwatch": 0.9, "VR Headset": 1.0, "Coffee Machine": 0.7,
          "Powerbank": 1.1, "USB Charger": 1.1, "Pendrive": 1.1,
          "Luxury Watch": 1.1, "Diamond Necklace": 1.1, "Gaming Laptop": 0.95, "High-end Drone": 1.0, "4K OLED TV": 1.0,
          "Fiat": 0.8, "Opel Astra": 1.0, "Ford Focus": 1.05, "Ferrari": 0.85, "Bentley": 1.15, "Bugatti": 1.1,
          "Weed": 1.0, "Cocaine": 1.2, "Grenade": 1.1, "Pistol": 1.15, "Shotgun": 1.2}),
    City("Amsterdam", "Netherlands", {"TV": 0.95, "Computer": 1.1, "Printer": 0.9, "Phone": 1.05,
          "Camera": 0.95, "Laptop": 1.15, "Tablet": 1.1, "Console": 1.05,
          "Headphones": 0.85, "Smartwatch": 1.05, "VR Headset": 1.1, "Coffee Machine": 0.85,
          "Powerbank": 0.9, "USB Charger": 0.9, "Pendrive": 0.9,
          "Luxury Watch": 0.95, "Diamond Necklace": 1.0, "Gaming Laptop": 1.1, "High-end Drone": 1.0, "4K OLED TV": 1.05,
          "Fiat": 0.95, "Opel Astra": 0.95, "Ford Focus": 1.0, "Ferrari": 1.05, "Bentley": 1.0, "Bugatti": 1.05,
          "Weed": 0.5, "Cocaine": 0.65, "Grenade": 0.8, "Pistol": 0.85, "Shotgun": 0.9}),
    City("Barcelona", "Spain", {"TV": 1.15, "Computer": 0.85, "Printer": 1.05, "Phone": 0.95,
          "Camera": 1.05, "Laptop": 0.95, "Tablet": 0.9, "Console": 1.15,
          "Headphones": 1.05, "Smartwatch": 0.95, "VR Headset": 0.9, "Coffee Machine": 0.9,
          "Powerbank": 1.05, "USB Charger": 1.05, "Pendrive": 1.05,
          "Luxury Watch": 1.05, "Diamond Necklace": 1.1, "Gaming Laptop": 0.95, "High-end Drone": 0.95, "4K OLED TV": 0.9,
          "Fiat": 0.9, "Opel Astra": 0.95, "Ford Focus": 1.0, "Ferrari": 0.95, "Bentley": 1.05, "Bugatti": 1.0,
          "Weed": 0.95, "Cocaine": 1.1, "Grenade": 1.05, "Pistol": 1.05, "Shotgun": 1.1}),
    City("Stockholm", "Sweden", {"TV": 0.75, "Computer": 1.3, "Printer": 0.85, "Phone": 1.2,
          "Camera": 0.8, "Laptop": 1.25, "Tablet": 1.15, "Console": 0.9,
          "Headphones": 0.8, "Smartwatch": 1.25, "VR Headset": 1.05, "Coffee Machine": 1.05,
          "Powerbank": 0.8, "USB Charger": 0.8, "Pendrive": 0.8,
          "Luxury Watch": 1.25, "Diamond Necklace": 1.3, "Gaming Laptop": 1.2, "High-end Drone": 1.15, "4K OLED TV": 1.2,
          "Fiat": 1.05, "Opel Astra": 1.1, "Ford Focus": 1.1, "Ferrari": 1.3, "Bentley": 1.2, "Bugatti": 1.25,
          "Weed": 1.5, "Cocaine": 1.65, "Grenade": 1.6, "Pistol": 1.6, "Shotgun": 1.65}),
]

# Difficulty levels
DIFFICULTY_LEVELS: List[DifficultyLevel] = [
    DifficultyLevel(
        name="playground",
        display_name="Playground",
        start_cash=1_000_000,
        start_capacity=1000,
        description="Unlimited funds for experimentation"
    ),
    DifficultyLevel(
        name="easy",
        display_name="Easy",
        start_cash=100_000,
        start_capacity=100,
        description="Generous starting resources"
    ),
    DifficultyLevel(
        name="normal",
        display_name="Normal",
        start_cash=50_000,
        start_capacity=50,
        description="Balanced challenge"
    ),
    DifficultyLevel(
        name="hard",
        display_name="Hard",
        start_cash=10_000,
        start_capacity=10,
        description="Limited resources, strategic planning required"
    ),
    DifficultyLevel(
        name="insane",
        display_name="Insane",
        start_cash=0,
        start_capacity=1,
        description="Start with nothing, maximum challenge"
    ),
]
