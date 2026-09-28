**TOOJUNTO**

**Plano de Desenvolvimento do MVP 0.1**

*Plano técnico, sprints, User Stories e ordem de implementação*

  -------------------------------------------------------------------------------
  **Campo**   **Valor**
  ----------- -------------------------------------------------------------------
  Versão      0.14

  Data        28 de setembro de 2026

  Status      MVP 0.1 homologado e implantado em STAGING/PILOTO; MVP 0.2 com
              escopo e roadmap aprovados para execução.

  Objetivo    Construir, testar e colocar o MVP em piloto com o menor escopo
              possível, preservando simplicidade para usuários com baixo
              letramento digital.
  -------------------------------------------------------------------------------

# 1. Objetivo do desenvolvimento

Entregar uma versão funcional do TooJunto capaz de executar a jornada
completa:

**Criar → Convidar → Entrar → Pagar → Registrar → Sortear → Acompanhar**

O desenvolvimento deve priorizar validação com usuários reais, evitando
funcionalidades que não sejam necessárias para testar a hipótese
principal do produto.

# 2. Estratégia de desenvolvimento

-   Construção incremental e vertical: cada sprint entrega uma parte
    utilizável.
-   Priorizar primeiro o caminho feliz do usuário.
-   Testar as regras críticas desde o início.
-   Evitar perfeccionismo visual antes dos testes de usabilidade.
-   Usar dados de teste controlados até o piloto.
-   Publicar em staging antes de produção.
-   Corrigir problemas que bloqueiem a jornada antes de adicionar
    funcionalidades.
-   Fluxo de trabalho: Backlog → Sprint → User Story → Card/Prompt →
    /dev-backend (análise interna, implementação, testes e revisão) →
    /dev-frontend (análise interna, implementação, testes e revisão) →
    Homologação do PO → Documentação → Commit/Push manual → Done. Os
    agents só interrompem o fluxo antes da implementação quando
    identificarem mudança arquitetural, alteração estrutural de banco,
    nova dependência, mudança de regra de negócio, alteração de contrato
    existente com impacto em outras funcionalidades ou trabalho fora do
    escopo.
-   Manter o MVP simples e evitar tecnologia ou funcionalidades sem
    problema concreto a resolver.

# 3. Ordem de implementação

  -----------------------------------------------------------------------------------------
  **Prioridade**   **Bloco**       **Resultado**
  ---------------- --------------- --------------------------------------------------------
  P0               Fundação        Repositório, ambientes, banco, autenticação e base
                                   técnica.

  P1               Usuários        Cadastro, login, sessão e proteção de rotas.

  P1               Grupos          Criar, listar, consultar, editar e cancelar grupos.

  P1               Convites        Geração, compartilhamento, aceite/recusa e entrada no
                                   grupo.

  P1               Participantes   Formação do grupo e controle do limite de participantes.

  P1               Sorteio         Preparação, execução e registro da ordem.

  P1               Ciclos          Contemplação e progresso.

  P1               Pagamentos      Declaração de pagamento e confirmação/rejeição, sem
                                   movimentação financeira pelo TooJunto.

  P1               Histórico       Adiado para MVP 0.3; reavaliar quando novas
                                   funcionalidades justificarem uma visão histórica
                                   dedicada.

  P2               Polimento       Usabilidade, mensagens, acessibilidade e correções.

  P2               Piloto          Deploy, monitoramento e suporte.
  -----------------------------------------------------------------------------------------

# 4. Status das User Stories

  -------------------------------------------------------------------------------
  **Sprint**   **US**     **Funcionalidade**                       **Status**
  ------------ ---------- ---------------------------------------- --------------
  Sprint 1     US-001     Criar conta                              DONE

  Sprint 1     US-002     Login, sessão, proteção de rotas e       DONE
                          logout

  Sprint 2     US-003     Criar Grupo                              DONE

  Sprint 2     US-003.1   Consultar Meus Grupos e detalhes         DONE

  Sprint 2     US-004     Gerenciar Grupo --- editar e cancelar    DONE

  Sprint 3     US-005     Convidar participantes                   DONE

  Sprint 3     US-006     Aceitar ou recusar convite / entrar no   DONE
                          Grupo

  Sprint 3     US-007     Visualizar participantes e formação do   DONE
                          Grupo

  Sprint 4     US-008     Preparar sorteio                         DONE

  Sprint 4     US-009     Realizar sorteio e registrar ordem       DONE

  Sprint 5     US-010     Ciclos, contemplação e progresso         DONE

  Sprint 6     US-011     Registrar pagamento                      DONE

  Sprint 6     US-012     Confirmar ou rejeitar pagamento          DONE

  Sprint 7     US-013     Histórico e acompanhamento               ADIADA --- MVP
                                                                   0.3

  Sprint 7     US-014A    Refinamento de convites e cadastro       DONE

  Sprint 7     US-014B    Criação e integridade do Grupo           DONE

  Sprint 7     US-014C    Simplificação da tela "Em andamento"     DONE

  Sprint 7     US-014D    Regressão e homologação final do MVP 0.1 DONE

  Sprint 7     US-014E    Identidade visual TooJunto para o piloto DONE

  Sprint 7     US-014F    Simplificação final da navegação para o  DONE
                          piloto
  -------------------------------------------------------------------------------

Observação: a numeração das User Stories passa a ser a referência
operacional do roadmap. A US-003.1 foi incorporada durante o Sprint 2
para permitir navegação persistente em "Meus Grupos" e acesso aos
detalhes após nova sessão/F5.

