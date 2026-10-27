---
sgbd: Progress OpenEdge
familia: relacional
licenca: comercial (Progress Software)
agentes: [dba, engenheiro]
revisado: 2026-10
---

# Progress OpenEdge

## O que é e quando usar
Banco e plataforma de desenvolvimento (linguagem ABL, antiga 4GL) por trás do
**TOTVS Datasul** e de outros ERPs legados. O banco é pensado para a ABL; o acesso
SQL existe, mas é um motor separado e com particularidades. Sempre fonte.

## Versões e licença
- Linhas 11.7 e 12.x (12.2 e 12.8 são LTS). Confira o calendário de suporte da Progress e a versão homologada pela TOTVS para o Datasul do cliente.
- O acesso SQL (ODBC/JDBC) depende da licença de SQL do cliente. Confirme antes de planejar a extração.

## Conectar e extrair
- Drivers: ODBC e JDBC do próprio OpenEdge (DataDirect), apontando para o **broker SQL** (porta diferente da usada pelos clientes ABL).
- Esquema SQL padrão: `PUB`. Nomes de tabelas e campos com hífen exigem aspas:
  ```sql
  SELECT "cod-emitente", "nome-abrev", "dt-implant"
  FROM PUB."emitente"
  WHERE "dt-implant" >= '2026-01-01';
  ```
- Usuário SQL com `SELECT` apenas nas tabelas necessárias (`GRANT SELECT ON PUB."emitente" TO extracao;`).
- Datasul usa vários bancos por área (cadastros, financeiro, distribuição etc.). Mapeie com o key user quais bancos e tabelas guardam o que precisa.
- Incremental: datas de alteração quando existem; senão, janelas por data do documento + reconciliação.
- CDC: o OpenEdge tem *Change Data Capture* nativo desde a 11.7 (verifique se está licenciado e habilitado) e o **Pro2**, produto da Progress que replica o banco para SQL Server ou Oracle; uma réplica Pro2 existente é a melhor fonte.

## Desempenho
- Atualize as estatísticas do motor SQL, senão os planos ficam ruins:
  ```sql
  UPDATE TABLE STATISTICS AND INDEX STATISTICS AND ALL COLUMN STATISTICS FOR PUB."emitente";
  ```
- Evite varreduras completas de tabelas grandes em horário comercial; filtre por campos indexados.
- Use `WITH (NOLOCK)` do OpenEdge SQL apenas em exploração (lê sem bloqueio, pode ver dados inconsistentes).

## Backup e alta disponibilidade
- `probkup online` (backup a quente) e *after-imaging* (AI) para recuperação até um ponto no tempo.
- OpenEdge Replication para réplica de leitura/DR (licença à parte).
- Uma cópia restaurada do backup noturno é uma boa fonte para o backfill histórico.

## Segurança
- Usuários do domínio SQL separados dos usuários ABL; senha forte e acesso restrito por rede.
- Não exponha o broker SQL fora da rede; use VPN ou túnel.

## Na cloud
Sem serviço gerenciado: roda em VMs. A TOTVS oferece hospedagem do Datasul na
própria cloud (TOTVS Cloud); nesse caso, o acesso aos dados passa pelo contrato com a TOTVS.

## Armadilhas
- **Largura SQL (SQL width)**: o motor SQL tem um tamanho máximo por campo; dados maiores geram erro de valor acima do tamanho. Corrija com a ferramenta `dbtool` (opção de ajuste de largura SQL) em janela combinada.
- Campos com *extent* (vetores) aparecem no SQL como texto separado por ponto e vírgula: divida na silver.
- Datas e decimais com formatos regionais herdados da ABL.
- Nomes de campos com hífen quebram ferramentas que não colocam aspas.

## Documentação oficial
- https://docs.progress.com/
- https://www.progress.com/openedge
