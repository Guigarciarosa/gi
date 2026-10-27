---
plataforma: Snowflake
agentes: [engenheiro, arquiteto, devops, finops, dba, cyber]
revisado: 2026-10
---

# Snowflake para o Engenheiro de Dados

## Quando usar
- O cliente já tem Snowflake, ou quer um warehouse sem nenhuma operação, com cargas isoladas (um warehouse para ETL, outro para BI), clones instantâneos para desenvolvimento e compartilhamento de dados com parceiros.
- Roda em AWS, Azure e Google Cloud; há região na AWS em São Paulo (confira as demais).
- Porte P com orçamento apertado costuma sair mais barato com BigQuery (camada gratuita) ou DuckDB/PostgreSQL.

## Conceitos que você precisa dominar
- Conta → bancos → schemas → tabelas, views, *stages*, *pipes*, *streams*, *tasks* e *dynamic tables*.
- **Virtual warehouses**: X-Small consome 1 crédito por hora, Small 2, Medium 4, Large 8 (dobra a cada tamanho); cobrança por segundo, com mínimo de 60 s a cada vez que liga; `AUTO_SUSPEND` e `AUTO_RESUME`; multi-cluster na Enterprise.
- **Armazenamento** cobrado por TB/mês comprimido; *Time Travel* (1 dia no padrão, até 90 na Enterprise) e *Fail-safe* (7 dias) somam armazenamento.
- **Edições**: Standard, Enterprise, Business Critical e VPS; o preço do crédito muda com edição, cloud e região.
- **Ingestão**: `COPY INTO` a partir de *stages* (S3, GCS, Azure), Snowpipe (automático por evento), Snowpipe Streaming, Openflow e conectores de parceiros.
- **Transformação**: SQL, Streams + Tasks (CDC dentro do Snowflake), **Dynamic Tables** (declarativas, com `TARGET_LAG`), Snowpark (Python) e dbt (`dbt-snowflake`).
- **Zero-copy clone**: `CREATE DATABASE dev CLONE prd;` cria uma cópia sem duplicar armazenamento (aplique máscaras: são dados reais).
- **Cortex**: funções de IA em SQL e perguntas em linguagem natural sobre modelos semânticos.

## Configuração base
```sql
-- warehouses separados, pequenos e que se desligam sozinhos
CREATE WAREHOUSE wh_transformacao WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE INITIALLY_SUSPENDED = TRUE;
CREATE WAREHOUSE wh_bi WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 120 AUTO_RESUME = TRUE INITIALLY_SUSPENDED = TRUE;

-- teto de gasto mensal
CREATE RESOURCE MONITOR rm_mensal WITH CREDIT_QUOTA = 100 FREQUENCY = MONTHLY START_TIMESTAMP = IMMEDIATELY
  TRIGGERS ON 80 PERCENT DO NOTIFY ON 100 PERCENT DO SUSPEND;
ALTER WAREHOUSE wh_transformacao SET RESOURCE_MONITOR = rm_mensal;

-- papéis funcionais (ACCOUNTADMIN só para administração da conta)
CREATE ROLE transformacao;
CREATE ROLE bi_leitura;
GRANT USAGE ON WAREHOUSE wh_bi TO ROLE bi_leitura;
GRANT USAGE ON DATABASE prd TO ROLE bi_leitura;
GRANT USAGE ON SCHEMA prd.gold TO ROLE bi_leitura;
GRANT SELECT ON ALL TABLES IN SCHEMA prd.gold TO ROLE bi_leitura;
GRANT SELECT ON FUTURE TABLES IN SCHEMA prd.gold TO ROLE bi_leitura;
GRANT ROLE transformacao TO ROLE SYSADMIN;

-- usuário de serviço com chave (sem senha)
CREATE USER svc_dbt TYPE = SERVICE DEFAULT_ROLE = transformacao DEFAULT_WAREHOUSE = wh_transformacao RSA_PUBLIC_KEY = '<chave pública>';
GRANT ROLE transformacao TO USER svc_dbt;
```
A Snowflake está bloqueando o login só com senha: use par de chaves ou OAuth para serviços e MFA/SSO para pessoas.

## Carga e transformação
```sql
-- arquivos Parquet que chegam no bucket
CREATE STAGE landing URL = 's3://cliente-landing/' STORAGE_INTEGRATION = int_s3;
COPY INTO bronze.pedidos FROM @landing/pedidos/
  FILE_FORMAT = (TYPE = PARQUET) MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;

-- silver sempre atualizada com atraso máximo de 1 hora
CREATE OR REPLACE DYNAMIC TABLE silver.pedidos TARGET_LAG = '1 hour' WAREHOUSE = wh_transformacao AS
SELECT id, cliente_id, valor::NUMBER(14,2) AS valor, status, atualizado_em
FROM bronze.pedidos
QUALIFY row_number() OVER (PARTITION BY id ORDER BY atualizado_em DESC) = 1;
```
Tabelas intermediárias de carga como `TRANSIENT` (sem Fail-safe) economizam armazenamento.

