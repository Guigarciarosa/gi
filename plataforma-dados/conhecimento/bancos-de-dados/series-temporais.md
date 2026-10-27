---
sgbd: Bancos de séries temporais (TimescaleDB, InfluxDB, QuestDB e serviços de cloud)
familia: séries temporais
licenca: varia (ver tabela)
agentes: [arquiteto, engenheiro, dba, devops]
revisado: 2026-10
---

# Bancos de séries temporais

## Quando usar
Dados com carimbo de tempo que chegam sem parar: sensores do chão de fábrica (CLP,
SCADA), telemetria de máquinas agrícolas, GPS de frota, energia, métricas de
servidores. As necessidades típicas são retenção por idade, agregação por janela
(minuto, hora, dia), compressão e consultas "último valor por equipamento".

## Opções
| Produto | Licença | Melhor para |
|---|---|---|
| **TimescaleDB** (extensão do PostgreSQL) | núcleo Apache 2.0; recursos avançados sob a Timescale License | PMEs: é PostgreSQL, o time já sabe usar, junta com os dados de negócio |
| **InfluxDB 3** (Core aberto, Enterprise pago) | MIT/Apache (Core) | métricas e IoT, SQL e InfluxQL, armazenamento em Parquet |
| **QuestDB** | Apache 2.0 | ingestão muito alta com SQL |
| **ClickHouse** | Apache 2.0 | telemetria em volume grande junto com analytics (ver `clickhouse.md`) |
| Prometheus | Apache 2.0 | métricas de infraestrutura (não é para dados de negócio) |

A empresa por trás do TimescaleDB passou a se chamar TigerData em 2025; o InfluxDB 1 e 2 (linguagem Flux) estão sendo substituídos pelo InfluxDB 3.

## TimescaleDB na prática
```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE TABLE leituras (momento timestamptz NOT NULL, equipamento_id int, temperatura real, vibracao real);
SELECT create_hypertable('leituras', by_range('momento', INTERVAL '1 day'));

-- compressão de dados antigos e retenção
ALTER TABLE leituras SET (timescaledb.compress, timescaledb.compress_segmentby = 'equipamento_id');
SELECT add_compression_policy('leituras', INTERVAL '7 days');
SELECT add_retention_policy('leituras', INTERVAL '24 months');

-- agregado contínuo por hora (alimenta o painel de OEE)
CREATE MATERIALIZED VIEW leituras_hora WITH (timescaledb.continuous) AS
SELECT time_bucket('1 hour', momento) AS hora, equipamento_id, avg(temperatura) AS temp_media, max(vibracao) AS vib_max
FROM leituras GROUP BY 1, 2;
```

## Na cloud
| Provedor | Serviço |
|---|---|
| AWS | Amazon Timestream for InfluxDB; IoT SiteWise para dados industriais |
| Azure | Azure Data Explorer (Kusto) e Eventhouse no Fabric (Real-Time Intelligence) |
| GCP | Bigtable para escala; BigQuery para análise |
| OCI | Autonomous Database ou PostgreSQL com TimescaleDB em VM |
| Outros | Timescale Cloud (TigerData), InfluxDB Cloud |

## Armadilhas
- Guardar o dado bruto de segundos para sempre: agregue e aplique retenção.
- Fuso horário e horário de verão: grave em UTC (`timestamptz`) e converta na exibição.
- Equipamentos que reenviam dados atrasados: aceite chegada fora de ordem e deduplique por (equipamento, momento).

## Documentação oficial
- https://docs.timescale.com/
- https://docs.influxdata.com/influxdb3/core/
- https://questdb.com/docs/
- https://learn.microsoft.com/azure/data-explorer/
