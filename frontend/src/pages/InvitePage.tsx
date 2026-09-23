import { AuthLayout } from "../components/AuthLayout";
import type { AceiteConvite, ConvitePublico } from "../types/invites";


const formatarValor = (valor: string) => Number(valor).toLocaleString(
  "pt-BR",
  { style: "currency", currency: "BRL" },
);

const formatarData = (data: string) => new Intl.DateTimeFormat(
  "pt-BR",
  { timeZone: "UTC" },
).format(new Date(`${data}T00:00:00Z`));

interface InvitePageProps {
  convite: ConvitePublico | null;
  aceite: AceiteConvite | null;
  carregando: boolean;
  aceitando: boolean;
  erro: string;
  autenticado: boolean;
  indisponivel: boolean;
  onEntrar: () => void;
  onAgoraNao: () => void;
  onCriarConta: () => void;
  onTentarNovamente: () => void;
  onVerGrupo: (grupoId: number) => void;
}

export function InvitePage({
  convite,
  aceite,
  carregando,
  aceitando,
  erro,
  autenticado,
  indisponivel,
  onEntrar,
  onAgoraNao,
  onCriarConta,
  onTentarNovamente,
  onVerGrupo,
}: InvitePageProps) {
  if (carregando) {
    return <AuthLayout><p className="card center" role="status">Carregando convite...</p></AuthLayout>;
  }

  if (aceite) {
    return <AuthLayout><section className="card invite-received center"><span className="badge">Tudo certo</span><h1>Você entrou no Grupo</h1><p>Agora você já pode acompanhar o Grupo no TooJunto.</p><button className="btn btn-primary" type="button" onClick={() => onVerGrupo(aceite.group_id)}>Ver Grupo</button></section></AuthLayout>;
  }

  if (indisponivel) {
    return <AuthLayout><section className="card invite-received center"><h1>Convite indisponível</h1><p>Este convite não está mais disponível.</p><button className="btn btn-secondary" type="button" onClick={onAgoraNao}>Ir para o início</button></section></AuthLayout>;
  }

  if (!convite) {
    return <AuthLayout><section className="card invite-received center"><h1>Não foi possível abrir o convite</h1><p className="alert error" role="alert">{erro || "Tente novamente."}</p><button className="btn btn-primary" type="button" onClick={onTentarNovamente}>Tentar novamente</button><button className="btn btn-secondary" type="button" onClick={onAgoraNao}>Agora não</button></section></AuthLayout>;
  }

  return <AuthLayout><section className="card invite-received"><span className="badge">Convite TooJunto</span><h1>Você foi convidado por {convite.manager_name}</h1><p>Participe de uma caixinha digital no grupo <strong>{convite.group_name}</strong>.</p><dl><div><dt>Cota</dt><dd>{formatarValor(convite.quota_value)}</dd></div><div><dt>Participantes</dt><dd>{convite.participant_limit}</dd></div><div><dt>Vagas disponíveis</dt><dd>{convite.available_slots}</dd></div><div><dt>Início</dt><dd>{formatarData(convite.start_date)}</dd></div></dl>{erro && <p className="alert error" role="alert">{erro}</p>}<button className="btn btn-primary" type="button" disabled={aceitando} onClick={onEntrar}>{aceitando ? "Entrando..." : "Entrar no Grupo"}</button>{!autenticado && <><p className="invite-guidance">Caso você ainda não tenha conta no TooJunto, crie sua conta para participar.</p><button className="btn btn-secondary" type="button" disabled={aceitando} onClick={onCriarConta}>Criar minha conta</button></>}<button className="btn btn-quiet" type="button" disabled={aceitando} onClick={onAgoraNao}>Agora não</button></section></AuthLayout>;
}
