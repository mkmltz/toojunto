import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import type { NotificationItem } from "./types/notifications";

const usuario = { id: 1, nome: "Ana Souza", email: "ana@example.com", telefone: null };
const grupo = {
  id: 7, nome: "Grupo Família", gestor_id: 1, gestor_nome: "Ana Souza",
  valor_cota: "100.00", valor_premio: "300.00", quantidade_participantes: 3,
  quantidade_ciclos: 3, data_inicio: "2026-10-01", status: "ATIVO",
  created_at: "2026-09-20T12:00:00", papel: "GESTOR", vagas_disponiveis: 0,
  formacao: { quantidade_atual: 3, limite: 3, vagas_disponiveis: 0, participantes: [] },
  ordem_recebimento: [],
};
const naoLida: NotificationItem = {
  id: 10, tipo: "SORTEIO_REALIZADO", titulo: "Sorteio realizado",
  mensagem: "A ordem de recebimento foi definida.",
  referencia_contextual: "/groups/7", status: "NAO_LIDA",
  created_at: "2026-09-29T14:30:00", lida_em: null,
};
const lida: NotificationItem = {
  id: 9, tipo: "CICLO_INICIADO", titulo: "Novo ciclo iniciado",
  mensagem: "O ciclo 1 foi iniciado.", referencia_contextual: null,
  status: "LIDA", created_at: "2026-09-28T09:15:00",
  lida_em: "2026-09-28T10:00:00",
};

function resposta(corpo: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: vi.fn().mockResolvedValue(corpo),
  } as unknown as Response;
}

function mockApi({
  count = 0,
  notifications = [],
  listFailure = false,
  readFailure = false,
}: {
  count?: number;
  notifications?: NotificationItem[];
  listFailure?: boolean;
  readFailure?: boolean;
} = {}) {
  vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request, options?: RequestInit) => {
    const url = String(input);
    if (url.endsWith("/auth/me")) return resposta(usuario);
    if (url.endsWith("/notifications/unread-count")) return resposta({ count });
    if (url.endsWith("/notifications") && !options?.method) {
      return listFailure ? resposta({ detail: "Falha" }, 500) : resposta(notifications);
    }
    if (url.endsWith("/notifications/10/read")) {
      const target = notifications.find((item) => item.id === 10) ?? naoLida;
      return readFailure
        ? resposta({ detail: "Falha" }, 500)
        : resposta({ ...target, status: "LIDA", lida_em: "2026-09-29T15:00:00" });
    }
    if (url.endsWith("/groups/7")) return resposta(grupo);
    if (url.endsWith("/groups")) return resposta([]);
    throw new Error(`Requisição inesperada: ${url}`);
  }));
}

async function renderizarAutenticado() {
  localStorage.setItem("toojunto_access_token", "token-valido");
  render(<App />);
  await screen.findByRole("heading", { name: "Meus Grupos" });
}

describe("interface mínima de notificações", () => {
  beforeEach(() => {
    localStorage.clear();
    window.history.replaceState({}, "", "/");
  });
  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("exibe sino, badge e lista com destaque sem enviar usuario_id", async () => {
    mockApi({ count: 2, notifications: [naoLida, lida] });
    await renderizarAutenticado();

    const bell = await screen.findByRole("button", { name: "Notificações, 2 não lidas" });
    expect(bell).toHaveTextContent("2");
    fireEvent.click(bell);

    expect(await screen.findByRole("heading", { name: "Notificações" })).toBeInTheDocument();
    expect(screen.getAllByRole("navigation", { name: "Navegação autenticada" })).toHaveLength(1);
    expect(screen.getByText("A ordem de recebimento foi definida.")).toBeInTheDocument();
    expect(screen.getByText(/29\/09\/2026,? 14:30/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Não lida. Sorteio realizado" })).toHaveClass("notification-unread");
    expect(screen.getByRole("button", { name: "Novo ciclo iniciado" })).not.toHaveClass("notification-unread");
    for (const [url, options] of vi.mocked(fetch).mock.calls) {
      expect(String(url)).not.toContain("usuario_id");
      expect(String(options?.body ?? "")).not.toContain("usuario_id");
    }
  });

  it("oculta badge quando contador é zero e apresenta estado vazio", async () => {
    mockApi();
    await renderizarAutenticado();
    const bell = await screen.findByRole("button", { name: "Notificações" });
    expect(within(bell).queryByText("0")).not.toBeInTheDocument();

    fireEvent.click(bell);
    expect(await screen.findByText("Você ainda não tem notificações.")).toBeInTheDocument();
  });

  it("marca como lida, atualiza contador e navega para a referência", async () => {
    mockApi({ count: 1, notifications: [naoLida] });
    await renderizarAutenticado();
    fireEvent.click(await screen.findByRole("button", { name: "Notificações, 1 não lidas" }));
    fireEvent.click(await screen.findByRole("button", { name: "Não lida. Sorteio realizado" }));

    expect(await screen.findByRole("heading", { name: "Grupo Família" })).toBeInTheDocument();
    expect(screen.getAllByRole("navigation", { name: "Navegação autenticada" })).toHaveLength(1);
    expect(window.location.pathname).toBe("/groups/7");
    expect(screen.getByRole("button", { name: "Notificações" })).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/notifications/10/read",
      expect.objectContaining({
        method: "PATCH",
        headers: expect.objectContaining({ Authorization: "Bearer token-valido" }),
      }),
    );
  });

  it("permanece na central ao ler notificação sem referência", async () => {
    mockApi({ count: 1, notifications: [{ ...naoLida, referencia_contextual: null }] });
    await renderizarAutenticado();
    fireEvent.click(await screen.findByRole("button", { name: "Notificações, 1 não lidas" }));
    fireEvent.click(await screen.findByRole("button", { name: "Não lida. Sorteio realizado" }));

    await waitFor(() => expect(screen.getByRole("button", { name: "Sorteio realizado" })).not.toHaveClass("notification-unread"));
    expect(screen.getByRole("heading", { name: "Notificações" })).toBeInTheDocument();
  });

  it("mostra erros de lista e leitura sem fingir sucesso", async () => {
    mockApi({ count: 1, notifications: [naoLida], listFailure: true });
    await renderizarAutenticado();
    fireEvent.click(await screen.findByRole("button", { name: "Notificações, 1 não lidas" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Não foi possível carregar suas notificações.");
    expect(screen.getByRole("button", { name: "Tentar novamente" })).toBeInTheDocument();

    cleanup();
    mockApi({ count: 1, notifications: [naoLida], readFailure: true });
    await renderizarAutenticado();
    fireEvent.click(await screen.findByRole("button", { name: "Notificações, 1 não lidas" }));
    const item = await screen.findByRole("button", { name: "Não lida. Sorteio realizado" });
    fireEvent.click(item);
    expect(await screen.findByRole("alert")).toHaveTextContent("Não foi possível marcar a notificação como lida.");
    expect(item).toHaveClass("notification-unread");
    expect(window.location.pathname).toBe("/");
  });
});
