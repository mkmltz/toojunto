# TooJunto — Plano de Desenvolvimento MVP 0.1

**Versão:** 0.11  
**Data:** 23 de setembro de 2026  
**Status:** Em execução — núcleo funcional concluído; US-013 descartada pelo PO; US-014 em preparação para o piloto.  
**Objetivo:** construir, testar e colocar o MVP em piloto com o menor escopo possível.

## 1. Princípios do produto e desenvolvimento

- Jornada principal: **Criar → Convidar → Entrar → Pagar → Registrar → Sortear → Acompanhar**.
- Priorizar validação com usuários reais.
- Mobile first e linguagem simples para usuários com baixo letramento digital.
- **Menos é mais.**
- Corrigir bloqueios e problemas reais antes de adicionar funcionalidades.
- O TooJunto não movimenta o dinheiro: pagamentos ocorrem diretamente entre participantes.
- Backend é a fonte das regras de negócio; frontend não deve recalcular regras críticas.
- Fluxo operacional: Backlog → Sprint → US → Card/Prompt → backend → frontend → homologação PO → documentação → commit/push manual → Done.
- Agents devem parar antes da implementação se detectarem mudança arquitetural, alteração estrutural de banco, nova dependência, mudança de regra de negócio, alteração incompatível de contrato ou trabalho fora do escopo.

## 2. Status das User Stories

| Sprint | US | Funcionalidade | Status |
|---|---|---|---|
| 1 | US-001 | Criar conta | DONE |
| 1 | US-002 | Login, sessão, proteção de rotas e logout | DONE |
| 2 | US-003 | Criar Grupo | DONE |
| 2 | US-003.1 | Meus Grupos e detalhes | DONE |
| 2 | US-004 | Editar/cancelar Grupo | DONE |
| 3 | US-005 | Convidar participantes | DONE |
| 3 | US-006 | Aceitar/recusar convite e entrar no Grupo | DONE |
| 3 | US-007 | Participantes e formação do Grupo | DONE |
| 4 | US-008 | Preparar sorteio | DONE |
| 4 | US-009 | Realizar sorteio e registrar ordem | DONE |
| 5 | US-010 | Ciclos, contemplação e progresso | DONE |
| 6 | US-011 | Registrar pagamento | DONE |
| 6 | US-012 | Confirmar/rejeitar pagamento e concluir ciclo | DONE |
| 7 | US-013 | Histórico e acompanhamento | **DESCARTADA PELO PO** |
| 7 | US-014 | Homologação e refinamento para piloto | **EM EXECUÇÃO** |

## 3. Estado funcional atual

### Grupos
- Gestor é automaticamente participante e ocupa uma vaga.
- `quantidade_ciclos = quantidade_participantes`.
- `valor_premio = valor_cota × quantidade_participantes`, calculado no Backend.
- Cancelamento é lógico.
- Detalhes são recarregados do Backend após nova sessão/F5.

### Convites
- Convite único e reutilizável por Grupo.
- Token seguro.
- Aceite protegido e concorrência da última vaga protegida por transação.
- Convite público expõe informação mínima.
- Link direto `/invites/{token}` deve funcionar em produção; fallback SPA é obrigatório antes do piloto (DT-010).

### Sorteio
- Gestor ocupa a posição 1.
- Posições 2..N são sorteadas entre os demais participantes.
- Sorteio definitivo é persistido.
- Calendário usa `data_inicio + (posição - 1) × 30 dias corridos`.
- Status visual `ATIVO` é apresentado ao usuário como **Em andamento**.
- Fluxo de sorteio no frontend usa modal única: Preparar sorteio → Realizar sorteio ou Cancelar.

### Ciclos
- Ciclo atual e calendário são derivados da ordem sorteada e da data de início.
- Ciclo não avança automaticamente pela data.
- Avanço depende da conclusão das obrigações de pagamento.

