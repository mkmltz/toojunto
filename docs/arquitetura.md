TOOJUNTO

Arquitetura Técnica --- MVP 0.1

Documento de arquitetura para implementação e validação

# 1. Visão geral

A arquitetura do MVP deve ser pequena e modular, suficiente para
cadastro, grupos, convites, sorteio, ciclos, pagamentos declarados e
acompanhamento. O TooJunto não movimenta dinheiro no MVP.

Arquitetura: Navegador/Smartphone → Frontend Web → API Backend →
PostgreSQL; com armazenamento privado para comprovantes e
logs/auditoria.

# 2. Princípios arquiteturais

Manter o MVP pequeno e fácil de alterar.

Preferir aplicação web responsiva a aplicativo nativo.

Separar interface, regras de negócio e persistência.

Usar banco relacional para consistência de grupos, ciclos e pagamentos.

Registrar operações críticas para transparência.

Evitar microserviços no MVP.

Evitar integrações externas não indispensáveis.

Preparar pontos de extensão sem implementar complexidade
antecipadamente.

# 3. Stack tecnológica proposta

Kubernetes, microserviços e arquitetura distribuída não são necessários
nesta fase.

# 4. Arquitetura lógica

# 5. Módulos do backend

# 6. Modelo de dados

# 7. Sorteio --- requisitos técnicos

O sorteio só pode ocorrer quando o grupo estiver completo.

O backend é a autoridade para gerar e registrar o resultado.

O resultado deve ser persistido em transação.

A ordem final recebe data/hora e usuário responsável.

Após finalizado, o resultado não pode ser alterado por operação comum.

Correções administrativas futuras devem gerar auditoria.

# 8. Fluxo técnico de pagamento

1.  API identifica contemplado e valor do ciclo.

2.  Frontend apresenta os dados de pagamento.

3.  Usuário realiza o Pix fora do TooJunto.

4.  Usuário registra a declaração.

5.  Comprovante opcional é enviado ao storage.

6.  Gestor confirma ou rejeita.

7.  API atualiza o status e registra auditoria.

Nenhuma etapa do MVP movimenta ou custodia o dinheiro.

# 9. Autenticação e autorização

Senhas nunca são armazenadas em texto puro.

API utiliza HTTPS em produção.

Cada requisição autenticada identifica o usuário.

Gestor só administra grupos em que é gestor.

Participante só consulta grupos dos quais faz parte.

Autorização é validada no backend.

Tokens e segredos ficam fora do código-fonte.

# 10. Upload de comprovantes

Arquivo associado ao pagamento.

Validar tamanho e tipo.

Preferir armazenamento privado.

Acesso respeita permissões do grupo.

Registrar upload quando apropriado.

# 11. API inicial

# 12. Estrutura inicial do projeto

toojunto/ ├── frontend/ │ ├── src/pages/ │ ├── src/components/ │ ├──
src/services/ │ └── src/types/ ├── backend/ │ ├── app/api/ │ ├──
app/domain/ │ ├── app/models/ │ ├── app/schemas/ │ ├── app/services/ │
└── tests/ ├── infra/ ├── docs/ └── .github/workflows/

# 13. Ambientes

Credenciais separadas por ambiente.

Dados reais não devem ser usados em desenvolvimento.

Segredos via variáveis de ambiente.

Banco de produção com backup.

# 14. CI/CD

Pull request dispara lint e testes.

Build de frontend/backend validado automaticamente.

Deploy para staging após aprovação.

Produção somente após validação.

Migrations do banco versionadas.

Rollback simples para versões recentes.

# 15. Estratégia de testes

Prioridade máxima: sorteio, controle de acesso e consistência dos
pagamentos.

# 16. Logs e auditoria

Registrar criação de grupo, aceite de convite, sorteio, declaração e
confirmação/rejeição de pagamento.

Registrar usuário, data/hora, entidade e resultado.

Não registrar senhas ou dados sensíveis desnecessários.

Manter histórico suficiente para explicar o resultado de um sorteio.

# 17. Escalabilidade

Começar com monólito modular. Separação de serviços só deve ocorrer
quando houver necessidade real de escala ou operação.

# 18. Segurança e privacidade --- mínimo

Controle de acesso por papel e grupo.

HTTPS.

Hash seguro de senha.

Validação no frontend e backend.

Proteção contra acesso a dados de outro grupo.

Backup do banco.

Política de retenção de comprovantes.

Armazenar apenas dados necessários.

# 19. Custos e infraestrutura inicial

Iniciar com serviços gerenciados e baixo custo, pagando apenas pelo
necessário ao piloto. Evitar servidores próprios e infraestrutura
antecipada.

# 20. Decisões que ficam para depois

Pix integrado

Open Finance

WhatsApp API

