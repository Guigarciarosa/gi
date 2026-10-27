# 11 — Precificação: quanto cobrar

Este documento mostra como a consultoria forma preço e traz exemplos completos para os
tipos de cliente que você atende. Todos os números saem da calculadora
(`servidor/src/plataforma/precificacao.py` + `dados/precificacao.yaml`), a mesma que o
agente Comercial usa pela ferramenta MCP `preco_estimar`. Mude a tabela e rode
`python scripts/gerar_exemplos_preco.py` para atualizar as tabelas abaixo.

> Valores de partida para PMEs no Brasil, em outubro de 2026. Ajuste à sua região, ao
> seu posicionamento e ao que o mercado aceita. Revise a cada 6 meses.

## Como o preço é formado
1. **Horas por perfil**, tiradas das tabelas de estimativa das skills de cada agente.
2. **Taxa da hora** = taxa base líquida × multiplicador do perfil (arquiteto, DBA, Databricks/Snowflake valem mais por hora).
3. **Gestão** de 15% sobre as horas técnicas (reuniões, alinhamento, documentação).
4. **Reserva de risco** de 10%, 15% ou 25% conforme a complexidade (fontes desconhecidas, dados ruins, fornecedor de ERP lento).
5. **Impostos** por dentro: preço = valor líquido ÷ (1 − alíquota efetiva).
6. **Arredondamento** para cima em centenas.
7. **Checagem por valor**: o preço do projeto deve ficar abaixo de 30–40% do valor que ele gera no primeiro ano. Se passar, corte o escopo da primeira fase em vez de dar desconto.
8. **Infraestrutura à parte**: o cliente paga a cloud direto ao provedor (não entra na sua nota nem no seu imposto). No ZimaOS, a infraestrutura está dentro da taxa de plataforma da mensalidade.

## O que oferecer (escada de valor)
| Oferta | Para quê | Referência |
|---|---|---|
| Diagnóstico pago | porta de entrada; abatido do MVP | tabela "Diagnóstico pago" |
| MVP / projeto | primeira pergunta de negócio respondida em 30–60 dias | exemplos 1 a 12 |
| Plataforma gerenciada | receita recorrente; sustentação + evolução | tabela de mensalidades |
| Banco de horas | evolução contínua (novas fontes, painéis, apps) | tabela de banco de horas |
| Serviços avulsos de DBA, migração, Databricks/Snowflake | clientes que já têm plataforma | exemplos 8 a 11 |

<!-- exemplos:inicio -->

*Gerado por `scripts/gerar_exemplos_preco.py` a partir de `precificacao.yaml`. Não edite à mão.*

### Taxa por hora de cada perfil

| Perfil | Líquido/h | Com impostos/h |
|---|---:|---:|
| negocios | R$ 170 | R$ 185 |
| arquiteto | R$ 213 | R$ 232 |
| dba | R$ 196 | R$ 213 |
| engenheiro | R$ 170 | R$ 185 |
| analista | R$ 153 | R$ 166 |
| cientista | R$ 204 | R$ 222 |
| fullstack | R$ 170 | R$ 185 |
| cyber | R$ 196 | R$ 213 |
| devops | R$ 179 | R$ 195 |
| finops | R$ 170 | R$ 185 |
| plataforma | R$ 221 | R$ 240 |

Impostos: Simples Nacional, anexo III, faturamento de 12 meses de R$ 300.000: alíquota efetiva de 8,08%.

### Simples Nacional: anexo III × anexo V

| Faturamento em 12 meses | Anexo III (Fator R ≥ 28%) | Anexo V |
|---|---:|---:|
| R$ 150.000 | 6,0% | 15,5% |
| R$ 300.000 | 8,1% | 16,5% |
| R$ 500.000 | 10,0% | 17,5% |
| R$ 800.000 | 11,5% | 18,4% |
| R$ 1.500.000 | 13,6% | 19,4% |

Com pró-labore + folha de pelo menos 28% do faturamento (Fator R), a consultoria fica no anexo III e paga cerca da metade do imposto do anexo V. Confirme com o seu contador.

### Resumo dos exemplos

