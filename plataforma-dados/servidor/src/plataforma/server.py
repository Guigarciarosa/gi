"""Servidor MCP da plataforma (roda no ZimaOS).

Expõe, no mesmo processo:
  /mcp                 MCP (Streamable HTTP) para Claude Desktop, Claude Code,
                       Open WebUI, n8n ou qualquer cliente MCP
  /                    app web do questionário (para o cliente responder)
  /api/...             API REST usada pelo app web

Rodar:  python -m plataforma.server            (HTTP, porta 8787)
        python -m plataforma.server --stdio    (stdio, para Claude Desktop local)
"""

from __future__ import annotations

import argparse
import json
from http.cookies import SimpleCookie
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

import httpx2 as httpx
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response

from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

from . import __version__
from . import agentes as ag
from .config import carregar
from .llm import ErroLLM
from .orquestrador import Plataforma, slugificar
from .questionario import preenchida

CFG = carregar()
_PLATAFORMA: Plataforma | None = None
WEB = Path(__file__).parent / "web"


def plataforma() -> Plataforma:
    global _PLATAFORMA
    if _PLATAFORMA is None:
        _PLATAFORMA = Plataforma(CFG)
    return _PLATAFORMA


INSTRUCOES = f"""Servidor da plataforma de dados {CFG.marca}. Fluxo de trabalho:
1. cliente_criar ou cliente_listar para escolher o cliente (slug).
2. Discovery: discovery_proximas devolve as próximas perguntas visíveis (a árvore se ramifica
   conforme as respostas); discovery_responder grava cada resposta. Para respostas vindas do
   app web, use discovery_importar.
3. Agentes (ordem: negocios, arquiteto, engenheiro, analista, cientista, cyber, devops, finops,
   comercial). Para atuar como um agente: agente_contexto -> raciocine -> entregavel_salvar.
   Ou pipeline_executar para o servidor rodar todos com o LLM configurado.
4. custos_estimar faz as contas de AWS/GCP/Azure/OCI/on-premise; nunca invente preços.
5. proposta_gerar consolida tudo.
Memória: memoria_buscar / memoria_indexar (coleções conhecimento, clientes, projetos, marca)."""

mcp = MCPServer(name="plataforma-dados", title=f"{CFG.marca} — Plataforma de Dados", version=__version__, instructions=INSTRUCOES)


def _formatar_pergunta(p: Any, q: Any) -> dict[str, Any]:
    d: dict[str, Any] = {"id": p.id, "texto": p.texto, "tipo": p.tipo, "secao": p.secao, "obrigatoria": p.obrigatoria}
    if p.opcoes:
        d["opcoes"] = [
            {"valor": o.valor, "rotulo": o.rotulo, **({"abre": len(o.subperguntas)} if o.subperguntas else {})}
            for o in p.opcoes
        ]
    if p.tipo == "escala":
        d["escala"] = [p.minimo or 1, p.maximo or 5]
    return d


# ===================================================================== tools
@mcp.tool()
def plataforma_saude() -> dict[str, Any]:
    """Verifica banco, memória vetorial, Ollama e backend de LLM configurado."""
    p = plataforma()
    estado: dict[str, Any] = {"versao": __version__, "marca": CFG.marca, "llm_backend": CFG.llm_backend}
    try:
        estado["clientes"] = len(p.store.clientes())
        estado["banco"] = "ok"
    except Exception as e:
        estado["banco"] = f"erro: {e}"
    try:
        estado["memoria"] = p.memoria.estatisticas()
    except Exception as e:
        estado["memoria"] = f"indisponível: {e}"
    if CFG.modelo_embedding != "hash" or CFG.llm_backend == "ollama":
        try:
            r = httpx.get(f"{CFG.ollama_url}/api/tags", timeout=5)
            estado["ollama_modelos"] = [m["name"] for m in r.json().get("models", [])]
        except Exception as e:
            estado["ollama"] = f"indisponível: {e}"
    return estado


