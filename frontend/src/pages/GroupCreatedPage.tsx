import { AppShell } from "../components/AppShell";
import type { Grupo } from "../types/groups";

const formatarValor = (valor: string) => Number(valor).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
const formatarData = (data: string) => new Intl.DateTimeFormat("pt-BR", { timeZone: "UTC" }).format(new Date(`${data}T00:00:00Z`));

export function GroupCreatedPage({ grupo, nomeUsuario, onVoltar, onVerGrupo }: { grupo: Grupo; nomeUsuario: string; onVoltar: () => void; onVerGrupo: () => void }) {
  return <AppShell nome={nomeUsuario}><section className="screen-title"><div><span className="badge">Grupo criado</span><h1 className="success-title">Tudo certo!</h1><p className="subtitle">Seu grupo foi criado e você já faz parte dele.</p></div></section><section className="card group-summary" aria-label="Resumo do grupo"><h2>{grupo.nome}</h2><dl><div><dt>Valor por ciclo</dt><dd>{formatarValor(grupo.valor_cota)}</dd></div><div><dt>Participantes</dt><dd>{grupo.quantidade_participantes}</dd></div><div><dt>Ciclos</dt><dd>{grupo.quantidade_ciclos}</dd></div><div><dt>Valor do prêmio</dt><dd>{formatarValor(grupo.valor_premio)}</dd></div><div><dt>Início</dt><dd>{formatarData(grupo.data_inicio)}</dd></div></dl><p className="alert success" role="status">Grupo criado com sucesso.</p><button className="btn btn-primary" type="button" onClick={onVerGrupo}>Ver grupo</button><button className="btn btn-secondary" type="button" onClick={onVoltar}>Voltar para Meus Grupos</button></section></AppShell>;
}
