# Como montar o projeto a partir do Google Drive

A pasta do Drive guarda os arquivos-fonte. Alguns arquivos são gerados por script e
não foram copiados para o Drive. Para recriá-los num computador ou no ZimaOS:

```bash
# 1. Monte a estrutura de pastas igual à do Drive (plataforma-dados/...)
# 2. Fontes da marca (OFL) — necessárias para logo e posts
python scripts/baixar_fontes.py

# 3. Versões estáticas do questionário (questionario.html e questionario.json)
pip install pyyaml
python scripts/construir_questionario.py

# 4. Logos (já estão no Drive; regenere se mudar algo)
pip install fonttools brotli
python scripts/gerar_logo.py

# 5. Pacotes das skills para o Claude (dist/skills/*.zip)
python scripts/empacotar_skills.py

# 6. Posts do Instagram em PNG (já estão no Drive)
npm i -D playwright && npx playwright install chromium
node scripts/renderizar_posts.mjs

# 7. Testes do servidor
cd servidor && pip install -e ".[dev,anthropic]" && python -m pytest
```

Depois siga `docs/07-mcp-zimaos.md` para instalar no ZimaOS.

O repositório Git (`Guigarciarosa/gi`, branch `claude/plataforma-dados-agentes-11g939`)
tem tudo, inclusive os arquivos gerados, assim que o acesso de push for liberado.
