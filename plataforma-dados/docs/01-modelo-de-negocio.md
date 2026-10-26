# 01 — Modelo de negócio da consultoria

Este documento descreve o negócio **da consultoria** (Cardume). O modelo de
negócio **de cada cliente** é mapeado pelo questionário (seção 1) e pelo Agente
Analista de Negócios.

## Business Model Canvas

| Bloco | Conteúdo |
|---|---|
| **Segmentos de clientes** | PMEs com faturamento de R$ 5 a 300 milhões, começando pelo Oeste do Paraná: cooperativas e agroindústrias, transportadoras, associações de proteção veicular e corretoras, varejo regional, indústrias, clínicas, provedores de internet. Segundo segmento: software houses e revendas de ERP que querem oferecer BI aos seus clientes (white-label). |
| **Proposta de valor** | Plataforma de dados sob medida em semanas, não meses: discovery guiado, arquitetura e custo comparados nas 4 clouds e on-premise, e operação contínua. Para o cliente, decisões com números confiáveis; para o bolso, a infraestrutura mais barata que atende. |
| **Canais** | Instagram (conteúdo educativo + diagnóstico gratuito), LinkedIn, indicação de contadores e revendas de ERP, palestras em associações comerciais e cooperativas, site com o questionário. |
| **Relacionamento** | Diagnóstico gratuito de 20 minutos → Diagnóstico pago → MVP → Plataforma gerenciada com reunião mensal de resultados. |
| **Fontes de receita** | Diagnóstico (avulso), projetos de MVP, **mensalidade da plataforma gerenciada (recorrente)**, evolução por hora/sprint, projetos de IA aplicada. |
| **Recursos-chave** | Conhecimento sênior de engenharia de dados (AWS, Spark, Databricks, Lakehouse), servidor ZimaOS com GPU, plataforma MCP com os 11 agentes, base de conhecimento de SGBDs e memória vetorial, marca e conteúdo. |
| **Atividades-chave** | Discovery, desenho e implantação, operação e suporte, produção de conteúdo, gestão de custos dos clientes. |
| **Parcerias** | Programas de parceiros das clouds (AWS, Google, Microsoft, Oracle), Anthropic (Claude), contadores, revendas TOTVS/Sankhya, desenvolvedores freelancers. |
| **Estrutura de custos** | Energia e internet do servidor, assinatura/API do Claude, domínio e e-mail, ferramentas, impostos (Simples Nacional), horas de terceiros, marketing. |

## Ofertas e preços de partida
Calculados pela tabela da consultoria (`docs/11-precificacao.md`, com 12 exemplos completos). Resumo:

| Oferta | Preço (com impostos) | Objetivo |
|---|---|---|
| Diagnóstico de Dados | R$ 3.000 (P) a R$ 8.200 (G) | Porta de entrada paga; abatido do MVP |
| MVP de Plataforma | R$ 30–40 mil (P), R$ 70–110 mil (M/G) | Primeira pergunta de negócio respondida em 30–60 dias |
| Plataforma Gerenciada | R$ 2.350 (P), R$ 4.650 (M), R$ 10.050 (G) por mês | Receita recorrente; inclui horas de evolução |
| Banco de horas | R$ 3.700 (20 h/mês) a R$ 13.400 (80 h/mês) | Novas fontes, painéis, apps, automações |
| Serviços especializados | R$ 17–55 mil | DBA, migração de SGBD, Databricks/Snowflake com Git |
| IA Aplicada | a partir de ~R$ 31 mil | RAG, previsão, agentes |

## Economia unitária (cliente gerenciado porte P no ZimaOS)
| Item | Valor/mês |
|---|---|
| Mensalidade cobrada (10 h + taxa de plataforma) | R$ 2.350 |
| Horas de sustentação e evolução (10 h × R$ 100 de custo interno) | R$ 1.000 |
| Servidor, backup externo, monitoramento e API do Claude (rateio) | R$ 200 |
| Impostos (Simples anexo III, ~8,1%) | R$ 190 |
| **Margem de contribuição** | **R$ 960 (41%)** |

Com 8 clientes gerenciados nesse perfil: ~R$ 7,7 mil/mês de margem recorrente, além
dos projetos, suficiente para financiar a fase 2 do roadmap (`docs/09-roadmap-escala.md`).
A carteira de exemplo do `docs/11` mostra quando passa a faltar hora e entram freelancers.

## Posicionamento
- **Contra a consultoria grande**: preço e velocidade; o mesmo nível técnico com um time de agentes.
- **Contra o freelancer**: método, documentação, segurança e continuidade (plataforma gerenciada).
- **Contra o BI "de prateleira" do ERP**: cruza sistemas, guarda histórico, prevê e automatiza.

## Indicadores do negócio
Leads/mês por canal · taxa diagnóstico → MVP · ciclo de venda (dias) · ticket médio
de MVP · **MRR** da plataforma gerenciada · churn de clientes gerenciados · margem por
cliente · horas de operação por cliente (meta: cair com automação).

## Riscos e mitigação
| Risco | Mitigação |
|---|---|
| Dependência de uma pessoa | Skills e processos documentados; agentes padronizam a entrega; freelancers treinados no método |
| Servidor único (ZimaOS) cai | Backup 3-2-1, IaC para recriar em OCI Always Free em horas, clientes porte M+ direto na cloud |
| LLM local fraco | Modo assistido com Claude; local só para embeddings e rascunhos |
| Preço de cloud muda | Calculadora com preços em arquivo editável + validação por API pelo FinOps |
| LGPD | DPA padrão, isolamento por cliente, controles do agente Cyber (`docs/10-lgpd-contratos.md`) |
