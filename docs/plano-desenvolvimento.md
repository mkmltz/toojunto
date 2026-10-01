**TOOJUNTO**

Plano de Desenvolvimento — MVP 0.1 e Roadmap MVP 0.2 e MVP 0.3

Plano técnico, sprints, User Stories, ordem de implementação e histórico de evolução

| **Campo** | **Valor**                                                                                                                                                                                                              |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Versão    | 0.19                                                                                                                                                                                                                   |
| Data      | 29 de setembro de 2026                                                                                                                                                                                                 |
| Status    | MVP 0.1 — homologado e implantado em STAGING/PILOTO. Sprint 13 do MVP 0.2 — DONE; eventos operacionais de convite, formação, sorteio, ciclos e pagamentos integrados ao mecanismo de notificações.                     |
| Objetivo  | Preservar o MVP 0.1 como baseline funcional e evoluir de forma controlada para o MVP 0.2, priorizando comunicação operacional, segurança da evolução do banco, simplicidade de uso e validação incremental em staging. |

# Histórico de versões

| Versão | Data       | Atualização                                                                                                                                                                                                                                                                                                                            |
| ------ | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0.13   | 23/09/2026 | Baseline documental do MVP 0.1: desenvolvimento funcional, identidade visual e navegação homologados; preparação para o piloto.                                                                                                                                                                                                        |
| 0.14   | 28/09/2026 | MVP 0.1 registrado como implantado em STAGING/PILOTO; escopo do MVP 0.2 delimitado; roadmap das Sprints 9–15 e respectivas User Stories incluídos; matriz de eventos/notificações passa a orientar a evolução.                                                                                                                         |
| 0.15   | 28/09/2026 | Sprint 9 encerrada: US-015/US-016/US-017 concluídas; Alembic adotado com baseline 9b2f1c4d7e6a; primeiro backup real validado; deploy seguro executado no STAGING; DT-001 encerrada.                                                                                                                                                   |
| 0.16   | 29/09/2026 | Sprint 10 encerrada: US-018/US-019 concluídas; tabela/modelo de notificações e migration c4a8e2f6b1d3 implementados; NotificationService centralizado criado; 207 testes Backend aprovados; Alembic sem schema drift; STAGING não alterado.                                                                                            |
| 0.17   | 29/09/2026 | Sprint 11 encerrada: US-020/US-021 concluídas; API autenticada de notificações, contador de não lidas e marcação individual como lida implementados; 221 testes Backend aprovados; Alembic c4a8e2f6b1d3 sem schema drift; STAGING não alterado.                                                                                        |
| 0.18   | 29/09/2026 | Sprint 12 encerrada: US-022/US-023 concluídas; EmailService e provedor SMTP configurável implementados; persistência de entregas de e-mail criada pela migration e7d3a9c5f2b4; falhas do provedor isoladas das operações de domínio; 239 testes Backend aprovados; Alembic sem schema drift; STAGING não alterado.                     |
| 0.19   | 29/09/2026 | Sprint 13 encerrada: US-024/US-025/US-026/US-027 concluídas; eventos de convite/formação, recusa explícita, sorteio/ciclos e pagamentos integrados às notificações in-app e e-mail confiável; migration f1b6c8d4a2e9 adicionada para recusas de convite; 257 testes Backend aprovados; Alembic sem schema drift; STAGING não alterado. |

# 1\. Objetivo do desenvolvimento

Entregar uma versão funcional do TooJunto capaz de executar a jornada completa:

**Criar → Convidar → Entrar → Pagar → Registrar → Sortear → Acompanhar**

O desenvolvimento deve priorizar validação com usuários reais, evitando funcionalidades que não sejam necessárias para testar a hipótese principal do produto.

# 2\. Estratégia de desenvolvimento

- Construção incremental e vertical: cada sprint entrega uma parte utilizável.
- Priorizar primeiro o caminho feliz do usuário.
- Testar as regras críticas desde o início.
- Evitar perfeccionismo visual antes dos testes de usabilidade.
- Usar dados de teste controlados até o piloto.
- Publicar em staging antes de produção.
- Corrigir problemas que bloqueiem a jornada antes de adicionar funcionalidades.
- Fluxo de trabalho: Backlog → Sprint → User Story → Card/Prompt → /dev-backend (análise interna, implementação, testes e revisão) → /dev-frontend (análise interna, implementação, testes e revisão) → Homologação do PO → Documentação → Commit/Push manual → Done. Os agents só interrompem o fluxo antes da implementação quando identificarem mudança arquitetural, alteração estrutural de banco, nova dependência, mudança de regra de negócio, alteração de contrato existente com impacto em outras funcionalidades ou trabalho fora do escopo.
- Manter o MVP simples e evitar tecnologia ou funcionalidades sem problema concreto a resolver.

# 3\. Ordem de implementação

| **Prioridade** | **Bloco**     | **Resultado**                                                                                          |
| -------------- | ------------- | ------------------------------------------------------------------------------------------------------ |
| P0             | Fundação      | Repositório, ambientes, banco, autenticação e base técnica.                                            |
| P1             | Usuários      | Cadastro, login, sessão e proteção de rotas.                                                           |
| P1             | Grupos        | Criar, listar, consultar, editar e cancelar grupos.                                                    |
| P1             | Convites      | Geração, compartilhamento, aceite/recusa e entrada no grupo.                                           |
| P1             | Participantes | Formação do grupo e controle do limite de participantes.                                               |
| P1             | Sorteio       | Preparação, execução e registro da ordem.                                                              |
| P1             | Ciclos        | Contemplação e progresso.                                                                              |
| P1             | Pagamentos    | Declaração de pagamento e confirmação/rejeição, sem movimentação financeira pelo TooJunto.             |
| P1             | Histórico     | Adiado para MVP 0.3; reavaliar quando novas funcionalidades justificarem uma visão histórica dedicada. |
| P2             | Polimento     | Usabilidade, mensagens, acessibilidade e correções.                                                    |
| P2             | Piloto        | Deploy, monitoramento e suporte.                                                                       |

# 4\. Status das User Stories

| **Sprint** | **US**   | **Funcionalidade**                             | **Status**       |
| ---------- | -------- | ---------------------------------------------- | ---------------- |
| Sprint 1   | US-001   | Criar conta                                    | DONE             |
| Sprint 1   | US-002   | Login, sessão, proteção de rotas e logout      | DONE             |
| Sprint 2   | US-003   | Criar Grupo                                    | DONE             |
| Sprint 2   | US-003.1 | Consultar Meus Grupos e detalhes               | DONE             |
| Sprint 2   | US-004   | Gerenciar Grupo — editar e cancelar            | DONE             |
| Sprint 3   | US-005   | Convidar participantes                         | DONE             |
| Sprint 3   | US-006   | Aceitar ou recusar convite / entrar no Grupo   | DONE             |
| Sprint 3   | US-007   | Visualizar participantes e formação do Grupo   | DONE             |
| Sprint 4   | US-008   | Preparar sorteio                               | DONE             |
| Sprint 4   | US-009   | Realizar sorteio e registrar ordem             | DONE             |
| Sprint 5   | US-010   | Ciclos, contemplação e progresso               | DONE             |
| Sprint 6   | US-011   | Registrar pagamento                            | DONE             |
| Sprint 6   | US-012   | Confirmar ou rejeitar pagamento                | DONE             |
| Sprint 7   | US-013   | Histórico e acompanhamento                     | ADIADA — MVP 0.3 |
| Sprint 7   | US-014A  | Refinamento de convites e cadastro             | DONE             |
| Sprint 7   | US-014B  | Criação e integridade do Grupo                 | DONE             |
| Sprint 7   | US-014C  | Simplificação da tela "Em andamento"           | DONE             |
| Sprint 7   | US-014D  | Regressão e homologação final do MVP 0.1       | DONE             |
| Sprint 7   | US-014E  | Identidade visual TooJunto para o piloto       | DONE             |
| Sprint 7   | US-014F  | Simplificação final da navegação para o piloto | DONE             |

Observação: a numeração das User Stories passa a ser a referência operacional do roadmap. A US-003.1 foi incorporada durante o Sprint 2 para permitir navegação persistente em "Meus Grupos" e acesso aos detalhes após nova sessão/F5.

# 5\. Sprints atualizadas