| # | Exemplo | Horas | Projeto | À vista | Mensalidade | Infra e licenças/mês* | Payback |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 | Transportadora (porte P): custo por km e margem por cliente | 167,9 | R$ 36.200 | R$ 34.400 | R$ 2.350 | — | 3,6 meses |
| 2 | Associação de proteção veicular (porte P): inadimplência e sinistralidade | 154,1 | R$ 33.200 | R$ 31.500 | R$ 2.350 | R$ 5 | 2,7 meses |
| 3 | Cooperativa agroindustrial (porte M): recebimento, preço e estoque em um painel | 338,1 | R$ 72.800 | R$ 69.200 | R$ 4.650 | R$ 6.362 | 2,2 meses |
| 4 | Varejo com e-commerce (porte P): vendas por canal e margem | 156,4 | R$ 32.000 | R$ 30.400 | R$ 2.350 | R$ 562 | 4,3 meses |
| 5 | Indústria (porte M): OEE e custo por produto | 384,1 | R$ 90.300 | R$ 85.800 | R$ 4.650 | R$ 4.173 | 3 meses |
| 6 | Clínica e laboratório (porte P): faturamento por convênio e glosas | 149,5 | R$ 32.800 | R$ 31.200 | R$ 2.350 | — | 4,9 meses |
| 7 | Software house (porte G): analytics dentro do produto (embedded) e API | 460 | R$ 107.800 | R$ 102.400 | R$ 10.050 | R$ 3.898 | 4,3 meses |
| 8 | DBA avulso: saúde do banco SQL Server do ERP | 73,6 | R$ 17.300 | R$ 16.400 | R$ 1.700 | — | — |
| 9 | Migração de MySQL 5.7 (sem suporte) para PostgreSQL gerenciado | 172,5 | R$ 44.500 | R$ 42.300 | — | — | — |
| 10 | Cliente com Databricks (porte G): Git, CI/CD, Unity Catalog e custos | 170,2 | R$ 46.200 | R$ 43.900 | R$ 10.050 | — | 3,1 meses |
| 11 | Implantação de Snowflake com dbt e Git (porte M) | 213,9 | R$ 53.000 | R$ 50.400 | R$ 4.650 | — | — |
| 12 | Assistente de IA com os documentos da empresa, rodando local | 133,4 | R$ 30.800 | R$ 29.300 | R$ 2.350 | — | 6,2 meses |

*Cloud e licenças de BI estimadas pela calculadora de custos, pagas direto pelo cliente aos fornecedores; "—" quando a infraestrutura fica dentro da taxa de plataforma (ZimaOS) ou depende do dimensionamento (créditos Snowflake, DBUs, banco gerenciado).

### 1. Transportadora (porte P): custo por km e margem por cliente

**Cliente**: 40 caminhões, TOTVS Protheus em SQL Server, rastreador com API e planilha da oficina.  
**Hospedagem**: ZimaOS da consultoria (PostgreSQL + Metabase); infraestrutura dentro da taxa de plataforma  
**Complexidade**: média

| Item | Perfil | Horas | R$/h | Valor |
|---|---|---:|---:|---:|
| Discovery e mapa de KPIs | negocios | 10 | 170 | R$ 1.700 |
| Arquitetura e decisão de hospedagem | arquiteto | 6 | 213 | R$ 1.278 |
| Acesso ao Protheus: usuário de leitura, janela, VPN | dba | 6 | 196 | R$ 1.176 |
| Fonte Protheus: faturamento e contas a pagar | engenheiro | 40 | 170 | R$ 6.800 |
| API do rastreador | engenheiro | 12 | 170 | R$ 2.040 |
| Planilha da oficina com contrato | engenheiro | 6 | 170 | R$ 1.020 |
| Modelos dbt: viagens, custos, margem | engenheiro | 24 | 170 | R$ 4.080 |
| Ambiente base: orquestrador, CI, cofre, backup | devops | 16 | 179 | R$ 2.864 |
| 3 painéis e treinamento | analista | 22 | 153 | R$ 3.366 |
| Controles de acesso e LGPD | cyber | 4 | 196 | R$ 784 |
| Gestão do projeto | — | 21,9 | — | R$ 3.766 |
| Reserva de risco | — | — | — | R$ 4.331 |
| Impostos | — | — | — | R$ 2.925 |
| **Preço do projeto** | | **167,9 h** | | **R$ 36.200** |

