# Stack Docker de produção

Esta configuração integra Frontend, Backend e PostgreSQL sem configurar
VPS, domínio ou HTTPS. Somente o Frontend publica uma porta no host.
Backend e banco permanecem acessíveis apenas pela rede Docker.

## Variáveis

Copie `production.env.example` para `production.env` e substitua todos
os placeholders. O arquivo `production.env` é ignorado pelo Git e não
deve ser versionado. A senha presente em `DATABASE_URL` deve estar
codificada para URL quando contiver caracteres especiais. O host do
banco nessa URL deve ser `db`.

Para validação local, use `ALLOWED_HOSTS=localhost,127.0.0.1`. Quando
Frontend e API estiverem sob a mesma origem, `CORS_ORIGINS` pode
permanecer vazio.

## Construção e primeira inicialização

``` bash
docker compose --env-file production.env -f docker-compose.prod.yml build
docker compose --env-file production.env -f docker-compose.prod.yml up -d db
docker compose --env-file production.env -f docker-compose.prod.yml run --rm backend python -m app.init_db
docker compose --env-file production.env -f docker-compose.prod.yml up -d
```

A inicialização do schema é deliberadamente explícita. A API não executa
`create_all()` durante seu startup normal. O procedimento definitivo de
banco será tratado na Sprint 8.5.

## Operação

``` bash
docker compose --env-file production.env -f docker-compose.prod.yml ps
docker compose --env-file production.env -f docker-compose.prod.yml logs -f
docker compose --env-file production.env -f docker-compose.prod.yml logs -f backend
docker compose --env-file production.env -f docker-compose.prod.yml down
```

`down` preserva o volume do PostgreSQL. A remoção intencional dos dados
exige o comando destrutivo `down -v`, que não deve ser usado em produção
rotineira.

O Frontend fica disponível em `http://127.0.0.1:8080` por padrão. Ele
encaminha `/api/*` ao Backend removendo o prefixo `/api`, enquanto as
demais URLs usam o fallback SPA para `index.html`.

## Estado real do staging --- revisão 28/09/2026

Este Compose está atualmente implantado na VPS Hostinger como ambiente
de **STAGING/PILOTO**. Não é ambiente de desenvolvimento.

Arquitetura pública atual:

`Internet → Caddy :80/:443 → 127.0.0.1:8080 → Frontend/Nginx → /api/* → Backend → PostgreSQL`

Regras operacionais:

-   Caddy termina HTTPS e redireciona `www.toojunto.com` para
    `toojunto.com`.
-   O Frontend Docker é publicado somente em `127.0.0.1:8080`.
-   Backend e PostgreSQL não publicam portas no host.
-   UFW libera somente SSH/22, HTTP/80 e HTTPS/443.
-   `/api/health` e `/api/health/db` devem responder com sucesso após
    deploy.
-   rotas SPA, inclusive `/invites/{token}`, devem continuar retornando
    a aplicação.
-   `production.env` contém secrets do staging, é ignorado pelo Git e
    deve permanecer com permissões restritas.
-   não desenvolver nem corrigir código diretamente na VPS.

O procedimento com `app.init_db` permanece apenas como mecanismo legado
de primeira inicialização do schema. A partir da Sprint 9 do MVP 0.2,
alterações futuras de schema devem migrar para migrations versionadas,
acompanhadas de backup/restore e rollback documentados.
