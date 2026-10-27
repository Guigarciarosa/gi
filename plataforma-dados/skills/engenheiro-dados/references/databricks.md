---
plataforma: Databricks
agentes: [engenheiro, arquiteto, devops, finops, dba]
revisado: 2026-10
---

# Databricks para o Engenheiro de Dados

## Quando usar
- O cliente já tem Databricks, ou o volume pede Spark (TBs, milhões de arquivos, ML), ou o time trabalha em Python/Spark.
- Roda em AWS, Azure (Azure Databricks) e Google Cloud; há regiões em São Paulo na AWS e no Azure (confira a disponibilidade de cada recurso na região).
- Porte P sem Spark não precisa de Databricks: DuckDB ou PostgreSQL resolvem por uma fração do custo.

## Conceitos que você precisa dominar
- **Unity Catalog**: governança única — metastore por região → catálogo → schema → tabela, view, volume, função, modelo. Acesso a storage por *storage credentials* e *external locations*; tabelas gerenciadas ou externas; linhagem e auditoria automáticas.
- **Delta Lake**: ACID, `MERGE`, *time travel* (`VERSION AS OF`), `OPTIMIZE`, `VACUUM` (retenção padrão de 7 dias), Change Data Feed, **liquid clustering** (`CLUSTER BY`) no lugar de partição + Z-ORDER em tabelas novas, *predictive optimization*.
- **Computação**: serverless (notebooks, jobs, SQL warehouses), *jobs compute* clássico (mais barato por DBU que *all-purpose*), *all-purpose* (interativo, caro), SQL warehouses, Photon, instâncias spot nos workers, políticas de cluster e autodesligamento.
- **Lakeflow**: Lakeflow Connect (conectores gerenciados para bancos e SaaS), Lakeflow Declarative Pipelines (antigo Delta Live Tables, com *expectations* de qualidade) e Lakeflow Jobs (antigo Workflows).
- **Auto Loader** (`cloudFiles`) para arquivos que chegam no storage, com evolução de schema.
- **Databricks SQL**, dashboards AI/BI e Genie (perguntas em linguagem natural sobre tabelas do Unity Catalog). **Lakebase**: PostgreSQL gerenciado dentro do Databricks, lançado em 2025.

## Medalhão no Databricks
- Catálogos por ambiente (`dev`, `prd`) ou por cliente e ambiente; schemas `bronze`, `silver`, `gold`; arquivos de entrada em volumes (`/Volumes/prd/landing/...`).
```python
# Bronze com Auto Loader: só arquivos novos, execução em lote incremental
(spark.readStream.format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", "/Volumes/prd/bronze/_schemas/pedidos")
    .load("/Volumes/prd/landing/pedidos/")
    .selectExpr("*", "_metadata.file_path AS _arquivo", "current_timestamp() AS _carregado_em")
    .writeStream
    .option("checkpointLocation", "/Volumes/prd/bronze/_checkpoints/pedidos")
    .trigger(availableNow=True)
    .toTable("prd.bronze.pedidos"))
```
```sql
-- Silver com MERGE idempotente e clustering
CREATE TABLE IF NOT EXISTS prd.silver.pedidos (id BIGINT, cliente_id BIGINT, valor DECIMAL(14,2), status STRING, atualizado_em TIMESTAMP)
CLUSTER BY (atualizado_em);

MERGE INTO prd.silver.pedidos AS d
USING (
  SELECT id, cliente_id, CAST(valor AS DECIMAL(14,2)) AS valor, status, atualizado_em   -- mesmas colunas do destino
  FROM prd.bronze.pedidos
  QUALIFY row_number() OVER (PARTITION BY id ORDER BY atualizado_em DESC) = 1
) AS o
ON d.id = o.id
WHEN MATCHED AND o.atualizado_em > d.atualizado_em THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```
Em pipelines declarativos, a mesma ideia fica em SQL com regras de qualidade:
```sql
CREATE OR REFRESH STREAMING TABLE pedidos_bronze
AS SELECT * FROM STREAM read_files('/Volumes/prd/landing/pedidos/', format => 'json');

CREATE OR REFRESH MATERIALIZED VIEW pedidos_silver (
  CONSTRAINT id_preenchido EXPECT (id IS NOT NULL) ON VIOLATION DROP ROW
) AS SELECT id, cliente_id, CAST(valor AS DECIMAL(14,2)) AS valor, status FROM pedidos_bronze;
```

