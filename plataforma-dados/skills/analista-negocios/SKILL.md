---
name: analista-negocios
description: Traduz o modelo de negócio de um cliente em perguntas, KPIs com fórmula e requisitos de dados priorizados. Use ao iniciar o desenho de uma plataforma de dados, ao revisar respostas de discovery, ou quando precisar de um catálogo de KPIs por segmento (varejo, indústria, agro, logística, seguros/proteção veicular, finanças, saúde, educação, SaaS, setor público).
---

# Skill — Analista de Negócios

## Método
1. **Pergunta → decisão → número**: toda pergunta de negócio precisa nomear a decisão que ela destrava. Se não houver decisão, é curiosidade, não requisito.
2. **KPI bem definido** = nome + fórmula + filtro + granularidade + dimensões + fonte + dono + frequência.
3. **Árvore de KPIs**: decomponha o KPI principal (ex.: margem) em direcionadores (preço, mix, custo, desconto, frete) — cada folha aponta para uma fonte.
4. **MoSCoW** para priorizar; o MVP tem no máximo 8 KPIs.
5. **Valor**: horas manuais × custo/hora × 4,33 semanas; perda evitada (inadimplência, ruptura, fraude) × % de melhoria plausível (use 10–20% como premissa conservadora).

## Catálogo de KPIs por segmento

### Varejo / e-commerce
Receita líquida, ticket médio, itens por pedido, margem bruta por SKU/categoria, giro e cobertura de estoque (dias), ruptura (% de SKUs sem estoque com demanda), sell-through, GMROI, CAC por canal, taxa de conversão, recompra em 90 dias, LTV, devolução (%), take rate de marketplace, frete sobre receita.

### Indústria
OEE (disponibilidade × performance × qualidade), refugo e retrabalho (%), custo padrão vs real por produto, aderência ao plano de produção, lead time, MTBF/MTTR, consumo de energia por unidade, estoque em processo, atendimento de pedidos (OTIF).

### Agronegócio / cooperativas
Recebimento por safra e por cooperado, produtividade (sc/ha), preço médio pago vs CEPEA/B3, margem por unidade de negócio, inadimplência de cooperados, armazenagem (ocupação de silos, quebra técnica), custo de insumos por hectare, faturamento de insumos por técnico/agrônomo, prazo médio de recebimento.

### Logística / transporte
Custo por km e por entrega, receita por km, ocupação de carga (% peso/volume), OTIF, tempo de ciclo, consumo (km/l) por veículo e motorista, ociosidade da frota, avarias e sinistros por 100 mil km, margem por cliente/rota.

### Seguros / proteção veicular
Sinistralidade (sinistros pagos ÷ prêmios/contribuições), frequência e severidade de sinistro, inadimplência por safra de adesão, cancelamento (churn) mensal, ticket médio por perfil, % da tabela FIPE da carteira, tempo de regulação do sinistro, índice de fraude detectada, custo de aquisição por associado, eventos por rastreador.

### Serviços financeiros
Carteira ativa, inadimplência (over 30/60/90), roll rate, perda esperada (PD × LGD × EAD), aprovação de crédito, custo de captação, NIM, recuperação de cobrança, alertas de PLD tratados no prazo.

### Saúde
Taxa de ocupação de leitos, tempo médio de permanência, glosa (%), ticket por atendimento, absenteísmo de pacientes, sinistralidade (operadora), produção por médico, tempo de espera.

### Educação
Captação (lead → matrícula), evasão por turma/curso, inadimplência, rematrícula, custo por aluno, NPS, desempenho acadêmico.

### SaaS / tecnologia / ISP
MRR/ARR, churn de logo e de receita, NRR, CAC payback, LTV/CAC, ativação, DAU/MAU, tickets por cliente, ARPU; ISP: churn por bairro, tempo de reparo, ocupação de OLT.

### Serviços profissionais
Horas faturáveis (%), rentabilidade por cliente/projeto, prazo médio de recebimento, backlog, receita por colaborador.

### Setor público
Execução orçamentária, tempo de atendimento ao cidadão, indicadores de saúde/educação do município, transparência (dados abertos atualizados).

## Perguntas por área (para completar lacunas do discovery)
- **Financeiro**: quanto tempo leva o fechamento? Existe DRE gerencial por unidade? Como é feito o fluxo de caixa projetado?
- **Comercial**: as metas são por vendedor, região e mix? O CRM é a fonte da verdade do funil?
- **Operações**: o que é "produção" na sua empresa e onde é registrada?
- **Diretoria**: quais 3 números você olharia todo dia se estivessem confiáveis?

## Por cloud (o que o Analista de Negócios precisa saber)
Nada técnico, mas reconhecer ativos que mudam o caso de negócio:
- **Microsoft 365 / Power BI** já pagos (Azure): baixa a barreira de adoção dos painéis.
- **Google Workspace / GA4** (GCP): dados de marketing já exportáveis de graça ao BigQuery.
- **ERP Oracle** (OCI): integrações nativas e BYOL.
- **Já na AWS**: créditos e contratos existentes reduzem o custo de entrada.
Referências: `skills/_clouds/equivalencias.md`.

## Antipadrões
- Começar pelo dashboard em vez da decisão.
- KPI com nome bonito e fórmula vaga ("eficiência", "performance").
- MVP com 30 indicadores.
- Ignorar quem vai manter a definição do KPI depois do projeto.
