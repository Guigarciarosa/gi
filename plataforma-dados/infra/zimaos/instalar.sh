#!/usr/bin/env bash
# Instala/atualiza a plataforma no ZimaOS (ou em qualquer Linux com Docker).
# Uso:  bash instalar.sh            (núcleo)
#       bash instalar.sh dados automacao monitor   (com perfis opcionais)
set -euo pipefail

cd "$(dirname "$0")"
PERFIS=("$@")

echo "== Verificando Docker"
docker version --format '{{.Server.Version}}' >/dev/null
docker compose version >/dev/null

if [ ! -f .env ]; then
  cp .env.example .env
  token=$(openssl rand -hex 32 2>/dev/null || head -c 32 /dev/urandom | od -An -tx1 | tr -d ' \n')
  sed -i "s/^MCP_TOKEN=.*/MCP_TOKEN=${token}/" .env
  pg=$(openssl rand -hex 16 2>/dev/null || date +%s%N)
  sed -i "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=${pg}/" .env
  n8n=$(openssl rand -hex 24 2>/dev/null || date +%s%N)
  sed -i "s/^N8N_ENCRYPTION_KEY=.*/N8N_ENCRYPTION_KEY=${n8n}/" .env
  echo "Criado .env com segredos aleatórios. Revise-o antes de continuar (nano .env)."
fi

# shellcheck disable=SC1091
set -a; source .env; set +a
DADOS="${DADOS_HOST:-/DATA/AppData/plataforma}"
echo "== Pastas de dados em ${DADOS}"
mkdir -p "$DADOS"/{servidor,qdrant,ollama,postgres,n8n,uptime-kuma}
chown -R 10001 "$DADOS/servidor" 2>/dev/null || true
chown -R 1000:1000 "$DADOS/n8n" 2>/dev/null || true

echo "== GPU"
if command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
else
  echo "nvidia-smi não encontrado: o Ollama vai rodar na CPU."
  echo "Remova o bloco 'deploy' do serviço ollama no docker-compose.yml se a subida falhar."
fi

ARGS=()
for p in "${PERFIS[@]}"; do ARGS+=(--profile "$p"); done

echo "== Subindo serviços"
docker compose "${ARGS[@]}" up -d --build

echo "== Aguardando o servidor"
for _ in $(seq 1 30); do
  if curl -fs "http://127.0.0.1:${MCP_PORTA_HOST:-8787}/api/saude" >/dev/null; then break; fi
  sleep 2
done
curl -fs "http://127.0.0.1:${MCP_PORTA_HOST:-8787}/api/saude" && echo

echo "== Modelos do Ollama (o primeiro download pode levar alguns minutos)"
docker compose logs --no-log-prefix ollama-modelos | tail -n 3 || true

IP=$(hostname -I 2>/dev/null | awk '{print $1}')
cat <<EOF

Pronto.
  Questionário:  http://${IP:-SEU_IP}:${MCP_PORTA_HOST:-8787}/?token=${MCP_TOKEN}
  MCP:           http://${IP:-SEU_IP}:${MCP_PORTA_HOST:-8787}/mcp   (Authorization: Bearer <MCP_TOKEN>)

Próximo passo: indexe a base de conhecimento pelo seu cliente MCP com a ferramenta
memoria_reindexar_base, ou rode:
  docker compose exec plataforma python -c "from plataforma.server import plataforma, CFG; print(plataforma().memoria.indexar_pasta(CFG.raiz, ['docs','agentes','skills']))"
EOF
