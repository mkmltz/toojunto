from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.auth.security import criar_token_acesso, gerar_hash_senha
from app.db import SessionLocal
from app.groups.schemas import GrupoAtualizacao, GrupoCriacao
from app.groups.service import atualizar_grupo, cancelar_grupo, criar_grupo
from app.main import app
from app.models import Convite, Grupo, Participante, Usuario


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
            db.execute(delete(Convite).where(Convite.grupo_id.in_(ids_grupos)))
            db.execute(
                delete(Participante).where(
                    Participante.grupo_id.in_(ids_grupos)
                )
            )
            db.execute(delete(Grupo).where(Grupo.id.in_(ids_grupos)))
        db.delete(novo_usuario)
        db.commit()
        db.close()


@pytest.fixture
def outro_usuario():
    db = SessionLocal()
    novo_usuario = Usuario(
        nome="Outro usuário de teste",
        email=f"outro-grupo-{uuid4()}@example.com",
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
        db.execute(
            delete(Participante).where(
                Participante.usuario_id == novo_usuario.id
            )
        )
        if ids_grupos:
            db.execute(delete(Convite).where(Convite.grupo_id.in_(ids_grupos)))
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


def criar_grupo_via_api(usuario: Usuario, **sobrescritas) -> dict:
    response = client.post(
        "/groups",
        json=dados_grupo(**sobrescritas),
        headers=cabecalho_autorizacao(usuario),
    )
    assert response.status_code == 201
    return response.json()


def associar_usuario_ao_grupo(
    usuario: Usuario,
    grupo_id: int,
    status_participante: str = "ATIVO",
) -> None:
    db = SessionLocal()
    try:
        db.add(
            Participante(
                grupo_id=grupo_id,
                usuario_id=usuario.id,
                status=status_participante,
            )
        )
        db.commit()
    finally:
        db.close()


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


def test_gestor_edita_campos_e_backend_recalcula_derivados(usuario):
    grupo = criar_grupo_via_api(usuario)
    nova_data = date.today() + timedelta(days=5)

    response = client.patch(
        f"/groups/{grupo['id']}",
        json={
            "nome": "  Caixinha Atualizada  ",
            "valor_cota": "125.50",
            "quantidade_participantes": 8,
            "data_inicio": nova_data.isoformat(),
        },
        headers=cabecalho_autorizacao(usuario),
    )

    assert response.status_code == 200
    assert response.json()["nome"] == "Caixinha Atualizada"
    assert response.json()["valor_cota"] == "125.50"
    assert response.json()["valor_premio"] == "1004.00"
    assert response.json()["quantidade_participantes"] == 8
    assert response.json()["quantidade_ciclos"] == 8
    assert response.json()["data_inicio"] == nova_data.isoformat()
    assert response.json()["status"] == "RASCUNHO"


def test_edicao_parcial_preserva_campos_nao_informados(usuario):
    grupo = criar_grupo_via_api(usuario)

    response = client.patch(
        f"/groups/{grupo['id']}",
        json={"nome": "Novo nome"},
        headers=cabecalho_autorizacao(usuario),
    )

    assert response.status_code == 200
    assert response.json()["nome"] == "Novo nome"
    assert response.json()["valor_cota"] == grupo["valor_cota"]
    assert response.json()["valor_premio"] == grupo["valor_premio"]
    assert response.json()["quantidade_participantes"] == 10
    assert response.json()["quantidade_ciclos"] == 10
    assert response.json()["data_inicio"] == grupo["data_inicio"]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"nome": None},
        {"nome": " "},
        {"valor_cota": "0"},
        {"valor_cota": "10.001"},
        {"quantidade_participantes": 1},
        {"data_inicio": (date.today() - timedelta(days=1)).isoformat()},
        {"data_inicio": "data-invalida"},
        {"valor_premio": "1.00"},
        {"quantidade_ciclos": 4},
        {"gestor_id": 999},
        {"status": "ATIVO"},
        {"campo_desconhecido": "valor"},
    ],
)
def test_edicao_rejeita_payload_invalido_ou_campo_controlado(usuario, payload):
    grupo = criar_grupo_via_api(usuario)

    response = client.patch(
        f"/groups/{grupo['id']}",
        json=payload,
        headers=cabecalho_autorizacao(usuario),
    )

    assert response.status_code == 422