Notificações em escala

Microserviços

Kubernetes

Aplicativo nativo

Marketplace

White-label/API pública

KYC e antifraude avançado

# 21. Checklist de prontidão

Requisitos MVP aprovados.

UX/UI e wireframes aprovados.

Regra final do sorteio definida.

Stack aprovada.

Modelo de dados revisado.

Repositório Git criado.

Ambientes definidos.

PostgreSQL provisionado.

Storage definido.

CI básico configurado.

Critérios de aceite disponíveis.

  -----------------------------------------------------------------------
  Campo                               Valor
  ----------------------------------- -----------------------------------
  Versão                              0.1

  Data                                14 de setembro de 2026

  Status                              Proposta técnica

  Objetivo                            Construir o MVP com simplicidade,
                                      baixo custo e possibilidade de
                                      evolução.
  -----------------------------------------------------------------------

  -----------------------------------------------------------------------
  Camada                  Tecnologia              Justificativa
  ----------------------- ----------------------- -----------------------
  Frontend                React + TypeScript      Ecossistema maduro e
                                                  adequado para interface
                                                  responsiva.

  UI                      CSS/Tailwind ou         Acelera a construção e
                          biblioteca leve         mantém consistência.

  Backend                 Python + FastAPI        Aderente às
                                                  competências técnicas e
                                                  adequado para API.

  ORM                     SQLAlchemy              Separa regras de
                                                  negócio do acesso ao
                                                  banco.

  Banco                   PostgreSQL              Relacional e adequado
                                                  às relações do domínio.

  Autenticação            JWT + hash seguro       Modelo simples para o
                                                  MVP.

  Arquivos                Object Storage          Separa comprovantes dos
                          compatível com S3       dados estruturados.

  Testes                  Pytest + Vitest/React   Cobertura das regras e
                          Testing Library         interface.

  Versionamento           Git                     Histórico e
                                                  colaboração.

  CI/CD                   GitHub Actions          Automação de testes e
                                                  deploy.

  Deploy                  Cloud gerenciada        Reduz operação e evita
                          simples                 infraestrutura própria.
  -----------------------------------------------------------------------

  -----------------------------------------------------------------------
  Componente                          Responsabilidade
  ----------------------------------- -----------------------------------
  Frontend                            Telas, navegação, validação básica
                                      e comunicação com API.

  API                                 Autenticação, autorização, grupos,
                                      sorteio, ciclos e pagamentos.

  Domínio                             Regras de negócio independentes da
                                      interface.

  Persistência                        PostgreSQL.

  Storage                             Comprovantes de pagamento.

  Auditoria                           Eventos críticos.

  Observabilidade                     Logs e erros.
  -----------------------------------------------------------------------

  Módulo     Responsabilidades
  ---------- -------------------------------------------------
  auth       Cadastro e login.
  users      Dados do usuário.
  groups     Criação, configuração e estados.
  members    Participantes e convites.
  draws      Preparação, execução e registro do sorteio.
  cycles     Ciclos e contemplações.
  payments   Declaração, comprovante e confirmação/rejeição.
  audit      Rastreabilidade.

  -----------------------------------------------------------------------
  Entidade                            Campos principais
  ----------------------------------- -----------------------------------
  USUARIO                             id, nome, email, telefone,
                                      senha_hash, created_at

  GRUPO                               id, nome, gestor_id, valor_cota,
                                      quantidade_participantes,
                                      quantidade_ciclos, data_inicio,
                                      status, created_at

  PARTICIPANTE                        id, grupo_id, usuario_id,
                                      ordem_sorteio, status

  CONVITE                             id, grupo_id,
                                      convidado_email/telefone, token,
                                      status, created_at, expires_at

  CICLO                               id, grupo_id, numero, data,
                                      contemplado_id, status

  PAGAMENTO                           id, ciclo_id, pagador_id,
                                      recebedor_id, valor, status,
                                      comprovante_url, data_pagamento

  CONTEMPLACAO                        id, ciclo_id, participante_id,
                                      valor, status, data

  AUDITORIA                           id, usuario_id, grupo_id, evento,
                                      entidade, entidade_id, data_hora,
                                      metadata
  -----------------------------------------------------------------------

  Método   Endpoint                  Objetivo
  -------- ------------------------- ---------------------
  POST     /auth/register            Criar usuário
  POST     /auth/login               Autenticar
  GET      /groups                   Listar grupos
  POST     /groups                   Criar grupo
  GET      /groups/{id}              Consultar grupo
  POST     /groups/{id}/invites      Criar convite
  POST     /invites/{token}/accept   Aceitar convite
  POST     /groups/{id}/draw         Executar sorteio
  GET      /groups/{id}/cycles       Listar ciclos
  POST     /cycles/{id}/payments     Declarar pagamento
  POST     /payments/{id}/confirm    Confirmar pagamento
  POST     /payments/{id}/reject     Rejeitar pagamento
  GET      /groups/{id}/history      Consultar histórico

  Ambiente   Uso
  ---------- ----------------------
  Local      Desenvolvimento.
  Staging    Validação integrada.
  Produção   Piloto real.

  -----------------------------------------------------------------------
  Nível                               Foco
  ----------------------------------- -----------------------------------
  Unitário                            Sorteio, estados, permissões e
                                      cálculos.

  Integração                          API + PostgreSQL + storage.

  E2E                                 Cadastro, convite, entrada, sorteio
                                      e pagamento.

  Usabilidade                         10 telas com usuários reais.

  Segurança básica                    Autorização, acesso indevido e
                                      entradas inválidas.
  -----------------------------------------------------------------------

  MVP                Evolução se necessária
  ------------------ --------------------------
  Monólito modular   Serviços separados
  PostgreSQL único   Replicação/read replicas
  Storage simples    CDN/políticas avançadas
  Deploy simples     Orquestração
  Logs básicos       Observabilidade avançada
  Sem fila           Filas/eventos

