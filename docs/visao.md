TOOJUNTO

Documento de Visão --- MVP 0.1

Especificação inicial para validação com usuários reais

# 1. Objetivo do MVP

O TooJunto deverá permitir que um pequeno grupo de pessoas conhecidas
organize uma caixinha digital, acompanhe suas cotas e visualize a ordem
de contemplação.

Pergunta central de validação: As pessoas conseguem organizar e
participar de uma caixinha usando o TooJunto, com mais simplicidade e
transparência do que usando WhatsApp, caderno ou planilha?

# 2. Escopo do MVP 0.1

Jornada fundamental: Criar → Convidar → Entrar → Pagar → Registrar →
Sortear → Acompanhar.

# 3. Fora do Escopo do MVP 0.1

Integração automática com WhatsApp

Notificações automáticas

Suplentes automáticos

Substituição automática do gestor

Multas automáticas

Bloqueios automáticos

KYC e bureau de crédito

Open Finance

Chat interno

Login social

Autenticação 2FA

Aplicativo mobile nativo

Marketplace de grupos

Rating de participantes

White-label e API pública

Painel administrativo complexo

Esses itens permanecem como backlog/fases futuras e não fazem parte da
primeira validação.

# 4. Conceito de pagamento

O TooJunto não movimenta o dinheiro no MVP. O participante realiza o Pix
diretamente para o contemplado e o TooJunto registra a declaração do
pagamento.

Fluxo:

O sistema mostra o valor e os dados Pix do recebedor.

O participante copia a chave Pix e realiza o pagamento no aplicativo do
banco.

O participante retorna ao TooJunto e informa que pagou.

O comprovante pode ser anexado.

O gestor confirma ou rejeita a declaração.

# 5. Usuários do MVP

## 5.1 Gestor

Criar grupo

Definir valor e quantidade de participantes/ciclos

Convidar pessoas

Acompanhar participantes

Acompanhar pagamentos

Realizar o sorteio

Visualizar a situação do grupo

## 5.2 Participante

Aceitar convite

Visualizar o grupo

Visualizar valor da cota

Visualizar contemplações

Visualizar quem deve receber

Registrar pagamento

Acompanhar seu status

## 5.3 Administrador

Não será prioridade no primeiro protótipo. A operação inicial poderá ser
apoiada manualmente pela equipe do projeto.

# 6. Jornada principal

Criar grupo → Definir regras → Convidar pessoas → Participantes aceitam
→ Grupo completo → Realizar sorteio → Definir contemplação → Iniciar
ciclo → Pagamentos → Confirmar pagamentos → Contemplação liberada →
Próximo ciclo

# 7. Telas do MVP

## 01 --- Entrada

Logo TooJunto; mensagem curta; Entrar; Criar conta.

## 02 --- Criar conta

Nome, WhatsApp, e-mail e senha.

## 03 --- Minha página

Saudação, meus grupos, status, valor e botão para criar/abrir grupo.

## 04 --- Criar grupo

Nome, valor da cota, quantidade de pessoas, quantidade de meses e data
de início.

## 05 --- Convites

Link para convite, compartilhamento e lista de participantes.

## 06 --- Convite recebido

Dados do grupo e ações Aceitar/Recusar.

## 07 --- Meu grupo

Cota, participantes, ciclo atual, situação pessoal, próxima contemplação
e acessos.

## 08 --- Pagamento

Valor, recebedor, chave Pix, copiar Pix e informar pagamento.

## 09 --- Sorteio

Ação para realizar sorteio e tela com resultado da ordem.

## 10 --- Contemplação

Contemplado, valor, status dos pagamentos e acesso aos detalhes.

# 8. Modelo de dados inicial

# 9. Regras de negócio do MVP

RN-MVP-001 --- Um grupo é fechado e somente pessoas convidadas podem
participar.

RN-MVP-002 --- O gestor cria o grupo.

