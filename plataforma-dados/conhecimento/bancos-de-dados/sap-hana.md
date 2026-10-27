---
sgbd: SAP HANA
familia: relacional colunar em memória
licenca: comercial (SAP)
agentes: [dba, engenheiro, arquiteto, finops]
revisado: 2026-10
---

# SAP HANA

## O que é e quando usar
Banco colunar em memória da SAP, obrigatório para o S/4HANA e opcional para o SAP
Business One (que também roda em SQL Server). Rápido para analytics, caro e muito
amarrado ao contrato SAP. Para a plataforma de dados é fonte, e a forma de ler é
decidida pelo **licenciamento**, não pela técnica.

## Versões e licença
- HANA 2.0 (SPS mais recentes) on-premise e **SAP HANA Cloud**.
- **Licença runtime** (vendida junto com aplicações SAP): restringe o acesso direto às tabelas por ferramentas de terceiros. **Full use**: permite uso livre do banco.
- Antes de qualquer conexão, peça ao cliente o tipo de licença e consulte o gerente de contas SAP. É o maior risco jurídico de um projeto de dados com SAP.

## Conectar e extrair
- Drivers: `hdbcli` (Python), JDBC `ngdbc`, ODBC.
- Caminhos usados com SAP ECC e S/4HANA:
  - **CDS Views** com anotações de extração (`@Analytics.dataExtraction.enabled`), expostas por OData ou ODP.
  - **ODP via OData**: a SAP restringiu o uso da API ODP por RFC por ferramentas de terceiros (nota SAP 3255746). Prefira o caminho OData e confirme com o cliente e o parceiro SAP.
  - **SLT** (SAP Landscape Transformation): replicação baseada em triggers, para HANA, Datasphere ou outros destinos licenciados.
  - **SAP Datasphere** com fluxos de replicação para destinos externos (requer licença).
  - Conectores certificados de terceiros (Fivetran, Qlik, Informatica, Azure Data Factory com conector SAP).
- SAP Business One: **Service Layer** (REST) ou, com licença que permita, leitura direta do banco com usuário somente leitura.
- Tabelas clássicas para entender o modelo (ECC/S/4): `VBAK`/`VBAP` (ordens de venda), `VBRK`/`VBRP` (faturamento), `KNA1` (clientes), `LFA1` (fornecedores), `MARA`/`MAKT` (materiais), `EKKO`/`EKPO` (compras), `BKPF`/`BSEG` (contabilidade; no S/4 o diário universal é a `ACDOCA`).

## Desempenho
```sql
-- instruções mais caras no cache de planos
SELECT TOP 20 STATEMENT_STRING, EXECUTION_COUNT, TOTAL_EXECUTION_TIME
FROM M_SQL_PLAN_CACHE ORDER BY TOTAL_EXECUTION_TIME DESC;
-- instruções caras registradas (se o rastreio estiver ligado)
SELECT TOP 20 START_TIME, DURATION_MICROSEC, STATEMENT_STRING FROM M_EXPENSIVE_STATEMENTS ORDER BY DURATION_MICROSEC DESC;
```
- Memória é o recurso caro: monitore `M_SERVICE_MEMORY` e evite extrações que materializam tabelas inteiras.

## Backup e alta disponibilidade
- Backup de dados e de log nativos, para arquivo ou via **Backint** (ferramentas certificadas); *System Replication* para HA e DR.

## Segurança
- Usuários técnicos restritos, papéis por função, auditoria nativa; comunicação cifrada.

## Na cloud
| Opção | Observação |
|---|---|
| SAP HANA Cloud | Gerenciado pela SAP, na infraestrutura de AWS, Azure ou Google |
| RISE with SAP | ERP e HANA como serviço, com regras próprias de acesso aos dados |
| VMs certificadas | AWS, Azure, Google e OCI têm instâncias certificadas para HANA |

## Armadilhas
- Licença runtime e leitura direta das tabelas.
- Volume: tabelas como `ACDOCA` e `BSEG` crescem rápido; extraia por período e por empresa.
- Campos com zeros à esquerda (`MATNR`, `KUNNR`) e datas `AAAAMMDD` em texto.
- Customizações (`Z*`) mudam o significado dos campos: valide com o key user.

## Documentação oficial
- https://help.sap.com/docs/SAP_HANA_PLATFORM
- https://help.sap.com/docs/hana-cloud
- https://help.sap.com/docs/SAP_BUSINESS_ONE
- https://me.sap.com/notes/3255746
