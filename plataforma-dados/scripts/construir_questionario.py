"""Gera as versões estáticas do questionário a partir do YAML.

    python scripts/construir_questionario.py

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
    (RAIZ / "questionario" / "questionario.html").write_text(embutir(modelo, dados), encoding="utf-8")
    print(json.dumps(q.estatisticas(), ensure_ascii=False))


if __name__ == "__main__":
    main()
