import { useEffect, useState } from "react";
import { AuthLayout } from "./components/AuthLayout";
import { CreateGroupPage } from "./pages/CreateGroupPage";
import { EditGroupPage } from "./pages/EditGroupPage";
import { GroupCreatedPage } from "./pages/GroupCreatedPage";
import { GroupDetailsPage } from "./pages/GroupDetailsPage";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { ApiError, buscarUsuarioAtual, cadastrarUsuario, fazerLogin } from "./services/auth";
import { atualizarGrupo, buscarGrupo, cancelarGrupo, criarGrupo, listarGrupos } from "./services/groups";
import type { Usuario } from "./types/auth";
import type { Grupo, GrupoAtualizacaoDados, GrupoComPapel, GrupoCriacaoDados } from "./types/groups";

const CHAVE_TOKEN = "toojunto_access_token";
const CHAVE_GRUPO = "toojunto_selected_group_id";
type Tela = "login" | "cadastro" | "home" | "criar-grupo" | "grupo-criado" | "detalhes" | "editar-grupo";

function mensagemDeErro(error: unknown) {
  return error instanceof Error ? error.message : "Não foi possível concluir esta ação.";
}

function mensagemDeErroGrupo(error: unknown) {
  if (error instanceof ApiError) {
    if (error.status === 403) return "Você não tem permissão para gerenciar este grupo.";
    if (error.status === 404) return "Grupo não encontrado ou sem acesso.";
    if (error.status === 409) return "Este grupo não pode mais ser alterado.";
    if (error.status === 422) return "Confira os dados do grupo e tente novamente.";
  }
  return mensagemDeErro(error);
}

