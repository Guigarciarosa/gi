---
tema: Git e CI/CD em projetos de dados
agentes: [engenheiro, devops, analista, fullstack]
revisado: 2026-10
---

# Git para projetos de dados

## Um repositório por cliente
```text
plataforma-<cliente>/
├── ingestao/            # dlt, conectores, notebooks de Auto Loader
├── dbt/                 # models/, tests/, macros/, dbt_project.yml
├── orquestracao/        # Dagster/Airflow, ou databricks.yml + resources/ (Asset Bundles)
├── migracoes/           # SQL versionado fora do dbt (Snowflake, PostgreSQL)
├── infra/               # OpenTofu/Terraform
├── apps/                # código do Full Stack
├── docs/                # entregáveis dos agentes, ADRs, runbooks
├── .github/workflows/   # CI/CD
├── .pre-commit-config.yaml
├── .gitignore
└── README.md
```
O repositório é do cliente (cláusula de saída): crie na organização dele ou transfira no fim.

## Fluxo de trabalho
- **Trunk-based**: `main` protegida; branches curtas (`feat/fct-vendas`, `fix/carga-se1`); pull request com revisão e CI verde; *squash merge*.
- **Ambientes pelo deploy, não por branch**: PR → ambiente de desenvolvimento (ou efêmero); merge na `main` → produção com aprovação (GitHub Environments).
- Mensagens no padrão Conventional Commits (`feat(dbt): adiciona fct_vendas`); tags SemVer (`v1.4.0`) a cada entrega.
- `CODEOWNERS` define quem revisa cada pasta (ex.: `migracoes/` exige o DBA).

## O que nunca vai para o Git
- Segredos (`.env`, chaves, tokens): **gitleaks** no pre-commit e no CI.
- Dados (CSV, Parquet, dumps) e saídas de notebooks com dados pessoais (`nbstripout`).
- Artefatos gerados:
```gitignore
.env
.venv/
__pycache__/
target/
dbt_packages/
logs/
.databricks/
*.duckdb
*.parquet
*.csv
!dbt/seeds/*.csv
```
(Os seeds do dbt são CSVs pequenos e versionados de propósito: tabelas de-para, metas, feriados.)

## pre-commit
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ["--maxkb=500"]
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.24.0
    hooks:
      - id: gitleaks
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff
      - id: ruff-format
  - repo: https://github.com/sqlfluff/sqlfluff
    rev: 3.3.0
    hooks:
      - id: sqlfluff-lint
        additional_dependencies: ["dbt-postgres", "sqlfluff-templater-dbt"]
```

## CI do dbt só com o que mudou ("slim CI")
```yaml
# .github/workflows/dbt-ci.yml
name: dbt-ci
on: pull_request
jobs:
  dbt:
    runs-on: ubuntu-latest
    env:
      DBT_PROFILES_DIR: ./dbt
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install dbt-core dbt-postgres        # troque pelo adaptador do motor do cliente
      - name: Estado de produção (manifest do último deploy)
        run: mkdir -p estado && cp artefatos/prd/manifest.json estado/   # ou baixe do bucket/artefato do deploy
      - run: dbt deps --project-dir dbt
      - run: dbt build --project-dir dbt --target ci --select state:modified+ --defer --state estado
```
Compara com o `manifest.json` de produção e constrói só os modelos alterados e os que dependem deles, lendo o resto da produção (`--defer`).

## Por plataforma
| Plataforma | Como o Git entra |
|---|---|
| Databricks | Git folders para desenvolver; **Asset Bundles** para implantar; CI com service principal (ver `databricks.md`) |
| Snowflake | dbt + CI com par de chaves; integração Git nativa (`CREATE GIT REPOSITORY`) e schemachange para migrações (ver `snowflake.md`) |
| BigQuery | dbt + CI com Workload Identity Federation (sem chave JSON) |
| Microsoft Fabric | integração Git do workspace (Azure DevOps ou GitHub) + deployment pipelines |
| PostgreSQL / DuckDB no ZimaOS | dbt + Dagster no repositório; imagem construída no CI e atualizada com `docker compose pull && docker compose up -d` |

## CI sem segredo de longa duração
- AWS: OIDC do GitHub Actions → papel IAM.
- Google Cloud: Workload Identity Federation.
- Azure: credencial federada no Entra ID.
- Databricks: service principal com OAuth (ou federação de identidade de workload).
- Snowflake: par de chaves guardado como segredo do CI, com rotação.

## Checklist de revisão de PR de dados
- [ ] Modelo novo tem testes e descrição no YAML; `dbt build` verde
- [ ] Mudança em tabela da gold avisada aos donos dos painéis (contratos com `contract: {enforced: true}`)
- [ ] Consulta nova lê só as partições necessárias (dry-run no BigQuery, warehouse certo no Snowflake)
- [ ] Nenhum dado pessoal novo sem aprovação do Cyber
- [ ] Migração de banco revisada pelo DBA

## Documentação oficial
- https://git-scm.com/doc
- https://docs.github.com/actions
- https://docs.getdbt.com/best-practices/best-practice-workflows
- https://pre-commit.com/
- https://github.com/gitleaks/gitleaks