## Git no Databricks
- **Git folders** (antigo Repos): o repositório clonado no workspace; cada pessoa trabalha na sua branch e faz commit/pull pela interface. Salve notebooks como arquivo fonte (`.py` com `# Databricks notebook source`) para o diff ser legível.
- **Databricks Asset Bundles**: o projeto inteiro (jobs, pipelines, dashboards, permissões) declarado em `databricks.yml` e implantado por ambiente com a CLI: `databricks bundle validate`, `deploy -t dev`, `run`.
```yaml
# databricks.yml
bundle:
  name: plataforma-cliente
include:
  - resources/*.yml
targets:
  dev:
    mode: development          # prefixa recursos com o nome do usuário e pausa agendas
    default: true
    workspace:
      host: https://<workspace>.cloud.databricks.com
  prd:
    mode: production
    workspace:
      host: https://<workspace>.cloud.databricks.com
      root_path: /Workspace/Shared/.bundle/${bundle.name}/${bundle.target}
    run_as:
      service_principal_name: <application-id-do-service-principal>
```
```yaml
# resources/carga_diaria.yml
resources:
  jobs:
    carga_diaria:
      name: carga-diaria-${bundle.target}
      schedule:
        quartz_cron_expression: "0 0 5 * * ?"
        timezone_id: America/Sao_Paulo
      tasks:
        - task_key: ingestao
          notebook_task:
            notebook_path: ../src/ingestao_pedidos.py
        - task_key: transformacao
          depends_on: [{task_key: ingestao}]
          notebook_task:
            notebook_path: ../src/silver_gold.py
```
- **CI/CD** com GitHub Actions ou Azure DevOps usando *service principal* (OAuth M2M ou federação de identidade de workload). Nada de token pessoal (PAT) no pipeline.
```yaml
# .github/workflows/databricks.yml
name: databricks
on:
  pull_request:
  push: {branches: [main]}
jobs:
  bundle:
    runs-on: ubuntu-latest
    env:
      DATABRICKS_HOST: ${{ vars.DATABRICKS_HOST }}
      DATABRICKS_CLIENT_ID: ${{ secrets.DATABRICKS_CLIENT_ID }}
      DATABRICKS_CLIENT_SECRET: ${{ secrets.DATABRICKS_CLIENT_SECRET }}
    steps:
      - uses: actions/checkout@v4
      - uses: databricks/setup-cli@main      # fixe uma versão testada
      - run: databricks bundle validate -t prd
      - if: github.event_name == 'push'
        run: databricks bundle deploy -t prd
```
- dbt também roda no Databricks (`dbt-databricks`), como tarefa de job ou fora dele.

## Custos
- Preço = DBUs consumidos × preço do DBU (varia por cloud, plano e tipo de computação) + máquinas da cloud no modo clássico. No serverless a infraestrutura já está no preço do DBU.
- Ordem de grandeza (preço de lista nos EUA; confira a página de preços): jobs compute clássico na faixa de US$ 0,15–0,30 por DBU; *all-purpose* bem mais caro; SQL serverless na faixa de US$ 0,70 por DBU.
- Controles: jobs em *jobs compute* ou serverless (nunca em cluster interativo), autodesligamento em 10–20 min, políticas de cluster, spot nos workers, SQL warehouse com auto-stop, tags de custo, *budgets*.
```sql
-- DBUs por dia e SKU nos últimos 30 dias (system tables)
SELECT usage_date, sku_name, sum(usage_quantity) AS dbus
FROM system.billing.usage
WHERE usage_date >= current_date() - INTERVAL 30 DAYS
GROUP BY ALL ORDER BY usage_date, dbus DESC;
```

## Segurança e LGPD
- Grupos sincronizados do Entra ID/Okta (SCIM); jobs rodando como service principal; segredos em *secret scopes* (ou Key Vault).
- Filtros de linha e máscaras de coluna do Unity Catalog:
```sql
CREATE FUNCTION prd.seguranca.mascara_cpf(cpf STRING) RETURN
  CASE WHEN is_account_group_member('lgpd_leitura') THEN cpf ELSE concat('***.***.***-', right(cpf, 2)) END;
ALTER TABLE prd.silver.clientes ALTER COLUMN cpf SET MASK prd.seguranca.mascara_cpf;
```
- Private Link, listas de IP e workspace sem acesso público para clientes regulados.

## Estimativa de esforço (horas)
| Item | Simples | Médio | Complexo |
|---|---|---|---|
| Workspace + Unity Catalog (catálogos, grupos, external locations) | 8 | 16 | 40 |
| Asset Bundle + CI/CD (dev/prd, service principal) | 8 | 16 | 32 |
| Pipeline por fonte (Auto Loader, Lakeflow Connect ou declarativo) | 6 | 12 | 24 |
| Migrar notebooks soltos para Git + bundle | 8 | 24 | 60 |
| Rodada de otimização de custos | 6 | 12 | 24 |

## Armadilhas
- Cluster *all-purpose* ligado o dia inteiro rodando jobs agendados.
- Notebooks editados direto no workspace, sem Git e sem revisão.
- Token pessoal (PAT) de um funcionário no pipeline de produção.
- Milhares de arquivos pequenos sem `OPTIMIZE` ou *auto compaction*.
- `VACUUM` com retenção curta quebrando *time travel* e leituras em streaming.
- Hive metastore legado misturado com Unity Catalog sem plano de migração.

## Documentação oficial
- https://docs.databricks.com/
- https://docs.databricks.com/aws/en/dev-tools/bundles/
- https://docs.databricks.com/aws/en/repos/
- https://docs.databricks.com/aws/en/data-governance/unity-catalog/
- https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/
- https://learn.microsoft.com/azure/databricks/
- https://www.databricks.com/product/pricing
