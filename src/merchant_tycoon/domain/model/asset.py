from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Asset:
    """Represents a financial investment asset (stock, commodity, or cryptocurrency).

    Assets provide an alternative investment vehicle to physical goods trading.
    Unlike goods, assets are protected from random events and provide long-term
    wealth building through market volatility and strategic trading.

    Attributes:
        name: Full company or asset name (e.g., "Google", "Bitcoin", "Gold").
        symbol: Trading ticker symbol for exchange display (e.g., "GOOGL", "BTC", "GOLD").
            Should be unique across all assets and typically 2-5 uppercase characters.
        base_price: Default market price in dollars before variance.
            Represents the baseline trading value. Examples:
            - Stocks: $80-$250 (e.g., Meta $80, NVIDIA $250)
            - Commodities: $8-$1800 (e.g., Copper $8, Gold $1800)
            - Crypto: $5-$35000 (e.g., Dogecoin $5, Bitcoin $35000)
        price_variance: Price volatility factor (0.0-1.0) controlling fluctuation amplitude.
            Higher values = more dramatic price swings:
            - Stocks: 0.4-0.9 (±40-90%, e.g., NVIDIA 0.9, Microsoft 0.4)
            - Commodities: 0.3-0.8 (±30-80%, e.g., Gold 0.3, Oil 0.8)
            - Crypto: 0.7-1.0 (±70-100%, extreme volatility)
        asset_type: Classification of the asset for filtering and display.
            Valid values:
            - "stock": Company equity (e.g., GOOGL, AAPL, TSLA)
            - "commodity": Physical resources (e.g., Gold, Oil, Silver, Copper)
            - "crypto": Cryptocurrencies (e.g., BTC, ETH, SOL, DOGE)

    Examples:
        >>> google = Asset("Google", "GOOGL", 150, 0.6, "stock")
        >>> bitcoin = Asset("Bitcoin", "BTC", 35000, 0.7, "crypto")
        >>> gold = Asset("Gold", "GOLD", 1800, 0.3, "commodity")

    Notes:
        - Assets are immune to random events (fire, theft, etc.) unlike goods
        - Price changes occur daily when traveling between cities
        - Investments use FIFO (First In, First Out) accounting for profit/loss
        - Buy/sell transactions incur commission fees (configurable)
    """
    name: str
    symbol: str
    base_price: int
    price_variance: float = 0.5  # 50% variance (more volatile than goods)
    asset_type: str = "stock"  # "stock" | "commodity" | "crypto"
