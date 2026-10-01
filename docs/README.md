# TooJunto --- documentação operacional do repositório

Atualização: 01/10/2026.

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

-   **MVP 0.1:** funcionalmente homologada e implantada no ambiente de
    STAGING/PILOTO.
-   **MVP 0.2:** concluída como baseline funcional e técnica da MVP 0.3.
    Incluiu evolução segura de schema, notificações in-app, e-mail
    transacional, eventos operacionais da jornada, recusa explícita de
    convite, lembretes de pagamento e correções operacionais.
-   **MVP 0.3:** versão candidata ao lançamento público/piloto real
    controlado. Desenvolvimento iniciado em 01/10/2026.
-   **STAGING:** VPS Hostinger publicada por HTTPS em `toojunto.com`;
    permanece como ambiente integrado e não é ambiente de
    desenvolvimento.
-   **Desenvolvimento:** continua local.
-   **Princípio:** menos é mais; não ampliar escopo silenciosamente.

## MVP 0.3 --- objetivo e roadmap

Objetivo: colocar o TooJunto em condições de operar um piloto real
controlado com usuários reais, preservando simplicidade extrema,
segurança, privacidade e a regra de que a plataforma não movimenta nem
custodia dinheiro.

Roadmap aprovado:

-   **Sprint 16 --- Pix opcional e experiência de pagamento**
    -   US-033 --- cadastrar/editar chave Pix opcional.
    -   US-034 --- visualizar a chave Pix do contemplado no contexto
        autorizado do pagamento.
    -   US-035 --- copiar chave Pix e preservar o fluxo quando não
        houver Pix.
-   **Sprint 17 --- Qualidade, segurança e privacidade**
    -   regressão completa;
    -   autorização, isolamento e privacidade;
    -   consolidação do gate de release.
-   **Sprint 18 --- Release Candidate e Go-Live**
    -   STAGING final e homologação ponta a ponta;
    -   integração Landing Page → App;
    -   migrations, backup, health checks, smoke tests e rollback;
    -   decisão formal de GO/NO-GO.

O deploy consolidado da MVP 0.3 para STAGING ocorrerá após a conclusão
das sprints e atualização da documentação, antes do gate final de
Go-Live.

## Estado da Sprint 16

### US-033 --- cadastrar/editar chave Pix opcional

**Status: concluída, aprovada e homologada pelo PO em localhost.**

Implementação aprovada:

-   campo `usuarios.chave_pix`, `VARCHAR(255)`, nullable;
-   migration Alembic `a8c3e1f5b7d9`, com
    `down_revision = f1b6c8d4a2e9`;
-   `GET /auth/me/pix`;
-   `PUT /auth/me/pix`;
-   usuário determinado exclusivamente pelo JWT;
-   chave Pix opcional;
-   `null`, string vazia ou somente espaços removem a chave;
-   schemas específicos impedem exposição automática da chave em
    contratos existentes;
-   interface autenticada **Minha chave Pix**;
-   nenhuma validação bancária, integração Pix, QR Code ou consulta por
    `usuario_id`.

Validação da US-033:

-   Backend: **272 testes aprovados, 0 falhas, 0 skipped**;
-   Frontend: **101 testes aprovados, 0 falhas, 0 skipped**;
-   build de produção aprovado;
-   Alembic com uma única HEAD: `a8c3e1f5b7d9`;
-   `alembic check`: sem drift;
-   homologação manual em localhost: aprovada.

### US-034 e US-035

Ainda não concluídas. Não considerar funcionalidades dessas USs como
implementadas até aprovação e homologação de seus respectivos Cards.

## Fluxo de trabalho da MVP 0.3

Para cada User Story:

`Card Backend → /dev-backend no Codex → relatório → revisão/aprovação → Card Frontend → /dev-frontend no Codex → relatório → revisão/aprovação → homologação do PO em localhost → commit/push`

Regras do processo:

-   não fazer commit/push automaticamente pelos agents;
-   não ampliar escopo silenciosamente;
-   Backend e Frontend devem reutilizar os padrões existentes;
-   divergências entre Card e código real devem ser reportadas antes de
    decisão arquitetural;
-   após homologação local da US, realizar commit/push;
-   não fazer deploy incremental para STAGING a cada US/Sprint da MVP
    0.3;
-   ao concluir todas as sprints, atualizar a documentação e preparar a
    Release Candidate em STAGING;
-   nunca corrigir código manualmente na VPS.

## Gate de Go-Live

A MVP 0.3 somente poderá seguir para lançamento após decisão formal de
**GO/NO-GO** baseada em evidências.

O gate final deve cobrir, no mínimo:

-   jornada funcional completa;
-   regressão Backend e Frontend;
-   segurança, autorização, isolamento e privacidade;
-   zero bug bloqueante conhecido;
-   migrations Alembic consistentes e sem drift;
-   backup e estratégia de rollback;
-   SMTP real e notificações;
-   job financeiro;
-   health checks e smoke tests;
-   Landing Page → App;
-   homologação ponta a ponta pelo PO;
-   tratamento dos secrets/credenciais pendentes identificados no
    handoff.

## Documentos deste diretório

-   `visao.md` --- visão do produto e evolução funcional aprovada.
-   `requisitos.md` --- regras funcionais e requisitos vigentes.
-   `arquitetura.md` --- arquitetura atual, STAGING e evolução técnica
    aprovada.
-   `plano-desenvolvimento.md` --- histórico, roadmap e planejamento das
    MVPs.
-   `compose-producao.md` --- operação do stack Docker usado no STAGING
    e referência para migrations, adoção segura de bancos legados e
    rollback de schema.

## Escopo e limites da MVP 0.3

A MVP 0.3 mantém o TooJunto como plataforma de organização de grupos: o
dinheiro continua sendo transferido diretamente entre participantes.

A chave Pix é apenas uma facilidade para o recebimento. A plataforma não
valida titularidade bancária e a ausência de Pix nunca pode impedir o
fluxo de pagamento.

Permanecem fora do escopo de lançamento, salvo nova decisão formal:
WhatsApp automático, chat, push notification, SMS, aplicativo nativo,
Pix/Open Finance integrado, iniciação de pagamento, QR Code/Pix Copia e
Cola gerado pela plataforma, marketplace, reputação, painel
administrativo complexo, microserviços e brokers distribuídos sem
necessidade comprovada.
