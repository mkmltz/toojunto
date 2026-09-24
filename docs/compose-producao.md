# Stack Docker de produção

Esta configuração integra Frontend, Backend e PostgreSQL sem configurar VPS,
domínio ou HTTPS. Somente o Frontend publica uma porta no host. Backend e banco
permanecem acessíveis apenas pela rede Docker.

## Variáveis

Copie `production.env.example` para `production.env` e substitua todos os
placeholders. O arquivo `production.env` é ignorado pelo Git e não deve ser
versionado. A senha presente em `DATABASE_URL` deve estar codificada para URL
quando contiver caracteres especiais. O host do banco nessa URL deve ser `db`.

Para validação local, use `ALLOWED_HOSTS=localhost,127.0.0.1`. Quando Frontend e
API estiverem sob a mesma origem, `CORS_ORIGINS` pode permanecer vazio.

## Construção e primeira inicialização

```bash
docker compose --env-file production.env -f docker-compose.prod.yml build
docker compose --env-file production.env -f docker-compose.prod.yml up -d db
docker compose --env-file production.env -f docker-compose.prod.yml run --rm backend python -m app.init_db
docker compose --env-file production.env -f docker-compose.prod.yml up -d
```

A inicialização do schema é deliberadamente explícita. A API não executa
`create_all()` durante seu startup normal. O procedimento definitivo de banco
será tratado na Sprint 8.5.

## Operação

```bash
docker compose --env-file production.env -f docker-compose.prod.yml ps
docker compose --env-file production.env -f docker-compose.prod.yml logs -f
docker compose --env-file production.env -f docker-compose.prod.yml logs -f backend
docker compose --env-file production.env -f docker-compose.prod.yml down
```

`down` preserva o volume do PostgreSQL. A remoção intencional dos dados exige
o comando destrutivo `down -v`, que não deve ser usado em produção rotineira.

O Frontend fica disponível em `http://127.0.0.1:8080` por padrão. Ele encaminha
`/api/*` ao Backend removendo o prefixo `/api`, enquanto as demais URLs usam o
fallback SPA para `index.html`.
