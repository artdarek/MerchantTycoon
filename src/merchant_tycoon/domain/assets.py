"""Domain constant: All investable financial assets in the game.

This module defines the complete catalog of stocks, commodities, and cryptocurrencies
available for investment. Unlike goods, assets are protected from random events and
provide long-term wealth building through market volatility.

Constants:
    ASSETS: List of all 32 investable financial assets with base prices and volatility.
        Filter by asset_type ('stock' | 'commodity' | 'crypto') for specific asset classes.
        Used by InvestmentsService for price generation and portfolio management.

Asset Types:
    - stocks: 16 company equities (GOOGL, AAPL, NVDA, TSLA, CDR, NTD, etc.)
        Volatility: ±40-90%, medium to high risk
        Price range: $80-$250 per share
    - commodities: 8 physical resources (Gold, Oil, Silver, Copper, Platinum, etc.)
        Volatility: ±30-80%, medium risk
        Price range: $8-$2500 per unit
    - crypto: 8 cryptocurrencies (BTC, ETH, SOL, DOGE, AVAX, DOT, etc.)
        Volatility: ±70-100%, extreme risk/reward
        Price range: $1-$35,000 per coin

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

# All investable financial assets (32 total: 16 stocks, 8 commodities, 8 crypto)
# Filter by asset_type: 'stock' | 'commodity' | 'crypto'
# Dividend rates: stocks typically 0.001-0.01 (0.1%-1.0%), commodities/crypto = 0.0
ASSETS: List[Asset] = [
    # Stocks - Tech Giants (dividend rates: 0.001-0.005 = 0.1%-0.5%)
    Asset("Google", "GOOGL", 150, 0.6, "stock", 0.002),
    Asset("Meta", "META", 80, 0.5, "stock", 0.001),
    Asset("Apple", "AAPL", 120, 0.7, "stock", 0.003),
    Asset("Microsoft", "MSFT", 200, 0.4, "stock", 0.004),
    Asset("Amazon", "AMZN", 180, 0.6, "stock", 0.001),
    Asset("Netflix", "NFLX", 90, 0.8, "stock", 0.002),
    Asset("NVIDIA", "NVDA", 250, 0.9, "stock", 0.001),
    Asset("Tesla", "TSLA", 160, 0.8, "stock", 0.001),
    Asset("AMD", "AMD", 110, 0.7, "stock", 0.002),
    Asset("Oracle", "ORCL", 95, 0.5, "stock", 0.005),
    Asset("Adobe", "ADBE", 140, 0.6, "stock", 0.003),
    Asset("Intel", "INTC", 85, 0.6, "stock", 0.004),
    # Stocks - Gaming Companies (dividend rates: 0.002-0.005 = 0.2%-0.5%)
    Asset("CD Projekt Red", "CDR", 100, 0.7, "stock", 0.003),
    Asset("Nintendo", "NTD", 130, 0.6, "stock", 0.004),
    Asset("Ubisoft", "UBI", 85, 0.7, "stock", 0.002),
    Asset("Electronic Arts", "EAA", 125, 0.6, "stock", 0.003),
    # Commodities - Precious Metals (no dividends)
    Asset("Gold", "GOLD", 1800, 0.3, "commodity", 0.0),
    Asset("Silver", "SILV", 25, 0.4, "commodity", 0.0),
    Asset("Platinum", "PLT", 950, 0.35, "commodity", 0.0),
    Asset("Copper", "COPP", 8, 0.5, "commodity", 0.0),
    # Commodities - Energy & Agriculture (no dividends)
    Asset("Oil", "OIL", 75, 0.8, "commodity", 0.0),
    Asset("Cocoa", "COC", 2500, 0.5, "commodity", 0.0),
    Asset("Sugar", "SGR", 400, 0.6, "commodity", 0.0),
    Asset("Coffee", "CFE", 150, 0.7, "commodity", 0.0),
    # Crypto - Major Coins (no dividends)
    Asset("Bitcoin", "BTC", 35000, 0.7, "crypto", 0.0),
    Asset("Ethereum", "ETH", 2000, 0.8, "crypto", 0.0),
    Asset("Solana", "SOL", 80, 0.9, "crypto", 0.0),
    Asset("Dogecoin", "DOGE", 5, 1.0, "crypto", 0.0),
    # Crypto - Altcoins (no dividends)
    Asset("Avalanche", "AVAX", 35, 0.85, "crypto", 0.0),
    Asset("Polkadot", "DOT", 7, 0.9, "crypto", 0.0),
    Asset("Decentraland", "MANA", 2, 0.95, "crypto", 0.0),
    Asset("1inch", "1INCH", 3, 1.0, "crypto", 0.0),
]