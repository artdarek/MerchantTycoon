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

    # Contest Win: list of contest names with their 1st place base prizes
    # Format: [("Contest Name", base_1st_prize), ...]
    # 2nd place = base/2, 3rd place = base/4 (rounded up)
    contest_names: list[tuple[str, int]] = None
    # Contest Win: probability weights for each place [1st, 2nd, 3rd]
    contest_place_weights: list[int] = None

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

    # --- FBI confiscation configuration ---
    # Cash: keep this fraction of cash (0.25 = keep 25%, i.e., reduce by 75%)
    fbi_cash_keep_pct: float = 0.25
    # Bank: reduce balance by this fraction (1.0 = reduce by 100% to zero; 0.75 = reduce by 75%)
    fbi_bank_reduction_pct: float = 1.0
    # Inventory: if True, remove ALL goods (legal + contraband); if False, keep inventory
    fbi_remove_all_goods: bool = True
    # Cargo capacity after raid as a fraction of base capacity (1.0 = reset to base)
    fbi_cargo_capacity_pct: float = 1.0
    # FBI confiscation eligibility: minimum number of contraband lots required
    fbi_min_contraband_lots: int = 3

    # Contraband buyer scam: how many random contraband lots to remove
    contraband_scam_lots: int = 1


    def __post_init__(self):
        # Default selection weights for all travel events. Handlers may still
        # use their internal defaults if they don't consult this map.
        object.__setattr__(self, "weights", self.weights or {
            # Loss events
            "robbery": 8,
            "fire": 5,
            "flood": 4,
            "defective_batch": 5,
            "customs_duty": 6,
            "stolen_last_buy": 5,
            "cash_damage": 4,
            "portfolio_crash": 3,
            "lotto_ticket_lost": 4,
            "contraband_buyer_scam": 6,
            "fbi_confiscation": 2,

            # Gain events
            "dividend": 6,
            "contest_win": 3,
            "bank_correction": 4,
            "portfolio_boom": 3,

            # Neutral events
            "promo": 5,
            "oversupply": 4,
            "shortage": 4,
            "loyal_discount": 1,
            "market_boom": 8,
            "market_crash": 8,
        })
        object.__setattr__(self, "contest_names", self.contest_names or [
            ("International Sandwich Championship", 1000),
            ("World Pillow Fighting Cup", 2000),
            ("National Speed Napping Finals", 3000),
            ("Intergalactic Beard Grooming Show", 1500),
            ("Extreme Ironing Masters", 2500),
            ("Professional Duck Herding Competition", 1200),
            ("Global Air Guitar Championship", 1800),
            ("Underground Sock Sorting League", 800),
            ("Elite Backwards Running Marathon", 2200),
            ("International Paper Airplane Distance Cup", 1000),
        ])
        object.__setattr__(self, "contest_place_weights", self.contest_place_weights or [10, 30, 60])
