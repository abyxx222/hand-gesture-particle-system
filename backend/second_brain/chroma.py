"""Vector-store boundary: use Chroma when installed, otherwise MemoryIndex."""
from pathlib import Path
from .index import MemoryIndex, SearchResult
from .models import MemoryChunk


def _chroma_metadata(chunk: MemoryChunk) -> dict[str, str | int | float | bool]:
    metadata: dict[str, str | int | float | bool] = {"source": chunk.source}
    for key, value in chunk.metadata.items():
        if value is None:
            continue
        if isinstance(value, (str, int, float, bool)):
            metadata[key] = value
        elif isinstance(value, list):
            metadata[key] = ", ".join(str(item) for item in value)
        else:
            metadata[key] = str(value)
    return metadata


class ChromaIndex(MemoryIndex):
    """Drop-in index that can be upgraded to Chroma without changing the API."""
    def __init__(self, path: Path | None = None) -> None:
        super().__init__()
        self.path = path
        self.backend = "memory"
        try:
            import chromadb  # type: ignore
            self._client = chromadb.PersistentClient(path=str(path)) if path else chromadb.Client()
            self._collection = self._client.get_or_create_collection("memories")
            self.backend = "chroma"
        except (ImportError, RuntimeError):
            self._client = None
            self._collection = None

    def add(self, chunks: list[MemoryChunk]) -> None:
        # Keep a local metadata mirror for graph construction and offline fallback.
        super().add(chunks)
        if self._collection is None:
            return
        self._collection.upsert(
            ids=[c.id for c in chunks], documents=[c.text for c in chunks],
            metadatas=[_chroma_metadata(c) for c in chunks],
        )

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        if self._collection is None:
            return super().search(query, top_k)
        result = self._collection.query(query_texts=[query], n_results=top_k)
        return [SearchResult(MemoryChunk(id=i, text=d, source=m.get("source", "" ), metadata=m), 0.0)
                for i, d, m in zip(result["ids"][0], result["documents"][0], result["metadatas"][0])]
