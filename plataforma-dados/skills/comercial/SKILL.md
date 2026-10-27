---
name: comercial
description: Monta e precifica propostas de projetos e serviços de dados (diagnóstico, MVP, plataforma gerenciada, squad) com cálculo de ROI, cronograma, cláusulas LGPD e saída, tratamento de objeções e uso de programas de parceiros e créditos das clouds (AWS, Google Cloud, Microsoft, Oracle). Use ao transformar entregáveis técnicos em proposta, definir preço ou planejar o funil de vendas da consultoria.
---

# Skill — Comercial

## Portfólio em pacotes (escada de valor)
Valores da calculadora (`preco_estimar`, tabela em `servidor/src/plataforma/dados/precificacao.yaml`); exemplos completos em `docs/11-precificacao.md`.

| Pacote | O que é | Duração | Referência de preço (com impostos) |
|---|---|---|---|
| **Diagnóstico de Dados** | Discovery guiado + relatório dos agentes + proposta | 1–2 semanas | R$ 3.000 (P) · R$ 5.200 (M) · R$ 8.200 (G), abatido do MVP se fechar |
| **MVP de Plataforma** | 1–3 fontes, 1 pergunta de negócio, 3–6 painéis, ambiente produtivo | 30–60 dias | R$ 30–40 mil (P) · R$ 70–110 mil (M/G) |
| **Plataforma Gerenciada** | Sustentação + horas de evolução + taxa de plataforma | mensal | R$ 2.350 (P) · R$ 4.650 (M) · R$ 10.050 (G) + infraestrutura paga direto |
| **Banco de horas / evolução** | Novas fontes, painéis, apps, automações | mensal | R$ 3.700 (20 h) · R$ 7.100 (40 h) · R$ 13.400 (80 h); hora avulsa R$ 190 |
| **Serviços especializados** | DBA (saúde, tuning, backup), migração de SGBD, Databricks/Snowflake com Git | 3–8 semanas | R$ 17–55 mil |
| **IA Aplicada** | Assistente RAG local, previsão, automação com agentes | 4–8 semanas | a partir de ~R$ 31 mil |

A mensalidade gerenciada é a base do negócio: receita recorrente que paga o servidor e financia a escala.

## Precificação
1. **Horas por perfil** vindas das estimativas dos agentes.
2. **Taxa**: R$ 170/h líquida × multiplicador do perfil (arquiteto 1,25; DBA e Cyber 1,15; Databricks/Snowflake 1,3; analista 0,9).
3. **Gestão** de 15% sobre as horas técnicas e **reserva de risco** de 10/15/25% (complexidade baixa/média/alta).
4. **Impostos por dentro** (Simples Nacional anexo III com Fator R ≥ 28%; a alíquota efetiva sobe com o faturamento).
5. **Checagem por valor**: preço ≤ 30–40% do valor gerado no 1º ano; se passar, reduza o escopo da primeira fase.
6. **Checagem por orçamento**: se `orc.projeto` for menor, reduza escopo (nunca o preço abaixo do custo interno de R$ 100/h).
Use sempre `preco_estimar`: ele devolve tabela, parcelas (40/30/30), preço à vista (−5%), margem e premissas.

## ROI (fórmulas)
- Horas economizadas/ano = `aut.horas_manuais` × 52 × % automatizável (premissa 50–70%).
- Valor = horas × `aut.custo_hora` (ou R$ 50–80/h como premissa).
- Perda evitada = base (inadimplência, ruptura, sinistro, frete) × melhoria conservadora (5–15%).
- Payback (meses) = investimento ÷ (valor mensal − custo mensal de infraestrutura e sustentação).

## Estrutura de proposta que fecha
1. A pergunta de negócio do cliente com as palavras dele.
2. O que muda no dia a dia em 90 dias (antes × depois).
3. Escopo em fases, com a primeira pequena e garantida.
4. Investimento e retorno na mesma página.
5. Riscos e como mitigamos (mostra maturidade).
6. Próximo passo com data.

## Cláusulas que protegem os dois lados
- **Escopo e mudanças**: novas fontes/painéis via ordem de mudança ou banco de horas.
- **LGPD**: consultoria como operadora; DPA anexo; suboperadores listados (cloud escolhida).
- **Propriedade**: código e dados do cliente; frameworks e aceleradores da consultoria licenciados.
- **Saída**: entrega do repositório, documentação e dados em formato aberto ao fim do contrato.
- **SLA** da plataforma gerenciada: horário de atendimento, tempo de resposta por severidade.
- **Reajuste** anual (IPCA) e repasse de variação cambial da infraestrutura.

## Objeções comuns
| Objeção | Resposta |
|---|---|
| "Já temos relatórios do ERP." | Mostre a pergunta que o ERP não responde (cruzamento entre sistemas, histórico, previsão). |
| "Cloud é cara." | Mostre o comparativo do FinOps: há opção de R$ 0–500/mês no porte P. |
| "Nossos dados são bagunçados." | Por isso o MVP começa com 1 fonte e testes de qualidade; arrumar é parte do valor. |
| "E se vocês sumirem?" | Formatos abertos, repositório do cliente, cláusula de saída. |
| "IA vai vazar nossos dados?" | Opção de LLM 100% local; contratos de API sem treino; controles do Cyber. |

## Programas de parceiros e créditos (verifique regras vigentes)
| | Parceria | Créditos para clientes/startups | Marketplace |
|---|---|---|---|
| AWS | AWS Partner Network (APN) | AWS Activate; programas de migração via parceiros | AWS Marketplace |
| Google Cloud | Partner Advantage | Google for Startups Cloud Program; créditos de avaliação | Google Cloud Marketplace |
| Microsoft | Microsoft AI Cloud Partner Program | Microsoft for Startups; benefícios de parceiro | Azure Marketplace / AppSource |
| Oracle | Oracle PartnerNetwork (OPN) | Oracle for Startups; Always Free | Oracle Cloud Marketplace |
Créditos de cloud reduzem o custo de entrada do cliente e são argumento de venda.

## Funil e prospecção
- Etapas: lead → diagnóstico agendado → discovery respondido → proposta enviada → negociação → fechado/perdido.
- Fontes: Instagram (conteúdo educativo + diagnóstico gratuito de 20 min), LinkedIn, indicação de contadores e software houses de ERP, eventos locais (associações comerciais, cooperativas).
- Indicadores: taxa de conversão por etapa, ciclo de venda (dias), ticket médio, MRR da plataforma gerenciada, churn de clientes gerenciados.

## Antipadrões
- Proposta de 40 páginas técnicas para o sócio.
- Desconto antes de entender a objeção.
- Escopo aberto ("integrar todos os sistemas").
- Vender streaming e IA quando a dor é planilha manual.
