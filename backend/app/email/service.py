from email.message import EmailMessage
from email.utils import formataddr
import smtplib
import ssl
from typing import Protocol
from urllib.parse import urljoin, urlparse

from email_validator import EmailNotValidError, validate_email

from ..config import Settings, settings
from .templates import build_html_content, build_text_content


class EmailConfigurationError(RuntimeError):
    """Raised when the transactional email provider is not configured."""


class EmailProvider(Protocol):
    def send(self, message: EmailMessage) -> None: ...


class SmtpEmailProvider:
    def __init__(self, app_settings: Settings):
        self.settings = app_settings

    def _validate_configuration(self) -> None:
        if not self.settings.smtp_host:
            raise EmailConfigurationError("SMTP_HOST is required")
        if not self.settings.smtp_from_email:
            raise EmailConfigurationError("SMTP_FROM_EMAIL is required")
        if bool(self.settings.smtp_username) != bool(self.settings.smtp_password):
            raise EmailConfigurationError(
                "SMTP_USERNAME and SMTP_PASSWORD must be configured together"
            )

    def send(self, message: EmailMessage) -> None:
        self._validate_configuration()
        with smtplib.SMTP(
            host=self.settings.smtp_host,
            port=self.settings.smtp_port,
            timeout=self.settings.smtp_timeout_seconds,
        ) as smtp:
            if self.settings.smtp_use_tls:
                smtp.starttls(context=ssl.create_default_context())
            if self.settings.smtp_username and self.settings.smtp_password:
                smtp.login(
                    self.settings.smtp_username,
                    self.settings.smtp_password.get_secret_value(),
                )
            smtp.send_message(message)


class EmailService:
    def __init__(
        self,
        app_settings: Settings = settings,
        provider: EmailProvider | None = None,
    ):
        self.settings = app_settings
        self.provider = provider or SmtpEmailProvider(app_settings)

    @staticmethod
    def _required_text(value: object, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string")
        return value.strip()

    def _action_url(self, action_path: str | None) -> str | None:
        if action_path is None:
            return None
        if not isinstance(action_path, str) or not action_path.startswith("/"):
            raise ValueError("action_path must be an absolute application path")
        parsed_path = urlparse(action_path)
        if parsed_path.scheme or parsed_path.netloc:
            raise ValueError("action_path cannot contain an external URL")
        if not self.settings.public_app_url:
            raise EmailConfigurationError(
                "PUBLIC_APP_URL is required when an action link is used"
            )
        public_url = urlparse(self.settings.public_app_url)
        if public_url.scheme not in {"http", "https"} or not public_url.netloc:
            raise EmailConfigurationError("PUBLIC_APP_URL must be an HTTP(S) URL")
        return urljoin(self.settings.public_app_url.rstrip("/") + "/", action_path[1:])

    def construir_mensagem(
        self,
        *,
        destinatario: str,
        assunto: str,
        titulo: str,
        mensagem: str,
        action_path: str | None = None,
        action_label: str = "Abrir TooJunto",
    ) -> EmailMessage:
        try:
            recipient = validate_email(
                destinatario,
                check_deliverability=False,
            ).normalized
        except EmailNotValidError as error:
            raise ValueError("destinatario must be a valid email address") from error

        subject = self._required_text(assunto, "assunto")
        title = self._required_text(titulo, "titulo")
        body = self._required_text(mensagem, "mensagem")
        label = self._required_text(action_label, "action_label")
        action_url = self._action_url(action_path)
        if not self.settings.smtp_from_email:
            raise EmailConfigurationError("SMTP_FROM_EMAIL is required")

        email = EmailMessage()
        email["To"] = recipient
        email["From"] = formataddr(
            (self.settings.smtp_from_name, self.settings.smtp_from_email)
        )
        email["Subject"] = subject
        email.set_content(build_text_content(title, body, action_url, label))
        email.add_alternative(
            build_html_content(title, body, action_url, label),
            subtype="html",
        )
        return email

    def enviar_email(self, **message_data) -> EmailMessage:
        message = self.construir_mensagem(**message_data)
        self.provider.send(message)
        return message
