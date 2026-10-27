import re
from pathlib import Path

import pytest
import yaml

from plataforma import agentes as ag
from plataforma import coleta, custos
from plataforma import precificacao as pr

RAIZ = Path(__file__).resolve().parents[2]
DADOS = RAIZ / "servidor" / "src" / "plataforma" / "dados"


@pytest.fixture(scope="module")
def cfg():
    return pr.carregar(DADOS / "precificacao.yaml")


# ------------------------------------------------------------------ preços
def test_aliquota_efetiva_do_simples(cfg):
    tabela = cfg["simples_nacional"]
    assert pr.aliquota_simples(150_000, "III", tabela) == pytest.approx(0.06)
    # 2ª faixa do anexo III: (300.000 × 11,2% − 9.360) ÷ 300.000
    assert pr.aliquota_simples(300_000, "III", tabela) == pytest.approx(0.0808)
    assert pr.aliquota_simples(300_000, "V", tabela) == pytest.approx(0.165)
    with pytest.raises(ValueError):
        pr.aliquota_simples(5_000_000, "III", tabela)


def test_projeto_soma_gestao_risco_e_impostos(cfg):
    r = pr.precificar_projeto([pr.Item("Pipelines", 100, "engenheiro")], cfg, "baixa")
    assert r["valor_tecnico"] == 17_000  # 100 h × R$ 170
    assert r["valor_gestao"] == 2_550  # 15% das horas
    assert r["reserva_risco"] == pytest.approx(1_955)  # 10% de 19.550
    assert r["preco"] == 23_400  # 21.505 ÷ (1 − 8,08%), arredondado para cima
    assert r["preco"] % cfg["arredondar_para"] == 0
    assert sum(p["valor"] for p in r["parcelas"]) == pytest.approx(r["preco"])
    assert 0.35 < r["margem_estimada"] < 0.5


def test_projeto_recusa_perfil_e_complexidade_invalidos(cfg):
    with pytest.raises(ValueError):
        pr.precificar_projeto([pr.Item("x", 10, "astronauta")], cfg)
    with pytest.raises(ValueError):
        pr.precificar_projeto([pr.Item("x", 10)], cfg, "extrema")
    with pytest.raises(ValueError):
        pr.precificar_projeto([], cfg)


def test_especialidade_e_risco_encarecem(cfg):
    base = pr.precificar_projeto([pr.Item("x", 40, "engenheiro")], cfg, "media")["preco"]
    plataforma = pr.precificar_projeto([pr.Item("x", 40, "plataforma")], cfg, "media")["preco"]
    alta = pr.precificar_projeto([pr.Item("x", 40, "engenheiro")], cfg, "alta")["preco"]
    assert plataforma > base and alta > base


def test_mensalidade_diagnostico_e_banco_de_horas(cfg):
    m = pr.precificar_mensalidade("P", cfg)
    assert m["mensalidade"] == 2_350  # (10 h × 170 × 0,9 + 600) ÷ (1 − 8,08%)
    assert m["margem_estimada"] > 0.35
    assert pr.precificar_mensalidade("G", cfg)["mensalidade"] > pr.precificar_mensalidade("M", cfg)["mensalidade"] > m["mensalidade"]
    assert pr.precificar_diagnostico("P", cfg)["preco"] == 3_000
    assert pr.precificar_banco_horas(30, cfg)["desconto"] == 0
    assert pr.precificar_banco_horas(40, cfg)["desconto"] == 0.05
    assert pr.precificar_banco_horas(100, cfg)["desconto"] == 0.10
    with pytest.raises(ValueError):
        pr.precificar_mensalidade("XG", cfg)


def test_exemplos_de_preco_calculam_e_estao_no_documento(cfg):
    precos = custos.carregar_precos(DADOS / "precos.yaml")
    exemplos = yaml.safe_load((DADOS / "exemplos_preco.yaml").read_text(encoding="utf-8"))["exemplos"]
    doc = (RAIZ / "docs" / "11-precificacao.md").read_text(encoding="utf-8")
    assert len(exemplos) >= 10
    for ex in exemplos:
        r = pr.calcular_exemplo(ex, cfg, precos)
        assert r["projeto"]["preco"] > 0, ex["id"]
        for _, _, perfil in ex["itens"]:
            assert perfil in cfg["multiplicador_perfil"], ex["id"]
        # o documento é gerado por scripts/gerar_exemplos_preco.py: precisa estar atualizado
        assert pr._brl(r["projeto"]["preco"]) in doc, f"{ex['id']}: rode scripts/gerar_exemplos_preco.py"


# ------------------------------------------------------------- conhecimento
def test_arquivos_de_conhecimento_tem_cabecalho_e_fontes():
    arquivos = sorted((RAIZ / "conhecimento" / "bancos-de-dados").glob("*.md"))
    assert len(arquivos) >= 25
    ids = {a.id for a in ag.AGENTES}
    for arq in arquivos:
        if arq.name == "README.md":
            continue
        texto = arq.read_text(encoding="utf-8")
        assert texto.startswith("---\n"), arq.name
        meta = yaml.safe_load(texto.split("---\n")[1])
        assert {"agentes", "revisado"} <= set(meta) and ({"sgbd", "tema"} & set(meta)), arq.name
        assert set(meta["agentes"]) <= ids, arq.name
        assert "## Documentação oficial" in texto, arq.name


