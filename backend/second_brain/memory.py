import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from .models import MemoryChunk


class MemoryStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, name: str, chunks: list[MemoryChunk]) -> Path:
        path = (self.root / name).with_suffix(".json")
        payload = json.dumps([chunk.model_dump() for chunk in chunks], indent=2)
        with NamedTemporaryFile("w", encoding="utf-8", dir=self.root, delete=False) as tmp:
            tmp.write(payload)
            temporary = Path(tmp.name)
        os.replace(temporary, path)
        return path

    def load(self, name: str) -> list[MemoryChunk]:
        path = (self.root / name).with_suffix(".json")
        if not path.exists():
            return []
        return [MemoryChunk.model_validate(item) for item in json.loads(path.read_text(encoding="utf-8"))]

