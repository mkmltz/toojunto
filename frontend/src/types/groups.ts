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

export interface GrupoLista extends GrupoComPapel {
  vagas_disponiveis: number;
}

export interface IntegranteGrupo {
  nome: string;
  papel: PapelGrupo;
}

export interface FormacaoGrupo {
  quantidade_atual: number;
  limite: number;
  vagas_disponiveis: number;
  participantes: IntegranteGrupo[];
}

export interface GrupoDetalhe extends GrupoComPapel {
  formacao: FormacaoGrupo;
  ordem_recebimento?: {
    posicao: number;
    nome: string;
    papel: PapelGrupo;
    data_prevista: string;
  }[];
}

export type SituacaoCiclo = "ATUAL" | "PROXIMO" | "CONCLUIDO";

export interface ProgressoGrupo {
  ciclo_atual: number;
  total_ciclos: number;
  contemplado_ciclo_atual: string;
  data_prevista_ciclo_atual: string;
  grupo_concluido?: boolean;
  ciclos: {
    numero_ciclo: number;
    nome: string;
    papel: PapelGrupo;
    data_prevista: string;
    situacao: SituacaoCiclo;
  }[];
}

export type SituacaoObrigacao = "PENDENTE" | "AGUARDANDO_CONFIRMACAO" | "ATRASADO" | "CONFIRMADO" | "REJEITADO";

export interface ObrigacaoPagamento {
  grupo_id: number;
  numero_ciclo: number;
  pagador_id: number;
  pagador_usuario_id: number;
  pagamento_id?: number | null;
  pode_avaliar?: boolean;
  pagador_nome: string;
  recebedor_id: number;
  recebedor_nome: string;
  valor: string;
  data_prevista: string;
  prazo_pagamento: string;
  dias_ate_data_prevista: number;
  dias_ate_prazo: number;
  alerta_prazo: boolean;
  situacao: SituacaoObrigacao;
  status_registro: string | null;
  declarado_em: string | null;
}

export interface ConviteGrupo {
  id: number;
  group_id: number;
  token: string;
  invite_path: string;
  created_at: string;
}
