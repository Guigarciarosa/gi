---
sgbd: ClickHouse
familia: analítico colunar (OLAP) em servidor
licenca: Apache 2.0 (ClickHouse Cloud é comercial)
agentes: [arquiteto, engenheiro, dba, analista]
revisado: 2026-10
---

# ClickHouse

## O que é e quando usar
Banco colunar em servidor, feito para consultar bilhões de linhas em segundos.
Excelente para eventos e telemetria: posições de GPS de frota, sensores de fábrica,
logs, cliques de e-commerce. Quando o volume passa do que o DuckDB e o PostgreSQL
aguentam no porte M, é a alternativa barata a um warehouse gerenciado.

## Versões e licença
- Lançamentos mensais e versões LTS duas vezes por ano. Aberto (Apache 2.0); **ClickHouse Cloud** é o serviço gerenciado (AWS, GCP, Azure).

## Modelagem (o que mais importa)
```sql
CREATE TABLE posicoes (
    veiculo_id  UInt32,
    momento     DateTime64(3, 'America/Sao_Paulo'),
    lat         Float64,
    lon         Float64,
    velocidade  UInt16,
    ignicao     UInt8
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(momento)
ORDER BY (veiculo_id, momento)
TTL toDateTime(momento) + INTERVAL 24 MONTH;
```
- `ORDER BY` é o índice: coloque primeiro as colunas mais filtradas.
- `ReplacingMergeTree` para "upsert" (mantém a versão mais nova por chave após o merge; use `FINAL` ou deduplicação na consulta).
- `AggregatingMergeTree` + materialized views para agregados contínuos (ex.: km por veículo por hora).
- Particione por mês; partições demais deixam o banco lento.

## Ingestão
- Inserções em lotes grandes (milhares de linhas por vez) ou `async_insert = 1`; muitas inserções pequenas geram partes demais.
- Motores de integração: Kafka, S3 (`s3()` e `S3Queue`), PostgreSQL e MySQL.
- CDC do PostgreSQL para ClickHouse: ClickPipes (Cloud) ou PeerDB.

## Desempenho e operação
```sql
-- consultas mais lentas das últimas 24 h
SELECT query_duration_ms, read_rows, formatReadableSize(memory_usage) AS memoria, substring(query, 1, 120)
FROM system.query_log
WHERE type = 'QueryFinish' AND event_time > now() - INTERVAL 1 DAY
ORDER BY query_duration_ms DESC LIMIT 20;
-- partes por tabela (muitas partes = inserções pequenas demais)
SELECT table, count() AS partes FROM system.parts WHERE active GROUP BY table ORDER BY partes DESC;
```
- `UPDATE`/`DELETE` são *mutations* pesadas; prefira *lightweight deletes* ou reescrever partições.
- Junções: a tabela menor à direita; dicionários (`DICTIONARY`) para dimensões.

## Backup e alta disponibilidade
- `BACKUP TABLE/DATABASE ... TO S3(...)` nativo; réplicas com `ReplicatedMergeTree` e ClickHouse Keeper.

## Armadilhas
- Não é OLTP: nada de muitas atualizações linha a linha.
- Fuso horário: defina na coluna `DateTime` para evitar horas trocadas.
- Memória: consultas com `GROUP BY` enorme podem estourar; ajuste `max_memory_usage` e use spill para disco.

## Documentação oficial
- https://clickhouse.com/docs
- https://clickhouse.com/docs/engines/table-engines/mergetree-family/mergetree
- https://clickhouse.com/docs/operations/backup
