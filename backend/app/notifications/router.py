from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth.dependencies import get_current_user
from ..db import get_db
from ..models import Usuario
from .schemas import NotificationResponse, UnreadCountResponse
from .service import NotificationNotFoundError, NotificationService


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


@router.get("/unread-count", response_model=UnreadCountResponse)
def contar_notificacoes_nao_lidas(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {
        "count": NotificationService.contar_notificacoes_nao_lidas(usuario, db)
    }


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def marcar_notificacao_como_lida(
    notification_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return NotificationService.marcar_como_lida(notification_id, usuario, db)
    except NotificationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificacao nao encontrada.",
        ) from None
