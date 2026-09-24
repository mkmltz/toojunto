import type { ReactNode } from "react";
export function AuthLayout({ children }: { children: ReactNode }) { return <main className="auth-main"><section className="auth-content"><img className="auth-logo" src="/brand/toojunto-logo-header.png" alt="TooJunto" />{children}</section></main>; }
