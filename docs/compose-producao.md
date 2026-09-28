# Stack Docker de produção

Esta configuração integra Frontend, Backend e PostgreSQL sem configurar
VPS, domínio ou HTTPS. Somente o Frontend publica uma porta no host.
Backend e banco permanecem acessíveis apenas pela rede Docker.

> **STAGING existente:** não execute os comandos de adoção ou migration deste
> documento no banco atual antes da conclusão da US-016 e da autorização
> operacional prevista para a US-017. O exemplo de primeira inicialização
> abaixo destina-se a um banco novo e vazio.

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
docker compose --env-file production.env -f docker-compose.prod.yml run --rm backend python -m alembic upgrade head
docker compose --env-file production.env -f docker-compose.prod.yml up -d
```

A inicialização do schema é deliberadamente explícita. A API não executa
`create_all()` nem migrations durante seu startup normal. Para bancos novos,
Alembic é o mecanismo oficial de construção e evolução do schema.

## Operação de migrations

Execute os comandos Alembic a partir do diretório `backend`, com o ambiente
Python ativado e `DATABASE_URL` configurada para o banco pretendido. Em um
stack Docker, use o mesmo módulo dentro do serviço `backend`, como no exemplo
de primeira inicialização acima. Confirme sempre ambiente e destino antes de
qualquer operação que altere o banco.

### Banco novo

Um PostgreSQL vazio deve ser construído exclusivamente pelo histórico
versionado:

``` bash
python -m alembic upgrade head
```

Esse comando cria o schema atual e registra a revision aplicada em
`alembic_version`. Não use `app.init_db` para criar novos ambientes.

### Banco MVP 0.1 legado

Um banco criado antes da adoção do Alembic possui as sete tabelas do MVP 0.1,
mas não possui `alembic_version`. Para incorporá-lo ao histórico, execute:

``` bash
python -m app.adopt_mvp_0_1
```

O comando exige PostgreSQL e ausência de `alembic_version`, valida o conjunto
de tabelas e compara o schema existente com `Base.metadata`, incluindo colunas,
tipos, nullability, chaves, constraints e índices. Ele usa exclusivamente a
baseline fixa `9b2f1c4d7e6a` e somente executa o stamp após confirmar
equivalência. Divergências interrompem a adoção e não são corrigidas
automaticamente.

**Nunca execute `alembic stamp head` manualmente para adotar um banco legado.**
O stamp apenas registra uma revision; ele não valida, cria ou corrige o schema.

### Banco já controlado por Alembic

Comandos principais:

-   `python -m alembic current` --- mostra a revision registrada no banco;
-   `python -m alembic history` --- mostra o histórico disponível;
-   `python -m alembic heads` --- mostra as heads do código;
-   `python -m alembic check` --- compara o banco com `Base.metadata` e acusa
    operações de schema ainda não representadas por migration;
-   `python -m alembic upgrade head` --- aplica as revisions pendentes até a
    head atual.

Antes de um upgrade, confirme que `current`, `history` e `heads` correspondem
ao artefato que será promovido.

### Rollback de schema

Para retornar a uma revision anterior tecnicamente suportada pela migration:

``` bash
python -m alembic downgrade <revision>
```

Revise o `downgrade()` e avalie o impacto antes da execução. Downgrade altera o
schema e pode ser destrutivo; ele **não é backup** e não restaura dados
eliminados ou transformados. Backup e restauração são controles separados e
serão formalizados na US-016.

### Futuras alterações de schema

O fluxo obrigatório é:

1.  alterar os models;
2.  gerar uma nova revision Alembic, normalmente com `python -m alembic
    revision --autogenerate -m "descrição"`;
3.  revisar manualmente toda a migration gerada, sem aceitar autogenerate
    cegamente;
4.  testar o upgrade em PostgreSQL descartável;
5.  testar o downgrade quando ele for tecnicamente seguro e aplicável;
6.  executar `python -m alembic check` no schema atualizado;
7.  executar a suíte Backend completa;
8.  somente então promover a alteração pelo procedimento aprovado.

### Estado transitório de `app.init_db`

`app.init_db` permanece no código por compatibilidade e porque reproduziu o
banco pré-Alembic durante a validação da adoção legada. Ele não é o mecanismo
oficial para novas instalações nem para futuras evoluções de schema. Sua
remoção exige Task específica e confirmação de que não restam dependências
operacionais.

### Proteção do STAGING

Até a conclusão desta documentação, nenhuma adoção Alembic foi executada no
STAGING/PILOTO. Não execute `app.adopt_mvp_0_1`, `alembic stamp`, `alembic
upgrade` ou `alembic downgrade` nesse ambiente sem backup verificável e sem a
autorização operacional correspondente.

A US-016 deve primeiro definir e validar backup e restauração do PostgreSQL. A
adoção do banco do piloto só poderá ocorrer depois disso. A US-017 definirá em
seguida o procedimento seguro de deploy, migrations, verificações de saúde e
rollback no STAGING.

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

O procedimento com `app.init_db` permanece temporariamente apenas por
compatibilidade. A operação oficial de schema está definida na seção
[Operação de migrations](#operação-de-migrations), respeitando a proteção do
STAGING até a conclusão das US-016 e US-017.
