import re
from pathlib import Path
from .models import MemoryChunk


def chunk_markdown(text: str, source: str, chunk_size: int = 800, overlap: int = 100) -> list[MemoryChunk]:
    """Split markdown on headings and then into bounded word windows."""
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")
    sections = re.split(r"(?m)(?=^#{1,6}\s)", text)
    heading_stack: list[str] = []
    chunks: list[MemoryChunk] = []
    for section_no, section in enumerate(filter(str.strip, sections)):
        heading = re.match(r"^(#{1,6})\s+(.+?)(?:\n|$)", section)
        if heading:
            level, title = len(heading.group(1)), heading.group(2).strip()
            heading_stack = heading_stack[:level - 1] + [title]
        links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", section)
        words = section.split()
        step = chunk_size - overlap
        for start in range(0, len(words), step):
            body = " ".join(words[start:start + chunk_size]).strip()
            if not body:
                continue
            chunks.append(MemoryChunk(
                id=f"{Path(source).stem}-{section_no}-{start}",
                text=body, source=source,
                metadata={"section": section_no, "start": start,
                          "heading": heading_stack[-1] if heading_stack else None,
                          "heading_path": list(heading_stack), "links": links},
            ))
    return chunks
