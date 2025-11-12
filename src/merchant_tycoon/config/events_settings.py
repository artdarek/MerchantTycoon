from dataclasses import dataclass


@dataclass(frozen=True)
class EventsSettings:
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

