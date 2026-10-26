# 05 — Clouds e custos

## Resumo: quando cada opção costuma ganhar
| Opção | Ganha quando | Cuidado com |
|---|---|---|
| **OCI** | Menor custo em quase todos os portes; Always Free cobre um MVP; 10 TB/mês de saída grátis; preço igual em São Paulo e nos EUA; cliente Oracle | Ecossistema e mão de obra menores; BI nativo caro (use Metabase/Superset) |
| **GCP** | BigQuery resolve P/M sem servidor; 1 TiB de consulta grátis/mês; Looker Studio grátis; cliente Google Workspace/GA4 | Consultas sem partição no on-demand; Composer caro para poucos DAGs |
| **Azure** | Cliente Microsoft 365 + Power BI + Entra ID; Dynamics; SQL Server com Hybrid Benefit; Fabric como plataforma única | Power BI Pro por leitor em escala; capacidade Fabric ligada sem uso |
| **AWS** | Cliente já na AWS (créditos, contratos, time); ecossistema mais amplo; Bedrock | Região São Paulo cara; NAT Gateway; saída de internet; Glue/MWAA para cargas pequenas |
| **On-premise / ZimaOS** | Restrição de SaaS, LLM 100% local, hardware ocioso, câmbio; clientes P hospedados no servidor da consultoria | RTO baixo, crescimento rápido, falta de quem opere; energia e backup entram no custo |

Guias completos: `skills/_clouds/aws.md`, `gcp.md`, `azure.md`, `oci.md`, `on-premise.md`, e a tabela de equivalências `skills/_clouds/equivalencias.md`.

## Como a calculadora funciona
`custos_estimar` (código em `servidor/src/plataforma/custos.py`, preços em `servidor/src/plataforma/dados/precos.yaml`):

1. **Perfil de carga** a partir das respostas: volume (com crescimento médio em 12 meses), usuários de BI, fontes, atualizações por dia, streaming, ambientes, BI escolhido, IA.
2. **Porte** P/M/G com as mesmas regras do Arquiteto.
3. **Componentes por provedor** (região Brasil): armazenamento em 3 camadas, backup frio, VM do orquestrador/serviços (com Always Free da OCI), consulta (TB varrido na gold + transformações incrementais), Spark (porte G ou > 1 TB), streaming, saída de internet, BI por usuário, IA (API de LLM ou GPU) e custos fixos.
4. **On-premise**: hardware do perfil amortizado em 36 meses, energia, backup externo, link/IP fixo, GPU local se o LLM precisar ser local.
5. **TCO** = infraestrutura + horas de operação (cloud gerenciada exige menos horas).
6. **Câmbio e IOF** (cartão internacional) quando a fatura é em dólar.
7. **Ranking**: 60% custo + 40% afinidade dos sinais (80/20 se a prioridade for custo; 40/60 se for autonomia do time), com restrições eliminatórias (`sem_saas`, `air_gapped`).

O FinOps sempre confere a recomendação contra a opção mais barata viável: se a
diferença passar de 25% sem requisito que obrigue, pede revisão ao Arquiteto.

## Três cenários de exemplo (saída real da calculadora)

### A — Associação de proteção veicular (8 mil associados)
SQL Server próprio, planilhas e tabela FIPE; atualização diária; 15 usuários; prioridade custo.
Porte **P** · recomendação: **OCI** · mais barato: **OCI**

| # | Opção | Infra/mês | Operação/mês | TCO/mês | TCO 12 meses | Nota |
|---|-------|----------:|-------------:|--------:|-------------:|-----:|
| 1 | Oracle Cloud (OCI) | R$ 13 | R$ 240 | R$ 253 | R$ 3.040 | 80 |
| 2 | On-premise | R$ 251 | R$ 480 | R$ 731 | R$ 8.771 | 48 |
| 3 | Microsoft Azure | R$ 1.965 | R$ 240 | R$ 2.205 | R$ 26.454 | 29 |
| 4 | Google Cloud | R$ 562 | R$ 240 | R$ 802 | R$ 9.624 | 25 |
| 5 | AWS | R$ 1.017 | R$ 240 | R$ 1.257 | R$ 15.081 | 16 |

Leitura: o Always Free da OCI absorve VM e disco; o custo do Azure é quase todo
licença de Power BI (BI nativo quando o cliente deixa a escolha conosco). Com
Metabase em qualquer opção, as clouds se aproximam — o FinOps simula esse cenário.

