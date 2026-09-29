from datetime import datetime, timezone
import smtplib
from typing import Callable

from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import EntregaEmail
from .service import EmailService


class EmailDeliveryPersistenceError(RuntimeError):
    """Raised when an email attempt result cannot be persisted."""


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def sanitize_provider_error(error: Exception) -> str:
    if isinstance(error, smtplib.SMTPAuthenticationError):
        return "Falha de autenticacao no provedor de e-mail."
    if isinstance(error, (TimeoutError, smtplib.SMTPServerDisconnected)):
        return "Tempo limite ou desconexao do provedor de e-mail."
    if isinstance(error, (ConnectionError, OSError)):
        return "Falha de conexao com o provedor de e-mail."
    return "Falha no provedor de e-mail."


class ReliableEmailService:
    """Sends email and records its result in an isolated transaction."""

    def __init__(
        self,
        email_service: EmailService,
        session_factory: Callable[[], Session] = SessionLocal,
    ):
        self.email_service = email_service
        self.session_factory = session_factory

    def enviar_e_registrar(
        self,
        *,
        destinatario: str,
        evento: str,
        assunto: str,
        titulo: str,
        mensagem: str,
        notificacao_id: int | None = None,
        action_path: str | None = None,
        action_label: str = "Abrir TooJunto",
    ) -> EntregaEmail:
        tentado_em = _utc_now()
        status = "SUCESSO"
        enviado_em = None
        erro = None
        try:
            self.email_service.enviar_email(
                destinatario=destinatario,
                assunto=assunto,
                titulo=titulo,
                mensagem=mensagem,
                action_path=action_path,
                action_label=action_label,
            )
            enviado_em = _utc_now()
        except Exception as provider_error:
            status = "FALHA"
            erro = sanitize_provider_error(provider_error)

        entrega = EntregaEmail(
            notificacao_id=notificacao_id,
            destinatario=destinatario,
            evento=evento,
            status=status,
            tentativas=1,
            tentado_em=tentado_em,
            enviado_em=enviado_em,
            erro=erro,
        )
        db = self.session_factory()
        try:
            db.add(entrega)
            db.commit()
            db.refresh(entrega)
            db.expunge(entrega)
        except Exception as persistence_error:
            db.rollback()
            raise EmailDeliveryPersistenceError(
                "Email delivery result could not be persisted"
            ) from persistence_error
        finally:
            db.close()
        return entrega
