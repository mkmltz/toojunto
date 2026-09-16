import { useEffect, useState } from "react";
import { AuthLayout } from "./components/AuthLayout";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { ApiError, buscarUsuarioAtual, cadastrarUsuario, fazerLogin } from "./services/auth";
import type { Usuario } from "./types/auth";

const CHAVE_TOKEN = "toojunto_access_token";
type Tela = "login" | "cadastro";
function mensagemDeErro(error: unknown) { if (error instanceof ApiError && error.status === 401) return "E-mail ou senha inválidos."; return error instanceof Error ? error.message : "Não foi possível concluir esta ação."; }

export default function App() {
  const [tela, setTela] = useState<Tela>("login"); const [usuario, setUsuario] = useState<Usuario | null>(null); const [carregandoSessao, setCarregandoSessao] = useState(true); const [enviando, setEnviando] = useState(false); const [aviso, setAviso] = useState("");
  useEffect(() => { const token = localStorage.getItem(CHAVE_TOKEN); if (!token) { setCarregandoSessao(false); return; } buscarUsuarioAtual(token).then(setUsuario).catch((error: unknown) => { if (error instanceof ApiError && error.status === 401) localStorage.removeItem(CHAVE_TOKEN); }).finally(() => setCarregandoSessao(false)); }, []);
  async function entrar(email: string, senha: string) { setEnviando(true); try { const resposta = await fazerLogin({ email, senha }); localStorage.setItem(CHAVE_TOKEN, resposta.access_token); setUsuario(await buscarUsuarioAtual(resposta.access_token)); } catch (error) { localStorage.removeItem(CHAVE_TOKEN); throw new Error(mensagemDeErro(error)); } finally { setEnviando(false); } }
  async function cadastrar(dados: { nome: string; email: string; telefone: string; senha: string }) { setEnviando(true); try { await cadastrarUsuario({ ...dados, telefone: dados.telefone || undefined }); setAviso("Conta criada com sucesso. Agora entre para continuar."); setTela("login"); } catch (error) { throw new Error(mensagemDeErro(error)); } finally { setEnviando(false); } }
  function sair() { localStorage.removeItem(CHAVE_TOKEN); setUsuario(null); setTela("login"); setAviso("Você saiu da sua conta."); }
  if (carregandoSessao) return <main className="loading-screen">Carregando TooJunto...</main>;
  if (usuario) return <HomePage usuario={usuario} onSair={sair} />;
  return <AuthLayout>{tela === "login" ? <LoginPage aviso={aviso} carregando={enviando} onEntrar={entrar} onCadastrar={() => { setAviso(""); setTela("cadastro"); }} /> : <RegisterPage carregando={enviando} onVoltar={() => setTela("login")} onCadastrar={cadastrar} />}</AuthLayout>;
}
