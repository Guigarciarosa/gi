"""Memória vetorial: Qdrant (REST) + embeddings do Ollama.

Coleções (todas com o mesmo modelo de embedding):
  conhecimento  documentação da plataforma, agentes, skills e referências de cloud
  clientes      respostas do discovery e entregáveis dos agentes, por cliente
  projetos      lições aprendidas e resumos de projetos entregues (reuso em propostas)
  marca         identidade visual, tom de voz e posts publicados

Isolamento entre clientes: um único índice `clientes` com o campo `cliente`
marcado como tenant (recomendação do Qdrant para multi-inquilino), e toda
busca nessa coleção exige o filtro por cliente.

Para testes e instalações mínimas: QDRANT_URL=memoria usa um índice em memória
e MODELO_EMBEDDING=hash usa embeddings por hashing (sem GPU, qualidade menor).
"""

from __future__ import annotations

import hashlib
import math
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Protocol

import httpx2 as httpx

COLECOES = {
    "conhecimento": "Documentação, agentes, skills e referências de cloud",
    "clientes": "Respostas e entregáveis por cliente (filtro obrigatório por cliente)",
    "projetos": "Lições aprendidas e projetos entregues",
    "marca": "Identidade visual, tom de voz e conteúdo do Instagram",
}
NAMESPACE = uuid.UUID("6f1c2b8e-3d4a-4c1e-9b7a-0c5e2f8d9a11")


# ------------------------------------------------------------------ embeddings
class Embedder(Protocol):
    def embed(self, textos: list[str]) -> list[list[float]]: ...


class OllamaEmbedder:
    def __init__(self, url: str, modelo: str, timeout: float = 120.0):
        self.url = url.rstrip("/")
        self.modelo = modelo
        self.timeout = timeout

    def embed(self, textos: list[str]) -> list[list[float]]:
        r = httpx.post(f"{self.url}/api/embed", json={"model": self.modelo, "input": textos}, timeout=self.timeout)
        r.raise_for_status()
        return r.json()["embeddings"]


class HashEmbedder:
    """Bag-of-words com hashing assinado. Sem dependências e determinístico."""

    def __init__(self, dimensao: int = 768):
        self.dimensao = dimensao

    def embed(self, textos: list[str]) -> list[list[float]]:
        saida = []
        for t in textos:
            v = [0.0] * self.dimensao
            tokens = re.findall(r"\w+", t.lower())
            for a, b in zip(tokens, tokens[1:] + [""]):
                for termo, peso in ((a, 1.0), (f"{a}_{b}", 0.5)):
                    h = int(hashlib.blake2b(termo.encode(), digest_size=8).hexdigest(), 16)
                    v[h % self.dimensao] += peso if (h >> 63) & 1 else -peso
            n = math.sqrt(sum(x * x for x in v)) or 1.0
            saida.append([x / n for x in v])
        return saida


def criar_embedder(ollama_url: str, modelo: str) -> Embedder:
    return HashEmbedder() if modelo == "hash" else OllamaEmbedder(ollama_url, modelo)


# ---------------------------------------------------------------- fragmentação
def fragmentar(texto: str, tamanho: int = 1200, sobreposicao: int = 150) -> list[str]:
    """Quebra Markdown por títulos e depois por tamanho, mantendo o título
    da seção no início de cada pedaço (melhora a recuperação)."""
    secoes: list[str] = []
    for s in re.split(r"(?m)^(?=#{1,4} )", texto):
        # Junta seções muito curtas (ex.: só o título) com a seguinte.
        if secoes and len(secoes[-1].strip()) < 200:
            secoes[-1] = f"{secoes[-1].rstrip()}\n\n{s}"
        else:
            secoes.append(s)
    pedacos: list[str] = []
    for s in secoes:
        s = s.strip()
        if not s:
            continue
        titulo = s.splitlines()[0] if s.startswith("#") else ""
        if len(s) <= tamanho:
            pedacos.append(s)
            continue
        inicio = 0
        while inicio < len(s):
            trecho = s[inicio : inicio + tamanho]
            if inicio > 0 and titulo:
                trecho = f"{titulo}\n…{trecho}"
            pedacos.append(trecho)
            inicio += tamanho - sobreposicao
    return pedacos


def id_ponto(colecao: str, origem: str, indice: int) -> str:
    return str(uuid.uuid5(NAMESPACE, f"{colecao}|{origem}|{indice}"))