- **Preço**: R$ 36.200 (à vista R$ 34.400; parcelado 40/30/30: R$ 14.480 / R$ 10.860 / R$ 10.860) · R$ 216/h em média · margem estimada 45,5%
- **Mensalidade depois da entrega**: R$ 2.350 (6 h de sustentação + 4 h de evolução); hora adicional R$ 190
- **Retorno**: 2% de economia sobre R$ 6 milhões/ano de custo da frota ≈ R$ 120.000/ano → payback de 3,6 meses

### 2. Associação de proteção veicular (porte P): inadimplência e sinistralidade

**Cliente**: 8 mil associados, sistema próprio em MySQL, duas planilhas e alertas por WhatsApp.  
**Hospedagem**: OCI (Always Free) com Metabase  
**Complexidade**: média

| Item | Perfil | Horas | R$/h | Valor |
|---|---|---:|---:|---:|
| Discovery e KPIs | negocios | 8 | 170 | R$ 1.360 |
| Arquitetura | arquiteto | 4 | 213 | R$ 852 |
| Banco MySQL: réplica e usuário de leitura | dba | 6 | 196 | R$ 1.176 |
| Fonte do sistema: associados, boletos, sinistros | engenheiro | 24 | 170 | R$ 4.080 |
| 2 planilhas com contrato | engenheiro | 12 | 170 | R$ 2.040 |
| Modelos dbt: carteira, inadimplência, sinistralidade | engenheiro | 36 | 170 | R$ 6.120 |
| Alertas no WhatsApp (n8n) | engenheiro | 8 | 170 | R$ 1.360 |
| Ambiente base | devops | 12 | 179 | R$ 2.148 |
| 3 painéis e treinamento | analista | 18 | 153 | R$ 2.754 |
| Dados pessoais e LGPD | cyber | 6 | 196 | R$ 1.176 |
| Gestão do projeto | — | 20,1 | — | R$ 3.460 |
| Reserva de risco | — | — | — | R$ 3.979 |
| Impostos | — | — | — | R$ 2.683 |
| **Preço do projeto** | | **154,1 h** | | **R$ 33.200** |

- **Preço**: R$ 33.200 (à vista R$ 31.500; parcelado 40/30/30: R$ 13.280 / R$ 9.960 / R$ 9.960) · R$ 215/h em média · margem estimada 45,5%
- **Mensalidade depois da entrega**: R$ 2.350 (6 h de sustentação + 4 h de evolução) + cloud e licenças de ~R$ 5/mês pagas direto aos fornecedores; hora adicional R$ 190
- **Retorno**: 1 ponto a menos de inadimplência sobre R$ 15 milhões/ano de mensalidades ≈ R$ 150.000/ano → payback de 2,7 meses

### 3. Cooperativa agroindustrial (porte M): recebimento, preço e estoque em um painel

**Cliente**: 20 unidades, Protheus em Oracle, balança em SQL Server local, cotações CEPEA, Microsoft 365.  
**Hospedagem**: Azure com Power BI  
**Complexidade**: média

| Item | Perfil | Horas | R$/h | Valor |
|---|---|---:|---:|---:|
| Discovery com 4 áreas e KPIs | negocios | 16 | 170 | R$ 2.720 |
| Arquitetura e ADRs | arquiteto | 12 | 213 | R$ 2.556 |
| Banco Oracle do Protheus: janela, usuário, licença | dba | 16 | 196 | R$ 3.136 |
| Protheus: recebimento e vendas, financeiro, estoque | engenheiro | 72 | 170 | R$ 12.240 |
| Balança (SQL Server local) | engenheiro | 16 | 170 | R$ 2.720 |
| Cotações CEPEA e câmbio (APIs) | engenheiro | 8 | 170 | R$ 1.360 |
| Modelos dbt: 5 fatos | engenheiro | 60 | 170 | R$ 10.200 |
| Ambiente e CI no Azure | devops | 32 | 179 | R$ 5.728 |
| Camada semântica e 6 painéis Power BI | analista | 48 | 153 | R$ 7.344 |
| Segurança e LGPD | cyber | 8 | 196 | R$ 1.568 |
| Custos e reserva de capacidade | finops | 6 | 170 | R$ 1.020 |
| Gestão do projeto | — | 44,1 | — | R$ 7.589 |
| Reserva de risco | — | — | — | R$ 8.727 |
| Impostos | — | — | — | R$ 5.882 |
| **Preço do projeto** | | **338,1 h** | | **R$ 72.800** |

