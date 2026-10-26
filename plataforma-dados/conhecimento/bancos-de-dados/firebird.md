---
sgbd: Firebird
familia: relacional
licenca: aberta (IPL/IDPL)
agentes: [dba, engenheiro]
revisado: 2026-10
---

# Firebird

## O que é e quando usar
Banco relacional aberto, descendente do InterBase, muito usado em sistemas
brasileiros de pequeno porte: automação comercial, ERPs regionais, sistemas de
clínicas, contabilidade e postos. Leve e estável, mas com ferramentas e serviços
gerenciados escassos. Na plataforma de dados é sempre fonte.

## Versões e licença
- 3.0, 4.0 e 5.0 (lançada em 2024). Sistemas antigos ainda rodam 2.5 (sem suporte): sinalize como risco.
- Arquiteturas: SuperServer (padrão moderno), SuperClassic e Classic; também existe o modo embarcado (o sistema abre o arquivo direto).
- Gratuito; um banco é um arquivo `.fdb` (ou `.gdb` em sistemas antigos).

## Conectar e extrair
- Drivers: `firebird-driver` (Python, Firebird 3+), `fdb` (legado), Jaybird (JDBC), ODBC.
- Usuário de leitura (Firebird 3+):
  ```sql
  CREATE USER EXTRACAO PASSWORD 'troque-por-senha-forte';
  GRANT SELECT ON PEDIDOS TO USER EXTRACAO;
  GRANT SELECT ON ITENS_PEDIDO TO USER EXTRACAO;
  ```
  Em bancos com muitas tabelas, crie um papel (`CREATE ROLE LEITURA`), conceda `SELECT` ao papel e o papel ao usuário.
- Sem CDC nativo. Opções:
  1. Coluna de data de alteração (quando o sistema grava).
  2. Trigger que registra chave e operação numa tabela de log (combine com o fornecedor do sistema).
  3. Firebird 4+ tem replicação lógica embutida (journal), útil para manter uma réplica de leitura.
  4. Restaurar o backup diário (`gbak`) num servidor da plataforma e extrair dele: zero impacto.
- Conjunto de caracteres: bancos `NONE` ou `WIN1252`/`ISO8859_1` exigem informar o charset na conexão, senão os acentos chegam errados.

## Desempenho
```sql
-- conexões abertas
SELECT MON$ATTACHMENT_ID, MON$USER, MON$REMOTE_ADDRESS, MON$TIMESTAMP FROM MON$ATTACHMENTS;
-- consultas em execução
SELECT MON$ATTACHMENT_ID, MON$TIMESTAMP, MON$SQL_TEXT FROM MON$STATEMENTS WHERE MON$STATE = 1;
-- saúde das transações: distância grande entre a mais antiga e a próxima = lixo acumulado
SELECT MON$OLDEST_TRANSACTION, MON$OLDEST_ACTIVE, MON$OLDEST_SNAPSHOT, MON$NEXT_TRANSACTION FROM MON$DATABASE;
```
- Transações longas (inclusive de relatórios) impedem a coleta de versões antigas e deixam o banco lento: extração em transações curtas e somente leitura.
- `gstat -h` mostra o cabeçalho e os contadores de transação; o *sweep* limpa versões antigas.
- Índices com estatística desatualizada: `SET STATISTICS INDEX nome_indice;`.

## Backup e alta disponibilidade
- `gbak -b` (lógico, também reorganiza o banco na restauração) e `nbackup` (físico incremental por níveis).
- **Nunca** copie o arquivo `.fdb` com o banco aberto: a cópia sai corrompida.
- Teste a restauração (`gbak -c`) periodicamente: é o único jeito de saber se o backup presta.
- HA: replicação embutida do Firebird 4+ ou réplica por restauração periódica.

## Segurança
- Troque a senha do `SYSDBA` (o padrão antigo `masterkey` ainda aparece em produção).
- Firebird 3+ suporta criptografia de tráfego (`WireCrypt`); bloqueie a porta 3050 na internet.
- Plugins de criptografia do banco existem, mas dependem de fornecedor.

## Na cloud
Não há serviço gerenciado nas grandes clouds. Rode em VM (Linux ou Windows) ou no
ZimaOS em contêiner, com backup `gbak` agendado para o armazenamento de objetos.

## Armadilhas
- Dialeto 1 (bancos muito antigos) trata datas e números de forma diferente do dialeto 3.
- Charset `NONE` mistura codificações no mesmo banco.
- Banco embarcado não aceita conexões simultâneas de outra máquina: peça ao fornecedor o modo servidor ou use a cópia do backup.
- Tamanho de página pequeno em bancos antigos limita índices.

## Documentação oficial
- https://firebirdsql.org/en/documentation/
- https://firebirdsql.org/file/documentation/html/en/refdocs/fblangref50/firebird-50-language-reference.html
- https://firebirdsql.org/file/documentation/html/en/firebirddocs/gbak/firebird-gbak.html
- https://firebird-driver.readthedocs.io/