# 5. Sprints atualizadas

  -----------------------------------------------------------------------------------------------
  **Sprint**   **Duração   **Objetivo**    **Entrega / situação**
               alvo**
  ------------ ----------- --------------- ------------------------------------------------------
  Sprint 0     2--3 dias   Fundação        DONE --- Git, estrutura, ambiente local, PostgreSQL em
                                           Docker e base de testes.

  Sprint 1     4--5 dias   Autenticação    DONE --- cadastro, login, sessão, rotas protegidas e
                                           logout.

  Sprint 2     4--5 dias   Grupos          DONE --- criar, listar, consultar detalhes, editar e
                                           cancelar.

  Sprint 3     4--5 dias   Convites e      DONE --- US-005, US-006 e US-007 concluídas, testadas
                           participantes   e homologadas.

  Sprint 4     4--5 dias   Sorteio         DONE --- US-008 e US-009 concluídas, testadas e
                                           homologadas.

  Sprint 5     4--5 dias   Ciclos e        DONE --- US-010 concluída, testada e homologada.
                           contemplação

  Sprint 6     5--7 dias   Pagamentos      DONE --- US-011 e US-012 concluídas, testadas e
                                           homologadas.

  Sprint 7     4--5 dias   Integração e UX DONE --- US-013 descartada/adiada para MVP 0.3;
                                           US-014A/B/C/D/E/F concluídas; regressão, identidade
                                           visual, navegação final e homologação ponta a ponta
                                           aprovadas.

  Sprint 8     3--5 dias   Piloto          PRÓXIMO --- NÃO INICIADO. Preparação do ambiente real
                                           e execução do primeiro piloto controlado.
  -----------------------------------------------------------------------------------------------

Estimativa total de referência: aproximadamente 5--7 semanas de
desenvolvimento enxuto, sujeita a revisão conforme o aprendizado obtido
durante a implementação e os testes com usuários.

# 6. Sprints concluídas

## Sprint 0 --- Fundação --- DONE

-   Repositório Git e estrutura frontend/backend criados.
-   Ambiente local configurado.
-   PostgreSQL 16 executando em Docker.
-   Variáveis de ambiente e testes básicos configurados.
-   Base técnica pronta para desenvolvimento incremental.

Observação técnica: migrations versionadas permanecem como dívida
técnica; o ambiente atual ainda utiliza criação/sincronização de tabelas
sem Alembic.

## Sprint 1 --- Autenticação --- DONE

-   US-001 --- Cadastro de usuário.
-   US-002 --- Login, token/sessão, proteção de rotas e logout.
-   Hash seguro de senha e JWT.
-   Frontend de autenticação integrado ao Backend.
-   Homologação manual aprovada.
-   30 testes automatizados aprovados ao encerramento do Sprint 1.

## Sprint 2 --- Grupos --- DONE

-   US-003 --- Criar Grupo.
-   US-003.1 --- Consultar Meus Grupos e detalhes.
-   US-004 --- Gerenciar Grupo: editar e cancelar.
-   Home transformada em "Meus Grupos", válida para Gestor e
    Participante.
-   Gestor é automaticamente participante do grupo e ocupa uma vaga.
-   quantidade_ciclos = quantidade_participantes no MVP 0.1.
-   valor_premio calculado pelo Backend: valor_cota ×
    quantidade_participantes.
-   Cancelamento lógico com status CANCELADO, preservando histórico.
-   Somente Gestor de grupo em RASCUNHO pode editar ou cancelar.
-   Detalhes persistentes: após F5, o Frontend mantém somente o ID e
    recarrega os dados do Backend.
-   Backend: 77/77 testes aprovados.
-   Frontend: 19/19 testes aprovados e build de produção aprovado.
-   Homologação manual do PO aprovada.

Critério de saída atingido: usuário autenticado consegue criar um grupo,
encontrá-lo novamente em Meus Grupos, consultar seus detalhes e, quando
Gestor de um grupo em RASCUNHO, editar ou cancelar.

# 7. Sprint 3 --- Convites e participantes --- DONE

Objetivo: permitir que um Gestor forme o grupo convidando outros
usuários e que estes possam aceitar ou recusar a participação.

-   US-005 --- Convidar participantes --- DONE.

Backend: convite único e reutilizável por Grupo, token
criptograficamente seguro, operação idempotente e autorização exclusiva
do Gestor proprietário.

Segurança: grupo inexistente, participante não gestor e usuário externo
recebem resposta 404 indistinguível no endpoint de convite, evitando
enumeração de grupos privados.

Frontend: ação "Convidar pessoas" disponível somente para Gestor de
Grupo RASCUNHO; compartilhamento via Web Share API e fallback para
copiar link.

Contrato: POST /groups/{group_id}/invite.

Backend: 90/90 testes aprovados após correção e revisão final.

Frontend: 28/28 testes aprovados; TypeScript e build Vite aprovados.

Homologação manual do PO aprovada: geração, cópia do link e
compartilhamento real via WhatsApp pelo compartilhamento nativo do
sistema operacional.

US-006 --- Aceitar ou recusar convite / entrar no Grupo --- DONE.

Backend: GET /invites/{token} público com exposição mínima e POST
/invites/{token}/accept protegido por JWT; aceite cria Participante
ATIVO sem ordem de sorteio.

Regras Backend: validação de status, capacidade, duplicidade e Gestor;
toda associação persistida em Participante ocupa vaga, inclusive ATIVO e
INATIVO.

Concorrência: bloqueio pessimista do Grupo com FOR UPDATE protege a
última vaga; status e capacidade são revalidados dentro da transação.

Privacidade: token inválido, Grupo indisponível e Grupo lotado recebem
resposta pública uniforme 404; nenhuma informação do Gestor ou dos
participantes é exposta.

Frontend: abertura direta de /invites/{token}, preservação do convite
durante Login/Cadastro, retorno automático ao convite sem aceite
automático, ação "Agora não" sem persistência e "Ver Grupo" após aceite.

Frontend sem React Router nesta US; a própria URL é a fonte do token e o
fluxo é reconstruído após recarga.

Backend: 114/114 testes aprovados após implementação e revisão final.

Frontend: 41/41 testes aprovados após correção de assincronismo;
TypeScript e build Vite aprovados.

