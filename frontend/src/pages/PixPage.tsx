import { useEffect, useState, type FormEvent } from "react";
import { AppShell } from "../components/AppShell";

interface PixPageProps {
  nomeUsuario: string;
  chavePix: string | null;
  carregando: boolean;
  salvando: boolean;
  erro: string;
  sucesso: string;
  onVoltar: () => void;
  onTentarNovamente: () => void;
  onSalvar: (chavePix: string | null) => Promise<void>;
}

export function PixPage({ nomeUsuario, chavePix, carregando, salvando, erro, sucesso, onVoltar, onTentarNovamente, onSalvar }: PixPageProps) {
  const [valor, setValor] = useState(chavePix ?? "");

  useEffect(() => { setValor(chavePix ?? ""); }, [chavePix]);

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    const normalizada = valor.trim();
    await onSalvar(normalizada || null);
  }

  return <AppShell nome={nomeUsuario}>
    <button className="back" type="button" onClick={onVoltar}>← Voltar para Meus Grupos</button>
    <section className="screen-title"><div><h1>Minha chave Pix</h1><p className="subtitle">Cadastre a chave que você prefere receber.</p></div></section>
    {carregando ? <p className="card center" role="status">Carregando chave Pix...</p> : <form className="card pix-form" onSubmit={enviar}>
      {erro && <div className="alert error" role="alert">{erro}<button className="link-button" type="button" onClick={onTentarNovamente}>Tentar novamente</button></div>}
      {sucesso && <p className="alert success" role="status">{sucesso}</p>}
      <label htmlFor="chave-pix">Chave Pix</label>
      <input id="chave-pix" value={valor} onChange={(evento) => setValor(evento.target.value)} maxLength={255} disabled={salvando} aria-describedby="ajuda-chave-pix" />
      <p className="field-help" id="ajuda-chave-pix">Opcional. Usaremos esta chave para facilitar o pagamento quando você for contemplado.</p>
      <button className="btn btn-primary" type="submit" disabled={salvando}>{salvando ? "Salvando..." : "Salvar"}</button>
    </form>}
  </AppShell>;
}
