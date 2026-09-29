from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth.dependencies import get_current_user
from ..db import get_db
from ..models import Usuario
from .schemas import (
    AceiteConviteResposta,
    ConvitePublicoResposta,
    RecusaConviteResposta,
)
from .service import aceitar_convite, consultar_convite, recusar_convite


router = APIRouter(
    prefix="/invites",
    tags=["Convites"],
)


@router.get(
    "/{token}",
    response_model=ConvitePublicoResposta,
)
def consultar_convite_publico(
    token: str,
    db: Session = Depends(get_db),
):
    return consultar_convite(token, db)


@router.post(
    "/{token}/accept",
    response_model=AceiteConviteResposta,
)
def aceitar_convite_autenticado(
    token: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return aceitar_convite(token, usuario, db)


@router.post(
    "/{token}/reject",
    response_model=RecusaConviteResposta,
)
def recusar_convite_autenticado(
    token: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return recusar_convite(token, usuario, db)
