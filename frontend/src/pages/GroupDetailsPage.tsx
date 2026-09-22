import { useEffect, useRef, useState } from "react";
import { AppShell } from "../components/AppShell";
import { buscarObrigacoesPagamento, buscarProgressoGrupo, informarPagamento } from "../services/groups";
import type { ConviteGrupo, GrupoDetalhe, ObrigacaoPagamento, ProgressoGrupo, SituacaoCiclo, SituacaoObrigacao } from "../types/groups";

const formatarValor = (valor: string) => Number(valor).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
const formatarData = (data: string) => new Intl.DateTimeFormat("pt-BR", { timeZone: "UTC" }).format(new Date(`${data}T00:00:00Z`));
const rotuloSituacao: Record<SituacaoCiclo, string> = { ATUAL: "ATUAL", PROXIMO: "PRÓXIMO", CONCLUIDO: "CONCLUÍDO" };
const rotuloPagamento: Record<SituacaoObrigacao, string> = { PENDENTE: "Pendente", AGUARDANDO_CONFIRMACAO: "Aguardando confirmação", ATRASADO: "Atrasado", CONFIRMADO: "Confirmado" };

function mensagemPrazo(obrigacao: ObrigacaoPagamento) {
  const dias = obrigacao.dias_ate_data_prevista;
  if (dias > 0) return `Faltam ${dias} ${dias === 1 ? "dia" : "dias"} para o pagamento a ${obrigacao.recebedor_nome}.`;
  if (dias === 0) return `Pagamento a ${obrigacao.recebedor_nome} previsto para hoje.`;
  return `Pagamento a ${obrigacao.recebedor_nome} em atraso há ${Math.abs(dias)} ${dias === -1 ? "dia" : "dias"}.`;
}

interface GroupDetailsPageProps {
  nomeUsuario: string;
  usuarioId: number;
  grupo: GrupoDetalhe;
  aviso: string;
  carregando: boolean;
  onVoltar: () => void;
  onEditar: () => void;
  onCancelar: () => Promise<void>;
  onObterConvite: () => Promise<ConviteGrupo>;
  onPrepararSorteio: () => Promise<void>;
  onRealizarSorteio: () => Promise<void>;
}

