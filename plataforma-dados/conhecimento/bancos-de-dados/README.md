# Base de conhecimento — Bancos de dados

Referência técnica que os agentes consultam pela memória vetorial (coleção
`conhecimento`). Cada arquivo traz o essencial de um SGBD ou tema para o trabalho da
consultoria: extrair sem derrubar o sistema do cliente, operar, proteger, migrar e
estimar custo. O **DBA** recebe todos; os demais agentes recebem os arquivos ligados ao
seu papel (`conhecimento` em `servidor/src/plataforma/agentes.py`).

## Como os agentes aprendem
1. **Base curada (esta pasta)**: `memoria_reindexar_base` fragmenta e indexa todos os arquivos. O contexto de cada agente busca trechos pelas consultas do papel e, para DBA e Engenheiro, também pelos bancos, ERP e plataformas que o cliente informou no questionário.
2. **Documentação oficial**: cada arquivo termina com "Documentação oficial". A ferramenta MCP `conhecimento_baixar(fonte)` (ou `scripts/baixar_docs_oficiais.py`) baixa essas páginas e as vizinhas do mesmo site, converte para Markdown e indexa. `conhecimento_fontes` lista as fontes.
3. **Experiência dos projetos**: lições gravadas na coleção `projetos` ao fim de cada cliente (`memoria_indexar`).
4. **Skills empacotadas**: `python scripts/empacotar_skills.py` coloca estes arquivos dentro do .zip da skill do DBA (e os relevantes nos outros), para uso direto no claude.ai ou no Claude Code.

## Índice
### Relacionais
| Arquivo | Conteúdo |
|---|---|
| [postgresql.md](postgresql.md) | Banco da plataforma; replicação lógica, pg_stat_statements, pgBackRest, RLS |
| [mysql-mariadb.md](mysql-mariadb.md) | Binlog e CDC, utf8mb4, XtraBackup, serviços gerenciados |
| [sql-server.md](sql-server.md) | Edições e licença, Change Tracking × CDC, log de transações, Query Store |
| [oracle-database.md](oracle-database.md) | SE2 × EE, armadilhas de licença (AWR, VMware), LogMiner, RMAN |
| [firebird.md](firebird.md) | Sistemas regionais; sem CDC nativo, gbak, monitoramento MON$ |
| [progress-openedge.md](progress-openedge.md) | Datasul; acesso SQL, largura SQL, Pro2 |
| [ibm-db2.md](ibm-db2.md) | Db2 LUW e IBM i (AS/400), CCSID, replicação |
| [sap-hana.md](sap-hana.md) | Licença runtime × full use, CDS/ODP/SLT, tabelas SAP |
| [sqlite.md](sqlite.md) | Embarcado, apps de campo, Litestream |

### Analíticos, NoSQL e especializados
| Arquivo | Conteúdo |
|---|---|
| [duckdb.md](duckdb.md) | Gold do porte P sobre Parquet, leitura de PostgreSQL |
| [clickhouse.md](clickhouse.md) | Telemetria e eventos em volume; MergeTree |
| [mongodb.md](mongodb.md) | Documentos; change streams, Atlas e compatíveis |
| [redis-valkey.md](redis-valkey.md) | Cache, filas, mudança de licença e Valkey |
| [cassandra-scylladb.md](cassandra-scylladb.md) | Colunar largo; modelagem por consulta |
| [elasticsearch-opensearch.md](elasticsearch-opensearch.md) | Busca textual e logs |
| [neo4j-grafos.md](neo4j-grafos.md) | Grafos para fraude e redes |
| [series-temporais.md](series-temporais.md) | TimescaleDB, InfluxDB, QuestDB, serviços de cloud |
| [bancos-vetoriais.md](bancos-vetoriais.md) | Qdrant, pgvector e alternativas para RAG |

### Bancos das plataformas e dos ERPs
| Arquivo | Conteúdo |
|---|---|
| [aws-bancos-de-dados.md](aws-bancos-de-dados.md) | RDS, Aurora, DynamoDB, Redshift, Athena, DMS |
| [gcp-bancos-de-dados.md](gcp-bancos-de-dados.md) | Cloud SQL, AlloyDB, Spanner, BigQuery, Datastream |
| [azure-bancos-de-dados.md](azure-bancos-de-dados.md) | Azure SQL, Managed Instance, Flexible Server, Cosmos DB, Fabric |
| [oci-bancos-de-dados.md](oci-bancos-de-dados.md) | Autonomous Database, MySQL HeatWave, GoldenGate, Always Free |
| [erps-bancos-de-dados.md](erps-bancos-de-dados.md) | Protheus, RM, Datasul, WinThor, Senior, Sankhya, SAP B1: bancos e tabelas |
| Databricks e Snowflake | ver `skills/engenheiro-dados/references/databricks.md` e `snowflake.md` |

### Temas transversais
| Arquivo | Conteúdo |
|---|---|
| [comparativo-sgbds.md](comparativo-sgbds.md) | Qual banco usar, por papel e por porte |
| [cdc-por-sgbd.md](cdc-por-sgbd.md) | Estratégias incrementais e CDC de cada SGBD |
| [backup-e-alta-disponibilidade.md](backup-e-alta-disponibilidade.md) | RPO/RTO, 3-2-1 imutável, teste de restauração |
| [seguranca-de-bancos.md](seguranca-de-bancos.md) | Privilégio mínimo, criptografia, LGPD, auditoria |
| [desempenho-e-diagnostico.md](desempenho-e-diagnostico.md) | Roteiro de diagnóstico e onde olhar em cada SGBD |
| [migracao-entre-sgbds.md](migracao-entre-sgbds.md) | Ferramentas, mapa de tipos, plano de corte |

## Modelo para um SGBD novo
```markdown
---
sgbd: Nome
familia: relacional | documentos | analítico | ...
licenca: ...
agentes: [dba, ...]
revisado: AAAA-MM
---
# Nome
## O que é e quando usar
## Versões, edições e licença
## Conectar e extrair          (driver, usuário de leitura, incremental, CDC)
## Desempenho                  (consultas de diagnóstico)
## Backup e alta disponibilidade
## Segurança
## Na cloud                    (serviço por provedor)
## Armadilhas
## Documentação oficial        (links: o coletor usa esta seção)
```
Depois de criar ou editar, rode `memoria_reindexar_base`.

## Cuidados
- Versões, preços e regras de licença mudam: cada arquivo tem a data de revisão (`revisado`). Revise a cada 6 meses e confira na documentação oficial antes de levar ao cliente.
- A documentação oficial baixada fica fora do Git (`conhecimento/_oficiais/` e `/data/conhecimento-oficial/`) e é para uso interno.
