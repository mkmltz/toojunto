import { requisicao } from "./auth";
import type { AceiteConvite, ConvitePublico, RecusaConvite } from "../types/invites";


export const consultarConvite = (token: string) =>
  requisicao<ConvitePublico>(`/invites/${encodeURIComponent(token)}`);

export const aceitarConvite = (token: string, jwt: string) =>
  requisicao<AceiteConvite>(`/invites/${encodeURIComponent(token)}/accept`, {
    method: "POST",
    headers: { Authorization: `Bearer ${jwt}` },
  });

export const recusarConvite = (token: string, jwt: string) =>
  requisicao<RecusaConvite>(`/invites/${encodeURIComponent(token)}/reject`, {
    method: "POST",
    headers: { Authorization: `Bearer ${jwt}` },
  });
