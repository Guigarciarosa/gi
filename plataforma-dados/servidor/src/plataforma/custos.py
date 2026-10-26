"""Calculadora determinística de custos: AWS × GCP × Azure × OCI × on-premise.

Os agentes (principalmente FinOps e Arquiteto) chamam esta calculadora em vez de
fazer contas no LLM. O modelo é deliberadamente simples e explícito: cada
número sai de uma premissa listada em `premissas`, para que a proposta possa
ser auditada e ajustada.

Fluxo: respostas do questionário -> PerfilCarga -> estimativa por provedor ->
ranking ponderado (custo total + afinidade dos sinais + restrições).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

PROVEDORES = ("aws", "gcp", "azure", "oci")
HORAS_MES = 730

VOLUME_GB = {
    "ate_10gb": 10, "10_100gb": 60, "100gb_1tb": 500, "1_10tb": 5_000,
    "10_100tb": 50_000, "mais_100tb": 150_000,
}
VOLUME_POR_REGISTROS_GB = {"ate_100k": 5, "100k_1m": 30, "1m_10m": 200, "mais_10m": 1_000}
CRESCIMENTO = {"baixo": 0.03, "medio": 0.10, "alto": 0.20, "nao_sei": 0.05}
ATUALIZACOES_DIA = {
    "mensal": 1 / 30, "diario": 1, "intradiario": 4, "horario": 24,
    "near_real_time": 288, "tempo_real": 288,
}
USUARIOS = {"1_5": 5, "6_20": 15, "21_100": 60, "101_500": 300, "mais_500": 800}
EVENTOS_S = {"ate_100": 50, "100_5k": 1_500, "mais_5k": 10_000}
BI_POR_FERRAMENTA = {  # USD por usuário/mês, igual em qualquer cloud
    "powerbi": 14.0, "tableau": 15.0, "qlik": 30.0, "looker_studio": 0.0,
    "metabase_superset": 0.0, "excel": 0.0,
}

DICAS = {
    "aws": [
        "Compute Savings Plans de 1 ano reduzem EC2/Fargate em até ~66% (sem compromisso de instância).",
        "Prefira Graviton (t4g/m7g): ~20% mais barato que x86 equivalente.",
        "Athena: grave em Parquet particionado por data e use CTAS na camada gold; o custo cai com o volume varrido.",
        "S3 Intelligent-Tiering ou lifecycle para Glacier IR após 90 dias na camada bronze.",
        "Desligue dev/homolog fora do horário com Instance Scheduler.",
    ],
    "gcp": [
        "BigQuery: particione por data e clusterize por chaves de filtro; 1 TiB/mês de consulta é grátis.",
        "Para uso previsível, BigQuery Editions com autoscaling pode sair mais barato que on-demand.",
        "Committed Use Discounts flexíveis reduzem Compute Engine em ~28–46%.",
        "Cloud Run Jobs para pipelines curtos: cobra só o tempo de execução.",
        "Spot VMs para processamento em lote tolerante a interrupção (até ~60–91% de desconto).",
    ],
    "azure": [
        "Azure Hybrid Benefit se o cliente já tem licenças Windows Server/SQL Server.",
        "Reservas de 1 ano ou Savings Plan for Compute (até ~65%).",
        "Power BI Pro pode já estar incluso no Microsoft 365 E5 do cliente: confira antes de orçar.",
        "Fabric: pause a capacidade (F2/F4) fora do horário; cobra por hora ligada.",
        "Synapse Serverless cobra por TB processado: use Parquet/Delta e views na gold.",
    ],
    "oci": [
        "Always Free cobre 4 OCPU Ampere + 24 GB RAM: um MVP inteiro pode custar zero.",
        "Saída de internet: 10 TB/mês grátis, ótimo para portais e APIs de dados.",
        "Preço igual em todas as regiões: São Paulo e Vinhedo custam o mesmo que os EUA.",
        "Autonomous DW com auto-scaling e parada agendada fora do horário comercial.",
        "Licenças Oracle existentes (BYOL) baixam muito o custo do Autonomous Database.",
    ],
    "onprem": [
        "Use o hardware ocioso que o cliente já tem antes de comprar novo.",
        "Backup 3-2-1 com cópia imutável fora do site (Backblaze B2 / Cloudflare R2) é obrigatório.",
        "Monitore energia e temperatura; nobreak dimensionado evita corrupção de dados.",
        "Planeje troca de discos: RAID não é backup.",
    ],
}


@dataclass
class PerfilCarga:
    volume_gb: float = 50
    crescimento_mes: float = 0.05
    atualizacoes_dia: float = 1
    streaming: bool = False
    eventos_por_segundo: float = 0
    usuarios_bi: int = 10
    fontes: int = 3
    ambientes: int = 1
    ferramenta_bi: str | None = None
    ia_ml: bool = False
    ia_llm: bool = False
    llm_local_obrigatorio: bool = False
    consultas_llm_mes: int = 0
    regiao_brasil: bool = True
    restricoes: list[str] = field(default_factory=list)
    prioridade: str | None = None
    sinais: dict[str, float] = field(default_factory=dict)
    sem_ip_fixo: bool = False
    rto_minutos: bool = False

    @property
    def porte(self) -> str:
        if self.volume_gb > 10_000 or self.eventos_por_segundo > 1_000 or self.usuarios_bi > 500:
            return "G"
        if self.volume_gb > 200 or self.usuarios_bi > 50 or self.atualizacoes_dia >= 24 or self.fontes >= 8 or self.streaming:
            return "M"
        return "P"

    @property
    def volume_medio_12m(self) -> float:
        g = self.crescimento_mes
        if g <= 0:
            return self.volume_gb
        return self.volume_gb * ((1 + g) ** 12 - 1) / (12 * g)

    @property
    def usa_spark(self) -> bool:
        return self.porte == "G" or self.volume_gb > 1_000

    @property
    def execucoes_mes(self) -> float:
        return min(self.atualizacoes_dia, 96) * 30

    @property
    def processado_gb_mes(self) -> float:
        # Pipelines incrementais: dado novo passa por bronze -> silver -> gold
        # (~6 leituras/escritas) + leitura de dimensões a cada execução.
        novo = self.volume_medio_12m * max(self.crescimento_mes, 0.02)
        return novo * 6 + self.execucoes_mes * min(self.volume_medio_12m * 0.005, 25)

    @property
    def consulta_tb_mes(self) -> float:
        # Painéis leem a camada gold (agregada, ~3% do volume bruto) e só as
        # partições recentes; o BI faz cache entre atualizações.
        gold = max(0.5, self.volume_medio_12m * 0.03)
        paineis = self.fontes * 3
        refresh = paineis * min(self.atualizacoes_dia, 24) * 30 * min(2.0, gold * 0.1)
        analistas = max(1.0, self.usuarios_bi * 0.2)
        adhoc = analistas * 10 * 22 * min(5.0, gold * 0.1)
        transformacao = 0.0 if self.usa_spark else self.processado_gb_mes
        return (refresh + adhoc + transformacao) / 1024


def _escolhidas(v: Any) -> list[str]:
    if v is None or v == "":
        return []
    return [str(x) for x in v] if isinstance(v, list) else [str(v)]


def perfil_de_respostas(respostas: dict[str, Any], sinais: dict[str, float] | None = None) -> PerfilCarga:
    r = respostas
    vol = r.get("dados.volume_total")
    volume = VOLUME_GB.get(vol) or VOLUME_POR_REGISTROS_GB.get(r.get("dados.volume.registros", ""), 50)
    lat = r.get("dados.latencia", "diario")
    eventos = EVENTOS_S.get(r.get("dados.rt.eventos", ""), 0)
    casos = set(_escolhidas(r.get("ia.casos")))
    interesse = r.get("ia.interesse", "nenhum")
    usa_ia = interesse in ("explorar", "caso_definido", "producao")
    llm = usa_ia and bool(casos & {"rag", "agentes", "ocr", "sentimento"}) or r.get("cons.perguntas_linguagem") == "sim"
    usuarios = USUARIOS.get(r.get("cons.usuarios", ""), 10)
    return PerfilCarga(
        volume_gb=volume,
        crescimento_mes=CRESCIMENTO.get(r.get("dados.crescimento", "nao_sei"), 0.05),
        atualizacoes_dia=ATUALIZACOES_DIA.get(lat, 1),
        streaming=lat == "tempo_real" or eventos >= 1_500 or r.get("dados.iot.frequencia") == "segundos",
        eventos_por_segundo=eventos,
        usuarios_bi=usuarios,
        fontes=max(1, len(_escolhidas(r.get("dados.fontes")))),
        ambientes=max(1, len(_escolhidas(r.get("infra.ambientes"))) or 1),
        ferramenta_bi=r.get("cons.bi"),
        ia_ml=usa_ia and bool(casos - {"rag", "agentes", "ocr", "sentimento"}),
        ia_llm=bool(llm),
        llm_local_obrigatorio=r.get("ia.llm_privacidade") == "local",
        consultas_llm_mes=usuarios * 10 * 22 if llm else 0,
        regiao_brasil=True,
        restricoes=_escolhidas(r.get("infra.restricoes")),
        prioridade=r.get("obj.prioridade"),
        sinais=dict(sinais or {}),
        sem_ip_fixo="nenhum" in _escolhidas(r.get("infra.link.redundante")),
        rto_minutos=r.get("infra.disponibilidade") == "minutos",
    )


def carregar_precos(caminho: Path | str) -> dict[str, Any]:
    with open(caminho, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _custo_llm_api(perfil: PerfilCarga, precos: dict[str, Any], modelo: str = "claude-haiku-5-5") -> float:
    if not perfil.ia_llm or perfil.llm_local_obrigatorio:
        return 0.0
    p = precos["llm_api"][modelo]
    entrada = perfil.consultas_llm_mes * 3_000 / 1e6
    saida = perfil.consultas_llm_mes * 600 / 1e6
    return entrada * p["entrada"] + saida * p["saida"]


def _estimar_cloud(pid: str, perfil: PerfilCarga, precos: dict[str, Any]) -> dict[str, Any]:
    c = precos["provedores"][pid]
    mult = precos["regiao_brasil"][pid] if perfil.regiao_brasil else 1.0
    porte = perfil.porte
    fator_amb = 1 + 0.3 * (perfil.ambientes - 1)
    comp: dict[str, float] = {}

    armazenado = perfil.volume_medio_12m * 1.3  # camadas bronze/silver/gold em Parquet
    gratis_obj = c.get("free_tier", {}).get("objeto_gb", 0)
    comp["armazenamento"] = max(0.0, armazenado - gratis_obj) * c["armazenamento_objeto_gb"] * mult
    comp["backup"] = perfil.volume_medio_12m * c["armazenamento_frio_gb"] * mult

    vm = {"P": ("vm_pequena_h", 1, 100), "M": ("vm_media_h", 1, 200), "G": ("vm_grande_h", 2, 500)}[porte]
    horas_vm = HORAS_MES * vm[1] * fator_amb
    custo_vm = c[vm[0]] * horas_vm
    disco = vm[2] * vm[1] * c["disco_gb"]
    if pid == "oci":
        ft = c["free_tier"]
        ocpu, ram = {"vm_pequena_h": (2, 12), "vm_media_h": (4, 24), "vm_grande_h": (8, 48)}[vm[0]]
        excedente_ocpu = max(0.0, ocpu * horas_vm - ft["ocpu_h_mes"])
        excedente_ram = max(0.0, ram * horas_vm - ft["gb_ram_h_mes"])
        custo_vm = excedente_ocpu * 0.01 + excedente_ram * 0.0015
        disco = max(0, vm[2] * vm[1] - ft["disco_gb"]) * c["disco_gb"]
    comp["computacao"] = (custo_vm + disco) * mult

    tb = perfil.consulta_tb_mes
    if pid == "oci":
        # Porte P: DuckDB/PostgreSQL na própria VM. M/G: Autonomous DW com 2 ECPU
        # ligado ~12 h/dia útil (parada agendada).
        comp["consulta"] = 0.0 if porte == "P" else c["adw_ecpu_h"] * 2 * 264 * (2 if porte == "G" else 1)
    else:
        cobravel = max(0.0, tb - c.get("consulta_gratis_tb", 0.0))
        comp["consulta"] = cobravel * c["consulta_tb"] * mult

    if perfil.usa_spark:
        vcpu_h = perfil.processado_gb_mes / 8  # ~8 GB por vCPU-hora em Parquet
        comp["processamento_spark"] = vcpu_h * c["spark_vcpu_h"] * mult
    if perfil.streaming:
        gb_mes = max(perfil.eventos_por_segundo, 50) * 1e-6 * 86_400 * 30  # ~1 KB por evento
        comp["streaming"] = (c["streaming_base_mes"] + gb_mes * c["streaming_gb"]) * mult

    saida = perfil.usuarios_bi * 0.5
    comp["saida_internet"] = max(0.0, saida - c["saida_gratis_gb"]) * c["saida_internet_gb"]

    bi = perfil.ferramenta_bi
    if bi in BI_POR_FERRAMENTA:
        comp["bi"] = BI_POR_FERRAMENTA[bi] * perfil.usuarios_bi
    elif bi == "quicksight" and pid != "aws":
        comp["bi"] = 0.0  # fora da AWS, troca por Metabase/Superset na VM
    else:
        comp["bi"] = c["bi_por_usuario"] * perfil.usuarios_bi + c["bi_autor"]

    if perfil.ia_ml:
        comp["ia_ml"] = c["vm_media_h"] * 200 * mult
    if perfil.ia_llm:
        if perfil.llm_local_obrigatorio:
            comp["ia_gpu"] = c["gpu_h"] * 8 * 22 * mult
        else:
            comp["ia_llm_api"] = _custo_llm_api(perfil, precos)
    comp["fixos"] = c["fixos_mes"]

    comp = {k: round(v, 2) for k, v in comp.items()}
    return {
        "id": pid,
        "nome": c["nome"],
        "regiao": "Brasil" if perfil.regiao_brasil else "EUA",
        "componentes_usd": comp,
        "total_usd": round(sum(comp.values()), 2),
        "servicos": c["servicos"],
        "gratuidades": c.get("gratuidades", ""),
        "dicas": DICAS[pid],
    }


def _estimar_onprem(perfil: PerfilCarga, precos: dict[str, Any], cambio: float, tarifa_kwh: float, custo_hora: float) -> dict[str, Any]:
    op = precos["on_premise"]
    perfil_hw = op["perfis"][perfil.porte]
    comp: dict[str, float] = {
        "hardware_amortizado": perfil_hw["hardware_brl"] / op["amortizacao_meses"],
        "energia": perfil_hw["potencia_media_w"] * HORAS_MES / 1000 * tarifa_kwh,
        "backup_externo": perfil.volume_medio_12m * 1.3 * op["backup_externo_gb_usd"] * cambio,
    }
    if perfil.sem_ip_fixo:
        comp["link_ip_fixo"] = op["link_ip_fixo_brl"]
    if perfil.ia_llm:
        if perfil.llm_local_obrigatorio:
            gpu = op["gpu_local"]
            comp["ia_gpu_local"] = gpu["hardware_brl"] / op["amortizacao_meses"] + gpu["potencia_media_w"] * 176 / 1000 * tarifa_kwh
        else:
            comp["ia_llm_api"] = _custo_llm_api(perfil, precos) * cambio
    bi = perfil.ferramenta_bi
    if bi in BI_POR_FERRAMENTA:
        comp["bi"] = BI_POR_FERRAMENTA[bi] * perfil.usuarios_bi * cambio
    comp = {k: round(v, 2) for k, v in comp.items()}
    total = round(sum(comp.values()), 2)
    operacao = perfil_hw["horas_operacao_mes"] * custo_hora
    alertas = []
    if perfil.volume_gb > 50_000:
        alertas.append("Volume acima de 50 TB: on-premise exige storage dedicado e equipe; não recomendado como primeira opção.")
    if perfil.rto_minutos:
        alertas.append("RTO em minutos exige redundância (2+ nós, link e energia redundantes); o perfil já considera cluster só no porte G.")
    if perfil.sem_ip_fixo:
        alertas.append("Sem IP fixo: use Cloudflare Tunnel ou Tailscale para acesso externo seguro.")
    return {
        "id": "onprem",
        "nome": "On-premise",
        "regiao": "Local (cliente ou ZimaOS)",
        "hardware": perfil_hw["descricao"],
        "investimento_inicial_brl": perfil_hw["hardware_brl"] + (op["gpu_local"]["hardware_brl"] if perfil.llm_local_obrigatorio and perfil.ia_llm else 0),
        "componentes_brl": comp,
        "total_brl": total,
        "operacao_brl": round(operacao, 2),
        "tco_brl": round(total + operacao, 2),
        "alertas": alertas,
        "dicas": DICAS["onprem"],
    }


def estimar(
    perfil: PerfilCarga,
    precos: dict[str, Any],
    cambio: float = 5.50,
    tarifa_kwh: float = 0.90,
    custo_hora_operacao: float = 120.0,
    pagamento_usd_cartao: bool | None = None,
) -> dict[str, Any]:
    if pagamento_usd_cartao is None:
        pagamento_usd_cartao = "pagamento_brl" not in perfil.restricoes
    iof = precos["pagamento"]["iof_cartao_internacional"] if pagamento_usd_cartao else 0.0
    horas_cloud = precos["operacao_cloud_horas"][perfil.porte]

    clouds = []
    for pid in PROVEDORES:
        e = _estimar_cloud(pid, perfil, precos)
        e["total_brl"] = round(e["total_usd"] * cambio * (1 + iof), 2)
        e["operacao_brl"] = round(horas_cloud * custo_hora_operacao, 2)
        e["tco_brl"] = round(e["total_brl"] + e["operacao_brl"], 2)
        clouds.append(e)
    onprem = _estimar_onprem(perfil, precos, cambio, tarifa_kwh, custo_hora_operacao)
    opcoes = clouds + [onprem]

    # Viabilidade por restrições declaradas
    so_local = {"sem_saas", "air_gapped"} & set(perfil.restricoes)
    for o in opcoes:
        o["viavel"] = True
        o["motivos"] = []
        if so_local and o["id"] != "onprem":
            o["viavel"] = False
            o["motivos"].append("Restrição do cliente impede dados em provedor externo.")
        if o["id"] == "onprem" and perfil.volume_gb > 100_000:
            o["viavel"] = False
            o["motivos"].append("Volume incompatível com o perfil on-premise padronizado.")

    # Ranking: custo total (TCO) + afinidade (sinais do questionário)
    pesos = {"custo": 0.6, "afinidade": 0.4}
    if perfil.prioridade == "custo":
        pesos = {"custo": 0.8, "afinidade": 0.2}
    elif perfil.prioridade == "autonomia":
        pesos = {"custo": 0.4, "afinidade": 0.6}
    viaveis = [o for o in opcoes if o["viavel"]] or opcoes
    menor = min(o["tco_brl"] for o in viaveis)
    afin = {o["id"]: perfil.sinais.get(o["id"], 0.0) for o in opcoes}
    lo, hi = min(afin.values()), max(afin.values())
    for o in opcoes:
        nota_custo = 100 * menor / o["tco_brl"] if o["tco_brl"] else 100
        nota_afin = 50.0 if hi == lo else 100 * (afin[o["id"]] - lo) / (hi - lo)
        penal = 0.0
        if o["id"] == "onprem" and perfil.prioridade == "escala":
            penal = 15.0
            o["motivos"].append("Prioridade em escalabilidade penaliza on-premise.")
        o["nota"] = round(pesos["custo"] * nota_custo + pesos["afinidade"] * nota_afin - penal, 1) if o["viavel"] else 0.0
        o["afinidade"] = afin[o["id"]]
    ranking = sorted(opcoes, key=lambda o: o["nota"], reverse=True)

    premissas = [
        f"Porte {perfil.porte}: volume médio em 12 meses de {perfil.volume_medio_12m:,.0f} GB ".replace(",", ".")
        + f"(crescimento {perfil.crescimento_mes:.0%}/mês), "
        f"{perfil.usuarios_bi} usuários de BI, {perfil.fontes} fontes, {perfil.atualizacoes_dia:g} atualizações/dia.",
        f"Consultas estimadas: {perfil.consulta_tb_mes:.2f} TB varridos/mês na camada gold.",
        f"Câmbio US$ 1 = R$ {cambio:.2f}" + (f", IOF {iof:.1%} (cartão internacional)." if iof else ", faturamento em reais (sem IOF; impostos locais variam)."),
        "Região Brasil para todas as clouds (multiplicador sobre preço dos EUA; OCI tem preço único)." if perfil.regiao_brasil else "Regiões dos EUA.",
        f"Operação: {horas_cloud} h/mês em cloud e {precos['on_premise']['perfis'][perfil.porte]['horas_operacao_mes']} h/mês on-premise a R$ {custo_hora_operacao:.0f}/h.",
        f"Energia a R$ {tarifa_kwh:.2f}/kWh; hardware on-premise amortizado em {precos['on_premise']['amortizacao_meses']} meses.",
        f"Preços de referência: {precos['data_referencia']}.",
    ]
    return {
        "perfil": {**asdict(perfil), "porte": perfil.porte, "volume_medio_12m": round(perfil.volume_medio_12m, 1)},
        "premissas": premissas,
        "opcoes": opcoes,
        "ranking": [{"id": o["id"], "nome": o["nome"], "nota": o["nota"], "tco_brl": o["tco_brl"], "viavel": o["viavel"]} for o in ranking],
        "recomendacao": ranking[0]["id"],
        "mais_barato": min(viaveis, key=lambda o: o["tco_brl"])["id"],
        "tabela_markdown": tabela(opcoes, ranking),
    }


def _brl(v: float) -> str:
    return f"R$ {v:,.0f}".replace(",", ".")


def tabela(opcoes: list[dict[str, Any]], ranking: list[dict[str, Any]]) -> str:
    posicao = {o["id"]: i + 1 for i, o in enumerate(ranking)}
    linhas = [
        "| # | Opção | Infra/mês | Operação/mês | TCO/mês | TCO 12 meses | Nota |",
        "|---|-------|----------:|-------------:|--------:|-------------:|-----:|",
    ]
    for o in sorted(opcoes, key=lambda x: posicao[x["id"]]):
        extra = "" if o["viavel"] else " (inviável)"
        linhas.append(
            f"| {posicao[o['id']]} | {o['nome']}{extra} | {_brl(o['total_brl'])} | {_brl(o['operacao_brl'])} | "
            f"{_brl(o['tco_brl'])} | {_brl(o['tco_brl'] * 12)} | {o['nota']:.0f} |"
        )
    return "\n".join(linhas)
