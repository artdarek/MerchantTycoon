from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TravelSettings:
    # Base travel fee charged for any trip
    base_fee: int = 100
    # Extra fee per cargo unit carried (scales with inventory size)
    fee_per_cargo_unit: int = 1


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
    # Unified factor used by both pricing modes:
    #  - exponential: multiplier per bundle (e.g., 1.2, 1.5, 2.0)
    #  - linear: increment per bundle = extend_base_cost * extend_cost_factor
    #    e.g., base=100, factor=1.0 -> +100 each bundle; factor=1.5 -> +150
    # Factor used by both modes; exponential = multiplier per bundle, linear = (base_cost * factor) increment per bundle
    extend_cost_factor: float = 10




@dataclass(frozen=True)
class PricingSettings:
    # Minimum allowed unit price across generators (floor)
    min_unit_price: int = 1
    # Rolling history window size for price charts (entries per item)
    history_window: int = 10


@dataclass(frozen=True)
class BankSettings:
    # Daily-offer APR range for bank savings (annualized)
    bank_apr_range: tuple[float, float] = (0.01, 0.03)
    # Fallback APR used if range not available
    bank_default_apr: float = 0.02
    # Daily-offer APR range for new loans (annualized)
    loan_apr_range: tuple[float, float] = (0.01, 0.20)
    # Fallback APR for new loans
    loan_default_apr: float = 0.10
    # Maximum principal for a single loan
    loan_max_amount: int = 10_000
    # Commission rate for opening a loan (base tier)
    loan_base_commission_rate: float = 0.10
    # Higher commission rate for large number of loans
    loan_high_commission_rate: float = 0.30
    # Threshold (loan count) after which high commission applies
    loan_high_commission_threshold: int = 10


@dataclass(frozen=True)
class EventsSettings:
    # Probability that any event occurs on travel (0–1)
    base_probability: float = 0.25
    # Event probability weights by key (filled in __post_init__)
    weights: dict[str, float] = None
    # Ranges / parameters
    # Robbery: percent range of quantity lost for a single good
    robbery_loss_pct: tuple[float, float] = (0.10, 0.40)
    # Fire: percent range of total inventory to destroy
    fire_total_pct: tuple[float, float] = (0.20, 0.60)
    # Fire: per-good share range when distributing losses
    fire_per_good_pct: tuple[float, float] = (0.20, 0.60)
    # Flood: percent range of total inventory to destroy
    flood_total_pct: tuple[float, float] = (0.30, 0.80)
    # Flood: per-good share range when distributing losses
    flood_per_good_pct: tuple[float, float] = (0.30, 0.80)
    # Customs duty: percent range of total inventory value charged as a fee
    customs_duty_pct: tuple[float, float] = (0.05, 0.15)
    # Accident: percent range of cash to lose (before min/max limits)
    cash_damage_pct: tuple[float, float] = (0.01, 0.05)
    # Accident: minimum cash loss
    cash_damage_min: int = 50
    # Accident: maximum cash loss
    cash_damage_max: int = 2000
    # Dividend: percent range of stock position value credited to bank
    dividend_pct: tuple[float, float] = (0.005, 0.02)
    # Lottery: hit tiers (e.g., [3, 4, 5, 6])
    lottery_tiers: list[int] = None
    # Lottery: probability weights per tier (e.g., [50, 30, 15, 5])
    lottery_weights: list[int] = None
    # Lottery: reward ranges per tier in dollars (e.g., {3:(200,600), ...})
    lottery_reward_ranges: dict[int, tuple[int, int]] = None
    # Bank correction: percent range of bank balance credited as interest correction
    bank_correction_pct: tuple[float, float] = (0.01, 0.05)
    # Bank correction: minimum correction amount
    bank_correction_min: int = 10
    # Promotion: price reduction multiplier for a good (next day), 0.4–0.7
    promo_multiplier: tuple[float, float] = (0.4, 0.7)
    # Oversupply: strong price drop multiplier (next day), 0.3–0.6
    oversupply_multiplier: tuple[float, float] = (0.3, 0.6)
    # Shortage: price increase multiplier (next day), ×1.8–×2.2
    shortage_multiplier: tuple[float, float] = (1.8, 2.2)
    # Loyal discount: fixed price multiplier (e.g., 0.05 = 95% discount)
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
    # Minimum unit price for assets (defaults to pricing.min_unit_price)
    min_unit_price: int = 1
    # Multiplier applied to asset variance for global tuning
    variance_scale: float = 1.0
    # Buy commission rate (fraction of trade value)
    buy_fee_rate: float = 0.001
    # Minimum buy commission in currency units
    buy_fee_min: int = 1
    # Sell commission rate (fraction of trade value)
    sell_fee_rate: float = 0.003
    # Minimum sell commission in currency units
    sell_fee_min: int = 1


@dataclass(frozen=True)
class SaveUiSettings:
    # Directory name under user home for saves
    save_dir_name: str = ".merchant_tycoon"
    # Max number of messages retained in the in-game log
    messages_save_limit: int = 100
    # Max number of bank transactions shown/saved
    bank_transactions_limit: int = 100


@dataclass(frozen=True)
class GameSettings:
    # Starting cash for a new game
    start_cash: int = 500000000
    # Start date (ISO YYYY-MM-DD)
    start_date: str = "2025-01-01"


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
