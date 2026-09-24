# TooJunto — Sprint 0 Starter

Base técnica do MVP 0.1.

## Stack
- Frontend: React + TypeScript + Vite
- Backend: Python + FastAPI
- Banco: PostgreSQL
- ORM: SQLAlchemy
- Testes: Pytest
- CI: GitHub Actions
- Ambiente local: Docker Compose

## Sprint 0 — estado
- Estrutura frontend/backend: OK
- PostgreSQL via Docker Compose: OK
- Configuração por ambiente: OK
- Modelo inicial de dados: OK
- Health check da API: OK
- Health check do banco: OK
- Teste inicial: OK
- CI: OK

## Modelo inicial
Tabelas correspondentes ao MVP:
- usuarios
- grupos
- participantes
- ciclos
- pagamentos
- contemplacoes

## Inicializar banco local

1. Copie `.env.example` para `.env`.
2. Suba o PostgreSQL:

```bash
docker compose up -d db
```

3. Instale dependências do backend:

```bash
pip install -r backend/requirements.txt
```

4. Inicialize as tabelas:

```bash
PYTHONPATH=backend python -m app.init_db
```

5. Rode a API:

```bash
PYTHONPATH=backend uvicorn app.main:app --reload
```

O comando acima e a opção `--reload` são exclusivos de development. Em
production, use `APP_ENV=production`, configure `DATABASE_URL`, `JWT_SECRET`,
`ALLOWED_HOSTS` e, quando necessário, `CORS_ORIGINS` explicitamente, e nunca
execute o Uvicorn com `--reload`. O comando definitivo de produção será
definido no empacotamento do Sprint 8.3.

Health:
- `/health`
- `/health/db`

## Próximo passo
Sprint 1 — Autenticação:
- cadastro
- login
- hash de senha
- JWT
- autorização básica
- integração das telas reais do protótipo
