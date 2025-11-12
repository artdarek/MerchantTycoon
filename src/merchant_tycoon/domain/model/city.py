from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class TravelEventsConfig:
    """Configuration for travel events in a city.

    Attributes:
        probability: Probability that any event occurs when traveling to this city (0-1, required)
        loss_min: Minimum number of loss events (default: 0)
        loss_max: Maximum number of loss events (default: 2)
        gain_min: Minimum number of gain events (default: 0)
        gain_max: Maximum number of gain events (default: 2)
    """
    probability: float
    loss_min: int = 0
    loss_max: int = 2
    gain_min: int = 0
    gain_max: int = 2


@dataclass
class City:
    """Represents a trading city/location in the game world.

    Cities are the physical locations where trading occurs. Each city has unique
    price multipliers for every good, creating arbitrage opportunities for players
    who travel and exploit price differences between cities.

    Attributes:
        name: Display name of the city (e.g., "Warsaw", "London", "Tokyo").
        country: Country or region where the city is located (e.g., "Poland", "United Kingdom").
        price_multiplier: Dictionary mapping good names to city-specific price multipliers.
            Each multiplier is a float typically between 0.5 and 1.5:
            - < 1.0: Good is cheaper in this city (e.g., 0.8 = 20% discount)
            - = 1.0: Good is at base price (neutral)
            - > 1.0: Good is more expensive (e.g., 1.2 = 20% markup)

            Keys are good names (e.g., "TV", "Ferrari", "Cocaine")
            Values are multiplier floats applied to base prices

            Example: {"TV": 1.0, "Ferrari": 1.25, "Cocaine": 0.5}
            means TV is normal price, Ferrari is 25% more expensive, and
            Cocaine is 50% cheaper in this city.
        travel_events: Configuration for travel events when arriving in this city.
            Controls how many loss and gain events can occur per journey.

    Examples:
        >>> warsaw = City("Warsaw", "Poland", {"TV": 1.0, "Ferrari": 1.0})
        >>> london = City("London", "UK", {"TV": 0.85, "Ferrari": 1.25})

    Notes:
        - Price multipliers are static per city but combined with random variance
        - Cities with extreme multipliers (e.g., Amsterdam for contraband) create
          profitable trade routes for experienced players
        - Wealthy cities (Paris, London, Stockholm) typically have higher luxury
          good multipliers
    """
    name: str
    country: str
    price_multiplier: Dict[str, float]  # Per-good multipliers for this city
    travel_events: TravelEventsConfig = field(default_factory=TravelEventsConfig)
