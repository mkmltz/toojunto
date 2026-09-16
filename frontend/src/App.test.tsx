import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";

function resposta(corpo: unknown, status = 200): Response { return { ok: status >= 200 && status < 300, status, json: vi.fn().mockResolvedValue(corpo) } as unknown as Response; }
function preencherLogin() { fireEvent.change(screen.getByLabelText("E-mail"), { target: { value: "ana@example.com" } }); fireEvent.change(screen.getByLabelText("Senha"), { target: { value: "senha-segura" } }); fireEvent.click(screen.getByRole("button", { name: "Entrar" })); }
function preencherCadastro() { fireEvent.change(screen.getByLabelText("Nome completo *"), { target: { value: "Ana Souza" } }); fireEvent.change(screen.getByLabelText("E-mail *"), { target: { value: "ana@example.com" } }); fireEvent.change(screen.getByLabelText("Senha *"), { target: { value: "senha-segura" } }); fireEvent.click(screen.getByRole("button", { name: "Criar conta" })); }
async function autenticarPelaSessao() {
  localStorage.setItem("toojunto_access_token", "token-valido");
  vi.mocked(fetch).mockResolvedValueOnce(resposta({ id: 1, nome: "Ana Souza", email: "ana@example.com", telefone: null }));
  const app = render(<App />);
  await screen.findByRole("heading", { name: "Olá, Ana Souza!" });
  return app;
}

describe("autenticação", () => {
  afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
  beforeEach(() => { localStorage.clear(); vi.stubGlobal("fetch", vi.fn()); });
  it("renderiza a tela de login", async () => { render(<App />); expect(await screen.findByRole("heading", { name: "Bem-vindo ao TooJunto" })).toBeInTheDocument(); expect(screen.getByLabelText("E-mail")).toBeInTheDocument(); expect(screen.getByLabelText("Senha")).toBeInTheDocument(); });
  it("faz login e exibe a área autenticada", async () => { vi.mocked(fetch).mockResolvedValueOnce(resposta({ access_token: "token-valido", token_type: "bearer" })).mockResolvedValueOnce(resposta({ id: 1, nome: "Ana Souza", email: "ana@example.com", telefone: null })); render(<App />); preencherLogin(); expect(await screen.findByRole("heading", { name: "Olá, Ana Souza!" })).toBeInTheDocument(); expect(localStorage.getItem("toojunto_access_token")).toBe("token-valido"); });
  it("mostra erro para login inválido", async () => { vi.mocked(fetch).mockResolvedValueOnce(resposta({ detail: "E-mail ou senha inválidos." }, 401)); render(<App />); preencherLogin(); expect(await screen.findByRole("alert")).toHaveTextContent("E-mail ou senha inválidos."); expect(localStorage.getItem("toojunto_access_token")).toBeNull(); });
  it("cadastra e retorna para o login com confirmação", async () => { vi.mocked(fetch).mockResolvedValueOnce(resposta({ id: 1, nome: "Ana Souza", email: "ana@example.com", telefone: null }, 201)); render(<App />); fireEvent.click(await screen.findByRole("button", { name: "Criar minha conta" })); preencherCadastro(); expect(await screen.findByRole("status")).toHaveTextContent("Conta criada com sucesso"); expect(screen.getByRole("heading", { name: "Bem-vindo ao TooJunto" })).toBeInTheDocument(); });
  it("mostra erro de cadastro", async () => { vi.mocked(fetch).mockResolvedValueOnce(resposta({ detail: "E-mail já cadastrado." }, 409)); render(<App />); fireEvent.click(await screen.findByRole("button", { name: "Criar minha conta" })); preencherCadastro(); expect(await screen.findByRole("alert")).toHaveTextContent("E-mail já cadastrado."); });
  it("restaura acesso autenticado consultando /auth/me", async () => { localStorage.setItem("toojunto_access_token", "token-valido"); vi.mocked(fetch).mockResolvedValueOnce(resposta({ id: 1, nome: "Ana Souza", email: "ana@example.com", telefone: null })); render(<App />); expect(await screen.findByRole("heading", { name: "Olá, Ana Souza!" })).toBeInTheDocument(); });
  it("mantém login sem autenticação", async () => { render(<App />); expect(await screen.findByRole("heading", { name: "Bem-vindo ao TooJunto" })).toBeInTheDocument(); expect(screen.queryByText("Conta autenticada")).not.toBeInTheDocument(); });
  it("exibe a ação de sair para usuário autenticado", async () => { await autenticarPelaSessao(); expect(screen.getByRole("button", { name: "Sair" })).toBeInTheDocument(); });
  it("remove o token ao sair", async () => { await autenticarPelaSessao(); fireEvent.click(screen.getByRole("button", { name: "Sair" })); expect(localStorage.getItem("toojunto_access_token")).toBeNull(); });
  it("deixa de exibir dados da sessão ao sair", async () => { await autenticarPelaSessao(); fireEvent.click(screen.getByRole("button", { name: "Sair" })); expect(screen.queryByRole("heading", { name: "Olá, Ana Souza!" })).not.toBeInTheDocument(); expect(screen.queryByText("ana@example.com")).not.toBeInTheDocument(); });
  it("retorna para o login com feedback ao sair", async () => { await autenticarPelaSessao(); fireEvent.click(screen.getByRole("button", { name: "Sair" })); expect(await screen.findByRole("heading", { name: "Bem-vindo ao TooJunto" })).toBeInTheDocument(); expect(screen.getByRole("status")).toHaveTextContent("Você saiu da sua conta."); });
  it("exige novo login ao tentar acessar a área autenticada após sair", async () => {
    const { unmount } = await autenticarPelaSessao();
    fireEvent.click(screen.getByRole("button", { name: "Sair" }));
    unmount();

    render(<App />);

    expect(await screen.findByRole("heading", { name: "Bem-vindo ao TooJunto" })).toBeInTheDocument();
    expect(screen.queryByText("Conta autenticada")).not.toBeInTheDocument();
    expect(fetch).toHaveBeenCalledTimes(1);
  });
});