Homologação manual do PO aprovada: convite público exibido corretamente,
proteção contra Gestor/participante duplicado validada e fluxo real de
entrada testado.

Nenhum endpoint de recusa foi criado; recusar significa apenas sair do
fluxo sem alteração de domínio.

-   Gerar convite único.
-   Disponibilizar forma simples de compartilhamento.
-   US-007 --- Exibir participantes e progresso de formação do grupo ---
    DONE.
-   Backend: formação incorporada ao GET /groups/{group_id}, com
    quantidade atual, limite, vagas disponíveis e lista mínima de
    participantes contendo nome e papel. Gestor aparece primeiro e
    identificado como GESTOR.
-   Regras Backend: Gestor e Participante ATIVO podem consultar; usuário
    externo ou inativo recebe 404. Toda associação persistida em
    Participante ocupa vaga, inclusive INATIVO. Quantidades e vagas são
    calculadas exclusivamente pelo Backend.

Frontend: formação integrada à tela existente de detalhes, com
quantidade, limite, nomes, papéis e mensagem de vagas; ações exclusivas
do Gestor permanecem ocultas para Participantes. Backend: 116/116 testes
aprovados. Frontend: 46/46 testes aprovados e build de produção
aprovado. Homologação manual do PO aprovada nos perfis Gestor e
Participante. Commit 102969d publicado na main. Critério de saída
atingido: Gestor convida, Participante entra e ambos visualizam
corretamente a formação do Grupo.

# 8. Sprint 4 --- Sorteio --- DONE

-   US-008 --- Preparar sorteio quando o grupo estiver completo ---
    DONE.
-   Backend: criado POST /groups/{group_id}/prepare-draw, exclusivo do
    Gestor proprietário. A preparação valida, sob lock transacional, o
    estado e a formação completa antes de alterar o Grupo para SORTEIO.
    O preenchimento da última vaga não prepara automaticamente o
    sorteio.
-   Regra de negócio registrada para a US-009: a 1ª posição da ordem de
    contemplação é reservada ao Gestor; as posições 2..N serão sorteadas
    aleatoriamente entre os demais participantes. A US-008 não atribui
    nem persiste posições e não executa o sorteio.
-   Ajuste de UX: GET /groups passou a retornar vagas_disponiveis sem
    consultas adicionais por Grupo. Na tela Meus Grupos, RASCUNHO com
    vagas é exibido como "Em formação"; RASCUNHO sem vagas como "Grupo
    completo"; SORTEIO como "Pronto para sorteio"; e CANCELADO como
    "Cancelado". "Grupo completo" é apenas representação de interface,
    não um novo status de domínio.
-   Validação: Backend 125/125 testes aprovados. Frontend 52/52 testes
    aprovados, TypeScript e build de produção aprovados. Homologação
    manual do PO concluída, incluindo a sinalização visual dos estados
    em Meus Grupos.
-   US-009 --- Realizar sorteio e registrar ordem --- DONE.
-   Backend: criado POST /groups/{group_id}/draw, exclusivo do Gestor e
    permitido apenas para Grupo em SORTEIO. A posição 1 pertence ao
    Gestor e as posições 2..N são sorteadas aleatoriamente entre os
    demais participantes. A ordem definitiva é persistida no campo
    existente Participante.ordem_sorteio, sem alteração estrutural de
    banco.
-   Calendário: GET /groups/{id} disponibiliza aos integrantes
    autorizados posição, nome, papel e data prevista de recebimento. A
    data é derivada de data_inicio + (posição - 1) × 30 dias corridos,
    sem duplicação no banco.
-   Integridade e segurança: sorteio executado uma única vez em
    transação protegida contra concorrência; nova tentativa é bloqueada.
    Participantes podem consultar o resultado, mas somente o Gestor pode
    executar o sorteio. Usuários externos permanecem protegidos pelas
    regras de privacidade existentes.
-   Frontend: ação "Realizar sorteio" exibida somente ao Gestor quando
    disponível, com confirmação do caráter definitivo. Após a execução,
    Gestor e Participantes visualizam a mesma ordem persistida e o
    estado do Grupo após o sorteio. O frontend apenas formata as datas
    recebidas do Backend; não recalcula ordem nem calendário.

UX atualizada posteriormente no refinamento para piloto: o status ATIVO
é apresentado como "Em andamento", com badge azul e texto explícito.
"Grupo concluído" usa badge laranja. As mudanças relevantes de status
não dependem somente da cor.

# 9. Sprint 5 --- Ciclos e contemplação --- DONE

-   US-010 --- Criar e acompanhar ciclos conforme a ordem sorteada.
-   Identificar contemplado do ciclo.
-   Registrar contemplação.
-   Mostrar ciclo atual e progresso.
-   Permitir consulta de ciclos anteriores.
-   Controlar estados do ciclo.

Critério de saída: usuário entende quem recebe, em qual ciclo e qual o
progresso do grupo.

Critério de saída atingido: após o sorteio, os integrantes conseguem
acompanhar o calendário de contemplações e o ciclo atual sem antecipar a
lógica de pagamentos.

Commit da US-010: e92ed33 --- feat: add group cycles and progress.

Homologação manual do PO aprovada em 22 de setembro de 2026 para Gestor
e Participante.

Validação: Backend 131/131 testes aprovados. Frontend 58/58 testes
aprovados, TypeScript e build de produção aprovados.

Frontend: a tela de detalhes consulta o endpoint de ciclos após o
sorteio e apresenta "Ciclo X de N", contemplado, data prevista e
calendário completo. ATUAL recebe maior destaque visual; os estados
mantêm texto explícito e não dependem somente de cor.

Segurança: Gestor e Participantes autorizados visualizam o mesmo
progresso; usuários externos recebem 404 e integrantes recebem 409
quando o Grupo ainda não possui sorteio disponível.

