from pathlib import Path
from .chunking import chunk_markdown
from .index import MemoryIndex


def index_notes(notes_path: Path, index: MemoryIndex) -> int:
    """Recursively index markdown notes, retaining relative source paths."""
    if not notes_path.exists():
        return 0
    files = [notes_path] if notes_path.is_file() else sorted(notes_path.rglob("*.md"))
    total = 0
    for path in files:
        source = str(path.relative_to(notes_path.parent if notes_path.is_file() else notes_path))
        chunks = chunk_markdown(path.read_text(encoding="utf-8"), source)
        index.add(chunks)
        total += len(chunks)
    return total
