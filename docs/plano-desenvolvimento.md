TOOJUNTO

Plano de Desenvolvimento do MVP 0.1

Plano técnico, sprints e ordem de implementação

# 1. Objetivo do desenvolvimento

Entregar uma versão funcional do TooJunto capaz de executar a jornada completa:

Criar → Convidar → Entrar → Pagar → Registrar → Sortear → Acompanhar

O desenvolvimento deve priorizar validação com usuários reais, evitando funcionalidades que não sejam necessárias para testar a hipótese principal do produto.

# 2. Estratégia de desenvolvimento

Construção incremental e vertical: cada sprint entrega uma parte utilizável.

Priorizar primeiro o caminho feliz do usuário.

Testar as regras críticas desde o início.

Evitar perfeccionismo visual antes dos testes de usabilidade.

Usar dados de teste controlados até o piloto.

Publicar em staging antes de produção.

Corrigir problemas que bloqueiem a jornada antes de adicionar funcionalidades.

# 3. Ordem de implementação

# 4. Sprints propostas

Estimativa total de referência: aproximadamente 5–7 semanas de desenvolvimento enxuto, dependendo do time e das decisões técnicas. O prazo é uma estimativa de planejamento, não um compromisso.

# 5. Sprint 0 — Fundação

Criar repositório Git.

Criar estrutura frontend/backend.

Configurar ambiente local.

Configurar PostgreSQL de desenvolvimento.

Criar migrations iniciais.

Configurar lint/format.

Configurar testes automatizados básicos.

Configurar CI.

Definir variáveis de ambiente.

Preparar staging.

Critério de saída: projeto sobe localmente e pipeline executa com sucesso.

# 6. Sprint 1 — Autenticação

Cadastro de usuário.

Login.

Hash seguro de senha.

Token/sessão.

Proteção de rotas.

Logout.

Validação de dados.

Testes unitários e de API.

Critério de saída: usuário consegue criar conta, entrar e acessar área autenticada.

# 7. Sprint 2 — Grupos

Criar grupo.

Definir nome, valor, quantidade de participantes, ciclos e início.

Listar grupos do usuário.

Visualizar grupo.

Definir estados do grupo.

Validar permissões do gestor.

Critério de saída: gestor cria um grupo e consegue acompanhar sua formação.

# 8. Sprint 3 — Convites

Gerar convite único.

Compartilhar convite.

Exibir convite recebido.

Aceitar convite.

Recusar convite.

Atualizar quantidade de participantes.

Impedir entrada acima do limite.

Testar convite expirado/inválido.

Critério de saída: um usuário consegue convidar outra pessoa e ela consegue entrar no grupo.

# 9. Sprint 4 — Sorteio

Verificar grupo completo.

Preparar participantes elegíveis.

Executar sorteio no backend.

Gerar ordem de contemplação.

Persistir resultado em transação.

Registrar data/hora e usuário responsável.

Impedir alteração comum após finalização.

Exibir resultado para participantes.

Critério de saída: grupo completo realiza sorteio e todos visualizam a mesma ordem.

# 10. Sprint 5 — Ciclos e contemplação

Criar ciclo a partir da ordem sorteada.

Identificar contemplado do ciclo.

Registrar contemplação.

Mostrar ciclo atual.

Mostrar progresso.

Permitir consulta dos ciclos anteriores.

Controlar estados do ciclo.

Critério de saída: usuário consegue entender quem recebe, em qual ciclo e qual o progresso.

# 11. Sprint 6 — Pagamentos

Mostrar contemplado e valor.

Mostrar dados de pagamento disponíveis.

Orientar pagamento fora da plataforma.

Registrar declaração de pagamento.

Permitir comprovante opcional.

Confirmar pagamento pelo gestor.

Rejeitar pagamento pelo gestor.

Registrar auditoria.

Atualizar progresso.

Critério de saída: ciclo consegue registrar e confirmar pagamentos sem movimentação financeira pelo TooJunto.

# 12. Sprint 7 — Integração e UX

Executar jornada completa de ponta a ponta.

Revisar todas as 10 telas.

Corrigir navegação.

Revisar mensagens e linguagem.

Validar mobile-first.

Corrigir problemas de acessibilidade.

Testar estados vazios, erros e carregamento.

Executar testes E2E.

Corrigir bugs críticos.

# 13. Sprint 8 — Piloto

Executar checklist de produção.

Configurar domínio e HTTPS.

Configurar backup.

Validar logs e auditoria.

Executar teste controlado.

Selecionar primeiro grupo piloto.

Acompanhar uso.

Registrar feedback.

Priorizar correções antes de ampliar o número de grupos.

# 14. Backlog técnico

# 15. Definition of Done

Funcionalidade implementada.

Code review realizado, quando houver equipe.

Testes automatizados relevantes passando.

Permissões validadas.

Tratamento de erro implementado.

Interface responsiva.

Requisito correspondente atualizado.

Fluxo testado em staging.

Sem bug crítico conhecido.

# 16. Critérios para liberar o MVP

Cadastro e login funcionando.

