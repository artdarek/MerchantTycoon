from dataclasses import dataclass


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

