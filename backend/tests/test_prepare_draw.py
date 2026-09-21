from datetime import date
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.auth.security import criar_token_acesso, gerar_hash_senha
from app.db import SessionLocal
from app.main import app
from app.models import Ciclo, Convite, Grupo, Participante, Usuario


client = TestClient(app)


@pytest.fixture
def contexto():
    db = SessionLocal()
    usuarios = [
        Usuario(nome=nome, email=f"draw-{uuid4()}@example.com", senha_hash=gerar_hash_senha("senha-segura"))
        for nome in ("Gestor", "Participante", "Externo")
    ]
    db.add_all(usuarios)
    db.commit()
    try:
        yield usuarios
    finally:
        grupos = db.scalars(select(Grupo).where(Grupo.gestor_id == usuarios[0].id)).all()
        ids = [grupo.id for grupo in grupos]
        if ids:
            db.execute(delete(Convite).where(Convite.grupo_id.in_(ids)))
            db.execute(delete(Participante).where(Participante.grupo_id.in_(ids)))
            db.execute(delete(Grupo).where(Grupo.id.in_(ids)))
        db.execute(delete(Usuario).where(Usuario.id.in_([u.id for u in usuarios])))
        db.commit()
        db.close()


def headers(usuario):
    return {"Authorization": f"Bearer {criar_token_acesso(usuario.id)}"}


def grupo_com_convite(gestor):
    response = client.post("/groups", json={
        "nome": "Grupo sorteio", "valor_cota": "100.00",
        "quantidade_participantes": 2, "quantidade_ciclos": 2,
        "data_inicio": date.today().isoformat(),
    }, headers=headers(gestor))
    assert response.status_code == 201
    grupo = response.json()
    convite = client.post(f"/groups/{grupo['id']}/invite", headers=headers(gestor))
    assert convite.status_code == 200
    return grupo, convite.json()


def completar(grupo, convite, participante):
    resposta = client.post(f"/invites/{convite['token']}/accept", headers=headers(participante))
    assert resposta.status_code == 200
    detalhe = client.get(f"/groups/{grupo['id']}", headers=headers(participante))
    assert detalhe.json()["status"] == "RASCUNHO"


def test_gestor_prepara_grupo_completo_sem_atribuir_ordem(contexto):
    gestor, participante, externo = contexto
    grupo, convite = grupo_com_convite(gestor)
    completar(grupo, convite, participante)
    caminho = f"/groups/{grupo['id']}/prepare-draw"

    assert client.post(caminho, headers=headers(participante)).status_code == 403
    assert client.post(caminho, headers=headers(externo)).status_code == 403
    assert client.post(caminho).status_code == 401
    resposta = client.post(caminho, headers=headers(gestor))
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "SORTEIO"
    assert client.post(caminho, headers=headers(gestor)).status_code == 409
    assert client.patch(f"/groups/{grupo['id']}", json={"quantidade_participantes": 3}, headers=headers(gestor)).status_code == 409
    assert client.post(f"/groups/{grupo['id']}/invite", headers=headers(gestor)).status_code == 409
    assert client.get(f"/invites/{convite['token']}").status_code == 404
    assert client.post(f"/invites/{convite['token']}/accept", headers=headers(externo)).status_code == 409

    db = SessionLocal()
    try:
        integrantes = db.scalars(select(Participante).where(Participante.grupo_id == grupo["id"])).all()
        assert len(integrantes) == 2
        assert all(p.ordem_sorteio is None for p in integrantes)
        assert sum(p.usuario_id == gestor.id for p in integrantes) == 1
        assert db.scalars(select(Ciclo).where(Ciclo.grupo_id == grupo["id"])).all() == []
    finally:
        db.close()


def test_grupo_incompleto_e_cancelado_nao_podem_ser_preparados(contexto):
    gestor, _, _ = contexto
    grupo, _ = grupo_com_convite(gestor)
    caminho = f"/groups/{grupo['id']}/prepare-draw"
    assert client.post(caminho, headers=headers(gestor)).status_code == 409
    assert client.post(f"/groups/{grupo['id']}/cancel", headers=headers(gestor)).status_code == 200
    assert client.post(caminho, headers=headers(gestor)).status_code == 409


@pytest.mark.parametrize("estado", ["FORMANDO", "ATIVO", "ENCERRADO"])
def test_estado_incompativel_nao_pode_ser_preparado(contexto, estado):
    gestor, participante, _ = contexto
    grupo, convite = grupo_com_convite(gestor)
    completar(grupo, convite, participante)
    db = SessionLocal()
    try:
        db.get(Grupo, grupo["id"]).status = estado
        db.commit()
    finally:
        db.close()
    assert client.post(f"/groups/{grupo['id']}/prepare-draw", headers=headers(gestor)).status_code == 409
