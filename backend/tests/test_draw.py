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
from app.models import Ciclo, Convite, Grupo, Pagamento, Participante, Usuario


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
            ids_ciclos = db.scalars(select(Ciclo.id).where(Ciclo.grupo_id.in_(ids_grupos))).all()
            if ids_ciclos:
                db.execute(delete(Pagamento).where(Pagamento.ciclo_id.in_(ids_ciclos)))
                db.execute(delete(Ciclo).where(Ciclo.id.in_(ids_ciclos)))
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


def test_us011_obrigacoes_autorizacao_e_declaracao(contexto):
    gestor, pagador, outro, externo = contexto
    grupo, inicio = preparar_grupo(contexto)
    caminho = f"/groups/{grupo['id']}/cycles/1/payments"
    assert client.get(caminho, headers=headers(gestor)).status_code == 409
    assert client.post(caminho, headers=headers(pagador)).status_code == 409
    assert client.get(caminho, headers=headers(externo)).status_code == 404
    assert client.post(caminho, headers=headers(externo)).status_code == 404
    assert client.get(caminho).status_code == 401
    assert client.post(f"/groups/{grupo['id']}/cycles/2/payments", headers=headers(pagador)).status_code == 409

    assert client.post(f"/groups/{grupo['id']}/draw", headers=headers(gestor)).status_code == 200
    obrigacoes = client.get(caminho, headers=headers(gestor)).json()
    assert len(obrigacoes) == 2
    assert {o["pagador_nome"] for o in obrigacoes} == {"Pessoa A", "Pessoa B"}
    assert {o["pagador_usuario_id"] for o in obrigacoes} == {pagador.id, outro.id}
    assert all(o["recebedor_nome"] == "Gestor" for o in obrigacoes)
    assert all(o["valor"] == "100.00" for o in obrigacoes)
    assert all(o["prazo_pagamento"] == (inicio - timedelta(days=5)).isoformat() for o in obrigacoes)
    assert all(o["dias_ate_prazo"] == (inicio - date.today()).days - 5 for o in obrigacoes)
    assert all(o["situacao"] == "PENDENTE" and o["status_registro"] is None for o in obrigacoes)
    assert client.post(caminho, headers=headers(gestor)).status_code == 409
    assert client.post(caminho, headers=headers(pagador), json={"valor": "1.00"}).status_code == 422
    assert client.post(caminho, headers=headers(pagador), json={"pagador_id": 999}).status_code == 422
    resposta_pagamento = client.post(caminho, headers=headers(pagador))
    assert resposta_pagamento.status_code == 201
    assert resposta_pagamento.json()["pagador_usuario_id"] == pagador.id
    declaracao = client.get(caminho, headers=headers(outro)).json()
    propria = next(o for o in declaracao if o["pagador_nome"] == "Pessoa A")
    assert propria["pagador_usuario_id"] == pagador.id
    assert propria["situacao"] == "AGUARDANDO_CONFIRMACAO"
    assert propria["status_registro"] == "AGUARDANDO_CONFIRMACAO"
    assert propria["declarado_em"] is not None
    assert client.post(caminho, headers=headers(pagador)).status_code == 409
    assert client.get(f"/groups/{grupo['id']}/cycles", headers=headers(gestor)).json()["ciclo_atual"] == 1
    db = SessionLocal()
    try:
        participante_pagador = db.scalar(select(Participante).where(
            Participante.grupo_id == grupo["id"], Participante.usuario_id == pagador.id
        ))
        assert propria["pagador_id"] == participante_pagador.id
        assert resposta_pagamento.json()["pagador_id"] == participante_pagador.id
        registro = db.scalar(select(Pagamento).join(Ciclo).where(Ciclo.grupo_id == grupo["id"]))
        assert registro.pagador_id == propria["pagador_id"]
        assert registro.recebedor_id == propria["recebedor_id"]
        assert str(registro.valor) == "100.00"
    finally:
        db.close()