export function GroupDetailsPage({ nomeUsuario, usuarioId, grupo, aviso, carregando, onVoltar, onEditar, onCancelar, onObterConvite, onPrepararSorteio, onRealizarSorteio }: GroupDetailsPageProps) {
  const [confirmando, setConfirmando] = useState(false);
  const [confirmandoSorteio, setConfirmandoSorteio] = useState(false);
  const [confirmandoRealizacao, setConfirmandoRealizacao] = useState(false);
  const [erro, setErro] = useState("");
  const [convite, setConvite] = useState<ConviteGrupo | null>(null);
  const [carregandoConvite, setCarregandoConvite] = useState(false);
  const [feedbackConvite, setFeedbackConvite] = useState("");
  const [progresso, setProgresso] = useState<ProgressoGrupo | null>(null);
  const [carregandoProgresso, setCarregandoProgresso] = useState(false);
  const [erroProgresso, setErroProgresso] = useState("");
  const [obrigacoes, setObrigacoes] = useState<ObrigacaoPagamento[] | null>(null);
  const [carregandoObrigacoes, setCarregandoObrigacoes] = useState(false);
  const [erroObrigacoes, setErroObrigacoes] = useState("");
  const [confirmandoPagamento, setConfirmandoPagamento] = useState<number | null>(null);
  const [enviandoPagamento, setEnviandoPagamento] = useState(false);
  const envioPagamentoEmAndamento = useRef(false);
  const botaoInformarPagamento = useRef<HTMLButtonElement | null>(null);
  const botaoCancelarPagamento = useRef<HTMLButtonElement | null>(null);
  const botaoConfirmarPagamento = useRef<HTMLButtonElement | null>(null);
  const tituloPagamentos = useRef<HTMLHeadingElement | null>(null);
  const modalPagamentoAberta = useRef(false);
  useEffect(() => {
    setProgresso(null);
    setErroProgresso("");
    if (grupo.status !== "ATIVO") return;
    const token = localStorage.getItem("toojunto_access_token");
    if (!token) return;
    let ativo = true;
    setCarregandoProgresso(true);
    buscarProgressoGrupo(grupo.id, token)
      .then((dados) => { if (ativo) setProgresso(dados); })
      .catch(() => { if (ativo) setErroProgresso("Não foi possível carregar o progresso do grupo."); })
      .finally(() => { if (ativo) setCarregandoProgresso(false); });
    return () => { ativo = false; };
  }, [grupo.id, grupo.status]);
  useEffect(() => {
    setObrigacoes(null);
    setErroObrigacoes("");
    if (grupo.status !== "ATIVO" || !progresso) return;
    const token = localStorage.getItem("toojunto_access_token");
    if (!token) return;
    let ativo = true;
    setCarregandoObrigacoes(true);
    buscarObrigacoesPagamento(grupo.id, progresso.ciclo_atual, token)
      .then((dados) => { if (ativo) setObrigacoes(dados); })
      .catch(() => { if (ativo) setErroObrigacoes("Não foi possível carregar os pagamentos do ciclo."); })
      .finally(() => { if (ativo) setCarregandoObrigacoes(false); });
    return () => { ativo = false; };
  }, [grupo.id, grupo.status, progresso]);
  const obrigacaoConfirmada = obrigacoes?.find((item) => item.pagador_id === confirmandoPagamento && item.pagador_usuario_id === usuarioId);
  useEffect(() => {
    if (confirmandoPagamento === null) {
      if (modalPagamentoAberta.current) {
        const destino = botaoInformarPagamento.current?.isConnected
          ? botaoInformarPagamento.current : tituloPagamentos.current;
        destino?.focus();
      }
      modalPagamentoAberta.current = false;
      return;
    }
    modalPagamentoAberta.current = true;
    botaoCancelarPagamento.current?.focus();
    const overflowAnterior = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    function controlarTeclado(evento: KeyboardEvent) {
      if (evento.key === "Escape" && !envioPagamentoEmAndamento.current) {
        evento.preventDefault();
        setConfirmandoPagamento(null);
      }
      if (evento.key !== "Tab") return;
      const cancelar = botaoCancelarPagamento.current;
      const confirmar = botaoConfirmarPagamento.current;
      if (!cancelar || !confirmar || confirmar.disabled) {
        evento.preventDefault();
        return;
      }
      if (evento.shiftKey && document.activeElement === confirmar) {
        evento.preventDefault();
        cancelar.focus();
      } else if (!evento.shiftKey && document.activeElement === cancelar) {
        evento.preventDefault();
        confirmar.focus();
      }
    }
    document.addEventListener("keydown", controlarTeclado);
    return () => {
      document.body.style.overflow = overflowAnterior;
      document.removeEventListener("keydown", controlarTeclado);
    };
  }, [confirmandoPagamento]);

  async function confirmarPagamento() {
    if (!progresso || !obrigacaoConfirmada || envioPagamentoEmAndamento.current) return;
    const token = localStorage.getItem("toojunto_access_token");
    if (!token) { setErroObrigacoes("Entre novamente para informar o pagamento."); return; }
    envioPagamentoEmAndamento.current = true;
    setEnviandoPagamento(true);
    setErroObrigacoes("");
    try {
      const declarado = await informarPagamento(grupo.id, progresso.ciclo_atual, token);
      setObrigacoes((atuais) => atuais?.map((item) => item.pagador_id === declarado.pagador_id ? declarado : item) ?? null);
      setConfirmandoPagamento(null);
      try {
        setObrigacoes(await buscarObrigacoesPagamento(grupo.id, progresso.ciclo_atual, token));
      } catch {
        setErroObrigacoes("Pagamento informado. Não foi possível atualizar a lista.");
      }
    } catch {
      setErroObrigacoes("Não foi possível informar o pagamento. Confira a situação e tente novamente.");
    } finally {
      envioPagamentoEmAndamento.current = false;
      setEnviandoPagamento(false);
    }
  }
  const podeGerenciar = grupo.papel === "GESTOR" && grupo.status === "RASCUNHO";
  const podePreparar = podeGerenciar && grupo.formacao.vagas_disponiveis === 0;
  const podeRealizarSorteio = grupo.papel === "GESTOR" && grupo.status === "SORTEIO";
  const linkConvite = convite ? new URL(convite.invite_path, window.location.origin).toString() : "";
  const mensagemVagas = grupo.formacao.vagas_disponiveis === 0
    ? "Grupo completo."
    : grupo.formacao.vagas_disponiveis === 1
      ? "Falta 1 pessoa para completar o Grupo."
      : `Faltam ${grupo.formacao.vagas_disponiveis} pessoas para completar o Grupo.`;

  async function confirmarCancelamento() {
    setErro("");
    try { await onCancelar(); setConfirmando(false); }
    catch (error) { setErro(error instanceof Error ? error.message : "Não foi possível cancelar o grupo."); }
  }

  async function obterConvite() {
    setErro("");
    setFeedbackConvite("");
    setCarregandoConvite(true);
    try { setConvite(await onObterConvite()); }
    catch (error) { setErro(error instanceof Error ? error.message : "Não foi possível obter o convite. Tente novamente."); }
    finally { setCarregandoConvite(false); }
  }

  async function confirmarPreparacao() {
    setErro("");
    try { await onPrepararSorteio(); setConfirmandoSorteio(false); }
    catch (error) { setErro(error instanceof Error ? error.message : "Não foi possível preparar o sorteio."); }
  }

  async function confirmarRealizacao() {
    setErro("");
    try { await onRealizarSorteio(); setConfirmandoRealizacao(false); }
    catch (error) { setErro(error instanceof Error ? error.message : "Não foi possível realizar o sorteio."); }
  }

  async function copiarLink() {
    try {
      await navigator.clipboard.writeText(linkConvite);
      setFeedbackConvite("Link copiado com sucesso.");
      setErro("");
    } catch {
      setFeedbackConvite("");
      setErro("Não foi possível copiar o link. Tente novamente.");
    }
  }

  async function compartilharConvite() {
    if (!navigator.share) { await copiarLink(); return; }
    try {
      await navigator.share({
        title: `Convite para o Grupo ${grupo.nome}`,
        text: `Você foi convidado para participar do Grupo ${grupo.nome} no TooJunto. ${linkConvite}`,
        url: linkConvite,
      });
      setFeedbackConvite("Convite compartilhado.");
      setErro("");
    } catch (error) {
      if (error instanceof DOMException && error.name === "AbortError") return;
      setFeedbackConvite("");
      setErro("Não foi possível compartilhar o convite. Você pode copiar o link.");
    }
  }

  return <AppShell nome={nomeUsuario}>
    <button className="back" type="button" onClick={onVoltar}>← Voltar para Meus Grupos</button>
    <section className="screen-title"><div><span className={`badge ${grupo.status === "ATIVO" ? "group-situation drawn" : grupo.status === "CANCELADO" ? "danger" : ""}`}>{grupo.status === "ATIVO" ? "Sorteio realizado" : grupo.status === "SORTEIO" ? "Pronto para sorteio" : grupo.status}</span><h1 className="details-title">{grupo.nome}</h1><p className="subtitle">Seu papel: {grupo.papel === "GESTOR" ? "Gestor" : "Participante"}</p></div></section>
    {aviso && <p className="alert success" role="status">{aviso}</p>}
    {erro && <p className="alert error" role="alert">{erro}</p>}
    {grupo.status === "SORTEIO" && <p className="alert success" role="status">Formação encerrada. O grupo está pronto para o sorteio.</p>}
    {podeRealizarSorteio && !confirmandoRealizacao && <section className="card"><h2>Grupo pronto para sorteio</h2><button className="btn btn-primary" type="button" onClick={() => setConfirmandoRealizacao(true)}>Realizar sorteio</button></section>}
    {podeRealizarSorteio && confirmandoRealizacao && <section className="card confirmation" role="dialog" aria-labelledby="titulo-realizar-sorteio"><h2 id="titulo-realizar-sorteio">Realizar sorteio?</h2><p>Você ficará com a 1ª posição. As demais pessoas serão sorteadas.</p><p>Depois de realizado, o sorteio não poderá ser alterado.</p><button className="btn btn-primary" type="button" disabled={carregando} onClick={confirmarRealizacao}>{carregando ? "Sorteando..." : "Realizar sorteio"}</button><button className="btn btn-secondary" type="button" disabled={carregando} onClick={() => setConfirmandoRealizacao(false)}>Cancelar</button></section>}
    {grupo.status === "ATIVO" && carregandoProgresso && <p role="status">Carregando progresso do grupo...</p>}
    {grupo.status === "ATIVO" && erroProgresso && <p className="alert error" role="alert">{erroProgresso}</p>}
    {grupo.status === "ATIVO" && progresso && <section className="card cycles-progress" aria-labelledby="titulo-progresso"><h2 id="titulo-progresso">Progresso do grupo</h2><div className="cycle-current"><p>Ciclo atual</p><strong>Ciclo {progresso.ciclo_atual} de {progresso.total_ciclos}</strong><p>Contemplado: <b>{progresso.contemplado_ciclo_atual}</b></p><p>Data prevista: <b>{formatarData(progresso.data_prevista_ciclo_atual)}</b></p></div><h3>Calendário dos ciclos</h3><ol className="cycle-list">{progresso.ciclos.map((ciclo) => <li key={ciclo.numero_ciclo} className={`cycle-item cycle-${ciclo.situacao.toLowerCase()}`}><div><strong>Ciclo {ciclo.numero_ciclo}</strong><span className="cycle-status">{rotuloSituacao[ciclo.situacao]}</span></div><p>{ciclo.nome} · {ciclo.papel === "GESTOR" ? "Gestor" : "Participante"}</p><p>Data prevista: {formatarData(ciclo.data_prevista)}</p></li>)}</ol></section>}
    {grupo.status === "ATIVO" && carregandoObrigacoes && <p role="status">Carregando pagamentos do ciclo...</p>}
    {grupo.status === "ATIVO" && erroObrigacoes && !obrigacaoConfirmada && <p className="alert error" role="alert">{erroObrigacoes}</p>}
    {grupo.status === "ATIVO" && obrigacoes && <section className="card payments-section" aria-labelledby="titulo-pagamentos"><h2 id="titulo-pagamentos" ref={tituloPagamentos} tabIndex={-1}>Pagamentos do ciclo atual</h2><ul className="payments-list">{obrigacoes.map((item) => {
      const propria = item.pagador_usuario_id === usuarioId;
      const podeInformar = propria && item.status_registro === null && (item.situacao === "PENDENTE" || item.situacao === "ATRASADO");
      return <li key={item.pagador_id} className={`payment-item payment-${item.situacao.toLowerCase()} ${item.alerta_prazo ? "payment-alert" : ""}`}><div className="payment-heading"><strong>{item.pagador_nome}{propria ? " (você)" : ""}</strong><span className="payment-state">{rotuloPagamento[item.situacao]}</span></div><p>{formatarValor(item.valor)} para {item.recebedor_nome}</p><p>Prazo para pagar: {formatarData(item.prazo_pagamento)}</p><p>Data prevista do ciclo: {formatarData(item.data_prevista)}</p>{item.situacao !== "AGUARDANDO_CONFIRMACAO" && item.situacao !== "CONFIRMADO" && <p className="payment-deadline">{mensagemPrazo(item)}</p>}{podeInformar && <button className="btn btn-primary" type="button" onClick={(evento) => { botaoInformarPagamento.current = evento.currentTarget; setErroObrigacoes(""); setConfirmandoPagamento(item.pagador_id); }}>Informar pagamento</button>}</li>;
    })}</ul></section>}
    {obrigacaoConfirmada && <div className="payment-modal-backdrop"><section className="payment-modal card" role="dialog" aria-modal="true" aria-labelledby="titulo-confirmar-pagamento" aria-describedby="descricao-confirmar-pagamento"><h2 id="titulo-confirmar-pagamento">Confirmar pagamento</h2><p id="descricao-confirmar-pagamento">Você está informando que pagou {formatarValor(obrigacaoConfirmada.valor)} para {obrigacaoConfirmada.recebedor_nome}.</p><p>O pagamento ficará aguardando a confirmação de {obrigacaoConfirmada.recebedor_nome}.</p>{erroObrigacoes && <p className="alert error" role="alert">{erroObrigacoes}</p>}<button className="btn btn-primary" ref={botaoConfirmarPagamento} type="button" disabled={enviandoPagamento} onClick={confirmarPagamento}>{enviandoPagamento ? "Enviando..." : "Sim, já paguei"}</button><button className="btn btn-secondary" ref={botaoCancelarPagamento} type="button" disabled={enviandoPagamento} onClick={() => setConfirmandoPagamento(null)}>Cancelar</button></section></div>}
    {grupo.ordem_recebimento && <section className="card draw-result" aria-labelledby="titulo-ordem"><h2 id="titulo-ordem">Ordem de recebimento</h2><ol>{grupo.ordem_recebimento.map((item) => <li key={item.posicao}><strong>{item.posicao}º</strong><div><b>{item.nome}</b>{item.papel === "GESTOR" && <span> — Gestor</span>}<p>Recebe em {formatarData(item.data_prevista)}</p></div></li>)}</ol></section>}
    <section className="card group-summary" aria-label="Detalhes do grupo"><dl><div><dt>Valor por ciclo</dt><dd>{formatarValor(grupo.valor_cota)}</dd></div><div><dt>Valor do prêmio</dt><dd>{formatarValor(grupo.valor_premio)}</dd></div><div><dt>Participantes</dt><dd>{grupo.quantidade_participantes}</dd></div><div><dt>Ciclos</dt><dd>{grupo.quantidade_ciclos}</dd></div><div><dt>Data de início</dt><dd>{formatarData(grupo.data_inicio)}</dd></div></dl></section>
    <section className="card group-members" aria-labelledby="titulo-participantes">
      <div className="group-members-heading"><h2 id="titulo-participantes">Participantes</h2><strong>{grupo.formacao.quantidade_atual} de {grupo.formacao.limite} pessoas</strong></div>
      <ul>{grupo.formacao.participantes.map((participante, indice) => <li key={`${participante.nome}-${indice}`}><span>{participante.nome}</span><small className={participante.papel === "GESTOR" ? "manager-role" : ""}>{participante.papel === "GESTOR" ? "Gestor" : "Participante"}</small></li>)}</ul>
      <p className="formation-status">{mensagemVagas}</p>
    </section>
    {podeGerenciar && !podePreparar && !convite && <section className="card invite-action"><h2>Convide pessoas para o Grupo</h2><p>Compartilhe este convite com quem você deseja trazer para o grupo.</p><button className="btn btn-primary" type="button" disabled={carregandoConvite} onClick={obterConvite}>{carregandoConvite ? "Preparando convite..." : "Convidar pessoas"}</button></section>}
    {podeGerenciar && !podePreparar && convite && <section className="card invite-card"><h2>Convide pessoas para o Grupo</h2><p>Compartilhe este convite com quem você deseja trazer para o grupo.</p><div className="invite-link" aria-label="Link do convite">{linkConvite}</div>{feedbackConvite && <p className="alert success" role="status">{feedbackConvite}</p>}<button className="btn btn-primary" type="button" onClick={compartilharConvite}>Compartilhar convite</button><button className="btn btn-secondary" type="button" onClick={copiarLink}>Copiar link</button></section>}
    {podePreparar && !confirmandoSorteio && <section className="card"><h2>Seu grupo está completo</h2><p>A formação pode ser encerrada para preparar o sorteio.</p><button className="btn btn-primary" type="button" onClick={() => setConfirmandoSorteio(true)}>Preparar sorteio</button></section>}
    {podePreparar && confirmandoSorteio && <section className="card confirmation" role="dialog" aria-labelledby="titulo-preparacao"><h2 id="titulo-preparacao">Preparar sorteio?</h2><p>A formação do grupo será encerrada e não será possível adicionar novas pessoas.</p><p>Você ficará com a 1ª posição. A ordem dos demais participantes será definida no sorteio.</p><button className="btn btn-primary" type="button" disabled={carregando} onClick={confirmarPreparacao}>{carregando ? "Preparando..." : "Preparar sorteio"}</button><button className="btn btn-secondary" type="button" disabled={carregando} onClick={() => setConfirmandoSorteio(false)}>Cancelar</button></section>}
    {podeGerenciar && !confirmando && <section className="card"><h2>Gerenciar grupo</h2><button className="btn btn-secondary" type="button" onClick={onEditar}>Editar grupo</button><button className="btn btn-danger" type="button" onClick={() => setConfirmando(true)}>Cancelar grupo</button></section>}
    {podeGerenciar && confirmando && <section className="card confirmation" role="dialog" aria-labelledby="titulo-cancelamento"><h2 id="titulo-cancelamento">Cancelar este grupo?</h2><p>O grupo será cancelado, mas não será excluído. Depois disso, não será possível editar ou cancelar novamente.</p><button className="btn btn-danger-solid" type="button" disabled={carregando} onClick={confirmarCancelamento}>{carregando ? "Cancelando..." : "Sim, cancelar grupo"}</button><button className="btn btn-secondary" type="button" disabled={carregando} onClick={() => setConfirmando(false)}>Voltar</button></section>}
  </AppShell>;
}
