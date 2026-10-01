import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AuthenticatedBottomNav } from "./components/AuthenticatedBottomNav";

describe("US-035.1 — navegação autenticada global", () => {
  afterEach(cleanup);

  it("exibe uma única barra com ícones e preserva as três ações", () => {
    const onCriarGrupo = vi.fn();
    const onAbrirChavePix = vi.fn();
    const onSair = vi.fn();
    render(<AuthenticatedBottomNav onCriarGrupo={onCriarGrupo} onAbrirChavePix={onAbrirChavePix} onSair={onSair} />);
    const barra = screen.getByRole("navigation", { name: "Navegação autenticada" });
    const botoes = within(barra).getAllByRole("button");

    expect(botoes).toHaveLength(3);
    expect(barra.querySelectorAll("svg")).toHaveLength(3);
    expect(screen.getAllByRole("button", { name: "Criar novo grupo" })).toHaveLength(1);
    expect(screen.getAllByRole("button", { name: "Minha chave Pix" })).toHaveLength(1);
    expect(screen.getAllByRole("button", { name: "Sair" })).toHaveLength(1);

    fireEvent.click(screen.getByRole("button", { name: "Criar novo grupo" }));
    fireEvent.click(screen.getByRole("button", { name: "Minha chave Pix" }));
    fireEvent.click(screen.getByRole("button", { name: "Sair" }));
    expect(onCriarGrupo).toHaveBeenCalledOnce();
    expect(onAbrirChavePix).toHaveBeenCalledOnce();
    expect(onSair).toHaveBeenCalledOnce();
  });
});
