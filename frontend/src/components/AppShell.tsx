import type { ReactNode } from "react";
export function AppShell({ children, nome }: { children: ReactNode; nome: string }) {
  const iniciais = nome.split(" ").map((parte) => parte[0]).slice(0, 2).join("").toUpperCase();
  return <div className="app-shell"><header className="topbar"><div className="brand"><span className="brand-mark">T</span><span>TooJunto</span></div><div className="avatar" aria-label={`Perfil de ${nome}`}>{iniciais}</div></header><main className="main-content">{children}</main><nav className="bottom-nav" aria-label="Navegação principal"><span className="active"><b>⌂</b><small>Início</small></span><span><b>▣</b><small>Grupo</small></span><span><b>R$</b><small>Pagamentos</small></span><span><b>↻</b><small>Histórico</small></span></nav></div>;
}
