import { requisicao } from "./auth";
import type { ConviteGrupo, Grupo, GrupoAtualizacaoDados, GrupoCriacaoDados, GrupoDetalhe, GrupoLista, ObrigacaoPagamento, ProgressoGrupo } from "../types/groups";

export const criarGrupo = (dados: GrupoCriacaoDados, token: string) =>
  requisicao<Grupo>("/groups", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(dados),
  });

export const listarGrupos = (token: string) => requisicao<GrupoLista[]>("/groups", {
  headers: { Authorization: `Bearer ${token}` },
});

export const buscarGrupo = (grupoId: number, token: string) => requisicao<GrupoDetalhe>(`/groups/${grupoId}`, {
  headers: { Authorization: `Bearer ${token}` },
});

export const buscarProgressoGrupo = (grupoId: number, token: string) => requisicao<ProgressoGrupo>(`/groups/${grupoId}/cycles`, {
  headers: { Authorization: `Bearer ${token}` },
});

export const buscarObrigacoesPagamento = (grupoId: number, ciclo: number, token: string) =>
  requisicao<ObrigacaoPagamento[]>(`/groups/${grupoId}/cycles/${ciclo}/payments`, {
    headers: { Authorization: `Bearer ${token}` },
  });

export const informarPagamento = (grupoId: number, ciclo: number, token: string) =>
  requisicao<ObrigacaoPagamento>(`/groups/${grupoId}/cycles/${ciclo}/payments`, {
    method: "POST",
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

export const prepararSorteio = (grupoId: number, token: string) => requisicao<Grupo>(`/groups/${grupoId}/prepare-draw`, {
  method: "POST",
  headers: { Authorization: `Bearer ${token}` },
});

export const realizarSorteio = (grupoId: number, token: string) => requisicao<GrupoDetalhe>(`/groups/${grupoId}/draw`, {
  method: "POST",
  headers: { Authorization: `Bearer ${token}` },
});

export const gerarOuObterConvite = (grupoId: number, token: string) => requisicao<ConviteGrupo>(`/groups/${grupoId}/invite`, {
  method: "POST",
  headers: { Authorization: `Bearer ${token}` },
});
