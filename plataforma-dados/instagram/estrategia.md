# Instagram — estratégia

## Objetivo
Gerar **diagnósticos gratuitos agendados** com donos e gestores de PMEs (agro,
transporte, proteção veicular, varejo, indústria), mostrando autoridade técnica em
linguagem de negócio. Métrica principal: diagnósticos agendados por mês.

## Perfil
- **Nome**: Cardume | Plataformas de Dados
- **@**: `@cardume.dados` (verifique disponibilidade; alternativas: `@cardumedados`, `@cardume.analytics`)
- **Categoria**: Serviços de TI / Consultoria
- **Foto**: `png/perfil-avatar.png`
- **Bio** (até 150 caracteres):
  ```
  Plataformas de dados sob medida para PMEs
  9 especialistas, 1 só movimento
  AWS · Google · Azure · Oracle · servidor próprio
  Cascavel-PR 👇 diagnóstico gratuito
  ```
- **Link**: página do questionário curto ou agenda (ex.: `discovery.seudominio.com.br` pelo Cloudflare Tunnel, ou um link do WhatsApp com mensagem pronta).
- **Destaques** (capas em `png/destaque-*.png`): **Sobre** · **Agentes** · **Custos** · **Diagnóstico**.

## Pilares de conteúdo
| Pilar | % | Exemplos |
|---|---|---|
| Educação de negócio | 40% | KPIs por segmento, sinais de que precisa de dados, fórmulas (custo/km, sinistralidade) |
| Prova e números | 25% | Simulações de custo de cloud, antes × depois, casos (com autorização) |
| Bastidores e método | 20% | Os 9 agentes trabalhando, o questionário, o servidor ZimaOS, IA local |
| Oferta | 15% | Diagnóstico gratuito, vagas do mês, pacotes |

## Formatos e cadência
- **Feed**: 3 posts/semana (seg, qua, sex) — carrosséis de 4–7 lâminas rendem mais salvamentos.
- **Reels**: 1–2/semana, 20–40 s, tela gravada ou rosto + texto; roteiros no calendário.
- **Stories**: diários, com enquetes e caixas de pergunta ("qual relatório você mais odeia montar?").
- Horários de teste: 7h–8h e 12h–13h (gestores antes do expediente e no almoço); ajuste pelos dados do perfil após 4 semanas.

## Funil
```
Post/Reel → perfil → link da bio → questionário curto (ou WhatsApp)
          → diagnóstico gratuito (20 min) → questionário completo → proposta
```
Resposta a DM em até 2 horas no horário comercial. Script:
> "Oi, {nome}! Obrigado por chamar. Para eu já chegar com algo útil no diagnóstico:
> qual é o segmento da empresa e qual número você mais gostaria de ver todo dia e
> hoje dá trabalho conseguir?"

## Hashtags (3–6 por post, misture alcance e nicho)
`#dados` `#businessintelligence` `#powerbi` `#engenhariadedados` `#gestaoempresarial`
`#agronegocio` `#cooperativismo` `#transportadora` `#protecaoveicular` `#cascavel`
`#oestedoparana` `#pme` `#lgpd` `#inteligenciaartificial`

## Indicadores (revisão mensal)
Alcance de não seguidores · salvamentos por post · cliques no link · DMs iniciadas ·
**diagnósticos agendados** · diagnósticos → propostas.
Guarde os posts publicados na memória da plataforma (`memoria_indexar`, coleção `marca`)
para manter o tom e não repetir temas.

## Coerência com o LinkedIn
O Instagram reaproveita os temas de autoridade do LinkedIn com outra embalagem:
no LinkedIn, texto e análise; no Instagram, a mesma ideia em carrossel visual com
um número forte. Publique o carrossel de custo de cloud nos dois (no LinkedIn como PDF).

## Como publicar
1. Abra os PNGs de `instagram/png/` no celular (pasta do Google Drive).
2. Publique na ordem `p01` → `p09` (o primeiro fica no canto inferior direito da grade); o `p03` é um carrossel com as lâminas `p03a` a `p03d`.
3. Copie a legenda de `legendas.md` e cole o texto alternativo (Configurações avançadas → Acessibilidade).
4. Para agendar, use o Meta Business Suite ou uma ferramenta de agendamento (ex.: Postiz).

Para editar as artes: altere `posts/posts.html` e rode `node scripts/renderizar_posts.mjs`.
