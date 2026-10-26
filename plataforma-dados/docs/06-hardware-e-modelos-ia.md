# 06 — Hardware e modelos de IA (GPU de 6 GB, 16 GB de RAM)

## Estratégia: híbrido desde o primeiro dia
Rodar um LLM que dê conta de arquitetura, custos e proposta com qualidade de
consultoria exige modelos muito maiores do que cabem em 6 GB. Em vez de esperar
hardware, a plataforma divide o trabalho:

| Tarefa | Onde roda | Por quê |
|---|---|---|
| Embeddings (memória vetorial) | GPU local — `bge-m3` | Volume alto, custo zero, dado fica em casa |
| Busca, contas de custo, questionário | CPU local (código) | Determinístico; LLM não precisa fazer conta |
| Rascunhos, resumos, extração, classificação | GPU local — `qwen3:4b` | Bom o suficiente e grátis |
| Raciocínio dos agentes que vai para o cliente | **Claude** (Desktop/Code no modo assistido, ou API) | Qualidade; custa centavos a poucos dólares por cliente |
| Dado sensível que não pode sair | GPU local (`qwen3:8b` com contexto curto) | Privacidade acima de qualidade |

O modo padrão é `LLM_BACKEND=nenhum` (**assistido**): você usa o Claude conectado ao
MCP, e o servidor entrega o contexto completo de cada agente.

## Orçamento de VRAM (6 GB)
| Configuração | VRAM aproximada | Uso |
|---|---|---|
| `bge-m3` + `qwen3:4b` (Q4_K_M) com 16k de contexto e KV cache `q8_0` | ~5 GB | **Padrão**: tudo na GPU |
| `bge-m3` + `qwen3:8b` (Q4_K_M) com 4–8k de contexto | 6 GB+ | O Ollama descarrega parte para a CPU; mais lento |
| `nomic-embed-text` + `qwen3:8b` | ~5,8 GB | Alternativa com embedding leve (768 dimensões — exige reindexar) |
| `gemma3:4b` | ~3,3 GB | Alternativa forte em português, aceita imagem |

Configurações do compose que economizam VRAM: `OLLAMA_FLASH_ATTENTION=1`,
`OLLAMA_KV_CACHE_TYPE=q8_0`, `OLLAMA_NUM_PARALLEL=1`, `OLLAMA_MAX_LOADED_MODELS=2`.
Troque o modelo no `.env` (`MODELO_LOCAL`) e consulte ollama.com/library para versões
mais novas de modelos pequenos — a família muda rápido.

Velocidade esperada (ordem de grandeza, GPU de 6 GB de geração recente): 4B em Q4
gera dezenas de tokens por segundo; 8B com parte na CPU cai bastante. Um entregável
de agente (~2–4 mil tokens) leva de 1 a 5 minutos localmente.

## Orçamento de RAM (16 GB)
Ver tabela em `docs/04-arquitetura.md`. Resumo: núcleo (MCP + Qdrant + Ollama) usa
3–4 GB; o perfil `dados` (PostgreSQL + Metabase) mais ~2,5 GB; sobra espaço para os
pipelines de alguns clientes porte P.

## Custo do Claude por cliente (modo API)
Um pipeline completo (9 agentes) com Claude Opus 5.5 consome algo como 100–200 mil
tokens de entrada e 30–80 mil de saída (o raciocínio adaptativo conta como saída):
**≈ US$ 1,50 a 5,00 por cliente**. O papel + skill de cada agente fica em cache entre
clientes, o que reduz a entrada. No modo assistido, o uso entra na sua assinatura do Claude.

## Roadmap de hardware (acompanha a receita)
| Etapa | Gatilho | Investimento aproximado | Ganho |
|---|---|---|---|
| 0 — hoje | — | servidor atual (16 GB, GPU 6 GB) | Plataforma completa no modo assistido |
| 1 | 2 clientes gerenciados | +16 GB de RAM (total 32 GB) ~R$ 300–500 | Postgres + Metabase + pipelines de vários clientes sem aperto |
| 2 | 3–4 clientes | Nobreak senoidal + SSD NVMe 2 TB + HD de backup local ~R$ 1.500–2.500 | Disponibilidade e backup 3-2-1 local |
| 3 | 5–6 clientes | GPU de 12–16 GB (ex.: RTX 3060 12 GB, 4060 Ti 16 GB) ~R$ 2.000–3.500 | Modelos 8B–14B locais com contexto longo; agentes locais de verdade |
| 4 | 8+ clientes ou 1 cliente porte M | Clientes M/G na cloud escolhida pelo FinOps; ZimaOS fica com P e com a plataforma | Escala sem comprar servidor |
| 5 | MRR que pague | Segundo servidor (réplica) ou GPU 24 GB usada | Alta disponibilidade, modelos maiores |

Valores de hardware são estimativas do mercado brasileiro; pesquise antes de comprar.

## Checklist do servidor
- [ ] `nvidia-smi` funciona no ZimaOS (driver NVIDIA instalado)
- [ ] Docker vê a GPU: `docker run --rm --gpus all ubuntu nvidia-smi`
- [ ] Disco de dados com pelo menos 200 GB livres (modelos do Ollama ocupam 5–15 GB)
- [ ] Nobreak com desligamento automático
- [ ] Temperatura da GPU sob carga abaixo de ~80 °C
