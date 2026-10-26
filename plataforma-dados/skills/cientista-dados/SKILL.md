---
name: cientista-dados
description: Prioriza e desenha casos de machine learning e IA generativa (previsão, churn, fraude, crédito, precificação, RAG, agentes, OCR) com baseline, métrica, MLOps e decisão de onde rodar — GPU local de 6 GB com Ollama, Claude via API, ou SageMaker, Vertex AI, Azure ML e OCI Data Science. Use ao avaliar viabilidade de IA, estimar custo de inferência ou desenhar RAG sobre documentos e dados.
---

# Skill — Cientista de Dados

## Catálogo de casos (dados mínimos → abordagem inicial → métrica)
| Caso | Dados mínimos | Primeira abordagem | Métrica |
|---|---|---|---|
| Previsão de demanda/vendas | 2+ anos diários por SKU/loja | Sazonal ingênuo → ETS/Prophet → LightGBM com calendário | WAPE, viés |
| Churn / cancelamento | Histórico de clientes com rótulo de saída | Regras de risco → regressão logística → gradient boosting | AUC, precisão no top 10% |
| Inadimplência / crédito | Contratos + pagamentos + cadastro | Scorecard (WoE + logística) — explicável | KS, AUC, Gini |
| Fraude em sinistro/transação | Casos confirmados (mesmo poucos) | Regras + isolamento (Isolation Forest) → supervisionado | Precisão@k, recall |
| Precificação | Preço, volume, concorrência, custo | Elasticidade por segmento → otimização com restrições | Margem incremental |
| Segmentação | Transações e cadastro | RFM → k-means em features padronizadas | Estabilidade, uso pelo negócio |
| Manutenção preditiva | Sensores + ordens de manutenção | Limiares e tendência → sobrevivência / classificação | Falhas antecipadas |
| Rotas | Endereços, janelas, frota | OR-Tools (VRP) | Km e custo por entrega |
| OCR de documentos | PDFs/imagens | Docling/Tesseract → LLM para extrair campos com schema | Acurácia por campo |
| Assistente RAG | Documentos/FAQ/tickets | Busca híbrida (vetorial + palavra-chave) + LLM | Acerto em perguntas de teste |
| Text-to-SQL | Camada semântica documentada | Few-shot com SQL validado, views da gold | Acerto de execução |
| Agentes que executam tarefas | Processo descrito + APIs | Fluxo determinístico (n8n) + LLM só nas decisões | Tarefas concluídas sem retrabalho |

## Onde roda (decisão)
1. Regra/SQL resolve? → fica no dbt/BI.
2. ML clássico (tabular) → CPU basta; treino em VM/contêiner, inferência em lote no orquestrador.
3. LLM com dado sensível e `ia.llm_privacidade = local` → **Ollama local**.
4. LLM para entregável de alta qualidade (proposta, análise complexa) → **Claude via API** (Bedrock, Vertex, Azure AI Foundry ou API direta).
5. Volume alto e tarefa simples (classificação, extração) → modelo pequeno (Claude Haiku 5.5 por API, ou local 4B).

## LLM local com 6 GB de VRAM e 16 GB de RAM
| Modelo (Ollama) | Quantização | VRAM aprox. | Uso |
|---|---|---|---|
| `qwen3:4b` | Q4_K_M | ~3 GB + contexto | Padrão: resumos, extração, roteamento, SQL simples; cabe com 16k de contexto |
| `qwen3:8b` | Q4_K_M | ~5,2 GB | Melhor raciocínio; contexto curto (4–8k) para não estourar a VRAM |
| `gemma3:4b` | Q4 | ~3,3 GB | Bom em português; aceita imagem |
| `llama3.2:3b` | Q4 | ~2 GB | Rápido para classificação |
| `bge-m3` (embedding) | F16 | ~1,2 GB | Embeddings multilíngues (1024 dim) — ótimo para PT-BR |
| `nomic-embed-text` | F16 | ~0,3 GB | Alternativa leve (768 dim) |

Regras práticas: um modelo de chat por vez na GPU (`OLLAMA_MAX_LOADED_MODELS=2` com o embedding pequeno); `OLLAMA_FLASH_ATTENTION=1` e cache KV em `q8_0` economizam VRAM; acima de ~8B ou contextos longos, use API. Ver `docs/06-hardware-e-modelos-ia.md`.

## Custo de inferência (para o FinOps)
- API: tokens/mês × preço por milhão (tabela em `servidor/src/plataforma/dados/precos.yaml`, seção `llm_api`). Ex.: 20 usuários × 10 perguntas/dia × 22 dias × (3.000 entrada + 600 saída) ≈ 13,2 M tokens de entrada e 2,6 M de saída/mês.
- Local: energia da GPU (~120 W em uso) + amortização; latência maior.
- Cloud GPU: L4/T4/A10 por hora; só ligar em janelas (lotes) ou usar endpoints serverless.

## RAG — receita padrão
1. Ingestão: converter PDF/DOCX/HTML para Markdown (Docling), limpar cabeçalhos/rodapés.
2. Fragmentar por título, 800–1.200 caracteres, sobreposição de 10–15%, título da seção repetido em cada pedaço.
3. Embeddings `bge-m3`; Qdrant com payload (`cliente`, `origem`, `tipo`, data) e filtro obrigatório por cliente.
4. Busca híbrida (vetorial + BM25) e re-ranking quando a base passar de alguns milhares de trechos.
5. Prompt com instruções para citar a origem e responder "não encontrei" quando não houver evidência.
6. Avaliação: 30–50 perguntas reais com resposta esperada; medir antes de publicar e a cada mudança.

## MLOps proporcional
- P: notebooks versionados no Git, modelo salvo com data, previsão em lote pelo orquestrador, métrica no painel.
- M: MLflow (tracking + registry), validação automática antes de promover, alerta de drift (PSI > 0,2).
- G: plataforma da cloud (SageMaker, Vertex AI, Azure ML, OCI Data Science) com pipelines e endpoints.

## Por cloud
| | AWS | GCP | Azure | OCI |
|---|---|---|---|---|
| Plataforma ML | SageMaker AI | Vertex AI | Azure Machine Learning | OCI Data Science |
| LLM gerenciado | Bedrock (Claude) | Vertex AI (Claude, Gemini) | AI Foundry (Claude, OpenAI) | OCI Generative AI |
| ML no warehouse | Redshift ML | BigQuery ML | Fabric Data Science | Oracle Machine Learning (ADW) |
| OCR | Textract | Document AI | Document Intelligence | Document Understanding |
| Vetores | OpenSearch / S3 Vectors / pgvector | Vector Search / AlloyDB | AI Search / pgvector | Database 23ai Vector Search |

## Conformidade
- LGPD art. 20: titular pode pedir revisão de decisão automatizada → registre features e explicações (SHAP) para crédito, seguros, RH.
- Não usar dados sensíveis (art. 11) para treino sem base legal; pseudonimizar em ambiente de experimento.
- Contratos de API: confirmar que os dados não são usados para treino do provedor.

## Antipadrões
- Deep learning para 5 mil linhas tabulares.
- Modelo sem baseline ("90% de acurácia" em base desbalanceada).
- RAG sem conjunto de avaliação; LLM respondendo sem citar a fonte.
