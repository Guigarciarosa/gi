"""Calculadora de preços da consultoria: projeto, mensalidade, diagnóstico e banco de horas.

Como a calculadora de custos de cloud, existe para o Comercial não fazer contas no
LLM. Cada valor sai de uma premissa de `dados/precificacao.yaml`, e o resultado
lista as premissas usadas.

Projeto: horas por perfil × taxa × multiplicador → + gestão → + reserva de risco →
÷ (1 − imposto) → arredonda para cima.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

PORTES = ("P", "M", "G")


@dataclass
class Item:
    descricao: str
    horas: float
    perfil: str = "engenheiro"


def carregar(caminho: Path | str) -> dict[str, Any]:
    with open(caminho, encoding="utf-8") as f:
        return yaml.safe_load(f)


def aliquota_simples(receita_12m: float, anexo: str, tabela: dict[str, list[list[float]]]) -> float:
    """Alíquota efetiva do Simples Nacional para o faturamento dos últimos 12 meses."""
    faixas = tabela[str(anexo)]
    if receita_12m <= 0:
        return faixas[0][1]
    for limite, nominal, deducao in faixas:
        if receita_12m <= limite:
            return (receita_12m * nominal - deducao) / receita_12m
    raise ValueError("Faturamento acima do limite do Simples Nacional (R$ 4,8 milhões): informe outro regime.")


def aliquota(cfg: dict[str, Any], receita_12m: float | None = None, anexo: str | None = None) -> float:
    imp = cfg["impostos"]
    if imp.get("regime") == "simples":
        return aliquota_simples(receita_12m or imp["receita_12m"], anexo or imp["anexo"], cfg["simples_nacional"])
    return float(imp["aliquota"])


def _para_cima(valor: float, passo: float) -> float:
    return math.ceil(round(valor, 6) / passo) * passo


def _perto(valor: float, passo: float) -> float:
    return round(valor / passo) * passo


def _brl(v: float) -> str:
    return "R$ " + f"{v:,.0f}".replace(",", ".")


def _num(v: float, casas: int | None = None) -> str:
    """Número no formato brasileiro (vírgula decimal)."""
    return (f"{v:.{casas}f}" if casas is not None else f"{v:g}").replace(".", ",")


def _pct(v: float, casas: int = 2) -> str:
    return f"{v * 100:.{casas}f}".replace(".", ",") + "%"


def taxa_perfil(cfg: dict[str, Any], perfil: str) -> int:
    """Valor líquido da hora do perfil, em reais inteiros."""
    return int(math.floor(round(cfg["taxa_hora"] * cfg["multiplicador_perfil"][perfil], 2) + 0.5))


def _imposto_texto(cfg: dict[str, Any], aliq: float, receita_12m: float | None, anexo: str | None) -> str:
    imp = cfg["impostos"]
    if imp.get("regime") == "simples":
        rbt = receita_12m or imp["receita_12m"]
        return f"Simples Nacional, anexo {anexo or imp['anexo']}, faturamento de 12 meses de {_brl(rbt)}: alíquota efetiva de {_pct(aliq)}."
    return f"Alíquota de impostos sobre a nota: {_pct(aliq)}."


def precificar_projeto(
    itens: list[Item],
    cfg: dict[str, Any],
    complexidade: str = "media",
    receita_12m: float | None = None,
    anexo: str | None = None,
    valor_anual: float | None = None,
) -> dict[str, Any]:
    if not itens:
        raise ValueError("Informe ao menos um item com horas.")
    taxa, mult = cfg["taxa_hora"], cfg["multiplicador_perfil"]
    if complexidade not in cfg["risco"]:
        raise ValueError(f"Complexidade inválida: {complexidade}. Use {', '.join(cfg['risco'])}.")
    linhas, horas_tec, valor_tec = [], 0.0, 0.0
    for it in itens:
        if it.perfil not in mult:
            raise ValueError(f"Perfil desconhecido: {it.perfil}. Use {', '.join(mult)}.")
        hora = taxa_perfil(cfg, it.perfil)
        linhas.append({"descricao": it.descricao, "perfil": it.perfil, "horas": it.horas,
                       "valor_hora": round(hora, 2), "valor": round(it.horas * hora, 2)})
        horas_tec += it.horas
        valor_tec += it.horas * hora
    taxa_media = valor_tec / horas_tec
    horas_gestao = horas_tec * cfg["gestao"]
    valor_gestao = horas_gestao * taxa_media
    reserva = (valor_tec + valor_gestao) * cfg["risco"][complexidade]
    liquido = valor_tec + valor_gestao + reserva
    aliq = aliquota(cfg, receita_12m, anexo)
    preco = _para_cima(liquido / (1 - aliq), cfg["arredondar_para"])
    impostos = preco * aliq
    horas_totais = horas_tec + horas_gestao
    custo = horas_totais * cfg["custo_hora_interno"]
    pg = cfg["pagamento"]
    resultado: dict[str, Any] = {
        "tipo": "projeto",
        "itens": linhas,
        "horas_tecnicas": round(horas_tec, 1),
        "horas_gestao": round(horas_gestao, 1),
        "horas_totais": round(horas_totais, 1),
        "valor_tecnico": round(valor_tec, 2),
        "valor_gestao": round(valor_gestao, 2),
        "reserva_risco": round(reserva, 2),
        "impostos": round(impostos, 2),
        "preco": preco,
        "preco_a_vista": _perto(preco * (1 - pg["desconto_a_vista"]), cfg["arredondar_para"]),
        "parcelas": [{"quando": q, "valor": round(preco * f, 2)} for q, f in pg["parcelas_projeto"]],
        "valor_medio_hora": round(preco / horas_totais, 2),
        "margem_estimada": round((preco - impostos - custo) / preco, 3),
        "premissas": [
            f"Taxa base de R$ {taxa:.0f}/h líquida, ajustada por perfil ({', '.join(f'{k} ×{_num(v)}' for k, v in mult.items())}).",
            f"Gestão de {_pct(cfg['gestao'], 0)} das horas técnicas; reserva de risco de {_pct(cfg['risco'][complexidade], 0)} (complexidade {complexidade}).",
            _imposto_texto(cfg, aliq, receita_12m, anexo),
            f"Custo interno de R$ {cfg['custo_hora_interno']:.0f}/h para a margem estimada; arredondado para cima em múltiplos de R$ {cfg['arredondar_para']:.0f}.",
            "Infraestrutura (cloud, licenças) fora do preço: paga direto pelo cliente ou repassada à parte.",
        ],
    }
    if valor_anual:
        resultado["retorno"] = {
            "valor_anual": valor_anual,
            "payback_meses": round(preco / (valor_anual / 12), 1),
            "preco_sobre_valor_anual": round(preco / valor_anual, 2),
            "acima_do_recomendado": preco > 0.4 * valor_anual,
        }
    return resultado


def precificar_mensalidade(
    porte: str,
    cfg: dict[str, Any],
    horas_sustentacao: float | None = None,
    horas_evolucao: float | None = None,
    infra_brl: float = 0.0,
    infra_pela_consultoria: bool = False,
    receita_12m: float | None = None,
    anexo: str | None = None,
) -> dict[str, Any]:
    if porte not in PORTES:
        raise ValueError("Porte deve ser P, M ou G.")
    m = cfg["mensalidade"]
    hs = m["horas_sustentacao"][porte] if horas_sustentacao is None else horas_sustentacao
    he = m["horas_evolucao"][porte] if horas_evolucao is None else horas_evolucao
    horas = hs + he
    servico = horas * cfg["taxa_hora"] * (1 - m["desconto_recorrencia"]) + m["taxa_plataforma"][porte]
    aliq = aliquota(cfg, receita_12m, anexo)
    mensal = _para_cima(servico / (1 - aliq), 50)
    infra = _para_cima(infra_brl * (1 + m["taxa_gestao_infra"]) / (1 - aliq), 50) if infra_pela_consultoria and infra_brl else 0.0
    custo = horas * cfg["custo_hora_interno"] + m["custo_ferramentas"][porte]
    return {
        "tipo": "mensalidade",
        "porte": porte,
        "horas_sustentacao": hs,
        "horas_evolucao": he,
        "mensalidade": mensal,
        "infraestrutura_repassada": infra,
        "infraestrutura_direta_estimada": 0.0 if infra_pela_consultoria else round(infra_brl, 2),
        "total_mes_cliente": mensal + (infra if infra_pela_consultoria else infra_brl),
        "hora_adicional": _para_cima(cfg["taxa_hora"] / (1 - aliq), 10),
        "margem_estimada": round((mensal * (1 - aliq) - custo) / mensal, 3),
        "premissas": [
            f"{hs:g} h de sustentação + {he:g} h de evolução por mês, com {m['desconto_recorrencia']:.0%} de desconto por recorrência.",
            f"Taxa de plataforma de R$ {m['taxa_plataforma'][porte]:.0f}/mês (servidor, monitoramento, backup externo, agentes e ferramentas).",
            _imposto_texto(cfg, aliq, receita_12m, anexo),
            ("Infraestrutura paga pela consultoria e repassada com taxa de gestão de "
             f"{m['taxa_gestao_infra']:.0%} (também entra na nota)." if infra_pela_consultoria
             else "Infraestrutura paga direto pelo cliente ao provedor (recomendado: não entra na sua nota)."),
            "Horas não usadas não acumulam; excedente cobrado pela hora adicional.",
        ],
    }


def precificar_diagnostico(porte: str, cfg: dict[str, Any], receita_12m: float | None = None, anexo: str | None = None) -> dict[str, Any]:
    if porte not in PORTES:
        raise ValueError("Porte deve ser P, M ou G.")
    horas = cfg["diagnostico_horas"][porte]
    aliq = aliquota(cfg, receita_12m, anexo)
    preco = _para_cima(horas * cfg["taxa_hora"] / (1 - aliq), cfg["arredondar_para"])
    return {
        "tipo": "diagnostico", "porte": porte, "horas": horas, "preco": preco,
        "premissas": [f"{horas} h a R$ {cfg['taxa_hora']:.0f}/h líquida.", _imposto_texto(cfg, aliq, receita_12m, anexo),
                      "Valor abatido do MVP se o cliente fechar em até 30 dias."],
    }


def precificar_banco_horas(horas_mes: float, cfg: dict[str, Any], perfil: str = "engenheiro",
                           receita_12m: float | None = None, anexo: str | None = None) -> dict[str, Any]:
    descontos = cfg["banco_horas"]["descontos"]
    faixa = max((int(h) for h in descontos if horas_mes >= int(h)), default=None)
    desconto = descontos[faixa] if faixa is not None else 0.0
    hora = taxa_perfil(cfg, perfil) * (1 - desconto)
    aliq = aliquota(cfg, receita_12m, anexo)
    mensal = _para_cima(horas_mes * hora / (1 - aliq), cfg["arredondar_para"])
    return {
        "tipo": "banco_horas", "horas_mes": horas_mes, "perfil": perfil, "desconto": desconto,
        "mensal": mensal, "valor_hora": round(mensal / horas_mes, 2),
        "premissas": [f"{horas_mes:g} h/mês de {perfil} com {desconto:.0%} de desconto por volume.", _imposto_texto(cfg, aliq, receita_12m, anexo)],
    }


def tabela_projeto(res: dict[str, Any]) -> str:
    linhas = ["| Item | Perfil | Horas | R$/h | Valor |", "|---|---|---:|---:|---:|"]
    for i in res["itens"]:
        linhas.append(f"| {i['descricao']} | {i['perfil']} | {_num(i['horas'])} | {i['valor_hora']:.0f} | {_brl(i['valor'])} |")
    linhas += [
        f"| Gestão do projeto | — | {_num(res['horas_gestao'])} | — | {_brl(res['valor_gestao'])} |",
        f"| Reserva de risco | — | — | — | {_brl(res['reserva_risco'])} |",
        f"| Impostos | — | — | — | {_brl(res['impostos'])} |",
        f"| **Preço do projeto** | | **{_num(res['horas_totais'])} h** | | **{_brl(res['preco'])}** |",
    ]
    return "\n".join(linhas)


def calcular_exemplo(ex: dict[str, Any], cfg: dict[str, Any], precos: dict[str, Any] | None = None) -> dict[str, Any]:
    """Projeto + mensalidade de um exemplo de `dados/exemplos_preco.yaml`; a infraestrutura
    mensal vem da calculadora de custos de cloud quando o exemplo informa `infra`."""
    itens = [Item(d, float(h), p) for d, h, p in ex["itens"]]
    projeto = precificar_projeto(itens, cfg, ex.get("complexidade", "media"), valor_anual=ex.get("valor_anual"))
    infra = 0.0
    if ex.get("infra") and precos is not None:
        from . import custos

        parametros = dict(ex["infra"])
        provedor = parametros.pop("provedor")
        est = custos.estimar(custos.PerfilCarga(**parametros), precos)
        infra = next(o["total_brl"] for o in est["opcoes"] if o["id"] == provedor)
    mensalidade = None
    if ex.get("porte"):
        m = ex.get("mensalidade", {})
        mensalidade = precificar_mensalidade(ex["porte"], cfg, m.get("horas_sustentacao"), m.get("horas_evolucao"), infra_brl=infra)
    return {"exemplo": ex, "projeto": projeto, "mensalidade": mensalidade, "infra_mes": infra}