| **Sprint** | **Duração alvo** | **Objetivo**             | **Entrega / situação**                                                                                                                                           |
| ---------- | ---------------- | ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sprint 0   | 2–3 dias         | Fundação                 | DONE — Git, estrutura, ambiente local, PostgreSQL em Docker e base de testes.                                                                                    |
| Sprint 1   | 4–5 dias         | Autenticação             | DONE — cadastro, login, sessão, rotas protegidas e logout.                                                                                                       |
| Sprint 2   | 4–5 dias         | Grupos                   | DONE — criar, listar, consultar detalhes, editar e cancelar.                                                                                                     |
| Sprint 3   | 4–5 dias         | Convites e participantes | DONE — US-005, US-006 e US-007 concluídas, testadas e homologadas.                                                                                               |
| Sprint 4   | 4–5 dias         | Sorteio                  | DONE — US-008 e US-009 concluídas, testadas e homologadas.                                                                                                       |
| Sprint 5   | 4–5 dias         | Ciclos e contemplação    | DONE — US-010 concluída, testada e homologada.                                                                                                                   |
| Sprint 6   | 5–7 dias         | Pagamentos               | DONE — US-011 e US-012 concluídas, testadas e homologadas.                                                                                                       |
| Sprint 7   | 4–5 dias         | Integração e UX          | DONE — US-013 descartada/adiada para MVP 0.3; US-014A/B/C/D/E/F concluídas; regressão, identidade visual, navegação final e homologação ponta a ponta aprovadas. |
| Sprint 8   | 3–5 dias         | Piloto                   | PRÓXIMO — NÃO INICIADO. Preparação do ambiente real e execução do primeiro piloto controlado.                                                                    |

Estimativa total de referência: aproximadamente 5–7 semanas de desenvolvimento enxuto, sujeita a revisão conforme o aprendizado obtido durante a implementação e os testes com usuários.

# 6\. Sprints concluídas

## Sprint 0 — Fundação — DONE

- Repositório Git e estrutura frontend/backend criados.
- Ambiente local configurado.
- PostgreSQL 16 executando em Docker.
- Variáveis de ambiente e testes básicos configurados.
- Base técnica pronta para desenvolvimento incremental.

Observação técnica histórica: migrations versionadas eram dívida técnica desde a fundação. A DT-001 foi encerrada na Sprint 9 com Alembic, baseline MVP 0.1 e adoção controlada do banco legado em STAGING.

## Sprint 1 — Autenticação — DONE

- US-001 — Cadastro de usuário.
- US-002 — Login, token/sessão, proteção de rotas e logout.
- Hash seguro de senha e JWT.
- Frontend de autenticação integrado ao Backend.
- Homologação manual aprovada.
- 30 testes automatizados aprovados ao encerramento do Sprint 1.

## Sprint 2 — Grupos — DONE

- US-003 — Criar Grupo.
- US-003.1 — Consultar Meus Grupos e detalhes.
- US-004 — Gerenciar Grupo: editar e cancelar.
- Home transformada em "Meus Grupos", válida para Gestor e Participante.
- Gestor é automaticamente participante do grupo e ocupa uma vaga.
- quantidade_ciclos = quantidade_participantes no MVP 0.1.
- valor_premio calculado pelo Backend: valor_cota × quantidade_participantes.
- Cancelamento lógico com status CANCELADO, preservando histórico.
- Somente Gestor de grupo em RASCUNHO pode editar ou cancelar.
- Detalhes persistentes: após F5, o Frontend mantém somente o ID e recarrega os dados do Backend.
- Backend: 77/77 testes aprovados.
- Frontend: 19/19 testes aprovados e build de produção aprovado.
- Homologação manual do PO aprovada.

Critério de saída atingido: usuário autenticado consegue criar um grupo, encontrá-lo novamente em Meus Grupos, consultar seus detalhes e, quando Gestor de um grupo em RASCUNHO, editar ou cancelar.

# 7\. Sprint 3 — Convites e participantes — DONE

Objetivo: permitir que um Gestor forme o grupo convidando outros usuários e que estes possam aceitar ou recusar a participação.

- US-005 — Convidar participantes — DONE.

Backend: convite único e reutilizável por Grupo, token criptograficamente seguro, operação idempotente e autorização exclusiva do Gestor proprietário.

Segurança: grupo inexistente, participante não gestor e usuário externo recebem resposta 404 indistinguível no endpoint de convite, evitando enumeração de grupos privados.

Frontend: ação "Convidar pessoas" disponível somente para Gestor de Grupo RASCUNHO; compartilhamento via Web Share API e fallback para copiar link.

Contrato: POST /groups/{group_id}/invite.

Backend: 90/90 testes aprovados após correção e revisão final.

Frontend: 28/28 testes aprovados; TypeScript e build Vite aprovados.

Homologação manual do PO aprovada: geração, cópia do link e compartilhamento real via WhatsApp pelo compartilhamento nativo do sistema operacional.

US-006 — Aceitar ou recusar convite / entrar no Grupo — DONE.

Backend: GET /invites/{token} público com exposição mínima e POST /invites/{token}/accept protegido por JWT; aceite cria Participante ATIVO sem ordem de sorteio.

Regras Backend: validação de status, capacidade, duplicidade e Gestor; toda associação persistida em Participante ocupa vaga, inclusive ATIVO e INATIVO.

Concorrência: bloqueio pessimista do Grupo com FOR UPDATE protege a última vaga; status e capacidade são revalidados dentro da transação.

Privacidade: token inválido, Grupo indisponível e Grupo lotado recebem resposta pública uniforme 404; nenhuma informação do Gestor ou dos participantes é exposta.

Frontend: abertura direta de /invites/{token}, preservação do convite durante Login/Cadastro, retorno automático ao convite sem aceite automático, ação "Agora não" sem persistência e "Ver Grupo" após aceite.

Frontend sem React Router nesta US; a própria URL é a fonte do token e o fluxo é reconstruído após recarga.

Backend: 114/114 testes aprovados após implementação e revisão final.

Frontend: 41/41 testes aprovados após correção de assincronismo; TypeScript e build Vite aprovados.

Homologação manual do PO aprovada: convite público exibido corretamente, proteção contra Gestor/participante duplicado validada e fluxo real de entrada testado.

Nenhum endpoint de recusa foi criado; recusar significa apenas sair do fluxo sem alteração de domínio.

- Gerar convite único.
- Disponibilizar forma simples de compartilhamento.
- US-007 — Exibir participantes e progresso de formação do grupo — DONE.
- Backend: formação incorporada ao GET /groups/{group_id}, com quantidade atual, limite, vagas disponíveis e lista mínima de participantes contendo nome e papel. Gestor aparece primeiro e identificado como GESTOR.
- Regras Backend: Gestor e Participante ATIVO podem consultar; usuário externo ou inativo recebe 404. Toda associação persistida em Participante ocupa vaga, inclusive INATIVO. Quantidades e vagas são calculadas exclusivamente pelo Backend.

Frontend: formação integrada à tela existente de detalhes, com quantidade, limite, nomes, papéis e mensagem de vagas; ações exclusivas do Gestor permanecem ocultas para Participantes. Backend: 116/116 testes aprovados. Frontend: 46/46 testes aprovados e build de produção aprovado. Homologação manual do PO aprovada nos perfis Gestor e Participante. Commit 102969d publicado na main. Critério de saída atingido: Gestor convida, Participante entra e ambos visualizam corretamente a formação do Grupo.

# 8\. Sprint 4 — Sorteio — DONE

