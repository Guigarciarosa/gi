# Imagem do servidor MCP da plataforma.
# Contexto de build: a raiz `plataforma-dados/` (o compose já aponta para ela).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PLATAFORMA_RAIZ=/app \
    PLATAFORMA_DADOS=/data

WORKDIR /app

COPY servidor/pyproject.toml servidor/pyproject.toml
COPY servidor/src servidor/src
RUN pip install --no-cache-dir "./servidor[anthropic]"

# Conteúdo lido em tempo de execução. No compose estas pastas também são
# montadas como volume somente leitura, para editar sem reconstruir a imagem.
COPY questionario questionario
COPY agentes agentes
COPY skills skills
COPY docs docs
COPY conhecimento conhecimento

RUN useradd --system --uid 10001 plataforma && mkdir -p /data && chown plataforma /data
USER plataforma

EXPOSE 8787
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8787/api/saude', timeout=4)"

CMD ["python", "-m", "plataforma.server"]
