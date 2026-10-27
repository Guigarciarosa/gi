"""Gera as versões estáticas do questionário a partir do YAML.

    python scripts/construir_questionario.py [saida-fragmento.html]

Saídas:
  questionario/questionario.json   estrutura achatada (o app e os agentes leem)
  questionario/questionario.html   app autônomo, com o JSON embutido; abre
                                   offline no celular ou como artefato
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "servidor" / "src"))

from plataforma.questionario import Questionario  # noqa: E402

MARCADOR = "/*__QUESTIONARIO__*/"


def embutir(html: str, dados: dict) -> str:
    # "</" quebraria o <script>; escapar mantém o JSON válido.
    bruto = json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return html.replace(MARCADOR, bruto)


def main() -> None:
    q = Questionario.carregar(RAIZ / "questionario" / "questionario.yaml")
    dados = q.para_json()
    (RAIZ / "questionario" / "questionario.json").write_text(
        json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    modelo = (RAIZ / "servidor" / "src" / "plataforma" / "web" / "questionario.html").read_text(encoding="utf-8")
    fragmento = embutir(modelo, dados)
    # Documento completo (com doctype) para abrir direto no navegador/celular.
    (RAIZ / "questionario" / "questionario.html").write_text(
        '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        f"</head><body>{fragmento}</body></html>\n",
        encoding="utf-8",
    )
    if len(sys.argv) > 1:  # fragmento sem esqueleto, para publicar como artefato
        Path(sys.argv[1]).write_text(fragmento, encoding="utf-8")
    print(json.dumps(q.estatisticas(), ensure_ascii=False))


if __name__ == "__main__":
    main()