def test_us011_prazo_alerta_e_atraso(contexto):
    gestor, pagador, _, _ = contexto
    grupo, _ = preparar_grupo(contexto)
    assert client.post(f"/groups/{grupo['id']}/draw", headers=headers(gestor)).status_code == 200
    caminho = f"/groups/{grupo['id']}/cycles/1/payments"
    db = SessionLocal()
    try:
        db.get(Grupo, grupo["id"]).data_inicio = date.today() + timedelta(days=5)
        db.commit()
    finally:
        db.close()
    obrigacao = client.get(caminho, headers=headers(pagador)).json()[0]
    assert obrigacao["dias_ate_data_prevista"] == 5
    assert obrigacao["dias_ate_prazo"] == 0
    assert obrigacao["alerta_prazo"] is True
    db = SessionLocal()
    try:
        db.get(Grupo, grupo["id"]).data_inicio = date.today() + timedelta(days=2)
        db.commit()
    finally:
        db.close()
    obrigacao = client.get(caminho, headers=headers(pagador)).json()[0]
    assert obrigacao["dias_ate_data_prevista"] == 2
    assert obrigacao["alerta_prazo"] is True
    db = SessionLocal()
    try:
        db.get(Grupo, grupo["id"]).data_inicio = date.today() - timedelta(days=2)
        db.commit()
    finally:
        db.close()
    obrigacao = client.get(caminho, headers=headers(pagador)).json()[0]
    assert obrigacao["situacao"] == "ATRASADO"
    assert obrigacao["dias_ate_data_prevista"] == -2
    assert obrigacao["alerta_prazo"] is False
    assert client.post(caminho, headers=headers(pagador)).status_code == 201
    declarada = client.get(caminho, headers=headers(pagador)).json()[0]
    assert declarada["situacao"] == "ATRASADO"
    assert declarada["status_registro"] == "AGUARDANDO_CONFIRMACAO"


def test_us011_declaracoes_concorrentes_nao_duplicam(contexto):
    gestor, pagador, _, _ = contexto
    grupo, _ = preparar_grupo(contexto)
    assert client.post(f"/groups/{grupo['id']}/draw", headers=headers(gestor)).status_code == 200
    caminho = f"/groups/{grupo['id']}/cycles/1/payments"
    barreira = Barrier(2)

    def declarar(_):
        with TestClient(app) as cliente:
            barreira.wait()
            return cliente.post(caminho, headers=headers(pagador)).status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        resultados = list(executor.map(declarar, range(2)))
    assert sorted(resultados) == [201, 409]


def _pagamentos_do_ciclo(grupo_id, numero, usuarios):
    caminho = f"/groups/{grupo_id}/cycles/{numero}/payments"
    resposta = client.get(caminho, headers=headers(usuarios[0]))
    assert resposta.status_code == 200
    return caminho, resposta.json()


def test_us012_rejeicao_nova_declaracao_e_permissoes(contexto):
    gestor, pagador, terceiro, externo = contexto
    grupo, _ = preparar_grupo(contexto)
    assert client.post(f"/groups/{grupo['id']}/draw", headers=headers(gestor)).status_code == 200
    caminho, _ = _pagamentos_do_ciclo(grupo["id"], 1, contexto)
    declaracao = client.post(caminho, headers=headers(pagador)).json()
    pagamento_id = declaracao["pagamento_id"]
    rejeitar = f"{caminho}/{pagamento_id}/reject"
    confirmar = f"{caminho}/{pagamento_id}/confirm"
    assert declaracao["pode_avaliar"] is False
    assert client.get(caminho, headers=headers(gestor)).json()[0]["pode_avaliar"] is True
    assert client.post(confirmar).status_code == 401
    assert client.post(confirmar, headers=headers(externo)).status_code == 404
    assert client.post(confirmar, headers=headers(pagador)).status_code == 403
    assert client.post(confirmar, headers=headers(terceiro)).status_code == 403
    assert client.post(rejeitar, headers=headers(gestor)).json()["status_registro"] == "REJEITADO"
    assert client.post(rejeitar, headers=headers(gestor)).status_code == 409
    rejeitada = client.get(caminho, headers=headers(terceiro)).json()[0]
    assert rejeitada["situacao"] == "REJEITADO"
    assert rejeitada["pagamento_id"] == pagamento_id
    nova = client.post(caminho, headers=headers(pagador))
    assert nova.status_code == 201
    assert nova.json()["pagamento_id"] == pagamento_id
    assert nova.json()["status_registro"] == "AGUARDANDO_CONFIRMACAO"
    assert client.post(confirmar, headers=headers(gestor)).json()["situacao"] == "CONFIRMADO"
    assert client.post(confirmar, headers=headers(gestor)).status_code == 409
    assert client.get(f"/groups/{grupo['id']}/cycles", headers=headers(gestor)).json()["ciclo_atual"] == 1


