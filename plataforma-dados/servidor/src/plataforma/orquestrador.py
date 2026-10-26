"""Orquestração: do discovery à proposta.

    respostas -> Analista de Negócios -> Arquiteto -> DBA -> Engenheiro -> Analista
              -> Cientista -> Full Stack -> Cyber -> DevOps -> FinOps -> Comercial -> proposta

Cada agente recebe: o objetivo e as perguntas de negócio do cliente, as
respostas marcadas para ele, os sinais, a estimativa de custos (quando usa),
os entregáveis dos agentes de que depende e trechos recuperados da memória
vetorial. O resultado é salvo no SQLite e indexado na coleção `clientes`.
"""

from __future__ import annotations

import re
import threading
import unicodedata
from pathlib import Path
from typing import Any

from . import agentes as ag
from . import custos, llm as llm_mod, precificacao
from .config import Config
from .questionario import Questionario, preenchida
from .store import Store
from .vetorial import MemoriaVetorial, criar_embedder, criar_indice


def slugificar(texto: str) -> str:
    t = unicodedata.normalize("NFD", texto or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:80]


INSTRUCOES_SAIDA = (
    "Responda em português do Brasil, em Markdown, seguindo a seção 'Formato de entrega' do seu papel. "
    "Use os números da calculadora de custos quando houver; não invente preços. "
    "Marque suposições com [PREMISSA] e dúvidas que precisam do cliente com [PERGUNTA]. "
    "Seja específico para este cliente: cite as respostas que fundamentam cada decisão."
)


