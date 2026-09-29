from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..email import (
    EmailDeliveryPersistenceError,
    EmailService,
    ReliableEmailService,
)
from ..models import Grupo, Notificacao, Participante, Usuario
from .service import NotificationService


def _reliable_email_service() -> ReliableEmailService:
    return ReliableEmailService(EmailService(settings))


def _notify_user(
    *,
    recipient: Usuario,
    event: str,
    title: str,
    message: str,
    reference: str,
    action_label: str,
    db: Session,
) -> Notificacao:
    notification = NotificationService.criar_notificacao(
        usuario_id=recipient.id,
        tipo=event,
        titulo=title,
        mensagem=message,
        referencia_contextual=reference,
        db=db,
    )
    try:
        _reliable_email_service().enviar_e_registrar(
            destinatario=recipient.email,
            evento=event,
            assunto=title,
            titulo=title,
            mensagem=message,
            notificacao_id=notification.id,
            action_path=reference,
            action_label=action_label,
        )
    except EmailDeliveryPersistenceError:
        # The domain operation and in-app notification are already committed.
        # Delivery persistence/provider failures must not undo either one.
        pass
    return notification


def _notify_user_once(
    *,
    recipient: Usuario,
    event: str,
    title: str,
    message: str,
    reference: str,
    action_label: str,
    db: Session,
) -> Notificacao:
    existing = db.scalar(
        select(Notificacao).where(
            Notificacao.usuario_id == recipient.id,
            Notificacao.tipo == event,
            Notificacao.mensagem == message,
            Notificacao.referencia_contextual == reference,
        )
    )
    if existing is not None:
        return existing
    return _notify_user(
        recipient=recipient,
        event=event,
        title=title,
        message=message,
        reference=reference,
        action_label=action_label,
        db=db,
    )


def notificar_convite_aceito(
    grupo: Grupo,
    participante: Usuario,
    db: Session,
) -> Notificacao:
    gestor = db.get(Usuario, grupo.gestor_id)
    return _notify_user(
        recipient=gestor,
        event="CONVITE_ACEITO",
        title="Convite aceito",
        message=f"{participante.nome} entrou no grupo {grupo.nome}.",
        reference=f"/groups/{grupo.id}",
        action_label="Ver grupo",
        db=db,
    )


def notificar_convite_recusado(
    grupo: Grupo,
    convidado: Usuario,
    db: Session,
) -> Notificacao:
    gestor = db.get(Usuario, grupo.gestor_id)
    return _notify_user(
        recipient=gestor,
        event="CONVITE_RECUSADO",
        title="Convite recusado",
        message=f"{convidado.nome} recusou o convite para {grupo.nome}.",
        reference=f"/groups/{grupo.id}",
        action_label="Ver grupo",
        db=db,
    )


def notificar_grupo_completo(grupo: Grupo, db: Session) -> list[Notificacao]:
    recipients = db.scalars(
        select(Usuario)
        .join(Participante, Participante.usuario_id == Usuario.id)
        .where(Participante.grupo_id == grupo.id)
        .order_by(Usuario.id)
    ).all()
    notifications = []
    for recipient in recipients:
        action_label = (
            "Fazer sorteio" if recipient.id == grupo.gestor_id else "Ver grupo"
        )
        notifications.append(
            _notify_user(
                recipient=recipient,
                event="GRUPO_COMPLETO",
                title="Grupo completo",
                message=f"O grupo {grupo.nome} esta completo.",
                reference=f"/groups/{grupo.id}",
                action_label=action_label,
                db=db,
            )
        )
    return notifications


def notificar_sorteio_realizado(
    grupo: Grupo,
    db: Session,
) -> list[Notificacao]:
    recipients = db.scalars(
        select(Usuario)
        .join(Participante, Participante.usuario_id == Usuario.id)
        .where(Participante.grupo_id == grupo.id)
        .order_by(Usuario.id)
    ).all()
    return [
        _notify_user(
            recipient=recipient,
            event="SORTEIO_REALIZADO",
            title="Sorteio realizado",
            message=(
                f"A ordem de recebimento do grupo {grupo.nome} foi definida."
            ),
            reference=f"/groups/{grupo.id}",
            action_label="Ver grupo",
            db=db,
        )
        for recipient in recipients
    ]


def notificar_ciclo_iniciado(
    grupo: Grupo,
    numero_ciclo: int,
    db: Session,
) -> list[Notificacao]:
    recipients = db.scalars(
        select(Usuario)
        .join(Participante, Participante.usuario_id == Usuario.id)
        .where(Participante.grupo_id == grupo.id)
        .order_by(Usuario.id)
    ).all()
    return [
        _notify_user(
            recipient=recipient,
            event="CICLO_INICIADO",
            title="Novo ciclo iniciado",
            message=f"O ciclo {numero_ciclo} do grupo {grupo.nome} foi iniciado.",
            reference=f"/groups/{grupo.id}",
            action_label="Ver grupo",
            db=db,
        )
        for recipient in recipients
    ]


def notificar_pagamento_vencendo(
    grupo: Grupo,
    numero_ciclo: int,
    pagador: Usuario,
    prazo: date,
    db: Session,
) -> Notificacao:
    return _notify_user_once(
        recipient=pagador,
        event="PAGAMENTO_VENCENDO",
        title="Pagamento próximo do prazo",
        message=(
            f"O pagamento do ciclo {numero_ciclo} do grupo {grupo.nome} "
            f"vence em {prazo.strftime('%d/%m/%Y')}."
        ),
        reference=f"/groups/{grupo.id}",
        action_label="Ver pagamento",
        db=db,
    )


def notificar_pagamento_confirmado(
    grupo: Grupo,
    numero_ciclo: int,
    pagador: Usuario,
    db: Session,
) -> Notificacao:
    return _notify_user_once(
        recipient=pagador,
        event="PAGAMENTO_CONFIRMADO",
        title="Pagamento confirmado",
        message=(
            f"Seu pagamento do ciclo {numero_ciclo} do grupo {grupo.nome} "
            "foi confirmado."
        ),
        reference=f"/groups/{grupo.id}",
        action_label="Ver grupo",
        db=db,
    )


def notificar_pagamento_atrasado(
    grupo: Grupo,
    numero_ciclo: int,
    pagador: Usuario,
    db: Session,
) -> Notificacao:
    return _notify_user_once(
        recipient=pagador,
        event="PAGAMENTO_ATRASADO",
        title="Pagamento atrasado",
        message=(
            f"O pagamento do ciclo {numero_ciclo} do grupo {grupo.nome} "
            "está atrasado."
        ),
        reference=f"/groups/{grupo.id}",
        action_label="Ver pagamento",
        db=db,
    )


def notificar_grupo_cancelado(grupo: Grupo, db: Session) -> list[Notificacao]:
    recipients = db.scalars(
        select(Usuario)
        .join(Participante, Participante.usuario_id == Usuario.id)
        .where(
            Participante.grupo_id == grupo.id,
            Usuario.id != grupo.gestor_id,
        )
        .order_by(Usuario.id)
    ).all()
    return [
        _notify_user(
            recipient=recipient,
            event="GRUPO_CANCELADO",
            title="Grupo cancelado",
            message=f"O grupo {grupo.nome} foi cancelado.",
            reference=f"/groups/{grupo.id}",
            action_label="Ver meus grupos",
            db=db,
        )
        for recipient in recipients
    ]
