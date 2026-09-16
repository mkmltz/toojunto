import type { CadastroDados, LoginDados, TokenResposta, Usuario } from "../types/auth";

const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";
export class ApiError extends Error { constructor(public readonly status: number, message: string) { super(message); } }

export async function requisicao<T>(caminho: string, opcoes: RequestInit = {}): Promise<T> {
  const resposta = await fetch(`${API_URL}${caminho}`, { ...opcoes, headers: { "Content-Type": "application/json", ...opcoes.headers } });
  const corpo = await resposta.json().catch(() => null);
  if (!resposta.ok) throw new ApiError(resposta.status, typeof corpo?.detail === "string" ? corpo.detail : "Não foi possível concluir esta ação.");
  return corpo as T;
}
export const fazerLogin = (dados: LoginDados) => requisicao<TokenResposta>("/auth/login", { method: "POST", body: JSON.stringify(dados) });
export const cadastrarUsuario = (dados: CadastroDados) => requisicao<Usuario>("/auth/register", { method: "POST", body: JSON.stringify(dados) });
export const buscarUsuarioAtual = (token: string) => requisicao<Usuario>("/auth/me", { headers: { Authorization: `Bearer ${token}` } });
