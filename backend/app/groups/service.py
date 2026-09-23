import secrets
from datetime import date, datetime, time, timedelta

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import Ciclo, Convite, Grupo, Pagamento, Participante, Usuario
from .schemas import (
    ConviteResposta,
    GrupoAtualizacao,
    GrupoComPapelResposta,
    GrupoCriacao,
    GrupoDetalheResposta,
    GrupoListaResposta,
    GrupoResposta,
    FormacaoGrupoResposta,
    IntegranteGrupoResposta,
    PapelGrupo,
    PosicaoSorteioResposta,
    CicloResposta,
    ProgressoGrupoResposta,
    SituacaoCiclo,
    ObrigacaoPagamentoResposta,
    SituacaoObrigacao,
)


def _normalizar_nome_grupo(nome: str) -> str:
    return " ".join(nome.split()).casefold()


def _garantir_nome_disponivel(
    nome: str,
    gestor_id: int,
    db: Session,
    grupo_id_ignorado: int | None = None,
) -> None:
    db.scalar(
        select(Usuario.id)
        .where(Usuario.id == gestor_id)
        .with_for_update()
    )
    consulta = select(Grupo).where(
        Grupo.gestor_id == gestor_id,
        Grupo.status.notin_(("ENCERRADO", "CANCELADO")),
    )
    if grupo_id_ignorado is not None:
        consulta = consulta.where(Grupo.id != grupo_id_ignorado)
    nome_normalizado = _normalizar_nome_grupo(nome)
    conflito = next(
        (
            grupo
            for grupo in db.scalars(consulta).all()
            if _normalizar_nome_grupo(grupo.nome) == nome_normalizado
        ),
        None,
    )
    if conflito is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f'Você já possui um grupo ativo chamado "{conflito.nome}". '
                "Escolha outro nome para o novo grupo."
            ),
        )


def criar_grupo(
    dados: GrupoCriacao,
    gestor: Usuario,
    db: Session,
) -> Grupo:
    _garantir_nome_disponivel(dados.nome, gestor.id, db)
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


def _grupo_com_papel(
    grupo: Grupo,
    usuario: Usuario,
    gestor_nome: str,
) -> GrupoComPapelResposta:
    papel = (
        PapelGrupo.GESTOR
        if grupo.gestor_id == usuario.id
        else PapelGrupo.PARTICIPANTE
    )
    dados_grupo = GrupoResposta.model_validate(grupo).model_dump()
    return GrupoComPapelResposta(
        **dados_grupo,
        papel=papel,
        gestor_nome=gestor_nome,
    )


def listar_grupos_do_usuario(
    usuario: Usuario,
    db: Session,
) -> list[GrupoListaResposta]:
    participacao_ativa = (
        select(Participante.id)
        .where(
            Participante.grupo_id == Grupo.id,
            Participante.usuario_id == usuario.id,
            Participante.status == "ATIVO",
        )
        .exists()
    )
    ocupacao = (
        select(
            Participante.grupo_id.label("grupo_id"),
            func.count(Participante.id).label("quantidade_atual"),
        )
        .group_by(Participante.grupo_id)
        .subquery()
    )
    grupos = db.execute(
        select(
            Grupo,
            Usuario.nome,
            func.coalesce(ocupacao.c.quantidade_atual, 0),
        )
        .join(Usuario, Usuario.id == Grupo.gestor_id)
        .outerjoin(ocupacao, ocupacao.c.grupo_id == Grupo.id)
        .where(participacao_ativa)
        .order_by(Grupo.created_at.desc(), Grupo.id.desc())
    ).all()
    return [
        GrupoListaResposta(
            **_grupo_com_papel(grupo, usuario, gestor_nome).model_dump(),
            vagas_disponiveis=max(
                grupo.quantidade_participantes - quantidade_atual, 0
            ),
        )
        for grupo, gestor_nome, quantidade_atual in grupos
    ]