- US-008 — Preparar sorteio quando o grupo estiver completo — DONE.
- Backend: criado POST /groups/{group_id}/prepare-draw, exclusivo do Gestor proprietário. A preparação valida, sob lock transacional, o estado e a formação completa antes de alterar o Grupo para SORTEIO. O preenchimento da última vaga não prepara automaticamente o sorteio.
- Regra de negócio registrada para a US-009: a 1ª posição da ordem de contemplação é reservada ao Gestor; as posições 2..N serão sorteadas aleatoriamente entre os demais participantes. A US-008 não atribui nem persiste posições e não executa o sorteio.
- Ajuste de UX: GET /groups passou a retornar vagas_disponiveis sem consultas adicionais por Grupo. Na tela Meus Grupos, RASCUNHO com vagas é exibido como "Em formação"; RASCUNHO sem vagas como "Grupo completo"; SORTEIO como "Pronto para sorteio"; e CANCELADO como "Cancelado". "Grupo completo" é apenas representação de interface, não um novo status de domínio.
- Validação: Backend 125/125 testes aprovados. Frontend 52/52 testes aprovados, TypeScript e build de produção aprovados. Homologação manual do PO concluída, incluindo a sinalização visual dos estados em Meus Grupos.
- US-009 — Realizar sorteio e registrar ordem — DONE.
- Backend: criado POST /groups/{group_id}/draw, exclusivo do Gestor e permitido apenas para Grupo em SORTEIO. A posição 1 pertence ao Gestor e as posições 2..N são sorteadas aleatoriamente entre os demais participantes. A ordem definitiva é persistida no campo existente Participante.ordem_sorteio, sem alteração estrutural de banco.
- Calendário: GET /groups/{id} disponibiliza aos integrantes autorizados posição, nome, papel e data prevista de recebimento. A data é derivada de data_inicio + (posição - 1) × 30 dias corridos, sem duplicação no banco.
- Integridade e segurança: sorteio executado uma única vez em transação protegida contra concorrência; nova tentativa é bloqueada. Participantes podem consultar o resultado, mas somente o Gestor pode executar o sorteio. Usuários externos permanecem protegidos pelas regras de privacidade existentes.
- Frontend: ação "Realizar sorteio" exibida somente ao Gestor quando disponível, com confirmação do caráter definitivo. Após a execução, Gestor e Participantes visualizam a mesma ordem persistida e o estado do Grupo após o sorteio. O frontend apenas formata as datas recebidas do Backend; não recalcula ordem nem calendário.

UX atualizada posteriormente no refinamento para piloto: o status ATIVO é apresentado como "Em andamento", com badge azul e texto explícito. "Grupo concluído" usa badge laranja. As mudanças relevantes de status não dependem somente da cor.

# 9\. Sprint 5 — Ciclos e contemplação — DONE

- US-010 — Criar e acompanhar ciclos conforme a ordem sorteada.
- Identificar contemplado do ciclo.
- Registrar contemplação.
- Mostrar ciclo atual e progresso.
- Permitir consulta de ciclos anteriores.
- Controlar estados do ciclo.

Critério de saída: usuário entende quem recebe, em qual ciclo e qual o progresso do grupo.

Critério de saída atingido: após o sorteio, os integrantes conseguem acompanhar o calendário de contemplações e o ciclo atual sem antecipar a lógica de pagamentos.

Commit da US-010: e92ed33 — feat: add group cycles and progress.

Homologação manual do PO aprovada em 22 de setembro de 2026 para Gestor e Participante.

Validação: Backend 131/131 testes aprovados. Frontend 58/58 testes aprovados, TypeScript e build de produção aprovados.

Frontend: a tela de detalhes consulta o endpoint de ciclos após o sorteio e apresenta "Ciclo X de N", contemplado, data prevista e calendário completo. ATUAL recebe maior destaque visual; os estados mantêm texto explícito e não dependem somente de cor.

Segurança: Gestor e Participantes autorizados visualizam o mesmo progresso; usuários externos recebem 404 e integrantes recebem 409 quando o Grupo ainda não possui sorteio disponível.

Regra crítica: nenhum ciclo avança automaticamente pela data e não foi criado mecanismo manual de "Avançar ciclo". O avanço futuro dependerá da conclusão das obrigações de pagamento.

Progresso: imediatamente após o sorteio, o ciclo 1 permanece ATUAL e os demais ficam PROXIMO. O estado CONCLUIDO está previsto no contrato, mas somente será utilizado quando as obrigações de pagamento forem integradas nas US-011/US-012.

Calendário: a data prevista continua seguindo data_inicio + (ciclo - 1) × 30 dias corridos, preservando a regra aprovada na US-009.

Regras de domínio: os ciclos são derivados da ordem_sorteio e da data de início, sem alteração estrutural do banco. A posição sorteada define o ciclo e o contemplado correspondente.

Backend: criado GET /groups/{group_id}/cycles para disponibilizar ciclo atual, total de ciclos, contemplado e data prevista do ciclo atual, além do calendário completo com participante, papel e situação.

US-010 — Ciclos, contemplação e progresso do Grupo — DONE.

# 10\. Sprint 6 — Pagamentos — DONE

- US-011 — Registrar pagamento — DONE.
- Mostrar contemplado, pagador, valor, prazo e situação da obrigação.
- Pagamento realizado diretamente entre participante e contemplado, sem movimentação financeira pelo TooJunto.
- Registrar declaração do próprio pagamento como AGUARDANDO_CONFIRMACAO, sem permitir duplicidade.
- Não solicitar comprovante, valor digitado, chave Pix, banco, código de transação ou observação no MVP.
- US-012 — Confirmar ou rejeitar pagamento pelo contemplado — DONE.
- Atualizar progresso e rastreabilidade.

Critério de saída: ciclo registra e confirma pagamentos sem movimentação financeira pelo TooJunto.

US-011 — Resultado da implementação e homologação.

Backend: GET e POST /groups/{group_id}/cycles/{cycle_number}/payments. Nesta etapa, somente o ciclo atual (ciclo 1) está disponível. As respostas incluem pagador_id (Participante) e pagador_usuario_id (Usuário), permitindo ao frontend identificar com segurança a obrigação própria.

Persistência: reutilizadas as tabelas ciclos e pagamentos. O pagamento declarado fica AGUARDANDO_CONFIRMACAO. O backend define valor e contemplado; o participante não informa valor manualmente. O contemplado não possui obrigação de pagar a si próprio.

Prazo e transparência: pagamento esperado até 5 dias antes da data prevista do ciclo. A API fornece situação derivada e contagem de dias para exibir PENDENTE, alerta laranja na janela crítica, AGUARDANDO_CONFIRMACAO e ATRASADO. A confirmação futura pertence à US-012.

Frontend: a tela de detalhes exibe coletivamente as obrigações do ciclo. A ação "Informar pagamento" aparece somente para a obrigação do usuário autenticado. A confirmação foi ajustada após homologação para modal centralizada, evitando confirmação fora da área visível e múltiplos cliques.

Usabilidade: modal com Cancelar e "Sim, já paguei", bloqueio durante o POST, feedback de erro, atualização para "Aguardando confirmação", foco inicial, navegação por Tab, Escape e retorno de foco ao fechar.

Testes: backend 134/134; frontend 65/65; TypeScript e build de produção aprovados. Homologação manual do PO concluída em 22/09/2026.

Dívida técnica: DT-012 registrada para avaliar constraint única de pagamento por (ciclo_id, pagador_id). A proteção atual usa lock transacional no fluxo da API e não bloqueia o MVP.

# 11\. Sprint 7 — Integração, refinamento e UX — DONE

- US-013 — Histórico e acompanhamento — DESCARTADA PELO PO / ADIADA PARA MVP 0.3.
- Executar jornada completa de ponta a ponta.
- Corrigir navegação e mensagens.
- Validar mobile-first e acessibilidade.
- Testar estados vazios, erros e carregamento.
- Executar testes E2E.
- Corrigir bugs críticos.

## US-013 — Decisão de produto

Durante a homologação, o PO concluiu que uma seção dedicada de Histórico duplicava informações já disponíveis na interface e aumentava a complexidade para o público de baixo letramento digital. As alterações experimentais da US-013 foram revertidas. Histórico não é critério de liberação do MVP 0.1 e fica no backlog do MVP 0.3 para reavaliação quando novas funcionalidades justificarem sua existência.

## US-014 — Refinamento para o piloto — DONE

US-014A — Convites e cadastro — DONE. Telefone obrigatório no cadastro; regra de senha de 8 a 128 caracteres explicitada; confirmação de senha; convite identifica Gestor e Grupo; compartilhamento usa URL completa; tela pública orienta criação de conta; manager_name adicionado de forma aditiva ao contrato público.

US-014B — Criação e integridade do Grupo — DONE. Data inicial anterior a hoje recebe mensagem específica; nome do Grupo é único por Gestor enquanto o grupo não estiver ENCERRADO/CANCELADO, desconsiderando caixa e espaços adicionais; Gestores diferentes podem usar o mesmo nome; nome pode ser reutilizado após encerramento/cancelamento; cards exibem o nome do Gestor; gestor_nome foi adicionado aos contratos necessários; após o primeiro aceite de outro participante, as condições do Grupo tornam-se imutáveis; a participação automática do Gestor não bloqueia edição; cancelamento preserva as regras existentes.

US-014C — Simplificação da tela "Em andamento" — DONE. Ciclo atual virou o bloco operacional principal; pagamentos e progresso foram consolidados; "Calendário dos ciclos" e "Ordem de recebimento" foram unificados em "Próximos recebimentos"; Regras e Participantes ficam recolhidos por padrão; redundâncias foram removidas e as ações financeiras preservadas.

