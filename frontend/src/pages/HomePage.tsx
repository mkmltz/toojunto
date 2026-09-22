import { AppShell } from "../components/AppShell";
import type { Usuario } from "../types/auth";
import type { GrupoLista } from "../types/groups";

const formatarValor = (valor: string) => Number(valor).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
const formatarPapel = (papel: GrupoLista["papel"]) => papel === "GESTOR" ? "Gestor" : "Participante";

function situacaoGrupo(grupo: GrupoLista) {
  if (grupo.status === "RASCUNHO") return grupo.vagas_disponiveis === 0
    ? { texto: "Grupo completo", classe: "complete" }
    : { texto: "Em formação", classe: "forming" };
  if (grupo.status === "SORTEIO") return { texto: "Pronto para sorteio", classe: "ready" };
  if (grupo.status === "ATIVO") return { texto: "Sorteio realizado", classe: "drawn" };
  if (grupo.status === "CANCELADO") return { texto: "Cancelado", classe: "danger" };
  return { texto: grupo.status, classe: "" };
}

interface HomePageProps {
  usuario: Usuario;
  grupos: GrupoLista[];
  carregando: boolean;
  erro: string;
  onAbrirGrupo: (grupoId: number) => void;
  onCriarGrupo: () => void;
  onRecarregar: () => void;
  onSair: () => void;
}

export function HomePage({ usuario, grupos, carregando, erro, onAbrirGrupo, onCriarGrupo, onRecarregar, onSair }: HomePageProps) {
  return <AppShell nome={usuario.nome}>
    <section className="screen-title"><div><h1>Meus Grupos</h1><p className="subtitle">Escolha um grupo para ver os detalhes.</p></div></section>
    {erro && <div className="alert error" role="alert">{erro}<button className="link-button" type="button" onClick={onRecarregar}>Tentar novamente</button></div>}
    {carregando ? <p className="card center" role="status">Carregando grupos...</p> : grupos.length === 0 ? <section className="card empty-state"><h2>Nenhum grupo ainda</h2><p>Crie seu primeiro grupo para começar.</p></section> : <section className="group-list" aria-label="Meus Grupos">{grupos.map((grupo) => <article className="card group-card" key={grupo.id}><div className="group-card-heading"><h2>{grupo.nome}</h2><span className={`badge group-situation ${situacaoGrupo(grupo).classe}`}>{situacaoGrupo(grupo).texto}</span></div><p className="role-label">{formatarPapel(grupo.papel)}</p><dl><div><dt>Valor por ciclo</dt><dd>{formatarValor(grupo.valor_cota)}</dd></div><div><dt>Valor do prêmio</dt><dd>{formatarValor(grupo.valor_premio)}</dd></div></dl><button className="btn btn-primary" type="button" onClick={() => onAbrirGrupo(grupo.id)}>Ver grupo</button></article>)}</section>}
    <button className="btn btn-secondary" type="button" onClick={onCriarGrupo}>+ Criar novo grupo</button>
    <button className="btn btn-quiet" type="button" onClick={onSair}>Sair</button>
  </AppShell>;
}
