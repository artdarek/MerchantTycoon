from __future__ import annotations

from dataclasses import dataclass
from .travel_settings import TravelSettings
from .cargo_settings import CargoSettings
from .pricing_settings import PricingSettings
from .bank_settings import BankSettings
from .events_settings import EventsSettings
from .investments_settings import InvestmentsSettings
from .save_ui_settings import SaveUiSettings
from .game_settings import GameSettings


@dataclass(frozen=True)
class Settings:
    travel: TravelSettings = TravelSettings()
    cargo: CargoSettings = CargoSettings()
    pricing: PricingSettings = PricingSettings()
    bank: BankSettings = BankSettings()
    events: EventsSettings = EventsSettings()
    investments: InvestmentsSettings = InvestmentsSettings()
    saveui: SaveUiSettings = SaveUiSettings()
    game: GameSettings = GameSettings()


SETTINGS = Settings()
