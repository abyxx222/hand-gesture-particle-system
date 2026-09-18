import os
from typing import Any, Protocol
from .models import MemoryChunk
from .config import Settings


class Provider(Protocol):
    def answer(self, question: str, context: list[MemoryChunk]) -> str: ...


class MockProvider:
    def answer(self, question: str, context: list[MemoryChunk]) -> str:
        if not context:
            return "I don't have a matching memory yet."
        excerpts = " ".join(chunk.text[:240] for chunk in context)
        return f"Based on your memories: {excerpts}"


class OpenAIProvider(MockProvider):
    def __init__(self, client: Any | None = None, model: str = "gpt-4o-mini",
                 api_key: str | None = None, **kwargs) -> None:
        self.model = model
        if client is not None:
            self.client = client
            return
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OpenAI provider requires OPENAI_API_KEY; set it or inject a client for tests")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install the optional openai dependency: pip install openai") from exc
        self.client = OpenAI(api_key=key, **kwargs)

    def answer(self, question: str, context: list[MemoryChunk]) -> str:
        prompt = _context_prompt(question, context)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except (AttributeError, IndexError, TypeError, ValueError) as exc:
            raise RuntimeError(f"OpenAI request returned an invalid response: {exc}") from exc
        except Exception as exc:
            raise RuntimeError(f"OpenAI request failed: {exc}") from exc


class AnthropicProvider(MockProvider):
    def __init__(self, client: Any | None = None, model: str = "claude-3-5-sonnet-latest",
                 api_key: str | None = None, **kwargs) -> None:
        self.model = model
        if client is not None:
            self.client = client
            return
        key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("Anthropic provider requires ANTHROPIC_API_KEY; set it or inject a client for tests")
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise RuntimeError("Install the optional anthropic dependency: pip install anthropic") from exc
        self.client = Anthropic(api_key=key, **kwargs)

    def answer(self, question: str, context: list[MemoryChunk]) -> str:
        try:
            response = self.client.messages.create(
                model=self.model, max_tokens=1000,
                messages=[{"role": "user", "content": _context_prompt(question, context)}],
            )
            return response.content[0].text
        except (AttributeError, IndexError, TypeError, ValueError) as exc:
            raise RuntimeError(f"Anthropic request returned an invalid response: {exc}") from exc
        except Exception as exc:
            raise RuntimeError(f"Anthropic request failed: {exc}") from exc


class GrokProvider(OpenAIProvider):
    """Grok uses the OpenAI-compatible API; configure its base URL in production."""


def _context_prompt(question: str, context: list[MemoryChunk]) -> str:
    excerpts = "\n\n".join(f"[{chunk.source}]\n{chunk.text}" for chunk in context)
    return f"Answer using these personal memory excerpts. Cite sources when relevant.\n{excerpts}\n\nQuestion: {question}"


def create_provider(settings: Settings) -> Provider:
    if settings.provider == "mock":
        return MockProvider()
    if settings.provider == "openai":
        return OpenAIProvider(model=settings.model, api_key=settings.openai_api_key)
    if settings.provider == "anthropic":
        return AnthropicProvider(model=settings.model, api_key=settings.anthropic_api_key)
    if settings.provider == "grok":
        return GrokProvider(model=settings.model, api_key=settings.xai_api_key, base_url="https://api.x.ai/v1")
    raise ValueError(f"unsupported provider: {settings.provider}")
