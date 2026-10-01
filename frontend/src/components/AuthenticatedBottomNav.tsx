interface AuthenticatedBottomNavProps {
  onCriarGrupo: () => void;
  onAbrirChavePix: () => void;
  onSair: () => void;
}

export function AuthenticatedBottomNav({ onCriarGrupo, onAbrirChavePix, onSair }: AuthenticatedBottomNavProps) {
  return <nav className="authenticated-bottom-nav" aria-label="Navegação autenticada">
    <button type="button" onClick={onCriarGrupo} aria-label="Criar novo grupo">
      <svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" /><path d="M12 8v8M8 12h8" /></svg>
      <span>Criar</span>
    </button>
    <button type="button" onClick={onAbrirChavePix} aria-label="Minha chave Pix">
      <svg aria-hidden="true" viewBox="0 0 24 24"><path d="M7.5 8.5h7a3 3 0 0 1 0 6H10M10 5v14M14.5 18H18" /><circle cx="7" cy="5" r="1" /><circle cx="17" cy="19" r="1" /></svg>
      <span>Pix</span>
    </button>
    <button type="button" onClick={onSair}>
      <svg aria-hidden="true" viewBox="0 0 24 24"><path d="M10 5H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h4M14 8l4 4-4 4M9 12h9" /></svg>
      <span>Sair</span>
    </button>
  </nav>;
}
