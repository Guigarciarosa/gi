---
sgbd: Apache Cassandra e ScyllaDB
familia: colunar largo (wide-column, NoSQL)
licenca: Cassandra Apache 2.0; ScyllaDB com licenciamento próprio (verifique)
agentes: [arquiteto, dba, engenheiro]
revisado: 2026-10
---

# Apache Cassandra e ScyllaDB

## O que é e quando usar
Bancos distribuídos para volumes enormes de escrita, alta disponibilidade entre
datacenters e latência previsível: telemetria em escala, histórico de eventos,
mensageria. Raramente necessários em PMEs; aparecem como fonte em empresas de
tecnologia ou telecom. O ScyllaDB é reescrito em C++ e compatível com o protocolo do
Cassandra.

## Versões e licença
- Cassandra 5.0 (2024): índices SAI, busca vetorial, melhorias de compactação.
- ScyllaDB mudou o modelo de licença entre 2024 e 2025 (versão aberta substituída por uma edição com uso gratuito limitado); confirme antes de adotar.
- DataStax (Astra DB, serviço gerenciado de Cassandra) foi adquirida pela IBM em 2025.

## Modelagem: pense na consulta primeiro
- Uma tabela por padrão de consulta; dados duplicados são normais.
- **Chave de partição** distribui os dados; partições grandes demais (> 100 MB) causam lentidão.
- **Chaves de clustering** ordenam dentro da partição (ex.: por data decrescente).
```sql
CREATE TABLE posicoes_por_veiculo_dia (
  veiculo_id int, dia date, momento timestamp, lat double, lon double,
  PRIMARY KEY ((veiculo_id, dia), momento)
) WITH CLUSTERING ORDER BY (momento DESC);
```

## Extração
- Não há CDC simples: o recurso de CDC do commitlog e o conector Debezium para Cassandra são de uso avançado.
- Exportação em massa: DSBulk, Spark Cassandra Connector, ou leitura por intervalos de token.
- Prefira capturar os eventos **antes** de chegarem ao Cassandra (fila/Kafka) e mandar uma cópia para o lake.

## Operação
- `nodetool status`, `nodetool tablestats`, reparos (`repair`) periódicos, cuidado com *tombstones* (exclusões em massa deixam lápides que deixam leituras lentas).
- Níveis de consistência (`ONE`, `QUORUM`, `LOCAL_QUORUM`) definem o equilíbrio entre latência e garantia.

## Na cloud
| Provedor | Serviço |
|---|---|
| AWS | Amazon Keyspaces (compatível com CQL, serverless) |
| Azure | Azure Managed Instance for Apache Cassandra; Cosmos DB for Apache Cassandra |
| GCP | Cassandra em VMs/Marketplace; Bigtable como alternativa nativa |
| Outros | Astra DB (DataStax/IBM), ScyllaDB Cloud |

## Armadilhas
- Usar como banco relacional (junções, consultas ad hoc): não funciona.
- `ALLOW FILTERING` em produção.
- Exclusões em massa e TTLs mal planejados gerando *tombstones*.

## Documentação oficial
- https://cassandra.apache.org/doc/latest/
- https://docs.datastax.com/en/dsbulk/
- https://docs.scylladb.com/
- https://docs.aws.amazon.com/keyspaces/
