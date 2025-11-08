"""Module entry point: `python -m merchant_tycoon` runs the app."""

from merchant_tycoon.app import MerchantTycoon


def main() -> None:
    app = MerchantTycoon()
    app.run()

if __name__ == "__main__":
    main()
