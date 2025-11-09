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
    # Commission rate for opening a loan (base tier)
    loan_base_commission_rate: float = 0.10
    # Higher commission rate for large number of loans
    loan_high_commission_rate: float = 0.30
    # Threshold (loan count) after which high commission applies
    loan_high_commission_threshold: int = 10

    # ---- Credit capacity config ----
    # Enable credit capacity checks (limits total debt by wealth)
    credit_enabled: bool = True
    # Total debt cap = wealth * leverage_factor + base_allowance
    credit_leverage_factor: float = 0.8
    credit_base_allowance: int = 1000
    # Haircuts applied to valuation when computing credit wealth
    # Cash haircut reduces the weight of on-hand cash in credit capacity
    credit_haircut_cash: float = 0.1
    credit_haircut_stock: float = 0.5
    credit_haircut_commodity: float = 0.7
    credit_haircut_crypto: float = 0.2