def test_quantidade_nao_pode_ser_menor_que_participantes_associados(usuario):
    grupo = criar_grupo_via_api(
        usuario,
        quantidade_participantes=4,
        quantidade_ciclos=4,
    )
    db = SessionLocal()
    associados = [
        Usuario(
            nome=f"Participante associado {indice}",
            email=f"associado-{uuid4()}@example.com",
            senha_hash=gerar_hash_senha("senha-segura"),
        )
        for indice in range(2)
    ]
    db.add_all(associados)
    db.flush()
    db.add_all(
        [
        Participante(
            grupo_id=grupo["id"],
            usuario_id=associado.id,
            status="ATIVO",
        )
            for associado in associados
        ]
    )
    db.commit()

    try:
        response = client.patch(
            f"/groups/{grupo['id']}",
            json={"quantidade_participantes": 2},
            headers=cabecalho_autorizacao(usuario),
        )
        assert response.status_code == 409

        response = client.patch(
            f"/groups/{grupo['id']}",
            json={"quantidade_participantes": 3},
            headers=cabecalho_autorizacao(usuario),
        )
        assert response.status_code == 200
    finally:
        db.execute(
            delete(Participante).where(
                Participante.usuario_id.in_(
                    [associado.id for associado in associados]
                )
            )
        )
        for associado in associados:
            db.delete(associado)
        db.commit()
        db.close()


def test_usuario_que_nao_e_gestor_nao_pode_editar_ou_cancelar(usuario):
    grupo = criar_grupo_via_api(usuario)
    db = SessionLocal()
    outro = Usuario(
        nome="Outro usuário",
        email=f"outro-{uuid4()}@example.com",
        senha_hash=gerar_hash_senha("senha-segura"),
    )
    db.add(outro)
    db.commit()
    db.refresh(outro)

    try:
        editar = client.patch(
            f"/groups/{grupo['id']}",
            json={"nome": "Tentativa indevida"},
            headers=cabecalho_autorizacao(outro),
        )
        cancelar = client.post(
            f"/groups/{grupo['id']}/cancel",
            headers=cabecalho_autorizacao(outro),
        )
        assert editar.status_code == 403
        assert cancelar.status_code == 403
    finally:
        db.delete(outro)
        db.commit()
        db.close()


def test_grupo_inexistente_retorna_404_na_edicao_e_cancelamento(usuario):
    headers = cabecalho_autorizacao(usuario)

    editar = client.patch(
        "/groups/999999999",
        json={"nome": "Grupo inexistente"},
        headers=headers,
    )
    cancelar = client.post("/groups/999999999/cancel", headers=headers)

    assert editar.status_code == 404
    assert cancelar.status_code == 404


def test_edicao_e_cancelamento_exigem_autenticacao(usuario):
    grupo = criar_grupo_via_api(usuario)

    editar = client.patch(
        f"/groups/{grupo['id']}",
        json={"nome": "Sem autenticação"},
    )
    cancelar = client.post(f"/groups/{grupo['id']}/cancel")

    assert editar.status_code == 401
    assert cancelar.status_code == 401


def test_cancelamento_e_logico_e_retorna_grupo_atualizado(usuario):
    grupo = criar_grupo_via_api(usuario)

    response = client.post(
        f"/groups/{grupo['id']}/cancel",
        headers=cabecalho_autorizacao(usuario),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "CANCELADO"
    db = SessionLocal()
    try:
        persistido = db.get(Grupo, grupo["id"])
        participante = db.scalar(
            select(Participante).where(Participante.grupo_id == grupo["id"])
        )
        assert persistido is not None
        assert persistido.status == "CANCELADO"
        assert participante is not None
    finally:
        db.close()


def test_grupo_cancelado_nao_pode_ser_editado_nem_cancelado_novamente(usuario):
    grupo = criar_grupo_via_api(usuario)
    headers = cabecalho_autorizacao(usuario)
    primeira_resposta = client.post(
        f"/groups/{grupo['id']}/cancel",
        headers=headers,
    )
    assert primeira_resposta.status_code == 200

    editar = client.patch(
        f"/groups/{grupo['id']}",
        json={"nome": "Não permitido"},
        headers=headers,
    )
    cancelar = client.post(f"/groups/{grupo['id']}/cancel", headers=headers)

    assert editar.status_code == 409
    assert cancelar.status_code == 409


def test_atualizacao_faz_rollback_quando_persistencia_falha(usuario, monkeypatch):
    grupo = Grupo(
        id=123,
        nome="Grupo",
        gestor_id=usuario.id,
        valor_cota=Decimal("100.00"),
        valor_premio=Decimal("200.00"),
        quantidade_participantes=2,
        quantidade_ciclos=2,
        data_inicio=date.today(),
        status="RASCUNHO",
    )
    db = MagicMock()
    db.scalar.return_value = 1
    db.commit.side_effect = RuntimeError("falha de persistência")
    monkeypatch.setattr(
        "app.groups.service._buscar_grupo_gerenciavel",
        lambda *_: grupo,
    )

    with pytest.raises(RuntimeError, match="falha de persistência"):
        atualizar_grupo(
            grupo.id,
            GrupoAtualizacao(nome="Nome atualizado"),
            usuario,
            db,
        )

    db.rollback.assert_called_once_with()


def test_cancelamento_faz_rollback_quando_persistencia_falha(usuario, monkeypatch):
    grupo = Grupo(
        id=123,
        nome="Grupo",
        gestor_id=usuario.id,
        valor_cota=Decimal("100.00"),
        valor_premio=Decimal("200.00"),
        quantidade_participantes=2,
        quantidade_ciclos=2,
        data_inicio=date.today(),
        status="RASCUNHO",
    )
    db = MagicMock()
    db.commit.side_effect = RuntimeError("falha de persistência")
    monkeypatch.setattr(
        "app.groups.service._buscar_grupo_gerenciavel",
        lambda *_: grupo,
    )

    with pytest.raises(RuntimeError, match="falha de persistência"):
        cancelar_grupo(grupo.id, usuario, db)

    db.rollback.assert_called_once_with()


def test_listagem_retorna_grupo_do_gestor_com_papel_gestor(usuario):
    grupo = criar_grupo_via_api(usuario)

    response = client.get(
        "/groups",
        headers=cabecalho_autorizacao(usuario),
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            **grupo,
            "papel": "GESTOR",
            "vagas_disponiveis": 9,
        }
    ]


