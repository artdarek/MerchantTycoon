#!/usr/bin/env python3
"""
Compatibility wrapper for Merchant Tycoon app.

Stage 4 (Option B): keep this file as a thin wrapper that re-exports
MerchantTycoon and main() from app.py so existing entry points/imports
continue to work.
"""
from merchant_tycoon.app import main

if __name__ == "__main__":
    main()