def test_agentes_tem_conhecimento_e_pipeline():
    assert len(ag.AGENTES) == 11
    assert ag.ORDEM_PIPELINE.index("dba") < ag.ORDEM_PIPELINE.index("engenheiro")
    dba = ag.resolver("dba")
    arquivos = ag.arquivos_conhecimento(RAIZ, dba)
    assert len(arquivos) >= 25 and all((RAIZ / a).exists() for a in arquivos)
    for a in ag.AGENTES:
        assert all(d in ag.POR_ID for d in a.depende_de), a.id


def test_consultas_do_cliente_seguem_bancos_erp_e_plataforma():
    respostas = {"dados.erp.sistema": "protheus", "dados.erp.banco": "sqlserver",
                 "dados.bd.tipos": ["postgres", "sqlserver"], "infra.plataforma_dados": ["databricks"]}
    dba = ag.consultas_do_cliente(ag.resolver("dba"), respostas)
    eng = ag.consultas_do_cliente(ag.resolver("engenheiro"), respostas)
    assert sum("SQL Server" in c for c in dba) == 1  # sem repetir o banco
    assert any("PostgreSQL" in c for c in dba) and any("TOTVS Protheus" in c for c in dba)
    assert any("Databricks" in c and "Git" in c for c in eng)
    assert ag.consultas_do_cliente(ag.resolver("analista"), respostas) == []


# ------------------------------------------------------------------ coleta
def test_links_oficiais_encontra_as_secoes():
    fontes = coleta.links_oficiais(RAIZ)
    assert "postgresql" in fontes and "snowflake" in fontes
    assert all(u.startswith("http") and not u.endswith((".", ",", ")")) for us in fontes.values() for u in us)


def test_html_para_markdown_remove_navegacao_e_mantem_codigo():
    html = """<html><head><title>Backup | Docs</title><style>p{}</style></head><body>
    <nav><a href="/menu">Menu</a></nav>
    <main><h1>Backup</h1><p>Use   o <b>pg_dump</b> para cópias lógicas.</p>
    <pre>pg_dump -Fc banco &gt; banco.dump
  pg_restore -d novo banco.dump</pre>
    <ul><li>Teste a restauração</li></ul><a href="pitr.html">PITR</a></main>
    <script>alert(1)</script></body></html>"""
    titulo, texto, links = coleta.html_para_markdown(html)
    assert titulo == "Backup | Docs"
    assert "# Backup" in texto and "Use o pg_dump para cópias lógicas." in texto
    assert "pg_dump -Fc banco > banco.dump\n  pg_restore" in texto
    assert "- Teste a restauração" in texto
    assert "Menu" not in texto and "alert" not in texto and "p{}" not in texto
    assert links == ["pitr.html"]


def test_baixar_fonte_segue_links_da_mesma_pasta_e_respeita_robots(tmp_path):
    corpo = "<p>" + "conteúdo útil " * 30 + "</p>"
    paginas = {
        "https://docs.exemplo.com/robots.txt": ("text/plain", "User-agent: *\nDisallow: /manual/privado\n"),
        "https://docs.exemplo.com/manual/index.html": (
            "text/html",
            f"<title>Índice</title>{corpo}<a href='backup.html'>b</a><a href='privado.html'>p</a>"
            "<a href='/blog/x.html'>fora</a><a href='https://outro.com/manual/y'>outro</a><a href='curta.html'>c</a>",
        ),
        "https://docs.exemplo.com/manual/backup.html": ("text/html", f"<title>Backup</title>{corpo}"),
        "https://docs.exemplo.com/manual/curta.html": ("text/html", "<p>pouco</p>"),
    }
    pedidos = []

    def buscar(url):
        pedidos.append(url)
        if url not in paginas:
            return coleta.Resposta(404, "text/html", "")
        tipo, texto = paginas[url]
        return coleta.Resposta(200, tipo, texto)

    res = coleta.baixar_fonte("exemplo", ["https://docs.exemplo.com/manual/index.html"], tmp_path, atraso=0, buscar=buscar)
    nomes = sorted(Path(a).name for a in res.arquivos)
    assert nomes == ["docs-exemplo-com-manual-backup-html.md", "docs-exemplo-com-manual-index-html.md"]
    assert not any("blog" in p or "outro.com" in p for p in pedidos)
    assert any("robots.txt" in e for e in res.erros if "privado" in e)
    assert any("sem conteúdo" in e for e in res.erros if "curta" in e)
    salvo = (tmp_path / "exemplo" / "docs-exemplo-com-manual-backup-html.md").read_text(encoding="utf-8")
    assert salvo.startswith("# Backup\n\nFonte: https://docs.exemplo.com/manual/backup.html")
    assert re.search(r"Baixado em: \d{4}-\d{2}-\d{2}", salvo)

    limitado = coleta.baixar_fonte("limite", ["https://docs.exemplo.com/manual/index.html"], tmp_path,
                                   max_paginas=1, atraso=0, buscar=buscar)
    assert len(limitado.arquivos) == 1