- **Preço**: R$ 72.800 (à vista R$ 69.200; parcelado 40/30/30: R$ 29.120 / R$ 21.840 / R$ 21.840) · R$ 215/h em média · margem estimada 45,5%
- **Mensalidade depois da entrega**: R$ 4.650 (12 h de sustentação + 8 h de evolução) + cloud e licenças de ~R$ 6.362/mês pagas direto aos fornecedores; hora adicional R$ 190
- **Retorno**: 1% de ganho na compra de grãos e na gestão de estoque ≈ R$ 400.000/ano → payback de 2,2 meses

### 4. Varejo com e-commerce (porte P): vendas por canal e margem

**Cliente**: Loja VTEX, Mercado Livre e Bling; diretoria quer margem por canal e produto.  
**Hospedagem**: Google Cloud: BigQuery + Looker Studio  
**Complexidade**: baixa

| Item | Perfil | Horas | R$/h | Valor |
|---|---|---:|---:|---:|
| Discovery e KPIs | negocios | 10 | 170 | R$ 1.700 |
| Arquitetura | arquiteto | 6 | 213 | R$ 1.278 |
| API da VTEX | engenheiro | 8 | 170 | R$ 1.360 |
| API do Mercado Livre | engenheiro | 12 | 170 | R$ 2.040 |
| API do Bling | engenheiro | 8 | 170 | R$ 1.360 |
| Google Analytics 4 (exportação) | engenheiro | 4 | 170 | R$ 680 |
| Modelos dbt: 4 fatos | engenheiro | 40 | 170 | R$ 6.800 |
| Ambiente no Google Cloud | devops | 16 | 179 | R$ 2.864 |
| 4 painéis no Looker Studio | analista | 24 | 153 | R$ 3.672 |
| Custos do BigQuery (partições, limites) | finops | 4 | 170 | R$ 680 |
| LGPD | cyber | 4 | 196 | R$ 784 |
| Gestão do projeto | — | 20,4 | — | R$ 3.483 |
| Reserva de risco | — | — | — | R$ 2.670 |
| Impostos | — | — | — | R$ 2.586 |
| **Preço do projeto** | | **156,4 h** | | **R$ 32.000** |

- **Preço**: R$ 32.000 (à vista R$ 30.400; parcelado 40/30/30: R$ 12.800 / R$ 9.600 / R$ 9.600) · R$ 205/h em média · margem estimada 43,0%
- **Mensalidade depois da entrega**: R$ 2.350 (6 h de sustentação + 4 h de evolução) + cloud e licenças de ~R$ 562/mês pagas direto aos fornecedores; hora adicional R$ 190
- **Retorno**: 1 ponto de margem sobre R$ 9 milhões/ano de vendas online ≈ R$ 90.000/ano → payback de 4,3 meses

### 5. Indústria (porte M): OEE e custo por produto

**Cliente**: TOTVS Datasul (Progress) e MES em SQL Server; servidores próprios na fábrica.  
**Hospedagem**: Servidor do cliente (on-premise) com Power BI  
**Complexidade**: alta

| Item | Perfil | Horas | R$/h | Valor |
|---|---|---:|---:|---:|
| Discovery e KPIs industriais | negocios | 16 | 170 | R$ 2.720 |
| Arquitetura | arquiteto | 12 | 213 | R$ 2.556 |
| Progress (largura SQL, ODBC) e Change Tracking no MES | dba | 24 | 196 | R$ 4.704 |
| Datasul: vendas, produção, estoque | engenheiro | 108 | 170 | R$ 18.360 |
| MES em SQL Server (Change Tracking) | engenheiro | 24 | 170 | R$ 4.080 |
| Modelos dbt: 5 fatos, incluindo OEE | engenheiro | 70 | 170 | R$ 11.900 |
| Ambiente e CI on-premise | devops | 32 | 179 | R$ 5.728 |
| 5 painéis e treinamento | analista | 40 | 153 | R$ 6.120 |
| Segurança | cyber | 8 | 196 | R$ 1.568 |
| Gestão do projeto | — | 50,1 | — | R$ 8.660 |
| Reserva de risco | — | — | — | R$ 16.599 |
| Impostos | — | — | — | R$ 7.296 |
| **Preço do projeto** | | **384,1 h** | | **R$ 90.300** |