def obter_grupo_do_usuario(
    grupo_id: int,
    usuario: Usuario,
    db: Session,
) -> GrupoDetalheResposta:
    participacao_ativa = (
        select(Participante.id)
        .where(
            Participante.grupo_id == Grupo.id,
            Participante.usuario_id == usuario.id,
            Participante.status == "ATIVO",
        )
        .exists()
    )
    resultado = db.execute(
        select(Grupo, Usuario.nome)
        .join(Usuario, Usuario.id == Grupo.gestor_id)
        .where(
            Grupo.id == grupo_id,
            participacao_ativa,
        )
    ).one_or_none()
    if resultado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo não encontrado.",
        )
    grupo, gestor_nome = resultado
    integrantes = db.execute(
        select(Participante, Usuario)
        .join(Usuario, Usuario.id == Participante.usuario_id)
        .where(Participante.grupo_id == grupo.id)
        .order_by(
            (Participante.usuario_id != grupo.gestor_id),
            Participante.id,
        )
    ).all()
    quantidade_atual = len(integrantes)
    formacao = FormacaoGrupoResposta(
        quantidade_atual=quantidade_atual,
        limite=grupo.quantidade_participantes,
        vagas_disponiveis=max(
            grupo.quantidade_participantes - quantidade_atual,
            0,
        ),
        participantes=[
            IntegranteGrupoResposta(
                nome=integrante.nome,
                papel=(
                    PapelGrupo.GESTOR
                    if integrante.id == grupo.gestor_id
                    else PapelGrupo.PARTICIPANTE
                ),
            )
            for _, integrante in integrantes
        ],
    )
    dados_grupo = _grupo_com_papel(
        grupo,
        usuario,
        gestor_nome,
    ).model_dump()
    ordem_recebimento = None
    if grupo.status in ("ATIVO", "ENCERRADO"):
        ordem_recebimento = [
            PosicaoSorteioResposta(
                posicao=participante.ordem_sorteio,
                nome=integrante.nome,
                papel=(
                    PapelGrupo.GESTOR
                    if integrante.id == grupo.gestor_id
                    else PapelGrupo.PARTICIPANTE
                ),
                data_prevista=(
                    grupo.data_inicio + timedelta(
                        days=(participante.ordem_sorteio - 1) * 30
                    )
                ).date(),
            )
            for participante, integrante in sorted(
                integrantes,
                key=lambda item: item[0].ordem_sorteio or 0,
            )
        ]
    return GrupoDetalheResposta(
        **dados_grupo,
        formacao=formacao,
        ordem_recebimento=ordem_recebimento,
    )


def obter_progresso_grupo(
    grupo_id: int, usuario: Usuario, db: Session
) -> ProgressoGrupoResposta:
    detalhe = obter_grupo_do_usuario(grupo_id, usuario, db)
    if detalhe.status not in ("ATIVO", "ENCERRADO") or not detalhe.ordem_recebimento:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Os ciclos ainda não estão disponíveis.",
        )

    concluidos = set(db.scalars(select(Ciclo.numero).where(
        Ciclo.grupo_id == grupo_id, Ciclo.status == "CONCLUIDO"
    )).all())
    grupo_concluido = detalhe.status == "ENCERRADO"
    numero_atual = next((numero for numero in range(1, detalhe.quantidade_ciclos + 1)
                         if numero not in concluidos), detalhe.quantidade_ciclos)
    ciclos = [
        CicloResposta(
            numero_ciclo=posicao.posicao,
            nome=posicao.nome,
            papel=posicao.papel,
            data_prevista=posicao.data_prevista,
            situacao=(
                SituacaoCiclo.CONCLUIDO if posicao.posicao in concluidos
                else SituacaoCiclo.ATUAL
                if posicao.posicao == numero_atual and not grupo_concluido
                else SituacaoCiclo.PROXIMO
            ),
        )
        for posicao in detalhe.ordem_recebimento
    ]
    return ProgressoGrupoResposta(
        ciclo_atual=numero_atual,
        total_ciclos=detalhe.quantidade_ciclos,
        contemplado_ciclo_atual=ciclos[numero_atual - 1].nome,
        data_prevista_ciclo_atual=ciclos[numero_atual - 1].data_prevista,
        ciclos=ciclos,
        grupo_concluido=grupo_concluido,
    )


def _numero_ciclo_atual(grupo: Grupo, db: Session) -> int:
    concluidos = set(db.scalars(select(Ciclo.numero).where(
        Ciclo.grupo_id == grupo.id, Ciclo.status == "CONCLUIDO"
    )).all())
    return next((numero for numero in range(1, grupo.quantidade_ciclos + 1)
                 if numero not in concluidos), grupo.quantidade_ciclos + 1)


