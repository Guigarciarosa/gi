# Calendário — primeiros 30 dias

Semana 1 publica a grade inicial (9 posts em 4 dias para o perfil não nascer vazio);
depois, 3 posts por semana + reels. Ajuste as datas ao seu início.

| Dia | Formato | Tema | Pilar | Peça / roteiro |
|---|---|---|---|---|
| 1 | Feed | Manifesto | Oferta | `p01` |
| 1 | Feed | 9 especialistas | Bastidores | `p02` |
| 2 | Carrossel | Custo de cloud em 5 lugares | Prova | `p03a–d` |
| 2 | Feed | 3 sinais | Educação | `p04` |
| 3 | Feed | Agro: cooperativa | Educação | `p05` |
| 3 | Feed | Custo por km | Educação | `p06` |
| 4 | Feed | Proteção veicular | Educação | `p07` |
| 4 | Feed | IA sem vazar dados | Educação | `p08` |
| 4 | Feed | Diagnóstico gratuito | Oferta | `p09` |
| 5 | Reel | "Quem sou eu" (30 s) | Bastidores | Roteiro R1 |
| 7 | Stories | Enquete: "Quantos dias leva o seu fechamento?" | Educação | — |
| 8 | Carrossel | 5 KPIs que toda transportadora deveria olhar | Educação | Novo (modelo p06) |
| 10 | Reel | Questionário que se ramifica (tela gravada) | Bastidores | Roteiro R2 |
| 10 | Feed | Planilha não é sistema: 4 riscos | Educação | Novo (modelo p04) |
| 12 | Carrossel | Power BI, Looker Studio ou Metabase? | Educação | Novo |
| 14 | Stories | Caixa de pergunta: "Qual relatório você odeia montar?" | Educação | — |
| 15 | Reel | Servidor em casa com IA local (ZimaOS) | Bastidores | Roteiro R3 |
| 15 | Feed | Sinistralidade explicada em 1 imagem | Educação | Novo (modelo p06) |
| 17 | Carrossel | Cooperativa: do Protheus ao painel em 30 dias | Prova | Novo |
| 19 | Feed | Resposta à pergunta mais votada nos stories | Educação | Novo |
| 21 | Reel | "O FinOps achou uma opção 56% mais barata" (simulação) | Prova | Roteiro R4 |
| 22 | Feed | LGPD para PME em 5 pontos | Educação | Novo (modelo p08) |
| 24 | Carrossel | Quanto custa um MVP de dados (faixas e o que inclui) | Oferta | Novo |
| 26 | Feed | Bastidor: a proposta que os 9 agentes montam | Bastidores | Novo |
| 28 | Reel | 3 perguntas antes de contratar BI | Educação | Roteiro R5 |
| 29 | Feed | Vagas de diagnóstico do mês | Oferta | Reaproveitar `p09` |
| 30 | Stories | Resultados do mês + bastidores | Bastidores | — |

## Roteiros de reels
**R1 — Quem sou eu (30 s)**
1. (0–3 s) Texto na tela: "Eu monto plataformas de dados para empresas do interior." Rosto.
2. (3–15 s) "Sou engenheiro de dados há 7 anos, AWS, Spark, Databricks… e percebi que empresa média paga caro por projeto de dados que demora."
3. (15–25 s) "Criei a Cardume: um time de 9 agentes especialistas que desenha a solução e compara o custo em 4 clouds e no seu servidor."
4. (25–30 s) "Diagnóstico gratuito no link da bio."

**R2 — O questionário que se ramifica (25 s)**
Tela gravada: escolhendo "Logística" → aparecem perguntas de frota e rastreador; marcando "tempo real" → aparece "que decisão depende disso?". Texto: "Cada resposta abre as perguntas certas. 25 minutos e eu entendo a sua empresa."

**R3 — Servidor com IA local (30 s)**
Mostrar o servidor físico, a GPU e o painel do ZimaOS. Texto: "Seus dados sensíveis podem ficar aqui, com IA rodando sem internet." Fechar com o custo de energia por mês.

**R4 — FinOps em ação (30 s)**
Tela da tabela de custos (cenário C de `docs/05`): "Cliente queria AWS. O FinOps mostrou 2,3× o custo da opção mais barata. Resultado: micro-lotes no lugar de streaming." (Deixe claro que é uma simulação.)

**R5 — 3 perguntas antes de contratar BI (20 s)**
"1. Quem vai usar todo dia? 2. A métrica tem uma definição só? 3. Quem atualiza os dados?" Texto final: "Sem isso, o dashboard vira enfeite."

## Antes de cada post
- Revise números e diga quando for simulação.
- Texto alternativo preenchido.
- Guarde o post na memória: `memoria_indexar(texto, colecao="marca", origem="post-AAAA-MM-DD")`.
