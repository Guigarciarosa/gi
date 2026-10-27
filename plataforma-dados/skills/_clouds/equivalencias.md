# Equivalência de serviços entre clouds e on-premise

Referência comum a todos os agentes. Quando um agente recomenda um serviço numa
cloud, deve citar o equivalente nas outras três e no on-premise, para o FinOps
comparar maçãs com maçãs.

## Regiões no Brasil

| Provedor | Regiões | Observação |
|---|---|---|
| AWS | `sa-east-1` (São Paulo) | Região mais cara da AWS (~50–75% acima de `us-east-1`). Local Zones não substituem região. |
| Google Cloud | `southamerica-east1` (São Paulo) | Uma região no Brasil; DR fora do país usa `southamerica-west1` (Santiago). |
| Azure | `brazilsouth` (São Paulo), `brazilsoutheast` (Rio de Janeiro) | Brazil Southeast é restrita, pensada como par de DR. |
| OCI | `sa-saopaulo-1` (São Paulo), `sa-vinhedo-1` (Vinhedo/SP) | Mesmo preço em todas as regiões do mundo. Duas regiões no país facilitam DR sem sair do Brasil. |

LGPD não proíbe dados fora do Brasil (art. 33 permite transferência internacional
com salvaguardas), mas setor público, BACEN e alguns contratos exigem território
nacional. A pergunta `infra.restricoes = dados_brasil` decide.

## Dados e analytics

| Categoria | AWS | Google Cloud | Azure | OCI | On-premise (open source) |
|---|---|---|---|---|---|
| Object storage / data lake | S3 | Cloud Storage | ADLS Gen2 / Blob | Object Storage | SeaweedFS, Garage, Ceph RGW (MinIO: ver licença atual) |
| Formato de tabela | Iceberg (S3 Tables), Delta, Hudi | Iceberg (BigLake), Delta | Delta (Fabric/OneLake), Iceberg | Iceberg, Delta | Apache Iceberg ou Delta Lake |
| SQL serverless sobre o lake | Athena | BigQuery (tabelas externas/BigLake) | Synapse Serverless SQL, Fabric SQL endpoint | Autonomous DW (tabelas externas) | Trino, DuckDB |
| Data warehouse | Redshift (Serverless/provisionado) | BigQuery | Fabric Warehouse, Synapse dedicated | Autonomous Data Warehouse | PostgreSQL, ClickHouse, DuckDB |
| Spark gerenciado | EMR (Serverless), Glue | Dataproc (Serverless) | Fabric Spark, Azure Databricks, Synapse Spark | Data Flow | Apache Spark em Docker/K8s |
| Databricks | Sim | Sim | Azure Databricks (1ª parte) | — (via parceiros) | — |
| Snowflake | Sim | Sim | Sim | — | — |
| Streaming | Kinesis, MSK (Kafka) | Pub/Sub, Managed Kafka | Event Hubs (API Kafka) | Streaming (API Kafka) | Redpanda, Apache Kafka |
| Processamento de stream | Managed Flink, Lambda | Dataflow (Beam) | Stream Analytics, Fabric Real-Time | GoldenGate Stream Analytics | Flink, Bytewax, RisingWave |
| CDC de bancos | DMS | Datastream | Data Factory / Fabric Mirroring | GoldenGate | Debezium |
| ETL/ELT gerenciado | Glue, AppFlow | Data Fusion, Dataform | Data Factory, Fabric Pipelines | Data Integration | dlt, Airbyte, Meltano |
| Transformação SQL | dbt (qualquer) | Dataform, dbt | dbt | dbt | dbt-core, SQLMesh |
| Orquestração | MWAA (Airflow), Step Functions | Cloud Composer (Airflow), Workflows | Data Factory, Fabric | Data Integration, OCI Functions | Dagster, Airflow, Kestra, Prefect |
| Catálogo / governança | Glue Catalog, Lake Formation, DataZone | Dataplex, Data Catalog | Purview | Data Catalog | OpenMetadata, DataHub |
| Qualidade de dados | Glue Data Quality | Dataplex Data Quality | Purview Data Quality | — | dbt tests, Soda Core, Great Expectations |
| BI | QuickSight | Looker, Looker Studio (grátis) | Power BI | Oracle Analytics Cloud | Metabase, Apache Superset, Lightdash, Evidence |

## IA

