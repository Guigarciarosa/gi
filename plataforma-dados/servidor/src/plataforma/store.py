"""Armazenamento relacional (SQLite): clientes, respostas, entregáveis e execuções.

SQLite é suficiente para o volume da plataforma (dezenas de clientes) e cabe
num único arquivo em /DATA/AppData/plataforma, fácil de copiar no backup.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ESQUEMA = """
CREATE TABLE IF NOT EXISTS clientes (
    slug TEXT PRIMARY KEY,
    empresa TEXT NOT NULL,
    criado_em TEXT NOT NULL,
    atualizado_em TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS discovery (
    slug TEXT PRIMARY KEY REFERENCES clientes(slug) ON DELETE CASCADE,
    respostas TEXT NOT NULL,
    versao_questionario TEXT,
    atualizado_em TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS entregaveis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL REFERENCES clientes(slug) ON DELETE CASCADE,
    agente TEXT NOT NULL,
    titulo TEXT NOT NULL,
    conteudo TEXT NOT NULL,
    modelo TEXT,
    criado_em TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_entregaveis_slug ON entregaveis(slug, agente, criado_em);
CREATE TABLE IF NOT EXISTS execucoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL,
    backend TEXT NOT NULL,
    status TEXT NOT NULL,
    log TEXT NOT NULL DEFAULT '[]',
    iniciado_em TEXT NOT NULL,
    concluido_em TEXT
);
"""


def agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    def __init__(self, caminho: Path | str):
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        self._con = sqlite3.connect(str(caminho), check_same_thread=False)
        self._con.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        with self._lock:
            self._con.execute("PRAGMA journal_mode=WAL")
            self._con.execute("PRAGMA foreign_keys=ON")
            self._con.executescript(ESQUEMA)

    def _exec(self, sql: str, args: tuple = ()) -> sqlite3.Cursor:
        with self._lock:
            cur = self._con.execute(sql, args)
            self._con.commit()
            return cur

    def _consultar(self, sql: str, args: tuple = ()) -> list[dict[str, Any]]:
        with self._lock:
            return [dict(r) for r in self._con.execute(sql, args).fetchall()]

    # -------------------------------------------------------------- clientes
    def salvar_cliente(self, slug: str, empresa: str) -> None:
        t = agora()
        self._exec(
            "INSERT INTO clientes(slug, empresa, criado_em, atualizado_em) VALUES (?,?,?,?) "
            "ON CONFLICT(slug) DO UPDATE SET empresa=excluded.empresa, atualizado_em=excluded.atualizado_em",
            (slug, empresa, t, t),
        )

    def clientes(self) -> list[dict[str, Any]]:
        return self._consultar(
            "SELECT c.slug, c.empresa, c.criado_em, c.atualizado_em, d.atualizado_em AS discovery_em, "
            "(SELECT COUNT(*) FROM entregaveis e WHERE e.slug=c.slug) AS entregaveis "
            "FROM clientes c LEFT JOIN discovery d ON d.slug=c.slug ORDER BY c.atualizado_em DESC"
        )

    def cliente(self, slug: str) -> dict[str, Any] | None:
        linhas = self._consultar("SELECT * FROM clientes WHERE slug=?", (slug,))
        return linhas[0] if linhas else None

    def remover_cliente(self, slug: str) -> None:
        self._exec("DELETE FROM clientes WHERE slug=?", (slug,))

    # ------------------------------------------------------------- discovery
    def salvar_respostas(self, slug: str, empresa: str, respostas: dict[str, Any], versao: str | None) -> None:
        self.salvar_cliente(slug, empresa)
        self._exec(
            "INSERT INTO discovery(slug, respostas, versao_questionario, atualizado_em) VALUES (?,?,?,?) "
            "ON CONFLICT(slug) DO UPDATE SET respostas=excluded.respostas, "
            "versao_questionario=excluded.versao_questionario, atualizado_em=excluded.atualizado_em",
            (slug, json.dumps(respostas, ensure_ascii=False), versao, agora()),
        )

    def respostas(self, slug: str) -> dict[str, Any]:
        linhas = self._consultar("SELECT respostas FROM discovery WHERE slug=?", (slug,))
        return json.loads(linhas[0]["respostas"]) if linhas else {}

    # ----------------------------------------------------------- entregáveis
    def salvar_entregavel(self, slug: str, agente: str, titulo: str, conteudo: str, modelo: str | None = None) -> int:
        cur = self._exec(
            "INSERT INTO entregaveis(slug, agente, titulo, conteudo, modelo, criado_em) VALUES (?,?,?,?,?,?)",
            (slug, agente, titulo, conteudo, modelo, agora()),
        )
        return int(cur.lastrowid)

    def entregaveis(self, slug: str, agente: str | None = None, apenas_ultimos: bool = True) -> list[dict[str, Any]]:
        sql = "SELECT id, agente, titulo, conteudo, modelo, criado_em FROM entregaveis WHERE slug=?"
        args: tuple = (slug,)
        if agente:
            sql += " AND agente=?"
            args += (agente,)
        sql += " ORDER BY criado_em DESC, id DESC"
        linhas = self._consultar(sql, args)
        if not apenas_ultimos:
            return linhas
        vistos: set[str] = set()
        ultimos = []
        for l in linhas:
            if l["agente"] not in vistos:
                vistos.add(l["agente"])
                ultimos.append(l)
        return ultimos

    # ------------------------------------------------------------- execuções
    def iniciar_execucao(self, slug: str, backend: str) -> int:
        cur = self._exec(
            "INSERT INTO execucoes(slug, backend, status, iniciado_em) VALUES (?,?,?,?)",
            (slug, backend, "rodando", agora()),
        )
        return int(cur.lastrowid)

    def registrar(self, execucao: int, evento: dict[str, Any]) -> None:
        with self._lock:
            linha = self._con.execute("SELECT log FROM execucoes WHERE id=?", (execucao,)).fetchone()
            log = json.loads(linha["log"]) if linha else []
            log.append({"em": agora(), **evento})
            self._con.execute("UPDATE execucoes SET log=? WHERE id=?", (json.dumps(log, ensure_ascii=False), execucao))
            self._con.commit()

    def concluir_execucao(self, execucao: int, status: str) -> None:
        self._exec("UPDATE execucoes SET status=?, concluido_em=? WHERE id=?", (status, agora(), execucao))

    def execucao(self, execucao: int) -> dict[str, Any] | None:
        linhas = self._consultar("SELECT * FROM execucoes WHERE id=?", (execucao,))
        if not linhas:
            return None
        e = linhas[0]
        e["log"] = json.loads(e["log"])
        return e