def _contexto_pagamentos(
    grupo_id: int, numero_ciclo: int, usuario: Usuario, db: Session,
    bloquear: bool = False,
) -> tuple[Grupo, list[tuple[Participante, Usuario]], Participante, Usuario]:
    consulta = select(Grupo).where(Grupo.id == grupo_id)
    if bloquear:
        consulta = consulta.with_for_update()
    grupo = db.scalar(consulta)
    if grupo is None:
        raise HTTPException(status_code=404, detail="Grupo não encontrado.")
    integrantes = db.execute(
        select(Participante, Usuario)
        .join(Usuario, Usuario.id == Participante.usuario_id)
        .where(Participante.grupo_id == grupo_id, Participante.status == "ATIVO")
        .order_by(Participante.id)
    ).all()
    if not any(p.usuario_id == usuario.id for p, _ in integrantes):
        raise HTTPException(status_code=404, detail="Grupo não encontrado.")
    atual = _numero_ciclo_atual(grupo, db)
    if (grupo.status not in ("ATIVO", "ENCERRADO") or numero_ciclo < 1
            or numero_ciclo > grupo.quantidade_ciclos or numero_ciclo > atual):
        raise HTTPException(status_code=409, detail="Ciclo indisponível para pagamentos.")
    contemplados = [(p, u) for p, u in integrantes if p.ordem_sorteio == numero_ciclo]
    if len(contemplados) != 1 or len(integrantes) != grupo.quantidade_participantes:
        raise HTTPException(status_code=409, detail="Ciclo indisponível para pagamentos.")
    return grupo, integrantes, *contemplados[0]


def _obrigacoes_pagamento(
    grupo: Grupo, integrantes: list[tuple[Participante, Usuario]],
    contemplado: Participante, recebedor: Usuario, numero_ciclo: int,
    usuario: Usuario, db: Session,
) -> list[ObrigacaoPagamentoResposta]:
    ciclo = db.scalar(select(Ciclo).where(Ciclo.grupo_id == grupo.id, Ciclo.numero == numero_ciclo))
    pagamentos = {
        pagamento.pagador_id: pagamento
        for pagamento in db.scalars(
            select(Pagamento).where(Pagamento.ciclo_id == ciclo.id)
        ).all()
    } if ciclo else {}
    data_prevista = (grupo.data_inicio + timedelta(days=(numero_ciclo - 1) * 30)).date()
    prazo = data_prevista - timedelta(days=5)
    dias_ate_data = (data_prevista - date.today()).days
    dias_ate_prazo = (prazo - date.today()).days
    pode_avaliar_ciclo = (
        usuario.id == recebedor.id and grupo.status == "ATIVO"
        and numero_ciclo == _numero_ciclo_atual(grupo, db)
    )
    return [
        ObrigacaoPagamentoResposta(
            grupo_id=grupo.id,
            numero_ciclo=numero_ciclo,
            pagador_id=participante.id,
            pagador_usuario_id=pagador.id,
            pagamento_id=pagamentos[participante.id].id if participante.id in pagamentos else None,
            pagador_nome=pagador.nome,
            recebedor_id=contemplado.id,
            recebedor_nome=recebedor.nome,
            valor=grupo.valor_cota,
            data_prevista=data_prevista,
            prazo_pagamento=prazo,
            dias_ate_data_prevista=dias_ate_data,
            dias_ate_prazo=dias_ate_prazo,
            alerta_prazo=1 <= dias_ate_data <= 5 and (
                participante.id not in pagamentos or pagamentos[participante.id].status == "REJEITADO"
            ),
            situacao=(
                SituacaoObrigacao.CONFIRMADO if participante.id in pagamentos and pagamentos[participante.id].status == "CONFIRMADO"
                else SituacaoObrigacao.REJEITADO if participante.id in pagamentos and pagamentos[participante.id].status == "REJEITADO"
                else SituacaoObrigacao.ATRASADO if dias_ate_data <= 0
                else SituacaoObrigacao.AGUARDANDO_CONFIRMACAO if participante.id in pagamentos
                else SituacaoObrigacao.PENDENTE
            ),
            status_registro=pagamentos[participante.id].status if participante.id in pagamentos else None,
            declarado_em=pagamentos[participante.id].data_pagamento if participante.id in pagamentos else None,
            pode_avaliar=(
                pode_avaliar_ciclo
                and participante.id in pagamentos
                and pagamentos[participante.id].status == "AGUARDANDO_CONFIRMACAO"
            ),
        )
        for participante, pagador in integrantes
        if participante.id != contemplado.id
    ]


