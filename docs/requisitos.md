TOOJUNTO

Documento de Requisitos do Produto

MVP 0.1 --- Validação Inicial

Objetivo deste documento

Definir os requisitos mínimos necessários para construir e testar o
TooJunto sem transformar o primeiro produto em um sistema grande. O foco
do MVP 0.1 é validar se pessoas conseguem organizar e participar de uma
caixinha digital com simplicidade e transparência.

# 1. Objetivo e escopo

O MVP 0.1 deverá permitir a criação de grupos fechados, entrada por
convite, definição da ordem de contemplação por sorteio, registro das
declarações de pagamento e acompanhamento do andamento do grupo.

Jornada principal:

Criar → Convidar → Entrar → Pagar → Registrar → Sortear → Acompanhar

## 1.1 Hipótese principal a validar

As pessoas conseguem organizar e participar de uma caixinha usando o
TooJunto, com mais simplicidade e transparência do que usando WhatsApp,
caderno ou planilha?

## 1.2 Escopo do MVP

Cadastro e autenticação básica.

Criação de grupo fechado pelo gestor.

Convite de participantes.

Aceite do convite e entrada no grupo.

Visualização de valor, participantes, ciclos e situação do grupo.

Sorteio da ordem de contemplação.

Registro de pagamento pelo participante.

Confirmação ou rejeição do pagamento pelo gestor.

Registro de contemplações e histórico básico do grupo.

# 2. Atores

# 3. Jornada principal

# 4. Requisitos funcionais

# 5. Regras de negócio

# 6. Requisitos não funcionais essenciais

# 7. Critérios de aceitação do MVP

Um usuário consegue criar sua conta e entrar sem auxílio técnico.

Um gestor consegue criar um grupo e compartilhar convites.

Um convidado consegue aceitar o convite e visualizar o grupo.

Um grupo completo consegue realizar um sorteio com resultado registrado.

Os participantes conseguem identificar claramente quem é o contemplado
do ciclo.

Um participante consegue registrar um pagamento sem que o dinheiro passe
pela plataforma.

O gestor consegue confirmar ou rejeitar o pagamento declarado.

Todos os participantes conseguem acompanhar o progresso do grupo.

O sistema não permite alterar silenciosamente uma ordem de sorteio já
finalizada.

Uma operação-piloto consegue ser realizada do início ao fim sem
intervenção de desenvolvimento.

# 8. Estados do domínio

## 8.1 Grupo

RASCUNHO → FORMANDO → SORTEIO → ATIVO → ENCERRADO

RASCUNHO: grupo ainda não foi disponibilizado para participantes.

FORMANDO: convites estão sendo aceitos.

SORTEIO: número de participantes atingido.

ATIVO: sorteio realizado e ciclos em andamento.

ENCERRADO: todos os ciclos concluídos.

## 8.2 Ciclo

ABERTO → EM_PAGAMENTO → CONTEMPLADO → CONCLUIDO

ABERTO: ciclo criado e contemplado identificado.

EM_PAGAMENTO: pagamentos estão sendo declarados/confirmados.

CONTEMPLADO: contemplação registrada.

CONCLUIDO: ciclo encerrado após o processamento previsto.

## 8.3 Pagamento

PENDENTE → DECLARADO → CONFIRMADO / REJEITADO

# 9. Dados mínimos

# 10. Fora do MVP 0.1

Integração automática com WhatsApp.

Notificações automáticas por WhatsApp/e-mail.

Substituto automático de participante.

Substituição automática de gestor.

Cálculo e aplicação automática de multas.

Bloqueios automáticos por inadimplência.

Movimentação de dinheiro, Pix integrado ou conta digital.

Open Finance.

KYC, consulta a birôs de crédito ou validações avançadas de identidade.

Chat interno.

Login social e 2FA.

Aplicativo nativo Android/iOS.

Marketplace público.

Avaliações/reputação.

White-label e API pública.

Painel administrativo complexo.

# 11. Backlog futuro

# 12. Estratégia de validação

## 12.1 Métricas iniciais

Aceitação de convites \> 80%.

Entrada no grupo sem ajuda \> 70%.

Compreensão do fluxo de pagamento \> 80%.

Pagamentos corretamente registrados \> 90%.

Sorteios concluídos: 100%.

Ciclos concluídos no piloto: 100%.

Usuários que desejam continuar usando: \> 70%.

Pergunta qualitativa principal: "Você usaria o TooJunto novamente?"

# 13. Rastreabilidade com a Visão MVP 0.1

# 14. Decisões pendentes antes do desenvolvimento

Confirmar a regra definitiva de contemplação do gestor (posição inicial
automática ou sorteio em igualdade com os demais).

