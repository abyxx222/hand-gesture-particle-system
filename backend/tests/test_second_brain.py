from fastapi.testclient import TestClient
from second_brain.api import app, index, tools
from second_brain.chunking import chunk_markdown
from second_brain.config import Settings
from second_brain.memory import MemoryStore
from second_brain.providers import AnthropicProvider, MockProvider, OpenAIProvider, create_provider
from second_brain.ingest import index_notes
from pathlib import Path


def setup_function():
    index._items.clear()


def test_chunking_and_search():
    chunks = chunk_markdown("# Notes\n\nPython is useful for automation.", "notes.md", chunk_size=20, overlap=2)
    assert chunks and chunks[0].source == "notes.md"
    client = TestClient(app)
    client.post("/api/index", json={"text": "# Notes\n\nPython automation", "source": "x.md"})
    result = client.post("/api/ask", json={"question": "Python"})
    assert result.status_code == 200
    assert result.json()["sources"]


def test_sse_and_health():
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}
    response = client.post("/api/ask/stream", json={"question": "hello"})
    assert response.status_code == 200 and "data:" in response.text


def test_tool_confirmation_and_sandbox():
    tools._tools.clear()
    tools.register("echo", lambda value: value)
    client = TestClient(app)
    blocked = client.post("/api/tools/execute", json={"name": "echo", "arguments": {"value": "x"}})
    assert blocked.json()["requires_confirmation"]
    allowed = client.post("/api/tools/execute", json={"name": "echo", "arguments": {"value": "x"}, "confirmed": True})
    assert allowed.json()["output"] == "x"
    try:
        tools.path("../secrets")
        assert False
    except ValueError:
        pass


def test_config_validation_and_provider_selection():
    assert isinstance(create_provider(Settings(provider="mock")), MockProvider)
    try:
        Settings(provider="invalid")
        assert False
    except ValueError:
        pass


def test_atomic_memory_write(tmp_path: Path):
    store = MemoryStore(tmp_path)
    chunks = chunk_markdown("# Durable\n\ncontent", "a.md")
    path = store.save("notes", chunks)
    assert path.exists()
    assert store.load("notes")[0].text.startswith("# Durable")


def test_recursive_index_and_graph_links(tmp_path: Path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "a.md").write_text("# A\n\nSee [B](sub/b.md)", encoding="utf-8")
    (tmp_path / "sub" / "b.md").write_text("# B\n\nLinked", encoding="utf-8")
    index_notes(tmp_path, index)
    assert {chunk.source for chunk, _ in index._items} == {"a.md", "sub\\b.md"} or {
        chunk.source for chunk, _ in index._items} == {"a.md", "sub/b.md"}
    response = TestClient(app).get("/api/graph")
    assert any(edge["relation"] == "links" for edge in response.json()["edges"])


def test_injected_providers_call_models():
    class OpenAIClient:
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    return type("Response", (), {"choices": [
                        type("Choice", (), {"message": type("Message", (), {"content": "openai"})()})()
                    ]})()

    class AnthropicClient:
        class messages:
            @staticmethod
            def create(**kwargs):
                return type("Response", (), {"content": [type("Block", (), {"text": "anthropic"})()]})()

    assert OpenAIProvider(client=OpenAIClient()).answer("q", []) == "openai"
    assert AnthropicProvider(client=AnthropicClient()).answer("q", []) == "anthropic"


def test_provider_missing_key_is_actionable():
    try:
        OpenAIProvider(api_key="")
        assert False
    except RuntimeError as exc:
        assert "OPENAI_API_KEY" in str(exc)


def test_memory_write_and_tool_schema_endpoints():
    tools.register("safe", lambda: "ok", requires_confirmation=True, description="A test action")
    client = TestClient(app)
    written = client.post("/api/memory", json={"text": "# Captured\n\nA durable thought", "source": "captured.md"})
    assert written.status_code == 200
    assert written.json()["chunks"] == 1
    schemas = client.get("/api/tools").json()
    assert any(item["name"] == "safe" and item["requires_confirmation"] for item in schemas)
