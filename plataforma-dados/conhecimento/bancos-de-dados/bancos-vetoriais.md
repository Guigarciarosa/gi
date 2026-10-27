---
sgbd: Bancos vetoriais (Qdrant, pgvector e alternativas)
familia: vetorial
licenca: varia (ver tabela)
agentes: [cientista, fullstack, arquiteto, dba]
revisado: 2026-10
---

# Bancos vetoriais

## Para que servem
Guardam *embeddings* (vetores que representam o sentido de um texto ou imagem) e
encontram os mais parecidos com uma pergunta. São a base de RAG (assistente que
responde com documentos da empresa), busca semântica, deduplicação de cadastros e
recomendação. A própria plataforma usa o **Qdrant** como memória dos agentes
(`docs/08-memoria-vetorial.md`).

## Opções
| Produto | Licença | Quando escolher |
|---|---|---|
| **Qdrant** | Apache 2.0 | padrão da plataforma: filtros por payload, multi-tenant (`is_tenant`), quantização, roda leve no ZimaOS |
| **pgvector** (PostgreSQL) | PostgreSQL License | até alguns milhões de vetores, quando os dados já estão no Postgres; índice HNSW |
| Milvus / Zilliz | Apache 2.0 / comercial | bilhões de vetores, cluster |
| Weaviate | BSD-3 | módulos de vetorização embutidos |
| Chroma | Apache 2.0 | protótipos locais |
| OpenSearch / Elasticsearch | Apache 2.0 / Elastic | busca híbrida texto + vetor no mesmo índice |
| MongoDB Atlas Vector Search | comercial | dados já no Atlas |
| Oracle 23ai AI Vector Search | incluído no banco | dados já no Oracle/Autonomous |

Serviços de cloud: Azure AI Search, Vertex AI Vector Search, Amazon OpenSearch (k-NN),
AlloyDB e Cloud SQL com pgvector, Amazon S3 Vectors para grandes volumes baratos.

## pgvector na prática
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE trechos (id bigserial PRIMARY KEY, cliente text, origem text, texto text, embedding vector(1024));
CREATE INDEX ON trechos USING hnsw (embedding vector_cosine_ops);
-- busca: 6 trechos mais próximos do vetor da pergunta, só do cliente certo
SELECT origem, texto FROM trechos WHERE cliente = $1 ORDER BY embedding <=> $2 LIMIT 6;
```

## Decisões que importam
- **Modelo de embedding** define a dimensão (bge-m3 = 1024). Trocar de modelo exige reindexar tudo.
- **Fragmentação**: pedaços de 500 a 1.500 caracteres com sobreposição e o título da seção; documentos inteiros recuperam mal.
- **Filtros**: isolamento por cliente obrigatório (filtro por payload ou coluna) — na plataforma, a busca na coleção `clientes` sem cliente é recusada.
- **Busca híbrida** (palavra-chave + vetor) acerta mais em códigos, siglas e nomes de produto.
- **Quantização** (int8, binária) reduz memória em 4× a 32× com pouca perda.
- Avalie com perguntas reais: taxa de acerto do trecho certo entre os 5 primeiros.

## Armadilhas
- Indexar PDFs escaneados sem OCR (vetores de texto vazio).
- Misturar documentos de clientes diferentes sem filtro.
- Não versionar a origem: reindexar a mesma origem deve substituir, não duplicar.

## Documentação oficial
- https://qdrant.tech/documentation/
- https://github.com/pgvector/pgvector
- https://milvus.io/docs
- https://weaviate.io/developers/weaviate
