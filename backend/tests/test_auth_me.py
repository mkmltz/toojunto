from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from app.auth.security import ALGORITHM, criar_token_acesso, gerar_hash_senha
from app.config import settings
from app.db import SessionLocal
from app.main import app
from app.models import Usuario


client = TestClient(app)


@pytest.fixture
def usuario():
    db = SessionLocal()
    novo_usuario = Usuario(
        nome="Usuário de teste",
        email=f"auth-me-{uuid4()}@example.com",
        senha_hash=gerar_hash_senha("senha-segura"),
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    try:
        yield novo_usuario
    finally:
        db.delete(novo_usuario)
        db.commit()
        db.close()


def cabecalho_autorizacao(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_auth_me_com_token_valido(usuario):
    response = client.get(
        "/auth/me",
        headers=cabecalho_autorizacao(criar_token_acesso(usuario.id)),
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "telefone": None,
    }
    assert "senha_hash" not in response.json()


def test_auth_me_sem_token_retorna_401():
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_auth_me_com_token_invalido_retorna_401():
    response = client.get(
        "/auth/me",
        headers=cabecalho_autorizacao("token-invalido"),
    )

    assert response.status_code == 401


def test_auth_me_com_token_expirado_retorna_401(usuario):
    token_expirado = jwt.encode(
        {
            "sub": str(usuario.id),
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.jwt_secret,
        algorithm=ALGORITHM,
    )

    response = client.get(
        "/auth/me",
        headers=cabecalho_autorizacao(token_expirado),
    )

    assert response.status_code == 401


def test_auth_me_com_usuario_inexistente_retorna_401():
    response = client.get(
        "/auth/me",
        headers=cabecalho_autorizacao(criar_token_acesso(999999999)),
    )

    assert response.status_code == 401
