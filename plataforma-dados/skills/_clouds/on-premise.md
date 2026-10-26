# On-premise e ZimaOS — guia de referência para os agentes

On-premise aqui tem dois significados:
1. **Servidor do cliente**: a plataforma roda dentro da empresa (exigência de não usar SaaS, ambiente isolado, câmbio, dados sensíveis, ou hardware ocioso disponível).
2. **Servidor da própria consultoria (ZimaOS)**: hospedagem compartilhada para clientes pequenos, com isolamento por cliente. É o início do negócio, antes de ter caixa para cloud.

## Quando on-premise costuma ganhar
- Restrições `sem_saas` ou `air_gapped`, ou LLM 100% local (`ia.llm_privacidade = local`).
- Volume até alguns TB, poucas fontes, usuários internos, RTO de horas.
- Cliente já tem servidor com capacidade ociosa (`infra.onprem.ociosa = sim`).
- Variação do dólar é risco relevante (`infra.restricoes = cambio`).

## Quando costuma perder
- RTO em minutos, picos imprevisíveis, crescimento acima de 50% ao ano.
- Sem IP fixo, link instável, sem nobreak, sem ninguém para trocar um disco.
- Volume acima de dezenas de TB ou streaming de milhares de eventos por segundo.

## Stack open source de referência (cabe em 16 GB de RAM no porte P)

| Função | Ferramenta | RAM típica |
|---|---|---|
| Banco analítico | PostgreSQL 16+ (ou DuckDB em arquivos Parquet) | 1–4 GB |
| Ingestão | dlt (Python) | sob demanda |
| Transformação | dbt-core (dbt-postgres / dbt-duckdb) | sob demanda |
| Orquestração | Dagster (ou cron + n8n para começar) | 0,5–1 GB |
| BI | Metabase (JVM) ou Apache Superset | 1–2 GB |
| Automação | n8n | 0,3–0,5 GB |
| Banco vetorial | Qdrant (quantização int8, vetores em disco) | 0,3–1 GB |
| LLM local | Ollama (GPU 6 GB: modelos 3B–8B em Q4) | VRAM + 1–2 GB RAM |
| Acesso externo | Tailscale ou Cloudflare Tunnel (sem abrir porta no roteador) | 50 MB |
| Proxy/TLS | Caddy | 50 MB |
| Backup | restic ou Kopia para Backblaze B2 / Cloudflare R2 | sob demanda |
| Monitoramento | Uptime Kuma + Netdata (ou Prometheus/Grafana no porte M) | 0,2–1 GB |
| Identidade | Authentik ou Keycloak (porte M) | 0,5–1 GB |

## Multi-cliente no servidor da consultoria
- Um banco PostgreSQL **por cliente** (ou schema + roles separadas no mínimo) e um projeto dbt por cliente.
- Coleção `clientes` do Qdrant com filtro obrigatório por cliente (já implementado no servidor MCP).
- Usuários e coleções separados no Metabase; nunca um painel compartilhado entre clientes.
- Backups criptografados por cliente, com chave própria; contrato deixando claro onde os dados ficam (LGPD: a consultoria é operadora).
- Quando um cliente passar do porte P, migrar para a cloud escolhida pelo FinOps — o design em Parquet/dbt/Dagster é portátil.

## Requisitos mínimos de infraestrutura física
- Nobreak com autonomia de 15 minutos e desligamento automático (NUT).
- Discos em espelho (RAID 1/ZFS mirror) **e** backup fora do site; RAID não é backup.
- Link com IP fixo ou túnel; idealmente link secundário (4G/5G) para o acesso administrativo.
- Temperatura controlada; medir consumo de energia para o TCO real.

## TCO on-premise
A calculadora (`custos_estimar`) considera hardware amortizado em 36 meses, energia,
backup externo, link e horas de operação. O agente FinOps deve somar também:
licenças (se houver), substituição de discos (~5%/ano do valor) e o custo de
indisponibilidade quando o RTO exigido é baixo.