- **Preço**: R$ 90.300 (à vista R$ 85.800; parcelado 40/30/30: R$ 36.120 / R$ 27.090 / R$ 27.090) · R$ 235/h em média · margem estimada 49,4%
- **Mensalidade depois da entrega**: R$ 4.650 (12 h de sustentação + 8 h de evolução) + cloud e licenças de ~R$ 4.173/mês pagas direto aos fornecedores; hora adicional R$ 190
- **Retorno**: 3 pontos de OEE numa fábrica de R$ 40 milhões/ano ≈ R$ 360.000/ano → payback de 3 meses

### 6. Clínica e laboratório (porte P): faturamento por convênio e glosas

**Cliente**: Sistema regional em Firebird; dados de saúde.  
**Hospedagem**: ZimaOS da consultoria; leitura a partir do backup diário restaurado  
**Complexidade**: média

| Item | Perfil | Horas | R$/h | Valor |
|---|---|---:|---:|---:|
| Discovery e KPIs | negocios | 8 | 170 | R$ 1.360 |
| Arquitetura | arquiteto | 4 | 213 | R$ 852 |
| Firebird: restaurar o backup diário para leitura | dba | 10 | 196 | R$ 1.960 |
| Fonte Firebird: atendimentos e faturamento | engenheiro | 32 | 170 | R$ 5.440 |
| Modelos dbt: 3 fatos | engenheiro | 30 | 170 | R$ 5.100 |
| Ambiente base | devops | 12 | 179 | R$ 2.148 |
| 3 painéis | analista | 18 | 153 | R$ 2.754 |
| Dados de saúde (LGPD art. 11): controles e DPA | cyber | 16 | 196 | R$ 3.136 |
| Gestão do projeto | — | 19,5 | — | R$ 3.412 |
| Reserva de risco | — | — | — | R$ 3.924 |
| Impostos | — | — | — | R$ 2.650 |
| **Preço do projeto** | | **149,5 h** | | **R$ 32.800** |

- **Preço**: R$ 32.800 (à vista R$ 31.200; parcelado 40/30/30: R$ 13.120 / R$ 9.840 / R$ 9.840) · R$ 219/h em média · margem estimada 46,3%
- **Mensalidade depois da entrega**: R$ 2.350 (6 h de sustentação + 4 h de evolução); hora adicional R$ 190
- **Retorno**: redução de glosas de convênio ≈ R$ 80.000/ano → payback de 4,9 meses (preço acima de 40% do valor anual: reduza o escopo da primeira fase)

### 7. Software house (porte G): analytics dentro do produto (embedded) e API

**Cliente**: SaaS B2B com 150 clientes, PostgreSQL do produto; quer vender um módulo de indicadores.  
**Hospedagem**: AWS com Metabase embutido  
**Complexidade**: alta

| Item | Perfil | Horas | R$/h | Valor |
|---|---|---:|---:|---:|
| Discovery e definição do módulo | negocios | 12 | 170 | R$ 2.040 |
| Arquitetura multi-tenant | arquiteto | 16 | 213 | R$ 3.408 |
| CDC do PostgreSQL do produto | dba | 12 | 196 | R$ 2.352 |
| CDC e eventos de uso | engenheiro | 48 | 170 | R$ 8.160 |
| Modelos dbt: 6 fatos | engenheiro | 72 | 170 | R$ 12.240 |
| Projeto base do app: login, CI, deploy | fullstack | 24 | 170 | R$ 4.080 |
| Multi-tenant com RLS e testes de isolamento | fullstack | 16 | 170 | R$ 2.720 |
| 8 painéis embutidos com RLS | fullstack | 64 | 170 | R$ 10.880 |
| API de dados (10 endpoints) | fullstack | 40 | 170 | R$ 6.800 |
| Ambiente e CI | devops | 32 | 179 | R$ 5.728 |
| 8 painéis | analista | 48 | 153 | R$ 7.344 |
| Segurança da aplicação | cyber | 16 | 196 | R$ 3.136 |
| Gestão do projeto | — | 60 | — | R$ 10.333 |
| Reserva de risco | — | — | — | R$ 19.805 |
| Impostos | — | — | — | R$ 8.710 |
| **Preço do projeto** | | **460 h** | | **R$ 107.800** |