US-014D — Regressão e homologação final — DONE. Backend 157/157; Frontend 86/86; TypeScript, build de produção e git diff --check aprovados; contratos, autorização/segurança e responsividade aprovados; bugs bloqueantes conhecidos: zero. Homologação manual ponta a ponta do PO aprovada em 23/09/2026.

US-014E — Identidade visual TooJunto — DONE. Assets oficiais incorporados ao Frontend sem redesenho da marca; logo aplicada no cabeçalho, Login, Cadastro e Convite público; favicons, Apple Touch Icon e web manifest configurados; título da aplicação mantido como "TooJunto"; responsividade preservada. Frontend 86/86; TypeScript, build de produção e git diff --check aprovados. Homologação visual do PO aprovada em 23/09/2026.

US-014F — Simplificação final da navegação — DONE. A navegação inferior experimental foi revisada durante a homologação: "Início" era redundante com "Meus Grupos", enquanto "Pagamento" e "Histórico" não justificavam áreas independentes no MVP 0.1. Após teste visual, a barra inferior foi removida completamente por não agregar valor com apenas um destino. O retorno a Meus Grupos permanece contextual nas telas internas; ações financeiras continuam no contexto do Grupo/Ciclo. Frontend 86/86; TypeScript, build e git diff --check aprovados. Homologação visual do PO aprovada.

Conclusão do PO: todos os fluxos principais funcionam; a interface está leve, contém as informações necessárias e atende aos requisitos definidos para pessoas com baixo letramento digital.

## MARCO — MVP 0.1 FUNCIONALMENTE HOMOLOGADO

Data: 23/09/2026. O TooJunto concluiu o desenvolvimento funcional do MVP 0.1. A jornada Criar conta → Login → Criar Grupo → Convidar → Aceitar convite → Formar Grupo → Sortear → Iniciar ciclos → Informar pagamento → Confirmar/rejeitar → Concluir ciclo → Avançar ciclos → Encerrar Grupo foi validada por testes automatizados e homologada manualmente pelo PO. A identidade visual oficial também foi incorporada e homologada, e a navegação final foi simplificada com remoção da barra inferior permanente. Princípio de UX confirmado: MENOS É MAIS. Próximo marco: PRIMEIRO PILOTO CONTROLADO.

# 12\. Sprint 8 — Piloto — PRÓXIMO / NÃO INICIADO

- Executar checklist de produção.
- Configurar domínio e HTTPS.
- Configurar backup.
- Validar logs e auditoria.
- Executar teste controlado.
- Selecionar primeiro grupo piloto.
- Acompanhar uso e registrar feedback.
- Priorizar correções antes de ampliar o número de grupos.

Objetivo: preparar o ambiente real e executar o primeiro piloto controlado.

Atividades do Sprint 8: checklist de produção; preparar VPS/ambiente de produção; configurar domínio e HTTPS; configurar variáveis de ambiente; preparar PostgreSQL de produção; deploy Backend; deploy Frontend; configurar fallback SPA para /invites/\*; configurar backup; validar logs e auditoria mínima; executar smoke test em produção; validar convite pelo domínio público; validar jornada mobile em dispositivo real; selecionar o primeiro Grupo piloto; executar piloto controlado; registrar feedback; corrigir bloqueios antes de ampliar o piloto.

Nenhuma atividade operacional do Sprint 8 deve ser marcada como concluída sem evidência.

# 13\. Backlog técnico atualizado

| **ID**  | **Tarefa**                           | **Prioridade** | **Status**                                                                                                                                                |
| ------- | ------------------------------------ | -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DEV-001 | Repositório e estrutura base         | P0             | DONE                                                                                                                                                      |
| DEV-002 | PostgreSQL e estrutura de dados      | P0             | DONE — migrations versionadas com Alembic implantadas e validadas no STAGING                                                                              |
| DEV-003 | Autenticação                         | P1             | DONE                                                                                                                                                      |
| DEV-004 | Criação, consulta e gestão de grupos | P1             | DONE                                                                                                                                                      |
| DEV-005 | Convites e participantes             | P1             | DONE — US-005/US-006/US-007 concluídas                                                                                                                    |
| DEV-006 | Motor de sorteio                     | P1             | DONE — preparação e execução do sorteio concluídas na US-008/US-009.                                                                                      |
| DEV-007 | Ciclos/contemplações                 | P1             | DONE — ciclos, contemplação e progresso concluídos na US-010.                                                                                             |
| DEV-008 | Pagamentos — declaração              | P1             | DONE — US-011 concluída, testada e homologada.                                                                                                            |
| DEV-009 | Confirmação/rejeição de pagamentos   | P1             | DONE — US-012 concluída, testada e homologada.                                                                                                            |
| DEV-010 | Auditoria                            | P1             | BACKLOG                                                                                                                                                   |
| DEV-011 | Testes E2E                           | P1             | DONE — regressão/jornada ponta a ponta validada na US-014D.                                                                                               |
| DEV-012 | Responsividade/UX                    | P1             | DONE no MVP 0.1 — refinamentos US-014A/B/C/E/F homologados; interface mobile simplificada e identidade oficial incorporada; evolução continua por versão. |
| DEV-013 | Deploy produção                      | P1             | PRÓXIMO — Sprint 8                                                                                                                                        |
| DEV-014 | Monitoramento básico                 | P2             | PRÓXIMO — Sprint 8                                                                                                                                        |

# 14\. Dívidas Técnicas

Dívidas técnicas são itens conhecidos que não impedem o funcionamento atual do MVP, mas devem permanecer visíveis e ser tratados quando seu impacto justificar a implementação.

| ID     | Dívida técnica                                                                                                                              | Origem              | Impacto                                                                                                                                                 | Prioridade           | Status                   |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------- | ------------------------ |
| DT-001 | Implementar migrations versionadas com Alembic.                                                                                             | Sprint 0 / Sprint 2 | RESOLVIDO — schema controlado por Alembic; baseline adotada no banco legado sem perda de dados.                                                         | Média                | DONE — Sprint 9 / US-015 |
| DT-002 | Avaliar/criar índice composto em participantes (usuario_id, status, grupo_id).                                                              | US-003.1            | Pode afetar desempenho da consulta Meus Grupos quando o volume crescer.                                                                                 | Baixa/Média          | PENDENTE                 |
| DT-003 | Avaliar constraint única (grupo_id, usuario_id) para impedir participante duplicado.                                                        | US-003.1            | Risco de inconsistência de dados em cenários futuros de concorrência/convites.                                                                          | Média                | PENDENTE                 |
| DT-004 | Substituir usos depreciados de datetime.utcnow().                                                                                           | Testes Backend      | Warnings e futura incompatibilidade com versões mais novas.                                                                                             | Baixa                | PENDENTE                 |
| DT-005 | Eliminar warnings/depreciações relacionados ao TestClient e dependências de testes.                                                         | Testes Backend      | Ruído nos testes e risco futuro de incompatibilidade.                                                                                                   | Baixa                | PENDENTE                 |
| DT-006 | Ampliar testes específicos de autorização e erros 401/403/404/409/422 nos fluxos de grupos.                                                 | US-003.1 / US-004   | Cobertura atual é suficiente para o MVP, mas faltam alguns cenários explícitos de regressão.                                                            | Média                | PENDENTE                 |
| DT-007 | Adicionar teste automatizado de concorrência para criação do convite reutilizável.                                                          | US-005              | A implementação está protegida por lock e constraints, mas falta prova automatizada de chamadas simultâneas.                                            | Baixa/Média          | PENDENTE                 |
| DT-008 | Refinar tratamento de IntegrityError na geração de convites, distinguindo colisão recuperável de erro persistente e limitando retentativas. | US-005              | Reduz risco de laço de retentativa em erro persistente de banco.                                                                                        | Baixa                | PENDENTE                 |
| DT-009 | Ampliar testes Frontend da US-005 para parametrizar todos os estados de Grupo que não permitem convite.                                     | US-005              | Cobertura atual usa FORM(A)NDO como representante; ampliar melhora regressão futura.                                                                    | Baixa                | PENDENTE                 |
| DT-010 | Validar/configurar fallback SPA para acesso direto a /invites/\* no ambiente de produção.                                                   | US-006              | Sem fallback, um link de convite aberto diretamente pode receber 404 do servidor antes de o React carregar.                                             | Alta antes do piloto | PENDENTE                 |
| DT-011 | Reavaliar a navegação centralizada em App.tsx e a necessidade de biblioteca de rotas quando a complexidade justificar.                      | US-006              | A concentração de navegação aumenta a responsabilidade do App.tsx, mas não bloqueia o MVP atual.                                                        | Baixa                | PENDENTE                 |
| DT-012 | Adicionar constraint única no banco para pagamento por (ciclo_id, pagador_id).                                                              | US-011              | A API evita duplicidade com lock transacional do Grupo, mas a unicidade ainda não é garantida por constraint no banco.                                  | Média                | PENDENTE                 |
| DT-013 | Avaliar constraint/índice de banco para unicidade do nome do Grupo por Gestor entre grupos não encerrados/cancelados.                       | US-014B             | A aplicação protege criação/renomeação com lock transacional por Gestor, mas escritas diretas ou caminhos futuros fora desse lock podem violar a regra. | Média                | PENDENTE                 |
| DT-014 | Tornar usuarios.telefone NOT NULL no banco por migration quando a estratégia de migrations estiver definida.                                | US-014A             | Novos cadastros exigem telefone no contrato, porém a coluna permanece nullable por compatibilidade sem migration nesta etapa.                           | Baixa/Média          | PENDENTE                 |

