import os
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]

os.environ.setdefault("PLATAFORMA_RAIZ", str(RAIZ))
os.environ.setdefault("QDRANT_URL", "memoria")
os.environ.setdefault("MODELO_EMBEDDING", "hash")
os.environ.setdefault("LLM_BACKEND", "nenhum")


@pytest.fixture
def plataforma(tmp_path):
    from plataforma.config import Config
    from plataforma.orquestrador import Plataforma

    cfg = Config(raiz=RAIZ, dados=tmp_path)
    return Plataforma(cfg)


@pytest.fixture
def questionario():
    from plataforma.questionario import Questionario

    return Questionario.carregar(RAIZ / "questionario" / "questionario.yaml")
