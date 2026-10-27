---
name: dba
description: Administra bancos de dados de clientes e da plataforma — PostgreSQL, MySQL/MariaDB, SQL Server, Oracle, Firebird, Progress OpenEdge, Db2, SAP HANA, MongoDB e os serviços gerenciados de AWS, GCP, Azure e OCI. Define como ler bancos de ERP sem impacto (réplica, CDC, janela), usuários de leitura, backup e restauração, alta disponibilidade, desempenho, licenciamento e migração. Use ao inventariar bancos, planejar a extração, dimensionar o banco da plataforma ou diagnosticar lentidão.
---

# Skill — DBA

## Método de leitura (decida nesta ordem)
| Situação | Método | Observação |
|---|---|---|
| Existe réplica de leitura | Ler da réplica | Confirme o atraso aceitável para o painel |
| Backup diário disponível e D-1 basta | Restaurar o backup num servidor da plataforma e ler dele | Zero impacto no ERP; ótimo para o backfill histórico |
| Banco até ~50 GB, atualização diária | Incremental por data de alteração, de madrugada | O mais simples; reconcilie contagens toda semana |
| Sem coluna de alteração confiável | Change Tracking (SQL Server), CDC, ou hash por janela de datas | Peça a autorização do fornecedor do ERP |
| Números precisam mudar em minutos | CDC por log (Debezium, DMS, Datastream, GoldenGate) | Só com o motivo registrado; alerta de log obrigatório |
| ERP SaaS ou banco inacessível | API do fornecedor | Respeite limites (429) e pagine |

## Resumo por SGBD
Detalhes, scripts e consultas em `conhecimento/bancos-de-dados/`.

| SGBD | Usuário de leitura | Incremental / CDC | Backup | Armadilha nº 1 |
|---|---|---|---|---|
| PostgreSQL | `pg_read_all_data` (14+) | coluna de alteração; replicação lógica (`wal_level=logical`) | pgBackRest + WAL | slot de replicação inativo enche o disco |
| MySQL / MariaDB | `GRANT SELECT` no schema | binlog `ROW` + GTID | XtraBackup / mariadb-backup + binlog | `utf8` não é `utf8mb4`; datas `0000-00-00` |
| SQL Server | `db_datareader` | Change Tracking (leve) ou CDC (precisa do SQL Agent; o Express não tem) | full + diferencial + log (modelo FULL) | log de transações que nunca trunca |
| Oracle | `CREATE SESSION` + `SELECT` por tabela | LogMiner (Debezium, DMS), GoldenGate | RMAN | AWR/ASH exigem Diagnostics Pack (só EE) |
| Firebird | `GRANT SELECT` | sem CDC nativo: coluna de data ou trigger de log | gbak / nbackup | copiar o `.fdb` aberto gera backup corrompido |
| Progress OpenEdge (Datasul) | usuário SQL com `SELECT` em `PUB` | data de alteração; OpenEdge CDC; Pro2 | probkup + after-imaging | largura SQL (SQL width) estoura em campos longos |
| SAP HANA | depende da licença (runtime × full use) | SLT, ODP via OData, Datasphere | backup nativo / Backint | acesso direto pode violar o contrato SAP |
| MongoDB | papel `read` | change streams (exige replica set) | snapshot / mongodump | tipos diferentes no mesmo campo |
| Db2 / IBM i | `GRANT SELECT` | SQL Replication, IIDR | `BACKUP ONLINE` / SAVLIB | drivers e CCSID (acentos) no IBM i |

## Banco da plataforma por porte
| Porte | Recomendação | Configuração inicial |
|---|---|---|
| P no ZimaOS (16 GB) | PostgreSQL 17/18 em contêiner com `mem_limit: 2g` + DuckDB para arquivos | `shared_buffers=512MB`, `effective_cache_size=1536MB`, `work_mem=16MB`, `maintenance_work_mem=256MB`, `max_connections=50` + PgBouncer |
| P na cloud | OCI Always Free (Autonomous de 20 GB ou VM A1 com PostgreSQL) | backup para Object Storage |
| M | PostgreSQL gerenciado (RDS, Cloud SQL, Azure Flexible, OCI) + warehouse serverless (BigQuery, Athena, Fabric) | réplica só se o RTO pedir |
| G | Warehouse ou lakehouse (BigQuery, Snowflake, Databricks, Redshift, ADW) + PostgreSQL para apps | HA zonal, PITR |

