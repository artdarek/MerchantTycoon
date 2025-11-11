"""Domain constant: All investable financial assets in the game.

This module defines the complete catalog of stocks, commodities, and cryptocurrencies
available for investment. Unlike goods, assets are protected from random events and
provide long-term wealth building through market volatility.

Constants:
    ASSETS: List of all 20 investable financial assets with base prices and volatility.
        Filter by asset_type ('stock' | 'commodity' | 'crypto') for specific asset classes.
        Used by InvestmentsService for price generation and portfolio management.

Asset Types:
    - stocks: 12 company equities (GOOGL, AAPL, NVDA, TSLA, etc.)
        Volatility: ±40-90%, medium to high risk
        Price range: $80-$250 per share
    - commodities: 4 physical resources (Gold, Oil, Silver, Copper)
        Volatility: ±30-80%, medium risk
        Price range: $8-$1800 per unit
    - crypto: 4 cryptocurrencies (BTC, ETH, SOL, DOGE)
        Volatility: ±70-100%, extreme risk/reward
        Price range: $5-$35,000 per coin

Investment Benefits:
    - Immune to random events (fire, theft, robbery)
    - Daily price changes with market volatility
    - FIFO accounting for profit/loss tracking
    - Buy/sell commission fees apply

Examples:
    >>> from merchant_tycoon.domain.assets import ASSETS
    >>> stocks = [a for a in ASSETS if a.asset_type == "stock"]
    >>> crypto = [a for a in ASSETS if a.asset_type == "crypto"]
    >>> # Find most volatile asset
    >>> risky = max(ASSETS, key=lambda a: a.price_variance)
    >>> # Find asset by symbol
    >>> btc = [a for a in ASSETS if a.symbol == "BTC"][0]

See Also:
    - Asset: Domain model representing a single financial asset
    - InvestmentsService: Business logic for buying/selling and price management
    - InvestmentLot: Tracks individual asset purchase batches
"""
from __future__ import annotations
from typing import List

from merchant_tycoon.domain.model.asset import Asset

# All investable financial assets (20 total: 12 stocks, 4 commodities, 4 crypto)
# Filter by asset_type: 'stock' | 'commodity' | 'crypto'
ASSETS: List[Asset] = [
    # Stocks
    Asset("Google", "GOOGL", 150, 0.6, "stock"),
    Asset("Meta", "META", 80, 0.5, "stock"),
    Asset("Apple", "AAPL", 120, 0.7, "stock"),
    Asset("Microsoft", "MSFT", 200, 0.4, "stock"),
    Asset("Amazon", "AMZN", 180, 0.6, "stock"),
    Asset("Netflix", "NFLX", 90, 0.8, "stock"),
    Asset("NVIDIA", "NVDA", 250, 0.9, "stock"),
    Asset("Tesla", "TSLA", 160, 0.8, "stock"),
    Asset("AMD", "AMD", 110, 0.7, "stock"),
    Asset("Oracle", "ORCL", 95, 0.5, "stock"),
    Asset("Adobe", "ADBE", 140, 0.6, "stock"),
    Asset("Intel", "INTC", 85, 0.6, "stock"),
    # Commodities
    Asset("Gold", "GOLD", 1800, 0.3, "commodity"),
    Asset("Oil", "OIL", 75, 0.8, "commodity"),
    Asset("Silver", "SILV", 25, 0.4, "commodity"),
    Asset("Copper", "COPP", 8, 0.5, "commodity"),
    # Crypto
    Asset("Bitcoin", "BTC", 35000, 0.7, "crypto"),
    Asset("Ethereum", "ETH", 2000, 0.8, "crypto"),
    Asset("Solana", "SOL", 80, 0.9, "crypto"),
    Asset("Dogecoin", "DOGE", 5, 1.0, "crypto"),  # Price range $1-$10 (base 5, variance 1.0)
]