### B — Cooperativa agroindustrial (20 unidades)
Protheus, planilhas, dados públicos e telemetria; 4 atualizações/dia; 60 usuários;
Microsoft 365 + Power BI + Azure já em uso; previsão de demanda e assistente RAG.
Porte **M** · recomendação: **Azure** · mais barato: **OCI**

| # | Opção | Infra/mês | Operação/mês | TCO/mês | TCO 12 meses | Nota |
|---|-------|----------:|-------------:|--------:|-------------:|-----:|
| 1 | Microsoft Azure | R$ 7.236 | R$ 720 | R$ 7.956 | R$ 95.466 | 92 |
| 2 | Oracle Cloud (OCI) | R$ 6.141 | R$ 720 | R$ 6.861 | R$ 82.336 | 60 |
| 3 | On-premise | R$ 5.756 | R$ 1.200 | R$ 6.956 | R$ 83.475 | 59 |
| 4 | Google Cloud | R$ 6.937 | R$ 720 | R$ 7.657 | R$ 91.883 | 54 |
| 5 | AWS | R$ 7.040 | R$ 720 | R$ 7.760 | R$ 93.116 | 53 |

Leitura: Azure custa ~16% a mais que a OCI, mas o cliente já tem identidade,
licenças e time Microsoft — diferença abaixo de 25%, a afinidade justifica.

### C — Transportadora com telemetria (400 veículos)
ERP, rastreadores e bancos próprios; micro-lotes de minutos com até 5 mil eventos/s;
60 usuários; já usa AWS.
Porte **G** · recomendação: **AWS** · mais barato: **OCI**

| # | Opção | Infra/mês | Operação/mês | TCO/mês | TCO 12 meses | Nota |
|---|-------|----------:|-------------:|--------:|-------------:|-----:|
| 1 | AWS | R$ 18.248 | R$ 2.400 | R$ 20.648 | R$ 247.781 | 66 |
| 2 | Oracle Cloud (OCI) | R$ 6.662 | R$ 2.400 | R$ 9.062 | R$ 108.750 | 60 |
| 3 | On-premise | R$ 5.873 | R$ 4.800 | R$ 10.673 | R$ 128.073 | 51 |
| 4 | Google Cloud | R$ 15.126 | R$ 2.400 | R$ 17.526 | R$ 210.317 | 31 |
| 5 | Microsoft Azure | R$ 22.069 | R$ 2.400 | R$ 24.469 | R$ 293.624 | 22 |

Leitura: a afinidade coloca a AWS em 1º, mas o TCO é 2,3× o da OCI (streaming
Kinesis, região São Paulo e saída). Pela regra dos 25%, o FinOps pede revisão. Caminhos:
(1) AWS com micro-lotes no lugar de streaming e Savings Plans; (2) OCI com Streaming
(API Kafka) e migração gradual; (3) híbrido: ingestão de telemetria na OCI e BI onde
o cliente já está.

> Os valores dependem dos preços de referência em `precos.yaml` (final de 2025) e do câmbio
> configurado. São para comparar opções, não para faturar: valide antes de propor.

## Validar preços
| Provedor | Como |
|---|---|
| Azure | `precos_azure_consultar("Virtual Machines", "brazilsouth", "B2ms")` — Retail Prices API pública |
| OCI | `precos_oci_consultar("Ampere")` — Price List API pública |
| AWS | Price List API ou calculator.aws |
| GCP | Cloud Billing Catalog API ou calculadora oficial |
Atualize `precos.yaml` quando um preço mudar; o servidor relê o arquivo a cada chamada.

## Otimizações com maior retorno
1. Desligar dev/homolog fora do horário.
2. Parquet + partição + clusterização; gold agregada; cache no BI.
3. Lifecycle da bronze para camada fria após 90 dias.
4. ARM (Graviton, Ampere, T2A).
5. Micro-lotes em vez de streaming quando a decisão é em minutos ou horas.
6. Licenças de BI: leitor ocasional em Looker Studio/Metabase; Pro só para quem usa todo dia.
7. Compromissos de 1 ano só após 2–3 meses de uso estável.

## Faturamento em reais
Para clientes que não podem pagar em dólar (`pagamento_brl`): revenda CSP (Azure),
entidade local/contrato em reais (AWS, Google, Oracle — confirmar a modalidade
vigente), ou OCI/ZimaOS com custo previsível. A calculadora desliga o IOF nesse caso;
impostos locais variam e entram na proposta.