Regra de gestão: ao encerrar cada User Story, novas dívidas técnicas identificadas devem ser registradas nesta seção com ID, origem, impacto, prioridade e status. Dívida técnica não deve ser implementada automaticamente se não bloquear segurança, consistência, evolução ou o piloto.

## 14.1 Situação final de warnings e dívidas não bloqueantes

Regressão final registrou 467 warnings no Backend, principalmente usos depreciados de datetime.utcnow(), além de avisos de compatibilidade futura Starlette/httpx e AnyIO e aviso ambiental do cache do pytest por falta de permissão. Esses avisos não bloquearam a homologação funcional.

Após a Sprint 9, DT-001 (migrations/Alembic) está CONCLUÍDA. Permanecem abertas: coluna usuarios.telefone ainda nullable no banco; avaliação de constraint/índice para unicidade do nome do Grupo por Gestor; unicidade de pagamento por (ciclo_id, pagador_id); warnings/depreciações e demais itens registrados na tabela de dívidas técnicas.

# 15\. Definition of Done

- Funcionalidade implementada.
- Testes automatizados relevantes passando.
- Revisão independente realizada.
- Permissões validadas.
- Tratamento de erro implementado.
- Interface responsiva quando houver Frontend.
- Homologação manual do PO aprovada para fluxos de usuário.
- Sem bug crítico conhecido.
- Commit e push realizados após aprovação.
- Documentação atualizada pelo responsável do projeto.

# 16\. Critérios para liberar o MVP

- DONE — Cadastro e login funcionando.
- DONE — Criação, consulta e gestão de grupos funcionando.
- DONE — Entrada em Grupo funcionando.
- DONE — Convites funcionando.
- DONE — Sorteio reproduzível e registrado.
- DONE — Ciclos, contemplações, avanço e conclusão funcionando.
- DONE — Declaração, confirmação e rejeição de pagamento funcionando.
- ADIADO — Histórico dedicado removido do critério do MVP 0.1 e transferido para MVP 0.3.
- DONE — Controle de acesso funcionando.
- DONE — Fluxo principal responsivo e homologado em simulação mobile; validação em dispositivo real ocorrerá no Sprint 8.
- DONE — Regressão final: Backend 157/157 e Frontend 86/86; TypeScript e build aprovados.
- DONE — Identidade visual oficial incorporada e navegação final simplificada, sem barra inferior permanente; homologação visual do PO aprovada.
- PENDENTE SPRINT 8 — selecionar primeiro Grupo piloto.

Status de liberação funcional: MVP 0.1 FUNCIONALMENTE HOMOLOGADO. Permanecem pendentes somente as atividades operacionais do Sprint 8 necessárias antes do piloto real.

# 17\. Estratégia de testes

| **Momento**     | **Teste**             | **Objetivo**                                         |
| --------------- | --------------------- | ---------------------------------------------------- |
| Durante cada US | Unitário/API/Frontend | Detectar regressões e validar regras.                |
| Fim de cada US  | Revisão independente  | Verificar segurança, contratos e efeitos colaterais. |
| Fim de fluxo    | Homologação do PO     | Validar comportamento real no navegador.             |
| Sprint 7        | E2E                   | Validar jornada inteira.                             |
| Antes do piloto | Usabilidade           | Verificar compreensão pelo público-alvo.             |
| Piloto          | Observação real       | Validar valor e continuidade.                        |

# 18\. Métricas do desenvolvimento

- Tempo para concluir a jornada principal.
- Quantidade de bugs críticos.
- Taxa de falha por fluxo.
- Tempo médio para corrigir bloqueios.
- Percentual de testes críticos passando.
- Quantidade de funcionalidades fora do escopo adicionadas sem necessidade — meta: zero.
- Quantidade de US homologadas pelo PO.

# 19\. Gestão de risco

| **Risco**              | **Impacto** | **Mitigação**                                                                |
| ---------------------- | ----------- | ---------------------------------------------------------------------------- |
| Escopo crescer         | Alto        | Congelar MVP e manter backlog separado.                                      |
| Sorteio inconsistente  | Alto        | Regra no Backend + transação + testes.                                       |
| Acesso indevido        | Alto        | Autorização no Backend + testes.                                             |
| UX complexa            | Alto        | Teste com público-alvo antes do piloto.                                      |
| Falha de storage       | Médio       | Storage gerenciado + validação de upload.                                    |
| Custo cloud crescer    | Médio       | Começar pequeno e monitorar consumo.                                         |
| Integrações atrasarem  | Médio       | MVP sem dependências externas críticas.                                      |
| Dívida técnica crescer | Médio       | Registrar explicitamente e atacar apenas quando bloquear evolução/segurança. |

## 19.1 Backlog direcionado ao MVP 0.3

Itens adiados para evolução posterior: Perfil do usuário; edição de dados pessoais; dados para recebimento; chave Pix; copiar chave Pix; futura evolução para Pix Copia e Cola / QR Code; Histórico evoluído; e reavaliação de uma navegação global inferior quando houver destinos suficientes para justificá-la, por exemplo Meus Grupos, Buscar/Explorar e Perfil. Esses itens não pertencem ao escopo do MVP 0.1.

# 20\. Próximo passo — Sprint 8

Prosseguir para o Sprint 8 — preparação do ambiente real e execução do primeiro piloto controlado. O MVP 0.1 está funcionalmente concluído e homologado; produção e piloto ainda não foram iniciados.

O princípio permanece: menos é mais. Cada nova funcionalidade deve existir para validar a jornada principal do MVP, não para antecipar complexidade de versões futuras.

## Anexo A — Registro histórico da US-012 — Confirmar/Rejeitar pagamento e concluir ciclo

- Status: DONE — homologada pelo Product Owner em 22/09/2026.
- O contemplado do ciclo pode confirmar ou rejeitar individualmente pagamentos em AGUARDANDO_CONFIRMACAO; Gestor sem ser contemplado não possui privilégio especial.
- Pagamento rejeitado pode ser informado novamente pelo próprio pagador, reutilizando o registro existente.
- O ciclo somente é concluído quando todos os N−1 pagamentos exigíveis estiverem CONFIRMADO. A conclusão e o avanço para o próximo ciclo ocorrem de forma transacional.
- Após a última confirmação do último ciclo, o Grupo passa para ENCERRADO e todos os ciclos são apresentados como CONCLUIDO.
- API adicionada: POST /groups/{group_id}/cycles/{cycle_number}/payments/{payment_id}/confirm e POST /groups/{group_id}/cycles/{cycle_number}/payments/{payment_id}/reject.
- Contrato das obrigações ampliado com pagamento_id, pode_avaliar e estados CONFIRMADO/REJEITADO; progresso ampliado com grupo_concluido.
- Backend: 138/138 testes aprovados, sem alteração estrutural de banco e sem nova dependência.
- Frontend: ações Confirmar/Rejeitar condicionadas a pode_avaliar=true, modais com prevenção de múltiplos envios, atualização automática do progresso e suporte à nova declaração após rejeição.
- Frontend final: 74/74 testes aprovados, TypeScript e build de produção aprovados.
- Ajuste de UX homologado em Meus Grupos: Sorteio realizado com badge azul e Grupo concluído com badge laranja, mantendo texto explícito e os demais status inalterados.
- DT-012 permanece registrada: avaliar futuramente constraint única no banco para pagamento por (ciclo_id, pagador_id); não bloqueia o MVP.

