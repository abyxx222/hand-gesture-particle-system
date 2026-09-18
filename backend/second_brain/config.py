from pathlib import Path
from pydantic import BaseModel, Field, field_validator
import os


class Settings(BaseModel):
    provider: str = Field(default_factory=lambda: os.getenv("AI_PROVIDER", "mock"))
    memory_dir: Path = Field(default_factory=lambda: Path(os.getenv("MEMORY_DIR", "./data/memory")))
    chroma_dir: Path = Field(default_factory=lambda: Path(os.getenv("CHROMA_DIR", "./data/chroma")))
    allowed_root: Path = Field(default_factory=lambda: Path(os.getenv("ALLOWED_ROOT", "./data")))
    model: str = Field(default_factory=lambda: os.getenv("AI_MODEL", "mock"))
    openai_api_key: str | None = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    anthropic_api_key: str | None = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    xai_api_key: str | None = Field(default_factory=lambda: os.getenv("XAI_API_KEY"))
    notes_path: Path = Field(default_factory=lambda: Path(os.getenv("NOTES_PATH", "./notes")))
    personality_name: str = Field(default_factory=lambda: os.getenv("PERSONALITY_NAME", "Sage"))
    personality_prompt: str = Field(default_factory=lambda: os.getenv(
        "PERSONALITY_PROMPT", "Be thoughtful, concise, and cite memories when useful."))

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, value: str) -> str:
        allowed = {"mock", "openai", "anthropic", "grok"}
        if value.lower() not in allowed:
            raise ValueError(f"provider must be one of {sorted(allowed)}")
        return value.lower()

    def ensure_dirs(self) -> None:
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_dir.mkdir(parents=True, exist_ok=True)
        self.allowed_root.mkdir(parents=True, exist_ok=True)

    @property
    def personality(self) -> dict[str, str]:
        return {"name": self.personality_name, "system_prompt": self.personality_prompt}
