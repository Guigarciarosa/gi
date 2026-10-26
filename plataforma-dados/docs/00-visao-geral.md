# 00 — Visão geral

## O problema
Empresas pequenas e médias querem decidir com dados, mas:
- os números estão espalhados entre ERP, planilhas, CRM e sistemas de terceiros;
- não sabem se precisam de cloud, qual cloud, ou quanto vai custar;
- projetos de dados tradicionais começam caros, demoram e dependem de um time que elas não têm.

Do lado da consultoria, cada cliente novo exige o mesmo trabalho repetitivo de
entendimento do negócio, desenho de arquitetura, estimativa de custo e proposta.

## A solução
Uma plataforma que padroniza e acelera esse trabalho sem perder a personalização:

1. **Discovery estruturado**: um questionário de 231 perguntas em 11 seções, das quais o cliente só vê as que fazem sentido — cada escolha abre ou fecha ramos (150 perguntas condicionais, até 3 níveis de profundidade). Leva de 25 a 40 minutos.
2. **Time de onze agentes** com papéis, métodos e formatos de entrega definidos, que trabalham em sequência e leem o trabalho uns dos outros.
3. **Decisão de infraestrutura com números**: a calculadora compara AWS, GCP, Azure, OCI e on-premise (custo mensal, TCO com operação, câmbio e IOF) e o FinOps valida os preços nas APIs públicas.
4. **Memória que melhora com o tempo**: documentação, respostas, entregáveis e lições de projetos anteriores ficam num banco vetorial e alimentam os próximos clientes.
5. **Infraestrutura própria e barata**: tudo roda no servidor ZimaOS com GPU de 6 GB e 16 GB de RAM; a qualidade alta vem do Claude quando necessário.

## Princípios
- **A pergunta de negócio manda.** Toda peça técnica responde a uma pergunta escrita pelo cliente.
- **O mais simples que funciona.** Porte P não ganha Spark, streaming nem Kubernetes.
- **Números auditáveis.** Contas na calculadora determinística, nunca "de cabeça" no LLM.
- **Portabilidade.** Parquet/Iceberg, dbt, Dagster, OpenTofu: o cliente pode sair de uma cloud ou da consultoria.
- **Humano no fim do fluxo.** Nenhuma proposta sai sem revisão sua.
- **Segurança por padrão.** Isolamento por cliente na memória, no banco e nos backups.

## Quem usa o quê
| Pessoa | Usa | Para |
|---|---|---|
| Cliente | Questionário web (`/?token=...`) | Descrever o negócio e o objetivo |
| Você (consultor) | Claude Desktop/Code conectado ao MCP | Conduzir discovery, acionar agentes, revisar e enviar a proposta |
| Agentes | Ferramentas MCP + memória + calculadora | Produzir os entregáveis |
| Equipe futura | Mesmo MCP, mesmas skills | Escalar sem perder o padrão |

## Entregáveis por cliente
1. Mapa de negócio, KPIs e escopo do MVP
2. Arquitetura-alvo com ADRs e decisão de hospedagem
3. Plano de engenharia (fontes, pipelines, qualidade, esforço)
4. Camada semântica e painéis
5. Casos de IA e plano de experimentos
6. Segurança e LGPD
7. Infraestrutura como código, CI/CD e operação
8. Custos, TCO e otimizações
9. Proposta comercial consolidada
