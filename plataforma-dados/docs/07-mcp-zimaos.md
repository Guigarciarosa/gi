# 07 — Servidor MCP no ZimaOS

## 1. Pré-requisitos
- ZimaOS atualizado, com Docker (já vem no sistema) e acesso ao terminal (SSH ou terminal web, conforme a versão).
- GPU NVIDIA reconhecida: `nvidia-smi` deve listar a placa. Versões recentes do ZimaOS trazem suporte a GPU NVIDIA; sem driver, o Ollama roda na CPU (mais lento, funciona).
- 200 GB livres em `/DATA`.

## 2. Copiar o projeto para o servidor
Opção A — Git (se o repositório estiver acessível):
```bash
cd /DATA/AppData
docker run --rm -v "$PWD":/git alpine/git clone https://github.com/Guigarciarosa/gi.git plataforma-src
```
Opção B — Google Drive: baixe a pasta **Cardume — Plataforma de Dados com Agentes**
(arquivo `plataforma-dados.zip`) e copie para `/DATA/AppData/plataforma-src` pelo
gerenciador de arquivos do ZimaOS ou por `scp`.

## 3. Instalar
```bash
cd /DATA/AppData/plataforma-src/plataforma-dados/infra/zimaos
bash instalar.sh                         # núcleo: MCP + Qdrant + Ollama
# opcionais:
bash instalar.sh dados automacao monitor # + PostgreSQL/Metabase, n8n, Uptime Kuma
```
O script cria o `.env` com token e senhas aleatórias, prepara as pastas em
`/DATA/AppData/plataforma`, verifica a GPU, sobe os contêineres e baixa os modelos
(`bge-m3` e `qwen3:4b`, ~4 GB no total).

Ao final ele mostra:
```
Questionário:  http://192.168.x.x:8787/?token=...
MCP:           http://192.168.x.x:8787/mcp   (Authorization: Bearer <MCP_TOKEN>)
```

## 4. Indexar a base de conhecimento
Pelo cliente MCP: ferramenta `memoria_reindexar_base`. Ou no terminal:
```bash
docker compose exec plataforma python -c "from plataforma.server import plataforma, CFG; print(plataforma().memoria.indexar_pasta(CFG.raiz, ['docs','agentes','skills']))"
```
Rode de novo sempre que editar `docs/`, `agentes/` ou `skills/`.

## 5. Conectar o Claude

### Claude Code (terminal)
```bash
claude mcp add --transport http plataforma http://192.168.x.x:8787/mcp --header "Authorization: Bearer SEU_TOKEN"
```

### Claude Desktop (mesma rede ou via Tailscale)
Em `claude_desktop_config.json`, use a ponte `mcp-remote`:
```json
{
  "mcpServers": {
    "plataforma": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://zima.tailnet:8787/mcp", "--header", "Authorization: Bearer SEU_TOKEN"]
    }
  }
}
```

### claude.ai e app do Claude no celular (conector personalizado)
O conector remoto precisa de um endereço HTTPS público:
1. Crie um túnel na Cloudflare (Zero Trust → Networks → Tunnels), aponte `mcp.seudominio.com.br` para `http://plataforma:8787` e cole o token do túnel em `CLOUDFLARE_TUNNEL_TOKEN`.
2. `bash instalar.sh acesso` (sobe o `cloudflared`).
3. No `.env`: `MCP_HOSTS_PERMITIDOS=mcp.seudominio.com.br` e reinicie (`docker compose up -d`).
4. Em claude.ai → Configurações → Conectores → Adicionar conector personalizado, use
   `https://mcp.seudominio.com.br/mcp?token=SEU_TOKEN`.
Assim você usa a plataforma do celular, de qualquer lugar.

### Outros clientes MCP
Open WebUI, n8n (nó MCP Client) e qualquer cliente compatível com Streamable HTTP
usam a mesma URL e o mesmo token.

## 6. Primeiro cliente (teste)
No Claude conectado:
1. "Crie o cliente Cooperativa Teste" → `cliente_criar`.
2. "Conduza o discovery" → prompt `discovery_conversado`, ou envie `http://.../?token=...` ao cliente.
3. "Rode o time completo para cooperativa-teste" → prompt `rodar_time_completo`.
4. "Gere a proposta" → `proposta_gerar` (arquivo em `/DATA/AppData/plataforma/servidor/entregaveis/<slug>/proposta.md`).

## 7. Operação
| Tarefa | Comando |
|---|---|
| Ver estado | `docker compose ps` · ferramenta `plataforma_saude` |
| Logs | `docker compose logs -f plataforma` |
| Atualizar | `git pull` (ou copiar nova versão) → `docker compose up -d --build` |
| Trocar modelo local | editar `MODELO_LOCAL` no `.env` → `docker compose up -d ollama-modelos` |
| Backup | ver abaixo |

### Backup (restic para Backblaze B2 ou Cloudflare R2)
```bash
export RESTIC_REPOSITORY=s3:https://s3.us-west-000.backblazeb2.com/seu-bucket
export RESTIC_PASSWORD=...  AWS_ACCESS_KEY_ID=...  AWS_SECRET_ACCESS_KEY=...
docker run --rm -v /DATA/AppData/plataforma:/dados:ro -e RESTIC_REPOSITORY -e RESTIC_PASSWORD \
  -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY restic/restic backup /dados --exclude /dados/ollama
```
Agende diariamente (agendador do ZimaOS ou cron) e teste a restauração todo mês.
O Qdrant também aceita snapshots por coleção (`POST /collections/<nome>/snapshots`).

## 8. Problemas comuns
| Sintoma | Causa provável | Solução |
|---|---|---|
| `could not select device driver "nvidia"` | Sem driver/runtime NVIDIA | Instale o suporte a GPU do ZimaOS ou remova o bloco `deploy` do `ollama` |
| `plataforma_saude` mostra Ollama indisponível | Modelo ainda baixando | `docker compose logs ollama-modelos` |
| 401 nas chamadas | Token ausente | Header `Authorization: Bearer` ou `?token=` na URL |
| 421/400 "Invalid Host header" | `MCP_HOSTS_PERMITIDOS` sem o host usado | Inclua o host (com porta, se houver) |
| Respostas lentas do agente local | Modelo grande para 6 GB | Volte para `qwen3:4b` ou use o modo assistido |
| Erro de dimensão no Qdrant | Trocou o modelo de embedding | Apague as coleções e reindexe (dimensões diferentes) |
