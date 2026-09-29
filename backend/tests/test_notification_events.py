from datetime import date
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.auth.security import criar_token_acesso
from app.db import SessionLocal
from app.email import EmailDeliveryPersistenceError
from app.main import app
from app.models import (
    Convite,
    EntregaEmail,
    Grupo,
    Notificacao,
    Participante,
    Usuario,
)
from app.notifications import events


client = TestClient(app)


class RecordingEmailDelivery:
    def __init__(self, fail: bool = False):
        self.calls = []
        self.fail = fail

    def enviar_e_registrar(self, **data):
        self.calls.append(data)
        if self.fail:
            raise EmailDeliveryPersistenceError("delivery tracking failed")


@pytest.fixture
def contexto_eventos(monkeypatch):
    db = SessionLocal()
    usuarios = [
        Usuario(
            nome=nome,
            email=f"event-{uuid4()}@example.com",
            senha_hash="hash-de-teste",
        )
        for nome in ["Gestor", "Participante A", "Participante B", "Externo"]
    ]
    db.add_all(usuarios)
    db.commit()
    for usuario in usuarios:
        db.refresh(usuario)
    ids = [usuario.id for usuario in usuarios]
    delivery = RecordingEmailDelivery()
    monkeypatch.setattr(events, "_reliable_email_service", lambda: delivery)

    try:
        yield usuarios, delivery
    finally:
        grupos = db.scalars(select(Grupo).where(Grupo.gestor_id.in_(ids))).all()
        group_ids = [grupo.id for grupo in grupos]
        notification_ids = db.scalars(
            select(Notificacao.id).where(Notificacao.usuario_id.in_(ids))
        ).all()
        if notification_ids:
            db.execute(
                delete(EntregaEmail).where(
                    EntregaEmail.notificacao_id.in_(notification_ids)
                )
            )
            db.execute(
                delete(Notificacao).where(Notificacao.id.in_(notification_ids))
            )
        if group_ids:
            db.execute(delete(Convite).where(Convite.grupo_id.in_(group_ids)))
            db.execute(
                delete(Participante).where(Participante.grupo_id.in_(group_ids))
            )
            db.execute(delete(Grupo).where(Grupo.id.in_(group_ids)))
        db.execute(delete(Usuario).where(Usuario.id.in_(ids)))
        db.commit()
        db.close()


def headers(usuario: Usuario) -> dict[str, str]:
    return {"Authorization": f"Bearer {criar_token_acesso(usuario.id)}"}


def criar_grupo_e_convite(gestor: Usuario, quantidade: int = 3) -> tuple[int, str]:
    group_response = client.post(
        "/groups",
        json={
            "nome": f"Grupo eventos {uuid4()}",
            "valor_cota": "100.00",
            "quantidade_participantes": quantidade,
            "quantidade_ciclos": quantidade,
            "data_inicio": date.today().isoformat(),
        },
        headers=headers(gestor),
    )
    assert group_response.status_code == 201
    group_id = group_response.json()["id"]
    invite_response = client.post(
        f"/groups/{group_id}/invite",
        headers=headers(gestor),
    )
    assert invite_response.status_code == 200
    return group_id, invite_response.json()["token"]


def notificacoes(tipo: str, group_id: int) -> list[Notificacao]:
    db = SessionLocal()
    try:
        return list(
            db.scalars(
                select(Notificacao)
                .where(
                    Notificacao.tipo == tipo,
                    Notificacao.referencia_contextual == f"/groups/{group_id}",
                )
                .order_by(Notificacao.id)
            ).all()
        )
    finally:
        db.close()


def test_convite_aceito_notifica_somente_gestor_com_contexto_e_email(
    contexto_eventos,
):
    (gestor, participante, _, externo), delivery = contexto_eventos
    group_id, token = criar_grupo_e_convite(gestor)

    response = client.post(
        f"/invites/{token}/accept",
        headers=headers(participante),
    )

    assert response.status_code == 200
    result = notificacoes("CONVITE_ACEITO", group_id)
    assert len(result) == 1
    assert result[0].usuario_id == gestor.id
    assert result[0].usuario_id not in {participante.id, externo.id}
    assert result[0].referencia_contextual == f"/groups/{group_id}"
    assert delivery.calls[0]["notificacao_id"] == result[0].id
    assert delivery.calls[0]["destinatario"] == gestor.email


