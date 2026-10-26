"""Empacota as skills dos agentes no formato do Claude.

    python scripts/empacotar_skills.py              # gera dist/skills/<nome>.zip
    python scripts/empacotar_skills.py --instalar   # copia também para ~/.claude/skills/

Cada pacote leva:
  SKILL.md                  a skill do agente (caminhos ajustados para references/)
  references/papel.md       o AGENT.md do agente (missão, processo, formato de entrega)
  references/<cloud>.md     os guias compartilhados de AWS, GCP, Azure, OCI, on-premise e equivalências
  references/<extra>.md     as referências próprias da skill (ex.: Databricks e Snowflake no Engenheiro)
  references/<banco>.md     os arquivos de conhecimento/ ligados ao agente (todos os de bancos no DBA)

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

from plataforma.agentes import AGENTES, arquivos_conhecimento  # noqa: E402

INDICE_BANCOS = "bancos-de-dados-indice.md"


def plano(raiz: Path = RAIZ) -> dict[str, list[tuple[str, Path | str]]]:
    """Pasta do agente → [(caminho dentro do pacote, arquivo de origem ou texto pronto)]."""
    clouds = sorted((raiz / "skills" / "_clouds").glob("*.md"))
    saida: dict[str, list[tuple[str, Path | str]]] = {}
    for a in AGENTES:
        refs: dict[str, Path] = {"references/papel.md": raiz / "agentes" / a.pasta / "AGENT.md"}
        for c in clouds:
            refs[f"references/{c.name}"] = c
        extra = raiz / "skills" / a.pasta / "references"
        if extra.exists():
            for f in sorted(extra.glob("*.md")):
                refs[f"references/{f.name}"] = f
        for rel in arquivos_conhecimento(raiz, a):
            f = raiz / rel
            refs.setdefault(f"references/{INDICE_BANCOS if f.name == 'README.md' else f.name}", f)
        skill = (raiz / "skills" / a.pasta / "SKILL.md").read_text(encoding="utf-8")
        skill = (
            skill.replace("`skills/_clouds/*.md`", "`references/*.md`")
            .replace("skills/_clouds/", "references/")
            .replace("conhecimento/bancos-de-dados/README.md", f"references/{INDICE_BANCOS}")
            .replace("conhecimento/bancos-de-dados/", "references/")
        )
        skill += "\n\n## Referências deste pacote\n- `references/papel.md` — papel, processo e formato de entrega do agente\n"
        skill += "".join(f"- `{k}`\n" for k in refs if k != "references/papel.md")
        saida[a.pasta] = [("SKILL.md", skill), *refs.items()]
    return saida


def montar(destino: Path) -> list[Path]:
    if destino.exists():
        shutil.rmtree(destino)
    pacotes = []
    for pasta_agente, entradas in plano().items():
        pasta = destino / pasta_agente
        for nome, origem in entradas:
            alvo = pasta / nome
            alvo.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(origem, Path):
                shutil.copy(origem, alvo)
            else:
                alvo.write_text(origem, encoding="utf-8")
        arquivo = destino / f"{pasta_agente}.zip"
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
