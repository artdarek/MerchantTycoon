from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from merchant_tycoon.engine.services.clock_service import ClockService
    from merchant_tycoon.engine.services.bank_service import BankService
    from merchant_tycoon.engine.services.investments_service import InvestmentsService
    from merchant_tycoon.engine.services.goods_service import GoodsService


class DayAdvanceService:
    """Encapsulates end-of-day progression effects.

    This service advances the in-game day and applies all cross-cutting
    systems that tick daily (interest, price generation, holdings age).
    It lets TravelService focus purely on travel logic.
    """

    def __init__(
        self,
        clock_service: "ClockService",
        bank_service: "BankService",
        investments_service: "InvestmentsService",
        goods_service: "GoodsService",
    ) -> None:
        self.clock_service = clock_service
        self.bank_service = bank_service
        self.investments_service = investments_service
        self.goods_service = goods_service

    def advance_day(self) -> None:
        """Advance the in-game day and update dependent systems."""
        # Advance calendar/day
        self.clock_service.advance_day()

        # Randomize daily loan APR offer
        try:
            self.bank_service.randomize_daily_rates()
        except Exception:
            pass

        # Accrue interest on loans and bank account
        try:
            self.bank_service.accrue_loan_interest()
        except Exception:
            pass
        try:
            self.bank_service.accrue_bank_interest()
        except Exception:
            pass

        # Age investment lots for dividend eligibility
        try:
            self.investments_service.increment_lot_holding_days()
        except Exception:
            pass

        # Generate new daily prices for goods and assets
        try:
            self.goods_service.generate_prices()
        except Exception:
            pass
        try:
            self.investments_service.generate_asset_prices()
        except Exception:
            pass
