from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth.dependencies import get_current_user
from ..db import get_db
from ..models import Usuario
from .schemas import NotificationResponse
from .service import NotificationService


router = APIRouter(
    prefix="/notifications",
    tags=["Notificacoes"],
)


@router.get("", response_model=list[NotificationResponse])
def listar_notificacoes(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return NotificationService.listar_notificacoes_do_usuario(usuario, db)
