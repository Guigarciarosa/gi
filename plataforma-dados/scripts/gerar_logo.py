"""Gera os arquivos de logo da marca em SVG (texto convertido em curvas).

    pip install fonttools brotli
    python scripts/gerar_logo.py

O símbolo: nove peixes (triângulos) em formação diagonal ascendente — os nove
agentes se movendo como um só, desenhando uma tendência de alta. O peixe da
frente, em coral, é a decisão: o ponto para onde o cardume vai.
"""

from __future__ import annotations

import math
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "identidade-visual"
FONTE = SAIDA / "fontes" / "BricolageGrotesque-normal-latin.woff2"

ABISSAL = "#0B2238"
CARDUME = "#0F7C7A"
CARDUME_CLARO = "#3CC6BE"
CORAL = "#E4572E"
ESPUMA = "#F2F6F6"
BRANCO = "#FFFFFF"

# Centros dos 9 peixes num quadro de 100×100 (3 fileiras deslocadas para cima à direita).
CENTROS = [
    (20, 78), (41, 70), (62, 62),
    (28, 55), (49, 47), (70, 39),
    (36, 32), (57, 24), (80, 15),
]
LIDER = 8  # índice do peixe coral


def peixe(cx: float, cy: float, escala: float = 1.0, angulo: float = -18.0) -> str:
    """Triângulo apontando para a direita, levemente inclinado para cima."""
    pts = [(-9, -6.5), (10, 0), (-9, 6.5)]
    a = math.radians(angulo)
    saida = []
    for x, y in pts:
        x, y = x * escala, y * escala
        rx = x * math.cos(a) - y * math.sin(a)
        ry = x * math.sin(a) + y * math.cos(a)
        saida.append(f"{cx + rx:.2f},{cy + ry:.2f}")
    return "M" + " L".join(saida) + " Z"


def simbolo(cor: str, cor_lider: str = CORAL, escala: float = 1.3) -> str:
    return "".join(
        f'<path d="{peixe(x, y, escala)}" fill="{cor_lider if i == LIDER else cor}"/>'
        for i, (x, y) in enumerate(CENTROS)
    )


def palavra_em_curvas(texto: str, peso: int = 760, tamanho: float = 64.0) -> tuple[str, float, float]:
    fonte = TTFont(str(FONTE))
    eixos = {a.axisTag for a in fonte["fvar"].axes}
    alvo = {"wght": peso}
    if "opsz" in eixos:
        alvo["opsz"] = 48
    fonte = instantiateVariableFont(fonte, alvo)
    glifos = fonte.getGlyphSet()
    cmap = fonte.getBestCmap()
    upm = fonte["head"].unitsPerEm
    esc = tamanho / upm
    caneta = SVGPathPen(glifos)
    x = 0.0
    for ch in texto:
        nome = cmap[ord(ch)]
        tp = TransformPen(caneta, (esc, 0, 0, -esc, x, 0))
        glifos[nome].draw(tp)
        x += glifos[nome].width * esc
    limites = BoundsPen(glifos)
    x2 = 0.0
    for ch in texto:
        nome = cmap[ord(ch)]
        glifos[nome].draw(TransformPen(limites, (esc, 0, 0, -esc, x2, 0)))
        x2 += glifos[nome].width * esc
    _, y_min, _, y_max = limites.bounds
    return caneta.getCommands(), x, y_max - y_min


def svg(conteudo: str, largura: float, altura: float, titulo: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura:.0f} {altura:.0f}" '
        f'width="{largura:.0f}" height="{altura:.0f}" role="img" aria-label="{titulo}">'
        f"<title>{titulo}</title>{conteudo}</svg>\n"
    )


def main() -> None:
    # Símbolo sobre quadrado arredondado (ícone de app / avatar)
    icone = f'<rect width="100" height="100" rx="22" fill="{CARDUME}"/><g transform="translate(8,8) scale(0.84)">{simbolo(BRANCO)}</g>'
    (SAIDA / "logo-simbolo.svg").write_text(svg(icone, 100, 100, "Cardume — símbolo"), encoding="utf-8")
    (SAIDA / "logo-simbolo-escuro.svg").write_text(
        svg(f'<rect width="100" height="100" rx="22" fill="{ABISSAL}"/><g transform="translate(8,8) scale(0.84)">{simbolo(CARDUME_CLARO, "#FF8A63")}</g>', 100, 100, "Cardume — símbolo"),
        encoding="utf-8",
    )
    (SAIDA / "logo-simbolo-transparente.svg").write_text(svg(simbolo(CARDUME), 100, 100, "Cardume — símbolo"), encoding="utf-8")
    (SAIDA / "logo-simbolo-branco.svg").write_text(svg(simbolo(BRANCO), 100, 100, "Cardume — símbolo"), encoding="utf-8")

    caminhos, largura_txt, _ = palavra_em_curvas("cardume")
    for nome, cor_txt, cor_simb, cor_lider in (
        ("logo-horizontal.svg", ABISSAL, CARDUME, CORAL),
        ("logo-horizontal-negativo.svg", ESPUMA, CARDUME_CLARO, "#FF8A63"),
    ):
        conteudo = (
            f'<g transform="translate(0,2)">{simbolo(cor_simb, cor_lider)}</g>'
            f'<path transform="translate(112,72)" d="{caminhos}" fill="{cor_txt}"/>'
        )
        (SAIDA / nome).write_text(svg(conteudo, 112 + largura_txt + 8, 100, "Cardume"), encoding="utf-8")
    print("Logos gerados em", SAIDA)


if __name__ == "__main__":
    main()
