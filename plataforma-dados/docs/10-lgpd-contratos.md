# 10 — LGPD e contratos da consultoria

> Orientação operacional, não parecer jurídico. Valide os modelos de contrato com um advogado.

## Papéis
- **Cliente** = controlador dos dados dos titulares (clientes, associados, funcionários dele).
- **Consultoria** = operadora: trata os dados por conta do cliente, conforme instruções.
- **Suboperadores**: provedores usados no tratamento — a cloud escolhida, Cloudflare (túnel), Backblaze/R2 (backup), Anthropic (quando o Claude processa dados do cliente). Liste-os no contrato e avise quando mudarem.

## O que o DPA (acordo de tratamento de dados) precisa ter
1. Objeto, finalidade e tipos de dados tratados (puxe do discovery: `dados.pessoais.tipos`).
2. Instruções do controlador e proibição de uso para outros fins.
3. Medidas de segurança (resumo dos controles do agente Cyber).
4. Lista de suboperadores e local de armazenamento (Brasil/exterior e mecanismo de transferência).
5. Confidencialidade das pessoas com acesso.
6. Apoio ao controlador nos direitos dos titulares e em RIPD.
7. Comunicação de incidentes ao controlador **sem demora**, com as informações necessárias para ele comunicar ANPD e titulares no prazo (3 dias úteis).
8. Devolução e eliminação dos dados ao fim do contrato (prazo e evidência).
9. Direito de auditoria razoável.

## Práticas internas
- **Isolamento**: banco, usuário, coleção vetorial (filtro por cliente) e chave de backup por cliente.
- **Mínimo necessário**: o discovery não pede dados de titulares; amostras para desenvolvimento são mascaradas.
- **IA**: dados de titulares só vão para API de LLM se o cliente autorizou (`ia.llm_privacidade`) e o contrato do provedor não usa os dados para treino; senão, modelo local.
- **Acesso**: MFA em tudo (Google, clouds, ZimaOS, GitHub, Cloudflare); token do MCP rotacionado a cada 90 dias.
- **Registro**: log de acesso aos dados dos clientes; inventário de tratamentos (por cliente) atualizado a cada projeto.
- **Retenção**: dados do cliente só enquanto o contrato durar + prazo combinado; entregáveis e lições anonimizados podem ficar (sem dados pessoais).
- **Conteúdo do Instagram**: nunca mostrar dados reais de clientes; casos só com autorização por escrito e números agregados.

## Cláusulas comerciais ligadas a dados
- Propriedade: dados e código do projeto pertencem ao cliente; aceleradores da consultoria (questionário, agentes, skills) são licenciados.
- Saída: repositório, documentação e dados em formato aberto entregues no encerramento.
- Responsabilidade proporcional ao papel de operadora; seguro de responsabilidade cibernética quando a carteira crescer.
