---
tema: bancos de dados dos ERPs e sistemas comuns no Brasil
agentes: [dba, engenheiro, analista, negocios]
revisado: 2026-10
---

# Bancos de dados dos ERPs brasileiros

Nomes de tabelas abaixo são os mais usados e servem de ponto de partida. Cada cliente
tem versão, módulos e customizações próprias: confirme com o key user e com o
dicionário de dados do sistema antes de construir modelos.

## Resumo
| Sistema | Bancos suportados | Como ler | Observação |
|---|---|---|---|
| TOTVS Protheus | SQL Server, Oracle, PostgreSQL | banco (réplica ou janela) ou API REST | tabelas com sufixo da empresa (`SA1010`) |
| TOTVS RM | SQL Server, Oracle | banco ou consultas SQL cadastradas via API | prefixo indica o módulo |
| TOTVS Datasul | Progress OpenEdge (SQL via ODBC) | ODBC no broker SQL, réplica Pro2 | nomes com hífen, vários bancos por área |
| TOTVS Logix | conforme a instalação (Informix, Oracle, SQL Server) | banco | confirme o SGBD com o cliente |
| TOTVS WinThor (distribuição) | Oracle | banco | tabelas com prefixo `PC` |
| Senior (Gestão Empresarial e HCM) | SQL Server, Oracle | banco ou APIs da plataforma Senior X | tabelas `E` (ERP) e `R` (HCM) |
| Sankhya | Oracle, SQL Server | banco ou API Sankhya-W | tabelas `TGF*` |
| SAP Business One | SQL Server, SAP HANA | Service Layer (REST) ou banco | tabelas com `O` (cabeçalho) e linhas numeradas |
| SAP ECC / S/4HANA | HANA (S/4), outros no ECC | OData/CDS, SLT, conectores certificados | ver `sap-hana.md` (licença) |
| Omie, Bling, Tiny/Olist, Conta Azul | SaaS | só API | limite de requisições por minuto |
| Hospitalares (Tasy, MV) | Oracle | visões fornecidas pelo fornecedor | dados de saúde: LGPD art. 11 |

## TOTVS Protheus
- Nome físico = alias + código da empresa + `0`: `SA1010` é a tabela de clientes da empresa 01.
- Campos de controle: `D_E_L_E_T_` (`'*'` = excluído lógico; filtre sempre), `R_E_C_N_O_` (número do registro), `R_E_C_D_E_L_` (em tabelas com índice único), filial em `<prefixo>_FILIAL`.
- Datas como texto `AAAAMMDD`; valores em `FLOAT`.
- Dicionário: `SX2` (tabelas) e `SX3` (campos, com título e descrição em português) — use para documentar a bronze automaticamente.
- Tabelas frequentes:
  | Assunto | Tabelas |
  |---|---|
  | Cadastros | `SA1` clientes, `SA2` fornecedores, `SB1` produtos, `SA3` vendedores, `CTT` centros de custo, `SED` naturezas |
  | Vendas | `SC5`/`SC6` pedidos e itens, `SF2`/`SD2` notas de saída e itens, `DA0`/`DA1` tabelas de preço |
  | Compras | `SC7` pedidos de compra, `SF1`/`SD1` notas de entrada e itens |
  | Estoque | `SB2` saldos por armazém, `SD3` movimentos internos, `SF4` tipos de entrada e saída (TES) |
  | Financeiro | `SE1` contas a receber, `SE2` contas a pagar, `SE5` movimentação bancária |
  | Contabilidade | `CT1` plano de contas, `CT2` lançamentos |
  | Folha | `SRA` funcionários, `SRC`/`SRD` movimentos da folha |
- Incremental: `S_T_A_M_P_` e `I_N_S_D_T_` quando habilitados no DBAccess; senão, datas de emissão e baixa com reconciliação semanal. `R_E_C_N_O_` não detecta alteração.
- Gravação no Protheus: sempre pelas APIs (REST/TLPP) ou rotinas do próprio sistema, nunca direto no banco.