def test_us012_conclusao_avanco_e_encerramento(contexto):
    gestor, primeiro, segundo, _ = contexto
    usuarios_por_nome = {u.nome: u for u in (gestor, primeiro, segundo)}
    grupo, inicio = preparar_grupo(contexto)
    sorteio = client.post(f"/groups/{grupo['id']}/draw", headers=headers(gestor)).json()
    ordem = sorteio["ordem_recebimento"]
    for numero in (1, 2, 3):
        contemplado = usuarios_por_nome[ordem[numero - 1]["nome"]]
        caminho, obrigacoes = _pagamentos_do_ciclo(grupo["id"], numero, contexto)
        assert len(obrigacoes) == 2
        assert all(o["recebedor_nome"] == contemplado.nome for o in obrigacoes)
        assert all(o["data_prevista"] == (inicio + timedelta(days=(numero - 1) * 30)).isoformat() for o in obrigacoes)
        for indice, obrigacao in enumerate(obrigacoes):
            pagador = usuarios_por_nome[obrigacao["pagador_nome"]]
            declarada = client.post(caminho, headers=headers(pagador))
            assert declarada.status_code == 201
            pagamento_id = declarada.json()["pagamento_id"]
            assert client.post(f"{caminho}/{pagamento_id}/confirm", headers=headers(gestor if contemplado != gestor else pagador)).status_code == 403
            confirmada = client.post(f"{caminho}/{pagamento_id}/confirm", headers=headers(contemplado))
            assert confirmada.status_code == 200
            assert confirmada.json()["status_registro"] == "CONFIRMADO"
            progresso = client.get(f"/groups/{grupo['id']}/cycles", headers=headers(pagador)).json()
            if indice == 0:
                assert progresso["ciclo_atual"] == numero
                assert progresso["ciclos"][numero - 1]["situacao"] == "ATUAL"
            elif numero < 3:
                assert progresso["ciclo_atual"] == numero + 1
                assert progresso["ciclos"][numero - 1]["situacao"] == "CONCLUIDO"
                assert progresso["ciclos"][numero]["situacao"] == "ATUAL"
            else:
                assert progresso["grupo_concluido"] is True
                assert all(c["situacao"] == "CONCLUIDO" for c in progresso["ciclos"])
                assert client.get(f"/groups/{grupo['id']}", headers=headers(pagador)).json()["status"] == "ENCERRADO"
        assert client.post(caminho, headers=headers(usuarios_por_nome[obrigacoes[0]["pagador_nome"]])).status_code == 409
    db = SessionLocal()
    try:
        ciclos = db.scalars(select(Ciclo).where(Ciclo.grupo_id == grupo["id"]).order_by(Ciclo.numero)).all()
        assert [c.numero for c in ciclos] == [1, 2, 3]
        assert all(c.status == "CONCLUIDO" for c in ciclos)
    finally:
        db.close()


def test_us012_confirmacoes_concorrentes_avancam_uma_vez(contexto):
    gestor, primeiro, segundo, _ = contexto
    grupo, _ = preparar_grupo(contexto)
    assert client.post(f"/groups/{grupo['id']}/draw", headers=headers(gestor)).status_code == 200
    caminho, _ = _pagamentos_do_ciclo(grupo["id"], 1, contexto)
    ids = [client.post(caminho, headers=headers(usuario)).json()["pagamento_id"] for usuario in (primeiro, segundo)]
    barreira = Barrier(2)

    def confirmar(pagamento_id):
        with TestClient(app) as cliente:
            barreira.wait()
            return cliente.post(f"{caminho}/{pagamento_id}/confirm", headers=headers(gestor)).status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        resultados = list(executor.map(confirmar, ids))
    assert resultados == [200, 200]
    progresso = client.get(f"/groups/{grupo['id']}/cycles", headers=headers(gestor)).json()
    assert progresso["ciclo_atual"] == 2
    db = SessionLocal()
    try:
        ciclos = db.scalars(select(Ciclo).where(Ciclo.grupo_id == grupo["id"])).all()
        assert sorted(c.numero for c in ciclos) == [1, 2]
    finally:
        db.close()


def test_us012_confirmacao_repetida_concorrente_nao_antecipa_ciclo(contexto):
    gestor, pagador, _, _ = contexto
    grupo, _ = preparar_grupo(contexto)
    assert client.post(f"/groups/{grupo['id']}/draw", headers=headers(gestor)).status_code == 200
    caminho, _ = _pagamentos_do_ciclo(grupo["id"], 1, contexto)
    pagamento_id = client.post(caminho, headers=headers(pagador)).json()["pagamento_id"]
    barreira = Barrier(2)

    def confirmar(_):
        with TestClient(app) as cliente:
            barreira.wait()
            return cliente.post(f"{caminho}/{pagamento_id}/confirm", headers=headers(gestor)).status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        resultados = list(executor.map(confirmar, range(2)))
    assert sorted(resultados) == [200, 409]
    progresso = client.get(f"/groups/{grupo['id']}/cycles", headers=headers(gestor)).json()
    assert progresso["ciclo_atual"] == 1
    assert progresso["ciclos"][0]["situacao"] == "ATUAL"