Regra crítica: nenhum ciclo avança automaticamente pela data e não foi
criado mecanismo manual de "Avançar ciclo". O avanço futuro dependerá da
conclusão das obrigações de pagamento.

Progresso: imediatamente após o sorteio, o ciclo 1 permanece ATUAL e os
demais ficam PROXIMO. O estado CONCLUIDO está previsto no contrato, mas
somente será utilizado quando as obrigações de pagamento forem
integradas nas US-011/US-012.

Calendário: a data prevista continua seguindo data_inicio + (ciclo - 1)
× 30 dias corridos, preservando a regra aprovada na US-009.

Regras de domínio: os ciclos são derivados da ordem_sorteio e da data de
início, sem alteração estrutural do banco. A posição sorteada define o
ciclo e o contemplado correspondente.

Backend: criado GET /groups/{group_id}/cycles para disponibilizar ciclo
atual, total de ciclos, contemplado e data prevista do ciclo atual, além
do calendário completo com participante, papel e situação.

US-010 --- Ciclos, contemplação e progresso do Grupo --- DONE.

# 10. Sprint 6 --- Pagamentos --- DONE

-   US-011 --- Registrar pagamento --- DONE.
-   Mostrar contemplado, pagador, valor, prazo e situação da obrigação.
-   Pagamento realizado diretamente entre participante e contemplado,
    sem movimentação financeira pelo TooJunto.
-   Registrar declaração do próprio pagamento como
    AGUARDANDO_CONFIRMACAO, sem permitir duplicidade.
-   Não solicitar comprovante, valor digitado, chave Pix, banco, código
    de transação ou observação no MVP.
-   US-012 --- Confirmar ou rejeitar pagamento pelo contemplado ---
    DONE.
-   Atualizar progresso e rastreabilidade.

Critério de saída: ciclo registra e confirma pagamentos sem movimentação
financeira pelo TooJunto.

US-011 --- Resultado da implementação e homologação.

Backend: GET e POST /groups/{group_id}/cycles/{cycle_number}/payments.
Nesta etapa, somente o ciclo atual (ciclo 1) está disponível. As
respostas incluem pagador_id (Participante) e pagador_usuario_id
(Usuário), permitindo ao frontend identificar com segurança a obrigação
própria.

Persistência: reutilizadas as tabelas ciclos e pagamentos. O pagamento
declarado fica AGUARDANDO_CONFIRMACAO. O backend define valor e
contemplado; o participante não informa valor manualmente. O contemplado
não possui obrigação de pagar a si próprio.

Prazo e transparência: pagamento esperado até 5 dias antes da data
prevista do ciclo. A API fornece situação derivada e contagem de dias
para exibir PENDENTE, alerta laranja na janela crítica,
AGUARDANDO_CONFIRMACAO e ATRASADO. A confirmação futura pertence à
US-012.

Frontend: a tela de detalhes exibe coletivamente as obrigações do ciclo.
A ação "Informar pagamento" aparece somente para a obrigação do usuário
autenticado. A confirmação foi ajustada após homologação para modal
centralizada, evitando confirmação fora da área visível e múltiplos
cliques.

Usabilidade: modal com Cancelar e "Sim, já paguei", bloqueio durante o
POST, feedback de erro, atualização para "Aguardando confirmação", foco
inicial, navegação por Tab, Escape e retorno de foco ao fechar.

Testes: backend 134/134; frontend 65/65; TypeScript e build de produção
aprovados. Homologação manual do PO concluída em 22/09/2026.

Dívida técnica: DT-012 registrada para avaliar constraint única de
pagamento por (ciclo_id, pagador_id). A proteção atual usa lock
transacional no fluxo da API e não bloqueia o MVP.

# 11. Sprint 7 --- Integração, refinamento e UX --- DONE

-   US-013 --- Histórico e acompanhamento --- DESCARTADA PELO PO /
    ADIADA PARA MVP 0.3.
-   Executar jornada completa de ponta a ponta.
-   Corrigir navegação e mensagens.
-   Validar mobile-first e acessibilidade.
-   Testar estados vazios, erros e carregamento.
-   Executar testes E2E.
-   Corrigir bugs críticos.

## US-013 --- Decisão de produto

Durante a homologação, o PO concluiu que uma seção dedicada de Histórico
duplicava informações já disponíveis na interface e aumentava a
complexidade para o público de baixo letramento digital. As alterações
experimentais da US-013 foram revertidas. Histórico não é critério de
liberação do MVP 0.1 e fica no backlog do MVP 0.3 para reavaliação
quando novas funcionalidades justificarem sua existência.

## US-014 --- Refinamento para o piloto --- DONE

US-014A --- Convites e cadastro --- DONE. Telefone obrigatório no
cadastro; regra de senha de 8 a 128 caracteres explicitada; confirmação
de senha; convite identifica Gestor e Grupo; compartilhamento usa URL
completa; tela pública orienta criação de conta; manager_name adicionado
de forma aditiva ao contrato público.

US-014B --- Criação e integridade do Grupo --- DONE. Data inicial
anterior a hoje recebe mensagem específica; nome do Grupo é único por
Gestor enquanto o grupo não estiver ENCERRADO/CANCELADO, desconsiderando
caixa e espaços adicionais; Gestores diferentes podem usar o mesmo nome;
nome pode ser reutilizado após encerramento/cancelamento; cards exibem o
nome do Gestor; gestor_nome foi adicionado aos contratos necessários;
após o primeiro aceite de outro participante, as condições do Grupo
tornam-se imutáveis; a participação automática do Gestor não bloqueia
edição; cancelamento preserva as regras existentes.

US-014C --- Simplificação da tela "Em andamento" --- DONE. Ciclo atual
virou o bloco operacional principal; pagamentos e progresso foram
consolidados; "Calendário dos ciclos" e "Ordem de recebimento" foram
unificados em "Próximos recebimentos"; Regras e Participantes ficam
recolhidos por padrão; redundâncias foram removidas e as ações
financeiras preservadas.

