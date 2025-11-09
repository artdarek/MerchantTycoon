from dataclasses import dataclass


@dataclass(frozen=True)
class PricingSettings:
    # Minimum allowed unit price across generators (floor)
    min_unit_price: int = 1
    # Rolling history window size for price charts (entries per item)
    history_window: int = 10

