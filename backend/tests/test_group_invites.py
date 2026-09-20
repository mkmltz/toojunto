from datetime import date
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.auth.security import criar_token_acesso, gerar_hash_senha
from app.db import SessionLocal
from app.main import app
from app.models import Convite, Grupo, Participante, Usuario


client = TestClient(app)


@pytest.fixture
def usuarios():
    db = SessionLocal()
    gestor = Usuario(
        nome="Gestor dos convites",
        email=f"gestor-convite-{uuid4()}@example.com",
        senha_hash=gerar_hash_senha("senha-segura"),
    )
    participante = Usuario(
        nome="Participante dos convites",
        email=f"participante-convite-{uuid4()}@example.com",
        senha_hash=gerar_hash_senha("senha-segura"),
    )
    externo = Usuario(
        nome="Externo aos convites",
        email=f"externo-convite-{uuid4()}@example.com",
        senha_hash=gerar_hash_senha("senha-segura"),
    )
    db.add_all([gestor, participante, externo])
    db.commit()
    for usuario in (gestor, participante, externo):
        db.refresh(usuario)

    try:
        yield gestor, participante, externo
    finally:
        grupos = db.scalars(
            select(Grupo).where(
                Grupo.gestor_id.in_([gestor.id, participante.id, externo.id])
            )
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
                Participante.usuario_id.in_([gestor.id, participante.id, externo.id])
            )
        )
        db.execute(
            delete(Usuario).where(
                Usuario.id.in_([gestor.id, participante.id, externo.id])
            )
        )
        db.commit()
        db.close()


def headers(usuario: Usuario) -> dict[str, str]:
    return {"Authorization": f"Bearer {criar_token_acesso(usuario.id)}"}


def criar_grupo(gestor: Usuario, nome: str = "Grupo com convite") -> dict:
    response = client.post(
        "/groups",
        json={
            "nome": nome,
            "valor_cota": "100.00",
            "quantidade_participantes": 3,
            "quantidade_ciclos": 3,
            "data_inicio": date.today().isoformat(),
        },
        headers=headers(gestor),
    )
    assert response.status_code == 201
    return response.json()


def test_gestor_cria_convite_reutilizavel_e_persistido(usuarios):
    gestor, _, _ = usuarios
    grupo = criar_grupo(gestor)

    response = client.post(
        f"/groups/{grupo['id']}/invite",
        headers=headers(gestor),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["group_id"] == grupo["id"]
    assert body["token"]
    assert body["invite_path"] == f"/invites/{body['token']}"
    db = SessionLocal()
    try:
        convite = db.scalar(select(Convite).where(Convite.grupo_id == grupo["id"]))
        assert convite is not None
        assert convite.token == body["token"]
    finally:
        db.close()


def test_nova_solicitacao_retorna_exatamente_o_mesmo_convite(usuarios):
    gestor, _, _ = usuarios
    grupo = criar_grupo(gestor)

    primeira = client.post(f"/groups/{grupo['id']}/invite", headers=headers(gestor))
    segunda = client.post(f"/groups/{grupo['id']}/invite", headers=headers(gestor))

    assert primeira.status_code == segunda.status_code == 200
    assert primeira.json() == segunda.json()


def test_participante_comum_recebe_404_ao_tentar_gerar_convite(usuarios):
    gestor, participante, _ = usuarios
    grupo = criar_grupo(gestor)
    db = SessionLocal()
    try:
        db.add(
            Participante(
                grupo_id=grupo["id"],
                usuario_id=participante.id,
                status="ATIVO",
            )
        )
        db.commit()
    finally:
        db.close()

    response = client.post(
        f"/groups/{grupo['id']}/invite",
        headers=headers(participante),
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Grupo não encontrado."}


def test_usuario_externo_recebe_404_ao_tentar_gerar_convite(usuarios):
    gestor, _, externo = usuarios
    grupo = criar_grupo(gestor)

    response = client.post(f"/groups/{grupo['id']}/invite", headers=headers(externo))

    assert response.status_code == 404
    assert response.json() == {"detail": "Grupo não encontrado."}


def test_grupo_inexistente_retorna_404(usuarios):
    gestor, _, _ = usuarios
    response = client.post("/groups/999999999/invite", headers=headers(gestor))
    assert response.status_code == 404
    assert response.json() == {"detail": "Grupo não encontrado."}


def test_grupo_privado_e_inexistente_sao_indistinguiveis(usuarios):
    gestor, _, externo = usuarios
    grupo = criar_grupo(gestor)

    privado = client.post(
        f"/groups/{grupo['id']}/invite",
        headers=headers(externo),
    )
    inexistente = client.post(
        "/groups/999999999/invite",
        headers=headers(externo),
    )

    assert privado.status_code == inexistente.status_code == 404
    assert privado.json() == inexistente.json() == {
        "detail": "Grupo não encontrado."
    }


def test_grupo_cancelado_rejeita_convite(usuarios):
    gestor, _, _ = usuarios
    grupo = criar_grupo(gestor)
    cancelamento = client.post(
        f"/groups/{grupo['id']}/cancel",
        headers=headers(gestor),
    )
    assert cancelamento.status_code == 200

    response = client.post(f"/groups/{grupo['id']}/invite", headers=headers(gestor))

    assert response.status_code == 409


@pytest.mark.parametrize(
    "status_grupo",
    ["FORMANDO", "SORTEIO", "ATIVO", "ENCERRADO"],
)
def test_grupo_fora_de_rascunho_rejeita_convite(usuarios, status_grupo):
    gestor, _, _ = usuarios
    grupo = criar_grupo(gestor)
    db = SessionLocal()
    try:
        persistido = db.get(Grupo, grupo["id"])
        persistido.status = status_grupo
        db.commit()
    finally:
        db.close()

    response = client.post(f"/groups/{grupo['id']}/invite", headers=headers(gestor))

    assert response.status_code == 409


def test_grupos_diferentes_recebem_tokens_unicos(usuarios):
    gestor, _, _ = usuarios
    primeiro = criar_grupo(gestor, "Primeiro grupo")
    segundo = criar_grupo(gestor, "Segundo grupo")

    convite_um = client.post(f"/groups/{primeiro['id']}/invite", headers=headers(gestor))
    convite_dois = client.post(f"/groups/{segundo['id']}/invite", headers=headers(gestor))

    assert convite_um.status_code == convite_dois.status_code == 200
    assert convite_um.json()["token"] != convite_dois.json()["token"]


def test_convite_exige_autenticacao(usuarios):
    gestor, _, _ = usuarios
    grupo = criar_grupo(gestor)
    response = client.post(f"/groups/{grupo['id']}/invite")
    assert response.status_code == 401
