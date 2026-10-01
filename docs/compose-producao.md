# Stack Docker de produção

Esta configuração integra Frontend, Backend e PostgreSQL sem configurar
VPS, domínio ou HTTPS. Somente o Frontend publica uma porta no host.
Backend e banco permanecem acessíveis apenas pela rede Docker.

> **STAGING existente:** não execute comandos de backup, restore, adoção ou
> migration no banco atual fora de uma etapa operacional autorizada. O exemplo
> de primeira inicialização abaixo destina-se somente a banco novo e vazio.

## Variáveis

Copie `production.env.example` para `production.env` e substitua todos
os placeholders. O arquivo `production.env` é ignorado pelo Git e não
deve ser versionado. A senha presente em `DATABASE_URL` deve estar
codificada para URL quando contiver caracteres especiais. O host do
banco nessa URL deve ser `db`.

Para validação local, use `ALLOWED_HOSTS=localhost,127.0.0.1`. Quando
Frontend e API estiverem sob a mesma origem, `CORS_ORIGINS` pode
permanecer vazio.

E-mails transacionais exigem `PUBLIC_APP_URL`, `SMTP_HOST` e
`SMTP_FROM_EMAIL`. `SMTP_USERNAME` e `SMTP_PASSWORD` devem ser configurados
em conjunto quando o provedor exigir autenticação. Porta, nome do remetente,
TLS e timeout usam os defaults documentados em `production.env.example`, mas
devem ser conferidos com o provedor antes do deploy. Nunca coloque valores
reais no arquivo de exemplo.

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
estão definidos na seção [Backup e restauração do PostgreSQL](#backup-e-restauração-do-postgresql).

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

Historicamente, o banco do piloto existiu antes da adoção do Alembic. As
US-016 e US-017 concluíram a validação operacional de backup, adoção, deploy e
rollback no STAGING. Isso não autoriza execuções futuras automaticamente.

Em toda nova release, confirme o estado real com `alembic current`, faça e
valide um novo backup e siga o runbook pelo commit homologado. Não execute
`app.adopt_mvp_0_1`, `alembic stamp`, `alembic upgrade` ou `alembic downgrade`
sem identificar previamente o estado do banco e obter autorização operacional.

## Backup e restauração do PostgreSQL

O procedimento abaixo usa `pg_dump` e `pg_restore` do PostgreSQL 16 dentro do
serviço Docker `db`. Foi validado com bancos descartáveis e operacionalmente no
STAGING durante a US-016. Cada release continua exigindo novo backup validado.

### Pré-requisitos

-   Docker e Docker Compose disponíveis;
-   serviço `db` em execução e saudável;
-   arquivo Compose e arquivo de ambiente explicitamente identificados;
-   espaço livre suficiente fora do container;
-   acesso restrito ao diretório que receberá o backup.

O utilitário não lê nem imprime a senha. As ferramentas PostgreSQL usam as
variáveis já presentes no serviço `db` e sua conexão local. Não coloque senha,
URL real ou conteúdo do arquivo de ambiente na linha de comando ou em logs.

### Criar backup

Na raiz do repositório:

``` bash
python backend/scripts/postgres_backup.py \
  --compose-file docker-compose.prod.yml \
  --env-file production.env \
  --project-name toojunto \
  backup \
  --output-dir backups
```

O resultado usa formato custom (`pg_dump -Fc`) e nome UTC no padrão
`toojunto_YYYYMMDD_HHMMSS_utc.dump`. A gravação ocorre primeiro em arquivo
temporário; somente um dump não vazio e reconhecido por `pg_restore --list` é
promovido ao nome definitivo. Falha do `pg_dump` ou da validação retorna código
de erro e remove o arquivo parcial.

O diretório `backups/` e arquivos `*.dump` são ignorados pelo Git. Mesmo assim,
confirme `git status` após a operação.

### Restaurar em banco vazio

O database alvo deve existir, estar vazio e ser inequivocamente diferente de
`POSTGRES_DB`. O utilitário não cria, apaga ou limpa databases. A criação do
destino deve ser uma ação separada e consciente, por exemplo:

``` bash
docker compose --env-file production.env -f docker-compose.prod.yml \
  exec -T db sh -c 'createdb --username="$POSTGRES_USER" toojunto_restore'
```

Depois restaure informando e confirmando explicitamente o mesmo destino:

``` bash
python backend/scripts/postgres_backup.py \
  --compose-file docker-compose.prod.yml \
  --env-file production.env \
  --project-name toojunto \
  restore \
  --backup-file backups/toojunto_YYYYMMDD_HHMMSS_utc.dump \
  --target-db toojunto_restore \
  --confirm-target-db toojunto_restore
```

O restore usa `pg_restore --single-transaction --exit-on-error`, não restaura
owners ou privilégios globais e só informa sucesso depois da conclusão. Ele
recusa arquivo inexistente/vazio, confirmação divergente, o database primário
e destino que já contenha relações de usuário. Não existe opção automática de
`--clean`: qualquer descarte de banco é uma operação distinta e destrutiva que
exige procedimento e autorização próprios.

### Validar a restauração

Configure temporariamente a aplicação para apontar ao database restaurado e
verifique:

``` bash
python -m alembic current
python -m alembic check
python -m alembic upgrade head
```

Também compare com a origem:

-   revision em `alembic_version`;
-   sete tabelas da aplicação;
-   contagens por tabela e dados sentinela;
-   PKs, FKs, constraints e índices relevantes;
-   ausência de alterações após `upgrade head`.

Um backup somente é considerado válido depois de um restore verificado. O
restore não substitui a inspeção de integridade nem autoriza migrations ou
deploy.

### Segurança dos arquivos

Backups podem conter dados pessoais, hashes de senha, tokens de convite e
referências a comprovantes. Não versione, não compartilhe por canais não
autorizados e restrinja permissões e acesso ao diretório. Remova cópias locais
descartáveis ao terminar a validação. Retenção, armazenamento externo,
agendamento e execução do primeiro backup real do piloto não fazem parte deste
procedimento.

## Runbook de deploy seguro no STAGING

Este runbook foi validado no STAGING durante a US-017. Sua execução para uma
nova release continua dependendo de autorização específica. Cada bloco é um
gate: diante de resultado inesperado, interrompa o deploy, preserve as
evidências e não avance por tentativa e erro.

Use sempre o mesmo identificador de projeto Compose:

``` bash
COMPOSE="docker compose --project-name toojunto --env-file production.env -f docker-compose.prod.yml"
```

Não use `set -x`, não imprima `production.env` e não copie valores sensíveis
para logs ou tickets.

### 1. Pré-deploy

#### 1.1 Versão homologada e repositório

Antes de atualizar o checkout, registre o commit atualmente implantado e o
commit homologado que será promovido:

``` bash
cd /opt/toojunto
test -z "$(git status --porcelain)"
CURRENT_COMMIT=$(git rev-parse HEAD)
git branch --show-current
git rev-parse HEAD
git fetch --prune origin
git cat-file -e "${TARGET_COMMIT}^{commit}"
git checkout --detach "$TARGET_COMMIT"
test "$(git rev-parse HEAD)" = "$TARGET_COMMIT"
```

`TARGET_COMMIT` deve ser informado explicitamente a partir da versão homologada;
não use simplesmente o estado mais recente de uma branch. Working tree sujo,
commit ausente ou divergente aborta o procedimento.

#### 1.2 Ambiente, Docker e Compose

Confirme a presença das variáveis obrigatórias sem exibir valores:

``` bash
test -f production.env
for name in POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD DATABASE_URL JWT_SECRET ALLOWED_HOSTS PUBLIC_APP_URL SMTP_HOST SMTP_FROM_EMAIL; do
  grep -qE "^${name}=.+" production.env || { echo "Variável obrigatória ausente: ${name}"; exit 1; }
done
docker version
docker compose version
$COMPOSE config --quiet
```

Nunca use `docker compose config` sem `--quiet` em logs compartilhados, pois a
saída expandida pode conter secrets.

#### 1.3 Estado atual e capacidade

Registre containers, imagens, health, uso de disco e volume antes de alterar
qualquer serviço:

``` bash
$COMPOSE ps
$COMPOSE images
DB_CONTAINER=$($COMPOSE ps -q db)
test -n "$DB_CONTAINER"
docker inspect "$DB_CONTAINER" --format '{{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}'
docker volume inspect toojunto_toojunto_prod_pgdata --format '{{.Name}} {{.Mountpoint}}'
df -h / /var/lib/docker /opt/toojunto
```

Os nomes efetivos do container e volume devem ser confirmados por `$COMPOSE ps`
e `docker volume ls`; não presuma nomes se o projeto já tiver sido iniciado com
outro identificador. Falta de espaço ou estado atual não saudável exige análise
antes de continuar.

Prepare o diretório protegido de backup e confira suas permissões:

``` bash
install -d -m 700 backups
test "$(stat -c '%a' backups)" = "700"
```

### 2. Gate obrigatório de backup

Nenhuma adoção, migration ou atualização de container pode ocorrer antes deste
gate:

``` bash
python backend/scripts/postgres_backup.py \
  --compose-file docker-compose.prod.yml \
  --env-file production.env \
  --project-name toojunto \
  backup \
  --output-dir backups
```

Registre nome, timestamp e tamanho do arquivo. O comando já exige dump não
vazio e valida o formato com `pg_restore --list`. Confirme ainda que o arquivo
está ignorado pelo Git:

``` bash
git status --short --ignored backups
```

Se o comando falhar, se não houver arquivo válido ou se a proteção do diretório
for inadequada, **aborte o deploy**. Não existe exceção para “mudança sem risco”.

### 3. Build e identificação da migration

O build deve terminar antes de qualquer alteração no banco; falha de build
mantém os containers atuais em execução:

``` bash
$COMPOSE build
$COMPOSE run --rm --no-deps backend python -m alembic history
$COMPOSE run --rm --no-deps backend python -m alembic heads
```

Compare a head retornada com a revision prevista na versão homologada. Para a
RC da MVP 0.3, a única head esperada é `a8c3e1f5b7d9`. Head
ausente, múltipla ou inesperada aborta o deploy.

### 4. Primeiro deploy pós-Alembic

O banco atual do piloto foi criado antes do Alembic. Identifique o estado sem
alterá-lo:

``` bash
$COMPOSE exec -T \
  -e "CHECK_SQL=SELECT(to_regclass('public.alembic_version')NOTNULL);" \
  db sh -c 'exec psql --username="$POSTGRES_USER" --dbname="$POSTGRES_DB" \
  --tuples-only --no-align --command="$CHECK_SQL"'
```

Se retornar `f`, execute **uma única vez** o comando de adoção segura:

``` bash
$COMPOSE run --rm --no-deps backend python -m app.adopt_mvp_0_1
```

Esse comando valida todo o schema antes de registrar a baseline fixa. Qualquer
divergência ou erro aborta o deploy. Não corrija automaticamente o banco e não
use `alembic stamp head`.

Se a consulta retornar `t`, o banco já possui controle Alembic: não execute a
adoção novamente. Confira diretamente:

``` bash
$COMPOSE run --rm --no-deps backend python -m alembic current
```

Após adoção ou confirmação, prossiga pelo fluxo comum de migration.

### 5. Deploys subsequentes e migrations

Em todo deploy com banco já controlado:

``` bash
$COMPOSE run --rm --no-deps backend python -m alembic current
$COMPOSE run --rm --no-deps backend python -m alembic upgrade head
$COMPOSE run --rm --no-deps backend python -m alembic current
$COMPOSE run --rm --no-deps backend python -m alembic heads
$COMPOSE run --rm --no-deps backend python -m alembic check
```

Falha de migration ou drift impede a atualização dos containers. Registre a
revision anterior, a revision alcançada e o erro; não declare sucesso e não
execute downgrade ou restore automaticamente.

### 6. Atualização controlada dos serviços

O PostgreSQL deve permanecer em execução e seu volume deve ser preservado.
Atualize primeiro o Backend, aguarde health e depois atualize o Frontend:

``` bash
$COMPOSE up -d --no-deps backend
$COMPOSE ps backend
$COMPOSE exec -T backend python -c \
  "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5)"
$COMPOSE exec -T backend python -c \
  "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/db', timeout=5)"

$COMPOSE up -d --no-deps frontend
$COMPOSE ps frontend
$COMPOSE exec -T frontend wget -q -O /dev/null http://127.0.0.1:8080/
```

Não execute `docker compose down` como parte do deploy normal. **Nunca execute
`docker compose down -v`**, `docker volume rm` ou comando equivalente: o volume
`toojunto_prod_pgdata` contém o banco persistente.

### 7. Health checks e smoke tests

Primeiro confirme internamente todos os serviços:

``` bash
$COMPOSE ps
$COMPOSE exec -T db sh -c 'pg_isready --username="$POSTGRES_USER" --dbname="$POSTGRES_DB"'
$COMPOSE exec -T backend python -c \
  "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5)"
$COMPOSE exec -T backend python -c \
  "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/db', timeout=5)"
$COMPOSE exec -T frontend wget -q -O /dev/null http://127.0.0.1:8080/
```

Depois execute os smokes públicos, somente leitura:

``` bash
curl -fsS https://toojunto.com/ -o /dev/null
curl -fsS https://toojunto.com/invites/smoke-deploy -o /dev/null
curl -fsS https://toojunto.com/api/health
curl -fsS https://toojunto.com/api/health/db
curl -sS -o /dev/null -w '%{http_code} %{redirect_url}\n' https://www.toojunto.com/
```

A página principal e a rota SPA devem responder, os dois health checks devem
indicar sucesso, HTTPS deve ser válido e `www` deve redirecionar ao domínio
canônico. Esses testes não criam nem alteram dados funcionais.

### 8. Rollback da aplicação

Use rollback da aplicação quando o problema estiver no código/container e o
schema continuar compatível com a versão anterior:

1.  preserve logs, commit implantado, `current`, imagens e health;
2.  volte o checkout ao `CURRENT_COMMIT` registrado no início;
3.  reconstrua as imagens dessa revisão;
4.  atualize Backend e Frontend na mesma ordem controlada;
5.  repita health checks e smoke tests.

``` bash
git checkout --detach "$CURRENT_COMMIT"
$COMPOSE build backend frontend
$COMPOSE up -d --no-deps backend
$COMPOSE up -d --no-deps frontend
```

Não inicie a aplicação anterior se ela for incompatível com o schema já
migrado. Nesse caso, interrompa e trate o banco separadamente.

### 9. Rollback do banco

Rollback de aplicação não desfaz schema ou dados. `alembic downgrade` somente
pode ser usado quando o `downgrade()` foi revisado, testado e preserva os dados
necessários. Ele não substitui restore.

Se a migration alterar ou destruir dados, pode ser necessário restaurar o
backup em um **database distinto e vazio**, validar integralmente e decidir de
forma explícita como redirecionar a aplicação. O utilitário de restore recusa o
database primário e nunca executa automaticamente. Não sobrescreva o banco do
piloto e não altere `production.env` sem autorização operacional específica.

### 10. Encerramento

O deploy somente termina após registrar:

-   commit anterior e commit implantado;
-   arquivo, horário e tamanho do backup validado;
-   revision Alembic antes e depois;
-   resultado do build e identificação das imagens;
-   estado/health de todos os containers;
-   resultado de cada smoke test;
-   horário final e responsável pela execução.

Qualquer gate não aprovado mantém o deploy como falho ou interrompido. A
execução real deste runbook no STAGING requer autorização separada e será a
evidência necessária para homologar a release em execução.

## Agendamento dos lembretes financeiros

Para a MVP 0.3, o acionador escolhido é o `cron` do host. O job roda diariamente
às 08:00 no fuso `America/Bahia`, em container efêmero do serviço Backend. O
`flock` impede duas execuções simultâneas e a saída é anexada a um log dedicado.

Instale somente durante uma etapa operacional autorizada, com o checkout em
`/opt/toojunto`, adicionando ao crontab do usuário operacional:

``` cron
CRON_TZ=America/Bahia
0 8 * * * cd /opt/toojunto && /usr/bin/flock -n /run/lock/toojunto-financial-notifications.lock /usr/bin/docker compose --project-name toojunto --env-file production.env -f docker-compose.prod.yml run --rm --no-deps backend python -m app.jobs.financial_notifications >> /var/log/toojunto-financial-notifications.log 2>&1
```

Antes de instalar, confirme os caminhos de `docker`, `flock`, checkout e log no
host. Para validar, confira `crontab -l`, timestamp/saída do log e os registros
de notificações e entregas criados. Execute novamente de forma controlada para
confirmar a idempotência. Exit code diferente de zero fica registrado no log;
o job não deve ser repetido manualmente por tentativa e erro sem diagnóstico.

Para desabilitar, comente ou remova somente essa entrada do crontab e confirme
com `crontab -l`. A remoção do agendamento não altera dados nem containers.

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
STAGING e o runbook operacional validado na US-017.