### Pagamentos
- Pagamento é direto entre participante e contemplado.
- Prazo esperado: **5 dias antes da data prevista do ciclo**.
- Janela crítica de 5 a 1 dia deve ser comunicada ao usuário.
- Pagador declara apenas a própria obrigação.
- Declaração gera `AGUARDANDO_CONFIRMACAO`.
- Contemplado pode confirmar ou rejeitar.
- Pagamento rejeitado pode ser informado novamente.
- Ciclo conclui apenas quando todos os N−1 pagamentos exigíveis estão `CONFIRMADO`.
- Último ciclo concluído encerra o Grupo.
- Estados relevantes: `PENDENTE`, `ATRASADO`, `AGUARDANDO_CONFIRMACAO`, `CONFIRMADO`, `REJEITADO`.

## 4. US-013 — decisão de produto

**Status: DESCARTADA PELO PO após homologação.**

Motivo: o Histórico duplicava informações já presentes na tela do Grupo e aumentava a complexidade da interface.

- Alterações frontend e backend exclusivas da US-013 foram revertidas antes de commit/push.
- Backend após reversão: **138/138 testes**.
- Frontend após reversão: **76/76 testes**, TypeScript e build aprovados.
- Histórico fica no backlog da **MVP 0.3**.
- Só deve retornar quando houver valor funcional suficiente para justificar uma área própria.

## 5. US-014 — Homologação e refinamento para piloto

### US-014A — Convites e cadastro — ANTES DO PILOTO

#### 1. WhatsApp deve receber link utilizável
Corrigir o compartilhamento para que a mensagem enviada ao WhatsApp contenha uma URL clicável do convite. Preservar e-mail e demais mecanismos existentes.

#### 2. Melhorar mensagem do convite
Mensagem-base:

> Você foi convidado por [nome do gestor] para participar de uma caixinha digital no grupo [nome do grupo] — TooJunto.

A tela do convite também deve identificar o Gestor e orientar:

> Caso você ainda não tenha conta na plataforma TooJunto, clique em Criar conta.

#### 3. Telefone obrigatório
- Telefone passa a ser obrigatório na criação da conta.
- O MVP 0.1 não precisa enviar mensagens automaticamente.

#### 4. Regras e confirmação de senha
- Exibir regras de senha de forma clara.
- Adicionar confirmação de senha.
- Bloquear envio quando os campos forem diferentes.
- Usar mensagens específicas.

### US-014B — Criação e integridade do Grupo — ANTES DO PILOTO

#### 5. Data de início
A regra já existe. Melhorar apenas o feedback:

> A data de início do grupo não pode ser menor que a data de hoje.

#### 6. RN-GRP — Unicidade do nome por Gestor
- Mesmo Gestor não pode manter simultaneamente dois grupos não encerrados/cancelados com o mesmo nome.
- Comparação ignora maiúsculas/minúsculas e espaços adicionais.
- Gestores diferentes podem usar o mesmo nome.
- Nome pode ser reutilizado após `ENCERRADO` ou `CANCELADO`.

Mensagem:

> Você já possui um grupo ativo chamado “[nome]”. Escolha outro nome para o novo grupo.

**RN-GRP — Identificação para participantes**
- Todo card de Grupo deve sempre exibir o nome do Gestor.
- Isso vale mesmo sem duplicidade.
- Grupos de Gestores diferentes com o mesmo nome são diferenciados pelo nome do Gestor.

#### 7. RN-GRP — Bloqueio das regras após o primeiro aceite
- Sem aceite: Gestor pode alterar dados/regras.
- Após o primeiro aceite: dados e regras tornam-se imutáveis.
- O Gestor não pode mudar condições aceitas pelos participantes.
- Se não quiser prosseguir, deve cancelar o Grupo conforme as regras de estado aplicáveis.

Esta é uma regra de **integridade do acordo**, não apenas UX.

### US-014C — Simplificação da tela em andamento — ANTES DO PILOTO

Problema atual: excesso e redundância entre:
- Progresso do Grupo;
- Calendário dos ciclos;
- Pagamentos do ciclo atual;
- Ordem de recebimento;
- Regras do Grupo;
- Participantes.

Hierarquia proposta:

1. **Ciclo atual**
   - ciclo X de N;
   - contemplado;
   - data prevista;
   - progresso dos pagamentos;
   - pagamentos do ciclo atual.

2. **Próximos recebimentos**
   - consolidar calendário + ordem de recebimento;
   - mostrar passado/atual/futuro sem duplicação.

