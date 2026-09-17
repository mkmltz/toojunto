import { AppShell } from "../components/AppShell";
import { GroupForm } from "../components/GroupForm";
import type { GrupoCriacaoDados, GrupoFormularioDados } from "../types/groups";

interface CreateGroupPageProps {
  nomeUsuario: string;
  carregando: boolean;
  onVoltar: () => void;
  onCriar: (dados: GrupoCriacaoDados) => Promise<void>;
}

export function CreateGroupPage({ nomeUsuario, carregando, onVoltar, onCriar }: CreateGroupPageProps) {
  async function criar(dados: GrupoFormularioDados) {
    await onCriar({ ...dados, quantidade_ciclos: dados.quantidade_participantes });
  }

  return <AppShell nome={nomeUsuario}>
    <button className="back" type="button" onClick={onVoltar}>← Voltar para o início</button>
    <section className="screen-title"><div><h1>Criar grupo</h1><p className="subtitle">Comece com o básico. Você poderá convidar as pessoas depois.</p></div></section>
    <GroupForm carregando={carregando} textoBotao="Criar grupo" textoCarregando="Criando grupo..." onEnviar={criar} />
  </AppShell>;
}
