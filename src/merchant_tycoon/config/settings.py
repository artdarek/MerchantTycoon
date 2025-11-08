from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TravelSettings:
    base_fee: int = 100
    fee_per_cargo_unit: int = 1


@dataclass(frozen=True)
class CargoSettings:
    base_capacity: int = 50
    extend_base_cost: int = 100
    extend_cost_factor: int = 2
    extend_step: int = 10  # number of slots added per purchase


@dataclass(frozen=True)
class PricingSettings:
    min_unit_price: int = 1
    history_window: int = 10


@dataclass(frozen=True)
class BankSettings:
    bank_apr_range: tuple[float, float] = (0.01, 0.03)
    bank_default_apr: float = 0.02
    loan_apr_range: tuple[float, float] = (0.01, 0.20)
    loan_default_apr: float = 0.10
    loan_max_amount: int = 10_000
    loan_base_commission_rate: float = 0.10
    loan_high_commission_rate: float = 0.30
    loan_high_commission_threshold: int = 10


@dataclass(frozen=True)
class EventsSettings:
    base_probability: float = 0.25
    # Weights per event key used internally
    weights: dict[str, float] = None  # filled in __post_init__
    # Ranges / parameters
    robbery_loss_pct: tuple[float, float] = (0.10, 0.40)
    fire_total_pct: tuple[float, float] = (0.20, 0.60)
    fire_per_good_pct: tuple[float, float] = (0.20, 0.60)
    flood_total_pct: tuple[float, float] = (0.30, 0.80)
    flood_per_good_pct: tuple[float, float] = (0.30, 0.80)
    customs_duty_pct: tuple[float, float] = (0.05, 0.15)
    cash_damage_pct: tuple[float, float] = (0.01, 0.05)
    cash_damage_min: int = 50
    cash_damage_max: int = 2000
    dividend_pct: tuple[float, float] = (0.005, 0.02)
    lottery_tiers: list[int] = None  # [3,4,5,6]
    lottery_weights: list[int] = None  # [50,30,15,5]
    lottery_reward_ranges: dict[int, tuple[int, int]] = None  # {3:(200,600),...}
    bank_correction_pct: tuple[float, float] = (0.01, 0.05)
    bank_correction_min: int = 10
    promo_multiplier: tuple[float, float] = (0.4, 0.7)
    oversupply_multiplier: tuple[float, float] = (0.3, 0.6)
    shortage_multiplier: tuple[float, float] = (1.8, 2.2)
    loyal_discount_multiplier: float = 0.05

    def __post_init__(self):
        object.__setattr__(self, "weights", self.weights or {
            "robbery": 8,
            "fire": 5,
            "flood": 4,
            "defective_batch": 5,
            "customs_duty": 6,
            "stolen_last_buy": 5,
            "cash_damage": 4,
            "dividend": 6,
            "lottery": 3,
            "bank_correction": 4,
            "promo": 5,
            "oversupply": 4,
            "shortage": 4,
            "loyal_discount": 1,
        })
        object.__setattr__(self, "lottery_tiers", self.lottery_tiers or [3, 4, 5, 6])
        object.__setattr__(self, "lottery_weights", self.lottery_weights or [50, 30, 15, 5])
        object.__setattr__(self, "lottery_reward_ranges", self.lottery_reward_ranges or {
            3: (200, 600),
            4: (700, 1500),
            5: (2000, 6000),
            6: (10_000, 30_000),
        })


@dataclass(frozen=True)
class InvestmentsSettings:
    min_unit_price: int = 1  # reuse pricing.min_unit_price by default
    variance_scale: float = 1.0


@dataclass(frozen=True)
class SaveUiSettings:
    save_dir_name: str = ".merchant_tycoon"
    messages_save_limit: int = 100
    bank_transactions_limit: int = 100


@dataclass(frozen=True)
class GameSettings:
    start_cash: int = 500000000
    start_date: str = "2025-01-01"  # ISO YYYY-MM-DD


@dataclass(frozen=True)
class Settings:
    travel: TravelSettings = TravelSettings()
    cargo: CargoSettings = CargoSettings()
    pricing: PricingSettings = PricingSettings()
    bank: BankSettings = BankSettings()
    events: EventsSettings = EventsSettings()
    investments: InvestmentsSettings = InvestmentsSettings()
    saveui: SaveUiSettings = SaveUiSettings()
    game: GameSettings = GameSettings()


SETTINGS = Settings()
