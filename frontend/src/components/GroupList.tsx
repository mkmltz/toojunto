import type { GrupoLista } from "../types/groups";

const formatarValor = (valor: string) => Number(valor).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
const formatarPapel = (papel: GrupoLista["papel"]) => papel === "GESTOR" ? "Gestor" : "Participante";

function situacaoGrupo(grupo: GrupoLista) {
  if (grupo.status === "RASCUNHO") return grupo.vagas_disponiveis === 0
    ? { texto: "Grupo completo", classe: "complete" }
    : { texto: "Em formação", classe: "forming" };
  if (grupo.status === "SORTEIO") return { texto: "Pronto para sorteio", classe: "ready" };
  if (grupo.status === "ATIVO") return { texto: "Em andamento", classe: "drawn" };
  if (grupo.status === "ENCERRADO") return { texto: "Grupo concluído", classe: "finished" };
  if (grupo.status === "CANCELADO") return { texto: "Cancelado", classe: "danger" };
  return { texto: grupo.status, classe: "" };
}

interface GroupListProps {
  grupos: GrupoLista[];
  ariaLabel: string;
  onAbrirGrupo: (grupoId: number) => void;
}

export function GroupList({ grupos, ariaLabel, onAbrirGrupo }: GroupListProps) {
  return <section className="group-list" aria-label={ariaLabel}>
    {grupos.map((grupo) => {
      const situacao = situacaoGrupo(grupo);
      return <article className="card group-card" key={grupo.id}>
        <div className="group-card-heading"><h2>{grupo.nome}</h2><span className={`badge group-situation ${situacao.classe}`}>{situacao.texto}</span></div>
        <p className="role-label">{formatarPapel(grupo.papel)}</p>
        <p className="manager-label">Gestor: {grupo.gestor_nome}</p>
        <dl><div><dt>Valor por ciclo</dt><dd>{formatarValor(grupo.valor_cota)}</dd></div><div><dt>Valor do prêmio</dt><dd>{formatarValor(grupo.valor_premio)}</dd></div></dl>
        <button className="btn btn-primary" type="button" onClick={() => onAbrirGrupo(grupo.id)}>Ver grupo</button>
      </article>;
    })}
  </section>;
}
