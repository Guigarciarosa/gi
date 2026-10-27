---
plataforma: Oracle Cloud Infrastructure (OCI)
tema: bancos de dados gerenciados
agentes: [dba, arquiteto, finops, engenheiro, devops]
revisado: 2026-10
---

# Bancos de dados na Oracle Cloud (OCI)

## Mapa de serviços
| Categoria | Serviço | Quando usar |
|---|---|---|
| Oracle autônomo | **Autonomous Database**: Transaction Processing (ATP), Data Warehouse (ADW), JSON, APEX | banco Oracle sem DBA operacional; ADW como warehouse |
| Oracle "clássico" | Base Database Service (VM), Exadata Database Service, Exadata Cloud@Customer | migrar Oracle on-premise mantendo controle |
| MySQL | **MySQL HeatWave** (MySQL com acelerador analítico e de ML em memória) | apps MySQL com consultas analíticas |
| PostgreSQL | OCI Database with PostgreSQL | apps e banco da plataforma |
| NoSQL | OCI NoSQL Database | chave-valor/documentos serverless |
| Cache | OCI Cache (compatível com Redis/Valkey) | cache e sessões |
| Busca | OCI Search with OpenSearch | busca e logs |
| CDC e replicação | **OCI GoldenGate** (gerenciado) | replicar Oracle, SQL Server, PostgreSQL, MySQL para ADW, Object Storage, Kafka |
| Migração | OCI Database Migration, Zero Downtime Migration (ZDM) | levar Oracle on-premise para a OCI |

Regiões no Brasil: São Paulo e Vinhedo. A OCI cobra o mesmo preço em todas as regiões.

## Always Free (confira as condições vigentes)
- 2 Autonomous Databases com até 20 GB cada.
- Computação Ampere A1 (4 OCPUs e 24 GB de RAM no total), 200 GB de block storage, 10 TB/mês de saída.
- Um porte P inteiro pode rodar de graça: PostgreSQL ou DuckDB numa VM A1 + Autonomous Data Warehouse para a gold.

## Escolhas por porte
- **P**: Always Free (ADW 20 GB ou VM A1) + Metabase/Superset na VM.
- **M**: ADW com 2 ECPUs e parada agendada fora do horário; PostgreSQL gerenciado para apps.
- **G**: ADW com auto scaling, Exadata para Oracle grande; GoldenGate para CDC.

## Armadilhas de custo e licença
- Autonomous: escolha **BYOL** se o cliente já tem licenças Oracle com suporte em dia (custo bem menor que licença incluída).
- Agende parada do ADW/ATP fora do horário comercial (cobra por ECPU-hora ligada).
- GoldenGate cobra por hora de OCPU/ECPU: dimensione pelo volume de mudanças.
- Exadata tem custo mínimo de infraestrutura alto: só para porte G ou consolidação de vários bancos.

## Leitura sem impacto e CDC
- Autonomous Data Guard (standby) e *refreshable clones* para leitura.
- GoldenGate do Oracle on-premise para ADW ou Object Storage.
- Data Pump para o Object Storage para cargas históricas.

## Segurança
- Private endpoint, Vault para segredos e chaves, Data Safe (avaliação de segurança, mascaramento, auditoria) incluso para bancos Oracle na OCI, criptografia por padrão.

## Documentação oficial
- https://docs.oracle.com/en/cloud/paas/autonomous-database/
- https://docs.oracle.com/en-us/iaas/mysql-database/
- https://docs.oracle.com/en-us/iaas/Content/postgresql/home.htm
- https://docs.oracle.com/en/cloud/paas/goldengate-service/
- https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier.htm
- https://www.oracle.com/cloud/price-list/