US-014D --- Regressão e homologação final --- DONE. Backend 157/157;
Frontend 86/86; TypeScript, build de produção e git diff --check
aprovados; contratos, autorização/segurança e responsividade aprovados;
bugs bloqueantes conhecidos: zero. Homologação manual ponta a ponta do
PO aprovada em 23/09/2026.

US-014E --- Identidade visual TooJunto --- DONE. Assets oficiais
incorporados ao Frontend sem redesenho da marca; logo aplicada no
cabeçalho, Login, Cadastro e Convite público; favicons, Apple Touch Icon
e web manifest configurados; título da aplicação mantido como
"TooJunto"; responsividade preservada. Frontend 86/86; TypeScript, build
de produção e git diff --check aprovados. Homologação visual do PO
aprovada em 23/09/2026.

US-014F --- Simplificação final da navegação --- DONE. A navegação
inferior experimental foi revisada durante a homologação: "Início" era
redundante com "Meus Grupos", enquanto "Pagamento" e "Histórico" não
justificavam áreas independentes no MVP 0.1. Após teste visual, a barra
inferior foi removida completamente por não agregar valor com apenas um
destino. O retorno a Meus Grupos permanece contextual nas telas
internas; ações financeiras continuam no contexto do Grupo/Ciclo.
Frontend 86/86; TypeScript, build e git diff --check aprovados.
Homologação visual do PO aprovada.

Conclusão do PO: todos os fluxos principais funcionam; a interface está
leve, contém as informações necessárias e atende aos requisitos
definidos para pessoas com baixo letramento digital.

## MARCO --- MVP 0.1 FUNCIONALMENTE HOMOLOGADO

Data: 23/09/2026. O TooJunto concluiu o desenvolvimento funcional do MVP
0.1. A jornada Criar conta → Login → Criar Grupo → Convidar → Aceitar
convite → Formar Grupo → Sortear → Iniciar ciclos → Informar pagamento →
Confirmar/rejeitar → Concluir ciclo → Avançar ciclos → Encerrar Grupo
foi validada por testes automatizados e homologada manualmente pelo PO.
A identidade visual oficial também foi incorporada e homologada, e a
navegação final foi simplificada com remoção da barra inferior
permanente. Princípio de UX confirmado: MENOS É MAIS. Próximo marco:
PRIMEIRO PILOTO CONTROLADO.

# 12. Sprint 8 --- Piloto --- PRÓXIMO / NÃO INICIADO

-   Executar checklist de produção.
-   Configurar domínio e HTTPS.
-   Configurar backup.
-   Validar logs e auditoria.
-   Executar teste controlado.
-   Selecionar primeiro grupo piloto.
-   Acompanhar uso e registrar feedback.
-   Priorizar correções antes de ampliar o número de grupos.

Objetivo: preparar o ambiente real e executar o primeiro piloto
controlado.

Atividades do Sprint 8: checklist de produção; preparar VPS/ambiente de
produção; configurar domínio e HTTPS; configurar variáveis de ambiente;
preparar PostgreSQL de produção; deploy Backend; deploy Frontend;
configurar fallback SPA para /invites/\*; configurar backup; validar
logs e auditoria mínima; executar smoke test em produção; validar
convite pelo domínio público; validar jornada mobile em dispositivo
real; selecionar o primeiro Grupo piloto; executar piloto controlado;
registrar feedback; corrigir bloqueios antes de ampliar o piloto.

Nenhuma atividade operacional do Sprint 8 deve ser marcada como
concluída sem evidência.

# 13. Backlog técnico atualizado

  -----------------------------------------------------------------------------------------------------
  **ID**    **Tarefa**             **Prioridade**   **Status**
  --------- ---------------------- ---------------- ---------------------------------------------------
  DEV-001   Repositório e          P0               DONE
            estrutura base

  DEV-002   PostgreSQL e estrutura P0               DONE parcial --- migrations pendentes
            de dados

  DEV-003   Autenticação           P1               DONE

  DEV-004   Criação, consulta e    P1               DONE
            gestão de grupos

  DEV-005   Convites e             P1               DONE --- US-005/US-006/US-007 concluídas
            participantes

  DEV-006   Motor de sorteio       P1               DONE --- preparação e execução do sorteio
                                                    concluídas na US-008/US-009.

  DEV-007   Ciclos/contemplações   P1               DONE --- ciclos, contemplação e progresso
                                                    concluídos na US-010.

  DEV-008   Pagamentos ---         P1               DONE --- US-011 concluída, testada e homologada.
            declaração

  DEV-009   Confirmação/rejeição   P1               DONE --- US-012 concluída, testada e homologada.
            de pagamentos

  DEV-010   Auditoria              P1               BACKLOG

  DEV-011   Testes E2E             P1               DONE --- regressão/jornada ponta a ponta validada
                                                    na US-014D.

  DEV-012   Responsividade/UX      P1               DONE no MVP 0.1 --- refinamentos US-014A/B/C/E/F
                                                    homologados; interface mobile simplificada e
                                                    identidade oficial incorporada; evolução continua
                                                    por versão.

  DEV-013   Deploy produção        P1               PRÓXIMO --- Sprint 8

  DEV-014   Monitoramento básico   P2               PRÓXIMO --- Sprint 8
  -----------------------------------------------------------------------------------------------------

# 14. Dívidas Técnicas

