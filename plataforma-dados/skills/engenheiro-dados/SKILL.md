---
name: engenheiro-dados
description: Planeja e implementa ingestão, transformação e qualidade de dados — conectores para ERPs brasileiros (TOTVS Protheus, RM, Datasul, Sankhya, Senior, SAP, Omie, Bling), CDC, NF-e XML, planilhas, APIs, IoT/GPS — com dlt, dbt, Dagster/Airflow e os serviços equivalentes de AWS, GCP, Azure e OCI. Use ao montar pipelines, estimar esforço de engenharia ou desenhar integrações e automações.
---

# Skill — Engenheiro de Dados

## Stack padrão (portável entre clouds e on-premise)
- **Ingestão**: `dlt` (Python) para bancos e APIs com estado incremental; Debezium para CDC; scripts dedicados para arquivos.
- **Transformação**: `dbt-core` com o adaptador do motor escolhido (postgres, duckdb, bigquery, athena, fabric/synapse, oracle, redshift, spark).
- **Orquestração**: Dagster (assets + schedules + sensors); Airflow quando o cliente já usa ou exige.
- **Qualidade**: testes dbt + `dbt source freshness`; Soda Core ou Great Expectations para contratos de fontes; Elementary para observabilidade dos modelos.
- **Automação operacional**: n8n (webhooks, WhatsApp, e-mail, planilhas) acionado pelo orquestrador.

## Conectores por sistema

### TOTVS Protheus (SQL Server / Oracle / PostgreSQL)
- Tabelas: `SA1` clientes, `SA2` fornecedores, `SB1` produtos, `SB2` saldos de estoque, `SC5`/`SC6` pedidos de venda, `SC7` pedidos de compra, `SF2`/`SD2` notas de saída, `SF1`/`SD1` notas de entrada, `SE1` contas a receber, `SE2` contas a pagar, `SE5` movimentação bancária, `CT2` lançamentos contábeis, `SRA` funcionários.
- Nome físico = tabela + código da empresa + `0` (ex.: `SA1010`). Campos de controle: `D_E_L_E_T_` (`'*'` = excluído), `R_E_C_N_O_`, filial em `<prefixo>_FILIAL`. Datas como texto `YYYYMMDD`.
- Incremental: use `S_T_A_M_P_`/`I_N_S_D_T_` se habilitados na versão; senão janela por data de emissão/baixa + reconciliação semanal. `R_E_C_N_O_` não detecta alteração.
- Leia de **réplica** ou fora do horário; usuário somente leitura; nunca grave no banco do Protheus (use as APIs REST/TLPP do próprio Protheus para escrita).

### TOTVS RM (SQL Server / Oracle)
- Tabelas comuns: `FCFO` (clientes/fornecedores), `TMOV`/`TITMMOV` (movimentos e itens), `FLAN` (lançamentos financeiros), `TPRD` (produtos), `PFUNC` (folha), `SALUNO`/`SMATRICPL` (educacional).
- Prefira as consultas SQL cadastradas (`GCONSSQL`) expostas via API do RM quando não houver acesso ao banco.

### TOTVS Datasul (Progress OpenEdge)
- Acesso via ODBC (DataDirect) ou réplica SQL; volume de tabelas alto — mapeie com o key user antes.

### Sankhya
- Tabelas: `TGFCAB` (cabeçalho de notas/pedidos), `TGFITE` (itens), `TGFPAR` (parceiros), `TGFPRO` (produtos), `TGFFIN` (financeiro), `TGFEST` (estoque). API REST (Sankhya-W) para integrações.

### SAP (ECC, S/4HANA, Business One)
- Não leia tabelas diretamente sem verificar licenciamento. Use OData/CDS views, ODP (via SLT/BW extractors) ou conectores certificados. Business One: Service Layer (REST) ou banco HANA/SQL com usuário de leitura.

### ERPs SaaS (Omie, Bling, Tiny/Olist, Conta Azul)
- APIs REST com limite de requisições: paginar, respeitar `429`, guardar cursor de data de alteração no estado do `dlt`.

### CRMs
- Salesforce (Bulk API 2.0), HubSpot (CRM API v3, OAuth app privado), RD Station (API v2), Pipedrive (API v1/v2). Use os conectores verificados do `dlt` quando existirem.

