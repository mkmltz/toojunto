export interface GrupoCriacaoDados {
  nome: string;
  valor_cota: string;
  quantidade_participantes: number;
  quantidade_ciclos: number;
  data_inicio: string;
}

export interface GrupoFormularioDados {
  nome: string;
  valor_cota: string;
  quantidade_participantes: number;
  data_inicio: string;
}

export type GrupoAtualizacaoDados = GrupoFormularioDados;
export type PapelGrupo = "GESTOR" | "PARTICIPANTE";

export interface Grupo {
  id: number;
  nome: string;
  gestor_id: number;
  valor_cota: string;
  valor_premio: string;
  quantidade_participantes: number;
  quantidade_ciclos: number;
  data_inicio: string;
  status: "RASCUNHO" | string;
  created_at: string;
}

export interface GrupoComPapel extends Grupo {
  papel: PapelGrupo;
}
