---
name: analista-dados
description: Cria catálogo de métricas, camada semântica e painéis de BI (Power BI, Looker/Looker Studio, QuickSight, Oracle Analytics, Metabase, Superset) com segurança por linha, alertas e plano de adoção. Use ao desenhar dashboards executivos e operacionais, padronizar métricas, escolher ferramenta de BI ou habilitar perguntas em linguagem natural sobre os dados.
---

# Skill — Analista de Dados

## Princípios de painel
- **Uma pergunta por painel**, escrita no topo.
- Hierarquia em Z: KPIs-resumo com comparação (meta, mês anterior, ano anterior) → tendência → quebra por dimensão → tabela de detalhe.
- Máximo de 7 KPIs no executivo; 1 cor de destaque para o que exige ação; vermelho/verde só para estado.
- Sempre mostrar **data da última atualização** e a definição da métrica (tooltip/descrição).
- Operação no celular: painel enxuto, filtros pré-aplicados por RLS.

## Catálogo de métricas — template
```
métrica: margem_bruta_pct
definição: (receita líquida − CMV) ÷ receita líquida, por período de emissão da NF
fórmula SQL: sum(receita_liquida - cmv) / nullif(sum(receita_liquida), 0)
filtros: exclui devoluções (CFOP 1202/2202) e transferências entre filiais
granularidade mínima: dia × filial × produto
dono: Controladoria
```

## Camada semântica por ferramenta
| Ferramenta | Onde vive a métrica | Observações |
|---|---|---|
| Power BI | Modelo semântico (DAX), medidas | Import para velocidade; DirectQuery só com volume alto; RLS por função DAX. |
| Looker | LookML (explores, measures) | Governança forte; custo enterprise. |
| Looker Studio | Campos calculados / views no BigQuery | Grátis; prefira a métrica na view do BigQuery. |
| QuickSight | Datasets + SPICE | Leitores baratos; RLS por dataset rules. |
| Oracle Analytics | Modelo semântico | Bom com ADW; cobrança por OCPU. |
| Metabase | Modelos + Metrics | Open source; ótimo para PMEs; sandboxing (RLS) na versão paga. |
| Superset | Datasets virtuais + métricas | Open source; RLS nativa. |
| dbt Semantic Layer / Cube | Fora do BI (headless) | Uma definição para vários BIs e para o LLM. |

## Escolha de BI (heurística)
1. Cliente tem Microsoft 365 e até ~150–250 leitores → **Power BI Pro**.
2. Orçamento mínimo, GCP ou BigQuery → **Looker Studio**.
3. On-premise/ZimaOS ou OCI, PME → **Metabase** (ou Superset se precisar de RLS sem pagar).
4. AWS com muitos leitores ocasionais → **QuickSight**.
5. Embedded para clientes externos → Metabase/Superset embedding, Power BI Embedded ou QuickSight embedding (orçar à parte).

## Segurança por linha
- Tabela de mapeamento `usuario → unidade/carteira/cliente` mantida pelo cliente, carregada pelo pipeline.
- Teste RLS com usuários reais de cada perfil antes do go-live.

## Perguntas em linguagem natural (text-to-SQL)
- O LLM consulta **apenas** a camada semântica/views da gold, com usuário de banco somente leitura e limite de linhas.
- Contexto do modelo: dicionário de métricas + exemplos de perguntas e SQL validado (few-shot).
- Toda resposta mostra a consulta usada e a data de atualização.
- Local (GPU 6 GB): modelos 7B–8B em Q4 funcionam para SQL simples sobre poucas tabelas; perguntas complexas vão para Claude via API.

## Alertas
Limiar fixo (estoque < mínimo), variação (queda > 15% vs média de 4 semanas), ausência (pipeline sem dado novo) — enviados por WhatsApp/Teams/e-mail pelo n8n.

## Plano de adoção
- Semana 1: painel validado com os donos das métricas (números batem com a fonte oficial).
- Semana 2–4: treinamento por perfil (30–60 min), ritual semanal de resultados usando o painel.
- Medir uso: acessos por usuário/semana; painel sem uso em 30 dias é revisto ou removido.

## Por cloud
| | AWS | GCP | Azure | OCI | On-prem |
|---|---|---|---|---|---|
| BI nativo | QuickSight | Looker / Looker Studio | Power BI / Fabric | Oracle Analytics Cloud | Metabase / Superset |
| Cache/aceleração | SPICE | BI Engine | Import / Direct Lake | OAC cache | Cache do Metabase |
| Embedded | QuickSight Embedding | Looker Embed | Power BI Embedded | OAC Embed | Metabase/Superset embed |

## Antipadrões
- Painel com 25 gráficos; pizza com 12 fatias; eixo Y truncado em barras.
- Métrica recalculada em cada relatório com filtros diferentes.
- Entregar sem validar com o dono do número.
