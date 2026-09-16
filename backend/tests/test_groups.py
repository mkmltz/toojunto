from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.auth.security import criar_token_acesso, gerar_hash_senha
from app.db import SessionLocal
from app.groups.schemas import GrupoCriacao
from app.groups.service import criar_grupo
from app.main import app
from app.models import Grupo, Participante, Usuario


client = TestClient(app)


@pytest.fixture
def usuario():
    db = SessionLocal()
    novo_usuario = Usuario(
        nome="Gestor de teste",
        email=f"grupo-{uuid4()}@example.com",
        senha_hash=gerar_hash_senha("senha-segura"),
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    try:
        yield novo_usuario
    finally:
        grupos = db.scalars(
            select(Grupo).where(Grupo.gestor_id == novo_usuario.id)
        ).all()
        ids_grupos = [grupo.id for grupo in grupos]
        if ids_grupos:
            db.execute(
                delete(Participante).where(
                    Participante.grupo_id.in_(ids_grupos)
                )
            )
            db.execute(delete(Grupo).where(Grupo.id.in_(ids_grupos)))
        db.delete(novo_usuario)
        db.commit()
        db.close()


def cabecalho_autorizacao(usuario: Usuario) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {criar_token_acesso(usuario.id)}"
    }


def dados_grupo(**sobrescritas):
    dados = {
        "nome": "Caixinha dos Amigos",
        "valor_cota": "200.00",
        "quantidade_participantes": 10,
        "quantidade_ciclos": 10,
        "data_inicio": date.today().isoformat(),
    }
    dados.update(sobrescritas)
    return dados


def test_participantes_e_ciclos_iguais_sao_aceitos(usuario):
    response = client.post(
        "/groups",
        json=dados_grupo(),
        headers=cabecalho_autorizacao(usuario),
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": response.json()["id"],
        "nome": "Caixinha dos Amigos",
        "gestor_id": usuario.id,
        "valor_cota": "200.00",
        "valor_premio": "2000.00",
        "quantidade_participantes": 10,
        "quantidade_ciclos": 10,
        "data_inicio": date.today().isoformat(),
        "status": "RASCUNHO",
        "created_at": response.json()["created_at"],
    }


def test_criacao_persiste_gestor_como_participante_ativo(usuario):
    response = client.post(
        "/groups",
        json=dados_grupo(),
        headers=cabecalho_autorizacao(usuario),
    )

    db = SessionLocal()
    try:
        participante = db.scalar(
            select(Participante).where(
                Participante.grupo_id == response.json()["id"],
                Participante.usuario_id == usuario.id,
            )
        )
        assert participante is not None
        assert participante.status == "ATIVO"
        assert participante.ordem_sorteio is None
    finally:
        db.close()


def test_valor_premio_e_calculado_e_persistido_pelo_backend(usuario):
    response = client.post(
        "/groups",
        json=dados_grupo(valor_cota="125.50"),
        headers=cabecalho_autorizacao(usuario),
    )

    db = SessionLocal()
    try:
        grupo = db.get(Grupo, response.json()["id"])
        assert response.status_code == 201
        assert response.json()["valor_premio"] == "1255.00"
        assert grupo is not None
        assert grupo.valor_premio == Decimal("1255.00")
    finally:
        db.close()


def test_campos_controlados_pelo_servidor_nao_podem_ser_manipulados(usuario):
    response = client.post(
        "/groups",
        json=dados_grupo(
            gestor_id=999999,
            status="ATIVO",
            valor_premio="1.00",
        ),
        headers=cabecalho_autorizacao(usuario),
    )

    assert response.status_code == 422


def test_cliente_nao_pode_informar_valor_premio(usuario):
    response = client.post(
        "/groups",
        json=dados_grupo(valor_premio="1.00"),
        headers=cabecalho_autorizacao(usuario),
    )

    assert response.status_code == 422


def test_participantes_e_ciclos_diferentes_retornam_422(usuario):
    response = client.post(
        "/groups",
        json=dados_grupo(quantidade_ciclos=9),
        headers=cabecalho_autorizacao(usuario),
    )

    assert response.status_code == 422


def test_criacao_de_grupo_sem_token_retorna_401():
    response = client.post("/groups", json=dados_grupo())

    assert response.status_code == 401


def test_criacao_de_grupo_com_token_invalido_retorna_401():
    response = client.post(
        "/groups",
        json=dados_grupo(),
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "sobrescritas",
    [
        {"nome": " "},
        {"valor_cota": "0"},
        {"valor_cota": "-1"},
        {"valor_cota": "10.001"},
        {"quantidade_participantes": 1},
        {"quantidade_ciclos": 1},
        {"data_inicio": (date.today() - timedelta(days=1)).isoformat()},
        {"data_inicio": "data-invalida"},
    ],
)
def test_dados_invalidos_retornam_422(usuario, sobrescritas):
    response = client.post(
        "/groups",
        json=dados_grupo(**sobrescritas),
        headers=cabecalho_autorizacao(usuario),
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "campo",
    [
        "nome",
        "valor_cota",
        "quantidade_participantes",
        "quantidade_ciclos",
        "data_inicio",
    ],
)
def test_campos_obrigatorios_retornam_422(usuario, campo):
    dados = dados_grupo()
    dados.pop(campo)

    response = client.post(
        "/groups",
        json=dados,
        headers=cabecalho_autorizacao(usuario),
    )

    assert response.status_code == 422


def test_servico_faz_rollback_quando_persistencia_falha(usuario):
    db = MagicMock()
    db.flush.side_effect = RuntimeError("falha de persistência")
    dados = GrupoCriacao(
        nome="Caixinha dos Amigos",
        valor_cota=Decimal("200.00"),
        quantidade_participantes=10,
        quantidade_ciclos=10,
        data_inicio=date.today(),
    )

    with pytest.raises(RuntimeError, match="falha de persistência"):
        criar_grupo(dados, usuario, db)

    db.rollback.assert_called_once_with()
    db.commit.assert_not_called()
