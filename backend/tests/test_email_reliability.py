from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.db import SessionLocal
from app.email import (
    EmailDeliveryPersistenceError,
    ReliableEmailService,
)
from app.models import EntregaEmail, Notificacao, Usuario


@pytest.fixture
def notificacao_temporaria():
    db = SessionLocal()
    usuario = Usuario(
        nome="Destinatario de entrega",
        email=f"email-delivery-{uuid4()}@example.com",
        senha_hash="hash-de-teste",
    )
    db.add(usuario)
    db.flush()
    notificacao = Notificacao(
        usuario_id=usuario.id,
        tipo="EVENTO_TESTE",
        titulo="Titulo",
        mensagem="Mensagem",
    )
    db.add(notificacao)
    db.commit()
    db.refresh(notificacao)
    ids = (usuario.id, notificacao.id)
    db.close()

    try:
        yield ids
    finally:
        db = SessionLocal()
        db.execute(
            EntregaEmail.__table__.delete().where(
                EntregaEmail.notificacao_id == notificacao.id
            )
        )
        db.execute(
            Notificacao.__table__.delete().where(
                Notificacao.id == notificacao.id
            )
        )
        db.execute(Usuario.__table__.delete().where(Usuario.id == usuario.id))
        db.commit()
        db.close()


def dados_envio(notificacao_id: int) -> dict:
    return {
        "destinatario": "pessoa@example.com",
        "evento": "EVENTO_TESTE",
        "assunto": "Assunto",
        "titulo": "Titulo",
        "mensagem": "Mensagem",
        "notificacao_id": notificacao_id,
    }


def test_envio_bem_sucedido_registra_resultado_e_associacao(
    notificacao_temporaria,
):
    _, notificacao_id = notificacao_temporaria
    email_service = Mock()
    service = ReliableEmailService(email_service)

    entrega = service.enviar_e_registrar(**dados_envio(notificacao_id))

    email_service.enviar_email.assert_called_once()
    assert entrega.status == "SUCESSO"
    assert entrega.notificacao_id == notificacao_id
    assert entrega.destinatario == "pessoa@example.com"
    assert entrega.evento == "EVENTO_TESTE"
    assert entrega.tentativas == 1
    assert entrega.tentado_em is not None
    assert entrega.enviado_em is not None
    assert entrega.erro is None

    db = SessionLocal()
    persistida = db.get(EntregaEmail, entrega.id)
    assert persistida.status == "SUCESSO"
    assert persistida.notificacao_id == notificacao_id
    db.close()


def test_falha_do_provedor_e_sanitizada_registrada_e_nao_propagada(
    notificacao_temporaria,
):
    _, notificacao_id = notificacao_temporaria
    email_service = Mock()
    email_service.enviar_email.side_effect = RuntimeError(
        "smtp_password=segredo-real token=token-secreto stack trace"
    )
    service = ReliableEmailService(email_service)

    entrega = service.enviar_e_registrar(**dados_envio(notificacao_id))

    assert entrega.status == "FALHA"
    assert entrega.enviado_em is None
    assert entrega.erro == "Falha no provedor de e-mail."
    assert "segredo-real" not in entrega.erro
    assert "token-secreto" not in entrega.erro
    assert "stack trace" not in entrega.erro

    db = SessionLocal()
    persistida = db.get(EntregaEmail, entrega.id)
    assert persistida.status == "FALHA"
    assert persistida.erro == "Falha no provedor de e-mail."
    db.close()


def test_falha_preserva_notificacao_e_operacao_ja_confirmada(
    notificacao_temporaria,
):
    usuario_id, notificacao_id = notificacao_temporaria
    email_service = Mock()
    email_service.enviar_email.side_effect = TimeoutError("secret=value")

    entrega = ReliableEmailService(email_service).enviar_e_registrar(
        **dados_envio(notificacao_id)
    )

    assert entrega.status == "FALHA"
    db = SessionLocal()
    notificacao = db.get(Notificacao, notificacao_id)
    usuario = db.get(Usuario, usuario_id)
    assert notificacao is not None
    assert notificacao.status == "NAO_LIDA"
    assert usuario is not None
    db.close()


def test_registro_pode_existir_sem_notificacao_associada():
    email_service = Mock()
    entrega = ReliableEmailService(email_service).enviar_e_registrar(
        destinatario="pessoa@example.com",
        evento="EVENTO_SEM_NOTIFICACAO",
        assunto="Assunto",
        titulo="Titulo",
        mensagem="Mensagem",
    )

    try:
        assert entrega.notificacao_id is None
        assert entrega.status == "SUCESSO"
    finally:
        db = SessionLocal()
        db.execute(
            EntregaEmail.__table__.delete().where(EntregaEmail.id == entrega.id)
        )
        db.commit()
        db.close()


def test_falha_ao_registrar_resultado_faz_rollback_sem_expor_erro_do_provedor():
    email_service = Mock()
    email_service.enviar_email.side_effect = RuntimeError(
        "smtp_password=nao-registrar"
    )
    db = Mock()
    db.commit.side_effect = RuntimeError("database failure")
    service = ReliableEmailService(email_service, session_factory=lambda: db)

    with pytest.raises(EmailDeliveryPersistenceError) as captured:
        service.enviar_e_registrar(**dados_envio(1))

    assert "nao-registrar" not in str(captured.value)
    db.rollback.assert_called_once_with()
    db.close.assert_called_once_with()


def test_horarios_registrados_sao_datetimes_sem_conteudo_sensivel(
    notificacao_temporaria,
):
    _, notificacao_id = notificacao_temporaria
    entrega = ReliableEmailService(Mock()).enviar_e_registrar(
        **dados_envio(notificacao_id)
    )

    assert isinstance(entrega.tentado_em, datetime)
    assert isinstance(entrega.enviado_em, datetime)
    assert entrega.erro is None
