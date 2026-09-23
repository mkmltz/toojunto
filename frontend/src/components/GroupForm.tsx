import { FormEvent, useState } from "react";
import type { GrupoFormularioDados } from "../types/groups";

interface GroupFormProps {
  carregando: boolean;
  dadosIniciais?: GrupoFormularioDados;
  textoBotao: string;
  textoCarregando: string;
  onEnviar: (dados: GrupoFormularioDados) => Promise<void>;
}

const DADOS_INICIAIS: GrupoFormularioDados = { nome: "", valor_cota: "", quantidade_participantes: 2, data_inicio: "" };
const hoje = new Date();
const DATA_MINIMA = [
  hoje.getFullYear(),
  String(hoje.getMonth() + 1).padStart(2, "0"),
  String(hoje.getDate()).padStart(2, "0"),
].join("-");

export function GroupForm({ carregando, dadosIniciais = DADOS_INICIAIS, textoBotao, textoCarregando, onEnviar }: GroupFormProps) {
  const [dados, setDados] = useState<GrupoFormularioDados>(dadosIniciais);
  const [erro, setErro] = useState("");
  const valorPremio = Number(dados.valor_cota) * dados.quantidade_participantes;
  const valorPremioFormatado = Number.isFinite(valorPremio) ? valorPremio.toLocaleString("pt-BR", { style: "currency", currency: "BRL" }) : "R$ 0,00";

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setErro("");
    try { await onEnviar({ ...dados, nome: dados.nome.trim() }); }
    catch (error) { setErro(error instanceof Error ? error.message : "Não foi possível salvar o grupo."); }
  }

  return <form className="card" onSubmit={enviar}>
    {erro && <p className="alert error" role="alert">{erro}</p>}
    <label htmlFor="grupo-nome">Nome do grupo *</label><input id="grupo-nome" value={dados.nome} onChange={(evento) => setDados({ ...dados, nome: evento.target.value })} placeholder="Ex.: Grupo dos Amigos" required minLength={2} maxLength={120} />
    <label htmlFor="grupo-valor">Valor por ciclo (R$) *</label><input id="grupo-valor" type="number" inputMode="decimal" value={dados.valor_cota} onChange={(evento) => setDados({ ...dados, valor_cota: evento.target.value })} placeholder="200,00" required min="0.01" step="0.01" />
    <label htmlFor="grupo-participantes">Quantidade de participantes *</label><input id="grupo-participantes" type="number" inputMode="numeric" value={dados.quantidade_participantes} onChange={(evento) => setDados({ ...dados, quantidade_participantes: Number(evento.target.value) })} required min="2" step="1" />
    <p className="field-help">Você já conta como uma pessoa do grupo.</p>
    <label htmlFor="grupo-ciclos">Quantidade de ciclos</label><input id="grupo-ciclos" className="calculated-input" type="number" value={dados.quantidade_participantes} readOnly aria-describedby="grupo-ciclos-ajuda" />
    <p id="grupo-ciclos-ajuda" className="field-help">Calculada automaticamente pelo número de participantes.</p>
    <div className="calculated-value"><span>Valor do prêmio</span><output aria-live="polite">{valorPremioFormatado}</output></div>
    <label htmlFor="grupo-data">Data de início *</label><input id="grupo-data" type="date" value={dados.data_inicio} onChange={(evento) => setDados({ ...dados, data_inicio: evento.target.value })} required min={DATA_MINIMA} />
    <button className="btn btn-primary" type="submit" disabled={carregando}>{carregando ? textoCarregando : textoBotao}</button>
  </form>;
}
