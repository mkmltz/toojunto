import secrets
from datetime import datetime, time

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import Convite, Grupo, Participante, Usuario
from .schemas import (
    ConviteResposta,
    GrupoAtualizacao,
    GrupoComPapelResposta,
    GrupoCriacao,
    GrupoDetalheResposta,
    GrupoListaResposta,
    GrupoResposta,
    FormacaoGrupoResposta,
    IntegranteGrupoResposta,
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
) -> list[GrupoListaResposta]:
    participacao_ativa = (
        select(Participante.id)
        .where(
            Participante.grupo_id == Grupo.id,
            Participante.usuario_id == usuario.id,
            Participante.status == "ATIVO",
        )
        .exists()
    )
    ocupacao = (
        select(
            Participante.grupo_id.label("grupo_id"),
            func.count(Participante.id).label("quantidade_atual"),
        )
        .group_by(Participante.grupo_id)
        .subquery()
    )
    grupos = db.execute(
        select(Grupo, func.coalesce(ocupacao.c.quantidade_atual, 0))
        .outerjoin(ocupacao, ocupacao.c.grupo_id == Grupo.id)
        .where(participacao_ativa)
        .order_by(Grupo.created_at.desc(), Grupo.id.desc())
    ).all()
    return [
        GrupoListaResposta(
            **_grupo_com_papel(grupo, usuario).model_dump(),
            vagas_disponiveis=max(
                grupo.quantidade_participantes - quantidade_atual, 0
            ),
        )
        for grupo, quantidade_atual in grupos
    ]


def obter_grupo_do_usuario(
    grupo_id: int,
    usuario: Usuario,
    db: Session,
) -> GrupoDetalheResposta:
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
    integrantes = db.execute(
        select(Participante, Usuario)
        .join(Usuario, Usuario.id == Participante.usuario_id)
        .where(Participante.grupo_id == grupo.id)
        .order_by(
            (Participante.usuario_id != grupo.gestor_id),
            Participante.id,
        )
    ).all()
    quantidade_atual = len(integrantes)
    formacao = FormacaoGrupoResposta(
        quantidade_atual=quantidade_atual,
        limite=grupo.quantidade_participantes,
        vagas_disponiveis=max(
            grupo.quantidade_participantes - quantidade_atual,
            0,
        ),
        participantes=[
            IntegranteGrupoResposta(
                nome=integrante.nome,
                papel=(
                    PapelGrupo.GESTOR
                    if integrante.id == grupo.gestor_id
                    else PapelGrupo.PARTICIPANTE
                ),
            )
            for _, integrante in integrantes
        ],
    )
    dados_grupo = _grupo_com_papel(grupo, usuario).model_dump()
    return GrupoDetalheResposta(**dados_grupo, formacao=formacao)


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


def preparar_sorteio(
    grupo_id: int,
    gestor: Usuario,
    db: Session,
) -> Grupo:
    grupo = db.scalar(
        select(Grupo).where(Grupo.id == grupo_id).with_for_update()
    )
    if grupo is None:
        raise HTTPException(status_code=404, detail="Grupo não encontrado.")
    if grupo.gestor_id != gestor.id:
        raise HTTPException(
            status_code=403,
            detail="Somente o gestor proprietário pode preparar o sorteio.",
        )
    if grupo.status != "RASCUNHO":
        raise HTTPException(
            status_code=409,
            detail="O estado do Grupo não permite preparar o sorteio.",
        )

    participantes = db.scalars(
        select(Participante).where(Participante.grupo_id == grupo.id)
    ).all()
    if (
        grupo.quantidade_participantes < 2
        or grupo.quantidade_ciclos != grupo.quantidade_participantes
        or len(participantes) != grupo.quantidade_participantes
        or len({p.usuario_id for p in participantes}) != len(participantes)
        or any(
            p.status != "ATIVO" or p.ordem_sorteio is not None
            for p in participantes
        )
        or sum(p.usuario_id == grupo.gestor_id for p in participantes) != 1
    ):
        raise HTTPException(
            status_code=409,
            detail="A formação do Grupo não está apta para o sorteio.",
        )

    try:
        grupo.status = "SORTEIO"
        db.commit()
        db.refresh(grupo)
    except Exception:
        db.rollback()
        raise
    return grupo


def gerar_ou_obter_convite(
    grupo_id: int,
    gestor: Usuario,
    db: Session,
) -> ConviteResposta:
    grupo = db.scalar(
        select(Grupo)
        .where(
            Grupo.id == grupo_id,
            Grupo.gestor_id == gestor.id,
        )
        .with_for_update()
    )
    if grupo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo não encontrado.",
        )

    if grupo.status != "RASCUNHO":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Somente grupos em RASCUNHO podem ser gerenciados.",
        )

    convite = db.scalar(
        select(Convite).where(Convite.grupo_id == grupo.id)
    )

    if convite is None:
        while convite is None:
            candidato = Convite(
                grupo_id=grupo.id,
                token=secrets.token_urlsafe(32),
            )
            try:
                with db.begin_nested():
                    db.add(candidato)
                    db.flush()
                convite = candidato
            except IntegrityError:
                convite = db.scalar(
                    select(Convite).where(Convite.grupo_id == grupo.id)
                )

        try:
            db.commit()
            db.refresh(convite)
        except Exception:
            db.rollback()
            raise

    return ConviteResposta(
        id=convite.id,
        group_id=convite.grupo_id,
        token=convite.token,
        invite_path=f"/invites/{convite.token}",
        created_at=convite.created_at,
    )