@mcp.tool()
def questionario_estrutura(secao: str | None = None) -> dict[str, Any]:
    """Sem `secao`: lista as seções e estatísticas. Com `secao` (ex.: 'negocio'):
    todas as perguntas da seção, inclusive as condicionais, com suas opções."""
    q = plataforma().questionario
    if not secao:
        return {"meta": q.meta, "estatisticas": q.estatisticas(), "secoes": q.secoes}
    perguntas = [p for p in q.perguntas.values() if p.secao == secao]
    if not perguntas:
        raise ValueError(f"Seção inexistente: {secao}. Seções: {[s['id'] for s in q.secoes]}")
    return {
        "secao": secao,
        "perguntas": [
            {**_formatar_pergunta(p, q), "profundidade": p.profundidade, "aparece_quando": p.pais or p.mostrar_se or "sempre"}
            for p in perguntas
        ],
    }


@mcp.tool()
def cliente_listar() -> list[dict[str, Any]]:
    """Lista os clientes cadastrados, com data do discovery e número de entregáveis."""
    return plataforma().store.clientes()


@mcp.tool()
def cliente_criar(empresa: str) -> dict[str, Any]:
    """Cadastra um cliente e devolve o slug usado nas demais ferramentas."""
    slug = slugificar(empresa)
    if not slug:
        raise ValueError("Nome de empresa vazio.")
    p = plataforma()
    if not p.store.cliente(slug):
        p.salvar_discovery(empresa, {"id.empresa": empresa}, slug)
    return {"slug": slug, "empresa": empresa}


@mcp.tool()
def discovery_proximas(slug: str, limite: int = 8, apenas_obrigatorias: bool = False) -> dict[str, Any]:
    """Próximas perguntas visíveis e ainda sem resposta, na ordem do questionário.
    Use para conduzir o discovery por conversa: pergunte, grave com
    discovery_responder e chame de novo (novas perguntas se abrem conforme as escolhas)."""
    p = plataforma()
    q = p.questionario
    r = p.store.respostas(slug)
    pend = q.pendentes(r, apenas_obrigatorias)
    return {
        "progresso": q.progresso(r),
        "proximas": [_formatar_pergunta(x, q) for x in pend[:limite]],
        "restantes": max(0, len(pend) - limite),
    }


@mcp.tool()
def discovery_responder(slug: str, pergunta_id: str, resposta: str | list[str] | int | float) -> dict[str, Any]:
    """Grava uma resposta. `unica`: o valor da opção; `multipla`: lista de valores;
    `escala`/`numero`: número; textos: string. Devolve as perguntas que se abriram."""
    p = plataforma()
    q = p.questionario
    antes = {x.id for x in q.visiveis(p.store.respostas(slug))}
    res = p.responder(slug, pergunta_id, resposta)
    depois = q.visiveis(p.store.respostas(slug))
    abertas = [_formatar_pergunta(x, q) for x in depois if x.id not in antes]
    return {"gravada": pergunta_id, "abertas": abertas, "avisos": res["avisos"], "percentual": res["progresso"]["percentual"]}


@mcp.tool()
def discovery_importar(empresa: str, respostas: dict[str, Any] | str) -> dict[str, Any]:
    """Importa respostas (o JSON exportado pelo app web, ou só o objeto `respostas`)."""
    dados = json.loads(respostas) if isinstance(respostas, str) else respostas
    if "respostas" in dados and isinstance(dados["respostas"], dict):
        empresa = dados.get("empresa") or empresa
        dados = dados["respostas"]
    return plataforma().salvar_discovery(empresa, dados)


@mcp.tool()
def discovery_resumo(slug: str, agente: str | None = None) -> dict[str, Any]:
    """Respostas em Markdown (todas ou só as do `agente`), progresso e sinais."""
    p = plataforma()
    q = p.questionario
    r = p.store.respostas(slug)
    return {
        "markdown": q.resumo(r, ag.resolver(agente).id if agente else None),
        "progresso": q.progresso(r),
        "sinais": q.sinais(r),
    }


