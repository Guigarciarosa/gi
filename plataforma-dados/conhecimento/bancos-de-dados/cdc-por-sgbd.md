---
tema: captura de mudanças (CDC) e cargas incrementais por SGBD
agentes: [dba, engenheiro, arquiteto, finops]
revisado: 2026-10
---

# CDC e cargas incrementais por SGBD

## Antes do CDC: precisa mesmo?
CDC por log é poderoso e caro de operar (mais um serviço ligado, log retido, alertas).
Use quando a decisão do negócio pede minutos, quando não existe coluna de alteração
confiável, ou quando exclusões precisam ser capturadas. Para painel D-1, carga
incremental por data resolve com muito menos risco.

| Estratégia | Quando | Capta exclusão? | Impacto na fonte |
|---|---|---|---|
| Full (carga completa) | tabelas pequenas (até ~1 milhão de linhas) | sim (compara) | médio |
| Incremental por coluna de data | existe `atualizado_em` confiável e indexado | não (precisa de exclusão lógica ou reconciliação) | baixo |
| Janela deslizante + reconciliação | sem coluna de alteração; documentos com data | parcial | baixo/médio |
| Change Tracking (SQL Server) | quer saber quais chaves mudaram, sem guardar a linha | sim | baixo |
| CDC por log | minutos de latência, exclusões, auditoria | sim | baixo na consulta; exige log retido |

## Mecanismo por SGBD
| SGBD | Mecanismo nativo | Pré-requisitos | Ferramentas | Monitorar |
|---|---|---|---|---|
| PostgreSQL | Replicação lógica (`pgoutput`) | `wal_level=logical`, slot, publicação, `REPLICA IDENTITY` em tabelas sem PK | Debezium, AWS DMS, Datastream, Fabric Mirroring, Airbyte | WAL retido pelo slot |
| MySQL / MariaDB | Binlog | `binlog_format=ROW`, `binlog_row_image=FULL`, GTID, retenção do binlog | Debezium, DMS, Datastream, Airbyte | atraso e retenção do binlog |
| SQL Server | CDC (tabelas `cdc.*`) ou Change Tracking | SQL Agent ligado (não existe no Express); Standard 2016 SP1+ | Debezium, DMS, Data Factory, Fabric Mirroring, Datastream | crescimento do log e das tabelas de CDC |
| Oracle | LogMiner; XStream e GoldenGate (licenciados) | `ARCHIVELOG`, log suplementar, privilégios de LogMiner | Debezium, DMS, OCI GoldenGate, Datastream | archivelogs e atraso |
| Db2 LUW | SQL Replication (ASN) | captura ASN configurada | Debezium Db2, IBM IIDR | — |
| IBM i | Journaling | journal ligado nas tabelas | IIDR, ferramentas de terceiros | receptores de journal |
| Firebird | não tem | coluna de data ou trigger de log; replicação do Firebird 4+ | scripts próprios | tabela de log |
| Progress OpenEdge | OpenEdge CDC (11.7+) | habilitar e licenciar | Pro2, scripts | tabelas de CDC |
| MongoDB | Change streams | replica set ou cluster | Debezium, conectores Atlas | janela do oplog |
| SAP | SLT, ODP (OData) | licença e autorização SAP | Datasphere, conectores certificados | — |

## Ferramentas gerenciadas por cloud
| Cloud | CDC gerenciado | Destinos típicos |
|---|---|---|
| AWS | DMS (full load + CDC) | S3 (Parquet), Redshift, Aurora |
| GCP | Datastream | BigQuery, Cloud Storage |
| Azure | Fabric Mirroring; Data Factory CDC | OneLake (Delta), Azure SQL |
| OCI | GoldenGate | ADW, Object Storage, Kafka |
| Neutras | Debezium (Kafka Connect ou Debezium Server), Airbyte, Fivetran, Estuary | qualquer |

No ZimaOS, o caminho mais leve é o **Debezium Server** publicando os eventos num Redis
Streams (ou NATS/Redpanda pequenos), um consumidor em Python gravando Parquet na bronze
e o dbt aplicando na silver com `MERGE`.

## Aplicando mudanças na silver
```sql
-- padrão de MERGE idempotente a partir de eventos de CDC deduplicados (último evento por chave)
MERGE INTO silver.pedidos AS d
USING (
  SELECT * FROM (
    SELECT *, row_number() OVER (PARTITION BY id ORDER BY lsn DESC) AS rn FROM bronze.pedidos_cdc
    WHERE _carregado_em > :ultima_execucao
  ) x WHERE rn = 1
) AS o ON d.id = o.id
WHEN MATCHED AND o.op = 'd' THEN DELETE
WHEN MATCHED THEN UPDATE SET valor = o.valor, status = o.status, atualizado_em = o.atualizado_em
WHEN NOT MATCHED AND o.op <> 'd' THEN INSERT (id, valor, status, atualizado_em) VALUES (o.id, o.valor, o.status, o.atualizado_em);
```
(`MERGE` existe no PostgreSQL 15+, SQL Server, Oracle, BigQuery, Snowflake, Databricks e DuckDB, com pequenas diferenças de sintaxe.)

## Checklist antes de ligar CDC num banco de cliente
1. Autorização escrita do cliente e do fornecedor do ERP.
2. Espaço em disco para o log retido em caso de parada do conector (dimensione para 3 dias).
3. Alerta de atraso e de log retido antes de ir para produção.
4. Procedimento para remover o slot/captura se o projeto acabar.
5. Carga inicial (snapshot) fora do horário comercial.

## Documentação oficial
- https://debezium.io/documentation/reference/stable/
- https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.html
- https://cloud.google.com/datastream/docs/sources
- https://learn.microsoft.com/fabric/database/mirrored-database/overview
- https://docs.oracle.com/en/cloud/paas/goldengate-service/
