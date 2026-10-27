# Google Cloud — guia de referência para os agentes

## Quando o GCP costuma ganhar
- **BigQuery** resolve o porte P e M sem servidor nenhum: 1 TiB de consulta/mês grátis e escala sem tuning.
- Cliente com **GA4/Google Ads** (export nativo e gratuito para o BigQuery) ou **Google Workspace**.
- **Looker Studio grátis** para dezenas de usuários de leitura: tira o custo de licença de BI.
- Analytics de marketing, e-commerce e produto digital.

## Quando costuma perder
- Muitas consultas mal escritas no on-demand (cobra por TB varrido) sem controle de cota.
- Cliente 100% Microsoft que exige Power BI com Entra ID em tudo (funciona, mas Azure tende a ser mais natural).

## Arquitetura de referência por porte

| Porte | Ingestão | Armazenamento | Transformação | Consulta | Orquestração | BI |
|---|---|---|---|---|---|---|
| P | dlt em Cloud Run Jobs | BigQuery (direto) + GCS para arquivos | dbt-bigquery ou Dataform | BigQuery on-demand | Cloud Scheduler + Cloud Run Jobs | Looker Studio |
| M | dlt + Datastream (CDC) | GCS + BigQuery (BigLake/Iceberg) | Dataform/dbt | BigQuery Editions com autoscaling | Dagster em Cloud Run / Composer pequeno | Looker Studio Pro / Power BI |
| G | Datastream, Pub/Sub, Dataflow | GCS + BigLake Iceberg | Dataproc Serverless + dbt | BigQuery Editions (Enterprise) | Cloud Composer | Looker |

## Armadilhas de custo
- `SELECT *` em tabela grande no on-demand: exija partição (`require_partition_filter`) e clusterização.
- Defina **cota diária de bytes por usuário/projeto** (custom quotas) antes de liberar o BI.
- Cloud Composer tem custo base relevante; para P/M, Cloud Run Jobs ou Dagster resolvem.
- Saída de internet com tier Premium é mais cara que o Standard.
- Logs: exclua logs de baixo valor no Log Router.

## Descontos
- Sustained Use Discounts automáticos em várias famílias de VM; CUDs por recurso ou flexíveis.
- BigQuery Editions com compromisso de slots para uso previsível.
- Créditos: US$ 300 para contas novas; Google for Startups Cloud Program.

## Segurança essencial
- Organização com pastas por ambiente; IAM com grupos do Workspace/Cloud Identity e MFA.
- VPC Service Controls para isolar o BigQuery; CMEK quando o cliente exigir chave própria.
- Security Command Center; Audit Logs de Data Access ligados para BigQuery.
- Column-level security e row-level security nativos no BigQuery (policy tags).

## IaC e CI/CD
- Terraform/OpenTofu (provider `hashicorp/google`); estado em GCS.
- GitHub Actions com Workload Identity Federation (`google-github-actions/auth`), sem chave JSON.

## Faturamento
- Contas de faturamento no Brasil podem ser em reais conforme o contrato/revenda; confirme antes de propor.

## Ferramentas de preço
- Cloud Billing Catalog API e cloud.google.com/products/calculator.
- Billing export para BigQuery: o FinOps monta o painel de custos com o próprio BigQuery + Looker Studio.