@dataclass
class Resultado:
    texto: str
    pontuacao: float
    metadados: dict[str, Any]


# ---------------------------------------------------------------------- índices
class Indice(Protocol):
    def garantir(self, colecao: str, dimensao: int) -> None: ...
    def inserir(self, colecao: str, pontos: list[dict[str, Any]]) -> None: ...
    def remover_origem(self, colecao: str, origem: str, cliente: str | None = None) -> None: ...
    def buscar(self, colecao: str, vetor: list[float], limite: int, filtro: dict[str, str]) -> list[Resultado]: ...
    def contar(self, colecao: str) -> int: ...


class QdrantIndice:
    def __init__(self, url: str, api_key: str = "", timeout: float = 30.0):
        self.url = url.rstrip("/")
        self.headers = {"api-key": api_key} if api_key else {}
        self.timeout = timeout

    def _req(self, metodo: str, caminho: str, **kw: Any) -> dict[str, Any]:
        r = httpx.request(metodo, f"{self.url}{caminho}", headers=self.headers, timeout=self.timeout, **kw)
        if r.status_code == 404 and metodo == "GET":
            return {}
        r.raise_for_status()
        return r.json() if r.content else {}

    def garantir(self, colecao: str, dimensao: int) -> None:
        existente = self._req("GET", f"/collections/{colecao}").get("result")
        if existente:
            atual = existente.get("config", {}).get("params", {}).get("vectors", {}).get("size")
            if atual and atual != dimensao:
                raise RuntimeError(
                    f"A coleção '{colecao}' tem vetores de {atual} dimensões e o modelo de embedding atual gera {dimensao}. "
                    "Você trocou MODELO_EMBEDDING: apague as coleções no Qdrant e rode memoria_reindexar_base."
                )
            return
        self._req(
            "PUT",
            f"/collections/{colecao}",
            json={
                "vectors": {"size": dimensao, "distance": "Cosine", "on_disk": True},
                # int8 na RAM, vetores originais em disco: cabe folgado em 16 GB.
                "quantization_config": {"scalar": {"type": "int8", "always_ram": True}},
                "hnsw_config": {"on_disk": True},
            },
        )
        indices = [("origem", {"type": "keyword"}), ("tipo", {"type": "keyword"})]
        if colecao == "clientes":
            indices.insert(0, ("cliente", {"type": "keyword", "is_tenant": True}))
        for campo, esquema in indices:
            self._req("PUT", f"/collections/{colecao}/index?wait=true", json={"field_name": campo, "field_schema": esquema})

    def inserir(self, colecao: str, pontos: list[dict[str, Any]]) -> None:
        for i in range(0, len(pontos), 64):
            self._req("PUT", f"/collections/{colecao}/points?wait=true", json={"points": pontos[i : i + 64]})

    def remover_origem(self, colecao: str, origem: str, cliente: str | None = None) -> None:
        must = [{"key": "origem", "match": {"value": origem}}]
        if cliente:
            must.append({"key": "cliente", "match": {"value": cliente}})
        if not self._req("GET", f"/collections/{colecao}").get("result"):
            return
        self._req("POST", f"/collections/{colecao}/points/delete?wait=true", json={"filter": {"must": must}})

    def buscar(self, colecao: str, vetor: list[float], limite: int, filtro: dict[str, str]) -> list[Resultado]:
        corpo: dict[str, Any] = {"query": vetor, "limit": limite, "with_payload": True}
        if filtro:
            corpo["filter"] = {"must": [{"key": k, "match": {"value": v}} for k, v in filtro.items()]}
        dados = self._req("POST", f"/collections/{colecao}/points/query", json=corpo)
        pontos = dados.get("result", {}).get("points", [])
        return [
            Resultado(texto=p["payload"].get("texto", ""), pontuacao=p.get("score", 0.0),
                      metadados={k: v for k, v in p["payload"].items() if k != "texto"})
            for p in pontos
        ]

    def contar(self, colecao: str) -> int:
        if not self._req("GET", f"/collections/{colecao}").get("result"):
            return 0
        return self._req("POST", f"/collections/{colecao}/points/count", json={"exact": True})["result"]["count"]


