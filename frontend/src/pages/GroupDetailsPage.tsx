import { useState } from "react";
import { AppShell } from "../components/AppShell";
import type { GrupoComPapel } from "../types/groups";

const formatarValor = (valor: string) => Number(valor).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
const formatarData = (data: string) => new Intl.DateTimeFormat("pt-BR", { timeZone: "UTC" }).format(new Date(`${data}T00:00:00Z`));

interface GroupDetailsPageProps {
  nomeUsuario: string;
  grupo: GrupoComPapel;
  aviso: string;
  carregando: boolean;
  onVoltar: () => void;
  onEditar: () => void;
  onCancelar: () => Promise<void>;
}

export function GroupDetailsPage({ nomeUsuario, grupo, aviso, carregando, onVoltar, onEditar, onCancelar }: GroupDetailsPageProps) {
  const [confirmando, setConfirmando] = useState(false);
  const [erro, setErro] = useState("");
  const podeGerenciar = grupo.papel === "GESTOR" && grupo.status === "RASCUNHO";

  async function confirmarCancelamento() {
    setErro("");
    try { await onCancelar(); setConfirmando(false); }
    catch (error) { setErro(error instanceof Error ? error.message : "Não foi possível cancelar o grupo."); }
  }

  return <AppShell nome={nomeUsuario}>
    <button className="back" type="button" onClick={onVoltar}>← Voltar para Meus Grupos</button>
    <section className="screen-title"><div><span className={`badge ${grupo.status === "CANCELADO" ? "danger" : ""}`}>{grupo.status}</span><h1 className="details-title">{grupo.nome}</h1><p className="subtitle">Seu papel: {grupo.papel === "GESTOR" ? "Gestor" : "Participante"}</p></div></section>
    {aviso && <p className="alert success" role="status">{aviso}</p>}
    {erro && <p className="alert error" role="alert">{erro}</p>}
    <section className="card group-summary" aria-label="Detalhes do grupo"><dl><div><dt>Valor por ciclo</dt><dd>{formatarValor(grupo.valor_cota)}</dd></div><div><dt>Valor do prêmio</dt><dd>{formatarValor(grupo.valor_premio)}</dd></div><div><dt>Participantes</dt><dd>{grupo.quantidade_participantes}</dd></div><div><dt>Ciclos</dt><dd>{grupo.quantidade_ciclos}</dd></div><div><dt>Data de início</dt><dd>{formatarData(grupo.data_inicio)}</dd></div></dl></section>
    {podeGerenciar && !confirmando && <section className="card"><h2>Gerenciar grupo</h2><button className="btn btn-primary" type="button" onClick={onEditar}>Editar grupo</button><button className="btn btn-danger" type="button" onClick={() => setConfirmando(true)}>Cancelar grupo</button></section>}
    {podeGerenciar && confirmando && <section className="card confirmation" role="dialog" aria-labelledby="titulo-cancelamento"><h2 id="titulo-cancelamento">Cancelar este grupo?</h2><p>O grupo será cancelado, mas não será excluído. Depois disso, não será possível editar ou cancelar novamente.</p><button className="btn btn-danger-solid" type="button" disabled={carregando} onClick={confirmarCancelamento}>{carregando ? "Cancelando..." : "Sim, cancelar grupo"}</button><button className="btn btn-secondary" type="button" disabled={carregando} onClick={() => setConfirmando(false)}>Voltar</button></section>}
  </AppShell>;
}
