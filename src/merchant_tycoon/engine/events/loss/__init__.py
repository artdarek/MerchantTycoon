"""Loss events - negative events that cost player resources."""

from merchant_tycoon.engine.events.loss.robbery_event import RobberyEventHandler
from merchant_tycoon.engine.events.loss.fire_event import FireEventHandler
from merchant_tycoon.engine.events.loss.flood_event import FloodEventHandler
from merchant_tycoon.engine.events.loss.defective_batch_event import DefectiveBatchEventHandler
from merchant_tycoon.engine.events.loss.customs_duty_event import CustomsDutyEventHandler
from merchant_tycoon.engine.events.loss.stolen_goods_event import StolenGoodsEventHandler
from merchant_tycoon.engine.events.loss.cash_damage_event import CashDamageEventHandler
from merchant_tycoon.engine.events.loss.portfolio_crash_event import PortfolioCrashEventHandler
from merchant_tycoon.engine.events.loss.lotto_ticket_lost_event import LottoTicketLostEventHandler
from merchant_tycoon.engine.events.loss.contraband_buyer_scam_event import ContrabandBuyerScamEventHandler
from merchant_tycoon.engine.events.loss.fbi_confiscation_event import FBIConfiscationEventHandler

__all__ = [
    "RobberyEventHandler",
    "FireEventHandler",
    "FloodEventHandler",
    "DefectiveBatchEventHandler",
    "CustomsDutyEventHandler",
    "StolenGoodsEventHandler",
    "CashDamageEventHandler",
    "PortfolioCrashEventHandler",
    "LottoTicketLostEventHandler",
    "ContrabandBuyerScamEventHandler",
    "FBIConfiscationEventHandler",
]
