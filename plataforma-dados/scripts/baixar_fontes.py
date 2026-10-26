"""Baixa as fontes da marca (licença SIL OFL) para identidade-visual/fontes/.

    python scripts/baixar_fontes.py

Gera os .woff2 (subsets latin e latin-ext) e o fontes.css que o tokens.css importa.
Necessário para renderizar os posts com a tipografia certa e para gerar o logo.
"""

from __future__ import annotations

import re
import urllib.request
from pathlib import Path

DESTINO = Path(__file__).resolve().parents[1] / "identidade-visual" / "fontes"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
FAMILIAS = {
    "BricolageGrotesque": "Bricolage+Grotesque:opsz,wght@12..96,400..800",
    "Figtree": "Figtree:ital,wght@0,400..800;1,400..800",
    "JetBrainsMono": "JetBrains+Mono:wght@400..700",
}


def baixar(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def main() -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    blocos_css = []
    for nome, consulta in FAMILIAS.items():
        css = baixar(f"https://fonts.googleapis.com/css2?family={consulta}&display=swap").decode()
        for subset, corpo in re.findall(r"/\* ([a-z-]+) \*/\s*@font-face \{(.*?)\}", css, re.S):
            if subset not in ("latin", "latin-ext"):
                continue
            url = re.search(r"url\((https://[^)]+)\)", corpo).group(1)
            estilo = re.search(r"font-style: (\w+)", corpo).group(1)
            arquivo = f"{nome}-{estilo}-{subset}.woff2"
            (DESTINO / arquivo).write_bytes(baixar(url))
            corpo = re.sub(r"src: url\([^)]+\) format\('woff2'\)", f"src: url('{arquivo}') format('woff2')", corpo)
            blocos_css.append(f"/* {nome} {estilo} {subset} */\n@font-face {{{corpo}}}")
            print(arquivo)
    (DESTINO / "fontes.css").write_text("\n".join(blocos_css), encoding="utf-8")


if __name__ == "__main__":
    main()