- **Preço**: R$ 107.800 (à vista R$ 102.400; parcelado 40/30/30: R$ 43.120 / R$ 32.340 / R$ 32.340) · R$ 234/h em média · margem estimada 49,2%
- **Mensalidade depois da entrega**: R$ 10.050 (28 h de sustentação + 16 h de evolução) + cloud e licenças de ~R$ 3.898/mês pagas direto aos fornecedores; hora adicional R$ 190
- **Retorno**: novo módulo vendido a 150 clientes por R$ 170/mês ≈ R$ 300.000/ano → payback de 4,3 meses

### 8. DBA avulso: saúde do banco SQL Server do ERP

**Cliente**: ERP lento no fechamento, backup nunca testado; o cliente quer diagnóstico e plano.  
**Hospedagem**: Servidor do cliente  
**Complexidade**: baixa

| Item | Perfil | Horas | R$/h | Valor |
|---|---|---:|---:|---:|
| Inventário e avaliação de saúde | dba | 8 | 196 | R$ 1.568 |
| Backup e teste de restauração documentado | dba | 8 | 196 | R$ 1.568 |
| 2 rodadas de diagnóstico e tuning | dba | 32 | 196 | R$ 6.272 |
| Monitoramento e alertas | dba | 8 | 196 | R$ 1.568 |
| Relatório e plano de ação | dba | 4 | 196 | R$ 784 |
| Revisão de acessos | cyber | 4 | 196 | R$ 784 |
| Gestão do projeto | — | 9,6 | — | R$ 1.882 |
| Reserva de risco | — | — | — | R$ 1.443 |
| Impostos | — | — | — | R$ 1.398 |
| **Preço do projeto** | | **73,6 h** | | **R$ 17.300** |

- **Preço**: R$ 17.300 (à vista R$ 16.400; parcelado 40/30/30: R$ 6.920 / R$ 5.190 / R$ 5.190) · R$ 235/h em média · margem estimada 49,4%
- **Mensalidade depois da entrega**: R$ 1.700 (4 h de sustentação + 2 h de evolução); hora adicional R$ 190

### 9. Migração de MySQL 5.7 (sem suporte) para PostgreSQL gerenciado

**Cliente**: Sistema próprio de 15 anos; a aplicação precisa de ajustes.  
**Hospedagem**: Serviço gerenciado (RDS, Cloud SQL, Azure ou OCI) dimensionado pelo DBA  
**Complexidade**: alta

| Item | Perfil | Horas | R$/h | Valor |
|---|---|---:|---:|---:|
| Arquitetura e escolha do serviço | arquiteto | 6 | 213 | R$ 1.278 |
| Inventário e plano de corte | dba | 12 | 196 | R$ 2.352 |
| Conversão de schema e dados (pgloader) | dba | 60 | 196 | R$ 11.760 |
| Validação e ensaio do corte | dba | 24 | 196 | R$ 4.704 |
| Ajustes na aplicação | fullstack | 32 | 170 | R$ 5.440 |
| Banco gerenciado como código (IaC) | devops | 16 | 179 | R$ 2.864 |
| Gestão do projeto | — | 22,5 | — | R$ 4.260 |
| Reserva de risco | — | — | — | R$ 8.164 |
| Impostos | — | — | — | R$ 3.596 |
| **Preço do projeto** | | **172,5 h** | | **R$ 44.500** |

- **Preço**: R$ 44.500 (à vista R$ 42.300; parcelado 40/30/30: R$ 17.800 / R$ 13.350 / R$ 13.350) · R$ 258/h em média · margem estimada 53,2%

### 10. Cliente com Databricks (porte G): Git, CI/CD, Unity Catalog e custos

**Cliente**: 30 notebooks editados direto no workspace, sem governança; gasto de R$ 50 mil/mês em DBUs.  
**Hospedagem**: Databricks existente do cliente (AWS ou Azure)  
**Complexidade**: média

