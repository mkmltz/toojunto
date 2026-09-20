from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    telefone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Grupo(Base):
    __tablename__ = "grupos"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    gestor_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    valor_cota: Mapped[Decimal] = mapped_column(Numeric(12,2))
    valor_premio: Mapped[Decimal] = mapped_column(Numeric(18,2))
    quantidade_participantes: Mapped[int] = mapped_column(Integer)
    quantidade_ciclos: Mapped[int] = mapped_column(Integer)
    data_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="RASCUNHO")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Convite(Base):
    __tablename__ = "convites"
    id: Mapped[int] = mapped_column(primary_key=True)
    grupo_id: Mapped[int] = mapped_column(
        ForeignKey("grupos.id"), unique=True, index=True
    )
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Participante(Base):
    __tablename__ = "participantes"
    id: Mapped[int] = mapped_column(primary_key=True)
    grupo_id: Mapped[int] = mapped_column(ForeignKey("grupos.id"))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    ordem_sorteio: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="ATIVO")

class Ciclo(Base):
    __tablename__ = "ciclos"
    id: Mapped[int] = mapped_column(primary_key=True)
    grupo_id: Mapped[int] = mapped_column(ForeignKey("grupos.id"))
    numero: Mapped[int] = mapped_column(Integer)
    data: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    contemplado_id: Mapped[int | None] = mapped_column(ForeignKey("participantes.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="ABERTO")

class Pagamento(Base):
    __tablename__ = "pagamentos"
    id: Mapped[int] = mapped_column(primary_key=True)
    ciclo_id: Mapped[int] = mapped_column(ForeignKey("ciclos.id"))
    pagador_id: Mapped[int] = mapped_column(ForeignKey("participantes.id"))
    recebedor_id: Mapped[int] = mapped_column(ForeignKey("participantes.id"))
    valor: Mapped[float] = mapped_column(Numeric(12,2))
    status: Mapped[str] = mapped_column(String(30), default="PENDENTE")
    comprovante: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_pagamento: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

class Contemplacao(Base):
    __tablename__ = "contemplacoes"
    id: Mapped[int] = mapped_column(primary_key=True)
    ciclo_id: Mapped[int] = mapped_column(ForeignKey("ciclos.id"))
    participante_id: Mapped[int] = mapped_column(ForeignKey("participantes.id"))
    valor: Mapped[float] = mapped_column(Numeric(12,2))
    status: Mapped[str] = mapped_column(String(30), default="REGISTRADA")
    data: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
