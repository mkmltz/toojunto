from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..auth.dependencies import get_current_user
from ..db import get_db
from ..models import Usuario
from .schemas import (
    ConviteResposta,
    GrupoAtualizacao,
    GrupoComPapelResposta,
    GrupoCriacao,
    GrupoDetalheResposta,
    GrupoResposta,
)
from .service import (
    atualizar_grupo,
    cancelar_grupo,
    criar_grupo,
    gerar_ou_obter_convite,
    listar_grupos_do_usuario,
    obter_grupo_do_usuario,
)


router = APIRouter(
    prefix="/groups",
    tags=["Grupos"],
)


@router.get(
    "",
    response_model=list[GrupoComPapelResposta],
)
def listar_grupos(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return listar_grupos_do_usuario(usuario, db)


@router.get(
    "/{group_id}",
    response_model=GrupoDetalheResposta,
)
def consultar_grupo(
    group_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return obter_grupo_do_usuario(group_id, usuario, db)


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
