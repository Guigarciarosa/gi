"""Configuração via variáveis de ambiente (ver infra/zimaos/.env.example)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _raiz_padrao() -> Path:
    # servidor/src/plataforma/config.py -> plataforma-dados/
    local = Path(__file__).resolve().parents[3]
    if (local / "questionario").exists():
        return local
    return Path("/app")


def _env(nome: str, padrao: str) -> str:
    return os.environ.get(nome, padrao)


@dataclass(frozen=True)
class Config:
    raiz: Path = field(default_factory=lambda: Path(_env("PLATAFORMA_RAIZ", str(_raiz_padrao()))))
    dados: Path = field(default_factory=lambda: Path(_env("PLATAFORMA_DADOS", "/data")))
    marca: str = field(default_factory=lambda: _env("MARCA_NOME", "Cardume"))

    # Rede
    host: str = field(default_factory=lambda: _env("MCP_HOST", "0.0.0.0"))
    porta: int = field(default_factory=lambda: int(_env("MCP_PORTA", "8787")))
    token: str = field(default_factory=lambda: _env("MCP_TOKEN", ""))
    hosts_permitidos: tuple[str, ...] = field(
        default_factory=lambda: tuple(h.strip() for h in _env("MCP_HOSTS_PERMITIDOS", "").split(",") if h.strip())
    )

    # Banco vetorial e embeddings
    qdrant_url: str = field(default_factory=lambda: _env("QDRANT_URL", "http://qdrant:6333"))
    qdrant_api_key: str = field(default_factory=lambda: _env("QDRANT_API_KEY", ""))
    ollama_url: str = field(default_factory=lambda: _env("OLLAMA_URL", "http://ollama:11434"))
    modelo_embedding: str = field(default_factory=lambda: _env("MODELO_EMBEDDING", "bge-m3"))

    # LLM dos agentes: "ollama" (local, GPU 6 GB), "anthropic" (API) ou "nenhum"
    # (o servidor só monta o contexto e quem raciocina é o cliente MCP, ex.: Claude Desktop).
    llm_backend: str = field(default_factory=lambda: _env("LLM_BACKEND", "nenhum"))
    modelo_local: str = field(default_factory=lambda: _env("MODELO_LOCAL", "qwen3:4b"))
    contexto_local: int = field(default_factory=lambda: int(_env("CONTEXTO_LOCAL", "16384")))
    modelo_anthropic: str = field(default_factory=lambda: _env("MODELO_ANTHROPIC", "claude-opus-5-5"))
    esforco_anthropic: str = field(default_factory=lambda: _env("ESFORCO_ANTHROPIC", "high"))

    # Custos
    cambio_usd_brl: float = field(default_factory=lambda: float(_env("CAMBIO_USD_BRL", "5.50")))
    tarifa_kwh_brl: float = field(default_factory=lambda: float(_env("TARIFA_KWH_BRL", "0.90")))

    @property
    def questionario(self) -> Path:
        return self.raiz / "questionario" / "questionario.yaml"

    @property
    def agentes(self) -> Path:
        return self.raiz / "agentes"

    @property
    def skills(self) -> Path:
        return self.raiz / "skills"

    @property
    def docs(self) -> Path:
        return self.raiz / "docs"

    @property
    def banco(self) -> Path:
        return self.dados / "plataforma.db"

    @property
    def entregaveis(self) -> Path:
        return self.dados / "entregaveis"


def carregar() -> Config:
    return Config()
