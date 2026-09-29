from uuid import uuid4

import pytest
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError

from app.db import SessionLocal, engine
from app.models import Notificacao, Usuario


@pytest.fixture
def usuario_temporario():
    db = SessionLocal()
    usuario = Usuario(
        nome="Destinatario de teste",
        email=f"notificacao-{uuid4()}@example.com",
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


def test_persiste_e_le_notificacao_associada_ao_destinatario(usuario_temporario):
    db = SessionLocal()
    notificacao = Notificacao(
        usuario_id=usuario_temporario,
        tipo="GRUPO_COMPLETO",
        titulo="Grupo completo",
        mensagem="O grupo está pronto para o sorteio.",
        referencia_contextual="/groups/42",
    )
    db.add(notificacao)
    db.commit()
    notificacao_id = notificacao.id
    db.expire_all()

    persistida = db.scalar(
        select(Notificacao).where(Notificacao.id == notificacao_id)
    )

    assert persistida is not None
    assert persistida.usuario_id == usuario_temporario
    assert persistida.destinatario.id == usuario_temporario
    assert persistida.tipo == "GRUPO_COMPLETO"
    assert persistida.titulo == "Grupo completo"
    assert persistida.mensagem == "O grupo está pronto para o sorteio."
    assert persistida.referencia_contextual == "/groups/42"
    assert persistida.status == "NAO_LIDA"
    assert persistida.created_at is not None
    assert persistida.lida_em is None
    db.close()


@pytest.mark.parametrize("campo", ["usuario_id", "tipo", "titulo", "mensagem"])
def test_campos_obrigatorios_rejeitam_nulo(usuario_temporario, campo):
    valores = {
        "usuario_id": usuario_temporario,
        "tipo": "GRUPO_COMPLETO",
        "titulo": "Grupo completo",
        "mensagem": "O grupo está pronto para o sorteio.",
    }
    valores[campo] = None
    db = SessionLocal()
    db.add(Notificacao(**valores))

    with pytest.raises(IntegrityError):
        db.commit()

    db.rollback()
    db.close()


def test_destinatario_inexistente_viola_integridade_referencial():
    db = SessionLocal()
    db.add(
        Notificacao(
            usuario_id=2_147_483_647,
            tipo="GRUPO_COMPLETO",
            titulo="Grupo completo",
            mensagem="O grupo está pronto para o sorteio.",
        )
    )

    with pytest.raises(IntegrityError):
        db.commit()

    db.rollback()
    db.close()


def test_schema_da_notificacao_exige_estado_e_data_de_criacao():
    colunas = {coluna["name"]: coluna for coluna in inspect(engine).get_columns("notificacoes")}

    assert colunas["status"]["nullable"] is False
    assert colunas["created_at"]["nullable"] is False
