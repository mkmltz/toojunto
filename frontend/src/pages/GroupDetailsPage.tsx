import { useState } from "react";
import { AppShell } from "../components/AppShell";
import type { ConviteGrupo, GrupoDetalhe } from "../types/groups";

const formatarValor = (valor: string) => Number(valor).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
const formatarData = (data: string) => new Intl.DateTimeFormat("pt-BR", { timeZone: "UTC" }).format(new Date(`${data}T00:00:00Z`));

interface GroupDetailsPageProps {
  nomeUsuario: string;
  grupo: GrupoDetalhe;
  aviso: string;
  carregando: boolean;
  onVoltar: () => void;
  onEditar: () => void;
  onCancelar: () => Promise<void>;
  onObterConvite: () => Promise<ConviteGrupo>;
  onPrepararSorteio: () => Promise<void>;
}

export function GroupDetailsPage({ nomeUsuario, grupo, aviso, carregando, onVoltar, onEditar, onCancelar, onObterConvite, onPrepararSorteio }: GroupDetailsPageProps) {
  const [confirmando, setConfirmando] = useState(false);
  const [confirmandoSorteio, setConfirmandoSorteio] = useState(false);
  const [erro, setErro] = useState("");
  const [convite, setConvite] = useState<ConviteGrupo | null>(null);
  const [carregandoConvite, setCarregandoConvite] = useState(false);
  const [feedbackConvite, setFeedbackConvite] = useState("");
  const podeGerenciar = grupo.papel === "GESTOR" && grupo.status === "RASCUNHO";
  const podePreparar = podeGerenciar && grupo.formacao.vagas_disponiveis === 0;
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
    <section className="screen-title"><div><span className={`badge ${grupo.status === "CANCELADO" ? "danger" : ""}`}>{grupo.status}</span><h1 className="details-title">{grupo.nome}</h1><p className="subtitle">Seu papel: {grupo.papel === "GESTOR" ? "Gestor" : "Participante"}</p></div></section>
    {aviso && <p className="alert success" role="status">{aviso}</p>}
    {erro && <p className="alert error" role="alert">{erro}</p>}
    {grupo.status === "SORTEIO" && <p className="alert success" role="status">Formação encerrada. O grupo está pronto para o sorteio.</p>}
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
