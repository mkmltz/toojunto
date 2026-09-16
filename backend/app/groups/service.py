from datetime import datetime, time

from sqlalchemy.orm import Session

from ..models import Grupo, Participante, Usuario
from .schemas import GrupoCriacao


def criar_grupo(
    dados: GrupoCriacao,
    gestor: Usuario,
    db: Session,
) -> Grupo:
    grupo = Grupo(
        nome=dados.nome,
        gestor_id=gestor.id,
        valor_cota=dados.valor_cota,
        valor_premio=dados.valor_cota * dados.quantidade_participantes,
        quantidade_participantes=dados.quantidade_participantes,
        quantidade_ciclos=dados.quantidade_ciclos,
        data_inicio=datetime.combine(dados.data_inicio, time.min),
        status="RASCUNHO",
    )

    try:
        db.add(grupo)
        db.flush()
        db.add(
            Participante(
                grupo_id=grupo.id,
                usuario_id=gestor.id,
                ordem_sorteio=None,
                status="ATIVO",
            )
        )
        db.commit()
        db.refresh(grupo)
    except Exception:
        db.rollback()
        raise

    return grupo
