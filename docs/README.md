# TooJunto --- documentação operacional do repositório

Atualização: 28/09/2026.

Este diretório contém a documentação Markdown de consulta rápida para
agents/Codex. A documentação histórica e oficial do produto permanece no
OneDrive `Toojunto/`. Os arquivos MD não substituem as User
Stories/Cards aprovados para execução.

## Hierarquia de referência

1.  **US/Card/Task aprovada da Sprint atual** --- define exatamente o
    que implementar.
2.  **Documentação MD do repositório** --- fornece contexto funcional,
    arquitetural e operacional.
3.  **Documentação oficial DOCX no OneDrive `Toojunto/`** --- histórico
    e referência documental do produto.

Em caso de conflito entre uma Task aprovada e documentação histórica, o
agent não deve decidir autonomamente: deve interromper a implementação e
reportar a divergência.

## Estado do produto

-   **MVP 0.1:** funcionalmente homologado e implantado no ambiente de
    STAGING/PILOTO.
-   **STAGING:** VPS Hostinger publicada por HTTPS em `toojunto.com`;
    não é ambiente de desenvolvimento.
-   **Desenvolvimento:** continua local.
-   **MVP 0.2:** escopo aprovado e roadmap definido para Sprints 9 a 15.
-   **Princípio:** menos é mais; não ampliar escopo silenciosamente.

## Fluxo de trabalho

`desenvolvimento local → testes → homologação da Task → commit/push → deploy controlado no staging → smoke test → homologação integrada`

Nunca corrigir código manualmente na VPS.

## Documentos deste diretório

-   `visao.md` --- visão do produto, baseline do MVP 0.1 e evolução
    aprovada do MVP 0.2.
-   `requisitos.md` --- regras funcionais e matriz oficial de
    eventos/notificações do MVP 0.2.
-   `arquitetura.md` --- arquitetura atual, staging e evolução técnica
    aprovada.
-   `plano-desenvolvimento.md` --- histórico do MVP 0.1 e roadmap
    executivo das Sprints 9--15.
-   `compose-producao.md` --- operação do stack Docker usado no staging.

## Escopo central do MVP 0.2

O MVP 0.2 adiciona evolução segura do schema, notificações in-app,
e-mail transacional, eventos operacionais da jornada, recusa explícita
de convite, lembretes de pagamento, integração Landing Page → App e
correção da nitidez da marca.

Permanecem fora do MVP 0.2: WhatsApp automático, chat, push
notification, SMS, aplicativo nativo, Pix/Open Finance integrado,
marketplace, reputação, painel administrativo complexo, microserviços e
brokers distribuídos sem necessidade comprovada.
