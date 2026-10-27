"""Gera as tabelas de exemplos de preço em docs/11-precificacao.md.

    python scripts/gerar_exemplos_preco.py

Lê servidor/src/plataforma/dados/{precificacao,exemplos_preco,precos}.yaml, calcula
cada exemplo com a calculadora (a mesma da ferramenta MCP preco_estimar) e reescreve
o trecho entre os marcadores do documento. Rode depois de mudar a tabela de preços.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "servidor" / "src"))

from plataforma import custos  # noqa: E402
from plataforma import precificacao as pr  # noqa: E402

DADOS = RAIZ / "servidor" / "src" / "plataforma" / "dados"
DOC = RAIZ / "docs" / "11-precificacao.md"
INICIO, FIM = "<!-- exemplos:inicio -->", "<!-- exemplos:fim -->"


def brl(v: float) -> str:
    return "R$ " + f"{v:,.0f}".replace(",", ".")


def pct(v: float) -> str:
    return f"{v:.1%}".replace(".", ",")


def num(v: float) -> str:
    return f"{v:g}".replace(".", ",")


COMPLEXIDADE = {"baixa": "baixa", "media": "média", "alta": "alta"}


def gerar() -> str:
    cfg = pr.carregar(DADOS / "precificacao.yaml")
    dados = yaml.safe_load((DADOS / "exemplos_preco.yaml").read_text(encoding="utf-8"))
    precos = custos.carregar_precos(DADOS / "precos.yaml")
    aliq = pr.aliquota(cfg)
    out = [INICIO, "", "*Gerado por `scripts/gerar_exemplos_preco.py` a partir de `precificacao.yaml`. Não edite à mão.*", ""]

    out += ["### Taxa por hora de cada perfil", "", "| Perfil | Líquido/h | Com impostos/h |", "|---|---:|---:|"]
    for perfil in cfg["multiplicador_perfil"]:
        liq = pr.taxa_perfil(cfg, perfil)
        out.append(f"| {perfil} | {brl(liq)} | {brl(liq / (1 - aliq))} |")
    out += ["", f"Impostos: {pr._imposto_texto(cfg, aliq, None, None)}", ""]

    out += ["### Simples Nacional: anexo III × anexo V", "",
            "| Faturamento em 12 meses | Anexo III (Fator R ≥ 28%) | Anexo V |", "|---|---:|---:|"]
    for rbt in (150_000, 300_000, 500_000, 800_000, 1_500_000):
        out.append(f"| {brl(rbt)} | {pct(pr.aliquota_simples(rbt, 'III', cfg['simples_nacional']))} "
                   f"| {pct(pr.aliquota_simples(rbt, 'V', cfg['simples_nacional']))} |")
    out += ["", "Com pró-labore + folha de pelo menos 28% do faturamento (Fator R), a consultoria fica no anexo III e paga cerca da metade do imposto do anexo V. Confirme com o seu contador.", ""]

    calc = [pr.calcular_exemplo(ex, cfg, precos) for ex in dados["exemplos"]]
    out += ["### Resumo dos exemplos", "",
            "| # | Exemplo | Horas | Projeto | À vista | Mensalidade | Infra e licenças/mês* | Payback |", "|---|---|---:|---:|---:|---:|---:|---:|"]
    for i, c in enumerate(calc, 1):
        p, m, ex = c["projeto"], c["mensalidade"], c["exemplo"]
        payback = f"{num(p['retorno']['payback_meses'])} meses" if "retorno" in p else "—"
        out.append(f"| {i} | {ex['titulo']} | {num(p['horas_totais'])} | {brl(p['preco'])} | {brl(p['preco_a_vista'])} | "
                   f"{brl(m['mensalidade']) if m else '—'} | {brl(c['infra_mes']) if c['infra_mes'] else '—'} | {payback} |")
    out += ["", "*Cloud e licenças de BI estimadas pela calculadora de custos, pagas direto pelo cliente aos fornecedores; "
            "\"—\" quando a infraestrutura fica dentro da taxa de plataforma (ZimaOS) ou depende do dimensionamento (créditos Snowflake, DBUs, banco gerenciado).", ""]

    for i, c in enumerate(calc, 1):
        p, m, ex = c["projeto"], c["mensalidade"], c["exemplo"]
        out += [f"### {i}. {ex['titulo']}", "", f"**Cliente**: {ex['contexto']}  ", f"**Hospedagem**: {ex['hospedagem']}  ",
                f"**Complexidade**: {COMPLEXIDADE[ex.get('complexidade', 'media')]}", "", pr.tabela_projeto(p), ""]
        parcelas = " / ".join(brl(x["valor"]) for x in p["parcelas"])
        out.append(f"- **Preço**: {brl(p['preco'])} (à vista {brl(p['preco_a_vista'])}; parcelado 40/30/30: {parcelas}) · "
                   f"{brl(p['valor_medio_hora'])}/h em média · margem estimada {pct(p['margem_estimada'])}")
        if m:
            infra = f" + cloud e licenças de ~{brl(c['infra_mes'])}/mês pagas direto aos fornecedores" if c["infra_mes"] else ""
            out.append(f"- **Mensalidade depois da entrega**: {brl(m['mensalidade'])} ({num(m['horas_sustentacao'])} h de sustentação + "
                       f"{num(m['horas_evolucao'])} h de evolução){infra}; hora adicional {brl(m['hora_adicional'])}")
        if "retorno" in p:
            r = p["retorno"]
            out.append(f"- **Retorno**: {ex['valor_texto']} ≈ {brl(r['valor_anual'])}/ano → payback de {num(r['payback_meses'])} meses"
                       + (" (preço acima de 40% do valor anual: reduza o escopo da primeira fase)" if r["acima_do_recomendado"] else ""))
        out.append("")

    out += ["### Diagnóstico pago", "", "| Porte | Horas | Preço |", "|---|---:|---:|"]
    for porte in pr.PORTES:
        d = pr.precificar_diagnostico(porte, cfg)
        out.append(f"| {porte} | {d['horas']} | {brl(d['preco'])} |")
    out += ["", "Abatido do MVP se o cliente fechar em até 30 dias.", "",
            "### Mensalidade da plataforma gerenciada", "", "| Porte | Horas/mês | Mensalidade | Hora adicional | Margem estimada |", "|---|---:|---:|---:|---:|"]
    for porte in pr.PORTES:
        m = pr.precificar_mensalidade(porte, cfg)
        out.append(f"| {porte} | {num(m['horas_sustentacao'] + m['horas_evolucao'])} | {brl(m['mensalidade'])} | {brl(m['hora_adicional'])} | {pct(m['margem_estimada'])} |")
    out += ["", "### Banco de horas", "", "| Horas/mês | Desconto | Mensal | R$/h com impostos |", "|---:|---:|---:|---:|"]
    for h in dados["banco_horas"]:
        b = pr.precificar_banco_horas(h, cfg)
        out.append(f"| {h} | {pct(b['desconto'])} | {brl(b['mensal'])} | {brl(b['valor_hora'])} |")

    cart = dados["carteira"]
    mensais = [pr.precificar_mensalidade(p, cfg) for p in cart["gerenciados"]]
    tipico = next(c for c in calc if c["exemplo"]["id"] == cart["projeto_tipico"])["projeto"]
    mrr = sum(m["mensalidade"] for m in mensais)
    receita_proj = tipico["preco"] * cart["projetos_por_mes"]
    horas = sum(m["horas_sustentacao"] + m["horas_evolucao"] for m in mensais) + tipico["horas_totais"] * cart["projetos_por_mes"]
    receita = mrr + receita_proj
    aliq_ano = pr.aliquota_simples(receita * 12, cfg["impostos"]["anexo"], cfg["simples_nacional"])
    custo = horas * cfg["custo_hora_interno"] + sum(cfg["mensalidade"]["custo_ferramentas"][p] for p in cart["gerenciados"])
    resultado = receita * (1 - aliq_ano) - custo
    falta = max(0.0, horas - cart["horas_produtivas_mes"])
    contagem = ", ".join(f"{cart['gerenciados'].count(p)} {p}" for p in pr.PORTES if p in cart["gerenciados"])
    out += ["", f"### {cart['titulo']}", "",
            f"{len(mensais)} clientes gerenciados ({contagem}) e um projeto como o exemplo \"{cart['projeto_tipico']}\" a cada "
            f"{num(1 / cart['projetos_por_mes'])} meses.", "",
            "| Item | Por mês |", "|---|---:|",
            f"| Mensalidades (MRR) | {brl(mrr)} |",
            f"| Projetos (média) | {brl(receita_proj)} |",
            f"| **Faturamento** | **{brl(receita)}** |",
            f"| Impostos (alíquota efetiva com {brl(receita * 12)}/ano: {pct(aliq_ano)}) | {brl(receita * aliq_ano)} |",
            f"| Horas de trabalho necessárias | {horas:.0f} h |",
            f"| Custo das horas e ferramentas | {brl(custo)} |",
            f"| **Resultado** | **{brl(resultado)}** |", ""]
    if falta:
        out.append(f"São {horas:.0f} h/mês para {cart['horas_produtivas_mes']} h produtivas de uma pessoa: faltam ~{falta:.0f} h, "
                   f"que vão para freelancers (o custo já está na conta pela hora interna) ou para os agentes reduzirem.")
    else:
        out.append(f"Cabe em {cart['horas_produtivas_mes']} h produtivas de uma pessoa, com folga de {cart['horas_produtivas_mes'] - horas:.0f} h.")
    out += ["", FIM]
    return "\n".join(out)


def main() -> None:
    texto = DOC.read_text(encoding="utf-8")
    if INICIO not in texto or FIM not in texto:
        sys.exit(f"Marcadores {INICIO} / {FIM} não encontrados em {DOC}")
    antes, resto = texto.split(INICIO, 1)
    depois = resto.split(FIM, 1)[1]
    DOC.write_text(antes + gerar() + depois, encoding="utf-8")
    print(f"{DOC.relative_to(RAIZ)} atualizado")


if __name__ == "__main__":
    main()
