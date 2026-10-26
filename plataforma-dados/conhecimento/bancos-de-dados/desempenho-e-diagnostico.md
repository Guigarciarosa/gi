---
tema: desempenho e diagnóstico de bancos de dados
agentes: [dba, engenheiro, analista, fullstack]
revisado: 2026-10
---

# Desempenho e diagnóstico

## Roteiro (vale para qualquer SGBD)
1. **Sintoma com número**: "o painel de vendas leva 40 s", não "está lento".
2. **É o banco?** CPU, memória, disco (latência e fila), rede, esperas e bloqueios.
3. **Qual consulta?** As 20 maiores por **tempo total** (frequência × duração), não só a mais lenta.
4. **Por quê?** Plano de execução real: varredura completa, estimativa errada de linhas, ordenação em disco, junção ruim.
5. **Corrigir** na ordem de menor risco: estatística → índice → reescrita → cache/agregado → horário da carga → hardware.
6. **Medir de novo** e registrar antes × depois.

## Onde olhar em cada SGBD
| SGBD | Consultas mais caras | Plano real | Esperas e bloqueios |
|---|---|---|---|
| PostgreSQL | `pg_stat_statements` | `EXPLAIN (ANALYZE, BUFFERS)` | `pg_stat_activity`, `pg_blocking_pids()` |
| MySQL / MariaDB | `performance_schema.events_statements_summary_by_digest`, slow log | `EXPLAIN ANALYZE` | `sys.processlist`, `information_schema.innodb_trx` |
| SQL Server | `sys.dm_exec_query_stats`, Query Store | plano real (SSMS) ou Query Store | `sys.dm_os_wait_stats`, `sp_WhoIsActive` |
| Oracle | `V$SQL` (AWR só com Diagnostics Pack) | `DBMS_XPLAN.DISPLAY_CURSOR` | `V$SESSION` (`blocking_session`) |
| Firebird | `MON$STATEMENTS` | plano no `isql` (`SET PLAN ON`) | `MON$ATTACHMENTS`, contadores de transação |
| Db2 LUW | `MON_GET_PKG_CACHE_STMT` | `db2exfmt` | `MON_GET_APPL_LOCKWAIT` |
| SAP HANA | `M_SQL_PLAN_CACHE` | `EXPLAIN PLAN` / PlanViz | `M_BLOCKED_TRANSACTIONS` |
| MongoDB | profiler (`system.profile`) | `explain("executionStats")` | `db.currentOp()` |
| ClickHouse | `system.query_log` | `EXPLAIN` | `system.processes` |
As consultas prontas estão nos arquivos de cada SGBD.

## Índices: regras práticas
- Índice para filtros e junções frequentes; colunas mais seletivas primeiro, mas igualdade antes de intervalo.
- Índice de cobertura (inclui as colunas retornadas) para consultas muito repetidas dos painéis.
- Cada índice custa em escrita e disco: em tabelas de ERP, **só com o fornecedor**; na plataforma, revise trimestralmente os não usados.
- Tabelas de fatos grandes: particione por data e filtre sempre pela partição.

## O BI é quem mais pesa
- **Import/extract** com atualização agendada em vez de DirectQuery/Live contra produção.
- Agregados prontos na gold (por dia, por cliente) em vez de o BI somar milhões de linhas.
- Cache do BI ligado (Metabase, Superset, Power BI, Looker Studio).
- Filtros padrão nos painéis (últimos 90 dias) para não abrir tudo.

## Carga sem atrapalhar o ERP
- Extração em lotes paginados por chave ou data, com limite de linhas por consulta.
- Horários combinados e janela máxima (ex.: 01h–05h); interrompa e retome no dia seguinte se passar.
- Medir antes e depois: CPU e IO do servidor do ERP durante a primeira carga.

## Sinais de alerta (para o monitoramento)
| Sinal | Possível causa |
|---|---|
| CPU 100% em horário comercial | consulta sem índice, painel em DirectQuery |
| Disco com fila alta | varreduras completas, backup no horário errado |
| Muitas conexões | aplicação sem pool, BI abrindo conexão por usuário |
| Bloqueios longos | transação aberta esquecida, carga em horário de uso |
| Log/WAL crescendo | backup de log parado, slot de replicação inativo |

## Documentação oficial
- https://www.postgresql.org/docs/current/using-explain.html
- https://dev.mysql.com/doc/refman/8.4/en/optimization.html
- https://learn.microsoft.com/sql/relational-databases/performance/monitoring-performance-by-using-the-query-store
- https://docs.oracle.com/en/database/oracle/oracle-database/19/tgsql/
