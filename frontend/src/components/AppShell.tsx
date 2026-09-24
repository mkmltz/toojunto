import type { ReactNode } from "react";
export function AppShell({ children, nome }: { children: ReactNode; nome: string }) {
  const iniciais = nome.split(" ").map((parte) => parte[0]).slice(0, 2).join("").toUpperCase();
  return <div className="app-shell"><header className="topbar"><img className="header-logo" src="/brand/toojunto-logo-header.png" alt="TooJunto" /><div className="avatar" aria-label={`Perfil de ${nome}`}>{iniciais}</div></header><main className="main-content">{children}</main></div>;
}