def listar_obrigacoes_pagamento(
    grupo_id: int, numero_ciclo: int, usuario: Usuario, db: Session,
) -> list[ObrigacaoPagamentoResposta]:
    grupo, integrantes, contemplado, recebedor = _contexto_pagamentos(
        grupo_id, numero_ciclo, usuario, db
    )
    return _obrigacoes_pagamento(grupo, integrantes, contemplado, recebedor, numero_ciclo, usuario, db)


def declarar_pagamento(
    grupo_id: int, numero_ciclo: int, usuario: Usuario, db: Session,
) -> ObrigacaoPagamentoResposta:
    grupo, integrantes, contemplado, recebedor = _contexto_pagamentos(
        grupo_id, numero_ciclo, usuario, db, bloquear=True
    )
    if grupo.status != "ATIVO" or numero_ciclo != _numero_ciclo_atual(grupo, db):
        raise HTTPException(status_code=409, detail="Ciclo indisponível para pagamentos.")
    pagador = next(p for p, u in integrantes if u.id == usuario.id)
    if pagador.id == contemplado.id:
        raise HTTPException(status_code=409, detail="O contemplado não possui pagamento neste ciclo.")
    ciclo = db.scalar(select(Ciclo).where(Ciclo.grupo_id == grupo.id, Ciclo.numero == numero_ciclo))
    pagamento_existente = db.scalar(select(Pagamento).where(
        Pagamento.ciclo_id == ciclo.id, Pagamento.pagador_id == pagador.id
    )) if ciclo else None
    if pagamento_existente and pagamento_existente.status != "REJEITADO":
        raise HTTPException(status_code=409, detail="Pagamento já declarado neste ciclo.")
    try:
        if ciclo is None:
            ciclo = Ciclo(grupo_id=grupo.id, numero=numero_ciclo,
                          data=grupo.data_inicio, contemplado_id=contemplado.id,
                          status="ABERTO")
            db.add(ciclo)
            db.flush()
        if pagamento_existente:
            pagamento_existente.status = "AGUARDANDO_CONFIRMACAO"
            pagamento_existente.data_pagamento = datetime.utcnow()
        else:
            db.add(Pagamento(
                ciclo_id=ciclo.id, pagador_id=pagador.id, recebedor_id=contemplado.id,
                valor=grupo.valor_cota, status="AGUARDANDO_CONFIRMACAO",
                data_pagamento=datetime.utcnow(),
            ))
        db.commit()
    except Exception:
        db.rollback()
        raise
    return next(o for o in _obrigacoes_pagamento(
        grupo, integrantes, contemplado, recebedor, numero_ciclo, usuario, db
    ) if o.pagador_id == pagador.id)


def avaliar_pagamento(
    grupo_id: int, numero_ciclo: int, pagamento_id: int,
    usuario: Usuario, confirmar: bool, db: Session,
) -> ObrigacaoPagamentoResposta:
    grupo, integrantes, contemplado, recebedor = _contexto_pagamentos(
        grupo_id, numero_ciclo, usuario, db, bloquear=True
    )
    if usuario.id != recebedor.id:
        raise HTTPException(status_code=403, detail="Somente o contemplado pode avaliar pagamentos.")
    if grupo.status != "ATIVO" or numero_ciclo != _numero_ciclo_atual(grupo, db):
        raise HTTPException(status_code=409, detail="Ciclo indisponível para pagamentos.")
    ciclo = db.scalar(select(Ciclo).where(Ciclo.grupo_id == grupo_id, Ciclo.numero == numero_ciclo))
    if ciclo is None:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado.")
    pagamento = db.scalar(select(Pagamento).where(
        Pagamento.id == pagamento_id,
        Pagamento.ciclo_id == ciclo.id,
    ))
    if pagamento is None or pagamento.recebedor_id != contemplado.id:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado.")
    if pagamento.status != "AGUARDANDO_CONFIRMACAO":
        raise HTTPException(status_code=409, detail="Pagamento não aguarda confirmação.")

    try:
        pagamento.status = "CONFIRMADO" if confirmar else "REJEITADO"
        db.flush()
        if confirmar:
            confirmados = db.scalar(select(func.count(func.distinct(Pagamento.pagador_id))).where(
                Pagamento.ciclo_id == ciclo.id, Pagamento.status == "CONFIRMADO"
            ))
            if confirmados == grupo.quantidade_participantes - 1:
                ciclo.status = "CONCLUIDO"
                proximo_numero = numero_ciclo + 1
                if proximo_numero <= grupo.quantidade_ciclos:
                    proximo_contemplado = next(
                        p for p, _ in integrantes if p.ordem_sorteio == proximo_numero
                    )
                    db.add(Ciclo(
                        grupo_id=grupo.id, numero=proximo_numero,
                        data=grupo.data_inicio + timedelta(days=(proximo_numero - 1) * 30),
                        contemplado_id=proximo_contemplado.id, status="ABERTO",
                    ))
                else:
                    grupo.status = "ENCERRADO"
        db.commit()
    except Exception:
        db.rollback()
        raise
    return next(o for o in _obrigacoes_pagamento(
        grupo, integrantes, contemplado, recebedor, numero_ciclo, usuario, db
    ) if o.pagamento_id == pagamento_id)


