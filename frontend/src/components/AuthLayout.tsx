import type { ReactNode } from "react";
export function AuthLayout({ children }: { children: ReactNode }) { return <main className="auth-main"><section className="auth-content">{children}</section></main>; }
