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
| **Recursos-chave** | Conhecimento sênior de engenharia de dados (AWS, Spark, Databricks, Lakehouse), servidor ZimaOS com GPU, plataforma MCP com os 9 agentes, base de conhecimento vetorial, marca e conteúdo. |
| **Atividades-chave** | Discovery, desenho e implantação, operação e suporte, produção de conteúdo, gestão de custos dos clientes. |
| **Parcerias** | Programas de parceiros das clouds (AWS, Google, Microsoft, Oracle), Anthropic (Claude), contadores, revendas TOTVS/Sankhya, desenvolvedores freelancers. |
| **Estrutura de custos** | Energia e internet do servidor, assinatura/API do Claude, domínio e e-mail, ferramentas, impostos (Simples Nacional), horas de terceiros, marketing. |

## Ofertas e preços de partida
Detalhe em `skills/comercial/SKILL.md`. Resumo:

| Oferta | Preço de partida | Objetivo |
|---|---|---|
| Diagnóstico de Dados | R$ 2.500–8.000 | Porta de entrada paga; abatido do MVP |
| MVP de Plataforma | R$ 15.000–60.000 | Primeira pergunta de negócio respondida em 30–60 dias |
| Plataforma Gerenciada | R$ 1.500–12.000/mês | Receita recorrente; inclui horas de evolução |
| Evolução / Squad | R$ 150–300/h | Novas fontes, painéis, automações |
| IA Aplicada | R$ 12.000–50.000 | RAG, previsão, agentes |

## Economia unitária (exemplo de cliente gerenciado porte P no ZimaOS)
| Item | Valor/mês |
|---|---|
| Mensalidade cobrada | R$ 2.500 |
| Horas de operação e evolução (6 h × R$ 100 de custo interno) | R$ 600 |
| Parcela do servidor (energia, link, backup, amortização) ÷ 8 clientes | R$ 60 |
| API do Claude (agentes, assistente) | R$ 40 |
| Impostos (Simples, ~11%) | R$ 275 |
| **Margem de contribuição** | **R$ 1.525 (61%)** |

Com 8 clientes gerenciados nesse perfil: ~R$ 12 mil/mês de margem, suficiente para
financiar a fase 2 do roadmap (`docs/09-roadmap-escala.md`).

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
