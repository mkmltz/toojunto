from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from threading import Barrier
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.auth.security import criar_token_acesso, gerar_hash_senha
from app.db import SessionLocal
from app.main import app
from app.models import Ciclo, Convite, Grupo, Participante, Usuario


client = TestClient(app)


def headers(usuario):
    return {"Authorization": f"Bearer {criar_token_acesso(usuario.id)}"}


@pytest.fixture
def contexto():
    db = SessionLocal()
    usuarios = [
        Usuario(
            nome=nome,
            email=f"us009-{uuid4()}@example.com",
            senha_hash=gerar_hash_senha("senha-segura"),
        )
        for nome in ("Gestor", "Pessoa A", "Pessoa B", "Externo")
    ]
    db.add_all(usuarios)
    db.commit()
    try:
        yield usuarios
    finally:
        ids = [u.id for u in usuarios]
        grupos = db.scalars(select(Grupo).where(Grupo.gestor_id.in_(ids))).all()
        ids_grupos = [g.id for g in grupos]
        if ids_grupos:
            db.execute(delete(Convite).where(Convite.grupo_id.in_(ids_grupos)))
            db.execute(delete(Participante).where(Participante.grupo_id.in_(ids_grupos)))
            db.execute(delete(Grupo).where(Grupo.id.in_(ids_grupos)))
        db.execute(delete(Usuario).where(Usuario.id.in_(ids)))
        db.commit()
        db.close()


def criar_grupo(gestor):
    inicio = date.today() + timedelta(days=40)
    resposta = client.post("/groups", json={
        "nome": "Grupo para sorteio", "valor_cota": "100.00",
        "quantidade_participantes": 3, "quantidade_ciclos": 3,
        "data_inicio": inicio.isoformat(),
    }, headers=headers(gestor))
    assert resposta.status_code == 201
    return resposta.json(), inicio


def preparar_grupo(usuarios):
    gestor, primeiro, segundo, _ = usuarios
    grupo, inicio = criar_grupo(gestor)
    convite = client.post(f"/groups/{grupo['id']}/invite", headers=headers(gestor))
    assert convite.status_code == 200
    for pessoa in (primeiro, segundo):
        assert client.post(
            f"/invites/{convite.json()['token']}/accept",
            headers=headers(pessoa),
        ).status_code == 200
    assert client.post(
        f"/groups/{grupo['id']}/prepare-draw", headers=headers(gestor),
    ).status_code == 200
    return grupo, inicio


def test_sorteio_persiste_ordem_e_calendario_de_30_dias(contexto):
    gestor, participante, _, externo = contexto
    grupo, inicio = preparar_grupo(contexto)
    caminho = f"/groups/{grupo['id']}"
    assert "ordem_recebimento" not in client.get(caminho, headers=headers(gestor)).json()
    assert client.post(f"{caminho}/draw", headers=headers(participante)).status_code == 403
    assert client.post(f"{caminho}/draw", headers=headers(externo)).status_code == 403
    assert client.get(caminho, headers=headers(externo)).status_code == 404
    assert client.post(f"{caminho}/draw").status_code == 401

    resposta = client.post(f"{caminho}/draw", headers=headers(gestor))
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "ATIVO"
    ordem = resposta.json()["ordem_recebimento"]
    assert [item["posicao"] for item in ordem] == [1, 2, 3]
    assert ordem[0]["nome"] == "Gestor"
    assert {item["nome"] for item in ordem} == {
        "Gestor", "Pessoa A", "Pessoa B",
    }
    assert [item["papel"] for item in ordem] == [
        "GESTOR", "PARTICIPANTE", "PARTICIPANTE",
    ]
    assert [item["data_prevista"] for item in ordem] == [
        (inicio + timedelta(days=30 * indice)).isoformat()
        for indice in range(3)
    ]
    assert client.post(f"{caminho}/draw", headers=headers(gestor)).status_code == 409
    assert client.get(caminho, headers=headers(gestor)).json()["ordem_recebimento"] == ordem
    assert client.get(caminho, headers=headers(participante)).json()["ordem_recebimento"] == ordem
    assert client.get(caminho, headers=headers(externo)).status_code == 404
    db = SessionLocal()
    try:
        participantes = db.scalars(select(Participante).where(Participante.grupo_id == grupo["id"])).all()
        assert sorted(p.ordem_sorteio for p in participantes) == [1, 2, 3]
        assert next(p for p in participantes if p.usuario_id == gestor.id).ordem_sorteio == 1
        assert db.scalars(select(Ciclo).where(Ciclo.grupo_id == grupo["id"])).all() == []
    finally:
        db.close()


