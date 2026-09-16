import { FormEvent, useState } from "react";
import { AppShell } from "../components/AppShell";
import type { GrupoCriacaoDados } from "../types/groups";

interface CreateGroupPageProps {
  nomeUsuario: string;
  carregando: boolean;
  onVoltar: () => void;
  onCriar: (dados: GrupoCriacaoDados) => Promise<void>;
}

export function CreateGroupPage({ nomeUsuario, carregando, onVoltar, onCriar }: CreateGroupPageProps) {
  const [dados, setDados] = useState<GrupoCriacaoDados>({ nome: "", valor_cota: "", quantidade_participantes: 2, quantidade_ciclos: 2, data_inicio: "" });
  const [erro, setErro] = useState("");
  const valorPremio = Number(dados.valor_cota) * dados.quantidade_participantes;
  const valorPremioFormatado = Number.isFinite(valorPremio) ? valorPremio.toLocaleString("pt-BR", { style: "currency", currency: "BRL" }) : "R$ 0,00";

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setErro("");
    try { await onCriar({ ...dados, nome: dados.nome.trim() }); }
    catch (error) { setErro(error instanceof Error ? error.message : "Não foi possível criar o grupo."); }
  }

  return <AppShell nome={nomeUsuario}><button className="back" type="button" onClick={onVoltar}>← Voltar para o início</button><section className="screen-title"><div><h1>Criar grupo</h1><p className="subtitle">Comece com o básico. Você poderá convidar as pessoas depois.</p></div></section><form className="card" onSubmit={enviar}>{erro && <p className="alert error" role="alert">{erro}</p>}<label htmlFor="grupo-nome">Nome do grupo *</label><input id="grupo-nome" value={dados.nome} onChange={(evento) => setDados({ ...dados, nome: evento.target.value })} placeholder="Ex.: Grupo dos Amigos" required minLength={2} maxLength={120} /><label htmlFor="grupo-valor">Valor por ciclo (R$) *</label><input id="grupo-valor" type="number" inputMode="decimal" value={dados.valor_cota} onChange={(evento) => setDados({ ...dados, valor_cota: evento.target.value })} placeholder="200,00" required min="0.01" step="0.01" /><label htmlFor="grupo-participantes">Quantidade de participantes *</label><input id="grupo-participantes" type="number" inputMode="numeric" value={dados.quantidade_participantes} onChange={(evento) => { const quantidade = Number(evento.target.value); setDados({ ...dados, quantidade_participantes: quantidade, quantidade_ciclos: quantidade }); }} required min="2" step="1" /><p className="field-help">Você já conta como uma pessoa do grupo.</p><label htmlFor="grupo-ciclos">Quantidade de ciclos</label><input id="grupo-ciclos" className="calculated-input" type="number" value={dados.quantidade_ciclos} readOnly aria-describedby="grupo-ciclos-ajuda" /><p id="grupo-ciclos-ajuda" className="field-help">Calculada automaticamente pelo número de participantes.</p><div className="calculated-value"><span>Valor do prêmio</span><output aria-live="polite">{valorPremioFormatado}</output></div><label htmlFor="grupo-data">Data de início *</label><input id="grupo-data" type="date" value={dados.data_inicio} onChange={(evento) => setDados({ ...dados, data_inicio: evento.target.value })} required /><button className="btn btn-primary" type="submit" disabled={carregando}>{carregando ? "Criando grupo..." : "Criar grupo"}</button></form></AppShell>;
}
