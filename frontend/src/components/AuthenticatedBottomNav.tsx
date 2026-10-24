interface AuthenticatedBottomNavProps {
  ativo: "grupos" | "criar" | "historico" | "pix" | null;
  onAbrirGrupos: () => void;
  onCriarGrupo: () => void;
  onAbrirHistorico: () => void;
  onAbrirChavePix: () => void;
}

export function AuthenticatedBottomNav({ ativo, onAbrirGrupos, onCriarGrupo, onAbrirHistorico, onAbrirChavePix }: AuthenticatedBottomNavProps) {
  return <nav className="authenticated-bottom-nav" aria-label="Navegação autenticada">
    <button className={ativo === "grupos" ? "active" : ""} type="button" onClick={onAbrirGrupos} aria-current={ativo === "grupos" ? "page" : undefined}>
      <svg aria-hidden="true" viewBox="0 0 24 24"><path d="M4 7h16M6 4h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2Z" /><path d="M8 11h8M8 15h5" /></svg>
      <span>Grupos</span>
    </button>
    <button className={ativo === "criar" ? "active" : ""} type="button" onClick={onCriarGrupo} aria-label="Criar novo grupo" aria-current={ativo === "criar" ? "page" : undefined}>
      <svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" /><path d="M12 8v8M8 12h8" /></svg>
      <span>Criar</span>
    </button>
    <button className={ativo === "historico" ? "active" : ""} type="button" onClick={onAbrirHistorico} aria-current={ativo === "historico" ? "page" : undefined}>
      <svg aria-hidden="true" viewBox="0 0 24 24"><path d="M4 12a8 8 0 1 0 2.3-5.7L4 8.6M4 4v4.6h4.6" /><path d="M12 8v4l3 2" /></svg>
      <span>Histórico</span>
    </button>
    <button className={ativo === "pix" ? "active" : ""} type="button" onClick={onAbrirChavePix} aria-label="Minha chave Pix" aria-current={ativo === "pix" ? "page" : undefined}>
      <svg aria-hidden="true" viewBox="0 0 24 24"><path d="M7.5 8.5h7a3 3 0 0 1 0 6H10M10 5v14M14.5 18H18" /><circle cx="7" cy="5" r="1" /><circle cx="17" cy="19" r="1" /></svg>
      <span>Pix</span>
    </button>
  </nav>;
}
