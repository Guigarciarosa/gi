# Microsoft Azure — guia de referência para os agentes

## Quando o Azure costuma ganhar
- Cliente **Microsoft 365 + Entra ID + Power BI** (sinal `azure` alto): SSO, governança e licenças já existem.
- ERP Dynamics 365, SQL Server on-premise (Azure Hybrid Benefit), SharePoint como fonte de planilhas.
- Diretoria que vive no Excel/Teams: Power BI integra direto.
- **Microsoft Fabric** para quem quer uma plataforma única (lake, warehouse, pipelines, BI) com cobrança por capacidade.

## Quando costuma perder
- Power BI Pro por usuário pesa com muitos leitores (acima de ~150–250 leitores, uma capacidade Fabric F64 pode compensar; abaixo disso, Pro).
- Brazil South é cara; Fabric F2/F4 ligados 24×7 sem necessidade.

## Arquitetura de referência por porte

| Porte | Ingestão | Armazenamento | Transformação | Consulta | Orquestração | BI |
|---|---|---|---|---|---|---|
| P | dlt em Container Apps Job, ou Fabric Dataflow Gen2 | ADLS Gen2 (Parquet) ou Azure SQL Basic | dbt (fabric/synapse/sqlserver) | Synapse Serverless SQL | Container Apps Jobs (cron) / Data Factory | Power BI Pro |
| M | Data Factory + CDC (SQL Server) | ADLS Gen2 + Delta / Fabric OneLake | dbt + Fabric Spark | Fabric Warehouse / SQL endpoint (F4–F16 pausável) | Data Factory / Fabric Pipelines | Power BI Pro / PPU |
| G | Event Hubs, Data Factory, Mirroring | OneLake / ADLS + Delta | Azure Databricks ou Fabric Spark | Fabric Warehouse / Databricks SQL | Data Factory / Databricks Workflows | Power BI Premium/Fabric F64+ |

## Armadilhas de custo
- Capacidade Fabric cobra por hora ligada: **pause** fora do horário ou use reserva se for 24×7.
- Data Factory cobra por atividade e por DIU-hora; pipelines muito granulares encarecem.
- Log Analytics: ingestão por GB; use tabelas Basic/Auxiliary para logs volumosos.
- Discos Premium em ambientes de dev; IPs públicos e NAT Gateway também cobram.

## Descontos
- Reservas (1/3 anos), Savings Plan for Compute, Azure Hybrid Benefit (Windows/SQL Server).
- Dev/Test pricing para ambientes não produtivos em assinaturas Visual Studio/Enterprise Dev/Test.
- Créditos: Microsoft for Startups; benefícios de parceiro (Microsoft AI Cloud Partner Program).

## Segurança essencial
- Entra ID com Acesso Condicional e MFA; PIM para acesso administrativo.
- Management groups + Azure Policy; Defender for Cloud; Key Vault com RBAC.
- Private Endpoints para Storage/SQL; Purview para classificação e LGPD.
- Power BI: RLS por unidade/carteira; workspaces separados por ambiente.

## IaC e CI/CD
- Terraform/OpenTofu (`azurerm`) ou Bicep; estado em Storage Account com lock por blob lease.
- GitHub Actions com OIDC (`azure/login` + federated credentials), sem segredo fixo.

## Faturamento
- Via CSP (revenda) é possível faturar em reais com nota fiscal brasileira — normalmente o caminho para PMEs.

## Ferramentas de preço
- Retail Prices API pública (`prices.azure.com/api/retail/prices`) — a ferramenta MCP `precos_azure_consultar` usa essa API.
- Pricing Calculator e Cost Management + Exports para o FinOps.