@mcp.tool()
def agente_listar() -> list[dict[str, Any]]:
    """Os 9 agentes, na ordem do pipeline, com entregável e dependências."""
    return [
        {"id": a.id, "nome": a.nome, "ordem": a.ordem, "entrega": a.entrega, "depende_de": list(a.depende_de), "usa_custos": a.usa_custos}
        for a in sorted(ag.AGENTES, key=lambda x: x.ordem)
    ]


@mcp.tool()
def agente_perfil(agente: str) -> dict[str, Any]:
    """Papel (AGENT.md), skill (SKILL.md) e referências de um agente."""
    pf = ag.carregar_perfil(CFG.raiz, agente)
    return {"id": pf.agente.id, "nome": pf.agente.nome, "papel": pf.papel, "skill": pf.skill, "referencias": pf.referencias}


@mcp.tool()
def agente_contexto(slug: str, agente: str) -> dict[str, str]:
    """Monta o contexto completo para VOCÊ atuar como o agente: `sistema` (papel + skill)
    e `usuario` (respostas, sinais, custos, entregáveis anteriores e memória). Siga o
    `sistema`, produza o entregável pedido no fim de `usuario` e grave com entregavel_salvar."""
    return plataforma().contexto(slug, agente)


@mcp.tool()
def entregavel_salvar(slug: str, agente: str, conteudo: str, titulo: str | None = None, modelo: str | None = None) -> dict[str, Any]:
    """Grava o entregável de um agente (Markdown) e indexa na memória do cliente."""
    eid = plataforma().salvar_entregavel(slug, agente, conteudo, modelo, titulo)
    return {"id": eid, "agente": ag.resolver(agente).id}


@mcp.tool()
def entregavel_listar(slug: str, historico: bool = False) -> list[dict[str, Any]]:
    """Entregáveis do cliente (o mais recente de cada agente, ou todo o histórico)."""
    itens = plataforma().store.entregaveis(slug, apenas_ultimos=not historico)
    return [{k: v for k, v in e.items() if k != "conteudo"} | {"tamanho": len(e["conteudo"])} for e in itens]


@mcp.tool()
def entregavel_obter(slug: str, agente: str) -> dict[str, Any]:
    """Conteúdo do entregável mais recente de um agente."""
    itens = plataforma().store.entregaveis(slug, ag.resolver(agente).id)
    if not itens:
        raise ValueError("Esse agente ainda não produziu entregável para este cliente.")
    return itens[0]


@mcp.tool()
def pipeline_executar(slug: str, agentes: list[str] | None = None, backend: str | None = None) -> dict[str, Any]:
    """Roda os agentes no servidor, em segundo plano, com o LLM configurado
    (`backend`: ollama ou anthropic; padrão = LLM_BACKEND). Acompanhe com pipeline_status."""
    try:
        eid = plataforma().executar_pipeline(slug, agentes, backend)
    except ErroLLM as e:
        return {"erro": str(e)}
    return {"execucao": eid, "acompanhe": "pipeline_status"}


@mcp.tool()
def pipeline_status(execucao: int) -> dict[str, Any]:
    """Situação de uma execução do pipeline e o log por agente."""
    e = plataforma().store.execucao(execucao)
    if not e:
        raise ValueError("Execução não encontrada.")
    return e


@mcp.tool()
def custos_estimar(
    slug: str | None = None,
    volume_gb: float | None = None,
    usuarios_bi: int | None = None,
    atualizacoes_dia: float | None = None,
    fontes: int | None = None,
    streaming: bool | None = None,
    ferramenta_bi: str | None = None,
    regiao_brasil: bool | None = None,
    prioridade: str | None = None,
) -> dict[str, Any]:
    """Compara AWS, GCP, Azure, OCI e on-premise: custo mensal por componente, TCO,
    ranking e premissas. Com `slug`, parte das respostas do cliente; os demais
    parâmetros sobrescrevem o perfil (simulação de cenários)."""
    return plataforma().estimar_custos(
        slug, volume_gb=volume_gb, usuarios_bi=usuarios_bi, atualizacoes_dia=atualizacoes_dia, fontes=fontes,
        streaming=streaming, ferramenta_bi=ferramenta_bi, regiao_brasil=regiao_brasil, prioridade=prioridade,
    )


