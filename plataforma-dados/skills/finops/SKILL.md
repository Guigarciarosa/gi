---
name: finops
description: Compara e otimiza custos de plataformas de dados em AWS, Google Cloud, Azure, Oracle Cloud e on-premise — TCO com operação, câmbio e IOF, free tiers, descontos por compromisso, armadilhas (NAT, egress, logs, licenças de BI), governança com tags, orçamentos, alertas e relatórios FOCUS. Use ao estimar quanto uma arquitetura custa, escolher a opção mais barata ou reduzir uma fatura de cloud.
---

# Skill — FinOps

## Método (FinOps Framework: Informar → Otimizar → Operar)
1. **Informar**: custo por componente e por cliente, com tags; mesma arquitetura funcional em todas as opções.
2. **Otimizar**: primeiro **desligar e reduzir** (rightsizing, agendamento, retenção), depois **descontos** (compromissos), por último **rearquitetar**.
3. **Operar**: orçamento com alertas, revisão mensal, custo unitário acompanhado como KPI.

## TCO — o que sempre entra
- Fatura da cloud (computação, armazenamento, consulta, rede, licenças nativas).
- Licenças de terceiros (BI por usuário, Databricks/Snowflake, conectores pagos).
- **Operação** (horas/mês × custo/hora) — cloud gerenciada exige menos horas que on-premise.
- On-premise: hardware amortizado (36 meses), energia (W × 730 h × tarifa), backup externo, link/IP fixo, reposição de discos.
- **Câmbio e IOF**: fatura em US$ com cartão internacional paga IOF; faturamento em reais via revenda/entidade local pode ter impostos. Use o câmbio do `.env` (`CAMBIO_USD_BRL`) e sensibilidade de ±10%.
- Custo de IA: tokens/mês (API) ou GPU (local/cloud).

## Ordem de grandeza (calculadora, região Brasil)
| Porte | Opção mais barata típica | Faixa de infraestrutura/mês |
|---|---|---|
| P | OCI (Always Free) ou ZimaOS/on-premise; BigQuery se o cliente já usa Google | R$ 0–1.500 (BI por usuário costuma ser o maior item) |
| M | OCI ou on-premise; AWS/GCP quando há afinidade e serviços gerenciados valem a diferença | R$ 2.000–12.000 |
| G | Depende de streaming e concorrência; compromissos de 1 ano mudam o ranking | R$ 20.000+ |
Rode sempre a calculadora: estes intervalos são só para checagem de sanidade.

## Armadilhas por cloud
- **AWS**: NAT Gateway (hora + GB), saída em `sa-east-1`, Glue para jobs pequenos, MWAA ligado 24×7, CloudWatch Logs sem retenção, snapshots esquecidos.
- **GCP**: BigQuery on-demand sem partição/cota, Cloud Composer para poucos DAGs, logs não filtrados, tier Premium de rede.
- **Azure**: Power BI Pro por leitor em escala, capacidade Fabric ligada sem uso, Log Analytics, Data Factory com muitas atividades pequenas.
- **OCI**: VPU de block volume alta sem necessidade, Autonomous DW sem parada agendada, misturar recursos Always Free e pagos sem tag.
- **On-premise**: esquecer energia, nobreak, reposição de discos e o custo da indisponibilidade.

## Otimizações com maior retorno (aplicar nesta ordem)
1. Desligar dev/homolog fora do horário (economia de ~65% nesses ambientes).
2. Parquet + partição + clusterização (consulta por TB varrido cai 10–100×).
3. Camada gold agregada e cache/import no BI (menos consultas no warehouse).
4. Lifecycle da bronze para camada fria após 90 dias.
5. ARM (Graviton/Ampere/T2A) para VMs e contêineres.
6. Micro-lotes no lugar de streaming quando a decisão é em minutos/horas.
7. Licenças de BI: Looker Studio/Metabase para leitores ocasionais; Power BI Pro só para quem cria/consome com frequência.
8. Compromissos (1 ano) só depois de 2–3 meses de uso estável.

## Descontos por compromisso
| | AWS | GCP | Azure | OCI |
|---|---|---|---|---|
| Computação flexível | Compute Savings Plans | CUD flexível | Savings Plan for Compute | Annual Flex (Universal Credits) |
| Por recurso | Reserved Instances (EC2, RDS, Redshift) | CUD por recurso; Sustained Use automático | Reservas (VM, SQL, Fabric) | — |
| Licenças | — | — | Azure Hybrid Benefit | BYOL Oracle |
| Interruptível | Spot | Spot VMs | Spot VMs | Preemptible |

## Governança desde o primeiro dia
- **Tags/labels**: `cliente`, `ambiente`, `projeto`, `centro_custo`, `gerenciado_por`.
- **Orçamentos e alertas** em 50/80/100% do valor aprovado: AWS Budgets, GCP Budgets (com Pub/Sub para ação), Azure Cost Management budgets, OCI Budgets.
- **Exportação de custos** no padrão **FOCUS** (FinOps Open Cost and Usage Specification), disponível em AWS Data Exports, Azure Cost Management, GCP (export de billing para BigQuery com visão FOCUS) e OCI Cost Reports — permite um painel único multi-cloud.
- **Custo unitário**: R$ por cliente atendido, por painel ativo, por GB processado, por pergunta ao assistente de IA.
- **Showback multi-cliente** no ZimaOS: rateio por uso (CPU/armazenamento por cliente) para precificar a mensalidade.

## Validação de preços (antes de enviar proposta)
- Azure: `precos_azure_consultar(servico, regiao='brazilsouth')` — Retail Prices API.
- OCI: `precos_oci_consultar(termo)` — Price List API.
- AWS: Price List API / calculator.aws. GCP: Billing Catalog API / calculadora.
- Atualize `servidor/src/plataforma/dados/precos.yaml` quando um preço de referência mudar.

## Antipadrões
- Comparar a fatura de uma cloud com só a infraestrutura da outra (sem licenças ou operação).
- Comprometer 3 anos no primeiro mês.
- Escolher on-premise "porque é de graça" ignorando energia, backup e horas de operação.
- Otimizar centavos de armazenamento e ignorar licença de BI por usuário.