RN-MVP-003 --- Cada participante possui uma única posição no grupo.

RN-MVP-004 --- O sorteio define a ordem de contemplação.

RN-MVP-005 --- Depois do sorteio, a ordem não pode ser alterada pelo
usuário comum.

RN-MVP-006 --- O pagamento ocorre diretamente entre os participantes.

RN-MVP-007 --- O TooJunto registra a declaração de pagamento.

RN-MVP-008 --- O gestor pode confirmar ou rejeitar uma declaração.

RN-MVP-009 --- O sistema registra quem foi contemplado em cada ciclo.

RN-MVP-010 --- Todos os participantes conseguem visualizar o andamento
do grupo.

# 10. Processos inicialmente manuais

A operação manual é intencional: primeiro validamos o comportamento dos
usuários e só depois automatizamos os processos que realmente agregarem
valor.

# 11. Estratégia de validação

## MVP-ALPHA

Criar grupo → convidar → entrar → sorteio → visualizar resultado. Testa
se as pessoas entendem o produto.

## MVP-BETA

Adicionar pagamento → declaração → confirmação → ciclo → contemplação.
Testa o uso real.

## MVP-PILOTO

Colocar um grupo real em funcionamento e acompanhar toda a jornada.

# 12. Critérios de sucesso

Pergunta qualitativa: "Você usaria o TooJunto novamente?"

# 13. Primeiro experimento

# 14. Posicionamento inicial

TooJunto --- Sua caixinha, organizada e transparente.

Mensagem inicial sugerida: Crie um grupo com pessoas que você conhece.
Cada pessoa contribui todos os meses. O grupo define quem recebe a cada
mês.

# 15. Princípios de UX

Mobile-first.

Poucos elementos por tela.

Botões grandes e claros.

Linguagem simples.

Ícones acompanhados de texto.

Uma ação principal por tela.

Mínimo de digitação.

Evitar menus e funcionalidades desnecessárias.

Projetar pensando em pessoas com baixo letramento digital.

# 16. Próximas etapas do projeto

Detalhar o fluxo completo do usuário.

Desenhar os wireframes das 10 telas.

Detalhar as regras de negócio.

Validar o modelo de dados.

Definir API e arquitetura.

Escolher o stack tecnológico.

Criar a estrutura do projeto.

Implementar o MVP-ALPHA.

Testar com usuários reais.

Iterar antes de ampliar o escopo.

TOOJUNTO • MVP 0.1

  -----------------------------------------------------------------------
  Campo                               Informação
  ----------------------------------- -----------------------------------
  Produto                             TooJunto

  Versão                              MVP 0.1

  Objetivo                            Validar o uso real de uma caixinha
                                      digital por pequenos grupos de
                                      pessoas conhecidas.

  Prioridade                          Simplicidade + velocidade de
                                      lançamento

  Plataforma                          Web responsiva, com prioridade para
                                      celular

  Status                              Especificação inicial
  -----------------------------------------------------------------------

  \#   Capacidade                      MVP 0.1
  ---- ------------------------------- ---------
  1    Criar conta                     Sim
  2    Criar grupo                     Sim
  3    Convidar pessoas                Sim
  4    Aceitar convite                 Sim
  5    Registrar/confirmar pagamento   Sim
  6    Realizar sorteio                Sim
  7    Acompanhar grupo                Sim

  -----------------------------------------------------------------------
  Entidade                            Campos iniciais
  ----------------------------------- -----------------------------------
  USUARIO                             id; nome; email; telefone; senha;
                                      created_at

  GRUPO                               id; nome; gestor_id; valor_cota;
                                      quantidade_participantes;
                                      quantidade_ciclos; data_inicio;
                                      status; created_at

  PARTICIPANTE                        id; grupo_id; usuario_id;
                                      ordem_sorteio; status

  CICLO                               id; grupo_id; numero; data;
                                      contemplado_id; status

  PAGAMENTO                           id; ciclo_id; pagador_id;
                                      recebedor_id; valor; status;
                                      comprovante; data_pagamento

  CONTEMPLACAO                        id; ciclo_id; participante_id;
                                      valor; status; data
  -----------------------------------------------------------------------

  Processo                 Tratamento no MVP
  ------------------------ -------------------------------------
  Convite via WhatsApp     Manual, usando link/copiar mensagem
  Lembrete de pagamento    Manual
  Suplente                 Manual
  Resolver inadimplência   Manual
  Atendimento              Manual
  Disputas                 Manual
  Suporte ao usuário       Manual
  Administração            Manual

  Métrica                                    Objetivo inicial
  ------------------------------------------ ------------------
  Pessoas que aceitaram convite              \> 80%
  Pessoas que conseguiram entrar sem ajuda   \> 70%
  Pessoas que entenderam como pagar          \> 80%
  Pagamentos registrados corretamente        \> 90%
  Sorteio concluído                          100%
  Ciclo concluído                            100%
  Usuários que querem continuar              \> 70%

  -----------------------------------------------------------------------
  Experimento             Escala                  Objetivo
  ----------------------- ----------------------- -----------------------
  Experimento 1           1 grupo / 5--10 pessoas Completar pelo menos um
                                                  ciclo real

  Experimento 2           3 grupos / 15--30       Validar repetição e
                          pessoas                 identificar melhorias

  Experimento 3           10 grupos / 50--100     Validar operação em
                          pessoas                 pequena escala
  -----------------------------------------------------------------------