Dívidas técnicas são itens conhecidos que não impedem o funcionamento
atual do MVP, mas devem permanecer visíveis e ser tratados quando seu
impacto justificar a implementação.

  ---------------------------------------------------------------------------------------------------------
  ID       Dívida técnica               Origem     Impacto                         Prioridade    Status
  -------- ---------------------------- ---------- ------------------------------- ------------- ----------
  DT-001   Implementar migrations       Sprint 0 / Mudanças futuras de banco ficam Média         PENDENTE
           versionadas com Alembic.     Sprint 2   menos controladas e
                                                   reproduzíveis.

  DT-002   Avaliar/criar índice         US-003.1   Pode afetar desempenho da       Baixa/Média   PENDENTE
           composto em participantes               consulta Meus Grupos quando o
           (usuario_id, status,                    volume crescer.
           grupo_id).

  DT-003   Avaliar constraint única     US-003.1   Risco de inconsistência de      Média         PENDENTE
           (grupo_id, usuario_id) para             dados em cenários futuros de
           impedir participante                    concorrência/convites.
           duplicado.

  DT-004   Substituir usos depreciados  Testes     Warnings e futura               Baixa         PENDENTE
           de datetime.utcnow().        Backend    incompatibilidade com versões
                                                   mais novas.

  DT-005   Eliminar                     Testes     Ruído nos testes e risco futuro Baixa         PENDENTE
           warnings/depreciações        Backend    de incompatibilidade.
           relacionados ao TestClient e
           dependências de testes.

  DT-006   Ampliar testes específicos   US-003.1 / Cobertura atual é suficiente    Média         PENDENTE
           de autorização e erros       US-004     para o MVP, mas faltam alguns
           401/403/404/409/422 nos                 cenários explícitos de
           fluxos de grupos.                       regressão.

  DT-007   Adicionar teste automatizado US-005     A implementação está protegida  Baixa/Média   PENDENTE
           de concorrência para criação            por lock e constraints, mas
           do convite reutilizável.                falta prova automatizada de
                                                   chamadas simultâneas.

  DT-008   Refinar tratamento de        US-005     Reduz risco de laço de          Baixa         PENDENTE
           IntegrityError na geração de            retentativa em erro persistente
           convites, distinguindo                  de banco.
           colisão recuperável de erro
           persistente e limitando
           retentativas.

  DT-009   Ampliar testes Frontend da   US-005     Cobertura atual usa FORM(A)NDO  Baixa         PENDENTE
           US-005 para parametrizar                como representante; ampliar
           todos os estados de Grupo               melhora regressão futura.
           que não permitem convite.

  DT-010   Validar/configurar fallback  US-006     Sem fallback, um link de        Alta antes do PENDENTE
           SPA para acesso direto a                convite aberto diretamente pode piloto
           /invites/\* no ambiente de              receber 404 do servidor antes
           produção.                               de o React carregar.

  DT-011   Reavaliar a navegação        US-006     A concentração de navegação     Baixa         PENDENTE
           centralizada em App.tsx e a             aumenta a responsabilidade do
           necessidade de biblioteca de            App.tsx, mas não bloqueia o MVP
           rotas quando a complexidade             atual.
           justificar.

  DT-012   Adicionar constraint única   US-011     A API evita duplicidade com     Média         PENDENTE
           no banco para pagamento por             lock transacional do Grupo, mas
           (ciclo_id, pagador_id).                 a unicidade ainda não é
                                                   garantida por constraint no
                                                   banco.

  DT-013   Avaliar constraint/índice de US-014B    A aplicação protege             Média         PENDENTE
           banco para unicidade do nome            criação/renomeação com lock
           do Grupo por Gestor entre               transacional por Gestor, mas
           grupos não                              escritas diretas ou caminhos
           encerrados/cancelados.                  futuros fora desse lock podem
                                                   violar a regra.

  DT-014   Tornar usuarios.telefone NOT US-014A    Novos cadastros exigem telefone Baixa/Média   PENDENTE
           NULL no banco por migration             no contrato, porém a coluna
           quando a estratégia de                  permanece nullable por
           migrations estiver definida.            compatibilidade sem migration
                                                   nesta etapa.
  ---------------------------------------------------------------------------------------------------------

Regra de gestão: ao encerrar cada User Story, novas dívidas técnicas
identificadas devem ser registradas nesta seção com ID, origem, impacto,
prioridade e status. Dívida técnica não deve ser implementada
automaticamente se não bloquear segurança, consistência, evolução ou o
piloto.

## 14.1 Situação final de warnings e dívidas não bloqueantes

Regressão final registrou 467 warnings no Backend, principalmente usos
depreciados de datetime.utcnow(), além de avisos de compatibilidade
futura Starlette/httpx e AnyIO e aviso ambiental do cache do pytest por
falta de permissão. Esses avisos não bloquearam a homologação funcional.

Permanecem como dívidas técnicas: migrations/Alembic; coluna
usuarios.telefone ainda nullable no banco embora novos cadastros exijam
telefone pelo contrato; avaliação de constraint/índice para unicidade do
nome do Grupo por Gestor; e demais itens já registrados nesta seção.

# 15. Definition of Done

-   Funcionalidade implementada.
-   Testes automatizados relevantes passando.
-   Revisão independente realizada.
-   Permissões validadas.
-   Tratamento de erro implementado.
-   Interface responsiva quando houver Frontend.
-   Homologação manual do PO aprovada para fluxos de usuário.
-   Sem bug crítico conhecido.
-   Commit e push realizados após aprovação.
-   Documentação atualizada pelo responsável do projeto.

# 16. Critérios para liberar o MVP

-   DONE --- Cadastro e login funcionando.
-   DONE --- Criação, consulta e gestão de grupos funcionando.
-   DONE --- Entrada em Grupo funcionando.
-   DONE --- Convites funcionando.
-   DONE --- Sorteio reproduzível e registrado.
-   DONE --- Ciclos, contemplações, avanço e conclusão funcionando.
-   DONE --- Declaração, confirmação e rejeição de pagamento
    funcionando.
-   ADIADO --- Histórico dedicado removido do critério do MVP 0.1 e
    transferido para MVP 0.3.
