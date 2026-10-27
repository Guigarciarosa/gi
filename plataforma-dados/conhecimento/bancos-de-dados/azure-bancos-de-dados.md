---
plataforma: Microsoft Azure
tema: bancos de dados gerenciados
agentes: [dba, arquiteto, finops, engenheiro, devops]
revisado: 2026-10
---

# Bancos de dados no Azure

## Mapa de serviços
| Categoria | Serviço | Quando usar |
|---|---|---|
| SQL Server gerenciado | **Azure SQL Database** (DTU ou vCore; serverless com pausa automática; Hyperscale) | bancos novos ou que cabem num banco isolado |
| SQL Server quase completo | **Azure SQL Managed Instance** | migrar ERPs em SQL Server (tem SQL Agent, CDC, jobs entre bancos) |
| SQL Server em VM | SQL Server on Azure VMs | controle total; licença própria com Azure Hybrid Benefit |
| PostgreSQL / MySQL | Azure Database for PostgreSQL e for MySQL – **Flexible Server** | apps e banco da plataforma |
| NoSQL multimodelo | **Cosmos DB** (NoSQL, MongoDB, Cassandra, Gremlin, Table; PostgreSQL distribuído) | apps globais, baixa latência |
| Analytics | **Microsoft Fabric** (Lakehouse, Warehouse, Eventhouse, Power BI) e Synapse | quando o cliente vive no Microsoft 365/Power BI |
| Tempo real | Azure Data Explorer / Eventhouse (KQL) | telemetria e logs |
| Cache | Azure Managed Redis (sucessor do Azure Cache for Redis) | cache e sessões |
| Migração | Azure Database Migration Service | migrar SQL Server, PostgreSQL, MySQL |

Região Brazil South (São Paulo) disponível para os principais serviços.

## Escolhas por porte
- **P**: Azure SQL Database serverless (pausa quando ninguém usa) ou PostgreSQL Flexible Burstable `B1ms/B2s`; Power BI Pro com modelo importado.
- **M**: Fabric F2–F8 (pausável) com Lakehouse + Power BI; Managed Instance só se migrar o ERP.
- **G**: Fabric F16+ ou Synapse/Databricks; Cosmos DB para apps globais.

## Ofertas gratuitas (confira as condições vigentes)
- Azure SQL Database: oferta gratuita mensal por assinatura (créditos de vCore-segundo e 32 GB por banco, para alguns bancos).
- Conta nova: créditos iniciais e serviços gratuitos por 12 meses.

## Armadilhas de custo
- Capacidade do Fabric cobra por hora ligada: **pause** fora do horário (ou use reserva se ficar ligada 24 h).
- Azure SQL em vCore provisionado ligado 24/7 para uso de 8 h/dia: use serverless.
- Managed Instance tem custo mínimo alto (vCores mínimos): não use para um banco pequeno.
- Cosmos DB: RU/s provisionadas sobrando; avalie serverless ou autoscale.
- Licença do SQL Server: sem Azure Hybrid Benefit o preço inclui a licença.

## Leitura sem impacto e CDC
- **Fabric Mirroring**: replica Azure SQL Database, Managed Instance, Cosmos DB, PostgreSQL Flexible e outros para o OneLake em Delta, quase em tempo real.
- Réplicas de leitura (Azure SQL geo-replicação, PostgreSQL read replicas).
- Data Factory com CDC para fontes on-premise via Self-hosted Integration Runtime.

## Segurança
- Autenticação Entra ID, Private Endpoint, Key Vault, TDE ligado por padrão no Azure SQL, Microsoft Defender for SQL, auditoria para Log Analytics.

## Documentação oficial
- https://learn.microsoft.com/azure/azure-sql/
- https://learn.microsoft.com/azure/postgresql/flexible-server/
- https://learn.microsoft.com/azure/cosmos-db/
- https://learn.microsoft.com/fabric/
- https://learn.microsoft.com/fabric/database/mirrored-database/overview
- https://azure.microsoft.com/pricing/details/azure-sql-database/