## Dimensionamento rápido
- **Memória**: o conjunto consultado no dia (gold + índices quentes) deve caber no cache. Mais memória resolve mais lentidão de BI do que mais CPU.
- **Disco**: dados × 1,3 (índices) × crescimento de 12 meses, mais 20% livres. Sempre SSD/NVMe; log/WAL em volume próprio quando possível.
- **Conexões**: pool (PgBouncer, ProxySQL) e cache no BI; painéis nunca abrem uma conexão por usuário.
- **CPU**: 4 vCPU atendem um porte P inteiro; cargas pesadas vão para a madrugada.

## Backup: regras
- 3-2-1: três cópias, dois meios, uma fora do servidor e imutável (Object Lock).
- RPO ≤ 15 min → log/WAL contínuo. RPO de 24 h → dump diário basta.
- Retenção padrão: 7 diários, 4 semanais, 12 mensais.
- Restauração testada todo mês, cronometrada e registrada.

## Diagnóstico de lentidão
1. É o banco? CPU, disco, esperas, bloqueios.
2. Qual consulta? As 20 maiores por tempo total.
3. Por quê? Plano de execução (`EXPLAIN`, plano real).
4. Correção: índice, estatística, reescrita, cache, mudar o horário da carga.
5. Medir de novo e registrar.
Consultas prontas por SGBD em `conhecimento/bancos-de-dados/desempenho-e-diagnostico.md`.

## Licenciamento: o que perguntar
- **SQL Server**: edição; por core (pacotes de 2, mínimo 4 por VM) ou Servidor + CAL; Software Assurance (mobilidade para cloud e réplica passiva).
- **Oracle**: edição (SE2 ou EE), métrica (Processor ou Named User Plus), packs e options em uso; virtualização (VMware não é particionamento reconhecido).
- **Na migração para cloud**: BYOL × licença incluída; Azure Hybrid Benefit; OCI costuma ser a mais favorável para BYOL Oracle.

## Monitoramento mínimo
| Sinal | Limite sugerido |
|---|---|
| Disco livre | < 20% alerta, < 10% crítico |
| Conexões | > 80% do máximo |
| Bloqueio | > 60 s |
| Atraso de réplica ou CDC | > 2× o intervalo de carga |
| Log/WAL retido | > 10% do disco |
| Último backup bom | > 26 h |
| Último teste de restauração | > 35 dias |

## Estimativa de esforço (horas)
| Item | Simples | Médio | Complexo |
|---|---|---|---|
| Inventário e avaliação de saúde (por banco) | 4 | 8 | 16 |
| Usuário de leitura e acesso seguro (VPN/túnel) | 2 | 4 | 8 |
| Habilitar e validar CDC (por banco) | 8 | 16 | 32 |
| Banco da plataforma (instalação, parâmetros, backup, monitoramento) | 6 | 12 | 24 |
| Rotina de backup e teste de restauração documentado | 4 | 8 | 16 |
| Diagnóstico e tuning (por rodada) | 8 | 16 | 40 |
| Alta disponibilidade (réplica e failover testado) | 8 | 24 | 60 |
| Migração de SGBD ou para serviço gerenciado (por banco) | 24 | 60 | 160 |

## Antipadrões
- Carga pesada no banco do ERP em horário comercial.
- Ferramenta de extração logada como `sa`, `sys` ou `postgres`.
- Backup que nunca foi restaurado.
- CDC sem alerta de crescimento de log.
- Painel em DirectQuery batendo direto na produção do ERP.
- Mudar `READ_COMMITTED_SNAPSHOT`, collation ou parâmetros do banco do ERP sem o fornecedor.

## Referências
Índice em `conhecimento/bancos-de-dados/README.md`: um arquivo por SGBD, bancos de AWS, GCP, Azure e OCI, bancos dos ERPs brasileiros, `cdc-por-sgbd.md`, `backup-e-alta-disponibilidade.md`, `seguranca-de-bancos.md`, `desempenho-e-diagnostico.md` e `migracao-entre-sgbds.md`.
