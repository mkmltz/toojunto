from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: str
    titulo: str
    mensagem: str
    referencia_contextual: str | None
    status: str
    created_at: datetime
    lida_em: datetime | None


class UnreadCountResponse(BaseModel):
    count: int
