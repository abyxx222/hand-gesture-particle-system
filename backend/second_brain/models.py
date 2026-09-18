from typing import Any, Literal
from pydantic import BaseModel, Field


class MemoryChunk(BaseModel):
    id: str
    text: str
    source: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=10000)
    top_k: int = Field(default=5, ge=1, le=20)
    stream: bool = False
    conversation_id: str = "default"


class AskResponse(BaseModel):
    answer: str
    sources: list[MemoryChunk] = Field(default_factory=list)


class GraphNode(BaseModel):
    id: str
    label: str
    kind: str = "memory"


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str = "references"


class GraphResponse(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


class ToolRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    arguments: dict[str, Any] = Field(default_factory=dict)
    confirmed: bool = False


class ToolResult(BaseModel):
    ok: bool
    output: Any = None
    requires_confirmation: bool = False
    error: str | None = None


class ToolSchema(BaseModel):
    name: str
    requires_confirmation: bool
    description: str = ""
    arguments: dict[str, Any] = Field(default_factory=dict)
    confirmation_details: str | None = None


class MemoryWriteRequest(BaseModel):
    text: str = Field(min_length=1, max_length=100000)
    source: str = "manual.md"
    name: str | None = None


class ProviderRequest(BaseModel):
    provider: Literal["mock", "openai", "anthropic", "grok"]
    model: str | None = None


class VoiceRequest(BaseModel):
    text: str = Field(min_length=1)
    voice: str = "alloy"


class Personality(BaseModel):
    name: str = "Sage"
    system_prompt: str = "Be thoughtful, concise, and cite memories when useful."
    traits: list[str] = Field(default_factory=lambda: ["curious", "grounded"])


class IndexRequest(BaseModel):
    text: str = ""
    source: str = "note.md"


class IndexPathRequest(BaseModel):
    path: str | None = None
