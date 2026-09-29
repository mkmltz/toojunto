from unittest.mock import Mock
from uuid import uuid4

import pytest
from sqlalchemy import func, select

from app.db import SessionLocal
from app.models import Notificacao, Usuario
from app.notifications import (
    NotificationRecipientNotFoundError,
    NotificationService,
    NotificationValidationError,
)


@pytest.fixture
def usuario_temporario():
    db = SessionLocal()
    usuario = Usuario(
        nome="Destinatario do servico",
        email=f"notification-service-{uuid4()}@example.com",
        senha_hash="hash-de-teste",
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    try:
        yield usuario.id
    finally:
        db.execute(
            Notificacao.__table__.delete().where(
                Notificacao.usuario_id == usuario.id
            )
        )
        db.execute(Usuario.__table__.delete().where(Usuario.id == usuario.id))
        db.commit()
        db.close()


def test_cria_e_persiste_notificacao_com_dados_completos(usuario_temporario):
    db = SessionLocal()

    criada = NotificationService.criar_notificacao(
        usuario_id=usuario_temporario,
        tipo="GRUPO_COMPLETO",
        titulo="Grupo completo",
        mensagem="O grupo esta pronto para o sorteio.",
        referencia_contextual="/groups/42",
        db=db,
    )
    notificacao_id = criada.id
    db.expire_all()
    persistida = db.scalar(
        select(Notificacao).where(Notificacao.id == notificacao_id)
    )

    assert persistida is not None
    assert persistida.usuario_id == usuario_temporario
    assert persistida.destinatario.id == usuario_temporario
    assert persistida.tipo == "GRUPO_COMPLETO"
    assert persistida.titulo == "Grupo completo"
    assert persistida.mensagem == "O grupo esta pronto para o sorteio."
    assert persistida.referencia_contextual == "/groups/42"
    assert persistida.status == "NAO_LIDA"
    db.close()


def test_cria_notificacao_sem_referencia_contextual(usuario_temporario):
    db = SessionLocal()

    criada = NotificationService.criar_notificacao(
        usuario_id=usuario_temporario,
        tipo="PAGAMENTO_CONFIRMADO",
        titulo="Pagamento confirmado",
        mensagem="Seu pagamento foi confirmado.",
        db=db,
    )

    assert criada.referencia_contextual is None
    db.close()


def test_destinatario_inexistente_nao_persiste_notificacao():
    db = SessionLocal()
    quantidade_antes = db.scalar(select(func.count(Notificacao.id)))

    with pytest.raises(NotificationRecipientNotFoundError):
        NotificationService.criar_notificacao(
            usuario_id=2_147_483_647,
            tipo="GRUPO_COMPLETO",
            titulo="Grupo completo",
            mensagem="O grupo esta pronto.",
            db=db,
        )

    assert db.scalar(select(func.count(Notificacao.id))) == quantidade_antes
    db.close()


@pytest.mark.parametrize("usuario_id", [None, "1", 0, -1, True])
def test_destinatario_invalido_e_rejeitado(usuario_id):
    db = Mock()

    with pytest.raises(NotificationValidationError):
        NotificationService.criar_notificacao(
            usuario_id=usuario_id,
            tipo="GRUPO_COMPLETO",
            titulo="Grupo completo",
            mensagem="O grupo esta pronto.",
            db=db,
        )

    db.scalar.assert_not_called()
    db.add.assert_not_called()
    db.commit.assert_not_called()


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("tipo", ""),
        ("tipo", "A" * 81),
        ("titulo", "   "),
        ("titulo", "A" * 161),
        ("mensagem", None),
        ("mensagem", "\t"),
        ("referencia_contextual", 42),
        ("referencia_contextual", "A" * 256),
    ],
)
def test_dados_invalidos_sao_rejeitados_antes_da_transacao(campo, valor):
    dados = {
        "usuario_id": 1,
        "tipo": "GRUPO_COMPLETO",
        "titulo": "Grupo completo",
        "mensagem": "O grupo esta pronto.",
        "referencia_contextual": "/groups/42",
    }
    dados[campo] = valor
    db = Mock()

    with pytest.raises(NotificationValidationError):
        NotificationService.criar_notificacao(**dados, db=db)

    db.scalar.assert_not_called()
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_normaliza_textos_antes_de_persistir(usuario_temporario):
    db = SessionLocal()

    criada = NotificationService.criar_notificacao(
        usuario_id=usuario_temporario,
        tipo="  GRUPO_COMPLETO  ",
        titulo="  Grupo completo  ",
        mensagem="  O grupo esta pronto.  ",
        referencia_contextual="  /groups/42  ",
        db=db,
    )

    assert criada.tipo == "GRUPO_COMPLETO"
    assert criada.titulo == "Grupo completo"
    assert criada.mensagem == "O grupo esta pronto."
    assert criada.referencia_contextual == "/groups/42"
    db.close()


def test_falha_no_commit_realiza_rollback_e_propaga_erro():
    db = Mock()
    db.scalar.return_value = Usuario(id=1)
    db.commit.side_effect = RuntimeError("database unavailable")

    with pytest.raises(RuntimeError, match="database unavailable"):
        NotificationService.criar_notificacao(
            usuario_id=1,
            tipo="GRUPO_COMPLETO",
            titulo="Grupo completo",
            mensagem="O grupo esta pronto.",
            db=db,
        )

    db.add.assert_called_once()
    db.rollback.assert_called_once_with()
    db.refresh.assert_not_called()
