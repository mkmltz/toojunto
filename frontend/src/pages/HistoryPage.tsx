import { AppShell } from "../components/AppShell";
import { GroupList } from "../components/GroupList";
import type { GrupoLista } from "../types/groups";

interface HistoryPageProps {
  nomeUsuario: string;
  grupos: GrupoLista[];
  carregando: boolean;
  erro: string;
  onAbrirGrupo: (grupoId: number) => void;
  onRecarregar: () => void;
  onVoltar: () => void;
}

export function HistoryPage({ nomeUsuario, grupos, carregando, erro, onAbrirGrupo, onRecarregar, onVoltar }: HistoryPageProps) {
  return <AppShell nome={nomeUsuario}>
    <button className="back" type="button" onClick={onVoltar}>← Voltar para Meus Grupos</button>
    <section className="screen-title"><div><h1>Histórico</h1><p className="subtitle">Consulte seus grupos encerrados ou cancelados.</p></div></section>
    {erro && <div className="alert error" role="alert">{erro}<button className="link-button" type="button" onClick={onRecarregar}>Tentar novamente</button></div>}
    {carregando
      ? <p className="card center" role="status">Carregando histórico...</p>
      : grupos.length === 0
        ? <section className="card empty-state"><h2>Nenhum grupo no histórico</h2><p>Quando um grupo for encerrado ou cancelado, ele aparecerá aqui.</p></section>
        : <GroupList grupos={grupos} ariaLabel="Histórico" onAbrirGrupo={onAbrirGrupo} />}
  </AppShell>;
}