## TOTVS RM
- Prefixos por módulo: `G` global (`GCOLIGADA`, `GFILIAL`), `F` financeiro (`FCFO` clientes/fornecedores, `FLAN` lançamentos), `T` estoque/compras/faturamento (`TMOV` movimentos, `TITMMOV` itens, `TPRD` produtos), `P` folha (`PFUNC` funcionários, `PFFINANC` ficha financeira), `S` educacional (`SALUNO`, `SMATRICPL`).
- Chave composta por coligada (`CODCOLIGADA`) em quase todas as tabelas.
- Sem acesso ao banco: consultas SQL cadastradas no RM (`GCONSSQL`) executadas pela API.

## TOTVS Datasul
- Progress OpenEdge, acesso SQL pelo esquema `PUB` (ver `progress-openedge.md`).
- Tabelas frequentes do EMS 2: `emitente` (clientes e fornecedores), `item`, `estabelec`, `ped-venda`, `ped-item`, `nota-fiscal`, `it-nota-fisc`, `saldo-estoq`, `movto-estoq`, `ord-prod`. No financeiro do EMS 5 aparecem nomes com sublinhado (`tit_acr` a receber, `tit_ap` a pagar).
- Muitos clientes já replicam o Datasul para SQL Server com o Pro2: pergunte antes de abrir o ODBC.

## TOTVS WinThor
- Oracle, tabelas com prefixo `PC`: `PCCLIENT` clientes, `PCPRODUT` produtos, `PCPEDC`/`PCPEDI` pedidos, `PCNFSAID` notas de saída, `PCMOV` movimentação, `PCEST` estoque, `PCPREST` títulos a receber, `PCLANC` lançamentos a pagar, `PCUSUARI` vendedores (RCA).

## Senior
- Gestão Empresarial: `E070EMP` empresas, `E070FIL` filiais, `E085CLI` clientes, `E095FOR` fornecedores, `E075PRO` produtos, `E120PED`/`E120IPD` pedidos e itens, `E140NFV`/`E140IPV` notas de saída e itens, `E301TCR` títulos a receber, `E501TCP` títulos a pagar.
- HCM: `R034FUN` colaboradores (dados pessoais: aplique os controles do Cyber).

## Sankhya
- `TGFCAB` cabeçalho de notas e pedidos (o tipo vem de `TGFTOP`), `TGFITE` itens, `TGFPAR` parceiros, `TGFPRO` produtos, `TGFFIN` financeiro, `TGFEST` estoque, `TGFVEN` vendedores, `TSIEMP` empresas.
- Campo `NUNOTA` liga cabeçalho e itens; `DTNEG` e `DTMOV` são as datas mais usadas.

## SAP Business One
- `OCRD` parceiros, `OITM` itens, `OITW` estoque por depósito, `OWHS` depósitos, `ORDR`/`RDR1` pedidos de venda, `OINV`/`INV1` notas de saída, `ORIN` devoluções, `OPCH`/`PCH1` notas de entrada, `OJDT`/`JDT1` lançamentos, `OACT` plano de contas.
- Service Layer (REST, porta 50000 por padrão) para leitura e escrita suportadas.

## ERPs SaaS (Omie, Bling, Tiny/Olist, Conta Azul)
- Só API: paginação, limite por minuto (trate `429` com espera), filtro por data de alteração guardado no estado do `dlt`.
- Exportações manuais (planilha) não são fonte confiável: use a API.

## Perguntas para o key user (vale para todos)
1. Quantas empresas e filiais existem no sistema e quais entram no projeto?
2. O que é "venda" para a diretoria: pedido, nota emitida ou nota com devolução descontada?
3. Quais campos foram customizados ou são usados de forma diferente do padrão?
4. Existe réplica, backup restaurável ou ambiente de homologação para leitura?
5. Quem autoriza o acesso ao banco: o cliente, o fornecedor do ERP ou os dois?

## Documentação oficial
- https://tdn.totvs.com/
- https://centraldeatendimento.totvs.com/
- https://documentacao.senior.com.br/
- https://ajuda.sankhya.com.br/
- https://help.sap.com/docs/SAP_BUSINESS_ONE
