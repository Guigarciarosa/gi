---
sgbd: Oracle Database
familia: relacional
licenca: comercial (edição Free gratuita, com limites)
agentes: [dba, engenheiro, finops, cyber, arquiteto]
revisado: 2026-10
---

# Oracle Database

## O que é e quando usar
Banco relacional corporativo presente em ERPs grandes (Oracle EBS, JD Edwards,
TOTVS Protheus e RM em Oracle, Sankhya, WinThor, Consinco) e em sistemas
hospitalares (Tasy, MV). Na plataforma de dados, é fonte; como destino, só quando o
cliente já tem licença ou usa o Autonomous Database na OCI.

## Versões, edições e licença
- **19c** é a versão de suporte longo mais encontrada nos clientes. **23ai** é a geração atual (a sucessora 26ai foi anunciada); confira a política de suporte vigente antes de recomendar migração.
- **Free** (antigo XE): grátis, com limites de CPU, memória e dados de usuário (na 23ai, cerca de 2 threads, 2 GB de RAM e 12 GB de dados).
- **Standard Edition 2 (SE2)**: servidores de até 2 soquetes e no máximo 16 threads por banco; sem Data Guard, particionamento e consultas paralelas.
- **Enterprise Edition (EE)**: completa, com *options* e *packs* pagos à parte: Partitioning, Diagnostics e Tuning Packs, Advanced Security, RAC, Active Data Guard, In-Memory.
- Licença por **Processor** (núcleos × fator) ou **Named User Plus**. É o item que mais gera multa em auditoria.

## Armadilhas de licença (leia antes de mexer)
- Consultar `DBA_HIST_*`, `V$ACTIVE_SESSION_HISTORY` ou gerar AWR/ADDM **conta como uso do Diagnostics Pack** (só existe na EE e é pago). Em SE2, use **Statspack**.
- VMware não é particionamento reconhecido pela Oracle: a interpretação comum exige licenciar todos os hosts do cluster. Confirme o contrato do cliente.
- Na cloud vale o documento *Licensing Oracle Software in the Cloud Computing Environment* (regras por vCPU em AWS, Azure e Google). A OCI tem regras próprias, em geral mais favoráveis para BYOL.

## Conectar e extrair
- Drivers: `python-oracledb` (modo thin, sem Instant Client), JDBC `ojdbc`, ODBC.
- Usuário de leitura com privilégio mínimo:
  ```sql
  CREATE USER extracao IDENTIFIED BY "troque-por-senha-forte";
  GRANT CREATE SESSION TO extracao;
  GRANT SELECT ON erp.pedidos TO extracao;        -- por tabela; evite SELECT ANY TABLE
  ```
- Incremental: coluna de data de alteração. `ORA_ROWSCN` só é confiável por linha em tabelas criadas com `ROWDEPENDENCIES`.
- Carga em massa: Data Pump (`expdp`/`impdp`) ou consulta paralela (EE).
- CDC:
  - **LogMiner** (Debezium Oracle, AWS DMS): banco em `ARCHIVELOG` e log suplementar.
    ```sql
    SELECT log_mode FROM v$database;                       -- precisa ser ARCHIVELOG
    ALTER DATABASE ADD SUPPLEMENTAL LOG DATA;
    ALTER TABLE erp.pedidos ADD SUPPLEMENTAL LOG DATA (ALL) COLUMNS;
    ```
    O usuário do conector precisa de privilégios de LogMiner (`LOGMINING`, `SELECT` em visões `V_$`); siga a lista da documentação do Debezium.
  - **XStream** e **GoldenGate**: exigem licença do GoldenGate. Na OCI existe o OCI GoldenGate gerenciado.
  - O antigo "Oracle Change Data Capture" foi descontinuado na 12c.

## Desempenho
```sql
-- SQL mais caro em memória (tempos em microssegundos)
SELECT sql_id, executions, ROUND(elapsed_time / 1e6) AS seg_total,
       ROUND(elapsed_time / NULLIF(executions, 0) / 1e3, 1) AS ms_medio,
       SUBSTR(sql_text, 1, 100) AS trecho
FROM v$sql ORDER BY elapsed_time DESC FETCH FIRST 20 ROWS ONLY;

-- plano real da última execução de um sql_id
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR('&sql_id', NULL, 'ALLSTATS LAST'));

-- sessões esperando e quem bloqueia
SELECT sid, username, event, blocking_session, seconds_in_wait FROM v$session
WHERE wait_class <> 'Idle' ORDER BY seconds_in_wait DESC;
```
- Estatísticas atualizadas (`DBMS_STATS`), variáveis de ligação (bind) nas aplicações, `SGA_TARGET` e `PGA_AGGREGATE_TARGET` dimensionados.

## Backup e alta disponibilidade
- **RMAN**: backup incremental nível 0/1, archivelogs, validação (`RESTORE VALIDATE`). *Block change tracking* acelera o incremental (EE).
- Lógico: Data Pump, útil para cópias de schema, não para recuperação de desastre.
- HA/DR: Data Guard (EE; Active Data Guard é option paga), RAC (option da EE). Em SE2: standby manual com aplicação de archivelogs ou ferramenta de terceiros.

## Segurança
- Perfis de senha, contas padrão bloqueadas, privilégios mínimos (nada de `DBA` para aplicação).
- Criptografia em repouso (TDE) faz parte do Advanced Security na EE on-premise; nos serviços da OCI vem incluída.
- Unified Auditing para quem lê dados sensíveis.

## Na cloud
| Provedor | Serviço |
|---|---|
| OCI | Autonomous Database (Transaction Processing, Data Warehouse, JSON), Base Database Service, Exadata Database Service; Always Free com 2 Autonomous Databases |
| Multicloud | Oracle Database@Azure, @AWS e @Google Cloud (Exadata e Autonomous dentro do datacenter da outra cloud) |
| AWS | RDS for Oracle (SE2 com licença incluída ou BYOL; EE em BYOL), EC2 |
| Azure / GCP | VMs (verifique a regra de licença por vCPU) |

## Armadilhas
- String vazia é `NULL` no Oracle: `WHERE campo = ''` nunca retorna linhas.
- `DATE` guarda hora; `NUMBER` sem precisão vira float no destino se não tipar.
- Conjunto de caracteres antigo (`WE8ISO8859P1`, `WE8MSWIN1252`) com dados gravados em outra codificação gera acentos quebrados: valide amostras na bronze.
- Sequências e triggers fazem o papel de autoincremento em bancos antigos.
- Packs usados sem querer (AWR) aparecem em auditoria de licença.

## Documentação oficial
- https://docs.oracle.com/en/database/oracle/oracle-database/19/index.html
- https://docs.oracle.com/en/database/oracle/oracle-database/23/index.html
- https://docs.oracle.com/en/database/oracle/oracle-database/19/dblic/
- https://www.oracle.com/assets/cloud-licensing-070579.pdf
- https://docs.oracle.com/en/cloud/paas/autonomous-database/
- https://debezium.io/documentation/reference/stable/connectors/oracle.html
