"""Empacota as skills dos agentes no formato do Claude.

    python scripts/empacotar_skills.py              # gera dist/skills/<nome>.zip
    python scripts/empacotar_skills.py --instalar   # copia também para ~/.claude/skills/

Cada pacote leva:
  SKILL.md                  a skill do agente (caminhos ajustados para references/)
  references/papel.md       o AGENT.md do agente (missão, processo, formato de entrega)
  references/<cloud>.md     os guias compartilhados de AWS, GCP, Azure, OCI, on-premise e equivalências

Os .zip podem ser enviados em claude.ai (Configurações → Capacidades → Skills) ou
usados no Claude Code copiando a pasta para ~/.claude/skills/.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "servidor" / "src"))

from plataforma.agentes import AGENTES  # noqa: E402


def montar(destino: Path) -> list[Path]:
    if destino.exists():
        shutil.rmtree(destino)
    pacotes = []
    clouds = sorted((RAIZ / "skills" / "_clouds").glob("*.md"))
    for a in AGENTES:
        pasta = destino / a.pasta
        refs = pasta / "references"
        refs.mkdir(parents=True)
        skill = (RAIZ / "skills" / a.pasta / "SKILL.md").read_text(encoding="utf-8")
        skill = skill.replace("skills/_clouds/", "references/").replace("`skills/_clouds/*.md`", "`references/*.md`")
        skill += "\n\n## Referências deste pacote\n- `references/papel.md` — papel, processo e formato de entrega do agente\n"
        skill += "".join(f"- `references/{c.name}`\n" for c in clouds)
        (pasta / "SKILL.md").write_text(skill, encoding="utf-8")
        shutil.copy(RAIZ / "agentes" / a.pasta / "AGENT.md", refs / "papel.md")
        for c in clouds:
            shutil.copy(c, refs / c.name)
        extra = RAIZ / "skills" / a.pasta / "references"
        if extra.exists():
            for f in extra.glob("*.md"):
                shutil.copy(f, refs / f.name)
        arquivo = destino / f"{a.pasta}.zip"
        with zipfile.ZipFile(arquivo, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(pasta.rglob("*")):
                if f.is_file():
                    z.write(f, f.relative_to(destino))
        pacotes.append(arquivo)
    return pacotes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--instalar", action="store_true", help="copiar para ~/.claude/skills/")
    args = ap.parse_args()
    destino = RAIZ / "dist" / "skills"
    pacotes = montar(destino)
    for p in pacotes:
        print(f"{p.relative_to(RAIZ)}  ({p.stat().st_size // 1024} KB)")
    if args.instalar:
        alvo = Path.home() / ".claude" / "skills"
        alvo.mkdir(parents=True, exist_ok=True)
        for a in AGENTES:
            shutil.copytree(destino / a.pasta, alvo / a.pasta, dirs_exist_ok=True)
        print(f"Instalado em {alvo}")


if __name__ == "__main__":
    main()
