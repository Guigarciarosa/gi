from plataforma import agentes as ag
from plataforma import custos
from plataforma.vetorial import HashEmbedder, MemoriaIndice, MemoriaVetorial, fragmentar

RESPOSTAS = {
    "id.empresa": "Transportes Exemplo",
    "neg.segmento": "logistica",
    "neg.log.rastreamento": "sim",
    "neg.log.posicoes": "minuto",
    "neg.descricao": "Transportadora de carga fracionada no Oeste do Paraná.",
    "dados.fontes": ["erp", "iot"],
    "dados.erp.sistema": "protheus",
    "dados.volume_total": "100gb_1tb",
    "dados.latencia": "horario",
    "infra.atual": "on_premise",
    "infra.preferencia": "mais_barato",
    "cons.usuarios": "6_20",
    "obj.objetivo": "Saber o custo por km e a margem por cliente.",
    "obj.perguntas": "Qual a margem por cliente?\nQual o custo por km por veículo?",
    "neg.segmento.outro": "ignorada porque o ramo 'outro' não foi escolhido",
}


def test_salvar_discovery_normaliza_e_remove_orfas(plataforma):
    res = plataforma.salvar_discovery("Transportes Exemplo", RESPOSTAS)
    assert res["slug"] == "transportes-exemplo"
    salvas = plataforma.store.respostas("transportes-exemplo")
    assert "neg.segmento.outro" not in salvas
    assert salvas["neg.log.posicoes"] == "minuto"
    assert any("Removida" in a for a in res["avisos"])


def test_contexto_do_agente_inclui_respostas_custos_e_dependencias(plataforma):
    plataforma.salvar_discovery("Transportes Exemplo", RESPOSTAS)
    plataforma.salvar_entregavel("transportes-exemplo", "negocios", "## KPIs\n- custo por km", "teste")
    ctx = plataforma.contexto("transportes-exemplo", "arquiteto")
    assert "Arquiteto de Dados" in ctx["nome"]
    assert "custo por km" in ctx["usuario"]  # entregável do Analista de Negócios
    assert "Estimativa de custos" in ctx["usuario"]  # arquiteto usa a calculadora
    assert "TOTVS Protheus" in ctx["usuario"]
    assert ctx["sistema"].strip()


def test_todos_os_agentes_tem_papel_e_skill(plataforma):
    for a in ag.AGENTES:
        pf = ag.carregar_perfil(plataforma.cfg.raiz, a.id)
        assert "Formato de entrega" in pf.papel, a.pasta
        assert len(pf.skill) > 500, a.pasta


def test_proposta_lista_pendencias(plataforma):
    plataforma.salvar_discovery("Transportes Exemplo", RESPOSTAS)
    texto = plataforma.proposta("transportes-exemplo")
    assert "Comparativo de custos" in texto and "Pendências" in texto


def test_calculadora_ordem_de_grandeza():
    precos = custos.carregar_precos(custos.Path(custos.__file__).parent / "dados" / "precos.yaml")
    pequeno = custos.estimar(custos.PerfilCarga(volume_gb=50, usuarios_bi=10, fontes=2), precos)
    assert pequeno["perfil"]["porte"] == "P"
    for o in pequeno["opcoes"]:
        assert 100 < o["tco_brl"] < 6_000, (o["id"], o["tco_brl"])
    grande = custos.estimar(custos.PerfilCarga(volume_gb=50_000, usuarios_bi=300, fontes=5, streaming=True, eventos_por_segundo=10_000), precos)
    assert grande["perfil"]["porte"] == "G"
    assert all(o["tco_brl"] > pequeno["opcoes"][i]["tco_brl"] for i, o in enumerate(grande["opcoes"]))


def test_restricao_sem_saas_so_permite_onprem():
    precos = custos.carregar_precos(custos.Path(custos.__file__).parent / "dados" / "precos.yaml")
    est = custos.estimar(custos.PerfilCarga(restricoes=["sem_saas"]), precos)
    assert est["recomendacao"] == "onprem"
    assert all(not o["viavel"] for o in est["opcoes"] if o["id"] != "onprem")


def test_memoria_isola_clientes():
    m = MemoriaVetorial(MemoriaIndice(), HashEmbedder())
    m.indexar("clientes", "discovery", "Cliente A usa SAP e Power BI", {"cliente": "a"})
    m.indexar("clientes", "discovery", "Cliente B usa Protheus e Looker", {"cliente": "b"})
    res = m.buscar("Protheus", "clientes", cliente="a")
    assert res and all(r.metadados["cliente"] == "a" for r in res)
    try:
        m.buscar("Protheus", "clientes")
    except ValueError:
        pass
    else:
        raise AssertionError("busca em 'clientes' sem cliente deveria falhar")


def test_fragmentar_mantem_titulo():
    texto = "# Título\n" + ("palavra " * 400)
    pedacos = fragmentar(texto, tamanho=500, sobreposicao=50)
    assert len(pedacos) > 1 and all(p.startswith("# Título") for p in pedacos)
