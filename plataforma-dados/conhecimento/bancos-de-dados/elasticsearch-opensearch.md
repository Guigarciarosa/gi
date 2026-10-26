---
sgbd: Elasticsearch e OpenSearch
familia: busca e análise de texto (documentos)
licenca: Elasticsearch com Elastic License, SSPL ou AGPLv3; OpenSearch Apache 2.0
agentes: [arquiteto, engenheiro, fullstack, devops]
revisado: 2026-10
---

# Elasticsearch e OpenSearch

## O que é e quando usar
Motores de busca com índice invertido: busca textual com relevância, filtros
facetados (catálogo de produtos, base de conhecimento), logs e observabilidade.
Fazem agregações rápidas, mas **não** são banco principal: os dados de negócio ficam
no banco transacional e são copiados para o índice. O OpenSearch é o fork aberto
criado a partir do Elasticsearch 7.10, hoje mantido pela OpenSearch Software Foundation (Linux Foundation).

## Versões e licença
- Elasticsearch 8.x e 9.x; desde 2024 a Elastic oferece AGPLv3 além da Elastic License e da SSPL.
- OpenSearch 2.x e 3.x, Apache 2.0.

## Uso na plataforma
- Busca no portal do cliente (produtos, documentos, chamados).
- Logs de aplicação e de pipelines (alternativa: Loki).
- Busca híbrida (texto + vetor) para RAG: ambos têm vetores (k-NN no OpenSearch, `dense_vector` no Elasticsearch). Para RAG simples, Qdrant ou pgvector bastam.

## Boas práticas
- Defina o *mapping* explicitamente (não deixe tudo virar `text` + `keyword` automático).
- Analisador `brazilian` (ou `portuguese`) para stemming e stopwords em português.
- Shards de 10 a 50 GB; poucos shards em índices pequenos.
- Heap da JVM em até metade da RAM e abaixo de ~31 GB.
- Ciclo de vida dos índices: ILM (Elasticsearch) ou ISM (OpenSearch) para logs.
```bash
curl -s localhost:9200/_cluster/health?pretty
curl -s 'localhost:9200/_cat/indices?v&s=store.size:desc' | head
```

## Extração
- Exportar: `search_after` com *point in time* (PIT); o `scroll` antigo ainda funciona.
- Snapshots para repositório S3/GCS/Azure são o backup oficial.

## Segurança
- Autenticação e TLS ligados (padrão no Elasticsearch 8+); no OpenSearch, plugin de segurança.
- Nunca exponha a porta 9200 na internet.

## Na cloud
| Provedor | Serviço |
|---|---|
| Elastic | Elastic Cloud (AWS, Azure, GCP), Elastic Serverless |
| AWS | Amazon OpenSearch Service (com opção Serverless) |
| Azure | Elastic Cloud nativo no Azure; Azure AI Search como alternativa |
| GCP | Elastic Cloud no Marketplace; Vertex AI Search como alternativa |
| OCI | OCI Search with OpenSearch |

## Armadilhas
- Usar como fonte da verdade e perder dados numa reindexação.
- Mapping dinâmico criando milhares de campos ("mapping explosion").
- Atualizações frequentes por documento custam caro (cada update reescreve o documento).

## Documentação oficial
- https://www.elastic.co/docs
- https://opensearch.org/docs/latest/
- https://www.elastic.co/docs/manage-data/lifecycle/index-lifecycle-management
