from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.orm import Session

from ..auth.dependencies import get_current_user
from ..db import get_db
from ..models import Usuario
from .schemas import (
    ConviteResposta,
    GrupoAtualizacao,
    GrupoCriacao,
    GrupoDetalheResposta,
    GrupoListaResposta,
    GrupoResposta,
    ProgressoGrupoResposta,
    ObrigacaoPagamentoResposta,
    DeclaracaoPagamento,
)
from .service import (
    atualizar_grupo,
    cancelar_grupo,
    criar_grupo,
    gerar_ou_obter_convite,
    listar_grupos_do_usuario,
    obter_grupo_do_usuario,
    obter_progresso_grupo,
    listar_obrigacoes_pagamento,
    declarar_pagamento,
    preparar_sorteio,
    realizar_sorteio,
)


router = APIRouter(
    prefix="/groups",
    tags=["Grupos"],
)


@router.get(
    "",
    response_model=list[GrupoListaResposta],
)
def listar_grupos(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return listar_grupos_do_usuario(usuario, db)


@router.get(
    "/{group_id}",
    response_model=GrupoDetalheResposta,
    response_model_exclude_none=True,
)
def consultar_grupo(
    group_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return obter_grupo_do_usuario(group_id, usuario, db)


@router.get("/{group_id}/cycles", response_model=ProgressoGrupoResposta)
def consultar_ciclos(
    group_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return obter_progresso_grupo(group_id, usuario, db)


@router.get(
    "/{group_id}/cycles/{cycle_number}/payments",
    response_model=list[ObrigacaoPagamentoResposta],
)
def consultar_obrigacoes_do_ciclo(
    group_id: int,
    cycle_number: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return listar_obrigacoes_pagamento(group_id, cycle_number, usuario, db)


@router.post(
    "/{group_id}/cycles/{cycle_number}/payments",
    response_model=ObrigacaoPagamentoResposta,
    status_code=status.HTTP_201_CREATED,
)
def registrar_pagamento_do_ciclo(
    group_id: int,
    cycle_number: int,
    dados: DeclaracaoPagamento = Body(default_factory=DeclaracaoPagamento),
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return declarar_pagamento(group_id, cycle_number, usuario, db)


@router.post(
    "",
    response_model=GrupoResposta,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_grupo(
    dados: GrupoCriacao,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return criar_grupo(dados, usuario, db)


@router.patch(
    "/{group_id}",
    response_model=GrupoResposta,
)
def editar_grupo(
    group_id: int,
    dados: GrupoAtualizacao,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return atualizar_grupo(group_id, dados, usuario, db)


@router.post(
    "/{group_id}/cancel",
    response_model=GrupoResposta,
)
def cancelar_grupo_em_rascunho(
    group_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return cancelar_grupo(group_id, usuario, db)


@router.post(
    "/{group_id}/invite",
    response_model=ConviteResposta,
)
def criar_ou_consultar_convite(
    group_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return gerar_ou_obter_convite(group_id, usuario, db)


@router.post(
    "/{group_id}/prepare-draw",
    response_model=GrupoResposta,
)
def preparar_sorteio_do_grupo(
    group_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return preparar_sorteio(group_id, usuario, db)


@router.post(
    "/{group_id}/draw",
    response_model=GrupoDetalheResposta,
    response_model_exclude_none=True,
)
def sortear_grupo(
    group_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    realizar_sorteio(group_id, usuario, db)
    return obter_grupo_do_usuario(group_id, usuario, db)
