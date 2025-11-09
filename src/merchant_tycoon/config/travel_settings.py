from dataclasses import dataclass


@dataclass(frozen=True)
class TravelSettings:
    # Base travel fee charged for any trip
    base_fee: int = 100
    # Extra fee per cargo unit carried (scales with inventory size)
    fee_per_cargo_unit: int = 1

