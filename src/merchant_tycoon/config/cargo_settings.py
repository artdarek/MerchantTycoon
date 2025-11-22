from dataclasses import dataclass


@dataclass(frozen=True)
class CargoSettings:
    # Starting inventory capacity (units)
    base_capacity: int = 50
    # Base price that anchors cargo extension pricing
    extend_base_cost: int = 10000
    # Number of slots added per purchase
    extend_step: int = 10
    # Pricing mode for cargo extensions: "exponential" or "linear"
    extend_pricing_mode: str = "linear"
    # Factor used by both modes; exponential = multiplier per bundle, linear = (base_cost * factor) increment per bundle
    extend_cost_factor: float = 2