| Categoria | AWS | Google Cloud | Azure | OCI | On-premise |
|---|---|---|---|---|---|
| Plataforma de ML | SageMaker AI | Vertex AI | Azure Machine Learning | OCI Data Science | MLflow + Jupyter |
| LLM gerenciado | Bedrock (inclui Claude) | Vertex AI Model Garden (inclui Claude) | Azure AI Foundry (inclui Claude) | OCI Generative AI | Ollama, vLLM, llama.cpp |
| ML dentro do warehouse | Redshift ML | BigQuery ML | Fabric ML | Oracle Machine Learning (ADW) | PostgresML, DuckDB + Python |
| Busca vetorial | OpenSearch, Aurora pgvector, S3 Vectors | Vertex Vector Search, AlloyDB, BigQuery vector | AI Search, Cosmos DB, PostgreSQL pgvector | Oracle Database 23ai (AI Vector Search) | Qdrant, pgvector |
| OCR / documentos | Textract | Document AI | Document Intelligence | Document Understanding | Tesseract, Docling, PaddleOCR |
| GPU sob demanda | EC2 G6 (L4), G5 (A10G) | G2 (L4), A2/A3 | NC T4/A10/H100 | VM.GPU.A10, A100/H100 | GPU própria (RTX) |

## Infraestrutura, segurança e operação

| Categoria | AWS | Google Cloud | Azure | OCI | On-premise |
|---|---|---|---|---|---|
| VM | EC2 (Graviton t4g/m7g) | Compute Engine (e2, t2a) | Virtual Machines (B, D) | Compute (A1/A2 Ampere, E5) | Proxmox, ZimaOS (Docker) |
| Containers serverless | Fargate, App Runner | Cloud Run | Container Apps | Container Instances | Docker Compose |
| Kubernetes | EKS | GKE (Autopilot) | AKS | OKE (control plane grátis) | k3s, Talos |
| Funções | Lambda | Cloud Run functions | Functions | OCI Functions | OpenFaaS, n8n |
| PostgreSQL gerenciado | RDS, Aurora | Cloud SQL, AlloyDB | Database for PostgreSQL Flexible | Database with PostgreSQL | PostgreSQL |
| IaC nativa | CloudFormation, CDK | Infrastructure Manager | Bicep / ARM | Resource Manager (Terraform) | OpenTofu + Ansible |
| IAM | IAM, IAM Identity Center | Cloud IAM, Workload Identity | Entra ID, RBAC | IAM (Identity Domains) | Keycloak, Authentik |
| Segredos | Secrets Manager, Parameter Store | Secret Manager | Key Vault | Vault | OpenBao/Vault, Infisical |
| Chaves (KMS) | KMS | Cloud KMS | Key Vault (HSM) | Vault (HSM) | OpenBao Transit |
| Postura de segurança | Security Hub, GuardDuty | Security Command Center | Defender for Cloud | Cloud Guard | Wazuh |
| WAF / borda | WAF, CloudFront, Shield | Cloud Armor, Cloud CDN | Front Door, WAF | WAF, Edge | Cloudflare (grátis), Caddy |
| Observabilidade | CloudWatch, X-Ray | Cloud Monitoring/Logging | Azure Monitor, Log Analytics | Monitoring, Logging | Prometheus, Grafana, Loki, Uptime Kuma |
| Backup | AWS Backup | Backup and DR | Azure Backup | Block/Object backup policies | restic, Kopia + Backblaze B2 / R2 |
| Custos | Cost Explorer, CUR 2.0, Budgets | Billing export para BigQuery, Budgets | Cost Management, Exports | Cost Analysis, Usage Reports, Budgets | Planilha de TCO + medidor de energia |
| Descontos por compromisso | Savings Plans, RIs | CUDs (recurso e flexíveis), SUDs automáticos | Reservas, Savings Plan for Compute | Universal Credits (Annual Flex) | Compra de hardware à vista |

## Free tiers que importam para MVP

- **OCI Always Free**: 4 OCPU + 24 GB RAM Ampere A1, 200 GB de block storage, 20 GB de object storage, 2 Autonomous Databases de 20 GB, 10 TB/mês de saída. Dá para rodar um MVP completo sem custo.
- **BigQuery**: 1 TiB de consulta e 10 GB de armazenamento por mês, para sempre.
- **Looker Studio**: grátis, sem limite de usuários de leitura.
- **AWS**: plano gratuito com créditos para contas novas; Lambda e DynamoDB têm franquia mensal permanente.
- **Azure**: créditos iniciais e 12 meses de serviços populares; Power BI Pro já vem no Microsoft 365 E5.

Os valores mudam: confirme na página oficial antes de prometer ao cliente.
