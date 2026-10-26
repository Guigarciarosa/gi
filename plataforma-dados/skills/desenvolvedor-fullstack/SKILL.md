---
name: desenvolvedor-fullstack
description: Desenvolve as aplicações em volta da plataforma de dados — portais de clientes, apps de campo, formulários que substituem planilhas, fluxos de aprovação, API de dados, analytics embutido (Metabase, Superset, Power BI Embedded) e assistentes de linguagem natural — com TypeScript/React/Next.js ou Python/FastAPI, PostgreSQL, login OIDC e deploy em contêiner no ZimaOS ou em AWS, GCP, Azure e OCI. Use quando a necessidade do cliente vai além de painéis.
---

# Skill — Desenvolvedor Full Stack

## Primeiro: precisa mesmo de software?
| Necessidade | Primeira opção | Quando partir para sob medida |
|---|---|---|
| Ver números | Painel no BI | Nunca só por isso |
| Painel para clientes externos | Embedded do BI com token assinado | Marca própria, regras complexas, muitos tenants |
| Substituir planilha | Formulário low-code (NocoDB, Appsmith, AppSheet, Power Apps) gravando no PostgreSQL | Validação complexa, offline, muitos usuários |
| Aprovação | n8n + formulário, ou Power Automate | Várias alçadas, auditoria, prazos |
| Dados para parceiro | Exportação agendada (SFTP, arquivo) | Consulta sob demanda → API |
| App de campo | AppSheet ou Power Apps | Offline de verdade, câmera, GPS, muitos usuários → PWA |

## Stack padrão
| Camada | Padrão | Alternativas |
|---|---|---|
| Front-end | Next.js (React + TypeScript) ou React + Vite; Tailwind | HTMX + templates (time Python) |
| API | FastAPI + Pydantic + SQLAlchemy/Alembic (mesmo ecossistema Python dos dados) | Node (Fastify ou NestJS + Prisma), .NET minimal APIs |
| Banco | PostgreSQL, schema `app_*` separado da gold | — |
| Login | OIDC: Keycloak ou Authentik no ZimaOS; Entra ID ou Google para clientes corporativos | Auth0, Clerk, Cognito, Firebase Auth |
| Tarefas e filas | n8n; Celery ou RQ com Redis/Valkey | Cloud Tasks, SQS, Service Bus |
| Data apps internos | Streamlit, Evidence | Dash |
| Testes | pytest, Vitest, Playwright | — |

## Analytics embutido
| Ferramenta | Como | Segurança por linha | Custo |
|---|---|---|---|
| Metabase (open source) | Static embedding: iframe com JWT assinado no servidor, parâmetros travados | parâmetro do tenant travado no token | grátis (com selo do Metabase); embedding interativo é pago |
| Apache Superset | Embedded SDK + guest token | regras de RLS no guest token | grátis |
| Power BI Embedded | "App owns data" com service principal e embed token | RLS por papel e identidade efetiva | capacidade Fabric F ou SKU A (F2 a partir de ~US$ 260/mês; confirme) |
| Looker Studio | Relatório incorporado | sem RLS confiável para usuário externo | grátis; só para dados públicos ou agregados |
| Gráficos próprios | API + ECharts ou Recharts | filtro na API | horas de desenvolvimento |

Regra: o token é gerado no servidor, expira em minutos e o tenant vem da sessão autenticada, nunca de parâmetro da URL.

## Multi-tenant
- Até algumas dezenas de tenants: coluna `tenant_id` + RLS no PostgreSQL e o tenant definido por transação:
  ```sql
  ALTER TABLE app_pedidos ENABLE ROW LEVEL SECURITY;
  CREATE POLICY isolamento ON app_pedidos
    USING (tenant_id = current_setting('app.tenant', true)::uuid);  -- sem tenant definido: nenhuma linha
  -- na API, dentro da transação de cada requisição:
  SELECT set_config('app.tenant', :tenant_da_sessao, true);
  ```
  A API conecta com um papel sem `BYPASSRLS` e que não é dono das tabelas.
- Tenants grandes ou contratos que exigem separação: schema ou banco por tenant.
- Teste automatizado obrigatório: o usuário do tenant A tenta ler dado do B e precisa falhar.

## API de dados
- REST com JSON, paginação por cursor, filtros explícitos e cache (`ETag`).
- Autenticação por chave com escopo e rotação, ou OAuth client credentials; limite por chave (responde 429).
- Lê só da gold/marts com papel somente leitura; nunca do ERP.
- OpenAPI gerado automaticamente (FastAPI faz) e versão no caminho (`/v1`).
- Log de acesso (quem consultou o quê e quando) para a LGPD.

## Assistente em linguagem natural (texto → SQL)
1. O modelo vê só a camada semântica (marts e descrição das métricas), não o banco inteiro.
2. Papel somente leitura, `statement_timeout`, `LIMIT` forçado e esquemas permitidos.
3. Validar o SQL antes de executar (parser como o sqlglot) e bloquear DDL e DML.
4. Mostrar a consulta e a fonte junto da resposta; registrar perguntas sem resposta para o Analista.
5. Dado sensível: modelo local (Ollama) ou API com contrato sem treino, conforme decisão do Cyber e do Cientista.

## Hospedagem por porte
| Porte | Onde | Observação |
|---|---|---|
| P | ZimaOS: Docker Compose + Cloudflare Tunnel (HTTPS sem abrir portas) | backup do banco entra na rotina do DBA |
| P/M na cloud | Cloud Run (GCP), Container Apps (Azure), ECS Fargate (AWS), Container Instances (OCI) | escala a zero onde houver |
| G | Kubernetes gerenciado, só se o cliente já tiver equipe para operar | — |
Front-end estático: Cloudflare Pages, S3 + CloudFront, Firebase Hosting ou Azure Static Web Apps.

## Estimativa de esforço (horas)
| Item | Simples | Médio | Complexo |
|---|---|---|---|
| Projeto base (repositório, login OIDC, CI, deploy) | 12 | 24 | 40 |
| Tela de listagem ou consulta | 3 | 6 | 12 |
| Formulário com validação e histórico | 4 | 8 | 16 |
| Fluxo de aprovação (por fluxo) | 8 | 16 | 32 |
| Endpoint de API | 2 | 4 | 8 |
| Analytics embutido (por painel, com RLS) | 4 | 8 | 16 |
| Multi-tenant com RLS e testes de isolamento | 8 | 16 | 32 |
| App de campo offline (PWA) | 40 | 80 | 160 |
| Assistente texto → SQL com guarda-corpos | 16 | 32 | 64 |

## Antipadrões
- App para o que um painel resolve.
- Chave de API ou segredo do BI no front-end.
- Tenant vindo da URL ou do corpo da requisição.
- Aplicação lendo o banco do ERP.
- Nenhum teste de isolamento entre clientes.
- Formulário que perde o que foi digitado quando a conexão cai (guarde rascunho local).

## Referências
`conhecimento/bancos-de-dados/postgresql.md` (RLS, pool de conexões), `redis-valkey.md` (cache e filas), `bancos-vetoriais.md` (busca semântica em apps).