Definir o formato técnico do convite (link/código) para o primeiro
piloto.

Definir se o comprovante de pagamento será opcional ou obrigatório no
piloto.

Definir stack tecnológica e ambiente de desenvolvimento.

Definir política de retenção e tratamento dos comprovantes de pagamento.

  Versão    0.1
  --------- ------------------------------------------------------
  Data      14 de setembro de 2026
  Status    Em validação
  Produto   TooJunto --- Sua caixinha, organizada e transparente

  -----------------------------------------------------------------------
  Ator                    Papel                   Principais ações
  ----------------------- ----------------------- -----------------------
  Gestor                  Responsável pelo grupo  Criar grupo, convidar
                                                  pessoas, acompanhar o
                                                  grupo e executar o
                                                  sorteio. A
                                                  confirmação/rejeição de
                                                  pagamento pertence ao
                                                  contemplado do ciclo.

  Participante            Membro do grupo         Aceitar convite,
                                                  consultar grupo, pagar
                                                  diretamente ao
                                                  contemplado, declarar
                                                  pagamento e acompanhar
                                                  sua situação.

  Administrador           Operação da plataforma  Não é prioridade no
                                                  MVP; suporte e
                                                  intervenções poderão
                                                  ser feitos manualmente.
  -----------------------------------------------------------------------

  -----------------------------------------------------------------------
  Etapa                   Tela/ação               Descrição
  ----------------------- ----------------------- -----------------------
  01                      Entrada                 Usuário acessa o
                                                  TooJunto e cria uma
                                                  conta ou entra.

  02                      Criar grupo             Gestor informa nome,
                                                  valor da cota,
                                                  quantidade de
                                                  participantes, ciclos e
                                                  início.

  03                      Convidar                Gestor gera/compartilha
                                                  convite com as pessoas
                                                  do grupo.

  04                      Entrar                  Convidado aceita o
                                                  convite e passa a
                                                  integrar o grupo.

  05                      Preparar                Quando o grupo estiver
                                                  completo, fica pronto
                                                  para o sorteio.

  06                      Sortear                 O gestor executa o
                                                  sorteio e a ordem fica
                                                  registrada.

  07                      Pagar                   Em cada ciclo, os
                                                  participantes pagam
                                                  diretamente ao
                                                  contemplado.

  08                      Registrar               Participante informa
                                                  que realizou o
                                                  pagamento; comprovante
                                                  pode ser anexado.

  09                      Confirmar               O contemplado do ciclo
                                                  confirma ou rejeita a
                                                  declaração destinada a
                                                  ele.

  10                      Acompanhar              Todos consultam o
                                                  progresso do grupo e as
                                                  contemplações.
  -----------------------------------------------------------------------

  -----------------------------------------------------------------------
  ID                      Requisito               Descrição
  ----------------------- ----------------------- -----------------------
  RF-001                  Cadastro de usuário     Permitir criar conta
                                                  com nome, e-mail,
                                                  telefone e senha.

  RF-002                  Login                   Permitir autenticação
                                                  de usuário cadastrado.

  RF-003                  Criar grupo             Permitir ao gestor
                                                  criar grupo informando
                                                  nome, valor da cota,
                                                  participantes,
                                                  quantidade de ciclos e
                                                  data de início.

  RF-004                  Convite                 Permitir ao gestor
                                                  gerar um convite para
                                                  cada participante.

  RF-005                  Aceitar convite         Permitir que usuário
                                                  convidado aceite o
                                                  convite e seja
                                                  associado ao grupo.

  RF-006                  Visualizar grupo        Exibir participantes,
                                                  valor da cota, ciclos,
                                                  status e progresso.

  RF-007                  Preparar sorteio        Indicar quando o grupo
                                                  estiver apto para o
                                                  sorteio.

  RF-008                  Realizar sorteio        Executar o sorteio e
                                                  registrar a ordem de
                                                  contemplação.

  RF-009                  Registrar ciclo         Criar/abrir o ciclo
                                                  correspondente à
                                                  próxima contemplação.

  RF-010                  Registrar pagamento     Permitir que
                                                  participante declare
                                                  pagamento realizado ao
                                                  contemplado e,
                                                  opcionalmente, anexe
                                                  comprovante.

  RF-011                  Confirmar pagamento     Permitir ao contemplado
                                                  do ciclo confirmar ou
                                                  rejeitar uma declaração
                                                  de pagamento destinada
                                                  a ele.

  RF-012                  Registrar contemplação  Registrar quem foi
                                                  contemplado, em qual
                                                  ciclo, valor e data.

  RF-013                  Histórico e progresso   Permitir consultar
                                                  ciclos anteriores,
                                                  pagamentos registrados
                                                  e contemplações do
                                                  grupo.
  -----------------------------------------------------------------------

  -----------------------------------------------------------------------
  ID                                  Regra
  ----------------------------------- -----------------------------------
  RN-001                              Grupos são fechados e acessíveis
                                      somente por convite.

  RN-002                              O gestor é responsável pela criação
                                      e condução operacional do grupo.

  RN-003                              O gestor também pode participar do
                                      grupo e ocupa uma vaga de
                                      participante.

  RN-004                              O grupo somente pode iniciar o
                                      sorteio quando estiver completo.

  RN-005                              A ordem de contemplação é definida
                                      pelo sorteio e deve ficar
                                      registrada.

  RN-006                              Após a finalização do sorteio, a
                                      ordem não pode ser alterada por
                                      usuários comuns.

  RN-007                              O pagamento não passa pelo
                                      TooJunto. O participante paga
                                      diretamente ao contemplado,
                                      preferencialmente via Pix.

  RN-008                              O TooJunto registra somente a
                                      declaração do pagamento e seu
                                      status de confirmação.

  RN-009                              O contemplado do ciclo pode
                                      confirmar ou rejeitar pagamentos
                                      destinados a ele; ser gestor não
                                      concede privilégio especial quando
                                      ele não é o contemplado.

  RN-010                              Cada ciclo possui um único
                                      contemplado.

  RN-011                              O sistema deve registrar data/hora
                                      das operações críticas de sorteio,
                                      pagamento e confirmação.

  RN-012                              Não haverá cálculo automático de
                                      multa, bloqueio ou substituição no
                                      MVP 0.1.

  RN-013                              Não haverá integração automática
                                      com WhatsApp ou banco no MVP 0.1.

  RN-014                              A regra histórica de posição
                                      inicial do gestor deve ser tratada
                                      como decisão de produto a confirmar
                                      antes do piloto; o MVP não deve
                                      escondê-la ou alterá-la
                                      silenciosamente.
  -----------------------------------------------------------------------

  -----------------------------------------------------------------------
  ID                      Categoria               Requisito
  ----------------------- ----------------------- -----------------------
  RNF-001                 Mobile-first            A experiência deve
                                                  funcionar
                                                  prioritariamente em
                                                  smartphones e telas
                                                  pequenas.

  RNF-002                 Simplicidade            Uma ação principal por
                                                  tela, linguagem
                                                  simples, botões grandes
                                                  e poucos elementos.

  RNF-003                 Acessibilidade prática  Usar ícones
                                                  acompanhados de texto,
                                                  contraste adequado e
                                                  mensagens de erro
                                                  claras.

  RNF-004                 Segurança básica        Senhas armazenadas de
                                                  forma segura,
                                                  comunicação protegida e
                                                  controle de acesso por
                                                  grupo.

  RNF-005                 Privacidade             Usuário somente
                                                  visualiza informações
                                                  dos grupos dos quais
                                                  participa, conforme seu
                                                  papel.

  RNF-006                 Rastreabilidade         Sorteio e alterações
                                                  relevantes devem
                                                  possuir registro de
                                                  data/hora e usuário
                                                  responsável.

  RNF-007                 Responsividade          Telas principais devem
                                                  responder rapidamente
                                                  em condições normais de
                                                  uso.
  -----------------------------------------------------------------------

  -----------------------------------------------------------------------
  Entidade                            Campos mínimos
  ----------------------------------- -----------------------------------
  USUARIO                             id, nome, email, telefone,
                                      senha_hash, created_at

  GRUPO                               id, nome, gestor_id, valor_cota,
                                      quantidade_participantes,
                                      quantidade_ciclos, data_inicio,
                                      status, created_at

  PARTICIPANTE                        id, grupo_id, usuario_id,
                                      ordem_sorteio, status

  CICLO                               id, grupo_id, numero, data,
                                      contemplado_id, status

  PAGAMENTO                           id, ciclo_id, pagador_id,
                                      recebedor_id, valor, status,
                                      comprovante, data_pagamento

  CONTEMPLACAO                        id, ciclo_id, participante_id,
                                      valor, status, data
  -----------------------------------------------------------------------

  -----------------------------------------------------------------------
  Prioridade                          Item
  ----------------------------------- -----------------------------------
  Pós-MVP 1                           Notificações e lembretes
                                      automáticos.

  Pós-MVP 2                           Gestão de inadimplência, multas e
                                      substitutos.

  Pós-MVP 3                           Integração Pix/Open Finance, caso
                                      validada e juridicamente adequada.

  Pós-MVP 4                           Aplicativo nativo/PWA mais
                                      completo.

  Pós-MVP 5                           Painel administrativo e
                                      indicadores.

  Pós-MVP 6                           Mecanismos avançados de segurança,
                                      identidade e prevenção a fraude.

  Pós-MVP 7                           Recursos de escala: marketplace,
                                      reputação, white-label e API.
  -----------------------------------------------------------------------

  -----------------------------------------------------------------------
  Etapa             Escala            Teste             Objetivo
  ----------------- ----------------- ----------------- -----------------
  MVP-ALPHA         1 grupo / 5--10   Criar → convidar  Validar
                    pessoas           → entrar →        compreensão e
                                      sortear →         fluxo.
                                      visualizar
                                      resultado.

  MVP-BETA          3 grupos / 15--30 Adicionar         Validar uso
                    pessoas           pagamentos e      recorrente.
                                      confirmações
                                      reais.

  MVP-PILOT         Até 10 grupos /   Operação real     Validar valor
                    50--100 pessoas   acompanhada.      percebido e
                                                        intenção de
                                                        continuidade.
  -----------------------------------------------------------------------

  Elemento da Visão                      Requisitos relacionados
  -------------------------------------- ---------------------------
  Visão: Criar conta                     RF-001, RF-002
  Visão: Criar grupo                     RF-003
  Visão: Convidar pessoas                RF-004, RF-005
  Visão: Registrar/confirmar pagamento   RF-010, RF-011
  Visão: Rodar sorteio                   RF-007, RF-008
  Visão: Acompanhar grupo                RF-006, RF-012, RF-013
  Princípio: simplicidade                RNF-001, RNF-002, RNF-003
  Princípio: não movimentar dinheiro     RN-007, RN-008