def test_listagem_retorna_grupo_associado_com_papel_participante(
    usuario,
    outro_usuario,
):
    grupo = criar_grupo_via_api(usuario)
    associar_usuario_ao_grupo(outro_usuario, grupo["id"])

    response = client.get(
        "/groups",
        headers=cabecalho_autorizacao(outro_usuario),
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            **grupo,
            "papel": "PARTICIPANTE",
            "vagas_disponiveis": 8,
        }
    ]


@pytest.mark.parametrize("estado", ["RASCUNHO", "SORTEIO", "CANCELADO"])
def test_listagem_informa_grupo_completo_para_gestor_e_participante(
    usuario,
    outro_usuario,
    estado,
):
    grupo = criar_grupo_via_api(
        usuario, quantidade_participantes=2, quantidade_ciclos=2,
    )
    associar_usuario_ao_grupo(outro_usuario, grupo["id"])
    db = SessionLocal()
    try:
        db.get(Grupo, grupo["id"]).status = estado
        db.commit()
    finally:
        db.close()

    for pessoa, papel in [(usuario, "GESTOR"), (outro_usuario, "PARTICIPANTE")]:
        resposta = client.get("/groups", headers=cabecalho_autorizacao(pessoa))
        assert resposta.status_code == 200
        assert resposta.json()[0]["status"] == estado
        assert resposta.json()[0]["papel"] == papel
        assert resposta.json()[0]["vagas_disponiveis"] == 0


def test_listagem_conta_associacao_inativa_como_vaga_ocupada(
    usuario,
    outro_usuario,
):
    grupo = criar_grupo_via_api(
        usuario, quantidade_participantes=2, quantidade_ciclos=2,
    )
    associar_usuario_ao_grupo(outro_usuario, grupo["id"], "INATIVO")

    resposta = client.get("/groups", headers=cabecalho_autorizacao(usuario))

    assert resposta.status_code == 200
    assert resposta.json()[0]["vagas_disponiveis"] == 0


def test_listagem_nao_retorna_grupo_sem_participacao_ativa(
    usuario,
    outro_usuario,
):
    grupo = criar_grupo_via_api(usuario)
    associar_usuario_ao_grupo(
        outro_usuario,
        grupo["id"],
        status_participante="INATIVO",
    )

    response = client.get(
        "/groups",
        headers=cabecalho_autorizacao(outro_usuario),
    )

    assert response.status_code == 200
    assert response.json() == []


