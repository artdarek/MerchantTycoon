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
ASSETS: List[Asset] = [
    # Stocks - Tech Giants
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
    # Stocks - Gaming Companies
    Asset("CD Projekt Red", "CDR", 100, 0.7, "stock"),
    Asset("Nintendo", "NTD", 130, 0.6, "stock"),
    Asset("Ubisoft", "UBI", 85, 0.7, "stock"),
    Asset("Electronic Arts", "EAA", 125, 0.6, "stock"),
    # Commodities - Precious Metals
    Asset("Gold", "GOLD", 1800, 0.3, "commodity"),
    Asset("Silver", "SILV", 25, 0.4, "commodity"),
    Asset("Platinum", "PLT", 950, 0.35, "commodity"),
    Asset("Copper", "COPP", 8, 0.5, "commodity"),
    # Commodities - Energy & Agriculture
    Asset("Oil", "OIL", 75, 0.8, "commodity"),
    Asset("Cocoa", "COC", 2500, 0.5, "commodity"),
    Asset("Sugar", "SGR", 400, 0.6, "commodity"),
    Asset("Coffee", "CFE", 150, 0.7, "commodity"),
    # Crypto - Major Coins
    Asset("Bitcoin", "BTC", 35000, 0.7, "crypto"),
    Asset("Ethereum", "ETH", 2000, 0.8, "crypto"),
    Asset("Solana", "SOL", 80, 0.9, "crypto"),
    Asset("Dogecoin", "DOGE", 5, 1.0, "crypto"),
    # Crypto - Altcoins
    Asset("Avalanche", "AVAX", 35, 0.85, "crypto"),
    Asset("Polkadot", "DOT", 7, 0.9, "crypto"),
    Asset("Decentraland", "MANA", 2, 0.95, "crypto"),
    Asset("1inch", "1INCH", 3, 1.0, "crypto"),
]