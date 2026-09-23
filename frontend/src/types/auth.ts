export interface Usuario { id: number; nome: string; email: string; telefone: string | null; }
export interface TokenResposta { access_token: string; token_type: "bearer"; }
export interface LoginDados { email: string; senha: string; }
export interface CadastroDados { nome: string; email: string; telefone: string; senha: string; }