@mcp.tool()
def precos_azure_consultar(servico: str, regiao: str = "brazilsouth", termo_sku: str | None = None, limite: int = 20) -> list[dict[str, Any]]:
    """Preços atuais do Azure (Retail Prices API, pública). `servico` = serviceName
    (ex.: 'Virtual Machines', 'Storage', 'Azure Synapse Analytics', 'Power BI')."""
    filtro = f"serviceName eq '{servico}' and armRegionName eq '{regiao}' and priceType eq 'Consumption'"
    if termo_sku:
        filtro += f" and contains(skuName, '{termo_sku}')"
    r = httpx.get("https://prices.azure.com/api/retail/prices", params={"$filter": filtro}, timeout=30)
    r.raise_for_status()
    itens = r.json().get("Items", [])[:limite]
    return [
        {k: i.get(k) for k in ("productName", "skuName", "meterName", "unitOfMeasure", "retailPrice", "currencyCode", "effectiveStartDate")}
        for i in itens
    ]


@mcp.tool()
def precos_oci_consultar(termo: str, moeda: str = "USD", limite: int = 20) -> list[dict[str, Any]]:
    """Preços atuais da Oracle Cloud (Price List API, pública). Filtra pelo `termo`
    no nome do produto (ex.: 'Ampere', 'Object Storage', 'Autonomous Data Warehouse')."""
    r = httpx.get("https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/", params={"currencyCode": moeda}, timeout=60)
    r.raise_for_status()
    termo_l = termo.lower()
    saida = []
    for item in r.json().get("items", []):
        if termo_l in str(item.get("displayName", "")).lower():
            precos = item.get("currencyCodeLocalizations", [{}])[0].get("prices", [])
            saida.append({
                "partNumber": item.get("partNumber"), "nome": item.get("displayName"),
                "metrica": item.get("metricName"), "precos": precos,
            })
        if len(saida) >= limite:
            break
    return saida


@mcp.tool()
def memoria_buscar(consulta: str, colecao: str = "conhecimento", cliente: str | None = None, limite: int = 6) -> list[dict[str, Any]]:
    """Busca semântica. Coleções: conhecimento, clientes (exige `cliente`), projetos, marca."""
    res = plataforma().memoria.buscar(consulta, colecao, limite, cliente)
    return [{"texto": r.texto, "pontuacao": round(r.pontuacao, 4), **r.metadados} for r in res]


@mcp.tool()
def memoria_indexar(texto: str, colecao: str, origem: str, cliente: str | None = None, tipo: str | None = None) -> dict[str, Any]:
    """Guarda um texto na memória vetorial. Reindexar a mesma `origem` substitui a versão anterior.
    Use 'projetos' para lições aprendidas ao fim de cada projeto e 'marca' para posts publicados."""
    meta = {k: v for k, v in {"cliente": cliente, "tipo": tipo}.items() if v}
    n = plataforma().memoria.indexar(colecao, origem, texto, meta)
    return {"colecao": colecao, "origem": origem, "trechos": n}


@mcp.tool()
def memoria_reindexar_base() -> dict[str, Any]:
    """Reindexa docs/, agentes/ e skills/ na coleção 'conhecimento'. Rode após editar a documentação."""
    total = plataforma().memoria.indexar_pasta(CFG.raiz, ["docs", "agentes", "skills"])
    return {"arquivos": len(total), "trechos": sum(total.values())}


