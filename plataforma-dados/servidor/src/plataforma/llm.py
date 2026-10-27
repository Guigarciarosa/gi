"""Backends de LLM para os agentes.

- `ollama`: modelo local na GPU de 6 GB (padrão qwen3:4b). Sem custo por uso;
  bom para rascunhos, resumos e tarefas estruturadas.
- `anthropic`: Claude pela API, para os entregáveis que vão ao cliente
  (arquitetura, custos, proposta). Custa centavos por cliente.
- `nenhum`: o servidor só monta o contexto; quem raciocina é o cliente MCP
  (Claude Desktop / Claude Code) e devolve o resultado com `entregavel_salvar`.
"""

from __future__ import annotations

import re
from typing import Protocol

import httpx2 as httpx

from .config import Config


class ErroLLM(RuntimeError):
    pass


class LLM(Protocol):
    nome: str

    def gerar(self, sistema: str, usuario: str, max_tokens: int = 8000) -> str: ...


class OllamaLLM:
    def __init__(self, url: str, modelo: str, contexto: int, timeout: float = 900.0):
        self.url = url.rstrip("/")
        self.modelo = modelo
        self.contexto = contexto
        self.timeout = timeout
        self.nome = f"ollama:{modelo}"

    def gerar(self, sistema: str, usuario: str, max_tokens: int = 8000) -> str:
        corpo = {
            "model": self.modelo,
            "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": usuario}],
            "stream": False,
            "think": False,
            "options": {"num_ctx": self.contexto, "num_predict": max_tokens, "temperature": 0.3},
        }
        try:
            r = httpx.post(f"{self.url}/api/chat", json=corpo, timeout=self.timeout)
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise ErroLLM(f"Ollama indisponível em {self.url}: {e}") from e
        texto = r.json().get("message", {}).get("content", "")
        return re.sub(r"<think>.*?</think>", "", texto, flags=re.S).strip()


class AnthropicLLM:
    def __init__(self, modelo: str, esforco: str):
        import anthropic  # dependência opcional

        self._anthropic = anthropic
        self.cliente = anthropic.Anthropic(max_retries=4)
        self.modelo = modelo
        self.esforco = esforco
        self.nome = f"anthropic:{modelo}"

    def gerar(self, sistema: str, usuario: str, max_tokens: int = 32000) -> str:
        a = self._anthropic
        try:
            with self.cliente.beta.messages.stream(
                model=self.modelo,
                max_tokens=max_tokens,
                # O papel + skill do agente é estável entre clientes: fica em cache.
                system=[{"type": "text", "text": sistema, "cache_control": {"type": "ephemeral"}}],
                messages=[{"role": "user", "content": usuario}],
                thinking={"type": "adaptive"},
                output_config={"effort": self.esforco},
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            ) as stream:
                resposta = stream.get_final_message()
        except a.AuthenticationError as e:
            raise ErroLLM("ANTHROPIC_API_KEY inválida ou ausente.") from e
        except a.RateLimitError as e:
            raise ErroLLM("Limite de requisições da API atingido; tente de novo em alguns minutos.") from e
        except a.APIStatusError as e:
            raise ErroLLM(f"Erro da API ({e.status_code}): {e.message}") from e
        except a.APIConnectionError as e:
            raise ErroLLM("Sem conexão com a API da Anthropic.") from e
        if resposta.stop_reason == "refusal":
            raise ErroLLM("O modelo recusou esta solicitação; revise o conteúdo enviado.")
        texto = "".join(b.text for b in resposta.content if b.type == "text").strip()
        if resposta.stop_reason == "max_tokens":
            texto += "\n\n[Entregável cortado no limite de tokens; rode o agente de novo para completar.]"
        return texto


def criar(cfg: Config, backend: str | None = None) -> LLM | None:
    escolhido = (backend or cfg.llm_backend).lower()
    if escolhido == "ollama":
        return OllamaLLM(cfg.ollama_url, cfg.modelo_local, cfg.contexto_local)
    if escolhido == "anthropic":
        return AnthropicLLM(cfg.modelo_anthropic, cfg.esforco_anthropic)
    if escolhido in ("nenhum", "", "none"):
        return None
    raise ErroLLM(f"Backend desconhecido: {escolhido}. Use ollama, anthropic ou nenhum.")
