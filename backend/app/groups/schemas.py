from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class GrupoCriacao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nome: str = Field(min_length=2, max_length=120)
    valor_cota: Decimal = Field(gt=0, decimal_places=2)
    quantidade_participantes: int = Field(ge=2)
    quantidade_ciclos: int = Field(ge=2)
    data_inicio: date

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, nome: str) -> str:
        nome = nome.strip()
        if len(nome) < 2:
            raise ValueError("O nome deve ter pelo menos 2 caracteres.")
        return nome

    @field_validator("data_inicio")
    @classmethod
    def validar_data_inicio(cls, data_inicio: date) -> date:
        if data_inicio < date.today():
            raise ValueError("A data de início não pode estar no passado.")
        return data_inicio

    @model_validator(mode="after")
    def validar_quantidade_ciclos(self):
        if self.quantidade_ciclos != self.quantidade_participantes:
            raise ValueError(
                "A quantidade de ciclos deve ser igual à quantidade de participantes."
            )
        return self


class GrupoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    gestor_id: int
    valor_cota: Decimal
    valor_premio: Decimal
    quantidade_participantes: int
    quantidade_ciclos: int
    data_inicio: date
    status: str
    created_at: datetime
