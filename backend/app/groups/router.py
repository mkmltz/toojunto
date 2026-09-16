from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..auth.dependencies import get_current_user
from ..db import get_db
from ..models import Usuario
from .schemas import GrupoCriacao, GrupoResposta
from .service import criar_grupo


router = APIRouter(
    prefix="/groups",
    tags=["Grupos"],
)


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