def test_progresso_dos_ciclos_para_integrantes_autorizados(contexto):
    gestor, participante, _, externo = contexto
    grupo, inicio = preparar_grupo(contexto)
    caminho = f"/groups/{grupo['id']}/cycles"
    assert client.get(caminho, headers=headers(gestor)).status_code == 409
    assert client.get(caminho, headers=headers(externo)).status_code == 404
    assert client.get(caminho).status_code == 401

    assert client.post(
        f"/groups/{grupo['id']}/draw", headers=headers(gestor)
    ).status_code == 200
    progresso = client.get(caminho, headers=headers(gestor))
    assert progresso.status_code == 200
    dados = progresso.json()
    assert dados["ciclo_atual"] == 1
    assert dados["total_ciclos"] == 3
    assert dados["contemplado_ciclo_atual"] == "Gestor"
    assert dados["data_prevista_ciclo_atual"] == inicio.isoformat()
    assert [c["numero_ciclo"] for c in dados["ciclos"]] == [1, 2, 3]
    assert [c["situacao"] for c in dados["ciclos"]] == [
        "ATUAL", "PROXIMO", "PROXIMO"
    ]
    assert [c["data_prevista"] for c in dados["ciclos"]] == [
        (inicio + timedelta(days=30 * i)).isoformat() for i in range(3)
    ]
    assert dados["ciclos"][0]["papel"] == "GESTOR"
    assert all(c["papel"] == "PARTICIPANTE" for c in dados["ciclos"][1:])
    assert client.get(caminho, headers=headers(participante)).json() == dados
    assert client.get(caminho, headers=headers(externo)).status_code == 404

    db = SessionLocal()
    try:
        db.get(Grupo, grupo["id"]).data_inicio = inicio - timedelta(days=100)
        db.commit()
    finally:
        db.close()
    apos_datas_previstas = client.get(caminho, headers=headers(gestor)).json()
    assert apos_datas_previstas["ciclo_atual"] == 1
    assert [c["situacao"] for c in apos_datas_previstas["ciclos"]] == [
        "ATUAL", "PROXIMO", "PROXIMO"
    ]


@pytest.mark.parametrize("estado", ["RASCUNHO", "CANCELADO", "ATIVO"])
def test_estado_incorreto_impede_sorteio(contexto, estado):
    gestor = contexto[0]
    grupo, _ = criar_grupo(gestor)
    db = SessionLocal()
    try:
        db.get(Grupo, grupo["id"]).status = estado
        db.commit()
    finally:
        db.close()
    assert client.post(f"/groups/{grupo['id']}/draw", headers=headers(gestor)).status_code == 409


def test_sorteios_concorrentes_tem_um_unico_vencedor(contexto):
    gestor = contexto[0]
    grupo, _ = preparar_grupo(contexto)
    barreira = Barrier(2)

    def sortear(_):
        with TestClient(app) as cliente:
            barreira.wait()
            return cliente.post(
                f"/groups/{grupo['id']}/draw", headers=headers(gestor),
            ).status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        resultados = list(executor.map(sortear, range(2)))
    assert sorted(resultados) == [200, 409]
    ordem = client.get(f"/groups/{grupo['id']}", headers=headers(gestor)).json()["ordem_recebimento"]
    assert [item["posicao"] for item in ordem] == [1, 2, 3]