-   DONE --- Controle de acesso funcionando.
-   DONE --- Fluxo principal responsivo e homologado em simulação
    mobile; validação em dispositivo real ocorrerá no Sprint 8.
-   DONE --- Regressão final: Backend 157/157 e Frontend 86/86;
    TypeScript e build aprovados.
-   DONE --- Identidade visual oficial incorporada e navegação final
    simplificada, sem barra inferior permanente; homologação visual do
    PO aprovada.
-   PENDENTE SPRINT 8 --- selecionar primeiro Grupo piloto.

Status de liberação funcional: MVP 0.1 FUNCIONALMENTE HOMOLOGADO.
Permanecem pendentes somente as atividades operacionais do Sprint 8
necessárias antes do piloto real.

# 17. Estratégia de testes

  -------------------------------------------------------------------------------
  **Momento**   **Teste**               **Objetivo**
  ------------- ----------------------- -----------------------------------------
  Durante cada  Unitário/API/Frontend   Detectar regressões e validar regras.
  US

  Fim de cada   Revisão independente    Verificar segurança, contratos e efeitos
  US                                    colaterais.

  Fim de fluxo  Homologação do PO       Validar comportamento real no navegador.

  Sprint 7      E2E                     Validar jornada inteira.

  Antes do      Usabilidade             Verificar compreensão pelo público-alvo.
  piloto

  Piloto        Observação real         Validar valor e continuidade.
  -------------------------------------------------------------------------------

# 18. Métricas do desenvolvimento

-   Tempo para concluir a jornada principal.
-   Quantidade de bugs críticos.
-   Taxa de falha por fluxo.
-   Tempo médio para corrigir bloqueios.
-   Percentual de testes críticos passando.
-   Quantidade de funcionalidades fora do escopo adicionadas sem
    necessidade --- meta: zero.
-   Quantidade de US homologadas pelo PO.

# 19. Gestão de risco

  -------------------------------------------------------------------------------
  **Risco**       **Impacto**   **Mitigação**
  --------------- ------------- -------------------------------------------------
  Escopo crescer  Alto          Congelar MVP e manter backlog separado.

  Sorteio         Alto          Regra no Backend + transação + testes.
  inconsistente

  Acesso indevido Alto          Autorização no Backend + testes.

  UX complexa     Alto          Teste com público-alvo antes do piloto.

  Falha de        Médio         Storage gerenciado + validação de upload.
  storage

  Custo cloud     Médio         Começar pequeno e monitorar consumo.
  crescer

  Integrações     Médio         MVP sem dependências externas críticas.
  atrasarem

  Dívida técnica  Médio         Registrar explicitamente e atacar apenas quando
  crescer                       bloquear evolução/segurança.
  -------------------------------------------------------------------------------

## 19.1 Backlog direcionado ao MVP 0.3

Itens adiados para evolução posterior: Perfil do usuário; edição de
dados pessoais; dados para recebimento; chave Pix; copiar chave Pix;
futura evolução para Pix Copia e Cola / QR Code; Histórico evoluído; e
reavaliação de uma navegação global inferior quando houver destinos
suficientes para justificá-la, por exemplo Meus Grupos, Buscar/Explorar
e Perfil. Esses itens não pertencem ao escopo do MVP 0.1.

# 20. Próximo passo --- Sprint 8

Prosseguir para o Sprint 8 --- preparação do ambiente real e execução do
primeiro piloto controlado. O MVP 0.1 está funcionalmente concluído e
homologado; produção e piloto ainda não foram iniciados.

O princípio permanece: menos é mais. Cada nova funcionalidade deve
existir para validar a jornada principal do MVP, não para antecipar
complexidade de versões futuras.

## Anexo A --- Registro histórico da US-012 --- Confirmar/Rejeitar pagamento e concluir ciclo

-   Status: DONE --- homologada pelo Product Owner em 22/09/2026.
-   O contemplado do ciclo pode confirmar ou rejeitar individualmente
    pagamentos em AGUARDANDO_CONFIRMACAO; Gestor sem ser contemplado não
    possui privilégio especial.
-   Pagamento rejeitado pode ser informado novamente pelo próprio
    pagador, reutilizando o registro existente.
-   O ciclo somente é concluído quando todos os N−1 pagamentos exigíveis
    estiverem CONFIRMADO. A conclusão e o avanço para o próximo ciclo
    ocorrem de forma transacional.
-   Após a última confirmação do último ciclo, o Grupo passa para
    ENCERRADO e todos os ciclos são apresentados como CONCLUIDO.
-   API adicionada: POST
    /groups/{group_id}/cycles/{cycle_number}/payments/{payment_id}/confirm
    e POST
    /groups/{group_id}/cycles/{cycle_number}/payments/{payment_id}/reject.
-   Contrato das obrigações ampliado com pagamento_id, pode_avaliar e
    estados CONFIRMADO/REJEITADO; progresso ampliado com
    grupo_concluido.
-   Backend: 138/138 testes aprovados, sem alteração estrutural de banco
    e sem nova dependência.
-   Frontend: ações Confirmar/Rejeitar condicionadas a
    pode_avaliar=true, modais com prevenção de múltiplos envios,
    atualização automática do progresso e suporte à nova declaração após
    rejeição.
-   Frontend final: 74/74 testes aprovados, TypeScript e build de
    produção aprovados.
-   Ajuste de UX homologado em Meus Grupos: Sorteio realizado com badge
    azul e Grupo concluído com badge laranja, mantendo texto explícito e
    os demais status inalterados.
-   DT-012 permanece registrada: avaliar futuramente constraint única no
    banco para pagamento por (ciclo_id, pagador_id); não bloqueia o MVP.

Registro histórico: a US-012 foi concluída e publicada; a US-013 foi
posteriormente descartada/adiada para MVP 0.3 durante o Sprint 7.

# 21. Atualização de planejamento --- MVP 0.2

Data da revisão: 28/09/2026. Versão documental: 0.14.