def _buscar_grupo_gerenciavel(
    grupo_id: int,
    gestor: Usuario,
    db: Session,
) -> Grupo:
    grupo = db.scalar(
        select(Grupo).where(Grupo.id == grupo_id).with_for_update()
    )

    if grupo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo não encontrado.",
        )

    if grupo.gestor_id != gestor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Somente o gestor proprietário pode gerenciar o grupo.",
        )

    if grupo.status != "RASCUNHO":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Somente grupos em RASCUNHO podem ser gerenciados.",
        )

    return grupo


def atualizar_grupo(
    grupo_id: int,
    dados: GrupoAtualizacao,
    gestor: Usuario,
    db: Session,
) -> Grupo:
    grupo = _buscar_grupo_gerenciavel(grupo_id, gestor, db)
    alteracoes = dados.model_dump(exclude_unset=True)

    primeiro_aceite = db.scalar(
        select(Participante.id).where(
            Participante.grupo_id == grupo.id,
            Participante.usuario_id != grupo.gestor_id,
        ).limit(1)
    )
    if primeiro_aceite is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "As condições do Grupo não podem ser alteradas após "
                "o primeiro participante aceitar o convite."
            ),
        )

    if "nome" in alteracoes:
        _garantir_nome_disponivel(
            alteracoes["nome"],
            gestor.id,
            db,
            grupo_id_ignorado=grupo.id,
        )

    nova_quantidade = alteracoes.get(
        "quantidade_participantes",
        grupo.quantidade_participantes,
    )
    quantidade_associada = db.scalar(
        select(func.count(Participante.id)).where(
            Participante.grupo_id == grupo.id
        )
    )
    if nova_quantidade < quantidade_associada:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A quantidade de participantes não pode ser menor que a "
                "quantidade já associada ao grupo."
            ),
        )

    try:
        if "nome" in alteracoes:
            grupo.nome = alteracoes["nome"]
        if "valor_cota" in alteracoes:
            grupo.valor_cota = alteracoes["valor_cota"]
        if "quantidade_participantes" in alteracoes:
            grupo.quantidade_participantes = nova_quantidade
            grupo.quantidade_ciclos = nova_quantidade
        if "data_inicio" in alteracoes:
            grupo.data_inicio = datetime.combine(
                alteracoes["data_inicio"],
                time.min,
            )

        grupo.valor_premio = (
            grupo.valor_cota * grupo.quantidade_participantes
        )
        db.commit()
        db.refresh(grupo)
    except Exception:
        db.rollback()
        raise

    return grupo


def cancelar_grupo(
    grupo_id: int,
    gestor: Usuario,
    db: Session,
) -> Grupo:
    grupo = _buscar_grupo_gerenciavel(grupo_id, gestor, db)

    try:
        grupo.status = "CANCELADO"
        db.commit()
        db.refresh(grupo)
    except Exception:
        db.rollback()
        raise

    return grupo


