# TooJunto — Documentação de Referência

Esta pasta contém as versões Markdown convertidas diretamente dos documentos DOCX oficiais do MVP 0.1.

- `visao.md` — Documento de Visão
- `requisitos.md` — Documento de Requisitos
- `arquitetura.md` — Arquitetura Técnica
- `plano-desenvolvimento.md` — Plano de Desenvolvimento

## Regra de uso

O conteúdo deve permanecer fiel aos documentos oficiais. Alterações de produto, requisitos, arquitetura ou plano devem ser deliberadas e documentadas; não devem ser inferidas pelo agente.

## Rotina de desenvolvimento

Antes: Docker → PostgreSQL → `.venv` → dependências → backend → banco → `/health` → `/health/db`

Durante: implementar → testar → corrigir

Final: testes → validação → documentação → commit
