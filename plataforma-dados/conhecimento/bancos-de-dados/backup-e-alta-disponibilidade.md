---
tema: backup, restauração, alta disponibilidade e recuperação de desastres
agentes: [dba, devops, cyber]
revisado: 2026-10
---

# Backup, alta disponibilidade e DR

## Conceitos que o cliente precisa decidir
- **RPO** (`infra.perda_dados`): quanto dado pode ser perdido. Define a frequência do backup e se precisa de log contínuo.
- **RTO** (`infra.disponibilidade`): quanto tempo pode ficar fora. Define se precisa de réplica com failover ou se restaurar o backup basta.

| RPO / RTO pedido | Solução mínima |
|---|---|
| RPO 24 h, RTO dias | dump diário + cópia externa |
| RPO 1 h, RTO horas | backup físico + log/WAL a cada 15 min + restauração ensaiada |
| RPO minutos, RTO minutos | réplica síncrona/assíncrona com failover automático + backup |
| RPO ~0, RTO segundos | cluster em zonas diferentes (serviço gerenciado multi-AZ) |

## Regra 3-2-1 (com 1 imutável)
Três cópias, em dois meios, uma fora do servidor; e uma cópia **imutável** (não pode ser
apagada nem pelo administrador por um período), a defesa real contra ransomware:
S3 Object Lock, Backblaze B2 Object Lock, Azure immutable blob, OCI retention rules,
Cloudflare R2 com bloqueio de objetos.

## Ferramentas por SGBD
| SGBD | Backup lógico | Backup físico / PITR | HA |
|---|---|---|---|
| PostgreSQL | `pg_dump` | pgBackRest, Barman, `pg_basebackup` (incremental no 17+) | streaming + Patroni |
| MySQL / MariaDB | `mysqldump`, `mydumper` | XtraBackup / mariadb-backup + binlog | replicação, Group Replication, Galera |
| SQL Server | — | full + diff + log (modelo FULL) | Always On AG, FCI, log shipping |
| Oracle | Data Pump | RMAN + archivelogs | Data Guard (EE), RAC |
| Firebird | `gbak` | `nbackup` | replicação 4+ |
| Progress OpenEdge | — | `probkup` + after-imaging | OpenEdge Replication |
| MongoDB | `mongodump` | snapshot, backup contínuo (Atlas/Ops Manager) | replica set |
| DuckDB / SQLite | `EXPORT DATABASE`, API de backup | Litestream (SQLite) | — |
| Qdrant | snapshot por coleção | snapshot do armazenamento | cluster (opcional) |

## Restauração: o teste que importa
Todo mês, para cada banco crítico:
1. Restaurar o backup mais recente num ambiente separado.
2. Aplicar logs até um horário escolhido (se houver PITR).
3. Conferir contagens e uma consulta de negócio conhecida (ex.: faturamento do mês anterior).
4. Registrar o tempo total e comparar com o RTO.
5. Guardar a evidência (data, tempo, quem fez) para o cliente e para auditoria.

## No ZimaOS da consultoria
- PostgreSQL: `pg_dump` diário + pgBackRest semanal para Backblaze B2/R2 com Object Lock.
- Qdrant: snapshot das coleções (a memória dos agentes se reconstrói reindexando, mas os entregáveis não).
- Pasta `/DATA/AppData/plataforma`: backup com restic para armazenamento externo, com retenção 7 diários / 4 semanais / 12 mensais.
- Ensaiar a restauração inteira numa VM Always Free da OCI a cada trimestre.

## Na cloud
- Backups automáticos dos serviços gerenciados (RDS, Cloud SQL, Azure SQL, Autonomous) com PITR de 7 a 35 dias: confira a retenção e copie para outra região/conta se o RPO de desastre pedir.
- Multi-AZ/HA regional custa o dobro: só com RTO que justifique.

## Documentação oficial
- https://pgbackrest.org/user-guide.html
- https://learn.microsoft.com/sql/relational-databases/backup-restore/back-up-and-restore-of-sql-server-databases
- https://docs.oracle.com/en/database/oracle/oracle-database/19/bradv/
- https://docs.percona.com/percona-xtrabackup/
- https://restic.readthedocs.io/