@mcp.tool()
def proposta_gerar(slug: str) -> dict[str, Any]:
    """Consolida objetivo, custos e entregáveis numa proposta em Markdown e salva em
    /data/entregaveis/<slug>/proposta.md."""
    texto = plataforma().proposta(slug)
    destino = CFG.entregaveis / slug / "proposta.md"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8")
    return {"arquivo": str(destino), "caracteres": len(texto), "markdown": texto}


# ================================================================ resources
@mcp.resource("plataforma://questionario", mime_type="application/json", description="Questionário completo (estrutura achatada)")
def recurso_questionario() -> str:
    return json.dumps(plataforma().questionario.para_json(), ensure_ascii=False)


@mcp.resource("plataforma://agentes/{agente}", mime_type="text/markdown", description="Papel e skill de um agente")
def recurso_agente(agente: str) -> str:
    pf = ag.carregar_perfil(CFG.raiz, agente)
    return f"{pf.papel}\n\n---\n\n{pf.skill}"


@mcp.resource("plataforma://clientes/{slug}/proposta", mime_type="text/markdown", description="Proposta consolidada do cliente")
def recurso_proposta(slug: str) -> str:
    return plataforma().proposta(slug)


# ================================================================== prompts
@mcp.prompt()
def discovery_conversado(slug: str) -> str:
    """Conduz o discovery por conversa, uma pergunta de cada vez."""
    return (
        f"Conduza o discovery do cliente `{slug}`. Chame discovery_proximas, faça UMA pergunta por vez em linguagem "
        "simples (mostre as opções quando houver), grave com discovery_responder e repita. Quando uma resposta abrir "
        "novas perguntas, diga que vai detalhar aquele ponto. Ao chegar na seção 'objetivo', ajude o cliente a escrever "
        "o objetivo e de 3 a 5 perguntas de negócio concretas. No fim, mostre discovery_resumo."
    )


@mcp.prompt()
def atuar_como_agente(agente: str, slug: str) -> str:
    """Transforma o assistente no agente pedido, com todo o contexto do cliente."""
    ctx = plataforma().contexto(slug, agente)
    return (
        f"{ctx['sistema']}\n\n=====\n\n{ctx['usuario']}\n\n"
        f"Ao terminar, grave o resultado com entregavel_salvar(slug='{slug}', agente='{ctx['agente']}', conteudo=...)."
    )


@mcp.prompt()
def rodar_time_completo(slug: str) -> str:
    """Roda os 9 agentes em sequência dentro desta conversa."""
    ordem = ", ".join(ag.ORDEM_PIPELINE)
    return (
        f"Você vai atuar, em sequência, como cada agente da plataforma para o cliente `{slug}`: {ordem}. "
        "Para cada um: chame agente_contexto, siga o `sistema` como suas instruções, produza o entregável e grave com "
        "entregavel_salvar antes de passar ao próximo (os seguintes leem os anteriores). Use custos_estimar para números. "
        "No fim, chame proposta_gerar e apresente o sumário executivo."
    )


