import { AppShell } from "../components/AppShell";
import { GroupList } from "../components/GroupList";
import type { Usuario } from "../types/auth";
import type { GrupoLista } from "../types/groups";

interface HomePageProps {
  usuario: Usuario;
  grupos: GrupoLista[];
  carregando: boolean;
  erro: string;
  onAbrirGrupo: (grupoId: number) => void;
  onRecarregar: () => void;
}

export function HomePage({ usuario, grupos, carregando, erro, onAbrirGrupo, onRecarregar }: HomePageProps) {
  return <AppShell nome={usuario.nome}>
    <section className="screen-title"><div><h1>Meus Grupos</h1><p className="subtitle">Escolha um grupo para ver os detalhes.</p></div></section>
    {erro && <div className="alert error" role="alert">{erro}<button className="link-button" type="button" onClick={onRecarregar}>Tentar novamente</button></div>}
    {carregando ? <p className="card center" role="status">Carregando grupos...</p> : grupos.length === 0 ? <section className="card empty-state"><h2>Nenhum grupo em acompanhamento</h2><p>Crie seu primeiro grupo para começar.</p></section> : <GroupList grupos={grupos} ariaLabel="Meus Grupos" onAbrirGrupo={onAbrirGrupo} />}
  </AppShell>;
}
