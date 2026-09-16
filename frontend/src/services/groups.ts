import { requisicao } from "./auth";
import type { Grupo, GrupoCriacaoDados } from "../types/groups";

export const criarGrupo = (dados: GrupoCriacaoDados, token: string) =>
  requisicao<Grupo>("/groups", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(dados),
  });