# =================================================================== rotas web
def _html_questionario() -> str:
    modelo = (WEB / "questionario.html").read_text(encoding="utf-8")
    dados = json.dumps(plataforma().questionario.para_json(), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    corpo = modelo.replace("/*__QUESTIONARIO__*/", dados)
    return (
        "<!doctype html><html lang=\"pt-BR\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">"
        f"</head><body>{corpo}</body></html>"
    )


@mcp.custom_route("/", methods=["GET"])
async def pagina_inicial(request: Request) -> Response:
    resp = HTMLResponse(_html_questionario())
    token = request.query_params.get("token")
    if token:
        resp.set_cookie("plataforma_token", token, httponly=True, samesite="strict", max_age=60 * 60 * 24 * 30)
    return resp


@mcp.custom_route("/api/saude", methods=["GET"])
async def api_saude(request: Request) -> Response:
    return JSONResponse({"ok": True, "versao": __version__})


@mcp.custom_route("/api/questionario", methods=["GET"])
async def api_questionario(request: Request) -> Response:
    return JSONResponse(plataforma().questionario.para_json())


@mcp.custom_route("/api/discovery", methods=["GET"])
async def api_discovery_lista(request: Request) -> Response:
    itens = [{"slug": c["slug"], "empresa": c["empresa"], "atualizado_em": c["discovery_em"]} for c in plataforma().store.clientes()]
    return JSONResponse({"itens": itens})


@mcp.custom_route("/api/discovery/{slug}", methods=["GET", "PUT"])
async def api_discovery(request: Request) -> Response:
    slug = slugificar(request.path_params["slug"])
    p = plataforma()
    if request.method == "PUT":
        corpo = await request.json()
        try:
            res = p.salvar_discovery(corpo.get("empresa") or slug, corpo.get("respostas") or {}, slug)
        except ValueError as e:
            return JSONResponse({"erro": str(e)}, status_code=400)
        return JSONResponse(res)
    cliente = p.store.cliente(slug)
    if not cliente:
        return JSONResponse({"erro": "não encontrado"}, status_code=404)
    r = p.store.respostas(slug)
    if request.query_params.get("formato") == "markdown":
        return PlainTextResponse(f"# Discovery — {cliente['empresa']}\n\n" + p.questionario.resumo(r), media_type="text/markdown; charset=utf-8")
    return JSONResponse({"empresa": cliente["empresa"], "respostas": {k: v for k, v in r.items() if preenchida(v)}})


@mcp.custom_route("/api/clientes/{slug}/proposta", methods=["GET"])
async def api_proposta(request: Request) -> Response:
    try:
        texto = plataforma().proposta(slugificar(request.path_params["slug"]))
    except KeyError:
        return PlainTextResponse("Cliente não encontrado", status_code=404)
    return PlainTextResponse(texto, media_type="text/markdown; charset=utf-8")


# ============================================================ autenticação
class TokenMiddleware:
    """Exige `Authorization: Bearer <MCP_TOKEN>` (ou o cookie definido ao abrir
    `/?token=...`) quando MCP_TOKEN está configurado. A página inicial e /api/saude
    ficam abertas para o app conseguir carregar e detectar o servidor."""

    LIVRES = {"/", "/api/saude"}

    def __init__(self, app: Any, token: str):
        self.app = app
        self.token = token

    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        if scope["type"] != "http" or not self.token or scope["path"] in self.LIVRES:
            return await self.app(scope, receive, send)
        headers = {k.decode().lower(): v.decode() for k, v in scope.get("headers", [])}
        ok = headers.get("authorization", "") == f"Bearer {self.token}"
        if not ok and "cookie" in headers:
            cookie = SimpleCookie(headers["cookie"])
            ok = "plataforma_token" in cookie and cookie["plataforma_token"].value == self.token
        if not ok:
            qs = parse_qs(scope.get("query_string", b"").decode())
            ok = qs.get("token", [""])[0] == self.token
        if not ok:
            resp = JSONResponse({"erro": "não autorizado"}, status_code=401)
            return await resp(scope, receive, send)
        return await self.app(scope, receive, send)


def criar_app() -> Any:
    seguranca = None
    if CFG.hosts_permitidos:
        seguranca = TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=list(CFG.hosts_permitidos),
            allowed_origins=[f"http://{h}" for h in CFG.hosts_permitidos] + [f"https://{h}" for h in CFG.hosts_permitidos],
        )
    app = mcp.streamable_http_app(streamable_http_path="/mcp", transport_security=seguranca, host=CFG.host)
    return TokenMiddleware(app, CFG.token)


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor MCP da plataforma de dados")
    parser.add_argument("--stdio", action="store_true", help="usar transporte stdio (Claude Desktop local)")
    args = parser.parse_args()
    if args.stdio:
        mcp.run("stdio")
        return
    import uvicorn

    uvicorn.run(criar_app(), host=CFG.host, port=CFG.porta, log_level="info", proxy_headers=True)


if __name__ == "__main__":
    main()
