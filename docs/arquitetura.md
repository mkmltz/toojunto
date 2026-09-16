TOOJUNTO

Arquitetura Técnica — MVP 0.1

Documento de arquitetura para implementação e validação

# 1. Visão geral

A arquitetura do MVP deve ser pequena e modular, suficiente para cadastro, grupos, convites, sorteio, ciclos, pagamentos declarados e acompanhamento. O TooJunto não movimenta dinheiro no MVP.

Arquitetura: Navegador/Smartphone → Frontend Web → API Backend → PostgreSQL; com armazenamento privado para comprovantes e logs/auditoria.

# 2. Princípios arquiteturais

Manter o MVP pequeno e fácil de alterar.

Preferir aplicação web responsiva a aplicativo nativo.

Separar interface, regras de negócio e persistência.

Usar banco relacional para consistência de grupos, ciclos e pagamentos.

Registrar operações críticas para transparência.

Evitar microserviços no MVP.

Evitar integrações externas não indispensáveis.

Preparar pontos de extensão sem implementar complexidade antecipadamente.

# 3. Stack tecnológica proposta

Kubernetes, microserviços e arquitetura distribuída não são necessários nesta fase.

# 4. Arquitetura lógica

# 5. Módulos do backend

# 6. Modelo de dados

# 7. Sorteio — requisitos técnicos

O sorteio só pode ocorrer quando o grupo estiver completo.

O backend é a autoridade para gerar e registrar o resultado.

O resultado deve ser persistido em transação.

A ordem final recebe data/hora e usuário responsável.

Após finalizado, o resultado não pode ser alterado por operação comum.

Correções administrativas futuras devem gerar auditoria.

# 8. Fluxo técnico de pagamento

1. API identifica contemplado e valor do ciclo.

2. Frontend apresenta os dados de pagamento.

3. Usuário realiza o Pix fora do TooJunto.

4. Usuário registra a declaração.

5. Comprovante opcional é enviado ao storage.

6. Gestor confirma ou rejeita.

7. API atualiza o status e registra auditoria.

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

toojunto/
├── frontend/
│   ├── src/pages/
│   ├── src/components/
│   ├── src/services/
│   └── src/types/
├── backend/
│   ├── app/api/
│   ├── app/domain/
│   ├── app/models/
│   ├── app/schemas/
│   ├── app/services/
│   └── tests/
├── infra/
├── docs/
└── .github/workflows/

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

Prioridade máxima: sorteio, controle de acesso e consistência dos pagamentos.

# 16. Logs e auditoria

Registrar criação de grupo, aceite de convite, sorteio, declaração e confirmação/rejeição de pagamento.

Registrar usuário, data/hora, entidade e resultado.

Não registrar senhas ou dados sensíveis desnecessários.

Manter histórico suficiente para explicar o resultado de um sorteio.

# 17. Escalabilidade

Começar com monólito modular. Separação de serviços só deve ocorrer quando houver necessidade real de escala ou operação.

# 18. Segurança e privacidade — mínimo

Controle de acesso por papel e grupo.

HTTPS.

Hash seguro de senha.

Validação no frontend e backend.

Proteção contra acesso a dados de outro grupo.

Backup do banco.

Política de retenção de comprovantes.

Armazenar apenas dados necessários.

# 19. Custos e infraestrutura inicial

Iniciar com serviços gerenciados e baixo custo, pagando apenas pelo necessário ao piloto. Evitar servidores próprios e infraestrutura antecipada.

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

| Campo | Valor |
| --- | --- |
| Versão | 0.1 |
| Data | 14 de setembro de 2026 |
| Status | Proposta técnica |
| Objetivo | Construir o MVP com simplicidade, baixo custo e possibilidade de evolução. |

