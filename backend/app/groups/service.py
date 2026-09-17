from datetime import datetime, time

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Grupo, Participante, Usuario
from .schemas import (
    GrupoAtualizacao,
    GrupoComPapelResposta,
    GrupoCriacao,
    GrupoResposta,
    PapelGrupo,
)


def criar_grupo(
    dados: GrupoCriacao,
    gestor: Usuario,
    db: Session,
) -> Grupo:
    grupo = Grupo(
        nome=dados.nome,
        gestor_id=gestor.id,
        valor_cota=dados.valor_cota,
        valor_premio=dados.valor_cota * dados.quantidade_participantes,
        quantidade_participantes=dados.quantidade_participantes,
        quantidade_ciclos=dados.quantidade_ciclos,
        data_inicio=datetime.combine(dados.data_inicio, time.min),
        status="RASCUNHO",
    )

    try:
        db.add(grupo)
        db.flush()
        db.add(
            Participante(
                grupo_id=grupo.id,
                usuario_id=gestor.id,
                ordem_sorteio=None,
                status="ATIVO",
            )
        )
        db.commit()
        db.refresh(grupo)
    except Exception:
        db.rollback()
        raise

    return grupo


def _grupo_com_papel(
    grupo: Grupo,
    usuario: Usuario,
) -> GrupoComPapelResposta:
    papel = (
        PapelGrupo.GESTOR
        if grupo.gestor_id == usuario.id
        else PapelGrupo.PARTICIPANTE
    )
    dados_grupo = GrupoResposta.model_validate(grupo).model_dump()
    return GrupoComPapelResposta(**dados_grupo, papel=papel)


def listar_grupos_do_usuario(
    usuario: Usuario,
    db: Session,
) -> list[GrupoComPapelResposta]:
    participacao_ativa = (
        select(Participante.id)
        .where(
            Participante.grupo_id == Grupo.id,
            Participante.usuario_id == usuario.id,
            Participante.status == "ATIVO",
        )
        .exists()
    )
    grupos = db.scalars(
        select(Grupo)
        .where(participacao_ativa)
        .order_by(Grupo.created_at.desc(), Grupo.id.desc())
    ).all()
    return [_grupo_com_papel(grupo, usuario) for grupo in grupos]


def obter_grupo_do_usuario(
    grupo_id: int,
    usuario: Usuario,
    db: Session,
) -> GrupoComPapelResposta:
    participacao_ativa = (
        select(Participante.id)
        .where(
            Participante.grupo_id == Grupo.id,
            Participante.usuario_id == usuario.id,
            Participante.status == "ATIVO",
        )
        .exists()
    )
    grupo = db.scalar(
        select(Grupo).where(
            Grupo.id == grupo_id,
            participacao_ativa,
        )
    )
    if grupo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo não encontrado.",
        )
    return _grupo_com_papel(grupo, usuario)


def _buscar_grupo_gerenciavel(
    grupo_id: int,
    gestor: Usuario,
    db: Session,
) -> Grupo:
    grupo = db.scalar(
        select(Grupo).where(Grupo.id == grupo_id).with_for_update()
    )

    if grupo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo não encontrado.",
        )

    if grupo.gestor_id != gestor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Somente o gestor proprietário pode gerenciar o grupo.",
        )

    if grupo.status != "RASCUNHO":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Somente grupos em RASCUNHO podem ser gerenciados.",
        )

    return grupo


def atualizar_grupo(
    grupo_id: int,
    dados: GrupoAtualizacao,
    gestor: Usuario,
    db: Session,
) -> Grupo:
    grupo = _buscar_grupo_gerenciavel(grupo_id, gestor, db)
    alteracoes = dados.model_dump(exclude_unset=True)

    nova_quantidade = alteracoes.get(
        "quantidade_participantes",
        grupo.quantidade_participantes,
    )
    quantidade_associada = db.scalar(
        select(func.count(Participante.id)).where(
            Participante.grupo_id == grupo.id
        )
    )
    if nova_quantidade < quantidade_associada:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A quantidade de participantes não pode ser menor que a "
                "quantidade já associada ao grupo."
            ),
        )

    try:
        if "nome" in alteracoes:
            grupo.nome = alteracoes["nome"]
        if "valor_cota" in alteracoes:
            grupo.valor_cota = alteracoes["valor_cota"]
        if "quantidade_participantes" in alteracoes:
            grupo.quantidade_participantes = nova_quantidade
            grupo.quantidade_ciclos = nova_quantidade
        if "data_inicio" in alteracoes:
            grupo.data_inicio = datetime.combine(
                alteracoes["data_inicio"],
                time.min,
            )

        grupo.valor_premio = (
            grupo.valor_cota * grupo.quantidade_participantes
        )
        db.commit()
        db.refresh(grupo)
    except Exception:
        db.rollback()
        raise

    return grupo


def cancelar_grupo(
    grupo_id: int,
    gestor: Usuario,
    db: Session,
) -> Grupo:
    grupo = _buscar_grupo_gerenciavel(grupo_id, gestor, db)

    try:
        grupo.status = "CANCELADO"
        db.commit()
        db.refresh(grupo)
    except Exception:
        db.rollback()
        raise

    return grupo