class MemoriaIndice:
    def __init__(self) -> None:
        self.dados: dict[str, dict[str, dict[str, Any]]] = {}

    def garantir(self, colecao: str, dimensao: int) -> None:
        self.dados.setdefault(colecao, {})

    def inserir(self, colecao: str, pontos: list[dict[str, Any]]) -> None:
        for p in pontos:
            self.dados.setdefault(colecao, {})[p["id"]] = p

    def remover_origem(self, colecao: str, origem: str, cliente: str | None = None) -> None:
        c = self.dados.get(colecao, {})
        for pid in [k for k, p in c.items() if p["payload"].get("origem") == origem and (not cliente or p["payload"].get("cliente") == cliente)]:
            del c[pid]

    def buscar(self, colecao: str, vetor: list[float], limite: int, filtro: dict[str, str]) -> list[Resultado]:
        candidatos = [
            p for p in self.dados.get(colecao, {}).values()
            if all(p["payload"].get(k) == v for k, v in filtro.items())
        ]
        pont = sorted(((sum(a * b for a, b in zip(vetor, p["vector"])), p) for p in candidatos), key=lambda x: x[0], reverse=True)
        return [
            Resultado(texto=p["payload"]["texto"], pontuacao=s, metadados={k: v for k, v in p["payload"].items() if k != "texto"})
            for s, p in pont[:limite]
        ]

    def contar(self, colecao: str) -> int:
        return len(self.dados.get(colecao, {}))


def criar_indice(url: str, api_key: str = "") -> Indice:
    return MemoriaIndice() if url == "memoria" else QdrantIndice(url, api_key)


# ------------------------------------------------------------------ fachada
class MemoriaVetorial:
    def __init__(self, indice: Indice, embedder: Embedder):
        self.indice = indice
        self.embedder = embedder
        self._dimensao: int | None = None

    def _dim(self) -> int:
        if self._dimensao is None:
            self._dimensao = len(self.embedder.embed(["dimensão"])[0])
        return self._dimensao

    def indexar(self, colecao: str, origem: str, texto: str, metadados: dict[str, Any] | None = None) -> int:
        if colecao not in COLECOES:
            raise ValueError(f"Coleção desconhecida: {colecao}. Use: {', '.join(COLECOES)}")
        meta = dict(metadados or {})
        if colecao == "clientes" and not meta.get("cliente"):
            raise ValueError("A coleção 'clientes' exige metadados.cliente")
        self.indice.garantir(colecao, self._dim())
        self.indice.remover_origem(colecao, origem, meta.get("cliente"))
        pedacos = fragmentar(texto)
        if not pedacos:
            return 0
        vetores: list[list[float]] = []
        for i in range(0, len(pedacos), 16):
            vetores.extend(self.embedder.embed(pedacos[i : i + 16]))
        chave = f"{meta.get('cliente', '')}|{origem}"
        pontos = [
            {"id": id_ponto(colecao, chave, i), "vector": v,
             "payload": {"texto": t, "origem": origem, "trecho": i, **meta}}
            for i, (t, v) in enumerate(zip(pedacos, vetores))
        ]
        self.indice.inserir(colecao, pontos)
        return len(pontos)

    def buscar(self, consulta: str, colecao: str = "conhecimento", limite: int = 6,
               cliente: str | None = None, filtros: dict[str, str] | None = None) -> list[Resultado]:
        if colecao not in COLECOES:
            raise ValueError(f"Coleção desconhecida: {colecao}")
        filtro = dict(filtros or {})
        if colecao == "clientes":
            if not cliente:
                raise ValueError("Busca na coleção 'clientes' exige o cliente (isolamento entre clientes).")
            filtro["cliente"] = cliente
        self.indice.garantir(colecao, self._dim())
        vetor = self.embedder.embed([consulta])[0]
        return self.indice.buscar(colecao, vetor, limite, filtro)

    def indexar_pasta(self, raiz: Path, pastas: Iterable[str]) -> dict[str, int]:
        total: dict[str, int] = {}
        for pasta in pastas:
            for arq in sorted((raiz / pasta).rglob("*.md")):
                rel = str(arq.relative_to(raiz))
                tipo = pasta.split("/")[0]
                total[rel] = self.indexar("conhecimento", rel, arq.read_text(encoding="utf-8"), {"tipo": tipo})
        return total

    def estatisticas(self) -> dict[str, int]:
        return {c: self.indice.contar(c) for c in COLECOES}