Criação e entrada em grupo funcionando.

Convites funcionando.

Sorteio reproduzível e registrado.

Ciclos e contemplações funcionando.

Declaração e confirmação de pagamento funcionando.

Histórico básico funcionando.

Controle de acesso funcionando.

Fluxo principal funcionando em celular.

Testes críticos passando.

Primeiro grupo piloto selecionado.

# 17. Estratégia de testes

# 18. Métricas do desenvolvimento

Tempo para concluir a jornada principal.

Quantidade de bugs críticos.

Taxa de falha por fluxo.

Tempo médio para corrigir bloqueios.

Percentual de testes críticos passando.

Quantidade de funcionalidades fora do escopo adicionadas sem necessidade — meta: zero.

# 19. Gestão de risco

# 20. Próximo passo após o plano

O projeto está pronto para sair da documentação e entrar na execução. A primeira atividade é o Sprint 0: criar o repositório, estrutura do projeto, ambientes, banco e pipeline. Depois disso, o desenvolvimento deve seguir verticalmente até entregar a primeira jornada funcional completa.

| Campo | Valor |
| --- | --- |
| Versão | 0.1 |
| Data | 14 de setembro de 2026 |
| Status | Plano inicial |
| Objetivo | Construir, testar e colocar o MVP em piloto com o menor escopo possível. |

| Prioridade | Bloco | Resultado |
| --- | --- | --- |
| P0 | Fundação | Repositório, ambientes, banco, autenticação e CI básico. |
| P1 | Usuários | Cadastro e login. |
| P1 | Grupos | Criação e visualização. |
| P1 | Convites | Geração, compartilhamento e aceite. |
| P1 | Sorteio | Preparação, execução e registro. |
| P1 | Ciclos | Contemplação e progresso. |
| P1 | Pagamentos | Declaração, comprovante opcional e confirmação. |
| P1 | Histórico | Consulta de ciclos, pagamentos e contemplações. |
| P2 | Polimento | Usabilidade, mensagens, acessibilidade e correções. |
| P2 | Piloto | Deploy, monitoramento e suporte. |

| Sprint | Duração alvo | Objetivo | Entrega |
| --- | --- | --- | --- |
| Sprint 0 | 2–3 dias | Preparar projeto | Git, estrutura, ambientes, banco, CI/CD inicial. |
| Sprint 1 | 4–5 dias | Autenticação | Cadastro, login e proteção de rotas. |
| Sprint 2 | 4–5 dias | Grupos | Criar grupo, configurar dados e visualizar grupo. |
| Sprint 3 | 4–5 dias | Convites | Criar convite, aceitar e controlar participantes. |
| Sprint 4 | 4–5 dias | Sorteio | Validar grupo completo, executar e persistir ordem. |
| Sprint 5 | 4–5 dias | Ciclos e contemplação | Abrir ciclo, identificar contemplado e mostrar progresso. |
| Sprint 6 | 5–7 dias | Pagamentos | Registrar, anexar comprovante opcional e confirmar/rejeitar. |
| Sprint 7 | 4–5 dias | Integração e UX | Fluxo completo, mensagens, responsividade e correções. |
| Sprint 8 | 3–5 dias | Piloto | Testes finais, produção e acompanhamento inicial. |

| ID | Tarefa | Prioridade |
| --- | --- | --- |
| DEV-001 | Repositório e estrutura base | P0 |
| DEV-002 | PostgreSQL + migrations | P0 |
| DEV-003 | Autenticação | P1 |
| DEV-004 | CRUD de grupos | P1 |
| DEV-005 | Convites | P1 |
| DEV-006 | Motor de sorteio | P1 |
| DEV-007 | Ciclos/contemplações | P1 |
| DEV-008 | Pagamentos | P1 |
| DEV-009 | Upload de comprovantes | P1 |
| DEV-010 | Auditoria | P1 |
| DEV-011 | Testes E2E | P1 |
| DEV-012 | Responsividade/UX | P1 |
| DEV-013 | Deploy produção | P1 |
| DEV-014 | Monitoramento básico | P2 |

| Momento | Teste | Objetivo |
| --- | --- | --- |
| A cada PR | Unitário/API | Detectar regressões. |
| Final de sprint | Integração | Validar módulo completo. |
| Sprint 7 | E2E | Validar jornada inteira. |
| Antes do piloto | Usabilidade | Verificar compreensão. |
| Piloto | Observação real | Validar valor e continuidade. |

| Risco | Impacto | Mitigação |
| --- | --- | --- |
| Escopo crescer | Alto | Congelar MVP e manter backlog separado. |
| Sorteio inconsistente | Alto | Regra no backend + transação + testes. |
| Acesso indevido | Alto | Autorização no backend + testes. |
| UX complexa | Alto | Teste com público-alvo antes do piloto. |
| Falha de storage | Médio | Storage gerenciado + validação de upload. |
| Custo cloud crescer | Médio | Começar pequeno e monitorar consumo. |
| Integrações atrasarem | Médio | MVP sem dependências externas críticas. |
