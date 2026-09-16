from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from sqlalchemy import select

from app.auth.security import (
    ALGORITHM,
    criar_token_acesso,
    gerar_hash_senha,
    verificar_senha,
)
from app.config import settings
from app.db import SessionLocal
from app.main import app
from app.models import Usuario


client = TestClient(app)
SENHA_VALIDA = "senha-segura"


@pytest.fixture
def emails_temporarios():
    emails = []

    try:
        yield emails
    finally:
        db = SessionLocal()
        try:
            usuarios = db.scalars(
                select(Usuario).where(Usuario.email.in_(emails))
            ).all()
            for usuario in usuarios:
                db.delete(usuario)
            db.commit()
        finally:
            db.close()


@pytest.fixture
def usuario_temporario(emails_temporarios):
    email = f"auth-{uuid4()}@example.com"
    emails_temporarios.append(email)
    db = SessionLocal()
    try:
        usuario = Usuario(
            nome="Usuário de teste",
            email=email,
            senha_hash=gerar_hash_senha(SENHA_VALIDA),
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario
    finally:
        db.close()


def dados_cadastro(email: str, **sobrescritas):
    dados = {
        "nome": "Usuário de teste",
        "email": email,
        "telefone": "71999999999",
        "senha": SENHA_VALIDA,
    }
    dados.update(sobrescritas)
    return dados


def test_cadastro_valido_retorna_201_sem_senha_hash(emails_temporarios):
    email = f"cadastro-{uuid4()}@example.com"
    emails_temporarios.append(email)

    response = client.post("/auth/register", json=dados_cadastro(email))

    assert response.status_code == 201
    assert response.json()["email"] == email
    assert "senha_hash" not in response.json()


def test_cadastro_com_email_duplicado_retorna_409(usuario_temporario):
    response = client.post(
        "/auth/register",
        json=dados_cadastro(usuario_temporario.email),
    )

    assert response.status_code == 409


@pytest.mark.parametrize(
    "sobrescritas",
    [
        {"nome": "A"},
        {"email": "email-invalido"},
        {"senha": "curta"},
    ],
)
def test_cadastro_com_dados_invalidos_retorna_422(
    emails_temporarios,
    sobrescritas,
):
    email = f"invalido-{uuid4()}@example.com"
    emails_temporarios.append(email)

    dados = dados_cadastro(email)
    dados.update(sobrescritas)
    response = client.post("/auth/register", json=dados)

    assert response.status_code == 422


def test_login_com_credenciais_validas_retorna_bearer_token(usuario_temporario):
    response = client.post(
        "/auth/login",
        json={"email": usuario_temporario.email, "senha": SENHA_VALIDA},
    )

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["token_type"] == "bearer"


def test_login_com_senha_incorreta_retorna_401(usuario_temporario):
    response = client.post(
        "/auth/login",
        json={"email": usuario_temporario.email, "senha": "senha-incorreta"},
    )

    assert response.status_code == 401


def test_login_com_usuario_inexistente_retorna_401():
    response = client.post(
        "/auth/login",
        json={"email": f"ausente-{uuid4()}@example.com", "senha": SENHA_VALIDA},
    )

    assert response.status_code == 401


def test_senha_e_armazenada_com_hash_seguro():
    senha_hash = gerar_hash_senha(SENHA_VALIDA)

    assert senha_hash != SENHA_VALIDA
    assert verificar_senha(SENHA_VALIDA, senha_hash)
    assert not verificar_senha("senha-incorreta", senha_hash)


def test_jwt_gerado_contem_claims_esperadas(usuario_temporario):
    token = criar_token_acesso(usuario_temporario.id)

    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[ALGORITHM],
    )

    assert payload["sub"] == str(usuario_temporario.id)
    assert "iat" in payload
    assert "exp" in payload


def test_jwt_expirado_e_rejeitado(usuario_temporario):
    token_expirado = jwt.encode(
        {
            "sub": str(usuario_temporario.id),
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.jwt_secret,
        algorithm=ALGORITHM,
    )

    with pytest.raises(ExpiredSignatureError):
        jwt.decode(
            token_expirado,
            settings.jwt_secret,
            algorithms=[ALGORITHM],
        )


def test_jwt_adulterado_e_rejeitado(usuario_temporario):
    token_adulterado = f"{criar_token_acesso(usuario_temporario.id)}adulterado"

    with pytest.raises(JWTError):
        jwt.decode(
            token_adulterado,
            settings.jwt_secret,
            algorithms=[ALGORITHM],
        )