Registro histórico: a US-012 foi concluída e publicada; a US-013 foi posteriormente descartada/adiada para MVP 0.3 durante o Sprint 7.

# ATUALIZAÇÃO DE REFERÊNCIA — MVP 0.2

Atualização documental: 29/09/2026. Esta seção preserva o conteúdo histórico do MVP 0.1 e registra decisões aprovadas para a evolução do produto.

## Planejamento da evolução — MVP 0.2

O MVP 0.1 permanece congelado como baseline funcional do piloto. O MVP 0.2 será desenvolvido localmente e promovido para a VPS de staging somente após testes e commit/push.

Objetivos do MVP 0.2: (1) notificações in-app; (2) e-mails transacionais para todos os eventos operacionais relevantes e somente aos destinatários necessários; (3) recusa explícita de convite; (4) lembretes de pagamento; (5) integração Landing Page → área autenticada; (6) correção da nitidez da logo; (7) preparação operacional de backup/deploy/migrations necessária para evoluir o schema com segurança.

Fora do escopo: WhatsApp automático, chat, push notification, aplicativo nativo, preferências avançadas de canais, microserviços e filas sem necessidade comprovada.

## Sequência recomendada — MVP 0.2

1\. Fechar Matriz de Eventos × Destinatários × conteúdo × ação/link.

2\. Definir modelo de dados e migration para notificações/recusa de convite.

3\. Implementar NotificationService e persistência in-app.

4\. Implementar UI mínima de notificações e estado lida/não lida.

5\. Integrar provedor de e-mail e templates mínimos.

6\. Conectar todos os eventos operacionais e testar destinatários.

7\. Implementar lembretes de pagamento com regra de disparo definida.

8\. Integrar Landing Page e aplicação.

9\. Corrigir asset/renderização da logo.

10\. Regressão completa local → deploy staging → homologação do PO.

## Roadmap executivo — Sprints do MVP 0.2

O roadmap abaixo delimita o escopo aprovado do MVP 0.2. Novas funcionalidades identificadas durante a implementação devem ser direcionadas ao backlog, salvo correções necessárias para cumprir os critérios de aceite das User Stories já aprovadas.

| Sprint    | Objetivo                                | User Stories                   | Resultado esperado                                                                                                                                                                    |
| --------- | --------------------------------------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sprint 9  | Fundação para evolução segura           | US-015, US-016, US-017         | DONE — migrations versionadas, backup/restore e deploy/rollback seguro validados no STAGING real.                                                                                     |
| Sprint 10 | Fundação das notificações               | US-018, US-019                 | DONE — persistência de notificações e NotificationService desacoplado das regras de negócio, com 207 testes Backend aprovados.                                                        |
| Sprint 11 | Experiência in-app                      | US-020, US-021                 | DONE — central mínima via API, contador de não lidas e controle lida/não lida implementados, com 221 testes Backend aprovados.                                                        |
| Sprint 12 | Comunicação por e-mail                  | US-022, US-023                 | DONE — e-mail transacional centralizado e confiabilidade de entrega implementados, com registro de sucesso/falha, isolamento das operações de domínio e 239 testes Backend aprovados. |
| Sprint 13 | Eventos operacionais do negócio         | US-024, US-025, US-026, US-027 | DONE — convites, formação, recusa explícita, sorteio, ciclos e pagamentos integrados ao mecanismo de notificações; 257 testes Backend aprovados.                                      |
| Sprint 14 | Entrada no produto e refinamento visual | US-028, US-029                 | Integração Landing Page → aplicação e correção da nitidez/renderização da marca.                                                                                                      |
| Sprint 15 | Qualidade, segurança e homologação      | US-030, US-031, US-032         | Regressão completa, testes de segurança/privacidade, deploy e homologação final do MVP 0.2 em staging.                                                                                |

## User Stories aprovadas — MVP 0.2

| US     | Título                                   | Escopo resumido                                                                                                                                                                                                                        |
| ------ | ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| US-015 | Migrations versionadas                   | DONE — Controlar alterações do schema com migrations, substituindo a dependência operacional de create_all() para evoluções futuras.                                                                                                   |
| US-016 | Backup e restauração do PostgreSQL       | DONE — Garantir backup verificável e procedimento documentado de restauração antes de alterações relevantes no banco.                                                                                                                  |
| US-017 | Deploy seguro em Staging                 | DONE — Padronizar atualização, migrations, health checks, smoke tests e rollback da VPS de staging.                                                                                                                                    |
| US-018 | Modelo de notificações                   | DONE — Persistência por usuário implementada na tabela notificacoes, com tipo, título, mensagem, referência contextual, status, created_at e lida_em; migration c4a8e2f6b1d3 validada com upgrade/downgrade e sem schema drift.        |
| US-019 | Serviço de notificações                  | DONE — NotificationService centraliza criação e persistência, valida destinatário e dados, controla commit/refresh/rollback e permanece desacoplado de HTTP e dos canais de entrega.                                                   |
| US-020 | Central mínima de notificações           | DONE — GET /notifications autenticado, com isolamento por usuário, ordenação das mais recentes e contrato mínimo sem exposição de usuario_id.                                                                                          |
| US-021 | Leitura de notificações                  | DONE — GET /notifications/unread-count e PATCH /notifications/{notification_id}/read implementados; leitura idempotente, lida_em persistido e isolamento por usuário.                                                                  |
| US-022 | E-mail transacional                      | DONE — EmailService centralizado com mensagens multipart HTML/texto, template responsivo, link interno opcional, SMTP configurável por ambiente e provedor injetável/testável sem credenciais hardcoded.                               |
| US-023 | Confiabilidade do e-mail                 | DONE — Entregas de e-mail persistidas com sucesso/falha e associação opcional à notificação; ReliableEmailService isola falhas do provedor e usa transação independente. Migration e7d3a9c5f2b4 validada sem schema drift.             |
| US-024 | Notificações de convite e formação       | DONE — Eventos CONVITE_ACEITO, CONVITE_RECUSADO, GRUPO_COMPLETO e GRUPO_CANCELADO centralizados, com notificações in-app e e-mail pós-commit para os destinatários definidos.                                                          |
| US-025 | Recusa explícita de convite              | DONE — POST /invites/{token}/reject implementado com recusa explícita persistida por convite/usuário, idempotência, bloqueio de aceite posterior e notificação ao gestor. Migration f1b6c8d4a2e9.                                      |
| US-026 | Notificações de sorteio e ciclo          | DONE — Eventos SORTEIO_REALIZADO e CICLO_INICIADO integrados pós-commit; todos os integrantes do grupo são notificados sem alterar algoritmo de sorteio ou regras de progressão dos ciclos.                                            |
| US-027 | Notificações de pagamento                | DONE — Eventos PAGAMENTO_VENCENDO, PAGAMENTO_CONFIRMADO e PAGAMENTO_ATRASADO integrados; comunicação restrita ao participante responsável, idempotente e sem alterar regras financeiras. Acionador periódico permanece fora do escopo. |
| US-028 | Landing Page → aplicação                 | Criar a entrada clara da Landing Page para login/cadastro e aplicação TooJunto.                                                                                                                                                        |
| US-029 | Nitidez da marca                         | Corrigir asset/renderização da logo sem redesenhar a identidade visual.                                                                                                                                                                |
| US-030 | Regressão completa MVP 0.1 + 0.2         | Comprovar que a evolução não quebra os fluxos já homologados.                                                                                                                                                                          |
| US-031 | Segurança e privacidade das notificações | Validar isolamento entre usuários/grupos, autorização e ausência de exposição indevida.                                                                                                                                                |
| US-032 | Deploy e homologação do MVP 0.2          | Promover a versão para staging e concluir smoke tests, E2E e homologação do PO.                                                                                                                                                        |

## Governança de execução do MVP 0.2

- Fluxo padrão: Sprint → User Story → Task pequena → implementação → testes automatizados → homologação do PO → DONE → commit/push.
- O desenvolvimento permanece local. A VPS atual é STAGING/PILOTO e recebe somente versões testadas e versionadas.
- A Sprint 15 representa a homologação final do MVP 0.2; marcos utilizáveis das Sprints anteriores podem ser promovidos ao staging para validação integrada.
- WhatsApp automático, chat, push notification, SMS, aplicativo nativo, preferências avançadas de canais, microserviços e filas sem necessidade comprovada permanecem fora do MVP 0.2.
- A Matriz Oficial de Eventos e Notificações do Documento de Requisitos é a referência funcional para destinatários e ações dos eventos do MVP 0.2.