## Git no Snowflake
- **dbt + CI** é o caminho principal. Conexão do dbt com par de chaves vindo de variáveis do CI:
```yaml
# profiles.yml
plataforma_cliente:
  target: prd
  outputs:
    prd:
      type: snowflake
      account: "{{ env_var('SF_CONTA') }}"
      user: "{{ env_var('SF_USUARIO') }}"
      private_key: "{{ env_var('SF_CHAVE_PRIVADA') }}"
      role: TRANSFORMACAO
      warehouse: WH_TRANSFORMACAO
      database: PRD
      schema: SILVER
      threads: 4
```
- **Integração Git nativa**: o Snowflake lê o repositório e executa scripts direto de uma branch ou tag.
```sql
CREATE OR REPLACE SECRET ops.sec_github TYPE = password USERNAME = 'usuario-github' PASSWORD = '<token de acesso de leitura>';
CREATE OR REPLACE API INTEGRATION git_github
  API_PROVIDER = git_https_api
  API_ALLOWED_PREFIXES = ('https://github.com/minha-org/')
  ALLOWED_AUTHENTICATION_SECRETS = (ops.sec_github)
  ENABLED = TRUE;
CREATE OR REPLACE GIT REPOSITORY ops.repo_plataforma
  API_INTEGRATION = git_github GIT_CREDENTIALS = ops.sec_github
  ORIGIN = 'https://github.com/minha-org/plataforma-cliente.git';

ALTER GIT REPOSITORY ops.repo_plataforma FETCH;
EXECUTE IMMEDIATE FROM @ops.repo_plataforma/branches/main/migracoes/deploy.sql;
```
- **Migrações versionadas** de objetos fora do dbt (warehouses, papéis, stages, pipes): **schemachange** (scripts `V1.2.0__cria_stage.sql` e `R__views.sql`, histórico numa tabela de controle) ou o provider Terraform oficial do Snowflake para conta, warehouses, bancos e papéis.
- **Snowflake CLI** (`snow`) para executar SQL, sincronizar o repositório Git e publicar apps Snowpark no CI.

## Custos
- Crédito na faixa de US$ 2 a 4 conforme edição, cloud e região (confira a tabela vigente); um X-Small ligado 8 h por dia útil consome cerca de 176 créditos/mês, mas com `AUTO_SUSPEND` ele fica ligado só enquanto há consultas.
- A camada de *cloud services* só é cobrada acima de 10% do consumo diário de computação.
```sql
-- créditos por warehouse e dia nos últimos 30 dias
SELECT warehouse_name, date_trunc('day', start_time) AS dia, sum(credits_used) AS creditos
FROM snowflake.account_usage.warehouse_metering_history
WHERE start_time >= dateadd('day', -30, current_timestamp())
GROUP BY 1, 2 ORDER BY 2, 3 DESC;
```
- Maiores vilões: painel atualizando a cada poucos minutos (o warehouse nunca dorme), warehouse grande demais, Time Travel longo em tabelas que mudam muito, Snowpipe com arquivos minúsculos.

## Segurança e LGPD
- Políticas de rede, SSO (Entra ID/Okta), MFA, par de chaves para serviços.
- Políticas de máscara e de acesso por linha (a partir da Enterprise), tags e classificação automática de dados pessoais.
```sql
CREATE MASKING POLICY seguranca.mascara_cpf AS (v STRING) RETURNS STRING ->
  CASE WHEN IS_ROLE_IN_SESSION('LGPD_LEITURA') THEN v ELSE '***.***.***-' || RIGHT(v, 2) END;
ALTER TABLE silver.clientes MODIFY COLUMN cpf SET MASKING POLICY seguranca.mascara_cpf;
```

## Estimativa de esforço (horas)
| Item | Simples | Médio | Complexo |
|---|---|---|---|
| Conta: warehouses, papéis, monitores de recursos, rede | 8 | 16 | 32 |
| Ingestão por fonte (stage + COPY ou Snowpipe) | 4 | 8 | 16 |
| Projeto dbt com CI e par de chaves | 12 | 24 | 40 |
| Integração Git + migrações (schemachange ou Terraform) | 6 | 12 | 24 |
| Rodada de otimização de custos | 4 | 8 | 16 |

## Armadilhas
- Trabalhar como `ACCOUNTADMIN` no dia a dia.
- Um único warehouse para tudo (ETL e BI disputando, e ninguém sabe quem gasta).
- Usuários de serviço com senha.
- Clone de produção usado em desenvolvimento sem mascaramento de dados pessoais.
- Nenhum *resource monitor*: a conta descobre o gasto na fatura.

## Documentação oficial
- https://docs.snowflake.com/
- https://docs.snowflake.com/en/developer-guide/git/git-overview
- https://docs.snowflake.com/en/user-guide/warehouses-overview
- https://docs.snowflake.com/en/user-guide/resource-monitors
- https://docs.snowflake.com/en/user-guide/dynamic-tables-about
- https://github.com/Snowflake-Labs/schemachange
- https://www.snowflake.com/pricing/
