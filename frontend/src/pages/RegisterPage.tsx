import { FormEvent, useState } from "react";
import type { ChangeEvent } from "react";
type DadosCadastro = { nome: string; email: string; telefone: string; senha: string };
type DadosFormulario = DadosCadastro & { confirmarSenha: string };
export function RegisterPage({ carregando, onVoltar, onCadastrar }: { carregando: boolean; onVoltar: () => void; onCadastrar: (dados: DadosCadastro) => Promise<void> }) {
  const [dados, setDados] = useState<DadosFormulario>({ nome: "", email: "", telefone: "", senha: "", confirmarSenha: "" }); const [erro, setErro] = useState("");
  const atualizar = (campo: keyof DadosFormulario) => (evento: ChangeEvent<HTMLInputElement>) => setDados({ ...dados, [campo]: evento.target.value });
  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setErro("");
    if (!dados.telefone.trim()) { setErro("Informe seu telefone."); return; }
    if (dados.senha.length < 8 || dados.senha.length > 128) { setErro("A senha deve ter entre 8 e 128 caracteres."); return; }
    if (dados.senha !== dados.confirmarSenha) { setErro("As senhas não coincidem."); return; }
    const { confirmarSenha: _confirmarSenha, ...cadastro } = dados;
    try { await onCadastrar({ ...cadastro, telefone: cadastro.telefone.trim() }); }
    catch (error) { setErro(error instanceof Error ? error.message : "Não foi possível criar a conta."); }
  }
  return <div className="auth-screen"><button className="back" type="button" onClick={onVoltar}>← Voltar para entrar</button><div className="auth-heading"><h1>Criar sua conta</h1><p className="subtitle">É rápido. Vamos começar pelo básico.</p></div><form className="card" onSubmit={enviar}>{erro && <p className="alert error" role="alert">{erro}</p>}<label htmlFor="cadastro-nome">Nome completo *</label><input id="cadastro-nome" value={dados.nome} onChange={atualizar("nome")} required minLength={2} /><label htmlFor="cadastro-email">E-mail *</label><input id="cadastro-email" type="email" autoComplete="email" value={dados.email} onChange={atualizar("email")} required /><label htmlFor="cadastro-telefone">Telefone *</label><input id="cadastro-telefone" type="tel" autoComplete="tel" value={dados.telefone} onChange={atualizar("telefone")} placeholder="(71) 99999-9999" required /><label htmlFor="cadastro-senha">Senha *</label><input id="cadastro-senha" type="password" autoComplete="new-password" value={dados.senha} onChange={atualizar("senha")} required minLength={8} maxLength={128} aria-describedby="regra-senha" /><p className="field-help" id="regra-senha">A senha deve ter entre 8 e 128 caracteres.</p><label htmlFor="cadastro-confirmar-senha">Confirmar senha *</label><input id="cadastro-confirmar-senha" type="password" autoComplete="new-password" value={dados.confirmarSenha} onChange={atualizar("confirmarSenha")} required minLength={8} maxLength={128} /><button className="btn btn-primary" type="submit" disabled={carregando}>{carregando ? "Criando conta..." : "Criar conta"}</button></form></div>;
}