## Critérios de saída — MVP 0.2

Cada evento previsto possui destinatários definidos e testes de autorização/privacidade.

Notificações aparecem no aplicativo e podem ser marcadas como lidas sem poluir a jornada principal.

E-mails são enviados aos destinatários corretos e falhas de entrega não desfazem operações de negócio.

Convite recusado é distinguível de "Agora não".

Landing Page direciona corretamente para entrada/cadastro da aplicação.

Logo é exibida com nitidez adequada em mobile e desktop.

Suíte de regressão do MVP 0.1 permanece aprovada e homologação em staging é concluída.

# Encerramento da Sprint 9 — Fundação para evolução segura

Status: DONE em 28/09/2026. User Stories concluídas: US-015 — Migrations versionadas; US-016 — Backup e restauração PostgreSQL; US-017 — Deploy seguro em STAGING.

Alembic: baseline MVP 0.1 revision 9b2f1c4d7e6a adotada no banco legado do piloto após validação integral do schema. alembic current = 9b2f1c4d7e6a (head) e alembic check = No new upgrade operations detected.

Integridade de dados antes/depois da adoção: usuarios=2, grupos=1, convites=1, participantes=2, ciclos=2, pagamentos=2, contemplacoes=0. Nenhuma perda ou recriação funcional foi observada.

Backup real pré-Alembic preservado no STAGING: toojunto_20260928_224448_pre_alembic.dump, 21.353 bytes, permissões 600, SHA-256 10efcee2d1da163b7592741fb1f05606419832ef8f015b8a8c98ad10e8f3ddb3. O dump foi validado com pg_restore --list.

Deploy controlado: STAGING promovido do commit f9c3dca para o commit homologado 8fc630a97ce9871fd731fe330a7737df073829ea. Backend, PostgreSQL e Frontend permaneceram healthy.

Smoke tests finais: home, rota SPA /invites/smoke-deploy, /api/health e /api/health/db retornaram HTTP 200 internamente e pelo HTTPS público; <www.toojunto.com> permaneceu com redirecionamento 301 para <https://toojunto.com/>.

Resultado de dívida técnica: DT-001 — Implementar migrations versionadas com Alembic — encerrada. As demais dívidas permanecem no backlog técnico e serão tratadas conforme impacto, sem ampliar desnecessariamente o escopo do MVP 0.2.

Próximo passo após a Sprint 9: Sprint 10 — Fundação das notificações (US-018 e US-019), concluída em 29/09/2026.

# Encerramento da Sprint 10 — Fundação das notificações

Status: DONE em 29/09/2026. User Stories concluídas: US-018 — Modelo de notificações; US-019 — Serviço de notificações.

US-018: criada a tabela notificacoes associada ao usuário destinatário, com os campos id, usuario_id, tipo, titulo, mensagem, referencia_contextual, status, created_at e lida_em. Status inicial NAO_LIDA e índice ix_notificacoes_usuario_id.

Alembic: criada a revision c4a8e2f6b1d3, com down_revision 9b2f1c4d7e6a. O ciclo baseline → head → baseline → head foi validado em PostgreSQL 16 local descartável. Head única c4a8e2f6b1d3 e alembic check sem novas operações detectadas.

US-019: criado NotificationService com operação criar_notificacao, centralizando validação, persistência, commit, refresh e rollback. O serviço permanece independente de HTTP/endpoints e ainda não está integrado aos eventos de convites, grupos, sorteios, ciclos ou pagamentos.

Validação final da Sprint 10: 207 testes Backend aprovados, 0 falhas. Nenhum e-mail, WhatsApp, push, endpoint ou alteração de Frontend foi antecipado. STAGING/VPS não foi acessado durante a Sprint 10.

Próximo passo: iniciar a Sprint 11 — Experiência in-app (US-020 e US-021), conforme o roadmap aprovado do MVP 0.2.

# Encerramento da Sprint 11 — Experiência in-app

Status: DONE em 29/09/2026. User Stories concluídas: US-020 — Central mínima de notificações; US-021 — Leitura de notificações.

US-020: criado GET /notifications autenticado. O destinatário é derivado exclusivamente do token, as notificações são ordenadas por created_at DESC e id DESC e o contrato não expõe usuario_id.

US-021: criados GET /notifications/unread-count e PATCH /notifications/{notification_id}/read. A primeira leitura altera o status para LIDA e registra lida_em; leituras repetidas são idempotentes e preservam o timestamp original. Notificações inexistentes ou de outro usuário retornam 404.

Validação final: 221 testes Backend aprovados, 0 falhas. Alembic permanece em c4a8e2f6b1d3 (head), com uma única head e sem schema drift. Nenhuma migration adicional foi necessária. STAGING/VPS não foi acessado.

Próximo passo após a Sprint 11: Sprint 12 — Comunicação por e-mail (US-022 e US-023), concluída em 29/09/2026.

# Encerramento da Sprint 12 — Comunicação por e-mail

Status: DONE em 29/09/2026. User Stories concluídas: US-022 — E-mail transacional; US-023 — Confiabilidade do e-mail.

US-022: implementado EmailService centralizado, SmtpEmailProvider e contrato EmailProvider injetável. As mensagens são multipart HTML/texto, com template responsivo, conteúdo dinâmico escapado e link de ação opcional baseado na URL pública configurada. Nenhuma integração com eventos de negócio foi antecipada.

US-023: criada a tabela entregas_email para registrar tentativas, sucesso/falha, horário, erro sanitizado e associação opcional à notificação. O ReliableEmailService utiliza sessão/transação própria, impedindo que falhas do provedor revertam operações de domínio já concluídas ou removam notificações in-app.

Alembic: criada a revision e7d3a9c5f2b4, com down_revision c4a8e2f6b1d3. Upgrade, downgrade e reaplicação foram validados; existe uma única head e alembic check não detecta novas operações.

Validação final da Sprint 12: 239 testes Backend aprovados, 0 falhas. Nenhum e-mail real foi enviado; não foram implementados retry, fila, worker, WhatsApp, SMS, push ou integrações com eventos. STAGING/VPS não foi acessado durante a Sprint 12.

Próximo passo após a Sprint 12: Sprint 13 — Eventos operacionais do negócio (US-024, US-025, US-026 e US-027), concluída em 29/09/2026.

# Encerramento da Sprint 13 — Eventos operacionais do negócio

Status: DONE em 29/09/2026. User Stories concluídas: US-024 — Notificações de convite e formação; US-025 — Recusa explícita de convite; US-026 — Notificações de sorteio e ciclos; US-027 — Notificações financeiras.

US-024: criada a camada central de eventos de notificação. CONVITE_ACEITO, CONVITE_RECUSADO, GRUPO_COMPLETO e GRUPO_CANCELADO utilizam NotificationService e a infraestrutura confiável de e-mail, sempre após o commit da operação principal e somente para os destinatários definidos.

US-025: implementado POST /invites/{token}/reject. A recusa explícita é autenticada, persistida por convite e usuário, idempotente e impede aceite posterior do mesmo convite. "Agora não" permanece sem efeito persistente. Foi criada a tabela recusas_convite pela migration f1b6c8d4a2e9, com down_revision e7d3a9c5f2b4.

US-026: os eventos SORTEIO_REALIZADO e CICLO_INICIADO foram integrados pós-commit. Todos os integrantes do grupo recebem a comunicação correspondente, sem alteração do algoritmo, da ordem sorteada ou das regras existentes de criação e progressão dos ciclos.

US-027: implementados os eventos PAGAMENTO_VENCENDO, PAGAMENTO_CONFIRMADO e PAGAMENTO_ATRASADO. As notificações são restritas ao participante responsável e preservam valores, vencimentos, estados financeiros e progressão dos ciclos. A operação interna de lembretes/atrasos é idempotente.

Pendência operacional futura: como o sistema ainda não possui scheduler/cron/worker, a execução automática periódica de lembretes de vencimento e atrasos dependerá de um acionador futuro. A operação idempotente necessária já está disponível e essa pendência não bloqueia a Sprint 13.

Validação final da Sprint 13: 257 testes Backend aprovados, 0 falhas. Alembic permanece com uma única head f1b6c8d4a2e9 e alembic check sem novas operações detectadas. Nenhum e-mail real foi enviado e STAGING/VPS não foi acessado durante a Sprint 13.

