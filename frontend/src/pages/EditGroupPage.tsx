import { AppShell } from "../components/AppShell";
import { GroupForm } from "../components/GroupForm";
import type { GrupoAtualizacaoDados, GrupoComPapel } from "../types/groups";

export function EditGroupPage({ nomeUsuario, grupo, carregando, onVoltar, onSalvar }: { nomeUsuario: string; grupo: GrupoComPapel; carregando: boolean; onVoltar: () => void; onSalvar: (dados: GrupoAtualizacaoDados) => Promise<void> }) {
  return <AppShell nome={nomeUsuario}>
    <button className="back" type="button" onClick={onVoltar}>← Voltar para o grupo</button>
    <section className="screen-title"><div><h1>Editar grupo</h1><p className="subtitle">Confira os dados antes de salvar.</p></div></section>
    <GroupForm carregando={carregando} dadosIniciais={{ nome: grupo.nome, valor_cota: grupo.valor_cota, quantidade_participantes: grupo.quantidade_participantes, data_inicio: grupo.data_inicio }} textoBotao="Salvar alterações" textoCarregando="Salvando..." onEnviar={onSalvar} />
  </AppShell>;
}