export default function App() {
  const [tela, setTela] = useState<Tela>("login");
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [grupos, setGrupos] = useState<GrupoComPapel[]>([]);
  const [grupoSelecionado, setGrupoSelecionado] = useState<GrupoComPapel | null>(null);
  const [grupoCriado, setGrupoCriado] = useState<Grupo | null>(null);
  const [carregandoSessao, setCarregandoSessao] = useState(true);
  const [carregandoLista, setCarregandoLista] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [aviso, setAviso] = useState("");
  const [avisoGrupo, setAvisoGrupo] = useState("");
  const [erroLista, setErroLista] = useState("");

  function encerrarSessao(mensagem: string) {
    localStorage.removeItem(CHAVE_TOKEN);
    localStorage.removeItem(CHAVE_GRUPO);
    setUsuario(null);
    setGrupos([]);
    setGrupoSelecionado(null);
    setGrupoCriado(null);
    setTela("login");
    setAviso(mensagem);
  }

  useEffect(() => {
    const token = localStorage.getItem(CHAVE_TOKEN);
    if (!token) { setCarregandoSessao(false); return; }
    async function restaurar() {
      try {
        const usuarioAtual = await buscarUsuarioAtual(token!);
        const grupoId = Number(localStorage.getItem(CHAVE_GRUPO));
        if (grupoId) {
          try {
            const grupo = await buscarGrupo(grupoId, token!);
            setGrupoSelecionado(grupo);
            setTela("detalhes");
          } catch (error) {
            if (error instanceof ApiError && error.status === 401) throw error;
            localStorage.removeItem(CHAVE_GRUPO);
            setAvisoGrupo(error instanceof ApiError && error.status === 404 ? "O grupo selecionado não está mais disponível." : "Não foi possível reabrir o grupo.");
            setTela("home");
          }
        } else {
          setTela("home");
        }
        setUsuario(usuarioAtual);
      } catch (error) {
        if (error instanceof ApiError && error.status === 401) encerrarSessao("Sua sessão terminou. Entre novamente para continuar.");
      } finally {
        setCarregandoSessao(false);
      }
    }
    restaurar();
  }, []);

  useEffect(() => {
    if (usuario && tela === "home") carregarGrupos();
  }, [usuario, tela]);

  async function carregarGrupos() {
    const token = localStorage.getItem(CHAVE_TOKEN);
    if (!token) { encerrarSessao("Entre novamente para ver seus grupos."); return; }
    setCarregandoLista(true);
    setErroLista("");
    try { setGrupos(await listarGrupos(token)); }
    catch (error) {
      if (error instanceof ApiError && error.status === 401) { encerrarSessao("Sua sessão terminou. Entre novamente para continuar."); return; }
      setErroLista("Não foi possível carregar seus grupos.");
    } finally { setCarregandoLista(false); }
  }

  async function entrar(email: string, senha: string) {
    setEnviando(true);
    try {
      const resposta = await fazerLogin({ email, senha });
      localStorage.setItem(CHAVE_TOKEN, resposta.access_token);
      localStorage.removeItem(CHAVE_GRUPO);
      setUsuario(await buscarUsuarioAtual(resposta.access_token));
      setTela("home");
    } catch (error) {
      localStorage.removeItem(CHAVE_TOKEN);
      if (error instanceof ApiError && error.status === 401) throw new Error("E-mail ou senha inválidos.");
      throw new Error(mensagemDeErro(error));
    } finally { setEnviando(false); }
  }

  async function cadastrar(dados: { nome: string; email: string; telefone: string; senha: string }) {
    setEnviando(true);
    try {
      await cadastrarUsuario({ ...dados, telefone: dados.telefone || undefined });
      setAviso("Conta criada com sucesso. Agora entre para continuar.");
      setTela("login");
    } catch (error) { throw new Error(mensagemDeErro(error)); }
    finally { setEnviando(false); }
  }

  async function cadastrarGrupo(dados: GrupoCriacaoDados) {
    const token = localStorage.getItem(CHAVE_TOKEN);
    if (!token) { encerrarSessao("Entre novamente para criar seu grupo."); return; }
    setEnviando(true);
    try {
      setGrupoCriado(await criarGrupo(dados, token));
      setTela("grupo-criado");
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) { encerrarSessao("Sua sessão terminou. Entre novamente para continuar."); return; }
      throw new Error(mensagemDeErroGrupo(error));
    } finally { setEnviando(false); }
  }

  async function abrirGrupo(grupoId: number) {
    const token = localStorage.getItem(CHAVE_TOKEN);
    if (!token) { encerrarSessao("Entre novamente para abrir o grupo."); return; }
    setCarregandoLista(true);
    setErroLista("");
    try {
      const grupo = await buscarGrupo(grupoId, token);
      setGrupoSelecionado(grupo);
      localStorage.setItem(CHAVE_GRUPO, String(grupo.id));
      setAvisoGrupo("");
      setTela("detalhes");
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) { encerrarSessao("Sua sessão terminou. Entre novamente para continuar."); return; }
      setErroLista(mensagemDeErroGrupo(error));
    } finally { setCarregandoLista(false); }
  }

  async function atualizarGrupoSelecionado(dados: GrupoAtualizacaoDados) {
    if (!grupoSelecionado) return;
    const token = localStorage.getItem(CHAVE_TOKEN);
    if (!token) { encerrarSessao("Entre novamente para editar o grupo."); return; }
    setEnviando(true);
    try {
      const grupo = await atualizarGrupo(grupoSelecionado.id, dados, token);
      setGrupoSelecionado({ ...grupo, papel: grupoSelecionado.papel });
      setAvisoGrupo("Grupo atualizado com sucesso.");
      setTela("detalhes");
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) { encerrarSessao("Sua sessão terminou. Entre novamente para continuar."); return; }
      if (error instanceof ApiError && error.status === 409) {
        try { setGrupoSelecionado(await buscarGrupo(grupoSelecionado.id, token)); } catch { /* mantém os últimos dados visíveis */ }
      }
      throw new Error(mensagemDeErroGrupo(error));
    } finally { setEnviando(false); }
  }

  async function cancelarGrupoSelecionado() {
    if (!grupoSelecionado) return;
    const token = localStorage.getItem(CHAVE_TOKEN);
    if (!token) { encerrarSessao("Entre novamente para cancelar o grupo."); return; }
    setEnviando(true);
    try {
      const grupo = await cancelarGrupo(grupoSelecionado.id, token);
      setGrupoSelecionado({ ...grupo, papel: grupoSelecionado.papel });
      setAvisoGrupo("Grupo cancelado. Ele continua disponível para consulta.");
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) { encerrarSessao("Sua sessão terminou. Entre novamente para continuar."); return; }
      if (error instanceof ApiError && error.status === 409) {
        try { setGrupoSelecionado(await buscarGrupo(grupoSelecionado.id, token)); } catch { /* mantém os últimos dados visíveis */ }
      }
      throw new Error(mensagemDeErroGrupo(error));
    } finally { setEnviando(false); }
  }

  function voltarParaHome() {
    localStorage.removeItem(CHAVE_GRUPO);
    setGrupoSelecionado(null);
    setGrupoCriado(null);
    setAvisoGrupo("");
    setTela("home");
  }

  function sair() { encerrarSessao("Você saiu da sua conta."); }

  if (carregandoSessao) return <main className="loading-screen">Carregando TooJunto...</main>;
  if (usuario && tela === "criar-grupo") return <CreateGroupPage nomeUsuario={usuario.nome} carregando={enviando} onVoltar={voltarParaHome} onCriar={cadastrarGrupo} />;
  if (usuario && tela === "grupo-criado" && grupoCriado) return <GroupCreatedPage nomeUsuario={usuario.nome} grupo={grupoCriado} onVoltar={voltarParaHome} onVerGrupo={() => abrirGrupo(grupoCriado.id)} />;
  if (usuario && tela === "editar-grupo" && grupoSelecionado) return <EditGroupPage nomeUsuario={usuario.nome} grupo={grupoSelecionado} carregando={enviando} onVoltar={() => setTela("detalhes")} onSalvar={atualizarGrupoSelecionado} />;
  if (usuario && tela === "detalhes" && grupoSelecionado) return <GroupDetailsPage nomeUsuario={usuario.nome} grupo={grupoSelecionado} aviso={avisoGrupo} carregando={enviando} onVoltar={voltarParaHome} onEditar={() => { setAvisoGrupo(""); setTela("editar-grupo"); }} onCancelar={cancelarGrupoSelecionado} />;
  if (usuario) return <HomePage usuario={usuario} grupos={grupos} carregando={carregandoLista} erro={erroLista || avisoGrupo} onAbrirGrupo={abrirGrupo} onCriarGrupo={() => setTela("criar-grupo")} onRecarregar={carregarGrupos} onSair={sair} />;
  return <AuthLayout>{tela === "login" ? <LoginPage aviso={aviso} carregando={enviando} onEntrar={entrar} onCadastrar={() => { setAviso(""); setTela("cadastro"); }} /> : <RegisterPage carregando={enviando} onVoltar={() => setTela("login")} onCadastrar={cadastrar} />}</AuthLayout>;
}