| Item | Perfil | Horas | R$/h | Valor |
|---|---|---:|---:|---:|
| Arquitetura e governança | arquiteto | 16 | 213 | R$ 3.408 |
| Unity Catalog: catálogos, grupos, external locations | plataforma | 16 | 221 | R$ 3.536 |
| Asset Bundles e CI/CD com service principal | plataforma | 16 | 221 | R$ 3.536 |
| Migrar 30 notebooks para Git e bundle | plataforma | 24 | 221 | R$ 5.304 |
| 4 pipelines (Auto Loader / Lakeflow) | plataforma | 48 | 221 | R$ 10.608 |
| Rodada de otimização de custos | plataforma | 12 | 221 | R$ 2.652 |
| Rede e infraestrutura | devops | 8 | 179 | R$ 1.432 |
| Máscaras e acessos (LGPD) | cyber | 8 | 196 | R$ 1.568 |
| Gestão do projeto | — | 22,2 | — | R$ 4.807 |
| Reserva de risco | — | — | — | R$ 5.528 |
| Impostos | — | — | — | R$ 3.733 |
| **Preço do projeto** | | **170,2 h** | | **R$ 46.200** |

- **Preço**: R$ 46.200 (à vista R$ 43.900; parcelado 40/30/30: R$ 18.480 / R$ 13.860 / R$ 13.860) · R$ 271/h em média · margem estimada 55,1%
- **Mensalidade depois da entrega**: R$ 10.050 (28 h de sustentação + 16 h de evolução); hora adicional R$ 190
- **Retorno**: 30% de redução de DBUs sobre R$ 50 mil/mês ≈ R$ 180.000/ano → payback de 3,1 meses

### 11. Implantação de Snowflake com dbt e Git (porte M)

**Cliente**: Distribuidora que escolheu Snowflake; 5 fontes, painéis no Power BI.  
**Hospedagem**: Snowflake na AWS São Paulo (créditos estimados com o FinOps)  
**Complexidade**: média

| Item | Perfil | Horas | R$/h | Valor |
|---|---|---:|---:|---:|
| Arquitetura | arquiteto | 8 | 213 | R$ 1.704 |
| Conta: warehouses, papéis, monitores, rede | plataforma | 16 | 221 | R$ 3.536 |
| Ingestão de 5 fontes | plataforma | 40 | 221 | R$ 8.840 |
| Projeto dbt e CI com par de chaves | plataforma | 24 | 221 | R$ 5.304 |
| Integração Git e migrações | plataforma | 12 | 221 | R$ 2.652 |
| Modelos dbt: 4 fatos | engenheiro | 48 | 170 | R$ 8.160 |
| 4 painéis | analista | 24 | 153 | R$ 3.672 |
| Máscaras e acessos | cyber | 6 | 196 | R$ 1.176 |
| Revisão de custos | plataforma | 8 | 221 | R$ 1.768 |
| Gestão do projeto | — | 27,9 | — | R$ 5.522 |
| Reserva de risco | — | — | — | R$ 6.350 |
| Impostos | — | — | — | R$ 4.282 |
| **Preço do projeto** | | **213,9 h** | | **R$ 53.000** |

- **Preço**: R$ 53.000 (à vista R$ 50.400; parcelado 40/30/30: R$ 21.200 / R$ 15.900 / R$ 15.900) · R$ 248/h em média · margem estimada 51,6%
- **Mensalidade depois da entrega**: R$ 4.650 (12 h de sustentação + 8 h de evolução); hora adicional R$ 190

### 12. Assistente de IA com os documentos da empresa, rodando local

**Cliente**: Cooperativa quer perguntar em português sobre normas, contratos e manuais sem mandar dados para fora.  
**Hospedagem**: ZimaOS (GPU) ou servidor do cliente  
**Complexidade**: média

| Item | Perfil | Horas | R$/h | Valor |
|---|---|---:|---:|---:|
| Casos de uso e conjunto de avaliação | negocios | 8 | 170 | R$ 1.360 |
| Ingestão de documentos (PDF, manuais) | engenheiro | 16 | 170 | R$ 2.720 |
| RAG local: embeddings, Qdrant, avaliação | cientista | 40 | 204 | R$ 8.160 |
| Chat web com login | fullstack | 32 | 170 | R$ 5.440 |
| Implantação no servidor | devops | 12 | 179 | R$ 2.148 |
| LGPD e controle de acesso | cyber | 8 | 196 | R$ 1.568 |
| Gestão do projeto | — | 17,4 | — | R$ 3.209 |
| Reserva de risco | — | — | — | R$ 3.691 |
| Impostos | — | — | — | R$ 2.489 |
| **Preço do projeto** | | **133,4 h** | | **R$ 30.800** |