def preparar_sorteio(
    grupo_id: int,
    gestor: Usuario,
    db: Session,
) -> Grupo:
    grupo = db.scalar(
        select(Grupo).where(Grupo.id == grupo_id).with_for_update()
    )
    if grupo is None:
        raise HTTPException(status_code=404, detail="Grupo não encontrado.")
    if grupo.gestor_id != gestor.id:
        raise HTTPException(
            status_code=403,
            detail="Somente o gestor proprietário pode preparar o sorteio.",
        )
    if grupo.status != "RASCUNHO":
        raise HTTPException(
            status_code=409,
            detail="O estado do Grupo não permite preparar o sorteio.",
        )

    participantes = db.scalars(
        select(Participante).where(Participante.grupo_id == grupo.id)
    ).all()
    if (
        grupo.quantidade_participantes < 2
        or grupo.quantidade_ciclos != grupo.quantidade_participantes
        or len(participantes) != grupo.quantidade_participantes
        or len({p.usuario_id for p in participantes}) != len(participantes)
        or any(
            p.status != "ATIVO" or p.ordem_sorteio is not None
            for p in participantes
        )
        or sum(p.usuario_id == grupo.gestor_id for p in participantes) != 1
    ):
        raise HTTPException(
            status_code=409,
            detail="A formação do Grupo não está apta para o sorteio.",
        )

    try:
        grupo.status = "SORTEIO"
        db.commit()
        db.refresh(grupo)
    except Exception:
        db.rollback()
        raise
    return grupo


def realizar_sorteio(grupo_id: int, gestor: Usuario, db: Session) -> Grupo:
    grupo = db.scalar(
        select(Grupo).where(Grupo.id == grupo_id).with_for_update()
    )
    if grupo is None:
        raise HTTPException(status_code=404, detail="Grupo não encontrado.")
    if grupo.gestor_id != gestor.id:
        raise HTTPException(
            status_code=403,
            detail="Somente o gestor proprietário pode realizar o sorteio.",
        )
    if grupo.status != "SORTEIO":
        raise HTTPException(
            status_code=409,
            detail="O Grupo não está pronto para o sorteio.",
        )

    participantes = db.scalars(
        select(Participante).where(Participante.grupo_id == grupo.id)
    ).all()
    if (
        grupo.quantidade_participantes < 2
        or grupo.quantidade_ciclos != grupo.quantidade_participantes
        or len(participantes) != grupo.quantidade_participantes
        or len({p.usuario_id for p in participantes}) != len(participantes)
        or any(
            p.status != "ATIVO" or p.ordem_sorteio is not None
            for p in participantes
        )
        or sum(p.usuario_id == grupo.gestor_id for p in participantes) != 1
    ):
        raise HTTPException(
            status_code=409,
            detail="A formação do Grupo não está apta para o sorteio.",
        )

    gestor_participante = next(
        p for p in participantes if p.usuario_id == grupo.gestor_id
    )
    demais = [p for p in participantes if p.usuario_id != grupo.gestor_id]
    secrets.SystemRandom().shuffle(demais)
    try:
        gestor_participante.ordem_sorteio = 1
        for posicao, participante in enumerate(demais, start=2):
            participante.ordem_sorteio = posicao
        grupo.status = "ATIVO"
        db.commit()
        db.refresh(grupo)
    except Exception:
        db.rollback()
        raise
    return grupo


def gerar_ou_obter_convite(
    grupo_id: int,
    gestor: Usuario,
    db: Session,
) -> ConviteResposta:
    grupo = db.scalar(
        select(Grupo)
        .where(
            Grupo.id == grupo_id,
            Grupo.gestor_id == gestor.id,
        )
        .with_for_update()
    )
    if grupo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo não encontrado.",
        )

    if grupo.status != "RASCUNHO":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Somente grupos em RASCUNHO podem ser gerenciados.",
        )

    convite = db.scalar(
        select(Convite).where(Convite.grupo_id == grupo.id)
    )

    if convite is None:
        while convite is None:
            candidato = Convite(
                grupo_id=grupo.id,
                token=secrets.token_urlsafe(32),
            )
            try:
                with db.begin_nested():
                    db.add(candidato)
                    db.flush()
                convite = candidato
            except IntegrityError:
                convite = db.scalar(
                    select(Convite).where(Convite.grupo_id == grupo.id)
                )

        try:
            db.commit()
            db.refresh(convite)
        except Exception:
            db.rollback()
            raise

    return ConviteResposta(
        id=convite.id,
        group_id=convite.grupo_id,
        token=convite.token,
        invite_path=f"/invites/{convite.token}",
        created_at=convite.created_at,
    )
