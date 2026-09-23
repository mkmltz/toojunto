from concurrent.futures import ThreadPoolExecutor
from datetime import date
from decimal import Decimal
from threading import Barrier
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.auth.security import criar_token_acesso, gerar_hash_senha
from app.db import SessionLocal
from app.main import app
from app.models import Convite, Grupo, Participante, Usuario
from app.invites.service import aceitar_convite


client = TestClient(app)


@pytest.fixture
def contexto_convite():
    db = SessionLocal()
    usuarios = [
        Usuario(
            nome=nome,
            email=f"us006-{uuid4()}@example.com",
            senha_hash=gerar_hash_senha("senha-segura"),
        )
        for nome in ["Gestor", "Convidado A", "Convidado B", "Convidado C"]
    ]
    db.add_all(usuarios)
    db.commit()
    for usuario in usuarios:
        db.refresh(usuario)

    try:
        yield usuarios
    finally:
        ids_usuarios = [usuario.id for usuario in usuarios]
        grupos = db.scalars(
            select(Grupo).where(Grupo.gestor_id.in_(ids_usuarios))
        ).all()
        ids_grupos = [grupo.id for grupo in grupos]
        if ids_grupos:
            db.execute(delete(Convite).where(Convite.grupo_id.in_(ids_grupos)))
            db.execute(
                delete(Participante).where(Participante.grupo_id.in_(ids_grupos))
            )
            db.execute(delete(Grupo).where(Grupo.id.in_(ids_grupos)))
        db.execute(
            delete(Participante).where(
                Participante.usuario_id.in_(ids_usuarios)
            )
        )
        db.execute(delete(Usuario).where(Usuario.id.in_(ids_usuarios)))
        db.commit()
        db.close()


def headers(usuario: Usuario) -> dict[str, str]:
    return {"Authorization": f"Bearer {criar_token_acesso(usuario.id)}"}


def criar_grupo_e_convite(
    gestor: Usuario,
    quantidade_participantes: int = 3,
) -> tuple[dict, dict]:
    grupo = client.post(
        "/groups",
        json={
            "nome": "Grupo convidado",
            "valor_cota": "150.00",
            "quantidade_participantes": quantidade_participantes,
            "quantidade_ciclos": quantidade_participantes,
            "data_inicio": date.today().isoformat(),
        },
        headers=headers(gestor),
    )
    assert grupo.status_code == 201
    convite = client.post(
        f"/groups/{grupo.json()['id']}/invite",
        headers=headers(gestor),
    )
    assert convite.status_code == 200
    return grupo.json(), convite.json()


def associar_usuario(
    grupo_id: int,
    usuario: Usuario,
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


def alterar_status_grupo(grupo_id: int, status_grupo: str) -> None:
    db = SessionLocal()
    try:
        grupo = db.get(Grupo, grupo_id)
        grupo.status = status_grupo
        db.commit()
    finally:
        db.close()


def test_consulta_publica_retorna_somente_dados_essenciais(contexto_convite):
    gestor, *_ = contexto_convite
    _, convite = criar_grupo_e_convite(gestor)

    response = client.get(f"/invites/{convite['token']}")

    assert response.status_code == 200
    assert response.json() == {
        "group_name": "Grupo convidado",
        "manager_name": "Gestor",
        "quota_value": "150.00",
        "participant_limit": 3,
        "available_slots": 2,
        "start_date": date.today().isoformat(),
    }
    assert "email" not in response.json()
    assert "telefone" not in response.json()
    assert "gestor_id" not in response.json()


def test_consultar_convite_nao_cria_participacao(contexto_convite):
    gestor, convidado, *_ = contexto_convite
    grupo, convite = criar_grupo_e_convite(gestor)

    response = client.get(f"/invites/{convite['token']}")

    assert response.status_code == 200
    db = SessionLocal()
    try:
        participacao = db.scalar(
            select(Participante).where(
                Participante.grupo_id == grupo["id"],
                Participante.usuario_id == convidado.id,
            )
        )
        assert participacao is None
    finally:
        db.close()


@pytest.mark.parametrize("status_grupo", ["CANCELADO", "FORMANDO", "SORTEIO", "ATIVO", "ENCERRADO"])
def test_consulta_oculta_convite_de_grupo_indisponivel(
    contexto_convite,
    status_grupo,
):
    gestor, *_ = contexto_convite
    grupo, convite = criar_grupo_e_convite(gestor)
    alterar_status_grupo(grupo["id"], status_grupo)

    response = client.get(f"/invites/{convite['token']}")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Convite não encontrado ou indisponível."
    }


def test_consulta_oculta_token_inexistente(contexto_convite):
    response = client.get("/invites/token-inexistente")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Convite não encontrado ou indisponível."
    }


def test_toda_associacao_ocupa_vaga_inclusive_inativa(contexto_convite):
    gestor, associado_inativo, *_ = contexto_convite
    grupo, convite = criar_grupo_e_convite(gestor, quantidade_participantes=2)
    associar_usuario(grupo["id"], associado_inativo, "INATIVO")

    response = client.get(f"/invites/{convite['token']}")

    assert response.status_code == 404


