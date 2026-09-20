from datetime import date, datetime
from decimal import Decimal
from enum import Enum

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


class GrupoAtualizacao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nome: str | None = Field(default=None, min_length=2, max_length=120)
    valor_cota: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    quantidade_participantes: int | None = Field(default=None, ge=2)
    data_inicio: date | None = None

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, nome: str | None) -> str:
        if nome is None:
            raise ValueError("O nome não pode ser nulo.")
        nome = nome.strip()
        if len(nome) < 2:
            raise ValueError("O nome deve ter pelo menos 2 caracteres.")
        return nome

    @field_validator("valor_cota", "quantidade_participantes")
    @classmethod
    def validar_campo_nao_nulo(cls, valor):
        if valor is None:
            raise ValueError("O campo não pode ser nulo.")
        return valor

    @field_validator("data_inicio")
    @classmethod
    def validar_data_inicio(cls, data_inicio: date | None) -> date:
        if data_inicio is None:
            raise ValueError("A data de início não pode ser nula.")
        if data_inicio < date.today():
            raise ValueError("A data de início não pode estar no passado.")
        return data_inicio

    @model_validator(mode="after")
    def validar_campos_informados(self):
        if not self.model_fields_set:
            raise ValueError("Informe ao menos um campo para atualização.")
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


class PapelGrupo(str, Enum):
    GESTOR = "GESTOR"
    PARTICIPANTE = "PARTICIPANTE"


class GrupoComPapelResposta(GrupoResposta):
    papel: PapelGrupo


class ConviteResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    token: str
    invite_path: str
    created_at: datetime
