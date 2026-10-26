---
sgbd: PostgreSQL
familia: relacional
licenca: PostgreSQL License (aberta, permissiva)
agentes: [dba, engenheiro, arquiteto, fullstack, devops]
revisado: 2026-10
---

# PostgreSQL

## O que é e quando usar
Banco relacional aberto, padrão de fato para aplicações novas e para o banco da
plataforma no porte P/M. Bom em OLTP, aguenta analytics moderado (com índices,
particionamento e agregados) e tem extensões para quase tudo: PostGIS (mapas),
TimescaleDB (séries temporais), pgvector (vetores), pg_partman, pg_cron, postgres_fdw.
Em clientes brasileiros aparece como banco do TOTVS Protheus (suportado ao lado de
SQL Server e Oracle) e de muitos sistemas próprios.

## Versões, edições e licença
- Cada versão principal tem 5 anos de suporte. Em 2026: 14, 15, 16, 17 e 18 (a 14 sai de suporte em novembro de 2026). Confira em postgresql.org/support/versioning.
- Uma edição só, sem custo de licença. Distribuições comerciais (EDB, Crunchy) vendem suporte e ferramentas.
- Atualize as versões menores (ex.: 16.x) sempre: são só correções.

## Conectar e extrair
- Drivers: `psycopg` (Python), JDBC, ODBC (psqlODBC); `dlt` e Debezium têm conectores prontos.
- Usuário de leitura:
  ```sql
  CREATE ROLE extracao LOGIN PASSWORD 'troque-por-senha-forte';
  GRANT pg_read_all_data TO extracao;            -- PostgreSQL 14+; lê todas as tabelas
  -- ou, restrito a um schema:
  GRANT CONNECT ON DATABASE erp TO extracao;
  GRANT USAGE ON SCHEMA public TO extracao;
  GRANT SELECT ON ALL TABLES IN SCHEMA public TO extracao;
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO extracao;
  ```
- Incremental: coluna `atualizado_em` com índice. Exportação rápida: `COPY (SELECT ...) TO STDOUT WITH CSV`.
- CDC por replicação lógica (Debezium com o plugin `pgoutput`):
  ```sql
  -- postgresql.conf: wal_level = logical; max_replication_slots e max_wal_senders >= 4
  ALTER SYSTEM SET max_slot_wal_keep_size = '20GB';   -- teto para WAL retido (PG 13+)
  CREATE PUBLICATION pub_dados FOR TABLE pedidos, itens_pedido, clientes;
  CREATE ROLE cdc LOGIN REPLICATION PASSWORD '...';
  GRANT SELECT ON pedidos, itens_pedido, clientes TO cdc;
  ```
  Mudar `wal_level` exige reinício. Em serviços gerenciados: RDS/Aurora (`rds.logical_replication = 1`), Cloud SQL (flag `cloudsql.logical_decoding`), Azure Flexible (`wal_level = logical`).
- Tabelas sem chave primária precisam de `REPLICA IDENTITY FULL` para replicar `UPDATE`/`DELETE`.

## Desempenho
Ative `pg_stat_statements` (`shared_preload_libraries`) e comece por aqui:
```sql
-- consultas que mais consomem tempo
SELECT round(total_exec_time) AS ms_total, calls, round(mean_exec_time, 1) AS ms_medio,
       left(query, 120) AS consulta
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 20;

-- sessões ativas, esperas e bloqueios
SELECT pid, state, wait_event_type, wait_event, now() - query_start AS duracao, left(query, 100)
FROM pg_stat_activity WHERE state <> 'idle' ORDER BY duracao DESC;
SELECT pid, pg_blocking_pids(pid) AS bloqueado_por, left(query, 80)
FROM pg_stat_activity WHERE cardinality(pg_blocking_pids(pid)) > 0;

-- tabelas com muitas linhas mortas (autovacuum atrasado)
SELECT relname, n_live_tup, n_dead_tup, last_autovacuum
FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 20;

-- slots de replicação segurando WAL (risco de disco cheio)
SELECT slot_name, active, pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS wal_retido
FROM pg_replication_slots;
```
- Plano real: `EXPLAIN (ANALYZE, BUFFERS) SELECT ...`.
- Índices: B-tree (padrão), GIN (jsonb, texto), BRIN (tabelas enormes ordenadas por data), parciais (`WHERE status = 'aberto'`) e de cobertura (`INCLUDE`).
- Particionamento declarativo por data em tabelas de fatos acima de dezenas de milhões de linhas.
- Parâmetros de partida (servidor dedicado): `shared_buffers` ≈ 25% da RAM, `effective_cache_size` ≈ 50–75%, `work_mem` 16–64 MB (multiplica por operação e por conexão), `random_page_cost = 1.1` em SSD.
- Muitas conexões: PgBouncer em modo transação.

## Backup e alta disponibilidade
- Lógico: `pg_dump -Fc` e `pg_restore -j 4` (bom até dezenas de GB; não serve para PITR).
- Físico com PITR: pgBackRest ou Barman (backup completo, diferencial e incremental, WAL contínuo, repositório em S3 ou compatível). O PostgreSQL 17 trouxe backup incremental nativo no `pg_basebackup`.
- HA: replicação por streaming + Patroni (failover automático com etcd) ou o HA do serviço gerenciado.
- Upgrade de versão principal: `pg_upgrade --link` (minutos) ou replicação lógica (quase sem parada).

## Segurança
- `pg_hba.conf` com `scram-sha-256`, TLS obrigatório (`hostssl`), nunca `trust` fora de socket local.
- Papéis por função; aplicações sem superusuário; RLS (`CREATE POLICY`) para multi-tenant.
- Auditoria: extensão `pgaudit`.

## Na cloud
| Provedor | Serviço |
|---|---|
| AWS | RDS for PostgreSQL, Aurora PostgreSQL (Serverless v2) |
| GCP | Cloud SQL for PostgreSQL, AlloyDB |
| Azure | Azure Database for PostgreSQL – Flexible Server |
| OCI | OCI Database with PostgreSQL |
| Outros | Neon, Supabase, Crunchy Bridge, Tembo |

## Armadilhas
- Slot de replicação abandonado retém WAL até encher o disco (defina `max_slot_wal_keep_size` e alerte).
- Sessões `idle in transaction` seguram vacuum e bloqueiam DDL: use `idle_in_transaction_session_timeout`.
- Atualizar a glibc do sistema operacional muda a ordenação de texto: reindexe índices de texto após upgrade de SO.
- `timestamp` sem fuso confunde horários; prefira `timestamptz`.
- Contar linhas com `count(*)` em tabelas enormes é lento; use estatísticas (`reltuples`) para estimativas.

## Documentação oficial
- https://www.postgresql.org/docs/current/
- https://www.postgresql.org/support/versioning/
- https://www.postgresql.org/docs/current/logical-replication.html
- https://www.postgresql.org/docs/current/pgstatstatements.html
- https://pgbackrest.org/user-guide.html
- https://debezium.io/documentation/reference/stable/connectors/postgresql.html
