---
sgbd: MySQL e MariaDB
familia: relacional
licenca: MySQL Community GPLv2 (Enterprise comercial); MariaDB GPLv2
agentes: [dba, engenheiro, fullstack]
revisado: 2026-10
---

# MySQL e MariaDB

## O que é e quando usar
Bancos relacionais abertos muito comuns em sistemas web, e-commerce (WooCommerce,
Magento), sistemas próprios de associações e pequenos ERPs. O MariaDB nasceu como
fork do MySQL e hoje diverge em recursos; trate como produtos diferentes ao copiar
receitas.

## Versões, edições e licença
- MySQL: 8.0 chegou ao fim de suporte em 2026; 8.4 é a versão LTS; a série 9.x é a linha "innovation" (lançamentos frequentes, suporte curto). Prefira LTS em produção.
- MariaDB: versões LTS (10.6, 10.11, 11.4, 11.8) com 5 anos de suporte; as demais são de curto prazo.
- MySQL Enterprise (Oracle) acrescenta backup, auditoria e firewall pagos. Confira datas atuais de suporte antes de recomendar.

## Conectar e extrair
- Drivers: `PyMySQL`/`mysqlclient`, Connector/J, MariaDB Connector.
- Usuário de leitura e de CDC:
  ```sql
  CREATE USER 'extracao'@'10.8.0.%' IDENTIFIED BY 'troque-por-senha-forte';
  GRANT SELECT ON erp.* TO 'extracao'@'10.8.0.%';

  -- CDC (Debezium): leitura do binlog
  CREATE USER 'cdc'@'10.8.0.%' IDENTIFIED BY '...';
  GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'cdc'@'10.8.0.%';
  ```
- CDC exige `binlog_format = ROW`, `binlog_row_image = FULL`, `server_id` único e, de preferência, GTID ligado. Retenção do binlog maior que a maior parada esperada do conector (`binlog_expire_logs_seconds`). No RDS: `CALL mysql.rds_set_configuration('binlog retention hours', 48);`.
- Exportação consistente sem travar InnoDB: `mysqldump --single-transaction --quick` ou `mydumper` (paralelo).

## Desempenho
```sql
-- consultas mais caras (performance_schema; tempos em picossegundos)
SELECT DIGEST_TEXT, COUNT_STAR,
       ROUND(SUM_TIMER_WAIT / 1e12, 1) AS seg_total,
       ROUND(AVG_TIMER_WAIT / 1e9, 1) AS ms_medio
FROM performance_schema.events_statements_summary_by_digest
ORDER BY SUM_TIMER_WAIT DESC LIMIT 20;

-- quem está rodando agora
SELECT * FROM sys.processlist WHERE command <> 'Sleep' ORDER BY time DESC;
```
- `slow_query_log = ON` com `long_query_time = 1`.
- `EXPLAIN ANALYZE` (MySQL 8.0.18+) mostra o plano real.
- `innodb_buffer_pool_size` entre 50% e 70% da RAM em servidor dedicado.
- InnoDB guarda a tabela ordenada pela chave primária: PK curta e crescente (inteiro ou UUID ordenado).

## Backup e alta disponibilidade
- Físico a quente: Percona XtraBackup (MySQL) ou `mariadb-backup` (MariaDB); lógico: `mysqldump`/`mydumper`.
- PITR: backup + binlogs.
- HA: replicação assíncrona ou semi-síncrona; MySQL InnoDB Cluster (Group Replication); MariaDB Galera Cluster; ProxySQL ou MaxScale na frente.

## Segurança
- Usuário por aplicação com host restrito (`'app'@'10.0.0.%'`), nunca `'root'@'%'`.
- TLS (`require_secure_transport = ON`); plugin de autenticação `caching_sha2_password` (MySQL 8).
- Auditoria: plugin de auditoria do MariaDB ou Percona; no MySQL Community, logs gerais só para depuração (pesados).

## Na cloud
| Provedor | Serviço |
|---|---|
| AWS | RDS for MySQL, RDS for MariaDB, Aurora MySQL |
| GCP | Cloud SQL for MySQL |
| Azure | Azure Database for MySQL – Flexible Server (o serviço para MariaDB foi descontinuado) |
| OCI | MySQL HeatWave (MySQL com acelerador analítico em memória) |

## Armadilhas
- `utf8` no MySQL é `utf8mb3` (sem emoji e alguns caracteres): use `utf8mb4` em tudo.
- Datas `0000-00-00` e `sql_mode` permissivo quebram extração e tipos no destino; trate na bronze.
- Tabelas MyISAM em sistemas antigos: sem transação e sem consistência no CDC. Converta para InnoDB com o fornecedor.
- `lower_case_table_names` diferente entre Windows e Linux muda nomes de tabelas na migração.
- `TINYINT(1)` costuma significar booleano; converta explicitamente.

## Documentação oficial
- https://dev.mysql.com/doc/refman/8.4/en/
- https://dev.mysql.com/doc/refman/8.4/en/replication.html
- https://mariadb.com/kb/en/documentation/
- https://mariadb.com/kb/en/mariadb-backup-overview/
- https://debezium.io/documentation/reference/stable/connectors/mysql.html
