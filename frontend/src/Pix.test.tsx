import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";

const usuario = { id: 1, nome: "Ana Souza", email: "ana@example.com", telefone: null };

function resposta(corpo: unknown, status = 200): Response {
  return { ok: status >= 200 && status < 300, status, json: vi.fn().mockResolvedValue(corpo) } as unknown as Response;
}

async function autenticar() {
  localStorage.setItem("toojunto_access_token", "token-valido");
  vi.mocked(fetch)
    .mockResolvedValueOnce(resposta(usuario))
    .mockResolvedValueOnce(resposta([]));
  render(<App />);
  await screen.findByRole("heading", { name: "Meus Grupos" });
  await waitFor(() => expect(fetch).toHaveBeenCalledWith(
    "http://127.0.0.1:8000/notifications/unread-count",
    expect.anything(),
  ));
}

async function abrirPix(chavePix: string | null = null) {
  vi.mocked(fetch).mockResolvedValueOnce(resposta({ chave_pix: chavePix }));
  fireEvent.click(screen.getByRole("button", { name: "Minha chave Pix" }));
  await screen.findByLabelText("Chave Pix");
}

describe("US-033 — Minha chave Pix", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("oferece acesso na área autenticada e preserva a navegação existente", async () => {
    await autenticar();
    await abrirPix();

    expect(screen.getByRole("heading", { name: "Minha chave Pix" })).toBeInTheDocument();
    expect(screen.getAllByRole("navigation", { name: "Navegação autenticada" })).toHaveLength(1);
    fireEvent.click(screen.getByRole("button", { name: "← Voltar para Meus Grupos" }));
    expect(await screen.findByRole("heading", { name: "Meus Grupos" })).toBeInTheDocument();
    expect(screen.getAllByRole("navigation", { name: "Navegação autenticada" })).toHaveLength(1);
  });

  it("mostra loading inicial e estado vazio quando o GET retorna null", async () => {
    await autenticar();
    let resolver!: (value: Response) => void;
    vi.mocked(fetch).mockImplementationOnce(() => new Promise((resolve) => { resolver = resolve; }));

    fireEvent.click(screen.getByRole("button", { name: "Minha chave Pix" }));

    expect(screen.getByRole("status", { name: "" })).toHaveTextContent("Carregando chave Pix...");
    resolver(resposta({ chave_pix: null }));
    expect(await screen.findByLabelText("Chave Pix")).toHaveValue("");
  });

  it("carrega a chave existente e consulta somente o próprio usuário", async () => {
    await autenticar();
    await abrirPix("ana@example.com");

    await waitFor(() => expect(screen.getByLabelText("Chave Pix")).toHaveValue("ana@example.com"));
    expect(fetch).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/auth/me/pix",
      expect.objectContaining({ headers: expect.objectContaining({ Authorization: "Bearer token-valido" }) }),
    );
    expect(vi.mocked(fetch).mock.calls.some(([url]) => String(url).includes("usuario_id"))).toBe(false);
  });

  it("cadastra, altera e remove a chave com feedback de sucesso", async () => {
    await autenticar();
    await abrirPix();
    const campo = screen.getByLabelText("Chave Pix");

    vi.mocked(fetch).mockResolvedValueOnce(resposta({ chave_pix: "ana@example.com" }));
    fireEvent.change(campo, { target: { value: "  ana@example.com  " } });
    fireEvent.click(screen.getByRole("button", { name: "Salvar" }));
    expect(await screen.findByText("Chave Pix cadastrada.")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole("button", { name: "Salvar" })).toBeEnabled());
    expect(fetch).toHaveBeenLastCalledWith(
      "http://127.0.0.1:8000/auth/me/pix",
      expect.objectContaining({ method: "PUT", body: JSON.stringify({ chave_pix: "ana@example.com" }) }),
    );

    vi.mocked(fetch).mockResolvedValueOnce(resposta({ chave_pix: "+5571999999999" }));
    fireEvent.change(campo, { target: { value: "+5571999999999" } });
    fireEvent.click(screen.getByRole("button", { name: "Salvar" }));
    expect(await screen.findByText("Chave Pix alterada.")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole("button", { name: "Salvar" })).toBeEnabled());

    vi.mocked(fetch).mockResolvedValueOnce(resposta({ chave_pix: null }));
    fireEvent.change(campo, { target: { value: "" } });
    fireEvent.click(screen.getByRole("button", { name: "Salvar" }));
    expect(await screen.findByText("Chave Pix removida.")).toBeInTheDocument();
    expect(fetch).toHaveBeenLastCalledWith(
      "http://127.0.0.1:8000/auth/me/pix",
      expect.objectContaining({ method: "PUT", body: JSON.stringify({ chave_pix: null }) }),
    );
  });

  it("trata erro ao consultar e permite tentar novamente", async () => {
    await autenticar();
    vi.mocked(fetch).mockResolvedValueOnce(resposta({ detail: "erro" }, 500));
    fireEvent.click(screen.getByRole("button", { name: "Minha chave Pix" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Não foi possível carregar sua chave Pix.");
    vi.mocked(fetch).mockResolvedValueOnce(resposta({ chave_pix: "recuperada" }));
    fireEvent.click(screen.getByRole("button", { name: "Tentar novamente" }));
    await waitFor(() => expect(screen.getByLabelText("Chave Pix")).toHaveValue("recuperada"));
  });

  it("trata erro ao salvar e encerra corretamente o estado salvando", async () => {
    await autenticar();
    await abrirPix();
    vi.mocked(fetch).mockResolvedValueOnce(resposta({ detail: "erro" }, 500));

    fireEvent.change(screen.getByLabelText("Chave Pix"), { target: { value: "nova-chave" } });
    fireEvent.click(screen.getByRole("button", { name: "Salvar" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Não foi possível salvar sua chave Pix.");
    await waitFor(() => expect(screen.getByRole("button", { name: "Salvar" })).toBeEnabled());
  });
});
