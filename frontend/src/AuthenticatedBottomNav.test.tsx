import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AuthenticatedBottomNav } from "./components/AuthenticatedBottomNav";

describe("US-044 — navegação autenticada global", () => {
  afterEach(cleanup);

  it("exibe quatro opções com ícones, estado ativo e sem logout duplicado", () => {
    const onAbrirGrupos = vi.fn();
    const onCriarGrupo = vi.fn();
    const onAbrirHistorico = vi.fn();
    const onAbrirChavePix = vi.fn();
    render(<AuthenticatedBottomNav ativo="grupos" onAbrirGrupos={onAbrirGrupos} onCriarGrupo={onCriarGrupo} onAbrirHistorico={onAbrirHistorico} onAbrirChavePix={onAbrirChavePix} />);
    const barra = screen.getByRole("navigation", { name: "Navegação autenticada" });
    const botoes = within(barra).getAllByRole("button");

    expect(botoes).toHaveLength(4);
    expect(barra.querySelectorAll("svg")).toHaveLength(4);
    expect(screen.getByRole("button", { name: "Grupos" })).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("button", { name: "Histórico" })).not.toHaveAttribute("aria-current");
    expect(screen.getAllByRole("button", { name: "Criar novo grupo" })).toHaveLength(1);
    expect(screen.getAllByRole("button", { name: "Minha chave Pix" })).toHaveLength(1);
    expect(within(barra).queryByRole("button", { name: "Sair" })).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Grupos" }));
    fireEvent.click(screen.getByRole("button", { name: "Criar novo grupo" }));
    fireEvent.click(screen.getByRole("button", { name: "Histórico" }));
    fireEvent.click(screen.getByRole("button", { name: "Minha chave Pix" }));
    expect(onAbrirGrupos).toHaveBeenCalledOnce();
    expect(onCriarGrupo).toHaveBeenCalledOnce();
    expect(onAbrirHistorico).toHaveBeenCalledOnce();
    expect(onAbrirChavePix).toHaveBeenCalledOnce();
  });
});
