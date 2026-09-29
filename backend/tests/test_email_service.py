from email.message import EmailMessage
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from pydantic import SecretStr

from app.config import Settings
from app.email import EmailConfigurationError, EmailService, SmtpEmailProvider


BACKEND_ROOT = Path(__file__).resolve().parents[1]


def email_settings(**overrides) -> Settings:
    values = {
        "app_env": "development",
        "public_app_url": "https://app.toojunto.example",
        "smtp_host": "smtp.example",
        "smtp_port": 2525,
        "smtp_username": "smtp-user",
        "smtp_password": "environment-only-password",
        "smtp_from_email": "contato@toojunto.example",
        "smtp_from_name": "TooJunto",
        "smtp_use_tls": True,
        "smtp_timeout_seconds": 7,
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_constroi_mensagem_com_destinatario_assunto_html_texto_e_link():
    service = EmailService(email_settings(), provider=Mock())

    message = service.construir_mensagem(
        destinatario="pessoa@example.com",
        assunto="Grupo pronto",
        titulo="Seu grupo esta completo",
        mensagem="Agora voce pode acompanhar o sorteio.",
        action_path="/groups/42",
        action_label="Ver grupo",
    )

    assert message["To"] == "pessoa@example.com"
    assert message["From"] == "TooJunto <contato@toojunto.example>"
    assert message["Subject"] == "Grupo pronto"
    assert message.is_multipart()
    text = message.get_body(preferencelist=("plain",)).get_content()
    html = message.get_body(preferencelist=("html",)).get_content()
    assert "Seu grupo esta completo" in text
    assert "Agora voce pode acompanhar o sorteio." in text
    assert "Ver grupo: https://app.toojunto.example/groups/42" in text
    assert "<html" in html
    assert "max-width:560px" in html
    assert 'href="https://app.toojunto.example/groups/42"' in html
    assert "Ver grupo" in html


def test_constroi_mensagem_sem_link_opcional():
    service = EmailService(email_settings(), provider=Mock())

    message = service.construir_mensagem(
        destinatario="pessoa@example.com",
        assunto="Atualizacao",
        titulo="Atualizacao do TooJunto",
        mensagem="Existe uma nova informacao para voce.",
    )

    text = message.get_body(preferencelist=("plain",)).get_content()
    html = message.get_body(preferencelist=("html",)).get_content()
    assert "https://" not in text
    assert "href=" not in html


def test_escapa_conteudo_dinamico_no_html():
    service = EmailService(email_settings(), provider=Mock())

    message = service.construir_mensagem(
        destinatario="pessoa@example.com",
        assunto="Atualizacao",
        titulo="<script>alert(1)</script>",
        mensagem="<b>conteudo</b>",
    )

    html = message.get_body(preferencelist=("html",)).get_content()
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "<b>conteudo</b>" not in html


def test_env_configura_provedor_e_mantem_senha_protegida(monkeypatch):
    monkeypatch.setenv("PUBLIC_APP_URL", "https://app.env.example")
    monkeypatch.setenv("SMTP_HOST", "smtp.env.example")
    monkeypatch.setenv("SMTP_PORT", "465")
    monkeypatch.setenv("SMTP_USERNAME", "env-user")
    monkeypatch.setenv("SMTP_PASSWORD", "env-password")
    monkeypatch.setenv("SMTP_FROM_EMAIL", "env@example.com")
    monkeypatch.setenv("SMTP_USE_TLS", "false")

    config = Settings(_env_file=None, app_env="development")

    assert config.public_app_url == "https://app.env.example"
    assert config.smtp_host == "smtp.env.example"
    assert config.smtp_port == 465
    assert config.smtp_username == "env-user"
    assert isinstance(config.smtp_password, SecretStr)
    assert "env-password" not in repr(config)
    assert config.smtp_from_email == "env@example.com"
    assert config.smtp_use_tls is False


def test_envio_usa_provedor_injetado_sem_envio_real():
    provider = Mock()
    service = EmailService(email_settings(), provider=provider)

    result = service.enviar_email(
        destinatario="pessoa@example.com",
        assunto="Atualizacao",
        titulo="Atualizacao do TooJunto",
        mensagem="Existe uma nova informacao para voce.",
    )

    provider.send.assert_called_once_with(result)
    assert isinstance(result, EmailMessage)


def test_provedor_smtp_usa_configuracao_sem_expor_credencial():
    config = email_settings()
    smtp = Mock()
    smtp.__enter__ = Mock(return_value=smtp)
    smtp.__exit__ = Mock(return_value=False)

    with patch("app.email.service.smtplib.SMTP", return_value=smtp) as smtp_class:
        SmtpEmailProvider(config).send(EmailMessage())

    smtp_class.assert_called_once_with(
        host="smtp.example",
        port=2525,
        timeout=7.0,
    )
    smtp.starttls.assert_called_once()
    smtp.login.assert_called_once_with(
        "smtp-user", "environment-only-password"
    )
    smtp.send_message.assert_called_once()


@pytest.mark.parametrize(
    "overrides",
    [
        {"smtp_host": None},
        {"smtp_from_email": None},
        {"smtp_username": "user", "smtp_password": None},
    ],
)
def test_provedor_rejeita_configuracao_incompleta(overrides):
    provider = SmtpEmailProvider(email_settings(**overrides))

    with pytest.raises(EmailConfigurationError):
        provider.send(EmailMessage())


def test_link_exige_url_publica_configurada_e_caminho_interno():
    service = EmailService(
        email_settings(public_app_url=None),
        provider=Mock(),
    )

    with pytest.raises(EmailConfigurationError, match="PUBLIC_APP_URL"):
        service.construir_mensagem(
            destinatario="pessoa@example.com",
            assunto="Atualizacao",
            titulo="Atualizacao",
            mensagem="Mensagem",
            action_path="/groups/42",
        )

    service = EmailService(email_settings(), provider=Mock())
    with pytest.raises(ValueError, match="application path"):
        service.construir_mensagem(
            destinatario="pessoa@example.com",
            assunto="Atualizacao",
            titulo="Atualizacao",
            mensagem="Mensagem",
            action_path="https://attacker.example/path",
        )


def test_servico_nao_contem_credenciais_hardcoded():
    source = (BACKEND_ROOT / "app" / "email" / "service.py").read_text(
        encoding="utf-8"
    )

    assert "environment-only-password" not in source
    assert "smtp.example" not in source