- **Preço**: R$ 30.800 (à vista R$ 29.300; parcelado 40/30/30: R$ 12.320 / R$ 9.240 / R$ 9.240) · R$ 231/h em média · margem estimada 48,6%
- **Mensalidade depois da entrega**: R$ 2.350 (6 h de sustentação + 4 h de evolução); hora adicional R$ 190
- **Retorno**: horas economizadas em consultas a normas e contratos ≈ R$ 60.000/ano → payback de 6,2 meses (preço acima de 40% do valor anual: reduza o escopo da primeira fase)

### Diagnóstico pago

| Porte | Horas | Preço |
|---|---:|---:|
| P | 16 | R$ 3.000 |
| M | 28 | R$ 5.200 |
| G | 44 | R$ 8.200 |

Abatido do MVP se o cliente fechar em até 30 dias.

### Mensalidade da plataforma gerenciada

| Porte | Horas/mês | Mensalidade | Hora adicional | Margem estimada |
|---|---:|---:|---:|---:|
| P | 10 | R$ 2.350 | R$ 190 | 40,9% |
| M | 20 | R$ 4.650 | R$ 190 | 40,3% |
| G | 44 | R$ 10.050 | R$ 190 | 39,2% |

### Banco de horas

| Horas/mês | Desconto | Mensal | R$/h com impostos |
|---:|---:|---:|---:|
| 20 | 0,0% | R$ 3.700 | R$ 185 |
| 40 | 5,0% | R$ 7.100 | R$ 178 |
| 80 | 10,0% | R$ 13.400 | R$ 168 |

### Uma carteira possível no fim do ano 1

6 clientes gerenciados (4 P, 2 M) e um projeto como o exemplo "transportadora" a cada 2 meses.

| Item | Por mês |
|---|---:|
| Mensalidades (MRR) | R$ 18.700 |
| Projetos (média) | R$ 18.100 |
| **Faturamento** | **R$ 36.800** |
| Impostos (alíquota efetiva com R$ 441.600/ano: 9,5%) | R$ 3.498 |
| Horas de trabalho necessárias | 164 h |
| Custo das horas e ferramentas | R$ 17.995 |
| **Resultado** | **R$ 15.307** |

São 164 h/mês para 120 h produtivas de uma pessoa: faltam ~44 h, que vão para freelancers (o custo já está na conta pela hora interna) ou para os agentes reduzirem.

<!-- exemplos:fim -->

## Como ajustar à sua realidade
- **Taxa base** (`taxa_hora`): R$ 170/h líquida é um meio-termo para PMEs do interior. Consultorias de capitais cobram de R$ 200 a 350/h; freelancers, de R$ 100 a 180/h. Suba quando a agenda encher.
- **Custo interno** (`custo_hora_interno`): some pró-labore, INSS, ferramentas, contador e a parte do servidor, e divida pelas horas que você realmente fatura (cerca de 120 por mês, não 176).
- **Imposto** (`impostos`): atualize `receita_12m` a cada trimestre; com o faturamento crescendo, a alíquota efetiva sobe. Mantenha o Fator R ≥ 28% (pró-labore adequado) para ficar no anexo III.
- **Desconto**: só por pagamento à vista, contrato anual ou banco de horas maior. Nunca abaixo do custo interno; prefira reduzir escopo.
- **Preço por valor**: quando o retorno é muito alto (ex.: redução de inadimplência de milhões), o preço pode subir acima do cálculo por horas; o cálculo é o piso, não o teto.

## Usando no dia a dia (ferramenta MCP)
```text
preco_estimar(tipo="projeto", itens=[{"descricao": "Fonte Protheus", "horas": 40, "perfil": "engenheiro"},
                                     {"descricao": "Painéis", "horas": 20, "perfil": "analista"}],
              complexidade="media", valor_anual=120000)
preco_estimar(tipo="mensalidade", porte="M", infra_brl=850)
preco_estimar(tipo="diagnostico", porte="P")
preco_estimar(tipo="banco_horas", horas_mes=40)
```
O agente Comercial soma as horas que os outros agentes estimaram e chama a ferramenta;
o resultado traz a tabela, as parcelas, a margem e as premissas para a proposta.
