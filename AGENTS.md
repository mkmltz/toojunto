# TooJunto — Equipe de Desenvolvimento

Este arquivo define os papéis especializados utilizados no desenvolvimento do TooJunto.

## Fontes oficiais

Antes de implementar qualquer tarefa, consulte quando aplicável:

- docs/visao.md
- docs/requisitos.md
- docs/arquitetura.md
- docs/plano-desenvolvimento.md
- prototype/

O código existente também deve ser analisado antes de qualquer alteração.

## /dev-backend

Instruções: `agents/dev-backend.md`

Responsável pelo Backend, APIs, banco de dados, regras de negócio,
segurança, autenticação/autorização e testes Backend.

Quando uma tarefa começar com `/dev-backend`, leia
`agents/dev-backend.md` antes de executar a tarefa.

## /dev-frontend

Instruções: `agents/dev-frontend.md`

Responsável pelo Frontend React/TypeScript, UX/UI, integração com APIs,
responsividade e testes Frontend.

Quando uma tarefa começar com `/dev-frontend`, leia
`agents/dev-frontend.md` antes de executar a tarefa.

## Regras gerais

- Trabalhar somente na Task atribuída.
- Não alterar requisitos ou escopo sem autorização.
- Não implementar funcionalidades adicionais por iniciativa própria.
- Preservar funcionalidades existentes.
- Executar os testes relevantes antes de declarar uma Task concluída.
- Não fazer commit ou push sem autorização do Product Owner.
- Informar impedimentos em vez de contorná-los alterando o escopo.