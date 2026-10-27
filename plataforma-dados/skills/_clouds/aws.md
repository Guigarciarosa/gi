# AWS — guia de referência para os agentes

## Quando a AWS costuma ganhar
- O cliente **já está na AWS** (sinal `aws` alto): reaproveita contas, IAM, rede e créditos.
- Ecossistema de dados maduro e muita mão de obra no mercado brasileiro.
- Integrações prontas com SaaS (AppFlow), Bedrock com Claude para IA generativa.
- Exigência de região no Brasil com serviço gerenciado amplo (`sa-east-1`).

## Quando costuma perder
- Custo da região São Paulo (~1,5–1,8× os EUA), NAT Gateway e saída de internet.
- Times pequenos sem experiência: a quantidade de serviços e o IAM assustam.

## Arquitetura de referência por porte

| Porte | Ingestão | Armazenamento | Transformação | Consulta | Orquestração | BI |
|---|---|---|---|---|---|---|
| P | dlt/Python em 1 EC2 t4g.large (ou Lambda) | S3 (Parquet) | dbt-duckdb ou dbt-athena | Athena | Dagster/cron na mesma EC2 | Metabase na EC2 ou QuickSight |
| M | dlt + DMS (CDC) | S3 + Iceberg (S3 Tables) | dbt-athena / Glue | Athena; Redshift Serverless para concorrência alta | Dagster em ECS Fargate ou MWAA pequeno | QuickSight / Power BI |
| G | DMS, MSK/Kinesis, AppFlow | S3 + Iceberg + Lake Formation | EMR Serverless / Glue Spark + dbt | Redshift Serverless + Athena | MWAA ou Dagster em EKS | QuickSight Enterprise / Power BI |

## Armadilhas de custo (o FinOps sempre confere)
- **NAT Gateway**: cobra por hora **e** por GB processado. Use VPC Endpoints (Gateway) para S3/DynamoDB — são gratuitos.
- **Saída de internet** em `sa-east-1` é cara; BI externo puxando dados brutos vira conta alta.
- **Glue**: mínimo de 1 minuto por job e DPUs caros para jobs pequenos; para porte P prefira Python em EC2/Lambda.
- **MWAA**: ambiente mínimo fica ligado 24×7; para porte P/M, Dagster/Airflow em contêiner sai bem mais barato.
- **CloudWatch Logs**: ingestão cobrada por GB; defina retenção (padrão é "nunca expira").
- **Athena**: cobra por TB varrido; Parquet + partição + compressão reduzem o custo em ordens de grandeza.

## Descontos
- Compute Savings Plans (1 ou 3 anos), Reserved Instances (RDS, Redshift, OpenSearch), Spot para lotes.
- Graviton (ARM) costuma ser ~20% mais barato que x86 equivalente.
- Créditos: AWS Activate (startups), programas de migração (MAP) via parceiros.

## Segurança essencial
- AWS Organizations com contas separadas (prod, dev, log/auditoria); IAM Identity Center com MFA.
- CloudTrail em todas as regiões, GuardDuty, Security Hub, S3 Block Public Access ligado por padrão.
- KMS para chaves; Secrets Manager para credenciais de fontes; buckets com versionamento + Object Lock para backups.

## IaC e CI/CD
- Terraform/OpenTofu (provider `hashicorp/aws`) ou CDK. Estado remoto em S3 com lock nativo (`use_lockfile`).
- GitHub Actions com OIDC (`aws-actions/configure-aws-credentials`) — sem chaves de acesso fixas.

## Faturamento
- Contas com endereço no Brasil podem ser faturadas pela entidade local em reais; confirme no console de Billing e inclua impostos na proposta.
- Cartão internacional em dólar paga IOF.

## Ferramentas de preço
- Price List API (`pricing.us-east-1.amazonaws.com`) e calculator.aws.
