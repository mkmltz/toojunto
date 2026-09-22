import { useEffect, useRef, useState } from "react";
import { AuthLayout } from "./components/AuthLayout";
import { CreateGroupPage } from "./pages/CreateGroupPage";
import { EditGroupPage } from "./pages/EditGroupPage";
import { GroupCreatedPage } from "./pages/GroupCreatedPage";
import { GroupDetailsPage } from "./pages/GroupDetailsPage";
import { HomePage } from "./pages/HomePage";
import { InvitePage } from "./pages/InvitePage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { ApiError, buscarUsuarioAtual, cadastrarUsuario, fazerLogin } from "./services/auth";
import { atualizarGrupo, buscarGrupo, cancelarGrupo, criarGrupo, gerarOuObterConvite, listarGrupos, prepararSorteio, realizarSorteio } from "./services/groups";
import { aceitarConvite, consultarConvite } from "./services/invites";
import type { Usuario } from "./types/auth";
import type { ConviteGrupo, Grupo, GrupoAtualizacaoDados, GrupoCriacaoDados, GrupoDetalhe, GrupoLista } from "./types/groups";
import type { AceiteConvite, ConvitePublico } from "./types/invites";

const CHAVE_TOKEN = "toojunto_access_token";
const CHAVE_GRUPO = "toojunto_selected_group_id";
type Tela = "login" | "cadastro" | "home" | "criar-grupo" | "grupo-criado" | "detalhes" | "editar-grupo" | "convite";