Próximo passo: iniciar a Sprint 14 — Entrada no produto e refinamento visual (US-028 e US-029), conforme o roadmap aprovado do MVP 0.2.

# ATUALIZAÇÃO DE REFERÊNCIA — MVP 0.3

Atualização documental: 30/09/2026. Esta seção consolida o escopo aprovado da versão de lançamento MVP 0.3 e passa a ser a referência operacional para sua execução. O conteúdo das MVPs 0.1 e 0.2 permanece preservado como histórico.

## 21\. Escopo e requisitos da MVP 0.3

Objetivo: concluir a versão de lançamento do TooJunto para piloto real controlado, preservando a simplicidade radical e incorporando somente os requisitos necessários para facilitar o pagamento, concluir qualidade/segurança e realizar o Go-Live.

| ID     | Requisito                          | Descrição                                                                                                                                                                      |
| ------ | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| RF-020 | Chave Pix opcional                 | Permitir ao usuário cadastrar e atualizar uma chave Pix. O preenchimento é opcional e sua ausência não impede cadastro, login, participação em grupos ou pagamento.            |
| RF-021 | Exibir chave Pix do contemplado    | No contexto de pagamento, exibir a chave Pix do contemplado somente quando houver chave cadastrada e o usuário estiver autorizado a visualizar o grupo/ciclo.                  |
| RF-022 | Copiar chave Pix                   | Disponibilizar a ação simples "Copiar chave", usando o clipboard do navegador/dispositivo e apresentando feedback curto de sucesso ou erro.                                    |
| RF-023 | Pagamento sem chave Pix            | Quando o contemplado não possuir chave Pix cadastrada, preservar integralmente o fluxo de informar pagamento por outro meio combinado entre os participantes.                  |
| RF-024 | Qualidade, segurança e privacidade | Concluir a regressão e as pendências de autorização, isolamento entre usuários/grupos e privacidade previstas para a Sprint 15 da MVP 0.2, incluindo a proteção da chave Pix.  |
| RF-025 | Entrada pelo site                  | Antes do Go-Live, ajustar a Landing Page para direcionar claramente para login e criação de conta. O ajuste será feito na etapa final de lançamento e não terá sprint própria. |
| RF-026 | Go-Live                            | Promover a versão homologada para o ambiente definitivo do piloto com backup, migrations, health checks, smoke tests e rollback readiness.                                     |

## 22\. Regras de negócio complementares — MVP 0.3

- RN-021 — A chave Pix é opcional e não é requisito de entrada ou permanência no TooJunto.
- RN-022 — O TooJunto apenas apresenta a chave informada pelo próprio usuário; não valida titularidade bancária nem existência da chave junto ao sistema Pix.
- RN-023 — A chave Pix do contemplado somente pode ser disponibilizada no contexto do grupo/ciclo para usuários autorizados.
- RN-024 — A ausência de chave Pix nunca bloqueia a declaração de pagamento.
- RN-025 — O pagamento continua sendo realizado fora do TooJunto e diretamente ao contemplado.
- RN-026 — Pix integrado, QR Code, Pix Copia e Cola gerado pela plataforma, iniciação de pagamento e custódia permanecem fora da MVP 0.3.
- RN-027 — Monetização, gestor remunerado, programa de parceiros, marketplace e mecanismos de crescimento permanecem fora desta release.

## 23\. Planejamento das Sprints — MVP 0.3

A MVP 0.3 será executada em três sprints. O ajuste da Landing Page permanece deliberadamente no final da Sprint 18, imediatamente antes do Go-Live, sem sprint exclusiva.

| Sprint    | Objetivo                                 | User Stories           | Entregas principais                                                                                                                                       | Gate / resultado esperado                                                      |
| --------- | ---------------------------------------- | ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Sprint 16 | Pix opcional e experiência de pagamento  | US-033, US-034, US-035 | Cadastro/edição da chave Pix; exibição contextual ao pagador; copiar chave; fallback sem chave.                                                           | Fluxo Pix auxiliar homologado sem transformar o TooJunto em meio de pagamento. |
| Sprint 17 | Qualidade, segurança e privacidade       | US-036, US-037         | Regressão completa; autorização; isolamento entre usuários/grupos; privacidade da chave Pix; tratamento das pendências bloqueantes herdadas da Sprint 15. | Zero bug bloqueante conhecido e controles críticos aprovados.                  |
| Sprint 18 | Release candidata, homologação e Go-Live | US-038, US-039, US-040 | Release candidata em STAGING; homologação ponta a ponta; ajuste final Landing Page → login/cadastro; backup/migrations/health/smoke/rollback; Go-Live.    | Gate de Go-Live aprovado e piloto real liberado.                               |

## 24\. User Stories previstas — MVP 0.3

| US     | Título                                     | História / objetivo                                                                                                        | Critérios de aceite resumidos                                                                                                             |
| ------ | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| US-033 | Cadastrar/editar chave Pix opcional        | Como usuário, quero cadastrar ou alterar minha chave Pix para facilitar o recebimento quando eu for contemplado.           | Campo opcional; ausência não bloqueia cadastro/uso; persistência segura; usuário altera apenas sua própria chave.                         |
| US-034 | Visualizar chave Pix do contemplado        | Como participante pagador, quero visualizar a chave Pix do contemplado para realizar o pagamento no meu banco.             | Exibir somente se cadastrada; somente a integrantes autorizados do grupo/ciclo; sem exposição pública.                                    |
| US-035 | Copiar chave Pix e manter fallback         | Como participante, quero copiar a chave Pix com um toque e continuar o pagamento mesmo quando não houver chave cadastrada. | Botão "Copiar chave" + feedback; sem chave, fluxo "Informar pagamento" permanece disponível.                                              |
| US-036 | Regressão completa da versão de lançamento | Como PO, quero comprovar que as evoluções das MVPs 0.1, 0.2 e 0.3 não quebraram a jornada já homologada.                   | Suítes Backend/Frontend aprovadas; jornada principal E2E validada; mobile e estados críticos revisados.                                   |
| US-037 | Segurança e privacidade para Go-Live       | Como PO, quero validar autorização, isolamento e privacidade antes de liberar usuários reais.                              | Testes de acesso indevido; isolamento entre grupos/usuários; chave Pix protegida; sem exposição indevida em API/logs/interface.           |
| US-038 | Release candidata e homologação final      | Como PO, quero uma release candidata implantada em STAGING para homologar a jornada completa antes do lançamento.          | Deploy controlado; migrations; health checks; smoke tests; homologação ponta a ponta aprovada.                                            |
| US-039 | Ajustar Landing Page para lançamento       | Como visitante, quero entrar ou criar minha conta diretamente a partir da Landing Page.                                    | CTAs "Entrar" e "Criar minha conta" apontam corretamente para a aplicação; mobile validado; executada somente após homologação funcional. |
| US-040 | Go-Live do piloto real                     | Como PO, quero promover a versão homologada para o ambiente definitivo para iniciar o piloto real controlado.              | Backup final; versão/commit identificados; migrations controladas; health/smoke aprovados; rollback disponível; liberação do piloto.      |

## 25\. Dependências e sequência de execução

1. Sprint 16 deve estar homologada antes do fechamento da regressão da Sprint 17.
2. Sprint 17 é gate obrigatório para a release candidata.
3. A Landing Page será ajustada somente depois da homologação funcional da release candidata, dentro da Sprint 18.
4. O Go-Live somente ocorre após aprovação dos gates funcionais, de segurança, operação e rollback.

## 26\. Gate de Go-Live — MVP 0.3

- US-033 a US-040 concluídas e homologadas conforme aplicável.
- Jornada Criar conta → Criar Grupo → Convidar → Entrar → Sortear → Ciclos → Pagamentos → Encerrar Grupo aprovada.
- Nenhum bug bloqueante conhecido.
- Autorização, isolamento entre usuários/grupos e privacidade da chave Pix aprovados.
- Landing Page direciona corretamente para login/cadastro.
- Backup, migrations, health checks, smoke tests e rollback readiness validados.
- Ambiente liberado para aproximadamente 10 grupos pequenos de pessoas conhecidas.

## 27\. Pós-Go-Live e validação

O piloto deverá observar formação dos grupos, compreensão do sorteio e dos ciclos, pagamentos informados/confirmados, dificuldades de uso, necessidade de suporte e intenção de continuidade. Monetização e crescimento serão decididos somente após evidência obtida no piloto. O princípio permanece: menos é mais.
