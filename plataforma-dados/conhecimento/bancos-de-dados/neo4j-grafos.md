---
sgbd: Neo4j e bancos de grafos
familia: grafo
licenca: Neo4j Community GPLv3; Enterprise e AuraDB comerciais
agentes: [cientista, arquiteto, engenheiro]
revisado: 2026-10
---

# Neo4j e bancos de grafos

## O que é e quando usar
Bancos de grafos guardam nós (pessoas, veículos, contas) e relações (indicou, pagou,
usou o mesmo telefone). Brilham quando a pergunta é sobre **conexões**: anéis de
fraude em sinistros de proteção veicular, redes de indicação, rotas, dependências,
recomendação. Para a maioria dos painéis, SQL basta; o grafo entra para um caso de uso
específico do Cientista.

## Opções
| Produto | Linguagem | Observação |
|---|---|---|
| Neo4j | Cypher (e GQL, padrão ISO de 2024) | o mais conhecido; Community grátis, Enterprise e AuraDB pagos |
| Amazon Neptune | openCypher, Gremlin, SPARQL | gerenciado na AWS; Neptune Analytics para análises |
| Azure Cosmos DB for Apache Gremlin | Gremlin | gerenciado no Azure |
| Spanner Graph (GCP) | GQL/SQL | grafo dentro do Spanner |
| Oracle Database 23ai | SQL/PGQ (grafos de propriedades em SQL) | incluído no banco |
| Apache AGE (PostgreSQL) | openCypher dentro do Postgres | bom para começar sem novo banco |

## Exemplo (fraude em sinistros)
```cypher
// associados que compartilham telefone ou endereço com quem já teve sinistro negado por fraude
MATCH (a:Associado)-[:USA]->(c:Contato)<-[:USA]-(b:Associado)-[:ABRIU]->(s:Sinistro {status: 'negado_fraude'})
WHERE a <> b
RETURN a.id, count(DISTINCT b) AS ligacoes_suspeitas
ORDER BY ligacoes_suspeitas DESC LIMIT 50;
```

## Carga e extração
- Carregue da gold da plataforma (CSV/Parquet) com `LOAD CSV`, `neo4j-admin database import` (carga inicial em massa) ou o conector Spark.
- Exporte resultados (pontuações, comunidades) de volta para a gold para aparecer nos painéis.
- Biblioteca Graph Data Science (Neo4j): centralidade, comunidades (Louvain), similaridade.

## Armadilhas
- Modelar tudo como grafo "porque sim": aumenta custo e complexidade.
- Nós "super conectados" (um CEP com milhares de pessoas) deixam consultas lentas; filtre ou agrupe.

## Documentação oficial
- https://neo4j.com/docs/
- https://neo4j.com/docs/cypher-manual/current/
- https://docs.aws.amazon.com/neptune/
- https://age.apache.org/
