from dataclasses import dataclass


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
    # Dividend payout interval in days (0 = disabled)
    dividend_interval_days: int = 11
    # Minimum holding period in days to qualify for dividends
    dividend_min_holding_days: int = 10
    # Minimum total wealth required to unlock investment trading (0 = no limit, always unlocked)
    # Wealth = cash + bank_balance + portfolio_value (gross, excluding debt)
    min_wealth_to_unlock_trading: int = 60000

