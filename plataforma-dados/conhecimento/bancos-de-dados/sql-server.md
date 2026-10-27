---
sgbd: Microsoft SQL Server
familia: relacional
licenca: comercial (Express e Developer gratuitas, com limites)
agentes: [dba, engenheiro, finops, cyber]
revisado: 2026-10
---

# Microsoft SQL Server

## O que é e quando usar
O banco mais comum nos ERPs de médio porte no Brasil: TOTVS Protheus, TOTVS RM,
Senior, Sankhya, SAP Business One e muitos sistemas próprios rodam nele. Na
plataforma de dados, ele quase sempre é **fonte**; raramente vale a licença para ser
o destino analítico de uma PME.

## Versões, edições e licença
- Versões com suporte em 2026: 2016 (suporte estendido termina em julho de 2026), 2017, 2019, 2022 e 2025. 2014 e anteriores estão sem suporte: sinalize como risco.
- **Express**: grátis, limite de 10 GB por banco, 1 soquete ou 4 núcleos e pouca memória de buffer; **sem SQL Server Agent** (sem CDC e sem jobs agendados). O SQL Server 2025 ampliou o limite do Express; confirme os números da versão do cliente.
- **Developer**: grátis, só para desenvolvimento e testes.
- **Standard**: por núcleo (pacotes de 2, mínimo de 4 núcleos por VM) ou Servidor + CAL; limites de núcleos e memória por instância.
- **Enterprise**: sem limites, Always On completo, recursos avançados.
- **Software Assurance** dá mobilidade de licença para cloud, réplica passiva gratuita e Azure Hybrid Benefit. Pergunte se o cliente tem.

## Conectar e extrair
- Drivers: ODBC Driver 18 (`pyodbc`), `pymssql`, JDBC da Microsoft. O driver 18 cifra por padrão: com certificado autoassinado use `TrustServerCertificate=yes` só em rede privada.
- Usuário de leitura:
  ```sql
  CREATE LOGIN extracao WITH PASSWORD = 'troque-por-senha-forte', CHECK_POLICY = ON;
  USE erp;
  CREATE USER extracao FOR LOGIN extracao;
  ALTER ROLE db_datareader ADD MEMBER extracao;
  ```
- **Change Tracking** (leve, informa a chave das linhas alteradas e a versão; exige chave primária na tabela):
  ```sql
  ALTER DATABASE erp SET CHANGE_TRACKING = ON (CHANGE_RETENTION = 3 DAYS, AUTO_CLEANUP = ON);
  ALTER TABLE dbo.pedidos ENABLE CHANGE_TRACKING;
  -- leitura incremental: guarde CHANGE_TRACKING_CURRENT_VERSION() a cada carga
  SELECT ct.id, ct.SYS_CHANGE_OPERATION, p.*
  FROM CHANGETABLE(CHANGES dbo.pedidos, @ultima_versao) AS ct
  LEFT JOIN dbo.pedidos p ON p.id = ct.id;
  ```
  Antes, confira se a tabela tem chave primária (`sp_pkeys 'pedidos'`); em tabelas de ERP isso varia.
- **CDC** (guarda as linhas alteradas em tabelas `cdc.*`; usado por Debezium, AWS DMS e Data Factory): disponível no Standard desde o 2016 SP1, exige o SQL Server Agent ligado.
  ```sql
  EXEC sys.sp_cdc_enable_db;
  EXEC sys.sp_cdc_enable_table @source_schema = N'dbo', @source_name = N'pedidos', @role_name = NULL;
  ```
- Combine a habilitação com o fornecedor do ERP: CDC e Change Tracking criam objetos e consomem log.
- `WITH (NOLOCK)` lê dados sujos e pode pular ou duplicar linhas; use só em exploração, nunca em carga financeira. Prefira réplica ou snapshot.

