---
tema: migração entre SGBDs e para serviços gerenciados
agentes: [dba, arquiteto, engenheiro, finops, devops]
revisado: 2026-10
---

# Migração entre SGBDs e para a cloud

## Tipos de migração
| Tipo | Exemplo | Risco |
|---|---|---|
| Mesmo SGBD, nova versão | SQL Server 2014 → 2022 | baixo/médio (compatibilidade) |
| Mesmo SGBD, para gerenciado | PostgreSQL local → Cloud SQL; SQL Server → Azure SQL MI | baixo/médio |
| SGBD diferente | Oracle → PostgreSQL; MySQL → PostgreSQL; Firebird → PostgreSQL | alto (código, tipos, comportamento) |
| Banco de ERP | qualquer mudança no banco do Protheus/RM/Datasul | só com o fornecedor e versão homologada |

## Ferramentas
| Origem → destino | Ferramenta |
|---|---|
| MySQL, SQLite, SQL Server → PostgreSQL | **pgloader** |
| Oracle → PostgreSQL | **ora2pg**; Google DMS com conversão; AWS DMS + Schema Conversion |
| SQL Server → Aurora PostgreSQL mantendo T-SQL | **Babelfish for Aurora PostgreSQL** |
| Oracle, MySQL, Db2, SAP ASE → SQL Server/Azure SQL | **SSMA** (SQL Server Migration Assistant) |
| SQL Server → Azure SQL / Managed Instance | Azure Database Migration Service, backup/restore para MI, Log Replay Service |
| Qualquer → AWS | AWS DMS (carga + CDC) e DMS Schema Conversion |
| Qualquer → Google Cloud | Database Migration Service, Datastream |
| Oracle → OCI | Zero Downtime Migration, OCI Database Migration, Data Pump, GoldenGate |
| Firebird → PostgreSQL | exportação por tabela (CSV) + scripts; ferramentas de terceiros |
| Validação de dados | contagens e somas por tabela/período; `data-diff`/consultas de hash por bloco |

## Mapa de tipos mais comuns (→ PostgreSQL)
| Origem | Tipo | PostgreSQL |
|---|---|---|
| Oracle | `NUMBER(p,s)` / `NUMBER` | `numeric(p,s)` / `numeric` (ou `bigint` quando inteiro) |
| Oracle | `DATE` | `timestamp(0)` (o DATE do Oracle tem hora) |
| Oracle | `VARCHAR2`, `CLOB`, `BLOB` | `varchar`, `text`, `bytea` |
| SQL Server | `DATETIME` / `DATETIME2` | `timestamp` (com cuidado com fuso) |
| SQL Server | `BIT`, `NVARCHAR(MAX)`, `UNIQUEIDENTIFIER`, `MONEY` | `boolean`, `text`, `uuid`, `numeric(19,4)` |
| MySQL | `TINYINT(1)`, `DATETIME`, `ENUM` | `boolean`, `timestamp`, `text` + `CHECK` (ou tipo enum) |
| Firebird | `BLOB SUB_TYPE TEXT`, `DOUBLE PRECISION` | `text`, `double precision` (ou `numeric` para valores) |

Diferenças de comportamento que quebram aplicações: string vazia = `NULL` no Oracle;
comparação sem diferenciar maiúsculas no SQL Server/MySQL (collation) e diferenciando no
PostgreSQL; `TOP` × `LIMIT`; funções de data; sequências × `IDENTITY`; procedures e triggers.

## Plano de corte (cutover)
1. **Inventário**: objetos, tamanho, dependências (aplicações, relatórios, jobs, integrações).
2. **Conversão de schema** e código, com testes automatizados das consultas críticas.
3. **Carga inicial** + **CDC** para manter o destino sincronizado.
4. **Validação**: contagens, somas por mês, amostras linha a linha, relatórios de negócio batendo.
5. **Ensaio do corte** em homologação, cronometrado.
6. **Corte**: congelar escrita, aplicar últimas mudanças, validar, apontar aplicações, liberar.
7. **Plano de volta**: até quando é possível voltar e como (CDC reverso ou backup).
8. **Desligar a origem** só depois de um ciclo de fechamento mensal completo no destino.

## Estimativa (horas, por banco)
| Cenário | Simples | Médio | Complexo |
|---|---|---|---|
| Upgrade de versão no mesmo SGBD | 8 | 24 | 60 |
| Para serviço gerenciado (mesmo SGBD) | 16 | 40 | 100 |
| Troca de SGBD (sem muito código no banco) | 40 | 100 | 240 |
| Troca de SGBD com muitas procedures/triggers | 100 | 240 | 600 |

## Documentação oficial
- https://pgloader.readthedocs.io/
- https://ora2pg.darold.net/documentation.html
- https://docs.aws.amazon.com/dms/latest/userguide/
- https://cloud.google.com/database-migration/docs
- https://learn.microsoft.com/sql/ssma/sql-server-migration-assistant
- https://babelfishpg.org/docs/