def test_convite_recusado_notifica_gestor_sem_antecipar_fluxo_us025(
    contexto_eventos,
):
    (gestor, convidado, _, externo), delivery = contexto_eventos
    group_id, _ = criar_grupo_e_convite(gestor)
    db = SessionLocal()
    grupo = db.get(Grupo, group_id)

    notification = events.notificar_convite_recusado(grupo, convidado, db)

    assert notification.usuario_id == gestor.id
    assert notification.usuario_id != externo.id
    assert notification.tipo == "CONVITE_RECUSADO"
    assert notification.referencia_contextual == f"/groups/{group_id}"
    assert delivery.calls[0]["evento"] == "CONVITE_RECUSADO"
    db.close()


def test_ultima_aceitacao_notifica_grupo_completo_para_todos_integrantes(
    contexto_eventos,
):
    (gestor, primeiro, ultimo, externo), delivery = contexto_eventos
    group_id, token = criar_grupo_e_convite(gestor)
    assert client.post(
        f"/invites/{token}/accept", headers=headers(primeiro)
    ).status_code == 200

    response = client.post(
        f"/invites/{token}/accept",
        headers=headers(ultimo),
    )

    assert response.status_code == 200
    result = notificacoes("GRUPO_COMPLETO", group_id)
    assert {item.usuario_id for item in result} == {
        gestor.id,
        primeiro.id,
        ultimo.id,
    }
    assert externo.id not in {item.usuario_id for item in result}
    assert all(
        item.referencia_contextual == f"/groups/{group_id}" for item in result
    )
    complete_emails = [
        call for call in delivery.calls if call["evento"] == "GRUPO_COMPLETO"
    ]
    assert len(complete_emails) == 3


def test_grupo_cancelado_notifica_participantes_mas_nao_gestor_ou_externo(
    contexto_eventos,
):
    (gestor, participante, _, externo), delivery = contexto_eventos
    group_id, token = criar_grupo_e_convite(gestor)
    assert client.post(
        f"/invites/{token}/accept", headers=headers(participante)
    ).status_code == 200

    response = client.post(
        f"/groups/{group_id}/cancel",
        headers=headers(gestor),
    )

    assert response.status_code == 200
    result = notificacoes("GRUPO_CANCELADO", group_id)
    assert [item.usuario_id for item in result] == [participante.id]
    assert gestor.id not in {item.usuario_id for item in result}
    assert externo.id not in {item.usuario_id for item in result}
    assert result[0].referencia_contextual == f"/groups/{group_id}"
    assert any(call["evento"] == "GRUPO_CANCELADO" for call in delivery.calls)


def test_falha_de_email_preserva_aceite_e_notificacao_in_app(
    contexto_eventos,
    monkeypatch,
):
    (gestor, participante, _, _), _ = contexto_eventos
    failing_delivery = RecordingEmailDelivery(fail=True)
    monkeypatch.setattr(
        events,
        "_reliable_email_service",
        lambda: failing_delivery,
    )
    group_id, token = criar_grupo_e_convite(gestor)

    response = client.post(
        f"/invites/{token}/accept",
        headers=headers(participante),
    )

    assert response.status_code == 200
    db = SessionLocal()
    assert db.scalar(
        select(Participante).where(
            Participante.grupo_id == group_id,
            Participante.usuario_id == participante.id,
        )
    ) is not None
    assert db.scalar(
        select(Notificacao).where(
            Notificacao.usuario_id == gestor.id,
            Notificacao.tipo == "CONVITE_ACEITO",
        )
    ) is not None
    db.close()


def test_repeticao_de_operacao_nao_duplica_notificacoes(contexto_eventos):
    (gestor, participante, _, _), _ = contexto_eventos
    group_id, token = criar_grupo_e_convite(gestor)
    assert client.post(
        f"/invites/{token}/accept", headers=headers(participante)
    ).status_code == 200

    repeated_accept = client.post(
        f"/invites/{token}/accept",
        headers=headers(participante),
    )
    assert repeated_accept.status_code == 409
    assert len(notificacoes("CONVITE_ACEITO", group_id)) == 1

    assert client.post(
        f"/groups/{group_id}/cancel", headers=headers(gestor)
    ).status_code == 200
    repeated_cancel = client.post(
        f"/groups/{group_id}/cancel",
        headers=headers(gestor),
    )
    assert repeated_cancel.status_code == 409
    assert len(notificacoes("GRUPO_CANCELADO", group_id)) == 1
