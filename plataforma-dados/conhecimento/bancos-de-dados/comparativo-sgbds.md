---
tema: comparativo e escolha de banco de dados
agentes: [arquiteto, dba, finops, fullstack]
revisado: 2026-10
---

# Comparativo de bancos de dados: qual usar

## Primeiro, o papel do banco
| Papel | Pergunta | Exemplos |
|---|---|---|
| Transacional (OLTP) | muitas leituras e escritas pequenas, consistência | PostgreSQL, MySQL, SQL Server, Oracle |
| Analítico (OLAP) | varrer milhões de linhas e agregar | BigQuery, Snowflake, Redshift, ClickHouse, DuckDB, ADW, Fabric |
| Documentos / chave-valor | esquema flexível, acesso por chave | MongoDB, DynamoDB, Firestore, Cosmos DB |
| Cache | resposta em milissegundos, dado descartável | Redis, Valkey |
| Busca | relevância de texto, facetas | Elasticsearch, OpenSearch |
| Séries temporais | sensores, GPS, métricas | TimescaleDB, InfluxDB, ClickHouse |
| Grafo | conexões entre entidades | Neo4j, Neptune |
| Vetorial | busca semântica, RAG | Qdrant, pgvector |

## Tabela de referência
| Banco | Tipo | Licença | Custo de licença | Ponto forte | Evite quando |
|---|---|---|---|---|---|
| PostgreSQL | relacional | aberta | zero | versátil, extensões | escala horizontal massiva de escrita |
| MySQL / MariaDB | relacional | GPL | zero (Enterprise pago) | web, simplicidade | analytics pesado |
| SQL Server | relacional | comercial | alto (por núcleo) | ecossistema Microsoft, ERPs | destino analítico de PME |
| Oracle | relacional | comercial | muito alto | ERPs grandes, recursos avançados | projeto novo sem licença existente |
| Firebird | relacional | aberta | zero | sistemas pequenos legados | projeto novo |
| Progress OpenEdge | relacional | comercial | alto | Datasul (legado) | projeto novo |
| Db2 | relacional | comercial | alto | legado IBM, IBM i | projeto novo |
| SAP HANA | colunar em memória | comercial | muito alto | S/4HANA | qualquer coisa fora do SAP |
| SQLite | embarcado | domínio público | zero | apps e offline | multiusuário |
| DuckDB | analítico embarcado | MIT | zero | gold de porte P, Parquet | muitos escritores |
| ClickHouse | analítico | Apache 2.0 | zero (Cloud pago) | eventos e telemetria em volume | OLTP |
| BigQuery | warehouse serverless | serviço | por TB lido ou reserva | zero operação, free tier | consultas muito frequentes sem partição |
| Snowflake | warehouse | serviço | créditos por segundo | separação de computação, cópias zero-copy | orçamento muito apertado |
| Databricks | lakehouse | serviço | DBUs + nuvem | Spark, ML, Delta | porte P sem Spark |
| MongoDB | documentos | SSPL | zero (Atlas pago) | esquema flexível | relatórios relacionais |
| Redis / Valkey | chave-valor | AGPL / BSD | zero | cache | fonte da verdade |
| Elasticsearch / OpenSearch | busca | Elastic / Apache | zero (serviço pago) | busca textual | banco principal |
| Qdrant | vetorial | Apache 2.0 | zero | RAG com filtros | dados tabulares |

## Banco da plataforma de dados por porte
| Porte | Transacional (apps, controle) | Analítico (gold) | BI |
|---|---|---|---|
| P | PostgreSQL no ZimaOS ou VM A1 da OCI | DuckDB + Parquet, ou PostgreSQL | Metabase / Superset, Looker Studio, Power BI Pro |
| M | PostgreSQL gerenciado | BigQuery, Athena + Iceberg, Fabric, ADW, ClickHouse | Power BI, Looker Studio, Metabase |
| G | PostgreSQL/AlloyDB/Aurora | BigQuery, Snowflake, Databricks, Redshift, ADW | Power BI, Looker, Tableau |

## Regras de decisão
1. O cliente já tem licença e time num banco? Isso pesa mais do que pequenas diferenças técnicas.
2. Dados até algumas centenas de GB cabem em PostgreSQL + DuckDB com folga: não compre warehouse por moda.
3. Comece com o banco que o time do cliente consegue operar sozinho no fim do contrato.
4. Escolha formatos abertos na gold (Parquet, Iceberg, Delta) para poder trocar de motor depois.
5. Para cada banco novo, alguém precisa fazer backup, atualizar e monitorar: conte esse custo.

## Documentação relacionada
Arquivos por SGBD nesta pasta; custos de cloud em `docs/05-clouds-e-custos.md`; Databricks e Snowflake em `skills/engenheiro-dados/references/`.

## Documentação oficial
- Guia da AWS para escolher banco: https://docs.aws.amazon.com/decision-guides/latest/databases-on-aws-how-to-choose/databases-on-aws-how-to-choose.html
- Guia da Microsoft para escolher armazenamento de dados: https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/data-store-overview
- Bancos do Google Cloud: https://cloud.google.com/products/databases
- Bancos da Oracle Cloud: https://www.oracle.com/database/
