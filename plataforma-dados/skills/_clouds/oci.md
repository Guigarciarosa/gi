# Oracle Cloud Infrastructure (OCI) — guia de referência para os agentes

## Quando a OCI costuma ganhar
- **Menor custo** em computação e rede: Ampere A1 barato, **10 TB/mês de saída grátis**, preço igual em todas as regiões (São Paulo custa o mesmo que os EUA).
- **Always Free** sustenta um MVP inteiro (4 OCPU + 24 GB RAM, 200 GB de disco, 2 Autonomous DB de 20 GB).
- Cliente com **Oracle Database / EBS / JD Edwards / NetSuite** (BYOL, GoldenGate, conectores nativos).
- Duas regiões no Brasil (São Paulo e Vinhedo) para DR sem sair do país.
- Portais e APIs de dados com muito tráfego de saída.

## Quando costuma perder
- Ecossistema de ferramentas de terceiros e mão de obra menores que AWS/Azure.
- BI nativo (Oracle Analytics Cloud) é cobrado por OCPU; para PMEs, Superset/Metabase em A1 resolvem.
- Capacidade Ampere A1 no Always Free pode faltar em algumas regiões (tente outra AD ou conta paga com preço baixo).

## Arquitetura de referência por porte

| Porte | Ingestão | Armazenamento | Transformação | Consulta | Orquestração | BI |
|---|---|---|---|---|---|---|
| P | dlt em VM A1 (Always Free) | Object Storage + PostgreSQL/DuckDB na VM | dbt-duckdb / dbt-postgres | DuckDB/PostgreSQL; ou ADW Always Free (20 GB) | Dagster na mesma VM | Metabase/Superset na VM |
| M | dlt + GoldenGate (se Oracle) | Object Storage (Iceberg) + Autonomous DW | dbt-oracle / Data Flow | Autonomous DW com auto-scaling e parada agendada | Dagster em OKE/VM ou Data Integration | Superset / Power BI / OAC |
| G | Streaming (Kafka), GoldenGate | Object Storage + Iceberg | Data Flow (Spark) + dbt | Autonomous DW / HeatWave | Dagster/Airflow em OKE | OAC / Power BI |

## Armadilhas de custo
- Block Volume tem custo de performance (VPU) além do GB; use "Balanced" e ajuste.
- Autonomous DW cobra por ECPU-hora ligado: agende parada fora do horário comercial.
- Recursos "Always Free" e pagos convivem na mesma conta: marque com tags para não confundir.

## Descontos
- Universal Credits / Annual Flex (compromisso anual com desconto); BYOL para licenças Oracle.
- Oracle Support Rewards para clientes com suporte Oracle.
- Créditos: Oracle for Startups; trial com US$ 300.

## Segurança essencial
- Compartimentos por ambiente/cliente; Identity Domains com MFA; políticas IAM em linguagem declarativa.
- Cloud Guard e Security Zones; Vault para chaves e segredos; Bastion gerenciado (grátis) no lugar de SSH aberto.
- Data Safe para auditoria e mascaramento nos Autonomous Databases.

## IaC e CI/CD
- Terraform/OpenTofu (provider `oracle/oci`) ou Resource Manager (Terraform gerenciado, grátis).
- GitHub Actions com API key em segredo do repositório ou OCI DevOps.

## Faturamento
- Oracle do Brasil fatura em reais com nota fiscal para contratos locais; confirme a modalidade.

## Ferramentas de preço
- Price List API pública (`apexapps.oracle.com/pls/apex/cetools/api/v1/products/`) — a ferramenta MCP `precos_oci_consultar` usa essa API.
- Cost Estimator no site da Oracle; Cost Analysis e Budgets no console.