3. **Informações do Grupo**
   - regras;
   - participantes;
   - apresentação secundária/expansível quando adequado.

Princípio: **o que está acontecendo agora → quem recebe depois → informações complementares**.

### US-014D — Regressão e homologação final
Depois de 014A–014C:
- executar jornada ponta a ponta;
- validar mobile first;
- validar mensagens e estados de erro;
- validar permissões;
- executar suítes completas;
- TypeScript/build;
- homologação final do PO;
- somente então seguir para Sprint 8 / Piloto.

## 6. Backlog MVP 0.3

### Perfil e edição de dados
- Acesso pelo avatar/iniciais.
- Nome.
- Telefone.
- Senha.
- Dados para recebimento.

### Chave Pix
Não adicionar como obrigatória no cadastro do MVP 0.1.

Planejar em Perfil/Dados para recebimento:
- tipo de chave;
- chave;
- edição;
- privacidade;
- exibição apenas quando necessária.

Evolução futura:
- Copiar chave.
- Pix Copia e Cola.
- QR Code.

### Histórico evoluído
Retomar somente quando puder reunir conteúdo útil, por exemplo:
- eventos do Grupo;
- ciclos;
- pagamentos;
- contemplações;
- comprovantes/relatórios quando aplicável.

## 7. Sprint 8 — Piloto

- Checklist de produção.
- Domínio e HTTPS.
- Backup.
- Logs e auditoria mínima.
- Fallback SPA para `/invites/*`.
- Teste controlado em produção.
- Primeiro grupo piloto.
- Acompanhamento do uso.
- Registrar feedback.
- Corrigir bloqueios antes de ampliar o piloto.

## 8. Dívidas técnicas relevantes

| ID | Item | Prioridade |
|---|---|---|
| DT-001 | Migrations versionadas com Alembic | Média |
| DT-002 | Avaliar índice composto em participantes | Baixa/Média |
| DT-003 | Avaliar unicidade `(grupo_id, usuario_id)` | Média |
| DT-004 | Substituir `datetime.utcnow()` depreciado | Baixa |
| DT-005 | Eliminar warnings/depreciações de testes | Baixa |
| DT-006 | Ampliar testes de autorização/erros | Média |
| DT-007 | Teste de concorrência do convite reutilizável | Baixa/Média |
| DT-008 | Refinar `IntegrityError` na geração de convites | Baixa |
| DT-009 | Ampliar testes frontend de estados sem convite | Baixa |
| DT-010 | Fallback SPA para `/invites/*` em produção | **Alta antes do piloto** |
| DT-011 | Reavaliar navegação centralizada em `App.tsx` | Baixa |
| DT-012 | Avaliar constraint única de pagamento `(ciclo_id, pagador_id)` | Média |

## 9. Definition of Done

- Funcionalidade implementada.
- Testes automatizados relevantes passando.
- Revisão independente realizada.
- Permissões validadas.
- Tratamento de erro implementado.
- Interface responsiva quando houver frontend.
- Homologação manual do PO.
- Sem bug crítico conhecido.
- Documentação atualizada.
- Commit e push somente após aprovação.

## 10. Critérios para liberar o MVP 0.1

- Cadastro/login funcionando.
- Criação, consulta e gestão de Grupos funcionando.
- Convites e entrada no Grupo funcionando.
- Sorteio registrado.
- Ciclos e contemplações funcionando.
- Declaração e confirmação/rejeição de pagamentos funcionando.
- Controle de acesso funcionando.
- Fluxo principal funcionando em celular.
- US-014A/B/C/D concluídas e homologadas.
- DT-010 resolvida no ambiente de produção.
- Testes críticos passando.
- Primeiro grupo piloto selecionado.

**Histórico não é critério de liberação do MVP 0.1.**

## 11. Próximo passo

**Executar US-014A — Convites e cadastro.**

Ordem:
1. US-014A.
2. Homologação do PO.
3. US-014B.
4. Homologação do PO.
5. US-014C.
6. US-014D — regressão e homologação final.
7. Sprint 8 — Piloto.

> Princípio permanente: **menos é mais**. Cada funcionalidade deve resolver um problema concreto da jornada principal.
