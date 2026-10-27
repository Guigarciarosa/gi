---
plataforma: AWS
tema: bancos de dados gerenciados
agentes: [dba, arquiteto, finops, engenheiro, devops]
revisado: 2026-10
---

# Bancos de dados na AWS

## Mapa de serviços
| Categoria | Serviço | Quando usar |
|---|---|---|
| Relacional | **RDS** (PostgreSQL, MySQL, MariaDB, SQL Server, Oracle, Db2) | banco gerenciado padrão; Multi-AZ para HA |
| Relacional nativo da AWS | **Aurora** (PostgreSQL e MySQL), Aurora Serverless v2, Aurora DSQL (distribuído) | carga variável, réplicas rápidas, alta escala |
| Chave-valor / documentos | **DynamoDB** | apps serverless, acesso por chave, escala sem gestão |
| Documentos | DocumentDB (API compatível com MongoDB) | apps MongoDB que querem ficar na AWS |
| Data warehouse | **Redshift** (provisionado ou Serverless) | analytics grande com SQL; porte M/G |
| Consulta no lake | **Athena** (SQL sobre S3, Iceberg) | porte P/M: paga por TB lido |
| Cache | ElastiCache (Valkey, Redis OSS, Memcached), MemoryDB | cache, sessões, filas |
| Busca | OpenSearch Service (e Serverless) | busca textual, logs, vetores |
| Grafo | Neptune | fraude, redes |
| Séries temporais | Timestream for InfluxDB | IoT e métricas |
| Cassandra | Keyspaces | CQL serverless |
| Migração e CDC | **DMS** (com Schema Conversion), SCT | migrar bancos e replicar mudanças para S3/Redshift |

Região São Paulo (`sa-east-1`) tem os principais serviços; preços são maiores que nos EUA
(a calculadora da plataforma aplica o multiplicador).

## Escolhas por porte
- **P**: RDS PostgreSQL `db.t4g.small/medium` sem Multi-AZ + Athena sobre S3; ou nada de RDS (DuckDB em Fargate).
- **M**: RDS/Aurora PostgreSQL Multi-AZ para apps + Athena ou Redshift Serverless.
- **G**: Redshift (RA3 ou Serverless) ou lakehouse com Iceberg + Athena/EMR.

## Armadilhas de custo
- **Multi-AZ** dobra o custo da instância: só quando o RTO exigir.
- Aurora no modo padrão cobra I/O por requisição; para muita leitura/escrita, compare com **Aurora I/O-Optimized**.
- Snapshots manuais e backups com retenção longa somam no armazenamento.
- **NAT Gateway** para o RDS acessar a internet (ou o DMS) custa por hora e por GB.
- Redshift Serverless cobra por RPU-hora com mínimo de capacidade base: consultas frequentes de BI mantêm o serviço ligado.
- DynamoDB: sob demanda é simples; com carga estável, capacidade provisionada + auto scaling sai mais barato.
- Licença incluída de SQL Server e Oracle no RDS pesa mais que a instância.

## Leitura sem impacto e CDC
- Réplica de leitura do RDS/Aurora para a extração.
- DMS lendo CDC (binlog, WAL lógico, MS-CDC, LogMiner) para S3 em Parquet; Aurora tem *zero-ETL* para o Redshift.
- Exportação de snapshot do RDS para S3 em Parquet: carga histórica sem tocar no banco.

## Segurança
- Sem acesso público; subnets privadas; IAM authentication no RDS (PostgreSQL/MySQL); segredos no Secrets Manager com rotação; criptografia KMS ligada na criação (não dá para ligar depois sem recriar).

## Documentação oficial
- https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/
- https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/
- https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/
- https://docs.aws.amazon.com/redshift/latest/mgmt/
- https://docs.aws.amazon.com/dms/latest/userguide/
- https://aws.amazon.com/rds/pricing/
