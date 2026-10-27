---
plataforma: Google Cloud
tema: bancos de dados gerenciados
agentes: [dba, arquiteto, finops, engenheiro, devops]
revisado: 2026-10
---

# Bancos de dados no Google Cloud

## Mapa de serviços
| Categoria | Serviço | Quando usar |
|---|---|---|
| Relacional | **Cloud SQL** (PostgreSQL, MySQL, SQL Server); edições Enterprise e Enterprise Plus | banco gerenciado padrão |
| PostgreSQL de alto desempenho | **AlloyDB** (com motor colunar e AlloyDB Omni para rodar fora do Google) | OLTP pesado + consultas analíticas no mesmo banco |
| Relacional distribuído | **Spanner** (SQL, consistência global; Spanner Graph) | escala horizontal e disponibilidade muito alta |
| Data warehouse | **BigQuery** | analytics em qualquer porte; 1 TiB de consulta e 10 GB de armazenamento grátis por mês |
| Documentos | **Firestore** (inclusive com compatibilidade MongoDB) | apps web e mobile |
| Colunar largo | **Bigtable** | séries temporais e eventos em grande escala |
| Cache | Memorystore (Valkey, Redis, Memcached) | cache e sessões |
| CDC | **Datastream** (MySQL, PostgreSQL, Oracle, SQL Server → BigQuery/Cloud Storage) | replicar bancos para o BigQuery sem código |
| Migração | **Database Migration Service** | migrar para Cloud SQL e AlloyDB (com conversão de Oracle) |

Região São Paulo (`southamerica-east1`) disponível para os principais serviços.

## Escolhas por porte
- **P**: BigQuery como gold + Looker Studio; dados de apps em Cloud SQL `db-g1-small`/`db-custom` pequeno ou Firestore.
- **M**: Cloud SQL Enterprise com HA regional para apps + BigQuery com Datastream.
- **G**: BigQuery com reservas (Editions) + AlloyDB/Spanner para cargas transacionais críticas.

## Armadilhas de custo
- BigQuery sob demanda cobra por TB lido: particione por data, clusterize, evite `SELECT *` e use visualizações materializadas.
- Painéis do Looker Studio sem cache disparam consultas a cada abertura.
- Cloud SQL com HA (regional) dobra o custo; Enterprise Plus é bem mais caro que Enterprise.
- Spanner tem custo mínimo por capacidade (processing units): não é para porte P.
- Saída de dados para a internet e entre regiões.

## Leitura sem impacto e CDC
- Réplica de leitura do Cloud SQL.
- Datastream do banco on-premise (via VPN ou IP permitido) direto para o BigQuery.
- Exportação do Cloud SQL para Cloud Storage (CSV/SQL) para cargas históricas.

## Segurança
- IP privado (Private Service Connect / VPC), Cloud SQL Auth Proxy ou conectores com IAM, segredos no Secret Manager, CMEK quando o cliente exigir chave própria.

## Documentação oficial
- https://cloud.google.com/sql/docs
- https://cloud.google.com/alloydb/docs
- https://cloud.google.com/spanner/docs
- https://cloud.google.com/bigquery/docs
- https://cloud.google.com/datastream/docs
- https://cloud.google.com/bigquery/pricing