### Planilhas
- SharePoint/OneDrive via Microsoft Graph; Google Sheets API. Defina **contrato** (colunas, tipos, aba) e valide antes de carregar; planilha que quebra o contrato gera alerta, não carga silenciosa.

### NF-e / CT-e / NFS-e (XML)
- Namespace `http://www.portalfiscal.inf.br/nfe`. Campos-chave: `infNFe/@Id` (chave de 44 dígitos), `ide/dhEmi`, `emit/CNPJ`, `dest/CNPJ|CPF`, `det/prod` (`cProd`, `xProd`, `NCM`, `CFOP`, `qCom`, `vUnCom`, `vProd`), `total/ICMSTot/vNF`.
- Deduplicar pela chave; tratar eventos (cancelamento, carta de correção) como tabela separada.

### IoT / rastreadores / telemetria
- MQTT (Mosquitto/EMQX) ou API do provedor de rastreamento (Sascar, Omnilink, Onixsat, Autotrac). Guarde o bruto particionado por data e agregue na silver (por veículo e hora) antes do BI.
- Para latência de minutos, micro-lotes de 5–15 min são suficientes; streaming verdadeiro só com motivo registrado.

### Dados públicos úteis
- Receita Federal (CNPJ), IBGE (municípios, renda), BCB (SGS: Selic, IPCA, câmbio), FIPE, CEPEA (agro), INMET (clima).

## Padrões de pipeline
- **Bronze** grava como veio (JSON/Parquet), com `_carregado_em` e `_origem`; nunca sobrescreve.
- **Silver** tipa, deduplica, aplica soft-delete e chaves de negócio.
- **Gold** = marts dimensionais e tabelas de métricas.
- Arquivos Parquet de 128 MB a 1 GB; particione por data de negócio na gold e por data de carga na bronze.
- Idempotência: `MERGE`/`INSERT OVERWRITE` por partição; reprocessamento por intervalo.
- Backfill em janelas (mês a mês) fora do horário; medir carga no ERP.

## Convenções dbt
`stg_<fonte>__<objeto>`, `int_<assunto>__<verbo>`, `fct_<processo>`, `dim_<entidade>`. Testes mínimos: `unique` + `not_null` na PK, `relationships` nas FKs, `accepted_values` em status, `dbt_utils.recency` nas fontes críticas.

## Estimativa de esforço (referência, horas)
| Item | Simples | Médio | Complexo |
|---|---|---|---|
| Fonte via API SaaS com conector pronto | 4 | 8 | 16 |
| Fonte via banco do ERP (por domínio: vendas, financeiro, estoque) | 12 | 24 | 48 |
| CDC configurado (por banco) | 16 | 32 | 60 |
| Modelo dbt de mart (por fato) | 6 | 12 | 24 |
| Planilha com contrato | 3 | 6 | 12 |
| Automação n8n (por fluxo) | 3 | 8 | 16 |
| Ambiente base (orquestrador, CI, cofre, observabilidade) | 16 | 32 | 64 |

## Por cloud
| Necessidade | AWS | GCP | Azure | OCI |
|---|---|---|---|---|
| Executar dlt/dbt | ECS Fargate task / Lambda (curto) | Cloud Run Jobs | Container Apps Jobs | Container Instances / VM A1 |
| CDC gerenciado | DMS | Datastream | Data Factory CDC / Fabric Mirroring | GoldenGate |
| ETL visual | Glue Studio | Data Fusion | Data Factory | Data Integration |
| Spark | EMR Serverless / Glue | Dataproc Serverless | Fabric Spark / Databricks | Data Flow |
| Fila/stream | Kinesis / MSK / SQS | Pub/Sub | Event Hubs / Service Bus | Streaming / Queue |
| Agendamento simples | EventBridge Scheduler | Cloud Scheduler | Logic Apps / Container Apps cron | Resource Scheduler / Functions |
| Segredos | Secrets Manager | Secret Manager | Key Vault | Vault |

Detalhes e armadilhas de custo em `skills/_clouds/*.md`.

## Antipadrões
- Lógica de negócio dentro do conector (deve ir para o dbt).
- Carga full diária de tabelas enormes quando há coluna de alteração.
- Testes só na gold (erros nascem na fonte: teste a bronze/silver também).
- Pipelines que falham em silêncio: todo erro alerta alguém (WhatsApp/Teams/e-mail).
