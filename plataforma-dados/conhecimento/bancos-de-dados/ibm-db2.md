---
sgbd: IBM Db2 (LUW, z/OS e IBM i)
familia: relacional
licenca: comercial (Community Edition gratuita, com limites)
agentes: [dba, engenheiro, finops]
revisado: 2026-10
---

# IBM Db2

## O que é e quando usar
Família de bancos relacionais da IBM em três plataformas: **Db2 para Linux, Unix e
Windows (LUW)**, **Db2 para z/OS** (mainframe) e **Db2 for i**, embutido no IBM i
(o antigo AS/400). No Brasil aparece em bancos, seguradoras, redes varejistas e
indústrias com sistemas antigos no IBM i. Sempre fonte.

## Versões, edições e licença
- LUW: 11.5 e 12.1 (2024). Community Edition gratuita limitada a 4 núcleos e 16 GB de RAM; edições Standard e Advanced pagas.
- IBM i: o Db2 vem com o sistema operacional; a versão acompanha o release do IBM i (7.4, 7.5, 7.6).

## Conectar e extrair
- LUW e z/OS: IBM Data Server Driver (ODBC/CLI, JDBC `db2jcc4`), `ibm_db` no Python.
- IBM i: JDBC **JTOpen** (`jt400`) ou ODBC do IBM i Access. Tabelas ficam em bibliotecas (equivalentes a schemas); arquivos físicos antigos podem não ter chave nem journal.
- Usuário de leitura:
  ```sql
  GRANT CONNECT ON DATABASE TO USER EXTRACAO;      -- LUW
  GRANT SELECT ON ERP.PEDIDOS TO USER EXTRACAO;
  ```
- Incremental: coluna de data de alteração ou `ROW CHANGE TIMESTAMP` (coluna gerada que o próprio Db2 mantém, LUW/z/OS).
- CDC: SQL Replication e Q Replication (Db2), **IBM Data Replication (IIDR)** licenciado, conector Db2 do Debezium (LUW, exige configurar a captura ASN). No IBM i, o CDC depende de *journaling* ligado nas tabelas.

## Desempenho
```sql
-- LUW: instruções mais caras no cache de pacotes
SELECT SUBSTR(STMT_TEXT, 1, 120) AS trecho, NUM_EXECUTIONS, TOTAL_ACT_TIME, ROWS_READ
FROM TABLE(MON_GET_PKG_CACHE_STMT(NULL, NULL, NULL, -2))
ORDER BY TOTAL_ACT_TIME DESC FETCH FIRST 20 ROWS ONLY;
```
- `RUNSTATS` para estatísticas e `REORG` para tabelas fragmentadas; `db2advis` sugere índices.
- No IBM i: Visual Explain e o *Index Advisor* do IBM i Navigator.

## Backup e alta disponibilidade
- LUW: `BACKUP DATABASE ... ONLINE` com *archive logging*; HADR para réplica com failover.
- IBM i: `SAVLIB`/BRMS e replicação de journal (soluções de HA de terceiros são comuns).

## Segurança
- Autenticação pelo sistema operacional ou LDAP; privilégios por papel; auditoria com `db2audit` (LUW).
- No IBM i, a autoridade de objeto (`*USE`, `*CHANGE`) vale também para o acesso SQL.

## Na cloud
| Provedor | Serviço |
|---|---|
| IBM Cloud | Db2 on Cloud, Db2 Warehouse |
| AWS | Amazon RDS for Db2, EC2 |
| Azure / GCP | VMs |
| IBM i | Power Virtual Server (IBM Cloud) e provedores especializados |

## Armadilhas
- **CCSID** (codificação) no IBM i: campos com CCSID 65535 chegam como binário; defina a tradução no driver ou converta para 37/1047/284 conforme o caso.
- Campos `CHAR` com espaços à direita; datas guardadas como números (`AAAAMMDD`) em sistemas antigos.
- Licença por PVU (Processor Value Unit) em ambientes virtualizados: confira com o cliente.

## Documentação oficial
- https://www.ibm.com/docs/en/db2/12.1
- https://www.ibm.com/docs/en/i/7.5
- https://jt400.sourceforge.net/
- https://debezium.io/documentation/reference/stable/connectors/db2.html
