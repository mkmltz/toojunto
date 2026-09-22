import { act, cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import type { GrupoDetalhe, GrupoLista } from "./types/groups";

const usuario = { id: 1, nome: "Ana Souza", email: "ana@example.com", telefone: null };

function resposta(corpo: unknown, status = 200): Response {
  return { ok: status >= 200 && status < 300, status, json: vi.fn().mockResolvedValue(corpo) } as unknown as Response;
}

function grupo(sobrescritas: Partial<GrupoDetalhe & GrupoLista> = {}): GrupoDetalhe & GrupoLista {
  return { id: 1, nome: "Grupo dos Amigos", gestor_id: 1, valor_cota: "200.00", valor_premio: "2000.00", quantidade_participantes: 10, quantidade_ciclos: 10, data_inicio: "2026-10-01", status: "RASCUNHO", created_at: "2026-09-16T12:00:00", papel: "GESTOR", vagas_disponiveis: 8, formacao: { quantidade_atual: 2, limite: 10, vagas_disponiveis: 8, participantes: [{ nome: "Ana Souza", papel: "GESTOR" }, { nome: "Bruno Lima", papel: "PARTICIPANTE" }] }, ...sobrescritas };
}

const convite = {
  id: 7,
  group_id: 1,
  token: "token-seguro",
  invite_path: "/invites/token-seguro",
  created_at: "2026-09-20T12:00:00",
};

async function autenticar(grupos: GrupoLista[] = []) {
  localStorage.setItem("toojunto_access_token", "token-valido");
  vi.mocked(fetch).mockResolvedValueOnce(resposta(usuario)).mockResolvedValueOnce(resposta(grupos));
  const app = render(<App />);
  await screen.findByRole("heading", { name: "Meus Grupos" });
  await waitFor(() => expect(fetch).toHaveBeenCalledWith("http://127.0.0.1:8000/groups", expect.anything()));
  return app;
}

async function abrirDetalhes(dadosGrupo = grupo()) {
  await autenticar([dadosGrupo]);
  vi.mocked(fetch).mockResolvedValueOnce(resposta(dadosGrupo));
  fireEvent.click(screen.getByRole("button", { name: "Ver grupo" }));
  await screen.findByRole("heading", { name: dadosGrupo.nome });
}

function preencherFormulario(nome = "Grupo Atualizado", valor = "250.00", participantes = "8") {
  fireEvent.change(screen.getByLabelText("Nome do grupo *"), { target: { value: nome } });
  fireEvent.change(screen.getByLabelText("Valor por ciclo (R$) *"), { target: { value: valor } });
  fireEvent.change(screen.getByLabelText("Quantidade de participantes *"), { target: { value: participantes } });
  fireEvent.change(screen.getByLabelText("Data de início *"), { target: { value: "2026-11-01" } });
}

describe("US-003.1 e US-004", () => {
  afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
  beforeEach(() => { localStorage.clear(); vi.stubGlobal("fetch", vi.fn()); });

  it("carrega Meus Grupos com dados simples de gestor e participante", async () => {
    await autenticar([grupo(), grupo({ id: 2, nome: "Grupo da Família", papel: "PARTICIPANTE", gestor_id: 9 })]);
    expect(screen.getByText("Grupo dos Amigos")).toBeInTheDocument();
    expect(screen.getByText("Grupo da Família")).toBeInTheDocument();
    expect(screen.getByText("Gestor")).toBeInTheDocument();
    expect(screen.getByText("Participante")).toBeInTheDocument();
    expect(screen.getAllByText("R$ 200,00")).toHaveLength(2);
    expect(screen.getAllByText("R$ 2.000,00")).toHaveLength(2);
  });

  it("mostra estado vazio", async () => {
    await autenticar();
    expect(await screen.findByRole("heading", { name: "Nenhum grupo ainda" })).toBeInTheDocument();
  });

  it("abre detalhes por GET e persiste o id selecionado", async () => {
    await abrirDetalhes();
    expect(fetch).toHaveBeenLastCalledWith("http://127.0.0.1:8000/groups/1", expect.objectContaining({ headers: expect.objectContaining({ Authorization: "Bearer token-valido" }) }));
    expect(localStorage.getItem("toojunto_selected_group_id")).toBe("1");
    expect(screen.getByText("Seu papel: Gestor")).toBeInTheDocument();
    expect(screen.getByText("01/10/2026")).toBeInTheDocument();
  });

  it("restaura detalhes após F5 usando GET", async () => {
    localStorage.setItem("toojunto_access_token", "token-valido");
    localStorage.setItem("toojunto_selected_group_id", "1");
    vi.mocked(fetch).mockResolvedValueOnce(resposta(usuario)).mockResolvedValueOnce(resposta(grupo()));
    render(<App />);
    expect(await screen.findByRole("heading", { name: "Grupo dos Amigos" })).toBeInTheDocument();
    expect(fetch).toHaveBeenLastCalledWith("http://127.0.0.1:8000/groups/1", expect.anything());
  });

  it("participante visualiza sem ações de gestão", async () => {
    await abrirDetalhes(grupo({ papel: "PARTICIPANTE", gestor_id: 9 }));
    expect(screen.getByText("Seu papel: Participante")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Editar grupo" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Cancelar grupo" })).not.toBeInTheDocument();
  });

  it("grupo cancelado permanece na lista e não apresenta ações", async () => {
    const cancelado = grupo({ status: "CANCELADO" });
    await abrirDetalhes(cancelado);
    expect(screen.getByText("CANCELADO")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Editar grupo" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Cancelar grupo" })).not.toBeInTheDocument();
  });

  it("edita, recalcula visualmente e envia somente campos permitidos", async () => {
    await abrirDetalhes();
    fireEvent.click(screen.getByRole("button", { name: "Editar grupo" }));
    preencherFormulario();
    expect(screen.getByLabelText("Quantidade de ciclos")).toHaveValue(8);
    expect(screen.getByText("R$ 2.000,00")).toBeInTheDocument();
    const atualizado = { ...grupo(), nome: "Grupo Atualizado", valor_cota: "250.00", valor_premio: "2000.00", quantidade_participantes: 8, quantidade_ciclos: 8, data_inicio: "2026-11-01", formacao: { ...grupo().formacao, limite: 8, vagas_disponiveis: 6 } };
    vi.mocked(fetch).mockResolvedValueOnce(resposta(atualizado)).mockResolvedValueOnce(resposta(atualizado));
    fireEvent.click(screen.getByRole("button", { name: "Salvar alterações" }));
    expect(await screen.findByText("Grupo atualizado com sucesso.")).toBeInTheDocument();
    expect(screen.getByText("2 de 8 pessoas")).toBeInTheDocument();
    const payload = { nome: "Grupo Atualizado", valor_cota: "250.00", quantidade_participantes: 8, data_inicio: "2026-11-01" };
    expect(fetch).toHaveBeenCalledWith("http://127.0.0.1:8000/groups/1", expect.objectContaining({ method: "PATCH", body: JSON.stringify(payload) }));
    expect(payload).not.toHaveProperty("quantidade_ciclos");
    expect(payload).not.toHaveProperty("valor_premio");
    expect(payload).not.toHaveProperty("gestor_id");
    expect(payload).not.toHaveProperty("status");
    expect(payload).not.toHaveProperty("papel");
  });

  it("solicita confirmação antes de cancelar e permite voltar", async () => {
    await abrirDetalhes();
    fireEvent.click(screen.getByRole("button", { name: "Cancelar grupo" }));
    expect(screen.getByRole("dialog")).toHaveTextContent("não será excluído");
    expect(fetch).toHaveBeenCalledTimes(3);
    fireEvent.click(screen.getByRole("button", { name: "Voltar" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("cancela, mantém detalhes e remove ações", async () => {
    await abrirDetalhes();
    fireEvent.click(screen.getByRole("button", { name: "Cancelar grupo" }));
    vi.mocked(fetch).mockResolvedValueOnce(resposta({ ...grupo(), status: "CANCELADO" }));
    fireEvent.click(screen.getByRole("button", { name: "Sim, cancelar grupo" }));
    expect(await screen.findByRole("status")).toHaveTextContent("Grupo cancelado");
    expect(screen.getByText("CANCELADO")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Grupo dos Amigos" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Editar grupo" })).not.toBeInTheDocument();
    expect(fetch).toHaveBeenLastCalledWith("http://127.0.0.1:8000/groups/1/cancel", expect.objectContaining({ method: "POST" }));
  });

  it("trata 404 ao abrir detalhes", async () => {
    await autenticar([grupo()]);
    vi.mocked(fetch).mockResolvedValueOnce(resposta({ detail: "Grupo não encontrado." }, 404));
    fireEvent.click(screen.getByRole("button", { name: "Ver grupo" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Grupo não encontrado ou sem acesso.");
  });

  it.each([
    [403, "Você não tem permissão"],
    [422, "Confira os dados"],
    [500, "Falha interna"],
  ])("trata erro %s na edição", async (status, mensagem) => {
    await abrirDetalhes();
    fireEvent.click(screen.getByRole("button", { name: "Editar grupo" }));
    vi.mocked(fetch).mockResolvedValueOnce(resposta({ detail: status === 500 ? "Falha interna" : "erro" }, status));
    fireEvent.click(screen.getByRole("button", { name: "Salvar alterações" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(mensagem);
  });

  it("trata 409 e recarrega o grupo", async () => {
    await abrirDetalhes();
    fireEvent.click(screen.getByRole("button", { name: "Editar grupo" }));
    vi.mocked(fetch).mockResolvedValueOnce(resposta({ detail: "conflito" }, 409)).mockResolvedValueOnce(resposta(grupo({ status: "CANCELADO" })));
    fireEvent.click(screen.getByRole("button", { name: "Salvar alterações" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("não pode mais ser alterado");
  });

  it("encerra sessão quando a listagem retorna 401", async () => {
    localStorage.setItem("toojunto_access_token", "token-valido");
    vi.mocked(fetch).mockResolvedValueOnce(resposta(usuario)).mockResolvedValueOnce(resposta({ detail: "Credenciais inválidas." }, 401));
    render(<App />);
    expect(await screen.findByRole("heading", { name: "Bem-vindo ao TooJunto" })).toBeInTheDocument();
    expect(localStorage.getItem("toojunto_access_token")).toBeNull();
  });

  it("trata falha de rede na listagem e permite tentar novamente", async () => {
    localStorage.setItem("toojunto_access_token", "token-valido");
    vi.mocked(fetch).mockResolvedValueOnce(resposta(usuario)).mockRejectedValueOnce(new TypeError("Failed to fetch"));
    render(<App />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Não foi possível carregar seus grupos.");
    expect(screen.getByRole("button", { name: "Tentar novamente" })).toBeInTheDocument();
  });

  it("preserva criação com ciclos calculados e sem valor do prêmio", async () => {
    await autenticar();
    fireEvent.click(screen.getByRole("button", { name: "+ Criar novo grupo" }));
    preencherFormulario("Grupo Novo", "200.00", "5");
    vi.mocked(fetch).mockResolvedValueOnce(resposta(grupo({ nome: "Grupo Novo", quantidade_participantes: 5, quantidade_ciclos: 5 }), 201));
    fireEvent.click(screen.getByRole("button", { name: "Criar grupo" }));
    expect(await screen.findByText("Grupo criado com sucesso.")).toBeInTheDocument();
    const payload = { nome: "Grupo Novo", valor_cota: "200.00", quantidade_participantes: 5, quantidade_ciclos: 5, data_inicio: "2026-11-01" };
    const chamadas = vi.mocked(fetch).mock.calls;
    const ultimaChamada = chamadas[chamadas.length - 1];
    expect(ultimaChamada[0]).toBe("http://127.0.0.1:8000/groups");
    expect(ultimaChamada[1]).toEqual(expect.objectContaining({ method: "POST" }));
    expect(JSON.parse(String(ultimaChamada[1]?.body))).toEqual(payload);
    expect(payload).not.toHaveProperty("valor_premio");
  });

  it("preserva login e logout", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(resposta({ access_token: "token-valido", token_type: "bearer" })).mockResolvedValueOnce(resposta(usuario)).mockResolvedValueOnce(resposta([]));
    render(<App />);
    fireEvent.change(screen.getByLabelText("E-mail"), { target: { value: "ana@example.com" } });
    fireEvent.change(screen.getByLabelText("Senha"), { target: { value: "senha-segura" } });
    fireEvent.click(screen.getByRole("button", { name: "Entrar" }));
    await screen.findByRole("heading", { name: "Meus Grupos" });
    fireEvent.click(screen.getByRole("button", { name: "Sair" }));
    expect(await screen.findByRole("heading", { name: "Bem-vindo ao TooJunto" })).toBeInTheDocument();
    expect(localStorage.getItem("toojunto_access_token")).toBeNull();
  });

  it("usa sempre a terminologia Grupo", async () => {
    await autenticar();
    expect(document.body.textContent).not.toMatch(/caixinha/i);
  });
});

describe("US-007", () => {
  afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
  beforeEach(() => { localStorage.clear(); vi.stubGlobal("fetch", vi.fn()); });

  it("renderiza a formação e os papéis usando os dados do Backend", async () => {
    await abrirDetalhes();

    const formacao = screen.getByRole("region", { name: "Participantes" });
    expect(within(formacao).getByText("2 de 10 pessoas")).toBeInTheDocument();
    expect(within(formacao).getByText("Ana Souza")).toBeInTheDocument();
    expect(within(formacao).getByText("Gestor")).toBeInTheDocument();
    expect(within(formacao).getByText("Bruno Lima")).toBeInTheDocument();
    expect(within(formacao).getByText("Participante")).toBeInTheDocument();
    expect(within(formacao).getByText("Faltam 8 pessoas para completar o Grupo.")).toBeInTheDocument();
  });

  it("trata uma vaga restante no singular", async () => {
    await abrirDetalhes(grupo({
      formacao: {
        quantidade_atual: 9,
        limite: 10,
        vagas_disponiveis: 1,
        participantes: [{ nome: "Ana Souza", papel: "GESTOR" }],
      },
    }));

    expect(screen.getByText("Falta 1 pessoa para completar o Grupo.")).toBeInTheDocument();
  });

  it("informa quando o Grupo está completo", async () => {
    await abrirDetalhes(grupo({
      formacao: {
        quantidade_atual: 10,
        limite: 10,
        vagas_disponiveis: 0,
        participantes: [{ nome: "Ana Souza", papel: "GESTOR" }],
      },
    }));

    expect(screen.getByText("Grupo completo.")).toBeInTheDocument();
  });

  it("mantém as ações do Gestor", async () => {
    await abrirDetalhes();

    expect(screen.getByRole("button", { name: "Convidar pessoas" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Editar grupo" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Cancelar grupo" })).toBeInTheDocument();
  });

  it("não oferece ações de Gestor ao Participante", async () => {
    await abrirDetalhes(grupo({ papel: "PARTICIPANTE", gestor_id: 9 }));

    expect(screen.getByRole("region", { name: "Participantes" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Convidar pessoas" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Editar grupo" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Cancelar grupo" })).not.toBeInTheDocument();
  });
});

describe("US-005", () => {
  const escreverClipboard = vi.fn().mockResolvedValue(undefined);

  afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
  beforeEach(() => {
    localStorage.clear();
    vi.stubGlobal("fetch", vi.fn());
    escreverClipboard.mockClear();
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: { writeText: escreverClipboard },
    });
    Object.defineProperty(navigator, "share", {
      configurable: true,
      value: undefined,
    });
  });

  it("mostra Convidar pessoas apenas para Gestor em RASCUNHO", async () => {
    await abrirDetalhes();
    expect(screen.getByRole("button", { name: "Convidar pessoas" })).toBeInTheDocument();

    cleanup();
    localStorage.clear();
    await abrirDetalhes(grupo({ papel: "PARTICIPANTE", gestor_id: 9 }));
    expect(screen.queryByRole("button", { name: "Convidar pessoas" })).not.toBeInTheDocument();

    cleanup();
    localStorage.clear();
    await abrirDetalhes(grupo({ status: "FORMANDO" }));
    expect(screen.queryByRole("button", { name: "Convidar pessoas" })).not.toBeInTheDocument();
  });

  it("solicita o convite por POST e monta o link com a origem atual", async () => {
    await abrirDetalhes();
    vi.mocked(fetch).mockResolvedValueOnce(resposta(convite));

    fireEvent.click(screen.getByRole("button", { name: "Convidar pessoas" }));

    const link = `${window.location.origin}/invites/token-seguro`;
    expect(await screen.findByLabelText("Link do convite")).toHaveTextContent(link);
    expect(fetch).toHaveBeenLastCalledWith(
      "http://127.0.0.1:8000/groups/1/invite",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({ Authorization: "Bearer token-valido" }),
      }),
    );
  });

  it("copia o link completo e apresenta feedback", async () => {
    await abrirDetalhes();
    vi.mocked(fetch).mockResolvedValueOnce(resposta(convite));
    fireEvent.click(screen.getByRole("button", { name: "Convidar pessoas" }));
    await screen.findByRole("button", { name: "Copiar link" });

    fireEvent.click(screen.getByRole("button", { name: "Copiar link" }));

    await waitFor(() => expect(escreverClipboard).toHaveBeenCalledWith(`${window.location.origin}/invites/token-seguro`));
    expect(screen.getByRole("status")).toHaveTextContent("Link copiado com sucesso.");
  });

  it("usa navigator.share com nome do Grupo e link", async () => {
    const compartilhar = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "share", { configurable: true, value: compartilhar });
    await abrirDetalhes();
    vi.mocked(fetch).mockResolvedValueOnce(resposta(convite));
    fireEvent.click(screen.getByRole("button", { name: "Convidar pessoas" }));
    await screen.findByRole("button", { name: "Compartilhar convite" });

    fireEvent.click(screen.getByRole("button", { name: "Compartilhar convite" }));

    await waitFor(() => expect(compartilhar).toHaveBeenCalledWith(expect.objectContaining({
      text: expect.stringContaining("Grupo dos Amigos"),
      url: `${window.location.origin}/invites/token-seguro`,
    })));
    expect(screen.getByRole("status")).toHaveTextContent("Convite compartilhado.");
  });

  it("copia o link como fallback quando navigator.share não existe", async () => {
    await abrirDetalhes();
    vi.mocked(fetch).mockResolvedValueOnce(resposta(convite));
    fireEvent.click(screen.getByRole("button", { name: "Convidar pessoas" }));
    await screen.findByRole("button", { name: "Compartilhar convite" });

    fireEvent.click(screen.getByRole("button", { name: "Compartilhar convite" }));

    await waitFor(() => expect(escreverClipboard).toHaveBeenCalledOnce());
    expect(screen.getByRole("status")).toHaveTextContent("Link copiado com sucesso.");
  });

  it.each([
    [404, "Este Grupo não está disponível."],
    [409, "Este Grupo não permite mais convites."],
    [500, "Não foi possível obter o convite. Tente novamente."],
  ])("trata erro %s ao obter convite", async (status, mensagem) => {
    await abrirDetalhes();
    vi.mocked(fetch).mockResolvedValueOnce(resposta({ detail: "erro" }, status));
    fireEvent.click(screen.getByRole("button", { name: "Convidar pessoas" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(mensagem);
    expect(screen.getByRole("button", { name: "Convidar pessoas" })).toBeInTheDocument();
  });

  it("encerra a sessão quando o convite retorna 401", async () => {
    await abrirDetalhes();
    vi.mocked(fetch).mockResolvedValueOnce(resposta({ detail: "Credenciais inválidas." }, 401));
    fireEvent.click(screen.getByRole("button", { name: "Convidar pessoas" }));
    expect(await screen.findByRole("heading", { name: "Bem-vindo ao TooJunto" })).toBeInTheDocument();
    expect(localStorage.getItem("toojunto_access_token")).toBeNull();
  });
});

describe("US-008 — sinalização em Meus Grupos", () => {
  afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
  beforeEach(() => { localStorage.clear(); vi.stubGlobal("fetch", vi.fn()); });

  it.each(["GESTOR", "PARTICIPANTE"] as const)("mostra todas as situações para %s", async (papel) => {
    const grupos = [
      grupo({ id: 1, nome: "Formando", papel, vagas_disponiveis: 3 }),
      grupo({ id: 2, nome: "Completo", papel, vagas_disponiveis: 0 }),
      grupo({ id: 3, nome: "Preparado", papel, status: "SORTEIO", vagas_disponiveis: 0 }),
      grupo({ id: 4, nome: "Cancelado teste", papel, status: "CANCELADO", vagas_disponiveis: 2 }),
    ];
    await autenticar(grupos);
    const lista = screen.getByRole("region", { name: "Meus Grupos" });
    const badges = Array.from(lista.querySelectorAll(".group-situation"));
    expect(badges.map((badge) => badge.textContent)).toEqual(["Em formação", "Grupo completo", "Pronto para sorteio", "Cancelado"]);
    expect(badges.map((badge) => badge.className)).toEqual([
      "badge group-situation forming", "badge group-situation complete",
      "badge group-situation ready", "badge group-situation danger",
    ]);
    expect(within(lista).queryByText("RASCUNHO")).not.toBeInTheDocument();
    expect(within(lista).queryByRole("button", { name: "Realizar sorteio" })).not.toBeInTheDocument();
  });
});

describe("US-008", () => {
  const completo = grupo({ formacao: { ...grupo().formacao, quantidade_atual: 10, vagas_disponiveis: 0 } });

  afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
  beforeEach(() => { localStorage.clear(); vi.stubGlobal("fetch", vi.fn()); });

  it("mostra a preparação somente ao gestor de grupo completo", async () => {
    await abrirDetalhes();
    expect(screen.queryByRole("button", { name: "Preparar sorteio" })).not.toBeInTheDocument();
    cleanup(); localStorage.clear();
    await abrirDetalhes(grupo({ ...completo, papel: "PARTICIPANTE" }));
    expect(screen.queryByRole("button", { name: "Preparar sorteio" })).not.toBeInTheDocument();
    cleanup(); localStorage.clear();
    await abrirDetalhes(completo);
    expect(screen.getByRole("button", { name: "Preparar sorteio" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Convidar pessoas" })).not.toBeInTheDocument();
  });

  it("confirma a regra do gestor antes de chamar a API e permite cancelar", async () => {
    await abrirDetalhes(completo);
    const chamadas = vi.mocked(fetch).mock.calls.length;
    fireEvent.click(screen.getByRole("button", { name: "Preparar sorteio" }));
    const dialogo = screen.getByRole("dialog", { name: "Preparar sorteio?" });
    expect(dialogo).toHaveTextContent("Você ficará com a 1ª posição");
    expect(dialogo).toHaveTextContent("não será possível adicionar novas pessoas");
    expect(fetch).toHaveBeenCalledTimes(chamadas);
    fireEvent.click(within(dialogo).getByRole("button", { name: "Cancelar" }));
    expect(fetch).toHaveBeenCalledTimes(chamadas);
  });

  it("prepara por POST, recarrega os dados e mostra o estado para participantes", async () => {
    await abrirDetalhes(completo);
    const preparado = grupo({ ...completo, status: "SORTEIO" });
    vi.mocked(fetch).mockResolvedValueOnce(resposta(preparado)).mockResolvedValueOnce(resposta(preparado));
    fireEvent.click(screen.getByRole("button", { name: "Preparar sorteio" }));
    fireEvent.click(within(screen.getByRole("dialog", { name: "Preparar sorteio?" })).getByRole("button", { name: "Preparar sorteio" }));
    expect(await screen.findByText("Grupo pronto para o sorteio.")).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith("http://127.0.0.1:8000/groups/1/prepare-draw", expect.objectContaining({ method: "POST", headers: expect.objectContaining({ Authorization: "Bearer token-valido" }) }));
    expect(fetch).toHaveBeenLastCalledWith("http://127.0.0.1:8000/groups/1", expect.anything());
    expect(screen.getByText("Formação encerrada. O grupo está pronto para o sorteio.")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Preparar sorteio" })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Realizar sorteio" })).toBeInTheDocument();
    cleanup(); localStorage.clear();
    await abrirDetalhes(grupo({ ...preparado, papel: "PARTICIPANTE" }));
    expect(screen.getByText("Formação encerrada. O grupo está pronto para o sorteio.")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Preparar sorteio" })).not.toBeInTheDocument();
  });

  it("atualiza o grupo e explica quando a preparação é recusada", async () => {
    await abrirDetalhes(completo);
    const incompleto = grupo();
    vi.mocked(fetch).mockResolvedValueOnce(resposta({ detail: "Formação incompleta." }, 409)).mockResolvedValueOnce(resposta(incompleto));
    fireEvent.click(screen.getByRole("button", { name: "Preparar sorteio" }));
    fireEvent.click(within(screen.getByRole("dialog", { name: "Preparar sorteio?" })).getByRole("button", { name: "Preparar sorteio" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("O grupo mudou e não pôde ser preparado.");
    expect(screen.getByText("Faltam 8 pessoas para completar o Grupo.")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Preparar sorteio" })).not.toBeInTheDocument();
  });
});

describe("US-009", () => {
  const preparado = grupo({ status: "SORTEIO", vagas_disponiveis: 0 });
  const sorteado = grupo({
    status: "ATIVO",
    vagas_disponiveis: 0,
    ordem_recebimento: [
      { posicao: 1, nome: "Ana Souza", papel: "GESTOR", data_prevista: "2026-10-10" },
      { posicao: 2, nome: "Bruno Lima", papel: "PARTICIPANTE", data_prevista: "2026-11-09" },
    ],
  });

  afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
  beforeEach(() => { localStorage.clear(); vi.stubGlobal("fetch", vi.fn()); });

  it("pede confirmação e só então chama POST e recarrega o resultado", async () => {
    await abrirDetalhes(preparado);
    const chamadas = vi.mocked(fetch).mock.calls.length;
    fireEvent.click(screen.getByRole("button", { name: "Realizar sorteio" }));
    const dialogo = screen.getByRole("dialog", { name: "Realizar sorteio?" });
    expect(dialogo).toHaveTextContent("Você ficará com a 1ª posição");
    expect(dialogo).toHaveTextContent("As demais pessoas serão sorteadas");
    expect(dialogo).toHaveTextContent("não poderá ser alterado");
    expect(fetch).toHaveBeenCalledTimes(chamadas);
    fireEvent.click(within(dialogo).getByRole("button", { name: "Cancelar" }));
    expect(fetch).toHaveBeenCalledTimes(chamadas);

    vi.mocked(fetch).mockResolvedValueOnce(resposta(sorteado)).mockResolvedValueOnce(resposta(sorteado));
    fireEvent.click(screen.getByRole("button", { name: "Realizar sorteio" }));
    fireEvent.click(within(screen.getByRole("dialog", { name: "Realizar sorteio?" })).getByRole("button", { name: "Realizar sorteio" }));
    expect(await screen.findByRole("heading", { name: "Ordem de recebimento" })).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith("http://127.0.0.1:8000/groups/1/draw", expect.objectContaining({ method: "POST", headers: expect.objectContaining({ Authorization: "Bearer token-valido" }) }));
    expect(fetch).toHaveBeenLastCalledWith("http://127.0.0.1:8000/groups/1", expect.anything());
    const ordem = screen.getByRole("region", { name: "Ordem de recebimento" });
    expect(within(ordem).getAllByRole("listitem").map((item) => item.textContent)).toEqual([
      "1ºAna Souza — GestorRecebe em 10/10/2026",
      "2ºBruno LimaRecebe em 09/11/2026",
    ]);
    expect(screen.getByText("Sorteio realizado")).toHaveClass("drawn");
    expect(screen.queryByRole("button", { name: "Realizar sorteio" })).not.toBeInTheDocument();
  });

  it("mostra a mesma ordem após recarregar e oculta a ação do participante", async () => {
    localStorage.setItem("toojunto_access_token", "token-valido");
    localStorage.setItem("toojunto_selected_group_id", "1");
    vi.mocked(fetch).mockResolvedValueOnce(resposta(usuario)).mockResolvedValueOnce(resposta(grupo({ ...sorteado, papel: "PARTICIPANTE" })));
    render(<App />);
    const ordem = await screen.findByRole("region", { name: "Ordem de recebimento" });
    expect(within(ordem).getAllByRole("listitem")).toHaveLength(2);
    expect(within(ordem).getByText("Recebe em 09/11/2026")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Realizar sorteio" })).not.toBeInTheDocument();
    expect(fetch).not.toHaveBeenCalledWith("http://127.0.0.1:8000/groups/1/draw", expect.anything());
  });

  it("atualiza o resultado após conflito sem mostrar novo botão", async () => {
    await abrirDetalhes(preparado);
    vi.mocked(fetch).mockResolvedValueOnce(resposta({ detail: "O sorteio já ocorreu." }, 409)).mockResolvedValueOnce(resposta(sorteado));
    fireEvent.click(screen.getByRole("button", { name: "Realizar sorteio" }));
    fireEvent.click(within(screen.getByRole("dialog", { name: "Realizar sorteio?" })).getByRole("button", { name: "Realizar sorteio" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("O sorteio não pôde ser realizado.");
    expect(screen.getByRole("heading", { name: "Ordem de recebimento" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Realizar sorteio" })).not.toBeInTheDocument();
  });

  it("mostra Sorteio realizado na lista para ambos os papéis", async () => {
    await autenticar([sorteado, grupo({ ...sorteado, id: 2, papel: "PARTICIPANTE" })]);
    const badges = screen.getAllByText("Sorteio realizado");
    expect(badges).toHaveLength(2);
    badges.forEach((badge) => expect(badge).toHaveClass("drawn"));
    expect(badges.every((badge) => !badge.classList.contains("complete"))).toBe(true);
    expect(screen.queryByText("ATIVO")).not.toBeInTheDocument();
  });
});

describe("US-006", () => {
  const conviteRecebido = {
    group_name: "Grupo Convidado",
    quota_value: "150.00",
    participant_limit: 5,
    available_slots: 2,
    start_date: "2026-10-01",
  };

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
    window.history.replaceState({}, "", "/");
  });

  beforeEach(() => {
    localStorage.clear();
    window.history.replaceState({}, "", "/invites/token-recebido");
    vi.stubGlobal("fetch", vi.fn());
  });

  it("abre a URL diretamente e consulta os dados públicos do convite", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(resposta(conviteRecebido));
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Você foi convidado para participar de um Grupo" })).toBeInTheDocument();
    expect(screen.getByText("Grupo Convidado")).toBeInTheDocument();
    expect(screen.getByText("R$ 150,00")).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("01/10/2026")).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/invites/token-recebido",
      expect.anything(),
    );
  });

  it("apresenta mensagem uniforme quando o convite está indisponível", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(resposta({ detail: "indisponível" }, 404));
    render(<App />);
    expect(await screen.findByText("Este convite não está mais disponível.")).toBeInTheDocument();
  });

  it("permite tentar novamente após falha ao consultar", async () => {
    vi.mocked(fetch)
      .mockRejectedValueOnce(new TypeError("Failed to fetch"))
      .mockResolvedValueOnce(resposta(conviteRecebido));
    render(<App />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Não foi possível abrir o convite");

    fireEvent.click(screen.getByRole("button", { name: "Tentar novamente" }));

    expect(await screen.findByText("Grupo Convidado")).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledTimes(2);
  });

  it("preserva a URL no Login e retorna ao convite sem aceitar automaticamente", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(resposta(conviteRecebido));
    render(<App />);
    await screen.findByText("Grupo Convidado");
    fireEvent.click(screen.getByRole("button", { name: "Entrar no Grupo" }));
    expect(await screen.findByRole("heading", { name: "Bem-vindo ao TooJunto" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/invites/token-recebido");

    vi.mocked(fetch)
      .mockResolvedValueOnce(resposta({ access_token: "token-valido", token_type: "bearer" }))
      .mockResolvedValueOnce(resposta(usuario));
    fireEvent.change(screen.getByLabelText("E-mail"), { target: { value: "ana@example.com" } });
    fireEvent.change(screen.getByLabelText("Senha"), { target: { value: "senha-segura" } });
    fireEvent.click(screen.getByRole("button", { name: "Entrar" }));

    expect(await screen.findByText("Grupo Convidado")).toBeInTheDocument();
    expect(window.location.pathname).toBe("/invites/token-recebido");
    expect(fetch).toHaveBeenCalledTimes(3);
  });

  it("reutiliza o cadastro e preserva a URL até o Login", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(resposta(conviteRecebido));
    render(<App />);
    await screen.findByText("Grupo Convidado");
    fireEvent.click(screen.getByRole("button", { name: "Criar minha conta" }));

    fireEvent.change(screen.getByLabelText("Nome completo *"), { target: { value: "Nova Pessoa" } });
    fireEvent.change(screen.getByLabelText("E-mail *"), { target: { value: "nova@example.com" } });
    fireEvent.change(screen.getByLabelText("Senha *"), { target: { value: "senha-segura" } });
    vi.mocked(fetch).mockResolvedValueOnce(resposta({ id: 9, nome: "Nova Pessoa", email: "nova@example.com", telefone: null }, 201));
    fireEvent.click(screen.getByRole("button", { name: "Criar conta" }));

    expect(await screen.findByRole("heading", { name: "Bem-vindo ao TooJunto" })).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent("Conta criada com sucesso");
    expect(window.location.pathname).toBe("/invites/token-recebido");
  });

  it("aceita com JWT e permite abrir o Grupo removendo a URL do convite", async () => {
    localStorage.setItem("toojunto_access_token", "token-valido");
    vi.mocked(fetch)
      .mockResolvedValueOnce(resposta(usuario))
      .mockResolvedValueOnce(resposta(conviteRecebido));
    render(<App />);
    await screen.findByText("Grupo Convidado");
    vi.mocked(fetch).mockResolvedValueOnce(resposta({ group_id: 1, participant_id: 8, status: "ATIVO" }));

    fireEvent.click(screen.getByRole("button", { name: "Entrar no Grupo" }));

    expect(await screen.findByRole("heading", { name: "Você entrou no Grupo" })).toBeInTheDocument();
    expect(fetch).toHaveBeenLastCalledWith(
      "http://127.0.0.1:8000/invites/token-recebido/accept",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({ Authorization: "Bearer token-valido" }),
      }),
    );

    vi.mocked(fetch).mockResolvedValueOnce(resposta(grupo({ papel: "PARTICIPANTE" })));
    fireEvent.click(screen.getByRole("button", { name: "Ver Grupo" }));
    expect(await screen.findByRole("heading", { name: "Grupo dos Amigos" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/");
  });

  it("retorna ao Login preservando o convite quando o aceite recebe 401", async () => {
    localStorage.setItem("toojunto_access_token", "token-valido");
    vi.mocked(fetch)
      .mockResolvedValueOnce(resposta(usuario))
      .mockResolvedValueOnce(resposta(conviteRecebido));
    render(<App />);
    await screen.findByText("Grupo Convidado");
    vi.mocked(fetch).mockResolvedValueOnce(resposta({ detail: "Credenciais inválidas." }, 401));

    fireEvent.click(screen.getByRole("button", { name: "Entrar no Grupo" }));

    expect(await screen.findByRole("heading", { name: "Bem-vindo ao TooJunto" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/invites/token-recebido");
    expect(localStorage.getItem("toojunto_access_token")).toBeNull();
  });

  it("mostra a mensagem do Backend quando o aceite recebe 409", async () => {
    localStorage.setItem("toojunto_access_token", "token-valido");
    vi.mocked(fetch)
      .mockResolvedValueOnce(resposta(usuario))
      .mockResolvedValueOnce(resposta(conviteRecebido));
    render(<App />);
    await screen.findByText("Grupo Convidado");
    vi.mocked(fetch).mockResolvedValueOnce(resposta({ detail: "Este Grupo não possui vagas disponíveis." }, 409));

    fireEvent.click(screen.getByRole("button", { name: "Entrar no Grupo" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Este Grupo não possui vagas disponíveis.");
    expect(screen.getByRole("button", { name: "Entrar no Grupo" })).toBeEnabled();
  });

  it("torna o convite indisponível quando o aceite recebe 404", async () => {
    localStorage.setItem("toojunto_access_token", "token-valido");
    vi.mocked(fetch)
      .mockResolvedValueOnce(resposta(usuario))
      .mockResolvedValueOnce(resposta(conviteRecebido));
    render(<App />);
    await screen.findByText("Grupo Convidado");
    vi.mocked(fetch).mockResolvedValueOnce(resposta({ detail: "Convite não encontrado." }, 404));

    fireEvent.click(screen.getByRole("button", { name: "Entrar no Grupo" }));

    expect(await screen.findByText("Este convite não está mais disponível.")).toBeInTheDocument();
  });

  it("permite repetir o aceite após erro genérico", async () => {
    localStorage.setItem("toojunto_access_token", "token-valido");
    vi.mocked(fetch)
      .mockResolvedValueOnce(resposta(usuario))
      .mockResolvedValueOnce(resposta(conviteRecebido));
    render(<App />);
    await screen.findByText("Grupo Convidado");
    vi.mocked(fetch).mockResolvedValueOnce(resposta({ detail: "Falha interna" }, 500));

    fireEvent.click(screen.getByRole("button", { name: "Entrar no Grupo" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Não foi possível entrar no Grupo. Tente novamente.");
    expect(screen.getByRole("button", { name: "Entrar no Grupo" })).toBeEnabled();
  });

  it("Agora não sai do fluxo sem chamar o Backend novamente", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(resposta(conviteRecebido));
    render(<App />);
    await screen.findByText("Grupo Convidado");

    fireEvent.click(screen.getByRole("button", { name: "Agora não" }));

    expect(await screen.findByRole("heading", { name: "Bem-vindo ao TooJunto" })).toBeInTheDocument();
    expect(window.location.pathname).toBe("/");
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it("ignora resposta tardia depois que a URL do convite é abandonada", async () => {
    let resolver!: (response: Response) => void;
    vi.mocked(fetch).mockReturnValueOnce(new Promise((resolve) => { resolver = resolve; }));
    render(<App />);
    window.history.replaceState({}, "", "/");
    fireEvent(window, new PopStateEvent("popstate"));
    expect(await screen.findByRole("heading", { name: "Bem-vindo ao TooJunto" })).toBeInTheDocument();

    await act(async () => { resolver(resposta(conviteRecebido)); });

    expect(screen.queryByText("Grupo Convidado")).not.toBeInTheDocument();
  });

  it("ignora aceite antigo quando a URL muda para outro convite", async () => {
    localStorage.setItem("toojunto_access_token", "token-valido");
    vi.mocked(fetch)
      .mockResolvedValueOnce(resposta(usuario))
      .mockResolvedValueOnce(resposta(conviteRecebido));
    render(<App />);
    await screen.findByText("Grupo Convidado");

    let resolverAceite!: (response: Response) => void;
    vi.mocked(fetch).mockReturnValueOnce(new Promise((resolve) => {
      resolverAceite = resolve;
    }));
    fireEvent.click(screen.getByRole("button", { name: "Entrar no Grupo" }));

    vi.mocked(fetch).mockResolvedValueOnce(resposta({
      ...conviteRecebido,
      group_name: "Outro Grupo",
    }));
    window.history.pushState({}, "", "/invites/outro-token");
    fireEvent(window, new PopStateEvent("popstate"));
    expect(await screen.findByText("Outro Grupo")).toBeInTheDocument();

    await act(async () => {
      resolverAceite(resposta({
        group_id: 1,
        participant_id: 8,
        status: "ATIVO",
      }));
    });

    expect(screen.queryByRole("heading", { name: "Você entrou no Grupo" })).not.toBeInTheDocument();
    expect(screen.getByText("Outro Grupo")).toBeInTheDocument();
  });
});
