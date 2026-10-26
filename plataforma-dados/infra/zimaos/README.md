# Instalação no ZimaOS

```bash
bash instalar.sh                         # núcleo: MCP + Qdrant + Ollama
bash instalar.sh dados automacao monitor # perfis opcionais
```

| Arquivo | Para quê |
|---|---|
| `docker-compose.yml` | Serviços: `plataforma` (MCP + questionário), `qdrant`, `ollama`, `ollama-modelos` e os perfis `dados`, `automacao`, `acesso`, `monitor` |
| `.env.example` | Variáveis (token, backend de LLM, modelos, câmbio, senhas). O `instalar.sh` cria o `.env` com segredos aleatórios |
| `instalar.sh` | Verifica Docker e GPU, cria pastas em `/DATA/AppData/plataforma`, sobe os serviços e mostra os links |
| `postgres-init/` | Cria o banco do Metabase na primeira subida do PostgreSQL |

Passo a passo completo, conexão do Claude, backup e problemas comuns: `docs/07-mcp-zimaos.md`.
