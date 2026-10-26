# 09 — Roadmap de escala

A regra: **cada etapa é paga pela anterior**. Nada de comprar infraestrutura antes da receita que a justifica.

| Fase | Meta de negócio | Infraestrutura | Plataforma | Marketing |
|---|---|---|---|---|
| **0 — Fundação** (mês 0–1) | Primeiro diagnóstico pago | ZimaOS 16 GB + GPU 6 GB; modo assistido com Claude | Questionário, 11 agentes, base de conhecimento, calculadoras de custo e de preço, MCP (esta entrega) | Identidade visual, Instagram com 9 posts de grid, LinkedIn alinhado |
| **1 — Primeiros clientes** (mês 1–4) | 2–3 MVPs, 2 clientes gerenciados | +16 GB RAM; perfil `dados` (Postgres + Metabase) no ZimaOS | Templates de projeto por segmento (agro, transporte, proteção veicular); lições na memória | 3 posts/semana; 1 caso real por mês; parcerias com 2 contadores |
| **2 — Recorrência** (mês 4–9) | MRR de R$ 10–15 mil; 5–8 clientes | Nobreak, SSD, backup 3-2-1; Cloudflare Tunnel; Uptime Kuma | Pipeline automático com `LLM_BACKEND=anthropic` para FinOps/Comercial; painel interno de clientes; n8n para alertas | Reels curtos de "antes e depois"; webinar mensal |
| **3 — Escala técnica** (mês 9–15) | MRR de R$ 25–40 mil; primeiro cliente porte M | GPU 12–16 GB; clientes M/G na cloud escolhida (conta por cliente, IaC padronizada) | Agentes locais com modelos 8–14B; módulos OpenTofu por cloud prontos; portal do cliente | Cases por segmento; presença em eventos do agro e do transporte |
| **4 — Time** (mês 15+) | 1–2 pessoas no time; white-label para software houses | Segundo servidor (réplica) ou migração da plataforma para OCI/AWS | Multiusuário no MCP (OAuth); SLA formal; certificações de parceiro nas clouds | Programa de indicação; parceiros de ERP |

## Gatilhos de decisão
- **Mais RAM**: uso médio acima de 75% por uma semana.
- **GPU maior**: mais de 30% do tempo de agentes indo para API por limite de contexto local, ou cliente com `ia.llm_privacidade = local`.
- **Cliente fora do ZimaOS**: porte M, RTO em horas ou menos, dado regulado (BACEN/ANS), ou consumo acima de 15% do servidor.
- **Contratar**: mais de 60 horas/mês de operação recorrente ou 3 implantações simultâneas.

## Métricas acompanhadas mensalmente
MRR · margem por cliente · horas de operação por cliente · leads e conversão por
canal · custo de infraestrutura por cliente · uso dos painéis pelos clientes · NPS.