## 21.1 Histórico da atualização

  -----------------------------------------------------------------------
  Versão                  Data                    Atualização
  ----------------------- ----------------------- -----------------------
  0.13                    23/09/2026              Baseline do MVP 0.1:
                                                  desenvolvimento
                                                  funcional, identidade
                                                  visual e navegação
                                                  homologados; preparação
                                                  para o piloto.

  0.14                    28/09/2026              MVP 0.1 registrado como
                                                  implantado em
                                                  STAGING/PILOTO; escopo
                                                  do MVP 0.2 delimitado;
                                                  roadmap das Sprints
                                                  9--15 e US-015 a US-032
                                                  aprovado.
  -----------------------------------------------------------------------

## 21.2 Situação

O desenvolvimento permanece local. A VPS Hostinger é STAGING/PILOTO e
recebe somente versões testadas e versionadas. O princípio "menos é
mais" continua obrigatório.

## 21.3 Roadmap executivo --- Sprints 9 a 15

  -----------------------------------------------------------------------
  Sprint            Objetivo          User Stories      Resultado
                                                        esperado
  ----------------- ----------------- ----------------- -----------------
  Sprint 9          Fundação para     US-015, US-016,   Migrations
                    evolução segura   US-017            versionadas,
                                                        backup/restore e
                                                        deploy/rollback
                                                        seguro em
                                                        staging.

  Sprint 10         Fundação das      US-018, US-019    Persistência de
                    notificações                        notificações e
                                                        serviço central
                                                        de notificações.

  Sprint 11         Experiência       US-020, US-021    Central mínima,
                    in-app                              contador e estado
                                                        lida/não lida.

  Sprint 12         Comunicação por   US-022, US-023    E-mail
                    e-mail                              transacional e
                                                        tratamento de
                                                        falhas sem
                                                        rollback do
                                                        domínio.

  Sprint 13         Eventos           US-024, US-025,   Convites,
                    operacionais      US-026, US-027    formação,
                                                        sorteio, ciclos e
                                                        pagamentos
                                                        integrados às
                                                        notificações.

  Sprint 14         Entrada e         US-028, US-029    Landing Page →
                    refinamento                         App e correção da
                    visual                              nitidez da marca.

  Sprint 15         Qualidade e       US-030, US-031,   Regressão,
                    homologação       US-032            segurança, deploy
                                                        e homologação
                                                        final do MVP 0.2
                                                        em staging.
  -----------------------------------------------------------------------

## 21.4 User Stories aprovadas

  -----------------------------------------------------------------------
  US                      Título                  Escopo resumido
  ----------------------- ----------------------- -----------------------
  US-015                  Migrations versionadas  Controlar alterações do
                                                  schema por migrations.

  US-016                  Backup e restauração do Garantir backup
                          PostgreSQL              verificável e
                                                  restauração
                                                  documentada.

  US-017                  Deploy seguro em        Padronizar atualização,
                          Staging                 migrations, health
                                                  checks, smoke tests e
                                                  rollback.

  US-018                  Modelo de notificações  Persistir notificações
                                                  por usuário, tipo,
                                                  conteúdo, contexto e
                                                  leitura.

  US-019                  Serviço de notificações Centralizar
                                                  geração/destinatários
                                                  sem acoplar domínio aos
                                                  canais.

  US-020                  Central mínima de       Exibir notificações
                          notificações            recentes e acesso ao
                                                  contexto da ação.

  US-021                  Leitura de notificações Controlar lida/não lida
                                                  e contador, sem
                                                  recursos avançados.

  US-022                  E-mail transacional     Enviar e-mails curtos
                                                  para os eventos
                                                  aprovados.

  US-023                  Confiabilidade do       Registrar sucesso/falha
                          e-mail                  e não reverter
                                                  operações de negócio.

  US-024                  Notificações de convite Convite
                          e formação              aceito/recusado, grupo
                                                  completo e cancelado.

  US-025                  Recusa explícita de     Diferenciar "Agora não"
                          convite                 de "Não quero
                                                  participar".

  US-026                  Notificações de sorteio Sorteio,
                          e ciclo                 início/conclusão de
                                                  ciclo, avanço e
                                                  encerramento.

  US-027                  Notificações de         Prazo, informado,
                          pagamento               confirmado, rejeitado e
                                                  conclusão do ciclo.

  US-028                  Landing Page →          Entrada clara para
                          aplicação               login/cadastro e App.

  US-029                  Nitidez da marca        Corrigir
                                                  asset/renderização sem
                                                  redesenhar a
                                                  identidade.

  US-030                  Regressão completa MVP  Preservar os fluxos
                          0.1 + 0.2               homologados.

  US-031                  Segurança e privacidade Validar isolamento,
                          das notificações        autorização e ausência
                                                  de exposição indevida.

  US-032                  Deploy e homologação do Promover para staging e
                          MVP 0.2                 concluir
                                                  smoke/E2E/homologação
                                                  do PO.
  -----------------------------------------------------------------------

## 21.5 Governança

Fluxo padrão:
`Sprint → US → Task pequena → implementação → testes → homologação do PO → DONE → commit/push`.

Depois de versionado, um marco utilizável pode ser promovido ao staging
para validação integrada. A Sprint 15 é a homologação final do MVP 0.2,
não o primeiro contato com a VPS.

Novas funcionalidades identificadas durante a execução devem ir para o
backlog, salvo quando indispensáveis para cumprir os critérios de aceite
de uma US aprovada.

## 21.6 Fora do escopo do MVP 0.2

WhatsApp automático, chat, push notification, SMS, aplicativo nativo,
Pix/Open Finance integrado, marketplace, reputação, painel
administrativo complexo, microserviços e brokers distribuídos sem
necessidade comprovada.

A Matriz Oficial de Eventos e Notificações em `requisitos.md` é a
referência funcional para destinatários e ações.