## Desempenho
```sql
-- consultas mais caras desde o último reinício (tempos em microssegundos)
SELECT TOP 20 qs.total_elapsed_time / 1000 AS ms_total, qs.execution_count,
       qs.total_elapsed_time / qs.execution_count / 1000 AS ms_medio,
       SUBSTRING(st.text, (qs.statement_start_offset / 2) + 1, 200) AS trecho
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) st
ORDER BY qs.total_elapsed_time DESC;

-- principais esperas do servidor
SELECT TOP 15 wait_type, wait_time_ms / 1000 AS seg, waiting_tasks_count
FROM sys.dm_os_wait_stats
WHERE wait_type NOT LIKE 'SLEEP%' AND wait_type NOT LIKE 'BROKER%'
  AND wait_type NOT IN ('XE_TIMER_EVENT', 'REQUEST_FOR_DEADLOCK_SEARCH', 'LAZYWRITER_SLEEP',
                        'SQLTRACE_BUFFER_FLUSH', 'CHECKPOINT_QUEUE', 'WAITFOR', 'XE_DISPATCHER_WAIT')
ORDER BY wait_time_ms DESC;
```
- Query Store guarda histórico de planos (ligado por padrão em bancos novos a partir do 2022).
- Ferramentas gratuitas da comunidade: `sp_WhoIsActive`, First Responder Kit (`sp_Blitz`, `sp_BlitzCache`), manutenção do Ola Hallengren.
- Configuração: `max server memory` deixando memória ao Windows, `cost threshold for parallelism` em torno de 50, `MAXDOP` conforme núcleos, tempdb com vários arquivos iguais.

## Backup e alta disponibilidade
- Modelo de recuperação **FULL** exige backup de log frequente; sem ele o log cresce até encher o disco. **SIMPLE** não permite PITR.
- Rotina típica: completo semanal, diferencial diário, log a cada 15 minutos; compressão de backup (disponível no Standard).
- Backup para URL: Azure Blob e, no 2022, armazenamento compatível com S3.
- Express não tem Agent: agende `sqlcmd` pelo Agendador de Tarefas do Windows.
- HA: Always On Availability Groups (Enterprise; o Standard tem o "Basic AG" com 2 réplicas e 1 banco por grupo), Failover Cluster Instance, log shipping.

## Segurança
- Autenticação Windows/Entra ID quando possível; logins SQL com política de senha.
- TDE (criptografia em repouso) existe no Standard a partir do 2019. Always Encrypted para colunas sensíveis.
- SQL Server Audit em nível de servidor e de banco; Dynamic Data Masking para esconder CPF de quem não precisa.

## Na cloud
| Provedor | Serviço |
|---|---|
| Azure | Azure SQL Database (DTU, vCore, serverless, Hyperscale), Azure SQL Managed Instance (compatibilidade alta, tem Agent e CDC), SQL Server em VM |
| AWS | RDS for SQL Server, SQL Server em EC2 |
| GCP | Cloud SQL for SQL Server |
| OCI | SQL Server em VM (sem serviço gerenciado) |
Leitura sem impacto no Azure: Fabric Mirroring replica Azure SQL e Managed Instance para o OneLake.

## Armadilhas
- Log de transações gigante: banco em FULL sem backup de log.
- Collation diferente entre bancos (`Latin1_General_CI_AS` × `SQL_Latin1_General_CP1_CI_AS`) quebra joins e ordenação de acentos.
- `datetime` arredonda milissegundos; `datetime2` não. Converta com cuidado.
- Protheus: excluídos lógicos com `D_E_L_E_T_ = '*'`; filtre sempre.
- Crescimento automático em porcentagem em arquivos grandes causa pausas; use MB fixos.
- Mudar `READ_COMMITTED_SNAPSHOT` no banco do ERP só com o fornecedor (muda o comportamento de bloqueios).

## Documentação oficial
- https://learn.microsoft.com/sql/sql-server/
- https://learn.microsoft.com/sql/relational-databases/track-changes/about-change-tracking-sql-server
- https://learn.microsoft.com/sql/relational-databases/track-changes/about-change-data-capture-sql-server
- https://learn.microsoft.com/sql/relational-databases/backup-restore/back-up-and-restore-of-sql-server-databases
- https://learn.microsoft.com/sql/sql-server/editions-and-components-of-sql-server-2022
- https://learn.microsoft.com/azure/azure-sql/
