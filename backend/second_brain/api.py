import json
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from .chunking import chunk_markdown
from .config import Settings
from .chroma import ChromaIndex
from .models import AskRequest, AskResponse, GraphEdge, GraphNode, GraphResponse, IndexPathRequest, IndexRequest, MemoryWriteRequest, Personality, ProviderRequest, ToolRequest, ToolResult, VoiceRequest
from .providers import create_provider
from .ingest import index_notes
from .tools import ToolRegistry
from .memory import MemoryStore


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = Settings()
settings.ensure_dirs()
index = ChromaIndex(settings.chroma_dir)
provider = create_provider(settings)
tools = ToolRegistry(settings.allowed_root)
memory_store = MemoryStore(settings.memory_dir)
conversations: dict[str, list[dict[str, str]]] = {}
app = FastAPI(title="Personal AI Second Brain", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/index")
def index_markdown(payload: IndexRequest) -> dict[str, int]:
    chunks = chunk_markdown(payload.text, payload.source)
    index.add(chunks)
    logger.info("indexed %d chunks from %s", len(chunks), payload.source)
    return {"chunks": len(chunks)}


@app.post("/api/index/path")
def index_path(payload: IndexPathRequest) -> dict[str, int]:
    target = settings.notes_path if payload.path is None else (settings.notes_path / payload.path).resolve()
    root = settings.notes_path.resolve()
    if target != root and root not in target.parents:
        raise HTTPException(status_code=400, detail="path escapes notes root")
    if not target.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Notes directory does not exist: {root}. Create it and add .md files.",
        )
    try:
        count = index_notes(target, index)
    except (OSError, UnicodeError, ValueError) as exc:
        logger.exception("failed to index notes from %s", target)
        raise HTTPException(status_code=500, detail=f"Unable to index notes: {exc}") from exc
    return {"chunks": count}


@app.post("/api/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    results = index.search(request.question, request.top_k)
    sources = [result.chunk for result in results]
    history = conversations.setdefault(request.conversation_id, [])
    contextual_question = "\n".join(f"{item['role']}: {item['text']}" for item in history[-6:])
    answer = provider.answer(f"{contextual_question}\nuser: {request.question}", sources)
    history.extend([{"role": "user", "text": request.question}, {"role": "assistant", "text": answer}])
    return AskResponse(answer=answer, sources=sources)


@app.post("/api/memory")
def write_memory(payload: MemoryWriteRequest) -> dict[str, str | int]:
    chunks = chunk_markdown(payload.text, payload.source)
    index.add(chunks)
    name = payload.name or payload.source.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    path = memory_store.save(name, chunks)
    return {"path": str(path), "chunks": len(chunks)}


@app.get("/api/provider")
def provider_status() -> dict[str, str]:
    return {"provider": settings.provider, "model": settings.model}


@app.post("/api/provider")
def switch_provider(payload: ProviderRequest) -> dict[str, str]:
    global provider
    settings.provider = payload.provider
    if payload.model:
        settings.model = payload.model
    provider = create_provider(settings)
    return provider_status()


@app.post("/api/ask/stream")
def ask_stream(request: AskRequest) -> StreamingResponse:
    response = ask(request)
    def events():
        for word in response.answer.split():
            yield f"data: {json.dumps({'token': word + ' '})}\n\n"
        yield f"data: {json.dumps({'done': True, 'sources': [s.model_dump() for s in response.sources]})}\n\n"
    return StreamingResponse(events(), media_type="text/event-stream")


@app.get("/api/graph", response_model=GraphResponse)
def graph() -> GraphResponse:
    nodes = [GraphNode(id=chunk.id, label=chunk.source, kind="memory")
             for chunk, _ in index._items]
    edges: list[GraphEdge] = []
    for chunk, _ in index._items:
        links = set(chunk.metadata.get("links", []))
        for other, _ in index._items:
            if chunk.id == other.id:
                continue
            normalized = other.source.replace("\\", "/")
            if links and any(link.replace("\\", "/") in normalized or normalized.endswith(link.replace("\\", "/"))
                             for link in links):
                edges.append(GraphEdge(source=chunk.id, target=other.id, relation="links"))
            elif set(chunk.metadata.get("links", [])) & set(other.metadata.get("links", [])):
                edges.append(GraphEdge(source=chunk.id, target=other.id, relation="shared-link"))
            else:
                similarity = sum(a * b for a, b in zip(index.embedder.embed([chunk.text])[0],
                                                       index.embedder.embed([other.text])[0]))
                if similarity >= 0.72:
                    edges.append(GraphEdge(source=chunk.id, target=other.id, relation="semantic"))
    return GraphResponse(nodes=nodes, edges=edges)


@app.post("/api/tools/execute", response_model=ToolResult)
def execute_tool(request: ToolRequest) -> ToolResult:
    return tools.execute(request.name, request.arguments, request.confirmed)


@app.get("/api/tools")
def tool_schemas() -> list[dict]:
    return tools.schemas()


@app.post("/api/voice")
def voice(request: VoiceRequest) -> dict[str, str]:
    return {"text": request.text, "voice": request.voice, "status": "queued"}


@app.get("/api/personality", response_model=Personality)
def personality() -> Personality:
    return Personality(**settings.personality)
