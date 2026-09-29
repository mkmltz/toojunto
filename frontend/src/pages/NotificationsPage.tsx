import { AppShell } from "../components/AppShell";
import type { NotificationItem } from "../types/notifications";

interface NotificationsPageProps {
  nomeUsuario: string;
  notificacoes: NotificationItem[];
  carregando: boolean;
  lendoId: number | null;
  erro: string;
  onVoltar: () => void;
  onTentarNovamente: () => void;
  onSelecionar: (notification: NotificationItem) => void;
}

function formatarDataHora(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Data não disponível";
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(date);
}

export function NotificationsPage({
  nomeUsuario,
  notificacoes,
  carregando,
  lendoId,
  erro,
  onVoltar,
  onTentarNovamente,
  onSelecionar,
}: NotificationsPageProps) {
  return <AppShell nome={nomeUsuario}>
    <button className="back" type="button" onClick={onVoltar}>← Voltar</button>
    <section className="screen-title">
      <div>
        <h1>Notificações</h1>
        <p className="subtitle">Veja as novidades dos seus grupos.</p>
      </div>
    </section>
    {erro && <div className="alert error" role="alert">
      {erro}
      <button className="link-button" type="button" onClick={onTentarNovamente}>
        Tentar novamente
      </button>
    </div>}
    {carregando ? <p className="card center" role="status">Carregando notificações...</p>
      : notificacoes.length === 0 && !erro
        ? <section className="card empty-state"><p>Você ainda não tem notificações.</p></section>
        : <section className="notification-list" aria-label="Suas notificações">
          {notificacoes.map((notification) => {
            const unread = notification.status === "NAO_LIDA";
            return <button
              className={`notification-item${unread ? " notification-unread" : ""}`}
              type="button"
              key={notification.id}
              disabled={lendoId === notification.id}
              onClick={() => onSelecionar(notification)}
              aria-label={`${unread ? "Não lida. " : ""}${notification.titulo}`}
            >
              <span className="notification-heading">
                <strong>{notification.titulo}</strong>
                {unread && <span className="unread-indicator">Nova</span>}
              </span>
              <span className="notification-message">{notification.mensagem}</span>
              <time dateTime={notification.created_at}>
                {formatarDataHora(notification.created_at)}
              </time>
            </button>;
          })}
        </section>}
  </AppShell>;
}
