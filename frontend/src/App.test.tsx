import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import type { GrupoComPapel } from "./types/groups";

const usuario = { id: 1, nome: "Ana Souza", email: "ana@example.com", telefone: null };

function resposta(corpo: unknown, status = 200): Response {
  return { ok: status >= 200 && status < 300, status, json: vi.fn().mockResolvedValue(corpo) } as unknown as Response;
}

function grupo(sobrescritas: Partial<GrupoComPapel> = {}): GrupoComPapel {
  return { id: 1, nome: "Grupo dos Amigos", gestor_id: 1, valor_cota: "200.00", valor_premio: "2000.00", quantidade_participantes: 10, quantidade_ciclos: 10, data_inicio: "2026-10-01", status: "RASCUNHO", created_at: "2026-09-16T12:00:00", papel: "GESTOR", ...sobrescritas };
}

const convite = {
  id: 7,
  group_id: 1,
  token: "token-seguro",
  invite_path: "/invites/token-seguro",
  created_at: "2026-09-20T12:00:00",
};

async function autenticar(grupos: GrupoComPapel[] = []) {
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
    const atualizado = { ...grupo(), nome: "Grupo Atualizado", valor_cota: "250.00", valor_premio: "2000.00", quantidade_participantes: 8, quantidade_ciclos: 8, data_inicio: "2026-11-01" };
    vi.mocked(fetch).mockResolvedValueOnce(resposta(atualizado));
    fireEvent.click(screen.getByRole("button", { name: "Salvar alterações" }));
    expect(await screen.findByText("Grupo atualizado com sucesso.")).toBeInTheDocument();
    const payload = { nome: "Grupo Atualizado", valor_cota: "250.00", quantidade_participantes: 8, data_inicio: "2026-11-01" };
    expect(fetch).toHaveBeenLastCalledWith("http://127.0.0.1:8000/groups/1", expect.objectContaining({ method: "PATCH", body: JSON.stringify(payload) }));
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