# 18. Requisitos aprovados --- MVP 0.2

Data da revisão: 28/09/2026.

## 18.1 Regras gerais de notificações

-   Todo evento operacional relevante gera notificação somente para os
    usuários que precisam conhecer ou agir sobre o acontecimento.
-   Para os eventos aprovados, o MVP 0.2 utiliza notificação in-app e
    e-mail transacional.
-   O e-mail deve ser curto e possuir uma chamada principal para retorno
    ao TooJunto.
-   Falha no envio de e-mail não pode reverter uma operação de domínio
    já concluída.
-   Notificações pertencem ao usuário destinatário e não podem ser
    consultadas por outro usuário.
-   Não gerar mensagens para simples abertura de telas,
    criação/compartilhamento do link de convite ou estados
    intermediários sem informação nova.
-   "Agora não" não representa recusa. O MVP 0.2 introduz a ação
    explícita "Não quero participar", persistindo a recusa.
-   WhatsApp automático, chat, push notification, SMS e preferências
    avançadas de canais ficam fora do MVP 0.2.

## 18.2 Matriz oficial de eventos e notificações

  ---------------------------------------------------------------------------
  Evento         Destinatário    In-app         E-mail         Ação principal
  -------------- --------------- -------------- -------------- --------------
  Convite aceito Gestor          Sim            Sim            Ver grupo

  Convite        Gestor          Sim            Sim            Ver grupo
  recusado

  Grupo completo Gestor          Sim            Sim            Fazer sorteio

  Grupo completo Participantes   Sim            Sim            Ver grupo

  Grupo          Participantes   Sim            Sim            Ver meus
  cancelado                                                    grupos

  Sorteio        Todos os        Sim            Sim            Ver resultado
  realizado      integrantes

  Ciclo iniciado Participantes   Sim            Sim            Ver ciclo
                 do grupo

  Pagamento      Pagador ainda   Sim            Sim            Ver pagamento
  próximo do     pendente
  prazo

  Pagamento      Contemplado do  Sim            Sim            Confirmar ou
  informado      ciclo                                         rejeitar

  Pagamento      Pagador         Sim            Sim            Ver grupo
  confirmado

  Pagamento      Pagador         Sim            Sim            Ver pagamento
  rejeitado

  Todos os       Contemplado     Sim            Sim            Ver ciclo
  pagamentos
  confirmados

  Ciclo          Participantes   Sim            Sim            Ver próximo
  concluído /    do grupo                                      ciclo
  próximo ciclo
  iniciado

  Grupo          Todos os        Sim            Sim            Ver grupo
  encerrado      integrantes
  ---------------------------------------------------------------------------

## 18.3 Regras complementares

O contemplado do ciclo continua sendo a autoridade para
confirmar/rejeitar os pagamentos destinados a ele. O gestor somente
recebe ou executa ações de pagamento quando outra regra funcional
explicitamente o autorizar; o papel de gestor isoladamente não concede
acesso às operações de outro contemplado.

Os detalhes de persistência, idempotência e entrega são responsabilidade
da arquitetura e não alteram as regras financeiras existentes.
