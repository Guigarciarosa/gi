"""Registro dos agentes: quem são, em que ordem trabalham e o que cada um lê.

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


AGENTES: tuple[Agente, ...] = (
    Agente("negocios", "Analista de Negócios", "analista-negocios",
           "Mapa do negócio, KPIs e requisitos priorizados",
           consultas_rag=("modelo de negócio KPIs por segmento", "requisitos e histórias de usuário de dados"), ordem=1),
    Agente("arquiteto", "Arquiteto de Dados", "arquiteto-dados",
           "Arquitetura-alvo, decisão de hospedagem e modelagem",
           depende_de=("negocios",),
           consultas_rag=("arquitetura medalhão lakehouse porte pequeno médio grande", "matriz de decisão cloud on-premise"),
           usa_custos=True, ordem=2),
    Agente("engenheiro", "Engenheiro de Dados", "engenheiro-dados",
           "Plano de ingestão, pipelines, qualidade e integrações",
           depende_de=("negocios", "arquiteto"),
           consultas_rag=("conectores ERP TOTVS SAP ingestão incremental CDC", "dbt dlt orquestração testes de qualidade"), ordem=3),
    Agente("analista", "Analista de Dados", "analista-dados",
           "Camada semântica, catálogo de métricas e dashboards",
           depende_de=("negocios", "arquiteto", "engenheiro"),
           consultas_rag=("catálogo de métricas camada semântica", "boas práticas de dashboards executivos"), ordem=4),
    Agente("cientista", "Cientista de Dados", "cientista-dados",
           "Casos de IA/ML, viabilidade e plano de experimentos",
           depende_de=("negocios", "arquiteto", "engenheiro"),
           consultas_rag=("casos de uso de machine learning por segmento", "LLM local GPU 6 GB RAG agentes"), ordem=5),
    Agente("cyber", "Cybersecurity", "cybersecurity",
           "Ameaças, LGPD, controles e plano de segurança",
           depende_de=("arquiteto", "engenheiro"),
           consultas_rag=("LGPD dados sensíveis controles", "segurança cloud IAM criptografia backup ransomware"), ordem=6),
    Agente("devops", "DevOps", "devops",
           "Infraestrutura como código, CI/CD, observabilidade e operação",
           depende_de=("arquiteto", "engenheiro", "cyber"),
           consultas_rag=("terraform módulos AWS GCP Azure OCI", "docker compose ZimaOS observabilidade backup"), ordem=7),
    Agente("finops", "FinOps", "finops",
           "Custo por cloud, TCO, otimizações e governança de gastos",
           depende_de=("arquiteto", "engenheiro", "devops", "cientista"),
           consultas_rag=("otimização de custos savings plans reservas", "free tier OCI Always Free BigQuery"),
           usa_custos=True, ordem=8),
    Agente("comercial", "Comercial", "comercial",
           "Proposta comercial, escopo, cronograma e preço",
           depende_de=("negocios", "arquiteto", "engenheiro", "analista", "cientista", "cyber", "devops", "finops"),
           consultas_rag=("precificação de serviços de dados pacotes", "objeções comerciais e ROI"), ordem=9),
)
POR_ID = {a.id: a for a in AGENTES}
ORDEM_PIPELINE = tuple(a.id for a in sorted(AGENTES, key=lambda a: a.ordem))


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
    return Perfil(agente=a, papel=papel, skill=skill, referencias=refs)


def cortar(texto: str, limite: int) -> str:
    if len(texto) <= limite:
        return texto
    return texto[:limite].rsplit("\n", 1)[0] + "\n\n[… cortado para caber no contexto …]"
