import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import App from "./App";

const API_URL = "http://127.0.0.1:8000";
const EMAIL = "us045-integracao-ui@example.com";
const EMAIL_PARTICIPANTE = "us045-integracao-participante@example.com";
const SENHA = "senha-integracao";

const suiteIntegrada = import.meta.env.VITE_RUN_REAL_INTEGRATION === "1" ? describe : describe.skip;

function dataFutura(dias: number) {
  const data = new Date();
  data.setDate(data.getDate() + dias);
  return data.toISOString().slice(0, 10);
}

suiteIntegrada("TASK-045.1 — Frontend × Backend reais", () => {
  afterEach(() => {
    cleanup();
    localStorage.clear();
  });

  it("integra JWT, categorias, detalhes, navegação, cancelamento e Pix", async () => {
    const cadastro = await fetch(`${API_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        nome: "Integração US-045",
        email: EMAIL,
        telefone: "71999990000",
        senha: SENHA,
      }),
    });
    expect(cadastro.status).toBe(201);
    const gestor = await cadastro.json();

    render(<App />);
    fireEvent.change(screen.getByLabelText("E-mail"), { target: { value: EMAIL } });
    fireEvent.change(screen.getByLabelText("Senha"), { target: { value: SENHA } });
    fireEvent.click(screen.getByRole("button", { name: "Entrar" }));

    expect(await screen.findByRole("heading", { name: "Nenhum grupo em acompanhamento" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Criar novo grupo" }));
    fireEvent.change(screen.getByLabelText("Nome do grupo *"), { target: { value: "Grupo integração US-045" } });
    fireEvent.change(screen.getByLabelText("Valor por ciclo (R$) *"), { target: { value: "100" } });
    fireEvent.change(screen.getByLabelText("Quantidade de participantes *"), { target: { value: "2" } });
    fireEvent.change(screen.getByLabelText("Data de início *"), { target: { value: dataFutura(40) } });
    fireEvent.click(screen.getByRole("button", { name: "Criar grupo" }));

    expect(await screen.findByText("Grupo criado com sucesso.")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Voltar para Meus Grupos" }));
    expect(await screen.findByText("Grupo integração US-045")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Ver grupo" }));
    fireEvent.click(await screen.findByRole("button", { name: "← Voltar para Meus Grupos" }));
    expect(await screen.findByText("Grupo integração US-045")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Ver grupo" }));
    fireEvent.click(await screen.findByRole("button", { name: "Cancelar grupo" }));
    fireEvent.click(screen.getByRole("button", { name: "Sim, cancelar grupo" }));
    expect(await screen.findByRole("status")).toHaveTextContent("Grupo cancelado");

    fireEvent.click(screen.getByRole("button", { name: "Grupos" }));
    expect(await screen.findByRole("heading", { name: "Nenhum grupo em acompanhamento" })).toBeInTheDocument();
    expect(screen.queryByText("Grupo integração US-045")).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Histórico" }));
    const historico = await screen.findByRole("region", { name: "Histórico" });
    expect(within(historico).getByText("Grupo integração US-045")).toBeInTheDocument();
    expect(within(historico).getByText("Cancelado")).toBeInTheDocument();

    fireEvent.click(within(historico).getByRole("button", { name: "Ver grupo" }));
    fireEvent.click(await screen.findByRole("button", { name: "← Voltar para o Histórico" }));
    expect(await screen.findByRole("heading", { name: "Histórico" })).toBeInTheDocument();

    const cadastroParticipante = await fetch(`${API_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        nome: "Participante integração US-045",
        email: EMAIL_PARTICIPANTE,
        telefone: "71999990001",
        senha: SENHA,
      }),
    });
    expect(cadastroParticipante.status).toBe(201);
    const participante = await cadastroParticipante.json();
    const loginParticipante = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: EMAIL_PARTICIPANTE, senha: SENHA }),
    });
    const tokenParticipante = (await loginParticipante.json()).access_token;
    const tokenGestor = localStorage.getItem("toojunto_access_token")!;
    const autorizacao = (token: string) => ({
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    });
    const criarEncerrado = await fetch(`${API_URL}/groups`, {
      method: "POST",
      headers: autorizacao(tokenGestor),
      body: JSON.stringify({
        nome: "Grupo encerrado integração US-045",
        valor_cota: "100.00",
        quantidade_participantes: 2,
        quantidade_ciclos: 2,
        data_inicio: dataFutura(50),
      }),
    });
    expect(criarEncerrado.status).toBe(201);
    const grupoEncerrado = await criarEncerrado.json();
    const convite = await fetch(`${API_URL}/groups/${grupoEncerrado.id}/invite`, {
      method: "POST",
      headers: autorizacao(tokenGestor),
    });
    const tokenConvite = (await convite.json()).token;
    expect((await fetch(`${API_URL}/invites/${tokenConvite}/accept`, {
      method: "POST",
      headers: autorizacao(tokenParticipante),
    })).status).toBe(200);
    expect((await fetch(`${API_URL}/groups/${grupoEncerrado.id}/prepare-draw`, {
      method: "POST",
      headers: autorizacao(tokenGestor),
    })).status).toBe(200);
    expect((await fetch(`${API_URL}/groups/${grupoEncerrado.id}/draw`, {
      method: "POST",
      headers: autorizacao(tokenGestor),
    })).status).toBe(200);

    for (const ciclo of [1, 2]) {
      const caminho = `${API_URL}/groups/${grupoEncerrado.id}/cycles/${ciclo}/payments`;
      const obrigacoes = await (await fetch(caminho, { headers: autorizacao(tokenGestor) })).json();
      expect(obrigacoes).toHaveLength(1);
      const obrigacao = obrigacoes[0];
      const tokenPagador = obrigacao.pagador_usuario_id === gestor.id ? tokenGestor : tokenParticipante;
      const tokenRecebedor = obrigacao.pagador_usuario_id === gestor.id ? tokenParticipante : tokenGestor;
      const declaracao = await fetch(caminho, { method: "POST", headers: autorizacao(tokenPagador) });
      expect(declaracao.status).toBe(201);
      const pagamentoId = (await declaracao.json()).pagamento_id;
      expect((await fetch(`${caminho}/${pagamentoId}/confirm`, {
        method: "POST",
        headers: autorizacao(tokenRecebedor),
      })).status).toBe(200);
    }

    fireEvent.click(screen.getByRole("button", { name: "Grupos" }));
    await screen.findByRole("heading", { name: "Nenhum grupo em acompanhamento" });
    expect(screen.queryByText("Grupo encerrado integração US-045")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Histórico" }));
    const historicoAtualizado = await screen.findByRole("region", { name: "Histórico" });
    const cardEncerrado = within(historicoAtualizado).getByText("Grupo encerrado integração US-045").closest("article")!;
    expect(within(cardEncerrado).getByText("Grupo concluído")).toBeInTheDocument();
    fireEvent.click(within(cardEncerrado).getByRole("button", { name: "Ver grupo" }));
    expect(await screen.findByText("Todos os ciclos e pagamentos deste Grupo foram concluídos.")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "← Voltar para o Histórico" }));

    fireEvent.click(screen.getByRole("button", { name: "Minha chave Pix" }));
    const chavePix = await screen.findByLabelText("Chave Pix");
    fireEvent.change(chavePix, { target: { value: "us045@example.test" } });
    fireEvent.click(screen.getByRole("button", { name: "Salvar" }));
    expect(await screen.findByRole("status")).toHaveTextContent("Chave Pix cadastrada.");

    fireEvent.click(screen.getByRole("button", { name: "Sair" }));
    expect(await screen.findByRole("heading", { name: "Bem-vindo ao TooJunto" })).toBeInTheDocument();
    await waitFor(() => expect(localStorage.getItem("toojunto_access_token")).toBeNull());
  });
});
