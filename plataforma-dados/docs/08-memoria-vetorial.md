# 08 — Memória vetorial

## Por que um banco vetorial
Os agentes precisam lembrar de três coisas que não cabem no prompt: a documentação
técnica (skills, guias de cloud), o histórico de cada cliente (respostas e
entregáveis) e o que aprendemos em projetos anteriores. O Qdrant guarda tudo isso como
vetores e devolve os trechos mais relevantes para cada agente.

## Coleções
| Coleção | O que guarda | Quem grava | Quem lê | Filtro obrigatório |
|---|---|---|---|---|
| `conhecimento` | `docs/`, `agentes/`, `skills/`, `conhecimento/` e a documentação oficial baixada | `memoria_reindexar_base`, `conhecimento_baixar` | Todos os agentes (consultas de cada um em `agentes.py`, mais as dos bancos, ERP e plataforma do cliente) | — |
| `clientes` | Resumo do discovery e cada entregável | Automático ao salvar discovery/entregável | Agentes do mesmo cliente | `cliente` |
| `projetos` | Lições aprendidas, custo estimado × real, decisões que funcionaram | Você, ao encerrar um projeto | Agentes de clientes do mesmo segmento | — |
| `marca` | Posts publicados, tom de voz, identidade visual | Você/Comercial | Comercial e quem produz conteúdo | — |

### Payload de cada ponto
```json
{
  "texto": "trecho fragmentado",
  "origem": "skills/finops/SKILL.md | discovery | entregavel:arquiteto | <slug>-licoes",
  "trecho": 3,
  "tipo": "skills | docs | agentes | conhecimento | oficial | discovery | entregavel | licao | post",
  "cliente": "cooperativa-oeste",
  "agente": "arquiteto"
}
```
Índices de payload: `cliente` (keyword, **tenant**), `origem`, `tipo`.

## Como os agentes aprendem
Três camadas, da mais curada para a mais ampla:

1. **Base curada** em `conhecimento/bancos-de-dados/` (um arquivo por SGBD, bancos de AWS,
   GCP, Azure e OCI, bancos dos ERPs, CDC, backup, segurança, desempenho, migração) e nas
   referências das skills (Databricks, Snowflake, Git). Cada agente tem os seus arquivos
   em `agentes.py` (`conhecimento`), que entram no perfil e no pacote da skill.
   `memoria_reindexar_base` indexa tudo.
2. **Documentação oficial**: cada arquivo termina com "## Documentação oficial".
   `conhecimento_fontes` lista as fontes; `conhecimento_baixar("postgresql", max_paginas=30)`
   baixa as páginas (mesmo site e mesma pasta, respeitando o robots.txt), grava em
   `/data/conhecimento-oficial/<fonte>/` e indexa com `tipo=oficial`. Fora do servidor:
   `python scripts/baixar_docs_oficiais.py --listar` e `--todas`.
3. **Consultas pelo cliente**: no pipeline, o DBA e o Engenheiro buscam na memória os
   trechos dos bancos, ERP e plataforma que o cliente marcou no questionário
   (`consultas_do_cliente`), além das consultas fixas de cada agente.

Revise a base curada a cada 6 meses (campo `revisado` no cabeçalho) e baixe de novo a
documentação oficial depois de versões novas dos bancos.

## Isolamento entre clientes
- Uma coleção `clientes` para todos, com `cliente` marcado como tenant (o Qdrant otimiza o armazenamento por inquilino).
- `MemoriaVetorial.buscar` **recusa** buscar em `clientes` sem o cliente (teste automatizado garante).
- IDs determinísticos (`uuid5(coleção | cliente | origem | trecho)`): reindexar a mesma origem substitui a versão anterior em vez de duplicar.

## Embeddings
- Padrão: `bge-m3` (multilíngue, 1024 dimensões, muito bom em português), servido pelo Ollama na GPU.
- Alternativa leve: `nomic-embed-text` (768 dimensões).
- Para testes sem GPU: `MODELO_EMBEDDING=hash` (hashing de palavras, sem modelo).
- **Trocar de modelo exige apagar as coleções e reindexar** (a dimensão muda).

## Fragmentação
Markdown é quebrado por títulos (`#` a `####`), seções curtas são unidas à seguinte,
e seções longas viram pedaços de ~1.200 caracteres com 150 de sobreposição, repetindo
o título da seção no início de cada pedaço.

## Tamanho e desempenho
- Vetores em disco, cópia quantizada em int8 na RAM: 100 mil trechos × 1024 dimensões ≈ 100 MB de RAM.
- A base inicial (docs + agentes + skills) gera algumas centenas de trechos.
- Cada cliente acrescenta dezenas de trechos por rodada de agentes.

## Operações
| Ação | Como |
|---|---|
| Reindexar documentação | `memoria_reindexar_base` |
| Aprender com a documentação oficial | `conhecimento_fontes`, depois `conhecimento_baixar(fonte, max_paginas=30)` |
| Guardar lição de projeto | `memoria_indexar(texto, colecao="projetos", origem="<slug>-licoes", tipo="licao")` |
| Guardar post publicado | `memoria_indexar(texto, colecao="marca", origem="post-2026-11-03", tipo="post")` |
| Buscar | `memoria_buscar("custo de NAT gateway", colecao="conhecimento")` |
| Estatísticas | `plataforma_saude` (contagem por coleção) |
| Painel web | descomente a porta 6333 no compose e abra `/dashboard` |
| Backup | snapshot por coleção ou backup da pasta `/DATA/AppData/plataforma/qdrant` |

## Modelo de lição aprendida (coleção `projetos`)
```markdown
# Lições — <cliente> (<segmento>, porte <P/M/G>)
- Cloud escolhida e por quê:
- Custo estimado × real (3 meses):
- Fontes e conectores que deram trabalho:
- O que o cliente mais usou:
- O que eu faria diferente:
- Reaproveitável em outros clientes:
```
