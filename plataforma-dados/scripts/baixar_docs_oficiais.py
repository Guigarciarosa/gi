"""Baixa a documentação oficial listada na base de conhecimento.

    python scripts/baixar_docs_oficiais.py --listar
    python scripts/baixar_docs_oficiais.py postgresql sql-server --max-paginas 30
    python scripts/baixar_docs_oficiais.py --todas

Lê os links da seção "Documentação oficial" de cada arquivo de `conhecimento/` e
`skills/`, baixa as páginas (respeitando o robots.txt) e grava Markdown em
`conhecimento/_oficiais/<fonte>/` (fora do Git). Depois rode a ferramenta MCP
`memoria_reindexar_base` para os agentes passarem a usar esse conteúdo. No servidor,
a ferramenta `conhecimento_baixar` faz o mesmo direto em /data.

Uso interno: respeite a licença e os termos de cada site.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "servidor" / "src"))

from plataforma import coleta  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fontes", nargs="*", help="nomes das fontes (nome do arquivo sem .md)")
    ap.add_argument("--todas", action="store_true", help="baixar todas as fontes")
    ap.add_argument("--listar", action="store_true", help="só listar as fontes e os links")
    ap.add_argument("--max-paginas", type=int, default=15, help="páginas por fonte (padrão 15)")
    ap.add_argument("--atraso", type=float, default=1.0, help="segundos entre páginas (padrão 1)")
    ap.add_argument("--destino", type=Path, default=RAIZ / "conhecimento" / "_oficiais")
    args = ap.parse_args()

    fontes = coleta.links_oficiais(RAIZ)
    if args.listar or not (args.todas or args.fontes):
        for nome, urls in fontes.items():
            print(f"{nome}  ({len(urls)} links)")
            for u in urls:
                print(f"    {u}")
        return
    escolhidas = list(fontes) if args.todas else args.fontes
    desconhecidas = [f for f in escolhidas if f not in fontes]
    if desconhecidas:
        sys.exit(f"Fontes desconhecidas: {', '.join(desconhecidas)}. Use --listar.")
    total = 0
    for nome in escolhidas:
        res = coleta.baixar_fonte(nome, fontes[nome], args.destino, args.max_paginas, args.atraso)
        total += len(res.arquivos)
        print(f"{nome}: {len(res.arquivos)} páginas" + (f", {len(res.erros)} avisos" if res.erros else ""))
        for e in res.erros[:5]:
            print(f"    {e}")
    print(f"\n{total} páginas em {args.destino}. Agora rode memoria_reindexar_base no MCP.")


if __name__ == "__main__":
    main()
