import { requisicao } from "./auth";
import type {
  NotificationItem,
  UnreadNotificationCount,
} from "../types/notifications";

const authorization = (token: string) => ({
  Authorization: `Bearer ${token}`,
});

export const listarNotificacoes = (token: string) =>
  requisicao<NotificationItem[]>("/notifications", {
    headers: authorization(token),
  });

export const contarNotificacoesNaoLidas = (token: string) =>
  requisicao<UnreadNotificationCount>("/notifications/unread-count", {
    headers: authorization(token),
  });

export const marcarNotificacaoComoLida = (
  notificationId: number,
  token: string,
) => requisicao<NotificationItem>(`/notifications/${notificationId}/read`, {
  method: "PATCH",
  headers: authorization(token),
});
