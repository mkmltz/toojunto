from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Notificacao, Usuario


class NotificationValidationError(ValueError):
    """Raised when notification data does not satisfy the persistence contract."""


class NotificationRecipientNotFoundError(LookupError):
    """Raised when the notification recipient does not exist."""


class NotificationService:
    """Central entry point for creating and persisting notifications."""

    @staticmethod
    def _required_text(value: object, field: str, max_length: int | None) -> str:
        if not isinstance(value, str) or not value.strip():
            raise NotificationValidationError(f"{field} must be a non-empty string")
        normalized = value.strip()
        if max_length is not None and len(normalized) > max_length:
            raise NotificationValidationError(
                f"{field} must contain at most {max_length} characters"
            )
        return normalized

    @staticmethod
    def _optional_reference(value: object) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            raise NotificationValidationError(
                "referencia_contextual must be a string or None"
            )
        normalized = value.strip()
        if not normalized:
            return None
        if len(normalized) > 255:
            raise NotificationValidationError(
                "referencia_contextual must contain at most 255 characters"
            )
        return normalized

    @classmethod
    def criar_notificacao(
        cls,
        *,
        usuario_id: int,
        tipo: str,
        titulo: str,
        mensagem: str,
        db: Session,
        referencia_contextual: str | None = None,
    ) -> Notificacao:
        if isinstance(usuario_id, bool) or not isinstance(usuario_id, int):
            raise NotificationValidationError("usuario_id must be an integer")
        if usuario_id <= 0:
            raise NotificationValidationError("usuario_id must be greater than zero")

        tipo_normalizado = cls._required_text(tipo, "tipo", 80)
        titulo_normalizado = cls._required_text(titulo, "titulo", 160)
        mensagem_normalizada = cls._required_text(mensagem, "mensagem", None)
        referencia_normalizada = cls._optional_reference(referencia_contextual)

        try:
            destinatario = db.scalar(
                select(Usuario).where(Usuario.id == usuario_id)
            )
            if destinatario is None:
                raise NotificationRecipientNotFoundError(
                    "Notification recipient was not found"
                )

            notificacao = Notificacao(
                usuario_id=usuario_id,
                tipo=tipo_normalizado,
                titulo=titulo_normalizado,
                mensagem=mensagem_normalizada,
                referencia_contextual=referencia_normalizada,
            )
            db.add(notificacao)
            db.commit()
            db.refresh(notificacao)
            return notificacao
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def listar_notificacoes_do_usuario(
        usuario: Usuario,
        db: Session,
    ) -> list[Notificacao]:
        return list(
            db.scalars(
                select(Notificacao)
                .where(Notificacao.usuario_id == usuario.id)
                .order_by(Notificacao.created_at.desc(), Notificacao.id.desc())
            ).all()
        )
