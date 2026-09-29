import { createContext, useContext, type ReactNode } from "react";

interface NotificationNavigation {
  unreadCount: number;
  onOpenNotifications: () => void;
}

const NotificationNavigationContext = createContext<NotificationNavigation | null>(null);

export function NotificationNavigationProvider({
  children,
  value,
}: {
  children: ReactNode;
  value: NotificationNavigation;
}) {
  return <NotificationNavigationContext.Provider value={value}>
    {children}
  </NotificationNavigationContext.Provider>;
}

export function AppShell({ children, nome }: { children: ReactNode; nome: string }) {
  const notifications = useContext(NotificationNavigationContext);
  const iniciais = nome.split(" ").map((parte) => parte[0]).slice(0, 2).join("").toUpperCase();
  return <div className="app-shell"><header className="topbar"><img className="header-logo" src="/brand/toojunto-logo-header.png" alt="TooJunto" /><div className="topbar-actions">{notifications && <button className="notification-button" type="button" onClick={notifications.onOpenNotifications} aria-label={notifications.unreadCount > 0 ? `Notificações, ${notifications.unreadCount} não lidas` : "Notificações"}><svg aria-hidden="true" viewBox="0 0 24 24"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4" /></svg>{notifications.unreadCount > 0 && <span className="notification-count">{notifications.unreadCount}</span>}</button>}<div className="avatar" aria-label={`Perfil de ${nome}`}>{iniciais}</div></div></header><main className="main-content">{children}</main></div>;
}