class Plataforma:
    def __init__(self, cfg: Config, memoria: MemoriaVetorial | None = None, store: Store | None = None):
        self.cfg = cfg
        self.store = store or Store(cfg.banco)
        self.memoria = memoria or MemoriaVetorial(
            criar_indice(cfg.qdrant_url, cfg.qdrant_api_key), criar_embedder(cfg.ollama_url, cfg.modelo_embedding)
        )
        self._q: tuple[float, Questionario] | None = None
        self._execucoes: dict[int, threading.Thread] = {}

    # ---------------------------------------------------------- questionário
    @property
    def questionario(self) -> Questionario:
        mtime = self.cfg.questionario.stat().st_mtime
        if not self._q or self._q[0] != mtime:
            self._q = (mtime, Questionario.carregar(self.cfg.questionario))
        return self._q[1]

    def precos(self) -> dict[str, Any]:
        return custos.carregar_precos(Path(__file__).parent / "dados" / "precos.yaml")

    def tabela_precos(self) -> dict[str, Any]:
        return precificacao.carregar(Path(__file__).parent / "dados" / "precificacao.yaml")

    def resumo_precos(self) -> str:
        cfg = self.tabela_precos()
        aliq = precificacao.aliquota(cfg)
        taxas = ", ".join(f"{p} R$ {precificacao.taxa_perfil(cfg, p)}" for p in cfg["multiplicador_perfil"])
        mensal = ", ".join(f"{p} R$ {precificacao.precificar_mensalidade(p, cfg)['mensalidade']:,.0f}".replace(",", ".") for p in precificacao.PORTES)
        diag = ", ".join(f"{p} R$ {precificacao.precificar_diagnostico(p, cfg)['preco']:,.0f}".replace(",", ".") for p in precificacao.PORTES)
        return (
            f"Taxa líquida por hora: {taxas}. Gestão {cfg['gestao']:.0%}; risco baixa/média/alta "
            f"{'/'.join(f'{v:.0%}' for v in cfg['risco'].values())}; impostos {aliq:.2%} (por dentro).\n"
            f"Mensalidade gerenciada: {mensal}. Diagnóstico pago: {diag}.\n"
            "Calcule o preço do projeto com a ferramenta preco_estimar (some as horas estimadas pelos agentes, por perfil); "
            "exemplos completos em docs/11-precificacao.md."
        )

    # ------------------------------------------------------------- discovery
    def salvar_discovery(self, empresa: str, respostas: dict[str, Any], slug: str | None = None) -> dict[str, Any]:
        q = self.questionario
        slug = slugificar(slug or empresa)
        if not slug:
            raise ValueError("Informe o nome da empresa.")
        normalizadas: dict[str, Any] = {}
        avisos: list[str] = []
        for pid, valor in respostas.items():
            if pid not in q.perguntas:
                avisos.append(f"Ignorada (não existe no questionário): {pid}")
                continue
            if not preenchida(valor):
                continue
            try:
                normalizadas[pid] = q.normalizar(pid, valor)
            except ValueError as e:
                avisos.append(str(e))
        limpas = q.limpar_orfas(normalizadas)
        avisos += [f"Removida (ramo não escolhido): {pid}" for pid in normalizadas if pid not in limpas]
        self.store.salvar_respostas(slug, empresa, limpas, q.meta.get("versao"))
        try:
            self.memoria.indexar("clientes", "discovery", f"# Discovery — {empresa}\n\n{q.resumo(limpas)}",
                                 {"cliente": slug, "tipo": "discovery"})
        except Exception as e:  # memória vetorial fora do ar não impede salvar
            avisos.append(f"Memória vetorial indisponível: {e}")
        return {"slug": slug, "respostas": len(limpas), "progresso": q.progresso(limpas), "avisos": avisos}

    def responder(self, slug: str, pergunta: str, valor: Any) -> dict[str, Any]:
        cliente = self.store.cliente(slug)
        if not cliente:
            raise KeyError(f"Cliente não encontrado: {slug}")
        r = self.store.respostas(slug)
        r[pergunta] = self.questionario.normalizar(pergunta, valor)
        return self.salvar_discovery(cliente["empresa"], r, slug)

    # --------------------------------------------------------------- custos
    def estimar_custos(self, slug: str | None = None, **ajustes: Any) -> dict[str, Any]:
        if slug:
            r = self.store.respostas(slug)
            perfil = custos.perfil_de_respostas(r, self.questionario.sinais(r))
        else:
            perfil = custos.PerfilCarga()
        for k, v in ajustes.items():
            if v is not None and hasattr(perfil, k):
                setattr(perfil, k, v)
        return custos.estimar(perfil, self.precos(), cambio=self.cfg.cambio_usd_brl, tarifa_kwh=self.cfg.tarifa_kwh_brl)

    # ------------------------------------------------------------- contexto
    def contexto(self, slug: str, agente: str, local: bool = False) -> dict[str, str]:
        a = ag.resolver(agente)
        perfil = ag.carregar_perfil(self.cfg.raiz, a.id)
        cliente = self.store.cliente(slug)
        if not cliente:
            raise KeyError(f"Cliente não encontrado: {slug}")
        q = self.questionario
        r = self.store.respostas(slug)
        limite_entregavel = 2_500 if local else 40_000
        limite_rag = 4 if local else 8

        sistema = f"{perfil.papel}\n\n---\n\n# Skill\n\n{perfil.skill}".strip()
        if local:
            sistema = ag.cortar(sistema, 14_000)

        partes = [f"# Cliente: {cliente['empresa']}  (`{slug}`)"]
        partes.append("## Objetivo da plataforma\n" + str(r.get("obj.objetivo", "[PERGUNTA] Objetivo ainda não informado.")))
        partes.append("## Perguntas de negócio a responder\n" + str(r.get("obj.perguntas", "[PERGUNTA] Perguntas ainda não informadas.")))
        partes.append(f"## Respostas do discovery relevantes para {a.nome}\n" + (q.resumo(r, a.id) or "Nenhuma resposta ainda."))
        sinais = q.sinais(r)
        if sinais:
            partes.append("## Sinais acumulados\n" + ", ".join(f"{k}: {v:+g}" for k, v in sorted(sinais.items())))
        if a.usa_custos:
            est = self.estimar_custos(slug)
            partes.append(
                "## Estimativa de custos (calculadora determinística)\n"
                + est["tabela_markdown"] + "\n\nPremissas:\n" + "\n".join(f"- {p}" for p in est["premissas"])
                + f"\n\nRecomendação da calculadora: **{est['recomendacao']}**; mais barato: **{est['mais_barato']}**."
            )
        if a.id == "comercial":
            partes.append("## Tabela de preços da consultoria (calculadora)\n" + self.resumo_precos())
        anteriores = {e["agente"]: e for e in self.store.entregaveis(slug)}
        blocos = []
        for dep in a.depende_de:
            if dep in anteriores:
                e = anteriores[dep]
                blocos.append(f"### {ag.POR_ID[dep].nome}: {e['titulo']}\n{ag.cortar(e['conteudo'], limite_entregavel)}")
        if blocos:
            partes.append("## Entregáveis dos agentes anteriores\n" + "\n\n".join(blocos))
        trechos = []
        try:
            for consulta in (*a.consultas_rag, *ag.consultas_do_cliente(a, r)):
                for res in self.memoria.buscar(consulta, "conhecimento", limite=limite_rag // 2):
                    trechos.append(f"- ({res.metadados.get('origem')}) {ag.cortar(res.texto, 700)}")
            for res in self.memoria.buscar("lições aprendidas " + str(r.get("neg.segmento", "")), "projetos", limite=2):
                trechos.append(f"- (projeto anterior) {ag.cortar(res.texto, 700)}")
        except Exception:
            trechos.append("- (memória vetorial indisponível nesta execução)")
        if trechos:
            partes.append("## Conhecimento de referência (memória vetorial)\n" + "\n".join(dict.fromkeys(trechos)))
        partes.append(f"## Sua tarefa\nProduza o entregável **{a.entrega}**. {INSTRUCOES_SAIDA}")
        return {"agente": a.id, "nome": a.nome, "entrega": a.entrega, "sistema": sistema, "usuario": "\n\n".join(partes)}

    # ------------------------------------------------------------- execução
    def salvar_entregavel(self, slug: str, agente: str, conteudo: str, modelo: str | None = None, titulo: str | None = None) -> int:
        a = ag.resolver(agente)
        if not self.store.cliente(slug):
            raise KeyError(f"Cliente não encontrado: {slug}")
        eid = self.store.salvar_entregavel(slug, a.id, titulo or a.entrega, conteudo, modelo)
        try:
            self.memoria.indexar("clientes", f"entregavel:{a.id}", f"# {a.nome} — {titulo or a.entrega}\n\n{conteudo}",
                                 {"cliente": slug, "tipo": "entregavel", "agente": a.id})
        except Exception:
            pass
        return eid

    def executar_agente(self, slug: str, agente: str, modelo: llm_mod.LLM) -> int:
        ctx = self.contexto(slug, agente, local=modelo.nome.startswith("ollama"))
        texto = modelo.gerar(ctx["sistema"], ctx["usuario"])
        return self.salvar_entregavel(slug, ctx["agente"], texto, modelo.nome)

    def executar_pipeline(self, slug: str, agentes: list[str] | None = None, backend: str | None = None,
                          em_segundo_plano: bool = True) -> int:
        modelo = llm_mod.criar(self.cfg, backend)
        if modelo is None:
            raise llm_mod.ErroLLM(
                "LLM_BACKEND=nenhum: use agente_contexto + entregavel_salvar a partir do seu cliente MCP, "
                "ou rode com backend='ollama' ou 'anthropic'."
            )
        if not self.store.cliente(slug):
            raise KeyError(f"Cliente não encontrado: {slug}")
        ordem = [ag.resolver(x).id for x in agentes] if agentes else list(ag.ORDEM_PIPELINE)
        ordem.sort(key=lambda x: ag.POR_ID[x].ordem)
        execucao = self.store.iniciar_execucao(slug, modelo.nome)

        def rodar() -> None:
            status = "concluida"
            for aid in ordem:
                self.store.registrar(execucao, {"agente": aid, "evento": "inicio"})
                try:
                    eid = self.executar_agente(slug, aid, modelo)
                    self.store.registrar(execucao, {"agente": aid, "evento": "ok", "entregavel": eid})
                except Exception as e:
                    status = "com_erros"
                    self.store.registrar(execucao, {"agente": aid, "evento": "erro", "erro": str(e)})
            self.store.concluir_execucao(execucao, status)

        if em_segundo_plano:
            t = threading.Thread(target=rodar, name=f"pipeline-{execucao}", daemon=True)
            self._execucoes[execucao] = t
            t.start()
        else:
            rodar()
        return execucao

    # -------------------------------------------------------------- proposta
    def proposta(self, slug: str) -> str:
        cliente = self.store.cliente(slug)
        if not cliente:
            raise KeyError(f"Cliente não encontrado: {slug}")
        entregas = {e["agente"]: e for e in self.store.entregaveis(slug)}
        est = self.estimar_custos(slug)
        r = self.store.respostas(slug)
        linhas = [
            f"# Proposta — Plataforma de Dados para {cliente['empresa']}",
            f"_Preparada por {self.cfg.marca}_",
            "## Objetivo",
            str(r.get("obj.objetivo", "—")),
            "## Perguntas que a plataforma vai responder",
            str(r.get("obj.perguntas", "—")),
        ]
        if "comercial" in entregas:
            linhas += ["## Resumo comercial", entregas["comercial"]["conteudo"]]
        linhas += ["## Comparativo de custos (mensal)", est["tabela_markdown"], "", *[f"- {p}" for p in est["premissas"]]]
        for aid in ag.ORDEM_PIPELINE:
            if aid in entregas and aid != "comercial":
                e = entregas[aid]
                linhas += [f"## {ag.POR_ID[aid].nome} — {e['titulo']}", e["conteudo"]]
        faltando = [ag.POR_ID[x].nome for x in ag.ORDEM_PIPELINE if x not in entregas]
        if faltando:
            linhas += ["## Pendências", "Ainda sem entregável: " + ", ".join(faltando) + "."]
        return "\n\n".join(linhas)
