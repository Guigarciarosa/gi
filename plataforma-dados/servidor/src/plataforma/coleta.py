"""Coleta de documentação oficial para a memória dos agentes.

Os arquivos de `conhecimento/` e `skills/` terminam com uma seção
"## Documentação oficial" com links. Este módulo baixa essas páginas (e, se pedido,
as páginas ligadas a elas no mesmo site e na mesma pasta), respeitando o robots.txt,
converte o HTML em Markdown simples e grava uma pasta por fonte. Indexadas na coleção
`conhecimento`, elas passam a aparecer no contexto dos agentes.

Uso interno: respeite a licença e os termos de cada site.
"""

from __future__ import annotations

import re
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx2 as httpx

AGENTE_HTTP = "PlataformaDados/1.0 (coleta de documentacao para uso interno)"
SECAO = re.compile(r"^## Documentação oficial[ \t]*\n(.*?)(?=^## |\Z)", re.M | re.S)
URL = re.compile(r"https?://[^\s)>\]`]+")


def links_oficiais(raiz: Path, pastas: tuple[str, ...] = ("conhecimento", "skills")) -> dict[str, list[str]]:
    """Fonte (nome do arquivo) → links da seção "Documentação oficial"."""
    fontes: dict[str, list[str]] = {}
    for pasta in pastas:
        if not (raiz / pasta).exists():
            continue
        for arq in sorted((raiz / pasta).rglob("*.md")):
            if "_oficiais" in arq.parts:
                continue
            m = SECAO.search(arq.read_text(encoding="utf-8"))
            if not m:
                continue
            urls = list(dict.fromkeys(u.rstrip(".,;") for u in URL.findall(m.group(1))))
            if urls:
                nome = arq.stem if arq.stem not in fontes else f"{arq.parent.name}-{arq.stem}"
                fontes[nome] = urls
    return fontes


# ------------------------------------------------------------ HTML → Markdown
class _Extrator(HTMLParser):
    IGNORAR = {"script", "style", "nav", "header", "footer", "aside", "noscript", "svg", "form", "button", "template"}
    BLOCOS = {"p", "div", "section", "article", "main", "br", "tr", "table", "ul", "ol", "dl", "dt", "dd", "blockquote"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.partes: list[str] = []
        self.links: list[str] = []
        self.titulo = ""
        self._ignorar = 0
        self._pre = 0
        self._no_titulo = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.IGNORAR:
            self._ignorar += 1
            return
        if self._ignorar:
            return
        if tag == "title":
            self._no_titulo = True
        elif tag in ("h1", "h2", "h3", "h4"):
            self.partes.append("\n\n" + "#" * int(tag[1]) + " ")
        elif tag == "li":
            self.partes.append("\n- ")
        elif tag == "pre":
            self._pre += 1
            self.partes.append("\n```\n")
        elif tag in ("td", "th"):
            self.partes.append(" | ")
        elif tag in self.BLOCOS:
            self.partes.append("\n")
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag in self.IGNORAR:
            self._ignorar = max(0, self._ignorar - 1)
            return
        if self._ignorar:
            return
        if tag == "title":
            self._no_titulo = False
        elif tag == "pre":
            self._pre = max(0, self._pre - 1)
            self.partes.append("\n```\n")
        elif tag in ("h1", "h2", "h3", "h4") or tag in self.BLOCOS:
            self.partes.append("\n")

    def handle_data(self, data: str) -> None:
        if self._no_titulo:
            self.titulo += data
            return
        if self._ignorar:
            return
        self.partes.append(data if self._pre else re.sub(r"\s+", " ", data))


def html_para_markdown(html: str) -> tuple[str, str, list[str]]:
    """Devolve (título, texto em Markdown simples, links encontrados no conteúdo)."""
    ex = _Extrator()
    ex.feed(html)
    ex.close()
    linhas = [ln.rstrip() for ln in "".join(ex.partes).splitlines()]
    texto = re.sub(r"\n{3,}", "\n\n", "\n".join(linhas)).strip()
    return re.sub(r"\s+", " ", ex.titulo).strip(), texto, ex.links


# ------------------------------------------------------------------- download
@dataclass
class Resposta:
    status: int
    tipo: str
    texto: str


def _buscar_http(url: str) -> Resposta:
    r = httpx.get(url, headers={"User-Agent": AGENTE_HTTP}, timeout=30, follow_redirects=True)
    return Resposta(r.status_code, r.headers.get("content-type", ""), r.text)


@dataclass
class ResultadoColeta:
    fonte: str
    arquivos: list[str] = field(default_factory=list)
    erros: list[str] = field(default_factory=list)


def _nome_arquivo(url: str) -> str:
    p = urlparse(url)
    base = re.sub(r"[^a-z0-9]+", "-", f"{p.netloc}{p.path}".lower()).strip("-")
    return (base[:120] or "pagina") + ".md"


def baixar_fonte(
    fonte: str,
    urls: list[str],
    destino: Path,
    max_paginas: int = 15,
    atraso: float = 1.0,
    buscar: Callable[[str], Resposta] = _buscar_http,
) -> ResultadoColeta:
    """Baixa as páginas da fonte e as ligadas a elas no mesmo site e na mesma pasta."""
    res = ResultadoColeta(fonte)
    pasta = destino / fonte
    pasta.mkdir(parents=True, exist_ok=True)
    prefixos = {u: u.rsplit("/", 1)[0] + "/" for u in urls}
    robots: dict[str, RobotFileParser | None] = {}

    def permitido(url: str) -> bool:
        p = urlparse(url)
        if p.netloc not in robots:
            rp = RobotFileParser()
            try:
                r = buscar(f"{p.scheme}://{p.netloc}/robots.txt")
                rp.parse(r.texto.splitlines() if r.status == 200 else [])
            except Exception:
                rp.parse([])
            robots[p.netloc] = rp
        rp = robots[p.netloc]
        return rp.can_fetch(AGENTE_HTTP, url) if rp else True

    fila = deque(urls)
    vistos = set(urls)
    while fila and len(res.arquivos) < max_paginas:
        url = fila.popleft()
        if not permitido(url):
            res.erros.append(f"{url}: bloqueado pelo robots.txt")
            continue
        try:
            r = buscar(url)
        except Exception as e:
            res.erros.append(f"{url}: {type(e).__name__}: {e}")
            continue
        if r.status != 200:
            res.erros.append(f"{url}: HTTP {r.status}")
            continue
        if "html" not in r.tipo and "text" not in r.tipo:
            res.erros.append(f"{url}: tipo não suportado ({r.tipo or 'desconhecido'})")
            continue
        titulo, texto, links = html_para_markdown(r.texto) if "html" in r.tipo else (url, r.texto, [])
        if len(texto) < 200:
            res.erros.append(f"{url}: página sem conteúdo útil")
            continue
        arq = pasta / _nome_arquivo(url)
        arq.write_text(
            f"# {titulo or url}\n\nFonte: {url}\nBaixado em: {date.today().isoformat()}\n"
            f"Uso interno da plataforma; respeite a licença do site.\n\n{texto}\n",
            encoding="utf-8",
        )
        res.arquivos.append(str(arq))
        prefixo = next((pre for u, pre in prefixos.items() if url.startswith(pre)), None)
        for href in links:
            alvo = urldefrag(urljoin(url, href))[0]
            if prefixo and alvo.startswith(prefixo) and alvo not in vistos:
                vistos.add(alvo)
                fila.append(alvo)
        if atraso:
            time.sleep(atraso)
    return res
