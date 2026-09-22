import { useEffect, useRef, useState } from "react";
import { AppShell } from "../components/AppShell";
import { avaliarPagamento, buscarObrigacoesPagamento, buscarProgressoGrupo, informarPagamento } from "../services/groups";
import type { ConviteGrupo, GrupoDetalhe, ObrigacaoPagamento, ProgressoGrupo, SituacaoCiclo, SituacaoObrigacao } from "../types/groups";

const formatarValor = (valor: string) => Number(valor).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
const formatarData = (data: string) => new Intl.DateTimeFormat("pt-BR", { timeZone: "UTC" }).format(new Date(`${data}T00:00:00Z`));
const rotuloSituacao: Record<SituacaoCiclo, string> = { ATUAL: "ATUAL", PROXIMO: "PRÓXIMO", CONCLUIDO: "CONCLUÍDO" };
const rotuloPagamento: Record<SituacaoObrigacao, string> = { PENDENTE: "Pendente", AGUARDANDO_CONFIRMACAO: "Aguardando confirmação", ATRASADO: "Atrasado", CONFIRMADO: "Confirmado", REJEITADO: "Rejeitado" };
type AcaoPagamento = { tipo: "informar" | "confirmar" | "rejeitar"; pagadorId: number };

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
  const [acaoPagamento, setAcaoPagamento] = useState<AcaoPagamento | null>(null);
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
    if (grupo.status !== "ATIVO" && grupo.status !== "ENCERRADO") return;
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
    if ((grupo.status !== "ATIVO" && grupo.status !== "ENCERRADO") || !progresso) return;
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
  const grupoConcluido = Boolean(progresso?.grupo_concluido || grupo.status === "ENCERRADO");
  const obrigacaoSelecionada = obrigacoes?.find((item) => item.pagador_id === acaoPagamento?.pagadorId);
  useEffect(() => {
    if (acaoPagamento === null) {
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
        setAcaoPagamento(null);
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
  }, [acaoPagamento]);

  async function executarAcaoPagamento() {
    if (!progresso || !obrigacaoSelecionada || !acaoPagamento || envioPagamentoEmAndamento.current) return;
    const token = localStorage.getItem("toojunto_access_token");
    if (!token) { setErroObrigacoes("Entre novamente para continuar."); return; }
    envioPagamentoEmAndamento.current = true;
    setEnviandoPagamento(true);
    setErroObrigacoes("");
    try {
      const atualizado = acaoPagamento.tipo === "informar"
        ? await informarPagamento(grupo.id, progresso.ciclo_atual, token)
        : await avaliarPagamento(grupo.id, progresso.ciclo_atual, obrigacaoSelecionada.pagamento_id!, acaoPagamento.tipo === "confirmar" ? "confirm" : "reject", token);
      setObrigacoes((atuais) => atuais?.map((item) => item.pagador_id === atualizado.pagador_id ? atualizado : item) ?? null);
      setAcaoPagamento(null);
      try {
        if (acaoPagamento.tipo === "informar") {
          setObrigacoes(await buscarObrigacoesPagamento(grupo.id, progresso.ciclo_atual, token));
        } else {
          setProgresso(await buscarProgressoGrupo(grupo.id, token));
        }
      } catch {
        setErroObrigacoes("Ação registrada. Não foi possível atualizar a lista.");
      }
    } catch {
      setErroObrigacoes(acaoPagamento.tipo === "informar"
        ? "Não foi possível informar o pagamento. Confira a situação e tente novamente."
        : "Não foi possível avaliar o pagamento. Tente novamente.");
    } finally {
      envioPagamentoEmAndamento.current = false;
      setEnviandoPagamento(false);
    }
  }
  const podeGerenciar = grupo.papel === "GESTOR" && grupo.status === "RASCUNHO";
  const temCiclos = grupo.status === "ATIVO" || grupo.status === "ENCERRADO";
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
    <section className="screen-title"><div><span className={`badge ${grupoConcluido ? "group-situation complete" : grupo.status === "ATIVO" ? "group-situation drawn" : grupo.status === "CANCELADO" ? "danger" : ""}`}>{grupoConcluido ? "Grupo concluído" : grupo.status === "ATIVO" ? "Sorteio realizado" : grupo.status === "SORTEIO" ? "Pronto para sorteio" : grupo.status}</span><h1 className="details-title">{grupo.nome}</h1><p className="subtitle">Seu papel: {grupo.papel === "GESTOR" ? "Gestor" : "Participante"}</p></div></section>
    {aviso && <p className="alert success" role="status">{aviso}</p>}
    {erro && <p className="alert error" role="alert">{erro}</p>}
    {grupo.status === "SORTEIO" && <p className="alert success" role="status">Formação encerrada. O grupo está pronto para o sorteio.</p>}
    {podeRealizarSorteio && !confirmandoRealizacao && <section className="card"><h2>Grupo pronto para sorteio</h2><button className="btn btn-primary" type="button" onClick={() => setConfirmandoRealizacao(true)}>Realizar sorteio</button></section>}
    {podeRealizarSorteio && confirmandoRealizacao && <section className="card confirmation" role="dialog" aria-labelledby="titulo-realizar-sorteio"><h2 id="titulo-realizar-sorteio">Realizar sorteio?</h2><p>Você ficará com a 1ª posição. As demais pessoas serão sorteadas.</p><p>Depois de realizado, o sorteio não poderá ser alterado.</p><button className="btn btn-primary" type="button" disabled={carregando} onClick={confirmarRealizacao}>{carregando ? "Sorteando..." : "Realizar sorteio"}</button><button className="btn btn-secondary" type="button" disabled={carregando} onClick={() => setConfirmandoRealizacao(false)}>Cancelar</button></section>}
    {grupoConcluido && <p className="alert success" role="status"><b>Grupo concluído.</b> Todos os ciclos e pagamentos deste Grupo foram concluídos.</p>}
    {temCiclos && carregandoProgresso && <p role="status">Carregando progresso do grupo...</p>}
    {temCiclos && erroProgresso && <p className="alert error" role="alert">{erroProgresso}</p>}
    {temCiclos && progresso && <section className="card cycles-progress" aria-labelledby="titulo-progresso"><h2 id="titulo-progresso">Progresso do grupo</h2>{!grupoConcluido && <div className="cycle-current"><p>Ciclo atual</p><strong>Ciclo {progresso.ciclo_atual} de {progresso.total_ciclos}</strong><p>Contemplado: <b>{progresso.contemplado_ciclo_atual}</b></p><p>Data prevista: <b>{formatarData(progresso.data_prevista_ciclo_atual)}</b></p></div>}<h3>Calendário dos ciclos</h3><ol className="cycle-list">{progresso.ciclos.map((ciclo) => <li key={ciclo.numero_ciclo} className={`cycle-item cycle-${ciclo.situacao.toLowerCase()}`}><div><strong>Ciclo {ciclo.numero_ciclo}</strong><span className="cycle-status">{rotuloSituacao[ciclo.situacao]}</span></div><p>{ciclo.nome} · {ciclo.papel === "GESTOR" ? "Gestor" : "Participante"}</p><p>Data prevista: {formatarData(ciclo.data_prevista)}</p></li>)}</ol></section>}
    {temCiclos && carregandoObrigacoes && <p role="status">Carregando pagamentos do ciclo...</p>}
    {temCiclos && erroObrigacoes && !obrigacaoSelecionada && <p className="alert error" role="alert">{erroObrigacoes}</p>}
    {temCiclos && obrigacoes && <section className="card payments-section" aria-labelledby="titulo-pagamentos"><h2 id="titulo-pagamentos" ref={tituloPagamentos} tabIndex={-1}>{grupoConcluido ? "Pagamentos do último ciclo" : "Pagamentos do ciclo atual"}</h2><ul className="payments-list">{obrigacoes.map((item) => {
      const propria = item.pagador_usuario_id === usuarioId;
      const podeInformar = !grupoConcluido && propria && (item.status_registro === null || item.status_registro === "REJEITADO") && (item.situacao === "PENDENTE" || item.situacao === "ATRASADO" || item.situacao === "REJEITADO");
      const podeAvaliar = !grupoConcluido && item.pode_avaliar === true && item.pagamento_id != null && item.status_registro === "AGUARDANDO_CONFIRMACAO";
      return <li key={item.pagador_id} className={`payment-item payment-${item.situacao.toLowerCase()} ${item.alerta_prazo ? "payment-alert" : ""}`}><div className="payment-heading"><strong>{item.pagador_nome}{propria ? " (você)" : ""}</strong><span className="payment-state">{rotuloPagamento[item.situacao]}</span></div><p>{formatarValor(item.valor)} para {item.recebedor_nome}</p><p>Prazo para pagar: {formatarData(item.prazo_pagamento)}</p><p>Data prevista do ciclo: {formatarData(item.data_prevista)}</p>{item.situacao !== "AGUARDANDO_CONFIRMACAO" && item.situacao !== "CONFIRMADO" && <p className="payment-deadline">{mensagemPrazo(item)}</p>}{podeInformar && <button className="btn btn-primary" type="button" onClick={(evento) => { botaoInformarPagamento.current = evento.currentTarget; setErroObrigacoes(""); setAcaoPagamento({ tipo: "informar", pagadorId: item.pagador_id }); }}>Informar pagamento</button>}{podeAvaliar && <div className="payment-actions"><button className="btn btn-primary" type="button" onClick={(evento) => { botaoInformarPagamento.current = evento.currentTarget; setErroObrigacoes(""); setAcaoPagamento({ tipo: "confirmar", pagadorId: item.pagador_id }); }}>Confirmar</button><button className="btn btn-secondary" type="button" onClick={(evento) => { botaoInformarPagamento.current = evento.currentTarget; setErroObrigacoes(""); setAcaoPagamento({ tipo: "rejeitar", pagadorId: item.pagador_id }); }}>Rejeitar</button></div>}</li>;
    })}</ul></section>}
    {obrigacaoSelecionada && acaoPagamento && <div className="payment-modal-backdrop"><section className="payment-modal card" role="dialog" aria-modal="true" aria-labelledby="titulo-confirmar-pagamento" aria-describedby="descricao-confirmar-pagamento"><h2 id="titulo-confirmar-pagamento">{acaoPagamento.tipo === "informar" ? "Confirmar pagamento" : acaoPagamento.tipo === "confirmar" ? "Confirmar recebimento?" : "Rejeitar pagamento?"}</h2><p id="descricao-confirmar-pagamento">{acaoPagamento.tipo === "informar" ? `Você está informando que pagou ${formatarValor(obrigacaoSelecionada.valor)} para ${obrigacaoSelecionada.recebedor_nome}.` : acaoPagamento.tipo === "confirmar" ? `Você confirma que recebeu o pagamento de ${obrigacaoSelecionada.pagador_nome} no valor de ${formatarValor(obrigacaoSelecionada.valor)}?` : `Você está informando que ainda não recebeu o pagamento de ${obrigacaoSelecionada.pagador_nome}.`}</p>{acaoPagamento.tipo === "informar" && <p>O pagamento ficará aguardando a confirmação de {obrigacaoSelecionada.recebedor_nome}.</p>}{acaoPagamento.tipo === "rejeitar" && <p>O participante poderá informar o pagamento novamente.</p>}{erroObrigacoes && <p className="alert error" role="alert">{erroObrigacoes}</p>}<button className="btn btn-primary" ref={botaoConfirmarPagamento} type="button" disabled={enviandoPagamento} onClick={executarAcaoPagamento}>{enviandoPagamento ? "Enviando..." : acaoPagamento.tipo === "informar" ? "Sim, já paguei" : acaoPagamento.tipo === "confirmar" ? "Sim, recebi" : "Rejeitar pagamento"}</button><button className="btn btn-secondary" ref={botaoCancelarPagamento} type="button" disabled={enviandoPagamento} onClick={() => setAcaoPagamento(null)}>Cancelar</button></section></div>}
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