def test_usuario_autenticado_aceita_e_passa_a_visualizar_grupo(contexto_convite):
    gestor, convidado, *_ = contexto_convite
    grupo, convite = criar_grupo_e_convite(gestor)

    response = client.post(
        f"/invites/{convite['token']}/accept",
        headers=headers(convidado),
    )

    assert response.status_code == 200
    assert response.json()["group_id"] == grupo["id"]
    assert response.json()["status"] == "ATIVO"
    detalhe = client.get(f"/groups/{grupo['id']}", headers=headers(convidado))
    assert detalhe.status_code == 200
    assert detalhe.json()["papel"] == "PARTICIPANTE"

    db = SessionLocal()
    try:
        participante = db.get(Participante, response.json()["participant_id"])
        assert participante is not None
        assert participante.usuario_id == convidado.id
        assert participante.ordem_sorteio is None
    finally:
        db.close()


def test_aceite_exige_autenticacao(contexto_convite):
    gestor, *_ = contexto_convite
    _, convite = criar_grupo_e_convite(gestor)
    response = client.post(f"/invites/{convite['token']}/accept")
    assert response.status_code == 401


def test_token_inexistente_nao_pode_ser_aceito(contexto_convite):
    _, convidado, *_ = contexto_convite
    response = client.post(
        "/invites/token-inexistente/accept",
        headers=headers(convidado),
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Convite não encontrado."}


@pytest.mark.parametrize("status_grupo", ["CANCELADO", "FORMANDO", "SORTEIO", "ATIVO", "ENCERRADO"])
def test_grupo_fora_de_rascunho_impede_aceite(
    contexto_convite,
    status_grupo,
):
    gestor, convidado, *_ = contexto_convite
    grupo, convite = criar_grupo_e_convite(gestor)
    alterar_status_grupo(grupo["id"], status_grupo)

    response = client.post(
        f"/invites/{convite['token']}/accept",
        headers=headers(convidado),
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Este Grupo não permite mais entradas."
    }


@pytest.mark.parametrize("status_associado", ["ATIVO", "INATIVO"])
def test_grupo_lotado_impede_aceite(contexto_convite, status_associado):
    gestor, associado, convidado, _ = contexto_convite
    grupo, convite = criar_grupo_e_convite(gestor, quantidade_participantes=2)
    associar_usuario(grupo["id"], associado, status_associado)

    response = client.post(
        f"/invites/{convite['token']}/accept",
        headers=headers(convidado),
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Este Grupo não possui vagas disponíveis."
    }


def test_participante_nao_pode_aceitar_novamente(contexto_convite):
    gestor, convidado, *_ = contexto_convite
    grupo, convite = criar_grupo_e_convite(gestor)
    associar_usuario(grupo["id"], convidado)

    response = client.post(
        f"/invites/{convite['token']}/accept",
        headers=headers(convidado),
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Você já participa deste Grupo."}


def test_gestor_nao_pode_aceitar_o_proprio_convite(contexto_convite):
    gestor, *_ = contexto_convite
    _, convite = criar_grupo_e_convite(gestor)

    response = client.post(
        f"/invites/{convite['token']}/accept",
        headers=headers(gestor),
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Você já participa deste Grupo."}


def test_chamada_repetida_nao_cria_participacao_duplicada(contexto_convite):
    gestor, convidado, *_ = contexto_convite
    grupo, convite = criar_grupo_e_convite(gestor)
    caminho = f"/invites/{convite['token']}/accept"

    primeira = client.post(caminho, headers=headers(convidado))
    segunda = client.post(caminho, headers=headers(convidado))

    assert primeira.status_code == 200
    assert segunda.status_code == 409
    db = SessionLocal()
    try:
        participacoes = db.scalars(
            select(Participante).where(
                Participante.grupo_id == grupo["id"],
                Participante.usuario_id == convidado.id,
            )
        ).all()
        assert len(participacoes) == 1
    finally:
        db.close()


def test_aceites_concorrentes_nao_ultrapassam_ultima_vaga(contexto_convite):
    gestor, convidado_a, convidado_b, _ = contexto_convite
    grupo, convite = criar_grupo_e_convite(gestor, quantidade_participantes=2)
    barreira = Barrier(2)

    def aceitar(usuario: Usuario) -> int:
        with TestClient(app) as cliente:
            barreira.wait()
            return cliente.post(
                f"/invites/{convite['token']}/accept",
                headers=headers(usuario),
            ).status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        resultados = list(executor.map(aceitar, [convidado_a, convidado_b]))

    assert sorted(resultados) == [200, 409]
    db = SessionLocal()
    try:
        participantes = db.scalars(
            select(Participante).where(Participante.grupo_id == grupo["id"])
        ).all()
        assert len(participantes) == grupo["quantidade_participantes"]
    finally:
        db.close()


def test_aceite_faz_rollback_quando_persistencia_falha(contexto_convite):
    gestor, convidado, *_ = contexto_convite
    grupo = Grupo(
        id=123,
        nome="Grupo",
        gestor_id=gestor.id,
        valor_cota=Decimal("100.00"),
        valor_premio=Decimal("200.00"),
        quantidade_participantes=2,
        quantidade_ciclos=2,
        data_inicio=date.today(),
        status="RASCUNHO",
    )
    db = MagicMock()
    db.scalar.side_effect = [grupo, None, 1]
    db.commit.side_effect = RuntimeError("falha de persistência")

    with pytest.raises(RuntimeError, match="falha de persistência"):
        aceitar_convite("token", convidado, db)

    db.rollback.assert_called_once_with()
