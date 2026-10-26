"""Registro dos 11 agentes: quem são, em que ordem trabalham e o que cada um lê.

O conteúdo de cada agente (papel, método, formato de entrega) vive em
`agentes/<pasta>/AGENT.md`, e o conhecimento técnico em
`skills/<pasta>/SKILL.md` (+ referências). Este módulo só sabe a ordem, as
dependências e como montar o contexto.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Agente:
    id: str
    nome: str
    pasta: str
    entrega: str
    depende_de: tuple[str, ...] = ()
    consultas_rag: tuple[str, ...] = ()
    usa_custos: bool = False
    ordem: int = 0
    # Arquivos de conhecimento/ que acompanham a skill do agente (padrões glob a partir da raiz).
    conhecimento: tuple[str, ...] = ()


AGENTES: tuple[Agente, ...] = (
    Agente("negocios", "Analista de Negócios", "analista-negocios",
           "Mapa do negócio, KPIs e requisitos priorizados",
           consultas_rag=("modelo de negócio KPIs por segmento", "requisitos e histórias de usuário de dados"), ordem=1),
    Agente("arquiteto", "Arquiteto de Dados", "arquiteto-dados",
           "Arquitetura-alvo, decisão de hospedagem e modelagem",
           depende_de=("negocios",),
           consultas_rag=("arquitetura medalhão lakehouse porte pequeno médio grande", "matriz de decisão cloud on-premise",
                          "comparativo de SGBDs quando usar cada banco"),
           usa_custos=True, ordem=2,
           conhecimento=("conhecimento/bancos-de-dados/comparativo-sgbds.md",)),
    Agente("dba", "DBA", "dba",
           "Inventário de bancos, método de leitura sem impacto, backup/HA, desempenho e licenças",
           depende_de=("negocios", "arquiteto"),
           consultas_rag=("réplica de leitura CDC usuário somente leitura banco do ERP",
                          "backup restauração alta disponibilidade RPO RTO banco de dados"),
           ordem=3,
           conhecimento=("conhecimento/bancos-de-dados/*.md",)),
    Agente("engenheiro", "Engenheiro de Dados", "engenheiro-dados",
           "Plano de ingestão, pipelines, qualidade e integrações",
           depende_de=("negocios", "arquiteto", "dba"),
           consultas_rag=("conectores ERP TOTVS SAP ingestão incremental CDC", "dbt dlt orquestração testes de qualidade",
                          "Databricks Snowflake Git CI/CD"),
           ordem=4,
           conhecimento=("conhecimento/bancos-de-dados/cdc-por-sgbd.md", "conhecimento/bancos-de-dados/erps-bancos-de-dados.md")),
    Agente("analista", "Analista de Dados", "analista-dados",
           "Camada semântica, catálogo de métricas e dashboards",
           depende_de=("negocios", "arquiteto", "engenheiro"),
           consultas_rag=("catálogo de métricas camada semântica", "boas práticas de dashboards executivos"), ordem=5),
    Agente("cientista", "Cientista de Dados", "cientista-dados",
           "Casos de IA/ML, viabilidade e plano de experimentos",
           depende_de=("negocios", "arquiteto", "engenheiro"),
           consultas_rag=("casos de uso de machine learning por segmento", "LLM local GPU 6 GB RAG agentes"), ordem=6,
           conhecimento=("conhecimento/bancos-de-dados/bancos-vetoriais.md",)),
    Agente("fullstack", "Desenvolvedor Full Stack", "desenvolvedor-fullstack",
           "Aplicações, portais, API de dados e analytics embutido",
           depende_de=("negocios", "arquiteto", "dba", "engenheiro", "analista"),
           consultas_rag=("embedded analytics segurança por linha Metabase Superset Power BI Embedded",
                          "API de dados autenticação multi-tenant portal do cliente"),
           ordem=7,
           conhecimento=("conhecimento/bancos-de-dados/postgresql.md", "conhecimento/bancos-de-dados/redis-valkey.md",
                         "conhecimento/bancos-de-dados/bancos-vetoriais.md")),
    Agente("cyber", "Cybersecurity", "cybersecurity",
           "Ameaças, LGPD, controles e plano de segurança",
           depende_de=("arquiteto", "dba", "engenheiro", "fullstack"),
           consultas_rag=("LGPD dados sensíveis controles", "segurança cloud IAM criptografia backup ransomware"), ordem=8,
           conhecimento=("conhecimento/bancos-de-dados/seguranca-de-bancos.md",)),
    Agente("devops", "DevOps", "devops",
           "Infraestrutura como código, CI/CD, observabilidade e operação",
           depende_de=("arquiteto", "dba", "engenheiro", "fullstack", "cyber"),
           consultas_rag=("terraform módulos AWS GCP Azure OCI", "docker compose ZimaOS observabilidade backup"), ordem=9,
           conhecimento=("conhecimento/bancos-de-dados/backup-e-alta-disponibilidade.md",)),
    Agente("finops", "FinOps", "finops",
           "Custo por cloud, TCO, otimizações e governança de gastos",
           depende_de=("arquiteto", "dba", "engenheiro", "fullstack", "devops", "cientista"),
           consultas_rag=("otimização de custos savings plans reservas", "free tier OCI Always Free BigQuery",
                          "licenciamento SQL Server Oracle na cloud"),
           usa_custos=True, ordem=10),
    Agente("comercial", "Comercial", "comercial",
           "Proposta comercial, escopo, cronograma e preço",
           depende_de=("negocios", "arquiteto", "dba", "engenheiro", "analista", "cientista", "fullstack", "cyber", "devops", "finops"),
           consultas_rag=("precificação de serviços de dados pacotes exemplos", "objeções comerciais e ROI"), ordem=11),
)
POR_ID = {a.id: a for a in AGENTES}
ORDEM_PIPELINE = tuple(a.id for a in sorted(AGENTES, key=lambda a: a.ordem))


# Rótulos usados para buscar, na memória, a documentação do que o cliente usa.
BANCOS = {
    "sqlserver": "SQL Server", "oracle": "Oracle Database", "postgres": "PostgreSQL",
    "progress": "Progress OpenEdge", "firebird": "Firebird", "mysql": "MySQL MariaDB",
    "hana": "SAP HANA", "mongodb": "MongoDB", "dynamodb_firestore": "DynamoDB Firestore Cosmos DB",
}
ERPS = {
    "sap": "SAP", "protheus": "TOTVS Protheus", "rm": "TOTVS RM", "datasul": "TOTVS Datasul",
    "senior": "Senior", "sankhya": "Sankhya", "oracle": "Oracle EBS JD Edwards", "dynamics": "Dynamics 365",
}
PLATAFORMAS = {
    "databricks": "Databricks", "snowflake": "Snowflake", "bigquery": "BigQuery", "redshift": "Redshift",
    "fabric_synapse": "Microsoft Fabric Synapse", "oracle_adw": "Autonomous Data Warehouse",
}


def _lista(v: object) -> list[str]:
    if v is None or v == "":
        return []
    return [str(x) for x in v] if isinstance(v, list) else [str(v)]


def consultas_do_cliente(agente: Agente, respostas: dict[str, object], limite: int = 6) -> list[str]:
    """Consultas extras à memória a partir dos bancos, ERP e plataformas que o cliente usa,
    para que o DBA e o Engenheiro leiam a documentação certa de cada um."""
    if agente.id not in ("dba", "engenheiro"):
        return []
    bancos = dict.fromkeys(_lista(respostas.get("dados.erp.banco")) + _lista(respostas.get("dados.bd.tipos")))
    consultas = []
    for b in bancos:
        if b in BANCOS:
            foco = "backup desempenho licença" if agente.id == "dba" else "extração incremental CDC"
            consultas.append(f"{BANCOS[b]} usuário somente leitura {foco}")
    erp = str(respostas.get("dados.erp.sistema", ""))
    if erp in ERPS:
        consultas.append(f"{ERPS[erp]} banco de dados tabelas principais")
    for p in _lista(respostas.get("infra.plataforma_dados")):
        if p in PLATAFORMAS:
            foco = "segurança e custos" if agente.id == "dba" else "Git CI/CD ingestão"
            consultas.append(f"{PLATAFORMAS[p]} {foco}")
    return consultas[:limite]


def resolver(agente: str) -> Agente:
    chave = agente.strip().lower()
    if chave in POR_ID:
        return POR_ID[chave]
    for a in AGENTES:
        if chave in (a.pasta, a.nome.lower()):
            return a
    raise KeyError(f"Agente desconhecido: {agente}. Disponíveis: {', '.join(POR_ID)}")


def _ler(caminho: Path) -> str:
    return caminho.read_text(encoding="utf-8") if caminho.exists() else ""


def _sem_frontmatter(texto: str) -> str:
    return re.sub(r"\A---\n.*?\n---\n", "", texto, flags=re.S).strip()


@dataclass
class Perfil:
    agente: Agente
    papel: str
    skill: str
    referencias: list[str] = field(default_factory=list)


def carregar_perfil(raiz: Path, agente: str) -> Perfil:
    a = resolver(agente)
    papel = _ler(raiz / "agentes" / a.pasta / "AGENT.md")
    skill_dir = raiz / "skills" / a.pasta
    skill = _sem_frontmatter(_ler(skill_dir / "SKILL.md"))
    refs = sorted(str(p.relative_to(raiz)) for p in (skill_dir / "references").glob("*.md")) if (skill_dir / "references").exists() else []
    refs += arquivos_conhecimento(raiz, a)
    return Perfil(agente=a, papel=papel, skill=skill, referencias=refs)


def arquivos_conhecimento(raiz: Path, agente: Agente) -> list[str]:
    vistos: dict[str, None] = {}
    for padrao in agente.conhecimento:
        for p in sorted(raiz.glob(padrao)):
            vistos[str(p.relative_to(raiz))] = None
    return list(vistos)


def cortar(texto: str, limite: int) -> str:
    if len(texto) <= limite:
        return texto
    return texto[:limite].rsplit("\n", 1)[0] + "\n\n[… cortado para caber no contexto …]"
