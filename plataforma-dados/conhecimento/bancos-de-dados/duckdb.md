---
sgbd: DuckDB
familia: analítico embarcado (OLAP)
licenca: MIT
agentes: [arquiteto, engenheiro, analista, dba]
revisado: 2026-10
---

# DuckDB

## O que é e quando usar
"O SQLite do analytics": banco colunar embarcado, sem servidor, que roda dentro do
Python, de um notebook ou de um contêiner. Lê e escreve Parquet, CSV e JSON locais ou
em S3, GCS e Azure, e consulta PostgreSQL, MySQL e SQLite diretamente. É o motor da
gold no porte P: custo zero, muito rápido, perfeito no ZimaOS ou numa VM A1 da OCI.

## Versões e licença
- Série 1.x (estável desde 2024), MIT. **MotherDuck** é a versão gerenciada na nuvem. O time do DuckDB também criou o **DuckLake**, formato de lakehouse com catálogo em banco SQL.

## Usar na plataforma
```sql
INSTALL httpfs; LOAD httpfs;
CREATE SECRET (TYPE s3, KEY_ID '...', SECRET '...', REGION 'sa-east-1');   -- ou credenciais do ambiente

-- consultar a bronze em Parquet direto do bucket
SELECT data_emissao::DATE AS dia, sum(valor_total) AS faturado
FROM read_parquet('s3://cliente-bronze/notas/*/*.parquet', hive_partitioning = true)
GROUP BY ALL ORDER BY dia;

-- ler o PostgreSQL da plataforma sem copiar
INSTALL postgres; LOAD postgres;
ATTACH 'dbname=plataforma host=postgres user=leitura' AS pg (TYPE postgres, READ_ONLY);
SELECT count(*) FROM pg.public.fct_vendas;

-- gravar a gold particionada
COPY (SELECT * FROM fct_vendas) TO 'gold/fct_vendas' (FORMAT parquet, PARTITION_BY (ano, mes));
```
- dbt: adaptador `dbt-duckdb` (modelos podem gravar Parquet externo).
- Extensões úteis: `postgres`, `mysql`, `sqlite`, `iceberg`, `delta`, `spatial`, `excel`.

## Desempenho
- `SET memory_limit = '4GB'; SET threads = 4;` dentro de contêiner (ele usa toda a máquina por padrão).
- Parquet particionado por data e com arquivos de 100 MB a 1 GB; ele lê só as colunas e partições necessárias.
- Grandes junções que não cabem na memória vão para disco (`temp_directory`).

## Concorrência e backup
- Um processo grava por vez no arquivo `.duckdb`; vários podem ler em modo somente leitura. Para BI com muitos usuários, publique a gold em Parquet ou PostgreSQL.
- Backup: copie o arquivo com o processo parado, ou `EXPORT DATABASE 'pasta'`.

## Armadilhas
- Não é banco transacional multiusuário: não use como banco de aplicação web.
- O formato do arquivo mudou entre versões antigas (antes da 1.0); exporte e importe ao atualizar bancos muito antigos.
- Metabase e Superset precisam de driver da comunidade para DuckDB; Parquet + PostgreSQL costuma ser mais simples para o BI.

## Documentação oficial
- https://duckdb.org/docs/
- https://duckdb.org/docs/extensions/httpfs/overview
- https://duckdb.org/docs/extensions/postgres
- https://motherduck.com/docs/
