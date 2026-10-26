---
name: comercial
description: Monta e precifica propostas de projetos e serviços de dados (diagnóstico, MVP, plataforma gerenciada, squad) com cálculo de ROI, cronograma, cláusulas LGPD e saída, tratamento de objeções e uso de programas de parceiros e créditos das clouds (AWS, Google Cloud, Microsoft, Oracle). Use ao transformar entregáveis técnicos em proposta, definir preço ou planejar o funil de vendas da consultoria.
---

# Skill — Comercial

## Portfólio em pacotes (escada de valor)
| Pacote | O que é | Duração | Referência de preço* |
|---|---|---|---|
| **Diagnóstico de Dados** | Discovery guiado + relatório dos 9 agentes + proposta | 1–2 semanas | R$ 2.500–8.000 (abatido do MVP se fechar) |
| **MVP de Plataforma** | 1–2 fontes, 1 pergunta de negócio, 2–3 painéis, ambiente produtivo | 30–60 dias | R$ 15.000–60.000 |
| **Plataforma Gerenciada** | Operação, monitoramento, ajustes e novas métricas (horas inclusas) | mensal | R$ 1.500–12.000/mês + infraestrutura |
| **Evolução / Squad** | Novas fontes, IA, automações por sprint | por sprint/hora | R$ 150–300/h |
| **IA Aplicada** | Assistente RAG, previsão, automação com agentes | 4–8 semanas | R$ 12.000–50.000 |
*Valores de partida para o mercado brasileiro de PMEs; ajuste à sua realidade, região e posicionamento. Revise a cada 6 meses.

A mensalidade gerenciada é a base do negócio: receita recorrente que paga o servidor e financia a escala.

## Precificação
1. **Custo**: horas estimadas × custo/hora interno (pró-labore + impostos + ferramentas) .
2. **Preço por esforço**: custo × (1 + margem de 40–60%) + gestão (15%) + risco (10–20%).
3. **Checagem por valor**: preço do projeto ≤ 30–40% do valor gerado no 1º ano → aprovação fácil.
4. **Checagem por orçamento**: se `orc.projeto` for menor, reduza escopo (nunca a margem abaixo do custo).
5. Impostos: considere o regime (Simples Nacional anexo III/V, Lucro Presumido) no preço final.

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
