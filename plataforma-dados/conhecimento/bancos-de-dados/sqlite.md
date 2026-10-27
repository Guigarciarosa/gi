---
sgbd: SQLite
familia: relacional embarcado
licenca: domínio público
agentes: [dba, fullstack, engenheiro]
revisado: 2026-10
---

# SQLite

## O que é e quando usar
Banco relacional embarcado: uma biblioteca que grava num único arquivo, sem servidor.
Está em celulares, navegadores, apps desktop, equipamentos e coletores. Bom para app
de campo offline (sincroniza depois), configuração local e pequenas ferramentas.
Não é servidor multiusuário: só um processo grava por vez.

## Versões e licença
- Série 3.x, atualizada com frequência e compatível com arquivos antigos. Domínio público, sem custo.

## Conectar e extrair
- Python traz o módulo `sqlite3`; DuckDB lê arquivos SQLite direto (`ATTACH 'app.db' (TYPE sqlite)`).
- Para extrair de equipamentos ou apps: copie o arquivo com o app parado ou use a API de backup online (`.backup` no shell ou `sqlite3.Connection.backup`). Copiar o arquivo durante uma escrita pode gerar cópia inconsistente.

## Desempenho e boas práticas
- `PRAGMA journal_mode = WAL;` permite leituras enquanto um processo grava.
- `PRAGMA foreign_keys = ON;` (vem desligado por padrão).
- Transações em lote para inserções em massa (milhares de linhas por `COMMIT`).
- `EXPLAIN QUERY PLAN` mostra se o índice está sendo usado.

## Backup e replicação
- API de backup online, `VACUUM INTO 'copia.db'`, ou **Litestream** (replica o WAL continuamente para S3 ou compatível).

## Armadilhas
- Tipagem flexível: uma coluna `INTEGER` aceita texto. Use `STRICT` nas tabelas novas.
- Datas são texto, número ou real, conforme quem gravou: padronize ISO 8601.
- Arquivo em pasta de rede (SMB/NFS) corrompe por causa de travas de arquivo.

## Documentação oficial
- https://www.sqlite.org/docs.html
- https://www.sqlite.org/wal.html
- https://litestream.io/
