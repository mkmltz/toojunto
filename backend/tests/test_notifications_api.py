from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.auth.security import criar_token_acesso
from app.db import SessionLocal
from app.main import app
from app.models import Notificacao, Usuario


client = TestClient(app)


def cabecalho_autorizacao(usuario_id: int) -> dict[str, str]:
    return {"Authorization": f"Bearer {criar_token_acesso(usuario_id)}"}


@pytest.fixture
def usuarios_temporarios():
    db = SessionLocal()
    usuarios = [
        Usuario(
            nome=f"Usuario {indice}",
            email=f"notifications-api-{uuid4()}@example.com",
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
    tipo: str,
    created_at: datetime,
    referencia_contextual: str | None = None,
) -> Notificacao:
    db = SessionLocal()
    notificacao = Notificacao(
        usuario_id=usuario_id,
        tipo=tipo,
        titulo=f"Titulo {tipo}",
        mensagem=f"Mensagem {tipo}",
        referencia_contextual=referencia_contextual,
        created_at=created_at,
    )
    db.add(notificacao)
    db.commit()
    db.refresh(notificacao)
    db.expunge(notificacao)
    db.close()
    return notificacao


def test_usuario_autenticado_consulta_suas_notificacoes_em_ordem_recente(
    usuarios_temporarios,
):
    usuario_id, _ = usuarios_temporarios
    agora = datetime.now()
    antiga = criar_notificacao(
        usuario_id,
        tipo="ANTIGA",
        created_at=agora - timedelta(hours=1),
    )
    recente = criar_notificacao(
        usuario_id,
        tipo="RECENTE",
        created_at=agora,
        referencia_contextual="/groups/42",
    )

    response = client.get(
        "/notifications",
        headers=cabecalho_autorizacao(usuario_id),
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [recente.id, antiga.id]


def test_usuario_sem_notificacoes_recebe_lista_vazia(usuarios_temporarios):
    usuario_id, _ = usuarios_temporarios

    response = client.get(
        "/notifications",
        headers=cabecalho_autorizacao(usuario_id),
    )

    assert response.status_code == 200
    assert response.json() == []


def test_notificacoes_sao_isoladas_por_usuario(usuarios_temporarios):
    usuario_id, outro_usuario_id = usuarios_temporarios
    propria = criar_notificacao(
        usuario_id,
        tipo="PROPRIA",
        created_at=datetime.now(),
    )
    criar_notificacao(
        outro_usuario_id,
        tipo="DE_OUTRO_USUARIO",
        created_at=datetime.now() + timedelta(seconds=1),
    )

    response = client.get(
        f"/notifications?usuario_id={outro_usuario_id}",
        headers=cabecalho_autorizacao(usuario_id),
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [propria.id]
    assert all(item["tipo"] != "DE_OUTRO_USUARIO" for item in response.json())


def test_acesso_sem_autenticacao_e_rejeitado():
    response = client.get("/notifications")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_resposta_contem_exclusivamente_os_campos_do_contrato(
    usuarios_temporarios,
):
    usuario_id, _ = usuarios_temporarios
    notificacao = criar_notificacao(
        usuario_id,
        tipo="GRUPO_COMPLETO",
        created_at=datetime.now(),
        referencia_contextual="/groups/42",
    )

    response = client.get(
        "/notifications",
        headers=cabecalho_autorizacao(usuario_id),
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": notificacao.id,
            "tipo": "GRUPO_COMPLETO",
            "titulo": "Titulo GRUPO_COMPLETO",
            "mensagem": "Mensagem GRUPO_COMPLETO",
            "referencia_contextual": "/groups/42",
            "status": "NAO_LIDA",
            "created_at": notificacao.created_at.isoformat(),
            "lida_em": None,
        }
    ]