function extrairTokenConvite(pathname: string): string | null {
  const correspondencia = pathname.match(/^\/invites\/([^/]+)\/?$/);
  if (!correspondencia) return null;
  try { return decodeURIComponent(correspondencia[1]); }
  catch { return null; }
}

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
  const [conviteToken, setConviteToken] = useState<string | null>(() => extrairTokenConvite(window.location.pathname));
  const conviteTokenAtual = useRef(conviteToken);
  const [tela, setTela] = useState<Tela>(() => conviteToken ? "convite" : "login");
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [grupos, setGrupos] = useState<GrupoLista[]>([]);
  const [grupoSelecionado, setGrupoSelecionado] = useState<GrupoDetalhe | null>(null);
  const [grupoCriado, setGrupoCriado] = useState<Grupo | null>(null);
  const [carregandoSessao, setCarregandoSessao] = useState(true);
  const [carregandoLista, setCarregandoLista] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [aviso, setAviso] = useState("");
  const [avisoGrupo, setAvisoGrupo] = useState("");
  const [erroLista, setErroLista] = useState("");
  const [convitePublico, setConvitePublico] = useState<ConvitePublico | null>(null);
  const [aceiteConvite, setAceiteConvite] = useState<AceiteConvite | null>(null);
  const [carregandoConvite, setCarregandoConvite] = useState(Boolean(conviteToken));
  const [aceitandoConvite, setAceitandoConvite] = useState(false);
  const [erroConvite, setErroConvite] = useState("");
  const [conviteIndisponivel, setConviteIndisponivel] = useState(false);
  const [tentativaConvite, setTentativaConvite] = useState(0);

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
        if (conviteToken) {
          setUsuario(usuarioAtual);
          setTela("convite");
          return;
        }
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
        if (error instanceof ApiError && error.status === 401) {
          if (conviteToken) {
            localStorage.removeItem(CHAVE_TOKEN);
            localStorage.removeItem(CHAVE_GRUPO);
            setUsuario(null);
            setTela("convite");
          } else {
            encerrarSessao("Sua sessão terminou. Entre novamente para continuar.");
          }
        }
      } finally {
        setCarregandoSessao(false);
      }
    }
    restaurar();
  }, []);

  useEffect(() => {
    if (!conviteToken) return;
    let ativo = true;
    setCarregandoConvite(true);
    setErroConvite("");
    setConviteIndisponivel(false);
    consultarConvite(conviteToken)
      .then((convite) => { if (ativo) setConvitePublico(convite); })
      .catch((error) => {
        if (!ativo) return;
        setConvitePublico(null);
        if (error instanceof ApiError && error.status === 404) {
          setConviteIndisponivel(true);
        } else {
          setErroConvite("Não foi possível abrir o convite. Tente novamente.");
        }
      })
      .finally(() => { if (ativo) setCarregandoConvite(false); });
    return () => { ativo = false; };
  }, [conviteToken, tentativaConvite]);

  useEffect(() => {
    function sincronizarComUrl() {
      const token = extrairTokenConvite(window.location.pathname);
      conviteTokenAtual.current = token;
      setConviteToken(token);
      setConvitePublico(null);
      setAceiteConvite(null);
      setErroConvite("");
      setConviteIndisponivel(false);
      setAceitandoConvite(false);
      setTela(token ? "convite" : usuario ? "home" : "login");
    }
    window.addEventListener("popstate", sincronizarComUrl);
    return () => window.removeEventListener("popstate", sincronizarComUrl);
  }, [usuario]);

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
      setTela(conviteToken ? "convite" : "home");
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
      await atualizarGrupo(grupoSelecionado.id, dados, token);
      setGrupoSelecionado(await buscarGrupo(grupoSelecionado.id, token));
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
      setGrupoSelecionado({ ...grupo, papel: grupoSelecionado.papel, formacao: grupoSelecionado.formacao });
      setAvisoGrupo("Grupo cancelado. Ele continua disponível para consulta.");
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) { encerrarSessao("Sua sessão terminou. Entre novamente para continuar."); return; }
      if (error instanceof ApiError && error.status === 409) {
        try { setGrupoSelecionado(await buscarGrupo(grupoSelecionado.id, token)); } catch { /* mantém os últimos dados visíveis */ }
      }
      throw new Error(mensagemDeErroGrupo(error));
    } finally { setEnviando(false); }
  }

  async function prepararSorteioSelecionado() {
    if (!grupoSelecionado) return;
    const token = localStorage.getItem(CHAVE_TOKEN);
    if (!token) { encerrarSessao("Entre novamente para preparar o sorteio."); return; }
    setEnviando(true);
    let preparado = false;
    try {
      await prepararSorteio(grupoSelecionado.id, token);
      preparado = true;
      await realizarSorteio(grupoSelecionado.id, token);
      setGrupoSelecionado(await buscarGrupo(grupoSelecionado.id, token));
      setAvisoGrupo("Sorteio realizado. A ordem de recebimento está disponível.");
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) { encerrarSessao("Sua sessão terminou. Entre novamente para continuar."); return; }
      if (preparado || (error instanceof ApiError && error.status === 409)) {
        try { setGrupoSelecionado(await buscarGrupo(grupoSelecionado.id, token)); } catch { /* mantém os últimos dados visíveis */ }
        throw new Error(preparado ? "O grupo foi preparado, mas o sorteio não pôde ser realizado. Tente novamente." : "O sorteio não pôde ser realizado. Confira a situação atual do grupo.");
      }
      throw new Error(mensagemDeErroGrupo(error));
    } finally { setEnviando(false); }
  }

  async function realizarSorteioSelecionado() {
    if (!grupoSelecionado) return;
    const token = localStorage.getItem(CHAVE_TOKEN);
    if (!token) { encerrarSessao("Entre novamente para realizar o sorteio."); return; }
    setEnviando(true);
    try {
      await realizarSorteio(grupoSelecionado.id, token);
      setGrupoSelecionado(await buscarGrupo(grupoSelecionado.id, token));
      setAvisoGrupo("Sorteio realizado. A ordem de recebimento está disponível.");
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) { encerrarSessao("Sua sessão terminou. Entre novamente para continuar."); return; }
      if (error instanceof ApiError && error.status === 409) {
        try { setGrupoSelecionado(await buscarGrupo(grupoSelecionado.id, token)); } catch { /* mantém os últimos dados visíveis */ }
        throw new Error("O sorteio não pôde ser realizado. Confira a situação atual do grupo.");
      }
      throw new Error(mensagemDeErroGrupo(error));
    } finally { setEnviando(false); }
  }

  async function obterConviteSelecionado(): Promise<ConviteGrupo> {
    if (!grupoSelecionado) throw new Error("O Grupo não está disponível.");
    const token = localStorage.getItem(CHAVE_TOKEN);
    if (!token) {
      encerrarSessao("Entre novamente para convidar pessoas.");
      throw new Error("Sua sessão terminou.");
    }
    try {
      return await gerarOuObterConvite(grupoSelecionado.id, token);
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        encerrarSessao("Sua sessão terminou. Entre novamente para continuar.");
        throw error;
      }
      if (error instanceof ApiError && error.status === 404) {
        throw new Error("Este Grupo não está disponível.");
      }
      if (error instanceof ApiError && error.status === 409) {
        throw new Error("Este Grupo não permite mais convites.");
      }
      throw new Error("Não foi possível obter o convite. Tente novamente.");
    }
  }

  async function entrarNoGrupoPeloConvite() {
    if (!conviteToken) return;
    if (!usuario) {
      setAviso("");
      setTela("login");
      return;
    }
    const jwt = localStorage.getItem(CHAVE_TOKEN);
    if (!jwt) {
      setUsuario(null);
      setTela("login");
      return;
    }
    setAceitandoConvite(true);
    setErroConvite("");
    const tokenSolicitado = conviteToken;
    try {
      const aceite = await aceitarConvite(tokenSolicitado, jwt);
      if (conviteTokenAtual.current !== tokenSolicitado) return;
      setAceiteConvite(aceite);
    } catch (error) {
      if (conviteTokenAtual.current !== tokenSolicitado) return;
      if (error instanceof ApiError && error.status === 401) {
        localStorage.removeItem(CHAVE_TOKEN);
        localStorage.removeItem(CHAVE_GRUPO);
        setUsuario(null);
        setTela("login");
        setAviso("Sua sessão terminou. Entre novamente para continuar.");
      } else if (error instanceof ApiError && error.status === 404) {
        setConvitePublico(null);
        setConviteIndisponivel(true);
      } else if (error instanceof ApiError && error.status === 409) {
        setErroConvite(error.message);
      } else {
        setErroConvite("Não foi possível entrar no Grupo. Tente novamente.");
      }
    } finally {
      if (conviteTokenAtual.current === tokenSolicitado) {
        setAceitandoConvite(false);
      }
    }
  }

  function abandonarConvite() {
    window.history.replaceState({}, "", "/");
    conviteTokenAtual.current = null;
    setConviteToken(null);
    setConvitePublico(null);
    setAceiteConvite(null);
    setErroConvite("");
    setConviteIndisponivel(false);
    setTela(usuario ? "home" : "login");
  }

  async function verGrupoAceito(grupoId: number) {
    window.history.replaceState({}, "", "/");
    conviteTokenAtual.current = null;
    setConviteToken(null);
    setConvitePublico(null);
    setAceiteConvite(null);
    await abrirGrupo(grupoId);
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
  if (tela === "convite" && conviteToken) return <InvitePage convite={convitePublico} aceite={aceiteConvite} carregando={carregandoConvite} aceitando={aceitandoConvite} erro={erroConvite} autenticado={Boolean(usuario)} indisponivel={conviteIndisponivel} onEntrar={entrarNoGrupoPeloConvite} onAgoraNao={abandonarConvite} onCriarConta={() => setTela("cadastro")} onTentarNovamente={() => setTentativaConvite((tentativa) => tentativa + 1)} onVerGrupo={verGrupoAceito} />;
  if (usuario && tela === "criar-grupo") return <CreateGroupPage nomeUsuario={usuario.nome} carregando={enviando} onVoltar={voltarParaHome} onCriar={cadastrarGrupo} />;
  if (usuario && tela === "grupo-criado" && grupoCriado) return <GroupCreatedPage nomeUsuario={usuario.nome} grupo={grupoCriado} onVoltar={voltarParaHome} onVerGrupo={() => abrirGrupo(grupoCriado.id)} />;
  if (usuario && tela === "editar-grupo" && grupoSelecionado) return <EditGroupPage nomeUsuario={usuario.nome} grupo={grupoSelecionado} carregando={enviando} onVoltar={() => setTela("detalhes")} onSalvar={atualizarGrupoSelecionado} />;
  if (usuario && tela === "detalhes" && grupoSelecionado) return <GroupDetailsPage nomeUsuario={usuario.nome} usuarioId={usuario.id} grupo={grupoSelecionado} aviso={avisoGrupo} carregando={enviando} onVoltar={voltarParaHome} onEditar={() => { setAvisoGrupo(""); setTela("editar-grupo"); }} onCancelar={cancelarGrupoSelecionado} onObterConvite={obterConviteSelecionado} onPrepararSorteio={prepararSorteioSelecionado} onRealizarSorteio={realizarSorteioSelecionado} />;
  if (usuario) return <HomePage usuario={usuario} grupos={grupos} carregando={carregandoLista} erro={erroLista || avisoGrupo} onAbrirGrupo={abrirGrupo} onCriarGrupo={() => setTela("criar-grupo")} onRecarregar={carregarGrupos} onSair={sair} />;
  return <AuthLayout>{tela === "login" ? <LoginPage aviso={aviso} carregando={enviando} onEntrar={entrar} onCadastrar={() => { setAviso(""); setTela("cadastro"); }} onVoltarConvite={conviteToken ? () => setTela("convite") : undefined} /> : <RegisterPage carregando={enviando} onVoltar={() => setTela("login")} onCadastrar={cadastrar} />}</AuthLayout>;
}
