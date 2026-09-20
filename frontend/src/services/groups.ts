import { requisicao } from "./auth";
import type { ConviteGrupo, Grupo, GrupoAtualizacaoDados, GrupoComPapel, GrupoCriacaoDados } from "../types/groups";

export const criarGrupo = (dados: GrupoCriacaoDados, token: string) =>
  requisicao<Grupo>("/groups", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(dados),
  });

export const listarGrupos = (token: string) => requisicao<GrupoComPapel[]>("/groups", {
  headers: { Authorization: `Bearer ${token}` },
});

export const buscarGrupo = (grupoId: number, token: string) => requisicao<GrupoComPapel>(`/groups/${grupoId}`, {
  headers: { Authorization: `Bearer ${token}` },
});

export const atualizarGrupo = (grupoId: number, dados: GrupoAtualizacaoDados, token: string) => requisicao<Grupo>(`/groups/${grupoId}`, {
  method: "PATCH",
  headers: { Authorization: `Bearer ${token}` },
  body: JSON.stringify(dados),
});

export const cancelarGrupo = (grupoId: number, token: string) => requisicao<Grupo>(`/groups/${grupoId}/cancel`, {
  method: "POST",
  headers: { Authorization: `Bearer ${token}` },
});

export const gerarOuObterConvite = (grupoId: number, token: string) => requisicao<ConviteGrupo>(`/groups/${grupoId}/invite`, {
  method: "POST",
  headers: { Authorization: `Bearer ${token}` },
});
