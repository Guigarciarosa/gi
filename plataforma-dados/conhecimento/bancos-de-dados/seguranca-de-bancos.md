---
tema: segurança de bancos de dados e LGPD
agentes: [dba, cyber, engenheiro, fullstack]
revisado: 2026-10
---

# Segurança de bancos de dados

## Princípios
1. **Privilégio mínimo**: cada ferramenta com um usuário próprio, só com o que precisa.
2. **Nada exposto na internet**: bancos em rede privada; acesso por VPN, Tailscale, Cloudflare Tunnel ou Private Endpoint.
3. **Tudo cifrado em trânsito** (TLS) e **em repouso** (disco/TDE).
4. **Segredos em cofre**, rotação de senhas, nunca no código ou na planilha.
5. **Auditoria** de quem leu dados pessoais e sensíveis.
6. **Backup imutável** (ver `backup-e-alta-disponibilidade.md`).

## Usuários de extração por SGBD (resumo)
| SGBD | Comando principal | Observação |
|---|---|---|
| PostgreSQL | `GRANT pg_read_all_data TO extracao;` | ou `SELECT` por schema |
| MySQL | `GRANT SELECT ON erp.* TO 'extracao'@'10.8.0.%';` | host restrito |
| SQL Server | `ALTER ROLE db_datareader ADD MEMBER extracao;` | por banco |
| Oracle | `GRANT CREATE SESSION` + `GRANT SELECT ON tabela` | evite `SELECT ANY TABLE` |
| Firebird | `GRANT SELECT ON tabela TO USER EXTRACAO;` | ou papel |
| MongoDB | papel `read` no banco | autenticação ligada |
| Db2 | `GRANT SELECT ON tabela TO USER extracao` | no IBM i, autoridade de objeto |
Scripts completos nos arquivos de cada SGBD.

## Criptografia em repouso
| SGBD | Recurso | Observação de licença |
|---|---|---|
| PostgreSQL | disco cifrado (LUKS, volume cifrado da cloud) | TDE só em distribuições comerciais |
| MySQL | InnoDB tablespace encryption | keyring na Community; recursos extras no Enterprise |
| SQL Server | TDE | Standard a partir do 2019; Enterprise antes disso |
| Oracle | TDE | Advanced Security (EE) on-premise; incluído nos serviços da OCI |
| Serviços gerenciados | cifrado por padrão (KMS/CMEK opcional) | — |

## Dados pessoais (LGPD)
- Mapear colunas com CPF, nome, telefone, e-mail, endereço, saúde e biometria (o Cyber classifica; o DBA marca no catálogo).
- **Mascaramento**: Dynamic Data Masking (SQL Server/Azure SQL), visões mascaradas, ou hash com sal na silver quando o dado não precisa ser lido.
- **Minimização**: não trazer para a plataforma colunas sensíveis que nenhum KPI usa.
- **Segurança por linha**: RLS no PostgreSQL e no SQL Server; RLS no BI.
- **Retenção e exclusão**: política de retenção por tabela e rotina para atender pedidos de titulares.
- Dados de saúde e de crianças: controles reforçados e base legal específica (art. 11 e 14).

## Auditoria
| SGBD | Ferramenta |
|---|---|
| PostgreSQL | `pgaudit`, `log_connections`, logs no Loki/CloudWatch |
| SQL Server | SQL Server Audit (servidor e banco) |
| Oracle | Unified Auditing; Data Safe na OCI |
| MySQL / MariaDB | plugins de auditoria (MariaDB, Percona) |
| Clouds | Cloud Audit Logs, CloudTrail + RDS logs, Azure SQL Auditing |

## Checklist rápido (para o relatório do DBA e do Cyber)
- [ ] Porta do banco fechada para a internet
- [ ] Senha padrão trocada (`sa`, `sys`, `SYSDBA`, `postgres`)
- [ ] Usuário de extração somente leitura e por IP
- [ ] TLS ligado
- [ ] Disco/banco cifrado
- [ ] Backup imutável e restauração testada
- [ ] Auditoria de acesso a dados pessoais
- [ ] Versão com suporte e atualizações de segurança aplicadas

## Documentação oficial
- https://www.postgresql.org/docs/current/user-manag.html
- https://learn.microsoft.com/sql/relational-databases/security/security-center-for-sql-server-database-engine-and-azure-sql-database
- https://docs.oracle.com/en/database/oracle/oracle-database/19/dbseg/
- https://www.gov.br/anpd/pt-br
