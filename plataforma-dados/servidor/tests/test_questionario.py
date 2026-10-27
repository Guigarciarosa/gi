import json
from pathlib import Path

import yaml

from plataforma.agentes import POR_ID

RAIZ = Path(__file__).resolve().parents[2]


def _valores_brutos(no, saida):
    if isinstance(no, dict):
        if "valor" in no:
            saida.append(no["valor"])
        for v in no.values():
            _valores_brutos(v, saida)
    elif isinstance(no, list):
        for v in no:
            _valores_brutos(v, saida)
    return saida


def test_valores_de_opcao_sao_texto_no_yaml():
    # `11_50` sem aspas vira o inteiro 1150 no YAML; todo valor precisa ser string.
    bruto = yaml.safe_load((RAIZ / "questionario" / "questionario.yaml").read_text(encoding="utf-8"))
    nao_texto = [v for v in _valores_brutos(bruto, []) if not isinstance(v, str)]
    assert nao_texto == []


def test_estrutura(questionario):
    est = questionario.estatisticas()
    assert est["secoes"] == 11
    assert est["perguntas"] >= 200
    assert est["condicionais"] >= 100
    assert est["profundidade_maxima"] >= 2


def test_agentes_citados_existem(questionario):
    citados = {a for p in questionario.perguntas.values() for a in p.agentes}
    assert citados <= set(POR_ID)
    assert citados == set(POR_ID), "todo agente deve receber alguma pergunta"


def test_mostrar_se_aponta_para_perguntas_existentes(questionario):
    def alvos(c):
        if "qualquer" in c or "todas" in c:
            for x in c.get("qualquer", []) + c.get("todas", []):
                yield from alvos(x)
        elif "nao" in c:
            yield from alvos(c["nao"])
        else:
            yield c["pergunta"]

    for p in questionario.perguntas.values():
        if p.mostrar_se:
            for alvo in alvos(p.mostrar_se):
                assert alvo in questionario.perguntas, (p.id, alvo)


def test_ramificacao_abre_e_fecha(questionario):
    r = {}
    assert not questionario.visivel("neg.seg.tipo", r)
    r["neg.segmento"] = "seguros_protecao"
    assert questionario.visivel("neg.seg.tipo", r)
    r["neg.segmento"] = "varejo"
    assert not questionario.visivel("neg.seg.tipo", r)
    assert questionario.visivel("neg.varejo.canais", r)


def test_neto_depende_do_pai_visivel(questionario):
    r = {"neg.segmento": "varejo", "neg.varejo.canais": ["marketplace"]}
    assert questionario.visivel("neg.varejo.marketplaces", r)
    r["neg.segmento"] = "agro"
    assert not questionario.visivel("neg.varejo.marketplaces", r)


def test_ancora_compartilhada_em_varias_opcoes(questionario):
    for faixa in ("2_5", "6_20", "mais_20"):
        assert questionario.visivel("neg.unidades.consolidacao", {"neg.unidades": faixa})
    assert not questionario.visivel("neg.unidades.consolidacao", {"neg.unidades": "1"})


def test_mostrar_se_cruzado(questionario):
    assert not questionario.visivel("infra.onprem.servidores", {"infra.atual": "cloud"})
    assert questionario.visivel("infra.onprem.servidores", {"infra.atual": "hibrido"})
    assert questionario.visivel("infra.cloud.provedores", {"infra.atual": "hibrido"})
    assert questionario.visivel("aut.custo_hora", {"aut.processos": ["relatorios"], "aut.horas_manuais": 10})
    assert not questionario.visivel("aut.custo_hora", {"aut.processos": ["relatorios"]})


def test_limpar_orfas(questionario):
    r = {"neg.segmento": "varejo", "neg.varejo.canais": ["marketplace"], "neg.varejo.marketplaces": ["amazon"]}
    r["neg.segmento"] = "saude"
    limpo = questionario.limpar_orfas(r)
    assert "neg.varejo.canais" not in limpo and "neg.varejo.marketplaces" not in limpo


def test_normalizar(questionario):
    assert questionario.normalizar("neg.funcionarios", "11 a 50") == "11_50"
    assert questionario.normalizar("aut.horas_manuais", "1.500,5") == 1500.5
    assert questionario.normalizar("aut.horas_manuais", "12.5") == 12.5
    assert questionario.normalizar("dados.fontes", "erp, crm") == ["erp", "crm"]
    assert questionario.normalizar("dados.qualidade", 3) == "3"


def test_sinais_somam_opcoes(questionario):
    r = {"infra.atual": "cloud", "infra.cloud.provedores": ["aws", "azure"], "cons.bi": "powerbi"}
    s = questionario.sinais(r)
    assert s["aws"] == 3 and s["azure"] == 5


def test_json_exportado_tem_pesos(questionario):
    dados = questionario.para_json()
    assert dados["pesos"]["infra.cloud.provedores=aws"] == {"aws": 3}
    json.dumps(dados)


def test_html_estatico_atualizado():
    html = (RAIZ / "questionario" / "questionario.html").read_text(encoding="utf-8")
    assert "/*__QUESTIONARIO__*/" not in html
    embutido = html.split('id="dados-questionario">', 1)[1].split("</script>", 1)[0]
    gerado = json.loads((RAIZ / "questionario" / "questionario.json").read_text(encoding="utf-8"))
    assert json.loads(embutido)["perguntas"] == gerado["perguntas"]
