# Identidade visual — Cardume

## Conceito
**Cardume** é um grupo de peixes que se move como um só, sem um chefe gritando
ordens: cada um lê o vizinho e o grupo inteiro muda de direção junto. É exatamente o
time da plataforma — nove especialistas (agentes) coordenados, levando o cliente para
uma decisão.

- **Assinatura**: *Nove especialistas. Um só movimento.*
- **Promessa**: *Seus dados já sabem a resposta. Falta alguém fazer a pergunta certa.*
- **Personalidade**: técnica sem ser fria; direta; regional com alcance nacional (Oeste do Paraná, atende o Brasil); obcecada por número certo e custo justo.

> Nome provisório. Antes de registrar, pesquise no INPI (classe 42 — serviços de TI e
> classe 35 — consultoria) e a disponibilidade de domínio (.com.br) e do @ no Instagram.
> Alternativas que mantêm o conceito: *Cardume Dados*, *Cardume Analytics*.

## Logo
| Arquivo | Uso |
|---|---|
| `logo-horizontal.svg` | Padrão em fundos claros |
| `logo-horizontal-negativo.svg` | Fundos escuros (abissal) |
| `logo-simbolo.svg` | Ícone de app, favicon, avatar quadrado |
| `logo-simbolo-escuro.svg` | Ícone em fundo escuro |
| `logo-simbolo-transparente.svg` | Símbolo solto sobre fundos claros ou como grafismo |
| `logo-simbolo-branco.svg` | Símbolo branco com peixe-líder coral (avatar do Instagram) |

O símbolo: **nove peixes** em formação diagonal ascendente (os agentes, e também uma
linha de tendência subindo). O **peixe da frente, em coral**, é a decisão — o único
elemento coral do logo.

Regras:
- Área de proteção mínima = altura de um peixe em volta do logo.
- Tamanho mínimo: símbolo com 24 px; logo horizontal com 96 px de largura.
- Não mude a cor do peixe-líder, não gire a formação, não use sombra ou contorno.
- O texto do logo está em curvas (não depende da fonte instalada). Para regerar: `python scripts/gerar_logo.py`.

## Cores
| Token | Hex | Uso |
|---|---|---|
| `--abissal` | `#0B2238` | Fundo escuro principal; texto em fundo claro |
| `--mar` | `#163A5C` | Superfícies sobre o abissal |
| `--cardume` | `#0F7C7A` | Cor da marca: botões, destaques, fundo de posts centrais |
| `--cardume-claro` | `#3CC6BE` | Cardume sobre fundo escuro |
| `--espuma` | `#F2F6F6` | Fundo claro (verde-água quase branco) |
| `--espuma-2` | `#DCF0ED` | Seleção, chips, realce suave |
| `--coral` | `#E4572E` | **Um** destaque por peça: CTA, número-chave, peixe-líder |
| `--coral-claro` | `#FF8A63` | Coral sobre fundo escuro |
| `--nevoa` | `#4A6070` | Texto secundário no claro |
| `--nevoa-clara` | `#A9BFCB` | Texto secundário no escuro |

Proporção sugerida: 60% fundo (abissal ou espuma), 30% cardume, 10% coral.
Contraste: texto abissal sobre espuma e texto `#EAF3F4` sobre abissal passam com folga
do AA; coral só em títulos/elementos grandes ou botões com texto abissal.

## Tipografia
| Papel | Família | Pesos | Onde |
|---|---|---|---|
| Display | **Bricolage Grotesque** | 560–800 | Títulos, números grandes, logo |
| Texto | **Figtree** | 400–700 | Parágrafos, listas, interface |
| Dado | **JetBrains Mono** | 400–600 | Etiquetas, fórmulas, valores, rodapés |

As três são livres (SIL Open Font License); os arquivos estão em `fontes/` e o
`tokens.css` já os importa. Títulos com entrelinha 0,94–0,98 e espaçamento -0,025em;
etiquetas em caixa alta com espaçamento +0,14em.

## Grafismos
- **Peixe** (triângulo a -18°) como marcador de lista; o último item, coral, é a ação.
- **Cardume grande** cortado na borda do quadro como textura (opacidade 25–55%).
- **Barras com escala real** para dados; o menor/melhor valor em coral.
- **Fórmulas em mono** dentro de cartão branco com operadores em coral.

## Grade dos posts (1080 × 1350)
- Margem de 88 px; conteúdo essencial dentro dos 1012 px centrais (a grade do perfil corta as laterais em 3:4).
- Topo: logo à esquerda (62 px de altura) e etiqueta da série à direita.
- Rodapé: `@cardume.dados` e uma instrução curta (arraste, salve, link na bio).
- Fundos alternados escuro/claro para o perfil formar um xadrez; o post central da grade em cardume.

## Tom de voz
- Fala de **decisão e dinheiro** antes de tecnologia ("custo por km", não "pipeline").
- Números concretos e honestos; sempre que for simulação, dizer que é simulação.
- Frases curtas. Sem jargão sem explicação. Sem promessa de "revolucionar".
- Sotaque de quem conhece o cliente: cooperativa, safra, frota, associado, FIPE.

| Em vez de | Diga |
|---|---|
| "Soluções inovadoras em big data" | "Seu fechamento do mês em 1 dia, não em 5" |
| "Arquitetura escalável multicloud" | "Comparamos AWS, Google, Azure e Oracle com os seus números" |
| "Transformação digital" | "Tirar a planilha manual da segunda-feira da sua equipe" |
