---
sgbd: Redis e Valkey
familia: chave-valor em memória
licenca: Redis 8 com opção AGPLv3 (antes RSALv2/SSPL); Valkey BSD-3
agentes: [fullstack, devops, dba]
revisado: 2026-10
---

# Redis e Valkey

## O que é e quando usar
Armazenamento chave-valor em memória para **cache**, sessões, filas leves, limite de
requisições (rate limit), contadores e pub/sub. Responde em submilissegundos. Não é a
fonte oficial de nenhum dado de negócio: se cair, o sistema deve se reconstruir a partir
do banco principal.

## Versões e licença
- Redis mudou a licença em 2024 (RSALv2/SSPL) e, no Redis 8 (2025), passou a oferecer também AGPLv3.
- **Valkey** é o fork aberto (BSD) mantido pela Linux Foundation, compatível com os comandos do Redis 7.2. AWS e Google oferecem Valkey gerenciado com preço menor que o Redis.
- Para projetos novos sem recursos exclusivos do Redis, Valkey é a escolha padrão.

## Uso na plataforma
- Cache de respostas da API de dados e de consultas caras do BI (com TTL).
- Fila de tarefas para Celery/RQ e para o n8n em modo fila.
- Rate limit por chave de API.
- Busca vetorial: módulos de vetor existem, mas para RAG prefira Qdrant ou pgvector.

## Boas práticas
- Toda chave com TTL, salvo exceções documentadas; `maxmemory` definido e política `allkeys-lru` para cache.
- Nunca `KEYS *` em produção: use `SCAN`.
- Evite chaves enormes (listas ou hashes com milhões de itens): fragmente.
- Persistência: RDB (fotos periódicas) e/ou AOF (log de escrita). Para cache puro, pode desligar.
```bash
redis-cli INFO memory | grep used_memory_human
redis-cli --bigkeys          # encontra chaves grandes
redis-cli SLOWLOG GET 10     # comandos lentos
```

## Alta disponibilidade
- Réplica + Sentinel (failover) ou Cluster (particionamento entre nós). No porte P, uma instância com persistência basta.

## Segurança
- Senha/ACL (`ACL SETUSER`), `protected-mode yes`, nunca exposto na internet; TLS em rede não confiável.

## Na cloud
| Provedor | Serviço |
|---|---|
| AWS | ElastiCache (Valkey, Redis OSS, Memcached), MemoryDB (durável) |
| GCP | Memorystore for Valkey / for Redis |
| Azure | Azure Managed Redis (sucessor do Azure Cache for Redis) |
| OCI | OCI Cache (compatível com Redis e Valkey) |

## Armadilhas
- Usar como banco principal sem persistência e perder dados num reinício.
- Memória acabando por chaves sem TTL.
- Diferenças de licença ao redistribuir Redis dentro de um produto (consulte o jurídico ou use Valkey).

## Documentação oficial
- https://valkey.io/docs/
- https://redis.io/docs/latest/
- https://redis.io/legal/licenses/