# 17. Atualização da visão --- MVP 0.2

Data da revisão: 28/09/2026.

## 17.1 Situação atual

O MVP 0.1 está funcionalmente homologado e implantado em STAGING/PILOTO
na VPS Hostinger. O desenvolvimento continua local; a VPS é usada para
homologação integrada e piloto controlado. Os fluxos já homologados
localmente foram reproduzidos com sucesso no staging.

A homologação do piloto evidenciou duas necessidades de produto:
comunicação operacional entre as etapas do Grupo e melhoria da nitidez
da logo em algumas condições de exibição.

## 17.2 Objetivo do MVP 0.2

Evoluir o TooJunto para comunicar mudanças relevantes de estado a
Gestores e Participantes, sem transformar a plataforma em chat ou
adicionar complexidade não validada.

O MVP 0.2 inclui:

-   migrations versionadas, backup/restore e deploy seguro em staging;
-   notificações in-app simples;
-   e-mail transacional para os eventos aprovados;
-   recusa explícita de convite, distinta de "Agora não";
-   notificações da formação do Grupo, sorteio, ciclos e pagamentos;
-   lembrete de pagamento próximo do prazo;
-   integração Landing Page → aplicação;
-   correção da nitidez/renderização da marca;
-   regressão, segurança e homologação final em staging.

## 17.3 Princípio de comunicação

Notificar somente quando existir informação nova relevante ou ação
necessária para o destinatário. Não notificar cliques, abertura de telas
ou estados intermediários sem consequência operacional.

O TooJunto continua sendo a fonte oficial do estado. O e-mail informa e
conduz o usuário de volta à aplicação.

## 17.4 Canais

Canais aprovados para o MVP 0.2:

-   notificação in-app;
-   e-mail transacional.

Ficam fora do MVP 0.2: WhatsApp automático, chat, respostas livres por
mensageria, push notification e SMS.

## 17.5 Fronteira do produto

O TooJunto continua sem movimentar ou custodiar dinheiro. Pagamentos
permanecem externos à plataforma e são apenas declarados/acompanhados no
sistema. Pix/Open Finance integrado, marketplace, reputação, aplicativo
nativo e painel administrativo complexo permanecem fora do MVP 0.2.

O princípio permanece: **menos é mais**. Nova funcionalidade
identificada durante a implementação vai para o backlog, salvo quando
necessária para cumprir uma User Story já aprovada.
