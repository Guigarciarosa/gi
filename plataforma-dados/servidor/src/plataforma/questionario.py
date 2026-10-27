"""Motor do questionário ramificado.

Lê `questionario/questionario.yaml`, achata a árvore (seção → pergunta → opção →
subpergunta) em uma lista ordenada e decide, a partir das respostas, quais
perguntas estão visíveis, quais faltam e quais sinais foram acumulados.

A mesma lógica existe em JavaScript no app web (web/questionario.html); os
testes garantem que as duas leiam a mesma estrutura exportada por `para_json`.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

TIPOS = {"texto", "texto_longo", "numero", "unica", "multipla", "escala", "sim_nao"}
OPCOES_SIM_NAO = (("sim", "Sim"), ("nao", "Não"))

Resposta = str | int | float | list[str]


@dataclass
class Opcao:
    valor: str
    rotulo: str
    sinais: dict[str, float] = field(default_factory=dict)
    subperguntas: list[str] = field(default_factory=list)


@dataclass
class Pergunta:
    id: str
    texto: str
    tipo: str
    secao: str
    ordem: int
    profundidade: int
    obrigatoria: bool = False
    agentes: list[str] = field(default_factory=list)
    opcoes: list[Opcao] = field(default_factory=list)
    mostrar_se: dict[str, Any] | None = None
    sinais: dict[str, float] = field(default_factory=dict)
    pais: list[tuple[str, str]] = field(default_factory=list)
    minimo: int | None = None
    maximo: int | None = None

    def opcao(self, valor: str) -> Opcao | None:
        return next((o for o in self.opcoes if o.valor == valor), None)


def _escolhidas(valor: Resposta | None) -> list[str]:
    if valor is None or valor == "" or valor == []:
        return []
    if isinstance(valor, list):
        return [str(v) for v in valor]
    return [str(valor)]


def preenchida(valor: Resposta | None) -> bool:
    if valor is None:
        return False
    if isinstance(valor, str):
        return valor.strip() != ""
    if isinstance(valor, list):
        return len(valor) > 0
    return True


class Questionario:
    def __init__(self, bruto: dict[str, Any]):
        self.meta: dict[str, Any] = bruto.get("meta", {})
        self.secoes: list[dict[str, Any]] = []
        self.perguntas: dict[str, Pergunta] = {}
        self._ordem: list[str] = []
        for secao in bruto["secoes"]:
            self.secoes.append({k: secao.get(k) for k in ("id", "titulo", "descricao")})
            for p in secao.get("perguntas", []):
                self._registrar(p, secao["id"], profundidade=0, pai=None)

    # ------------------------------------------------------------------ carga
    @classmethod
    def carregar(cls, caminho: Path | str) -> "Questionario":
        with open(caminho, encoding="utf-8") as f:
            return cls(yaml.safe_load(f))

    def _registrar(self, bruto: dict[str, Any], secao: str, profundidade: int, pai: tuple[str, str] | None) -> str:
        pid = bruto["id"]
        if pid in self.perguntas:
            # Mesma pergunta referenciada por âncora YAML em várias opções:
            # basta acrescentar o novo caminho de visibilidade.
            if pai and pai not in self.perguntas[pid].pais:
                self.perguntas[pid].pais.append(pai)
            return pid

        tipo = bruto.get("tipo", "texto")
        if tipo not in TIPOS:
            raise ValueError(f"{pid}: tipo desconhecido '{tipo}'")

        brutas = copy.deepcopy(bruto.get("opcoes", []))
        if tipo == "sim_nao":
            brutas = [
                {"valor": v, "rotulo": r, "subperguntas": bruto.get(f"se_{v}", []) or []}
                for v, r in OPCOES_SIM_NAO
            ]

        pergunta = Pergunta(
            id=pid,
            texto=bruto["texto"],
            tipo="unica" if tipo == "sim_nao" else tipo,
            secao=secao,
            ordem=len(self._ordem),
            profundidade=profundidade,
            obrigatoria=bool(bruto.get("obrigatoria", False)),
            agentes=list(bruto.get("agentes", [])),
            mostrar_se=bruto.get("mostrar_se"),
            sinais=dict(bruto.get("sinais", {})),
            pais=[pai] if pai else [],
            minimo=bruto.get("min"),
            maximo=bruto.get("max"),
        )
        self.perguntas[pid] = pergunta
        self._ordem.append(pid)

        for ob in brutas:
            opcao = Opcao(valor=str(ob["valor"]), rotulo=ob["rotulo"], sinais=dict(ob.get("sinais", {})))
            pergunta.opcoes.append(opcao)
            for sub in ob.get("subperguntas", []) or []:
                opcao.subperguntas.append(
                    self._registrar(sub, secao, profundidade + 1, pai=(pid, opcao.valor))
                )
        return pid

    # ---------------------------------------------------------- visibilidade
    def visivel(self, pid: str, respostas: dict[str, Resposta], _cache: dict[str, bool] | None = None) -> bool:
        cache = {} if _cache is None else _cache
        if pid in cache:
            return cache[pid]
        cache[pid] = False  # protege contra ciclos
        p = self.perguntas[pid]
        ok = True
        if p.pais:
            ok = any(
                self.visivel(pai, respostas, cache) and valor in _escolhidas(respostas.get(pai))
                for pai, valor in p.pais
            )
        if ok and p.mostrar_se:
            ok = self._avaliar(p.mostrar_se, respostas, cache)
        cache[pid] = ok
        return ok

    def _avaliar(self, cond: dict[str, Any], respostas: dict[str, Resposta], cache: dict[str, bool]) -> bool:
        if "qualquer" in cond:
            return any(self._avaliar(c, respostas, cache) for c in cond["qualquer"])
        if "todas" in cond:
            return all(self._avaliar(c, respostas, cache) for c in cond["todas"])
        if "nao" in cond:
            return not self._avaliar(cond["nao"], respostas, cache)
        alvo = cond["pergunta"]
        if alvo not in self.perguntas:
            raise KeyError(f"mostrar_se referencia pergunta inexistente: {alvo}")
        if not self.visivel(alvo, respostas, cache):
            return False
        valor = respostas.get(alvo)
        if "em" in cond:
            esperadas = {str(v) for v in cond["em"]}
            return bool(esperadas.intersection(_escolhidas(valor)))
        if "preenchida" in cond:
            return preenchida(valor) == bool(cond["preenchida"])
        if "maior_que" in cond:
            try:
                return float(valor) > float(cond["maior_que"])  # type: ignore[arg-type]
            except (TypeError, ValueError):
                return False
        raise ValueError(f"Condição inválida: {cond}")

    def visiveis(self, respostas: dict[str, Resposta]) -> list[Pergunta]:
        cache: dict[str, bool] = {}
        return [self.perguntas[pid] for pid in self._ordem if self.visivel(pid, respostas, cache)]

    def pendentes(self, respostas: dict[str, Resposta], apenas_obrigatorias: bool = False) -> list[Pergunta]:
        return [
            p
            for p in self.visiveis(respostas)
            if not preenchida(respostas.get(p.id)) and (p.obrigatoria or not apenas_obrigatorias)
        ]

    def limpar_orfas(self, respostas: dict[str, Resposta]) -> dict[str, Resposta]:
        """Remove respostas de perguntas que deixaram de ser visíveis
        (ex.: o cliente trocou o segmento e as subperguntas antigas sumiram)."""
        atual = dict(respostas)
        while True:
            visiveis = {p.id for p in self.visiveis(atual)}
            orfas = [pid for pid in atual if pid in self.perguntas and pid not in visiveis]
            if not orfas:
                return atual
            for pid in orfas:
                atual.pop(pid)

    # -------------------------------------------------------------- respostas
    def normalizar(self, pid: str, valor: Any) -> Resposta:
        if pid not in self.perguntas:
            raise KeyError(f"Pergunta inexistente: {pid}")
        p = self.perguntas[pid]
        validas = {o.valor for o in p.opcoes}
        if p.tipo == "unica":
            v = str(valor)
            if v not in validas:
                rotulos = {o.rotulo.lower(): o.valor for o in p.opcoes}
                if v.lower() in rotulos:
                    return rotulos[v.lower()]
                raise ValueError(f"{pid}: '{v}' não é opção válida ({sorted(validas)})")
            return v
        if p.tipo == "multipla":
            itens = valor if isinstance(valor, list) else [x.strip() for x in str(valor).split(",") if x.strip()]
            itens = [str(i) for i in itens]
            invalidas = [i for i in itens if i not in validas]
            if invalidas:
                raise ValueError(f"{pid}: opções inválidas {invalidas} (válidas: {sorted(validas)})")
            return list(dict.fromkeys(itens))
        if p.tipo == "numero":
            try:
                texto = str(valor).strip()
                if "," in texto:  # formato brasileiro: 1.500,50
                    texto = texto.replace(".", "").replace(",", ".")
                n = float(texto)
            except ValueError as e:
                raise ValueError(f"{pid}: esperado número, recebido '{valor}'") from e
            return int(n) if n.is_integer() else n
        if p.tipo == "escala":
            n = int(valor)
            lo, hi = p.minimo or 1, p.maximo or 5
            if not lo <= n <= hi:
                raise ValueError(f"{pid}: escala vai de {lo} a {hi}")
            return str(n)
        return str(valor).strip()

    def formatar(self, pid: str, valor: Resposta) -> str:
        p = self.perguntas[pid]
        if p.tipo in ("unica", "multipla"):
            rotulos = [(p.opcao(v).rotulo if p.opcao(v) else v) for v in _escolhidas(valor)]
            return "; ".join(rotulos)
        return str(valor)

    def sinais(self, respostas: dict[str, Resposta]) -> dict[str, float]:
        total: dict[str, float] = {}

        def somar(d: dict[str, float]) -> None:
            for k, v in d.items():
                total[k] = total.get(k, 0) + float(v)

        for p in self.visiveis(respostas):
            valor = respostas.get(p.id)
            if not preenchida(valor):
                continue
            somar(p.sinais)
            for v in _escolhidas(valor) if p.tipo in ("unica", "multipla") else []:
                if (o := p.opcao(v)) is not None:
                    somar(o.sinais)
        return total

    def progresso(self, respostas: dict[str, Resposta]) -> dict[str, Any]:
        visiveis = self.visiveis(respostas)
        por_secao: dict[str, dict[str, int]] = {}
        for p in visiveis:
            s = por_secao.setdefault(p.secao, {"visiveis": 0, "respondidas": 0, "obrigatorias_faltando": 0})
            s["visiveis"] += 1
            if preenchida(respostas.get(p.id)):
                s["respondidas"] += 1
            elif p.obrigatoria:
                s["obrigatorias_faltando"] += 1
        respondidas = sum(s["respondidas"] for s in por_secao.values())
        return {
            "visiveis": len(visiveis),
            "respondidas": respondidas,
            "percentual": round(100 * respondidas / len(visiveis), 1) if visiveis else 0.0,
            "obrigatorias_faltando": [p.id for p in self.pendentes(respostas, apenas_obrigatorias=True)],
            "por_secao": por_secao,
        }

    def resumo(self, respostas: dict[str, Resposta], agente: str | None = None) -> str:
        """Respostas em Markdown, agrupadas por seção. Com `agente`, só as
        perguntas marcadas para ele (o objetivo da plataforma vai sempre)."""
        titulos = {s["id"]: s["titulo"] for s in self.secoes}
        linhas: list[str] = []
        secao_atual = None
        for p in self.visiveis(respostas):
            valor = respostas.get(p.id)
            if not preenchida(valor):
                continue
            if agente and agente not in p.agentes and p.secao != "objetivo":
                continue
            if p.secao != secao_atual:
                secao_atual = p.secao
                linhas.append(f"\n### {titulos.get(p.secao, p.secao)}")
            recuo = "  " * p.profundidade
            linhas.append(f"{recuo}- **{p.texto}** {self.formatar(p.id, valor)}  `[{p.id}]`")
        return "\n".join(linhas).strip()

    # ------------------------------------------------------------ exportação
    def para_json(self) -> dict[str, Any]:
        # Pesos achatados ("id" e "id=valor") para o app web somar sinais sem
        # carregar a árvore inteira.
        pesos: dict[str, dict[str, float]] = {}
        for p in self.perguntas.values():
            if p.sinais:
                pesos[p.id] = p.sinais
            for o in p.opcoes:
                if o.sinais:
                    pesos[f"{p.id}={o.valor}"] = o.sinais
        return {
            "meta": self.meta,
            "secoes": self.secoes,
            "pesos": pesos,
            "perguntas": [
                {
                    "id": p.id,
                    "texto": p.texto,
                    "tipo": p.tipo,
                    "secao": p.secao,
                    "profundidade": p.profundidade,
                    "obrigatoria": p.obrigatoria,
                    "agentes": p.agentes,
                    "mostrar_se": p.mostrar_se,
                    "pais": [list(x) for x in p.pais],
                    "min": p.minimo,
                    "max": p.maximo,
                    "opcoes": [{"valor": o.valor, "rotulo": o.rotulo} for o in p.opcoes],
                }
                for p in (self.perguntas[i] for i in self._ordem)
            ],
        }

    def estatisticas(self) -> dict[str, Any]:
        ramificadas = [p for p in self.perguntas.values() if p.pais or p.mostrar_se]
        return {
            "secoes": len(self.secoes),
            "perguntas": len(self.perguntas),
            "condicionais": len(ramificadas),
            "profundidade_maxima": max(p.profundidade for p in self.perguntas.values()),
            "opcoes": sum(len(p.opcoes) for p in self.perguntas.values()),
        }
