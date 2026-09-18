from dataclasses import dataclass
from .embeddings import Embedder, MockEmbedder
from .models import MemoryChunk


@dataclass
class SearchResult:
    chunk: MemoryChunk
    score: float


class MemoryIndex:
    """Chroma-compatible abstraction with an in-memory fallback."""
    def __init__(self, embedder: Embedder | None = None) -> None:
        self.embedder = embedder or MockEmbedder()
        self._items: list[tuple[MemoryChunk, list[float]]] = []

    def add(self, chunks: list[MemoryChunk]) -> None:
        vectors = self.embedder.embed([chunk.text for chunk in chunks])
        self._items.extend(zip(chunks, vectors))

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        q = self.embedder.embed([query])[0]
        scored = [(chunk, sum(a * b for a, b in zip(q, vector))) for chunk, vector in self._items]
        return [SearchResult(c, s) for c, s in sorted(scored, key=lambda item: item[1], reverse=True)[:top_k]]