# 22. Evolução arquitetural aprovada --- MVP 0.2

Data da revisão: 28/09/2026.

## 22.1 Diretriz

O MVP 0.2 preserva o monólito modular. Groups, Invites, Draws, Cycles e
Payments continuam responsáveis pelas regras de domínio. O mecanismo de
notificações é uma camada interna desacoplada dos canais de entrega.

Arquitetura conceitual:

`Frontend/React → API/FastAPI → regra de negócio → PostgreSQL → evento/notificação → in-app + e-mail`

Não introduzir microserviços, Kafka, RabbitMQ ou outro broker
distribuído sem necessidade comprovada.

## 22.2 Persistência mínima

A evolução deverá suportar, no mínimo:

-   `NOTIFICACAO`: usuário destinatário, tipo, título, mensagem,
    referência contextual, estado lida/não lida e timestamps;
-   controle de entrega de e-mail: destinatário, evento, status,
    tentativas, envio e erro.

A implementação física será criada por migrations versionadas a partir
da Sprint 9.

## 22.3 Consistência

A operação de domínio é prioritária. Se um convite for aceito, um
pagamento informado ou outra transição válida for concluída, falha no
provedor de e-mail não pode desfazer essa operação. A entrega poderá ser
registrada como falha e retomada de forma controlada.

A solução deve evitar duplicidade de notificações/e-mails quando a mesma
operação for reprocessada.

## 22.4 API in-app prevista

-   listar notificações do usuário autenticado;
-   marcar uma notificação do próprio usuário como lida;
-   expor contador/estado de não lidas quando necessário à UX.

Filtros avançados, arquivamento, exclusão em massa e preferências
complexas ficam fora do MVP 0.2.

## 22.5 E-mail transacional

Um único provedor será escolhido durante a Sprint correspondente.
SDK/configuração do provedor não deve ser espalhado pelos services de
domínio. Secrets permanecem somente em variáveis de ambiente e nunca no
Git.

Webhooks do provedor só serão adicionados se forem necessários ao
contrato do provedor escolhido ou à confiabilidade mínima aprovada. Eles
não são objetivo independente do MVP 0.2.

## 22.6 Lembretes

O lembrete de pagamento próximo do prazo faz parte do MVP 0.2. A
implementação deve usar o mecanismo mais simples compatível com o stack
atual. Não introduzir infraestrutura distribuída apenas para
agendamento.

## 22.7 Staging e deploy

Development ocorre localmente. A VPS Hostinger é STAGING/PILOTO. O
acesso público usa Caddy como borda HTTPS e reverse proxy para o
Frontend Docker exposto apenas em `127.0.0.1:8080`; Backend e PostgreSQL
permanecem internos à rede Docker.

Antes de alterações de schema no staging: backup verificável + migration
versionada. A Sprint 9 formaliza migrations, backup/restore e
procedimento de deploy/rollback.

## 22.8 Landing Page

A integração Landing Page → App pertence ao MVP 0.2. A decisão final
entre subdomínio `app.toojunto.com` e rotas no mesmo domínio será tomada
antes da implementação da US-028, com revisão coordenada de DNS, Caddy,
`ALLOWED_HOSTS`, URLs de convite e frontend quando aplicável.

## 22.9 Segurança e privacidade

-   autorização por destinatário para notificações;
-   isolamento entre usuários e grupos;
-   minimizar dados pessoais em e-mails;
-   não colocar JWT em links;
-   links levam a rotas normais da aplicação e respeitam autenticação;
-   secrets segregados por ambiente;
-   nenhum desenvolvimento/correção manual na VPS.
