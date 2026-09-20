from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class ConvitePublicoResposta(BaseModel):
    group_name: str
    quota_value: Decimal
    participant_limit: int
    available_slots: int
    start_date: date


class AceiteConviteResposta(BaseModel):
    group_id: int
    participant_id: int
    status: str
