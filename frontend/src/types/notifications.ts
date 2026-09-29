export interface NotificationItem {
  id: number;
  tipo: string;
  titulo: string;
  mensagem: string;
  referencia_contextual: string | null;
  status: "NAO_LIDA" | "LIDA";
  created_at: string;
  lida_em: string | null;
}

export interface UnreadNotificationCount {
  count: number;
}
