from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.auth.security import criar_token_acesso, gerar_hash_senha
from app.db import SessionLocal
from app.main import app
from app.models import Usuario


client = TestClient(app)


@pytest.fixture
def usuarios():
    db = SessionLocal()
    criados = [
        Usuario(
            nome=f"Usuário Pix {indice}",
            email=f"pix-{uuid4()}@example.com",
            senha_hash=gerar_hash_senha("senha-segura"),
        )
        for indice in range(2)
    ]
    db.add_all(criados)
    db.commit()
    for usuario in criados:
        db.refresh(usuario)

    try:
        yield criados
    finally:
        for usuario in criados:
            db.delete(usuario)
        db.commit()
        db.close()


def headers(usuario: Usuario) -> dict[str, str]:
    return {"Authorization": f"Bearer {criar_token_acesso(usuario.id)}"}


def test_usuario_autenticado_consulta_sem_pix(usuarios):
    response = client.get("/auth/me/pix", headers=headers(usuarios[0]))

    assert response.status_code == 200
    assert response.json() == {"chave_pix": None}


def test_usuario_cadastra_consulta_altera_e_remove_pix(usuarios):
    usuario = usuarios[0]

    cadastro = client.put(
        "/auth/me/pix",
        headers=headers(usuario),
        json={"chave_pix": "  usuario@example.com  "},
    )
    assert cadastro.status_code == 200
    assert cadastro.json() == {"chave_pix": "usuario@example.com"}

    consulta = client.get("/auth/me/pix", headers=headers(usuario))
    assert consulta.json() == {"chave_pix": "usuario@example.com"}

    alteracao = client.put(
        "/auth/me/pix",
        headers=headers(usuario),
        json={"chave_pix": "+5571999999999"},
    )
    assert alteracao.json() == {"chave_pix": "+5571999999999"}

    remocao = client.put(
        "/auth/me/pix",
        headers=headers(usuario),
        json={"chave_pix": "   "},
    )
    assert remocao.json() == {"chave_pix": None}

    db = SessionLocal()
    try:
        assert db.get(Usuario, usuario.id).chave_pix is None
    finally:
        db.close()


def test_pix_sem_autenticacao_retorna_401():
    assert client.get("/auth/me/pix").status_code == 401
    assert client.put("/auth/me/pix", json={"chave_pix": "x"}).status_code == 401


def test_usuario_nao_altera_pix_de_outro_usuario(usuarios):
    primeiro, segundo = usuarios
    segundo.chave_pix = "segundo@example.com"
    db = SessionLocal()
    try:
        persistido = db.get(Usuario, segundo.id)
        persistido.chave_pix = segundo.chave_pix
        db.commit()
    finally:
        db.close()

    response = client.put(
        "/auth/me/pix",
        headers=headers(primeiro),
        json={"chave_pix": "primeiro@example.com", "usuario_id": segundo.id},
    )

    assert response.status_code == 200
    db = SessionLocal()
    try:
        assert db.get(Usuario, primeiro.id).chave_pix == "primeiro@example.com"
        assert db.get(Usuario, segundo.id).chave_pix == "segundo@example.com"
    finally:
        db.close()


def test_auth_me_nao_expoe_chave_pix(usuarios):
    usuario = usuarios[0]
    client.put(
        "/auth/me/pix",
        headers=headers(usuario),
        json={"chave_pix": "privada@example.com"},
    )

    response = client.get("/auth/me", headers=headers(usuario))

    assert response.status_code == 200
    assert "chave_pix" not in response.json()