| Camada | Tecnologia | Justificativa |
| --- | --- | --- |
| Frontend | React + TypeScript | Ecossistema maduro e adequado para interface responsiva. |
| UI | CSS/Tailwind ou biblioteca leve | Acelera a construção e mantém consistência. |
| Backend | Python + FastAPI | Aderente às competências técnicas e adequado para API. |
| ORM | SQLAlchemy | Separa regras de negócio do acesso ao banco. |
| Banco | PostgreSQL | Relacional e adequado às relações do domínio. |
| Autenticação | JWT + hash seguro | Modelo simples para o MVP. |
| Arquivos | Object Storage compatível com S3 | Separa comprovantes dos dados estruturados. |
| Testes | Pytest + Vitest/React Testing Library | Cobertura das regras e interface. |
| Versionamento | Git | Histórico e colaboração. |
| CI/CD | GitHub Actions | Automação de testes e deploy. |
| Deploy | Cloud gerenciada simples | Reduz operação e evita infraestrutura própria. |

| Componente | Responsabilidade |
| --- | --- |
| Frontend | Telas, navegação, validação básica e comunicação com API. |
| API | Autenticação, autorização, grupos, sorteio, ciclos e pagamentos. |
| Domínio | Regras de negócio independentes da interface. |
| Persistência | PostgreSQL. |
| Storage | Comprovantes de pagamento. |
| Auditoria | Eventos críticos. |
| Observabilidade | Logs e erros. |

| Módulo | Responsabilidades |
| --- | --- |
| auth | Cadastro e login. |
| users | Dados do usuário. |
| groups | Criação, configuração e estados. |
| members | Participantes e convites. |
| draws | Preparação, execução e registro do sorteio. |
| cycles | Ciclos e contemplações. |
| payments | Declaração, comprovante e confirmação/rejeição. |
| audit | Rastreabilidade. |

| Entidade | Campos principais |
| --- | --- |
| USUARIO | id, nome, email, telefone, senha_hash, created_at |
| GRUPO | id, nome, gestor_id, valor_cota, quantidade_participantes, quantidade_ciclos, data_inicio, status, created_at |
| PARTICIPANTE | id, grupo_id, usuario_id, ordem_sorteio, status |
| CONVITE | id, grupo_id, convidado_email/telefone, token, status, created_at, expires_at |
| CICLO | id, grupo_id, numero, data, contemplado_id, status |
| PAGAMENTO | id, ciclo_id, pagador_id, recebedor_id, valor, status, comprovante_url, data_pagamento |
| CONTEMPLACAO | id, ciclo_id, participante_id, valor, status, data |
| AUDITORIA | id, usuario_id, grupo_id, evento, entidade, entidade_id, data_hora, metadata |

| Método | Endpoint | Objetivo |
| --- | --- | --- |
| POST | /auth/register | Criar usuário |
| POST | /auth/login | Autenticar |
| GET | /groups | Listar grupos |
| POST | /groups | Criar grupo |
| GET | /groups/{id} | Consultar grupo |
| POST | /groups/{id}/invites | Criar convite |
| POST | /invites/{token}/accept | Aceitar convite |
| POST | /groups/{id}/draw | Executar sorteio |
| GET | /groups/{id}/cycles | Listar ciclos |
| POST | /cycles/{id}/payments | Declarar pagamento |
| POST | /payments/{id}/confirm | Confirmar pagamento |
| POST | /payments/{id}/reject | Rejeitar pagamento |
| GET | /groups/{id}/history | Consultar histórico |

| Ambiente | Uso |
| --- | --- |
| Local | Desenvolvimento. |
| Staging | Validação integrada. |
| Produção | Piloto real. |

| Nível | Foco |
| --- | --- |
| Unitário | Sorteio, estados, permissões e cálculos. |
| Integração | API + PostgreSQL + storage. |
| E2E | Cadastro, convite, entrada, sorteio e pagamento. |
| Usabilidade | 10 telas com usuários reais. |
| Segurança básica | Autorização, acesso indevido e entradas inválidas. |

| MVP | Evolução se necessária |
| --- | --- |
| Monólito modular | Serviços separados |
| PostgreSQL único | Replicação/read replicas |
| Storage simples | CDN/políticas avançadas |
| Deploy simples | Orquestração |
| Logs básicos | Observabilidade avançada |
| Sem fila | Filas/eventos |
