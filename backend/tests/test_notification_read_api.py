from datetime import datetime, timedelta
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.auth.security import criar_token_acesso
from app.db import SessionLocal
from app.main import app
from app.models import Notificacao, Usuario
from app.notifications import NotificationService


client = TestClient(app)


def cabecalho_autorizacao(usuario_id: int) -> dict[str, str]:
    return {"Authorization": f"Bearer {criar_token_acesso(usuario_id)}"}


@pytest.fixture
def usuarios_temporarios():
    db = SessionLocal()
    usuarios = [
        Usuario(
            nome=f"Usuario leitura {indice}",
            email=f"notification-read-{uuid4()}@example.com",
            senha_hash="hash-de-teste",
        )
        for indice in range(2)
    ]
    db.add_all(usuarios)
    db.commit()
    for usuario in usuarios:
        db.refresh(usuario)
    ids = [usuario.id for usuario in usuarios]

    try:
        yield ids
    finally:
        db.execute(
            Notificacao.__table__.delete().where(Notificacao.usuario_id.in_(ids))
        )
        db.execute(Usuario.__table__.delete().where(Usuario.id.in_(ids)))
        db.commit()
        db.close()


def criar_notificacao(
    usuario_id: int,
    *,
    status: str = "NAO_LIDA",
    lida_em: datetime | None = None,
) -> Notificacao:
    db = SessionLocal()
    notificacao = Notificacao(
        usuario_id=usuario_id,
        tipo="EVENTO_TESTE",
        titulo="Titulo de teste",
        mensagem="Mensagem de teste",
        status=status,
        lida_em=lida_em,
    )
    db.add(notificacao)
    db.commit()
    db.refresh(notificacao)
    db.expunge(notificacao)
    db.close()
    return notificacao


def test_contador_considera_somente_nao_lidas_do_usuario(usuarios_temporarios):
    usuario_id, outro_usuario_id = usuarios_temporarios
    criar_notificacao(usuario_id)
    criar_notificacao(usuario_id)
    criar_notificacao(usuario_id, status="LIDA", lida_em=datetime.now())
    criar_notificacao(outro_usuario_id)

    response = client.get(
        "/notifications/unread-count",
        headers=cabecalho_autorizacao(usuario_id),
    )

    assert response.status_code == 200
    assert response.json() == {"count": 2}


def test_contador_sem_notificacoes_retorna_zero(usuarios_temporarios):
    usuario_id, _ = usuarios_temporarios

    response = client.get(
        "/notifications/unread-count",
        headers=cabecalho_autorizacao(usuario_id),
    )

    assert response.status_code == 200
    assert response.json() == {"count": 0}


def test_marca_notificacao_propria_como_lida_e_reduz_contador(
    usuarios_temporarios,
):
    usuario_id, _ = usuarios_temporarios
    notificacao = criar_notificacao(usuario_id)

    response = client.patch(
        f"/notifications/{notificacao.id}/read",
        headers=cabecalho_autorizacao(usuario_id),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "LIDA"
    assert response.json()["lida_em"] is not None

    db = SessionLocal()
    persistida = db.scalar(
        select(Notificacao).where(Notificacao.id == notificacao.id)
    )
    assert persistida.status == "LIDA"
    assert persistida.lida_em is not None
    db.close()

    count_response = client.get(
        "/notifications/unread-count",
        headers=cabecalho_autorizacao(usuario_id),
    )
    assert count_response.json() == {"count": 0}


def test_nao_permite_marcar_notificacao_de_outro_usuario(usuarios_temporarios):
    usuario_id, outro_usuario_id = usuarios_temporarios
    notificacao = criar_notificacao(outro_usuario_id)

    response = client.patch(
        f"/notifications/{notificacao.id}/read",
        headers=cabecalho_autorizacao(usuario_id),
    )

    assert response.status_code == 404
    db = SessionLocal()
    persistida = db.get(Notificacao, notificacao.id)
    assert persistida.status == "NAO_LIDA"
    assert persistida.lida_em is None
    db.close()


def test_notificacao_inexistente_retorna_404(usuarios_temporarios):
    usuario_id, _ = usuarios_temporarios

    response = client.patch(
        "/notifications/2147483647/read",
        headers=cabecalho_autorizacao(usuario_id),
    )

    assert response.status_code == 404


def test_leitura_repetida_e_idempotente(usuarios_temporarios):
    usuario_id, _ = usuarios_temporarios
    leitura_original = datetime.now() - timedelta(minutes=5)
    notificacao = criar_notificacao(
        usuario_id,
        status="LIDA",
        lida_em=leitura_original,
    )

    response = client.patch(
        f"/notifications/{notificacao.id}/read",
        headers=cabecalho_autorizacao(usuario_id),
    )

    assert response.status_code == 200
    assert datetime.fromisoformat(response.json()["lida_em"]) == leitura_original
    db = SessionLocal()
    assert db.get(Notificacao, notificacao.id).lida_em == leitura_original
    db.close()


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/notifications/unread-count"),
        ("patch", "/notifications/1/read"),
    ],
)
def test_endpoints_rejeitam_acesso_sem_autenticacao(method, path):
    response = client.request(method, path)

    assert response.status_code == 401


def test_falha_ao_persistir_leitura_realiza_rollback():
    usuario = Usuario(id=1)
    notificacao = Notificacao(
        id=1,
        usuario_id=1,
        tipo="EVENTO_TESTE",
        titulo="Titulo",
        mensagem="Mensagem",
    )
    db = Mock()
    db.scalar.return_value = notificacao
    db.commit.side_effect = RuntimeError("database unavailable")

    with pytest.raises(RuntimeError, match="database unavailable"):
        NotificationService.marcar_como_lida(1, usuario, db)

    db.rollback.assert_called_once_with()
    db.refresh.assert_not_called()
