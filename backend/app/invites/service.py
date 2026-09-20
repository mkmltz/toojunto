from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Convite, Grupo, Participante, Usuario
from .schemas import AceiteConviteResposta, ConvitePublicoResposta


def _convite_indisponivel() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Convite não encontrado ou indisponível.",
    )


def _quantidade_associada(grupo_id: int, db: Session) -> int:
    return db.scalar(
        select(func.count(Participante.id)).where(
            Participante.grupo_id == grupo_id
        )
    ) or 0


def consultar_convite(
    token: str,
    db: Session,
) -> ConvitePublicoResposta:
    grupo = db.scalar(
        select(Grupo)
        .join(Convite, Convite.grupo_id == Grupo.id)
        .where(Convite.token == token)
    )
    if grupo is None or grupo.status != "RASCUNHO":
        raise _convite_indisponivel()

    quantidade_associada = _quantidade_associada(grupo.id, db)
    vagas_disponiveis = grupo.quantidade_participantes - quantidade_associada
    if vagas_disponiveis <= 0:
        raise _convite_indisponivel()

    return ConvitePublicoResposta(
        group_name=grupo.nome,
        quota_value=grupo.valor_cota,
        participant_limit=grupo.quantidade_participantes,
        available_slots=vagas_disponiveis,
        start_date=grupo.data_inicio.date(),
    )


def aceitar_convite(
    token: str,
    usuario: Usuario,
    db: Session,
) -> AceiteConviteResposta:
    grupo = db.scalar(
        select(Grupo)
        .join(Convite, Convite.grupo_id == Grupo.id)
        .where(Convite.token == token)
        .with_for_update(of=Grupo)
    )
    if grupo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Convite não encontrado.",
        )

    if grupo.status != "RASCUNHO":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este Grupo não permite mais entradas.",
        )

    participacao_existente = db.scalar(
        select(Participante).where(
            Participante.grupo_id == grupo.id,
            Participante.usuario_id == usuario.id,
        )
    )
    if grupo.gestor_id == usuario.id or participacao_existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Você já participa deste Grupo.",
        )

    if _quantidade_associada(grupo.id, db) >= grupo.quantidade_participantes:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este Grupo não possui vagas disponíveis.",
        )

    participante = Participante(
        grupo_id=grupo.id,
        usuario_id=usuario.id,
        ordem_sorteio=None,
        status="ATIVO",
    )
    try:
        db.add(participante)
        db.commit()
        db.refresh(participante)
    except Exception:
        db.rollback()
        raise

    return AceiteConviteResposta(
        group_id=participante.grupo_id,
        participant_id=participante.id,
        status=participante.status,
    )
