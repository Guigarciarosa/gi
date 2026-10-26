---
sgbd: MongoDB
familia: documentos (NoSQL)
licenca: SSPL (Community); Enterprise e Atlas comerciais
agentes: [dba, engenheiro, fullstack]
revisado: 2026-10
---

# MongoDB

## O que é e quando usar
Banco de documentos JSON (BSON). Comum em apps e SaaS modernos, catálogos de produto
e sistemas com esquema que muda muito. Para a plataforma de dados é fonte: os
documentos são achatados na silver.

## Versões e licença
- 7.0 e 8.0 (2024) são as linhas atuais; confira o fim de vida de cada uma.
- Community sob SSPL (não é considerada aberta pela OSI); **Atlas** é o serviço gerenciado em AWS, Azure e Google, inclusive em São Paulo.

## Conectar e extrair
- Drivers oficiais (`pymongo`), conector do `dlt`, Debezium MongoDB.
- Usuário de leitura:
  ```javascript
  use admin
  db.createUser({ user: "extracao", pwd: passwordPrompt(), roles: [{ role: "read", db: "app" }] })
  ```
- Extração em lote: filtro por `updatedAt` com índice, ou por `_id` (ObjectId é crescente no tempo).
- CDC: **change streams** (exigem replica set ou cluster; um servidor isolado não tem). Guarde o *resume token* para continuar de onde parou. A janela de retomada depende do tamanho do oplog.
- Ler da secundária: `readPreference=secondaryPreferred` para não pesar no primário.

## Desempenho
```javascript
db.setProfilingLevel(1, { slowms: 200 })                 // registra operações acima de 200 ms
db.system.profile.find().sort({ millis: -1 }).limit(10)
db.pedidos.find({ clienteId: 123 }).explain("executionStats")   // procure COLLSCAN
db.currentOp({ active: true, secs_running: { $gt: 5 } })
```
- Índices compostos na ordem igualdade → ordenação → intervalo.
- Cache do WiredTiger usa por padrão cerca de metade da RAM menos 1 GB; em contêiner, limite a memória.

## Backup e alta disponibilidade
- Replica set de 3 membros (ou 2 + árbitro) para HA.
- Backup: snapshot de disco consistente, `mongodump` (bancos pequenos), backup contínuo do Atlas ou Ops Manager.

## Segurança
- Autenticação sempre ligada (`security.authorization: enabled`); nunca exponha a porta 27017 na internet (ainda é causa comum de vazamento).
- TLS, papéis por banco, criptografia em repouso (Atlas e Enterprise).

## Na cloud
| Provedor | Serviço |
|---|---|
| MongoDB | Atlas (multicloud) |
| AWS | Amazon DocumentDB (API compatível com MongoDB; não é 100% igual) |
| Azure | Azure Cosmos DB for MongoDB (RU ou vCore) |
| GCP | Firestore com compatibilidade MongoDB; Atlas no Marketplace |
| OCI | Oracle Database API for MongoDB (Autonomous JSON Database) |

## Armadilhas
- Mesmo campo com tipos diferentes em documentos diferentes (número em um, texto em outro).
- Datas gravadas como texto; valores monetários como `double` (use `Decimal128`).
- Arrays que crescem sem limite dentro de um documento (limite de 16 MB por documento).
- `$lookup` pesado em coleções grandes: modele pensando na consulta.

## Documentação oficial
- https://www.mongodb.com/docs/manual/
- https://www.mongodb.com/docs/manual/changeStreams/
- https://www.mongodb.com/docs/atlas/
- https://debezium.io/documentation/reference/stable/connectors/mongodb.html