def test_listagem_nao_duplica_grupo_com_associacoes_ativas_repetidas(
    usuario,
    outro_usuario,
):
    grupo = criar_grupo_via_api(usuario)
    associar_usuario_ao_grupo(outro_usuario, grupo["id"])
    associar_usuario_ao_grupo(outro_usuario, grupo["id"])

    response = client.get(
        "/groups",
        headers=cabecalho_autorizacao(outro_usuario),
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == grupo["id"]


def test_listagem_inclui_grupo_cancelado(usuario):
    grupo = criar_grupo_via_api(usuario)
    cancelar = client.post(
        f"/groups/{grupo['id']}/cancel",
        headers=cabecalho_autorizacao(usuario),
    )
    assert cancelar.status_code == 200

    response = client.get(
        "/groups",
        headers=cabecalho_autorizacao(usuario),
    )

    assert response.status_code == 200
    assert response.json()[0]["id"] == grupo["id"]
    assert response.json()[0]["status"] == "CANCELADO"


def test_listagem_ordena_por_criacao_e_id_decrescentes(usuario):
    primeiro = criar_grupo_via_api(usuario, nome="Primeiro grupo")
    segundo = criar_grupo_via_api(usuario, nome="Segundo grupo")
    db = SessionLocal()
    try:
        grupo_primeiro = db.get(Grupo, primeiro["id"])
        grupo_segundo = db.get(Grupo, segundo["id"])
        grupo_segundo.created_at = grupo_primeiro.created_at
        db.commit()
    finally:
        db.close()

    response = client.get(
        "/groups",
        headers=cabecalho_autorizacao(usuario),
    )

    assert response.status_code == 200
    assert [grupo["id"] for grupo in response.json()] == [
        segundo["id"],
        primeiro["id"],
    ]


def test_detalhe_retorna_papel_gestor_para_proprietario(usuario):
    grupo = criar_grupo_via_api(usuario)

    response = client.get(
        f"/groups/{grupo['id']}",
        headers=cabecalho_autorizacao(usuario),
    )

    assert response.status_code == 200
    assert response.json() == {
        **grupo,
        "papel": "GESTOR",
        "formacao": {
            "quantidade_atual": 1,
            "limite": 10,
            "vagas_disponiveis": 9,
            "participantes": [
                {"nome": usuario.nome, "papel": "GESTOR"},
            ],
        },
    }


def test_detalhe_retorna_papel_participante_para_associado_ativo(
    usuario,
    outro_usuario,
):
    grupo = criar_grupo_via_api(usuario)
    associar_usuario_ao_grupo(outro_usuario, grupo["id"])

    response = client.get(
        f"/groups/{grupo['id']}",
        headers=cabecalho_autorizacao(outro_usuario),
    )

    assert response.status_code == 200
    assert response.json() == {
        **grupo,
        "papel": "PARTICIPANTE",
        "formacao": {
            "quantidade_atual": 2,
            "limite": 10,
            "vagas_disponiveis": 8,
            "participantes": [
                {"nome": usuario.nome, "papel": "GESTOR"},
                {
                    "nome": outro_usuario.nome,
                    "papel": "PARTICIPANTE",
                },
            ],
        },
    }


def test_detalhe_contabiliza_associacao_inativa_na_formacao(
    usuario,
    outro_usuario,
):
    grupo = criar_grupo_via_api(usuario)
    associar_usuario_ao_grupo(
        outro_usuario,
        grupo["id"],
        status_participante="INATIVO",
    )

    response = client.get(
        f"/groups/{grupo['id']}",
        headers=cabecalho_autorizacao(usuario),
    )

    assert response.status_code == 200
    assert response.json()["formacao"] == {
        "quantidade_atual": 2,
        "limite": 10,
        "vagas_disponiveis": 8,
        "participantes": [
            {"nome": usuario.nome, "papel": "GESTOR"},
            {"nome": outro_usuario.nome, "papel": "PARTICIPANTE"},
        ],
    }


def test_detalhe_de_grupo_completo_retorna_zero_vagas(
    usuario,
    outro_usuario,
):
    grupo = criar_grupo_via_api(
        usuario,
        quantidade_participantes=2,
        quantidade_ciclos=2,
    )
    associar_usuario_ao_grupo(outro_usuario, grupo["id"])

    response = client.get(
        f"/groups/{grupo['id']}",
        headers=cabecalho_autorizacao(usuario),
    )

    assert response.status_code == 200
    assert response.json()["formacao"]["quantidade_atual"] == 2
    assert response.json()["formacao"]["limite"] == 2
    assert response.json()["formacao"]["vagas_disponiveis"] == 0


def test_detalhe_retorna_404_para_usuario_externo_ou_inativo(
    usuario,
    outro_usuario,
):
    grupo = criar_grupo_via_api(usuario)

    externo = client.get(
        f"/groups/{grupo['id']}",
        headers=cabecalho_autorizacao(outro_usuario),
    )
    associar_usuario_ao_grupo(
        outro_usuario,
        grupo["id"],
        status_participante="INATIVO",
    )
    inativo = client.get(
        f"/groups/{grupo['id']}",
        headers=cabecalho_autorizacao(outro_usuario),
    )

    assert externo.status_code == 404
    assert inativo.status_code == 404


def test_detalhe_retorna_404_para_grupo_inexistente(usuario):
    response = client.get(
        "/groups/999999999",
        headers=cabecalho_autorizacao(usuario),
    )

    assert response.status_code == 404


@pytest.mark.parametrize("caminho", ["/groups", "/groups/1"])
def test_consultas_de_grupo_exigem_autenticacao(caminho):
    response = client.get(caminho)

    assert response.status_code == 401


@pytest.mark.parametrize("caminho", ["/groups", "/groups/1"])
def test_consultas_de_grupo_rejeitam_token_invalido(caminho):
    response = client.get(
        caminho,
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert response.status_code == 401
